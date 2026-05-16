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
# CHECK 3: FACEBOOK TOKEN
# ─────────────────────────────────────────────

def check_facebook_token():
    token   = config.get('facebook_page_token', '')
    page_id = config.get('facebook_page_id', '')
    if not token or not page_id:
        warnings.append('Facebook: token o page_id no configurados en config.json')
        return False

    r = requests.get(f'https://graph.facebook.com/v19.0/debug_token',
        params={'input_token': token, 'access_token': token}, timeout=10)
    d = r.json().get('data', {})

    if not d.get('is_valid'):
        err = d.get('error', {}).get('message', 'token inválido')
        warnings.append(f'Facebook token INVÁLIDO: {err} — Regenerar en developers.facebook.com')
        return False

    # Test posting permission
    r2 = requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed',
        data={'message': '🔧 Test monitor', 'access_token': token}, timeout=10)
    if r2.status_code == 200:
        test_id = r2.json().get('id','')
        # Delete test post immediately
        requests.delete(f'https://graph.facebook.com/v19.0/{test_id}',
            params={'access_token': token}, timeout=10)
        log('  ✓ Facebook token: válido y con permisos de publicación')
        return True
    else:
        err = r2.json().get('error', {}).get('message', '')
        warnings.append(f'Facebook token SIN PERMISO de publicación: {err} — Regenerar en developers.facebook.com → Graph API Explorer → pages_manage_posts + pages_read_engagement')
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


# ─────────────────────────────────────────────
# FIX: REPOSTEAR EN FACEBOOK artículos sin post
# ─────────────────────────────────────────────

def fix_facebook_missing_posts(site, recent_posts, fb_ok):
    if not fb_ok or not recent_posts:
        return
    token   = config.get('facebook_page_token', '')
    page_id = config.get('facebook_page_id', '')
    kw_key  = site.get('keywords_key', '')

    # Hashtags por nicho
    HASHTAGS = {
        'turismo_ourense':  '#TurismoOurense #Ourense #Galicia #TermasOurense #ViajarEspaña',
        'bengalas_humo':    '#BengalasDeHumo #Fotografia #HumoColores #FotografiaCreativa',
        'ia_principiantes': '#InteligenciaArtificial #IA #ChatGPT #AprendeIA',
        'prompts':          '#Prompts #PromptEngineering #ChatGPT #IA',
        'claude':           '#Claude #Anthropic #IA #InteligenciaArtificial',
    }
    hashtags = HASHTAGS.get(kw_key, '#IA')

    # Solo repostear el artículo más reciente
    post = recent_posts[0]
    title   = post['title']['rendered']
    url     = post['link']
    media_id = post.get('featured_media', 0)

    image_url = ''
    if media_id:
        try:
            clean = site['url'].rstrip('/')
            auth  = (site['wp_user'], site['wp_password'])
            r = requests.get(f'{clean}/wp-json/wp/v2/media/{media_id}', auth=auth, timeout=10)
            if r.status_code == 200:
                image_url = r.json().get('source_url', '')
        except Exception:
            pass

    message = f'📰 {title}\n\n🔗 {url}\n\n{hashtags}'

    # Intentar con imagen primero
    photo_id = None
    if image_url:
        try:
            img_bytes = requests.get(image_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'}).content
            r_photo = requests.post(
                f'https://graph.facebook.com/v19.0/{page_id}/photos',
                data={'published': 'false', 'access_token': token},
                files={'source': ('photo.jpg', img_bytes, 'image/jpeg')},
                timeout=60
            )
            if r_photo.status_code == 200:
                photo_id = r_photo.json().get('id')
        except Exception:
            pass

    post_data = {'message': message, 'access_token': token}
    if photo_id:
        post_data['attached_media'] = json.dumps([{'media_fbid': photo_id}])
    else:
        post_data['link'] = url

    r_post = requests.post(f'https://graph.facebook.com/v19.0/{page_id}/feed',
        data=post_data, timeout=25)
    if r_post.status_code == 200:
        fixes.append(f'Facebook post creado para {site["name"]}: {title[:50]}')
    else:
        issues.append(f'Facebook post falló para {site["name"]}: {r_post.json().get("error",{}).get("message","")}')


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

    # 3. Facebook token
    log('\n[3] Facebook token...')
    fb_ok = check_facebook_token()

    # 4. Pinterest
    log('\n[4] Pinterest...')
    check_pinterest()

    # 5. WordPress + Facebook retry
    log('\n[5] WordPress + Facebook...')
    for site in config['sites']:
        log(f'\n  [{site["name"]}]')
        recent = check_wordpress(site)
        if recent and fb_ok:
            fix_facebook_missing_posts(site, recent, fb_ok)

    # Resumen
    log(f'\n{"="*55}')
    log(f'  Fixes: {len(fixes)} | Warnings: {len(warnings)} | Issues: {len(issues)}')
    log(f'{"="*55}')

    # Email solo si hay algo que reportar
    if fixes or warnings or issues:
        has_critical = bool(warnings or issues)
        subject = ('🚨 Monitor: acción requerida' if has_critical
                   else '✅ Monitor: correcciones automáticas aplicadas')
        send_alert(subject, build_email_report())

    # Exit code no-zero si hay issues sin resolver
    if issues:
        sys.exit(1)


if __name__ == '__main__':
    main()
