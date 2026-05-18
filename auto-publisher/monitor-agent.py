# -*- coding: utf-8 -*-
"""
AGENTE MONITOR 24/7 — Auto-publisher watchdog
Verifica el estado de todas las webs y corrige problemas automáticamente.
Envía email solo cuando hay errores que no puede resolver solo.

Checks:
  1. WordPress: artículos publicados en las últimas 12h por web
  2. Groq API: disponibilidad y cuota restante
  3. Facebook: token válido + post del último artículo si faltó
  4. Pinterest: token válido
  5. Keywords: recicla automáticamente si se agotan
  6. Imágenes: verifica que se subieron correctamente

Fixes automáticos:
  - Recicla keywords agotadas
  - Reintenta publicación en Facebook si falló
  - Alerta por email si algo no puede arreglarse solo
"""
import requests, json, os, sys, re, time, smtplib, csv
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
KW_FILE     = os.path.join(BASE_DIR, 'keywords.json')
LOG_FILE    = os.path.join(BASE_DIR, 'monitor.log')

config = json.load(open(CONFIG_FILE, encoding='utf-8'))

ALERT_EMAIL = 'espiacm@gmail.com'
NOW_UTC     = datetime.now(timezone.utc)
WINDOW_H    = 13  # horas — esperamos al menos 1 artículo por web en este período

issues   = []   # problemas encontrados
fixes    = []   # correcciones aplicadas
warnings = []   # avisos que requieren acción manual


# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────

def log(msg):
    ts = NOW_UTC.strftime('%Y-%m-%d %H:%M')
    line = f'[{ts}] {msg}'
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def send_alert(subject, body_html):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = config.get('smtp_email', '')
        msg['To']      = ALERT_EMAIL
        msg.attach(MIMEText(body_html, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15) as s:
            s.login(config['smtp_email'], config['smtp_password'])
            s.sendmail(config['smtp_email'], ALERT_EMAIL, msg.as_string())
        log(f'  Email alerta enviado: {subject}')
    except Exception as e:
        log(f'  ERROR email: {e}')


# ─────────────────────────────────────────────
# CHECK 1: WORDPRESS — artículos recientes
# ─────────────────────────────────────────────

def check_wordpress(site):
    name  = site['name']
    clean = site['url'].rstrip('/')
    auth  = (site['wp_user'], site['wp_password'])
    cutoff = (NOW_UTC - timedelta(hours=WINDOW_H)).isoformat()

    try:
        r = requests.get(f'{clean}/wp-json/wp/v2/posts',
            params={'per_page': 5, 'orderby': 'date', 'order': 'desc',
                    '_fields': 'id,date,title,featured_media,link', 'after': cutoff},
            auth=auth, timeout=15)
        if r.status_code != 200:
            issues.append(f'WP {name}: error {r.status_code}')
            return []
        posts = r.json()
        if not posts:
            issues.append(f'WP {name}: 0 artículos en las últimas {WINDOW_H}h')
        else:
            log(f'  ✓ {name}: {len(posts)} artículo(s) en las últimas {WINDOW_H}h')
        return posts
    except Exception as e:
        issues.append(f'WP {name}: excepción — {e}')
        return []


# ─────────────────────────────────────────────
# CHECK 2: GROQ API
# ─────────────────────────────────────────────

def check_groq():
    try:
        r = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {config["groq_api_key"]}', 'Content-Type': 'application/json'},
            json={'model': 'llama-3.3-70b-versatile',
                  'messages': [{'role': 'user', 'content': 'Di solo OK'}],
                  'max_tokens': 5},
            timeout=20
        )
        if r.status_code == 200:
            log('  ✓ Groq API: OK')
            return True
        elif r.status_code == 429:
            issues.append('Groq API: límite de tokens diario alcanzado (se resetea medianoche UTC)')
            return False
        else:
            issues.append(f'Groq API: error {r.status_code}')
            return False
    except Exception as e:
        issues.append(f'Groq API: excepción — {e}')
        return False


# ─────────────────────────────────────────────
# CHECK 3: MAKE.COM FACEBOOK SCENARIO
# ─────────────────────────────────────────────

MAKE_FACEBOOK_SCENARIO_ID = 9243561
MAKE_API_TOKEN = '0b69fadd-8143-47ab-b771-61f10a6ed8c1'

def check_make_facebook_scenario():
    """Verifica que el escenario de Make.com para Facebook este activo y valido."""
    try:
        r = requests.get(
            f'https://eu2.make.com/api/v2/scenarios/{MAKE_FACEBOOK_SCENARIO_ID}',
            headers={'Authorization': f'Token {MAKE_API_TOKEN}'},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json().get('scenario', r.json())
            is_active  = data.get('isActive', False)
            is_invalid = data.get('isinvalid', False)
            if is_active and not is_invalid:
                log('  Make.com Facebook: escenario activo y valido')
                return True
            elif is_invalid:
                warnings.append('Make.com Facebook: escenario invalido — verificar en make.com')
            else:
                warnings.append('Make.com Facebook: escenario inactivo — activarlo en make.com')
        else:
            warnings.append(f'Make.com: no se pudo verificar escenario ({r.status_code})')
    except Exception as e:
        warnings.append(f'Make.com check error: {str(e)[:80]}')
    return False


# ─────────────────────────────────────────────
# CHECK 4: PINTEREST TOKEN
# ─────────────────────name─────────────────────

def check_pinterest():
    token = config.get('pinterest', {}).get('access_token', '')
    if not token:
        return
    r = requests.get('https://api.pinterest.com/v5/user_account',
        headers={'Authorization': f'Bearer {token}'}, timeout=10)
    if r.status_code == 200:
        log(f'  ✓ Pinterest token: válido ({r.json().get("username","")})')
    else:
        issues.append(f'Pinterest token inválido: {r.status_code}')


# ─────────────────────────────────────────────
# FIX: RECICLAR KEYWORDS AGOTADAS
# ─────────────────────────────────────────────

def fix_keywords():
    kw = json.load(open(KW_FILE, encoding='utf-8'))
    changed = False
    for site in config['sites']:
        key = site['keywords_key']
        if key in kw and len(kw[key]) == 0:
            used_key = f'{key}_usadas'
            recycled = kw.get(used_key, [])
            if recycled:
                kw[key] = recycled[:]
                kw[used_key] = []
                fixes.append(f'Keywords recicladas para {site["name"]} ({len(recycled)} keywords)')
                changed = True
            else:
                issues.append(f'Keywords agotadas en {site["name"]} y sin usadas para reciclar')
    if changed:
        with open(KW_FILE, 'w', encoding='utf-8') as f:
            json.dump(kw, f, ensure_ascii=False, indent=2)


# Facebook eliminado del agente — gestionado por Make.com automáticamente


# ─────────────────────────────────────────────
# REPORT FINAL
# ─────────────────────────────────────────────

def build_email_report():
    color_ok  = '#22c55e'
    color_err = '#ef4444'
    color_warn = '#f59e0b'

    rows = ''
    if fixes:
        rows += f'<h3 style="color:{color_ok}">✅ Correcciones automáticas ({len(fixes)})</h3><ul>'
        for f in fixes:
            rows += f'<li>{f}</li>'
        rows += '</ul>'

    if warnings:
        rows += f'<h3 style="color:{color_warn}">⚠️ Requieren acción manual ({len(warnings)})</h3><ul>'
        for w in warnings:
            rows += f'<li>{w}</li>'
        rows += '</ul>'

    if issues:
        rows += f'<h3 style="color:{color_err}">❌ Errores sin resolver ({len(issues)})</h3><ul>'
        for i in issues:
            rows += f'<li>{i}</li>'
        rows += '</ul>'

    ts = NOW_UTC.strftime('%d/%m/%Y %H:%M UTC')
    return f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
      <h2>🤖 Monitor Auto-Publisher — {ts}</h2>
      {rows}
      <p style="color:#888;font-size:.85em">Monitor automático — se ejecuta cada 6 horas</p>
    </div>
    """


# ─────────────────────────────────────────────
# ANALYTICS — DETECTA CONTENIDO POPULAR
# ─────────────────────────────────────────────

def get_top_posts_wp(site, limit=10):
    """Obtiene los artículos más recientes y con más comentarios vía WP REST API."""
    clean = site['url'].rstrip('/')
    auth  = (site['wp_user'], site['wp_password'])
    posts = []
    try:
        # Por comentarios (proxy de popularidad)
        r = requests.get(f'{clean}/wp-json/wp/v2/posts', auth=auth, params={
            'per_page': 50, 'orderby': 'comment_count', 'order': 'desc',
            'status': 'publish', '_fields': 'id,title,link,categories,comment_count,date'
        }, timeout=15)
        if r.status_code == 200:
            posts = r.json()[:limit]
    except Exception:
        pass
    return posts


def get_top_posts_ga4(site):
    """Obtiene páginas más visitadas vía GA4 Data API (requiere ga4_access_token en config)."""
    prop_id = site.get('ga4_id', '').replace('G-', '')
    token   = config.get('ga4_access_token', '')
    if not prop_id or not token:
        return []
    try:
        r = requests.post(
            f'https://analyticsdata.googleapis.com/v1beta/properties/{prop_id}:runReport',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={
                'dimensions':  [{'name': 'pagePath'}, {'name': 'pageTitle'}],
                'metrics':     [{'name': 'screenPageViews'}],
                'dateRanges':  [{'startDate': '30daysAgo', 'endDate': 'today'}],
                'limit':       10,
                'orderBys':    [{'metric': {'metricName': 'screenPageViews'}, 'desc': True}]
            }, timeout=15
        )
        if r.status_code == 200:
            rows = r.json().get('rows', [])
            return [{'path':  row['dimensionValues'][0]['value'],
                     'title': row['dimensionValues'][1]['value'],
                     'views': int(row['metricValues'][0]['value'])}
                    for row in rows]
    except Exception as e:
        log(f'  GA4 API error: {e}')
    return []


def extract_trending_topics(ga4_pages, wp_posts, site):
    """Combina datos GA4 + WP para identificar los temas que mejor funcionan."""
    topics = []
    # De GA4 (si disponible)
    for p in ga4_pages[:5]:
        title = p.get('title', '').strip()
        if title and title not in ('(not set)', 'Home', 'Inicio'):
            topics.append({'title': title, 'views': p.get('views', 0), 'source': 'ga4'})
    # De WP (fallback o complemento)
    for p in wp_posts[:5]:
        title = p.get('title', {}).get('rendered', '').strip()
        if title:
            topics.append({
                'title':    title,
                'comments': p.get('comment_count', 0),
                'link':     p.get('link', ''),
                'source':   'wp'
            })
    return topics


def generate_trending_article(site, groq_key, top_topic_title, model='llama-3.3-70b-versatile'):
    """Genera un artículo nuevo basado en un tema que ya funciona bien."""
    niche = site.get('niche_context', '')
    current_year = datetime.now().year
    prompt = f"""AÑO ACTUAL: {current_year}
INSTRUCCIÓN CRÍTICA DE FECHA: Usa siempre {current_year} para cualquier año que escribas en el artículo. Nunca uses {current_year - 1} como "este año" o "año actual".

Actúa como Consultor SEO Experto y Redactor enfocado en Google Discover y alto CPC.

Uno de los artículos más populares de este blog trata sobre: "{top_topic_title}"
Nicho del blog: {niche}

Crea un artículo NUEVO Y DIFERENTE que cubra un ángulo o subtema relacionado que complementa al artículo popular.
NO copies el artículo existente — crea contenido que capture búsquedas relacionadas y genere más tráfico.

TÍTULO (<60 chars, clickbait sano: curiosidad + beneficio real):
- Usa ángulos distintos: "Por qué...", "El error más común...", "Cómo los expertos..."

ESTRUCTURA OBLIGATORIA:
1. H1 con keyword principal + gancho potente
2. Intro 2-3 líneas con dato impactante
3. "En este artículo aprenderás:" con 5 puntos
4. 5-7 secciones H2 con contenido denso y práctico
5. FAQ con 5 preguntas H3 reales de Google
6. Conclusión con CTA hacia el artículo original relacionado

Idioma: Español de España. Directo, práctico, sin rodeos. 1800-2000 palabras.

Responde SOLO JSON válido:
{{
  "titulo_seo": "<60 chars clickbait sano",
  "meta_descripcion": "150-155 chars keyword + beneficio + CTA",
  "slug": "url-guiones-sin-acentos",
  "h1": "H1 completo del artículo",
  "contenido_html": "HTML completo. Mínimo 1800 palabras.",
  "descripcion_pinterest": "emoji + beneficio + verbo accion (140-160 chars)",
  "tags": ["tag1","tag2","tag3","tag4","tag5"],
  "categoria": "categoria del articulo"
}}"""

    headers = {'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'}
    MODELS  = ['llama-3.3-70b-versatile', 'openai/gpt-oss-120b', 'meta-llama/llama-4-scout-17b-16e-instruct']
    for model in MODELS:
        for attempt in range(2):
            try:
                r = requests.post('https://api.groq.com/openai/v1/chat/completions',
                    headers=headers,
                    json={'model': model, 'messages': [{'role': 'user', 'content': prompt}],
                          'temperature': 0.72, 'max_tokens': 6000,
                          'response_format': {'type': 'json_object'}},
                    timeout=90)
                if r.status_code == 200:
                    raw = r.json()['choices'][0]['message']['content']
                    if '```' in raw:
                        parts = raw.split('```')
                        raw = parts[1][4:] if parts[1].startswith('json') else parts[1]
                    article = json.loads(raw.strip())
                    # Validate minimum fields
                    if article.get('titulo_seo') and article.get('contenido_html') and len(article['contenido_html']) > 800:
                        return article
                    break  # Invalid content, try next model
                elif r.status_code == 429:
                    err_text = r.text
                    is_tpd = 'per day' in err_text or 'tokens per day' in err_text
                    if is_tpd:
                        break  # Daily limit, try next model
                    if attempt == 0:
                        time.sleep(65)  # TPM limit, wait 1 minute
                        continue
                    break
                else:
                    break
            except Exception:
                if attempt < 1:
                    time.sleep(5)
                continue
    return None


def publish_trending_article(site, article):
    """Publica un artículo generado por el análisis de tendencias."""
    clean = site['url'].rstrip('/')
    auth  = (site['wp_user'], site['wp_password'])

    # Categoría
    cat_id = None
    cat_name = article.get('categoria', 'Blog')
    try:
        r = requests.get(f'{clean}/wp-json/wp/v2/categories', auth=auth,
                         params={'search': cat_name, 'per_page': 3}, timeout=8)
        cats = r.json() if r.ok else []
        cat_id = next((c['id'] for c in cats if c.get('name','').lower() == cat_name.lower()), None)
        if not cat_id:
            r2 = requests.post(f'{clean}/wp-json/wp/v2/categories', auth=auth,
                               json={'name': cat_name}, timeout=8)
            cat_id = r2.json().get('id') if r2.ok else None
    except Exception:
        pass

    import re as _re
    slug = _re.sub(r'[^a-z0-9-]', '', article.get('slug', '').lower().replace(' ', '-'))
    payload = {
        'title':      article.get('titulo_seo', ''),
        'slug':       slug,
        'content':    article.get('contenido_html', ''),
        'status':     'publish',
        'excerpt':    article.get('meta_descripcion', ''),
        'categories': [cat_id] if cat_id else [],
        'comment_status': 'closed',
    }
    for attempt in range(3):
        try:
            r = requests.post(f'{clean}/wp-json/wp/v2/posts', auth=auth, json=payload, timeout=60)
            if r.status_code == 201:
                return r.json().get('link', '')
            if r.status_code >= 500 and attempt < 2:
                time.sleep(10)
                continue
            break
        except Exception:
            if attempt < 2:
                time.sleep(10)
    return ''


def run_analytics_and_generate(groq_ok):
    """Check 6: Analiza contenido popular y genera artículos similares (1 por web)."""
    log('\n[6] Analytics + generacion de contenido tendencia...')
    groq_key = config.get('groq_api_key', '')

    for site in config['sites']:
        name = site['name']
        log(f'\n  [{name}]')

        # Obtener top content
        ga4_pages = get_top_posts_ga4(site)
        wp_posts  = get_top_posts_wp(site)
        topics    = extract_trending_topics(ga4_pages, wp_posts, site)

        if not topics:
            log(f'    Sin datos suficientes para generar contenido')
            continue

        # Usar el tema más popular
        best = topics[0]
        best_title = best.get('title', '')
        source = best.get('source', 'wp')
        views = best.get('views', best.get('comments', 0))
        log(f'    Tema top ({source}): "{best_title[:60]}" ({views} interacciones)')

        if not groq_ok:
            log(f'    Groq no disponible — saltando generacion')
            continue

        # Generar artículo complementario
        log(f'    Generando articulo complementario...', )
        article = generate_trending_article(site, groq_key, best_title)
        if not article:
            log(f'    ERROR: no se pudo generar el articulo')
            issues.append(f'Analytics gen: fallo Groq para {name}')
            continue

        # Publicar
        url = publish_trending_article(site, article)
        if url:
            log(f'    Publicado: {url}')
            fixes.append(f'Articulo tendencia publicado en {name}: {article.get("titulo_seo","")[:50]}')
        else:
            log(f'    ERROR al publicar')
            issues.append(f'Analytics: error al publicar en {name}')


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    log(f'\n{"="*55}')
    log(f'  MONITOR AGENT  |  {NOW_UTC.strftime("%d/%m/%Y %H:%M UTC")}')
    log(f'{"="*55}')

    # 1. Keywords
    log('\n[1] Keywords...')
    fix_keywords()

    # 2. Groq
    log('\n[2] Groq API...')
    groq_ok = check_groq()

    # 3. Make.com Facebook scenario
    log('\n[3] Make.com Facebook...')
    check_make_facebook_scenario()

    # 4. Pinterest
    log('\n[4] Pinterest...')
    check_pinterest()

    # 5. WordPress
    log('\n[5] WordPress...')
    for site in config['sites']:
        log(f'\n  [{site["name"]}]')
        check_wordpress(site)

    # 6. Analytics + generacion de contenido tendencia
    run_analytics_and_generate(groq_ok)

    # Resumen
    log(f'\n{"="*55}')
    log(f'  Fixes: {len(fixes)} | Warnings: {len(warnings)} | Issues: {len(issues)}')
    log(f'{"="*55}')

    # Email solo si hay algo que reportar
    if fixes or warnings or issues:
        has_critical = bool(warnings or issues)
        subject = ('Monitor: accion requerida' if has_critical
                   else 'Monitor: correcciones automaticas aplicadas')
        send_alert(subject, build_email_report())

    # Exit code no-zero si hay issues sin resolver
    if issues:
        sys.exit(1)


if __name__ == '__main__':
    main()
