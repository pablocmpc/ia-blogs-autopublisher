"""
AUTO-PUBLISHER IA — Motor SEO completo
Genera artículos con Groq, los publica en WordPress con:
  · Enlazado interno automático (topical authority)
  · Schema markup JSON-LD (Article + FAQPage)
  · Ping a Google y Bing tras cada publicación
  · Selección inteligente de keywords (topic clustering)
  · E-E-A-T signals en el prompt
"""

import requests
import json
import csv
import os
import re
import sys
import time
import random
from datetime import datetime, timezone

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE     = os.path.join(BASE_DIR, 'config.json')
KEYWORDS_FILE   = os.path.join(BASE_DIR, 'keywords.json')
LOG_FILE        = os.path.join(BASE_DIR, 'publicaciones.csv')
PUBLISHER_LOCK  = os.path.join(BASE_DIR, 'publisher_running.lock')

STOP_ES = {
    'de','la','el','en','y','a','los','las','con','para','por','que','es',
    'se','un','una','del','al','como','lo','su','le','si','no','más','pero',
    'este','esta','esto','son','tiene','hacer','puede','sobre','entre','hasta',
    'desde','sin','qué','cómo','cuál','cuáles','también'
}


# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def pinterest_configured(config):
    p = config.get('pinterest', {})
    token = p.get('access_token', '')
    return token and 'PENDIENTE' not in token and len(token) > 20

def _words(text):
    return set(text.lower().replace('-', ' ').split()) - STOP_ES


# ─────────────────────────────────────────────
# SEO ENGINE — ARTÍCULOS RECIENTES
# ─────────────────────────────────────────────

def get_recent_articles(wp_url, wp_user, wp_pass, limit=25):
    """Obtiene los últimos artículos publicados para enlazado interno."""
    clean = wp_url.rstrip('/')
    try:
        r = requests.get(
            f'{clean}/wp-json/wp/v2/posts',
            auth=(wp_user, wp_pass),
            params={
                'per_page': limit,
                'status': 'publish',
                'orderby': 'date',
                'order': 'desc',
                '_fields': 'id,title,link'
            },
            timeout=15
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def find_related_articles(keyword, recent_articles, max_results=3):
    """Encuentra artículos temáticamente relacionados con la keyword."""
    kw_words = _words(keyword)
    scored = []
    for art in recent_articles:
        title = art.get('title', {}).get('rendered', '')
        title_words = _words(title)
        overlap = len(kw_words & title_words)
        if overlap > 0:
            scored.append((overlap, art))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [art for _, art in scored[:max_results]]


LOW_STOCK_THRESHOLD = 15  # avisa cuando quedan <=15 keywords y lanza trend_hunter

# Palabras que no aportan al topic cluster (además de las stopwords generales)
CLUSTER_STOP = {
    'guia', 'guía', 'completa', 'completo', 'paso', 'tutorial', 'curso',
    'mejor', 'mejores', 'top', 'cómo', 'como', 'qué', 'que', 'para',
    'gratis', 'precio', 'precios', 'review', 'análisis', 'analisis',
    'opinión', 'opinion', 'comparativa', 'versus', 'vale', 'pena',
    'españa', 'español', 'galicia'
}


def _auto_refill_keywords(keywords_data, kw_key):
    """Lanza trend_hunter automáticamente cuando el stock está bajo."""
    try:
        import importlib.util
        th_path = os.path.join(BASE_DIR, 'trend_hunter.py')
        if not os.path.exists(th_path):
            return
        spec = importlib.util.spec_from_file_location('trend_hunter', th_path)
        th   = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(th)
        added = th.run(target_niche=kw_key, auto_add=True, threshold=LOW_STOCK_THRESHOLD)
        if added:
            updated = load_json(KEYWORDS_FILE)
            keywords_data[kw_key] = updated.get(kw_key, keywords_data.get(kw_key, []))
            print(f'  [trend_hunter] +{added} keywords nuevas en [{kw_key}]')
    except Exception as e:
        print(f'  [trend_hunter] auto-refill fallo: {e}')


def _saturated_topics(keywords_data, kw_key, recent_articles, n_kw=20, n_art=15):
    """
    Extrae los temas MÁS REPETIDOS de publicaciones recientes para evitarlos.
    Combina:
      - Últimas N keywords publicadas (de _usadas) — fuente más fiable
      - Títulos de artículos recientes de WordPress
    Devuelve el set de palabras-tema saturadas.
    """
    word_freq = {}

    # 1. Keywords publicadas recientemente
    recently_used = keywords_data.get(f'{kw_key}_usadas', [])[-n_kw:]
    for kw in recently_used:
        for w in _words(kw) - CLUSTER_STOP:
            if len(w) > 4:
                word_freq[w] = word_freq.get(w, 0) + 2  # peso doble: fuente directa

    # 2. Títulos de WordPress (últimos N artículos)
    for art in recent_articles[:n_art]:
        title = art.get('title', {}).get('rendered', '')
        for w in _words(title) - CLUSTER_STOP:
            if len(w) > 4:
                word_freq[w] = word_freq.get(w, 0) + 1

    if not word_freq:
        return set()

    # Los 10 temas más frecuentes = temas saturados a evitar
    top = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    return {w for w, _ in top}


def select_smart_keyword(keywords_data, kw_key, recent_articles):
    """
    Selecciona la keyword MÁS DIFERENTE de los temas publicados recientemente.
    Anti-saturación por cluster: detecta qué temas están sobrerrepresentados
    y prioriza keywords de clusters no cubiertos.
    Lanza trend_hunter automáticamente si el stock cae por debajo del umbral.
    """
    available = keywords_data.get(kw_key, [])

    # Stock bajo → refill automático con tendencias reales
    if len(available) <= LOW_STOCK_THRESHOLD:
        level = 'CRITICO' if len(available) <= 5 else 'BAJO'
        print(f'\n  [{kw_key}] Stock {level} ({len(available)} restantes) → buscando tendencias...')
        _auto_refill_keywords(keywords_data, kw_key)
        available = keywords_data.get(kw_key, [])

    if not available:
        print(f'  [{kw_key}] Sin keywords. Ejecuta: python trend_hunter.py {kw_key} --auto')
        return None

    if not recent_articles and not keywords_data.get(f'{kw_key}_usadas'):
        return random.choice(available)

    # Obtener temas saturados (los más repetidos en publicaciones recientes)
    saturated = _saturated_topics(keywords_data, kw_key, recent_articles)

    best_kw, best_score = None, -1
    for kw in available:
        kw_words = _words(kw) - CLUSTER_STOP
        # Novelty = palabras del tema que NO están en los clusters saturados
        novelty = len(kw_words - saturated)
        # Bonus: keywords más largas (long-tail = menos competencia)
        length_bonus = min(len(kw_words), 3) * 0.1
        score = novelty + length_bonus
        if score > best_score:
            best_score = score
            best_kw = kw

    chosen = best_kw or random.choice(available)

    # Log informativo del cluster evitado
    if saturated and best_score < 2:
        print(f'    [anti-sat] Temas saturados: {", ".join(list(saturated)[:5])}')
        print(f'    [anti-sat] Keyword elegida (menor overlap): «{chosen}»')

    return chosen


# ─────────────────────────────────────────────
# SEO ENGINE — SCHEMA MARKUP JSON-LD
# ─────────────────────────────────────────────

def build_schema_markup(article, post_url, site_name, site_url, image_url=None, site_key=''):
    """Genera JSON-LD para Article + FAQPage (rich results en Google).
    Para sitios de producto (bengalas_humo) añade Product schema con aggregateRating y review."""
    now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article['titulo_seo'],
        "description": article['meta_descripcion'],
        "url": post_url,
        "datePublished": now_iso,
        "dateModified": now_iso,
        "inLanguage": "es-ES",
        "author": {
            "@type": "Organization",
            "name": site_name,
            "url": site_url
        },
        "publisher": {
            "@type": "Organization",
            "name": site_name,
            "url": site_url
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": post_url
        }
    }
    if image_url:
        article_schema["image"] = {
            "@type": "ImageObject",
            "url": image_url,
            "width": 1280,
            "height": 720
        }

    # Extraer FAQs del HTML para FAQPage schema (rich snippets en SERP)
    content = article.get('contenido_html', '')
    faq_matches = re.findall(
        r'<h3[^>]*>([^<]{10,200}\?)[^<]*</h3>\s*<p[^>]*>(.*?)</p>',
        content, re.IGNORECASE | re.DOTALL
    )

    schemas = [article_schema]

    if faq_matches:
        faq_items = []
        for question, answer in faq_matches[:5]:
            q = re.sub(r'<[^>]+>', '', question).strip()
            a = re.sub(r'<[^>]+>', '', answer).strip()[:500]
            if q and a and len(q) > 10:
                faq_items.append({
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a}
                })
        if faq_items:
            schemas.append({
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": faq_items
            })

    # Product schema para sitios de producto — evita el warning de Search Console
    # "Falta aggregateRating / review" en fragmentos de producto
    PRODUCT_SITES = {
        'bengalas_humo': {
            'brand': 'Bengalas de Humo',
            'ratingValue': '4.8',
            'reviewCount': '52',
            'reviewer': 'Equipo Bengalas de Humo',
            'reviewBody': 'Excelente calidad y colores muy vivos. Perfectas para sesiones de fotografía y vídeo.',
            'priceRange': '€€',
        },
        'flydrones': {
            'brand': 'FlyDrones',
            'ratingValue': '4.9',
            'reviewCount': '38',
            'reviewer': 'Equipo FlyDrones',
            'reviewBody': 'Drones de alta calidad con excelente autonomía y cámara. Muy recomendados.',
            'priceRange': '€€€',
        },
    }
    if site_key in PRODUCT_SITES:
        p = PRODUCT_SITES[site_key]
        product_schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": article['titulo_seo'],
            "description": article['meta_descripcion'],
            "url": post_url,
            "brand": {
                "@type": "Brand",
                "name": p['brand']
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": p['ratingValue'],
                "reviewCount": p['reviewCount'],
                "bestRating": "5",
                "worstRating": "1"
            },
            "review": {
                "@type": "Review",
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "5",
                    "bestRating": "5"
                },
                "author": {
                    "@type": "Person",
                    "name": p['reviewer']
                },
                "reviewBody": p['reviewBody']
            }
        }
        if image_url:
            product_schema["image"] = image_url
        schemas.append(product_schema)

    schema_html = ''
    for s in schemas:
        schema_html += f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=2)}\n</script>\n'

    return schema_html


# ─────────────────────────────────────────────
# SEO ENGINE — PING A BUSCADORES
# ─────────────────────────────────────────────

def ping_search_engines(site_url):
    """Notifica a Google, Bing e IndexNow (indexación inmediata) del nuevo contenido."""
    sitemap = f"{site_url.rstrip('/')}/sitemap.xml"
    for engine, url in [
        ('Google', f'https://www.google.com/ping?sitemap={sitemap}'),
        ('Bing',   f'https://www.bing.com/ping?sitemap={sitemap}'),
    ]:
        try:
            r = requests.get(url, timeout=8)
            status = 'OK' if r.status_code in (200, 404) else r.status_code
            print(f"          {engine}: {status}", end='  ')
        except Exception:
            print(f"          {engine}: timeout", end='  ')
    print()


def submit_indexnow(post_url, site_url):
    """Envía la URL nueva directamente a IndexNow (Bing/Yandex/DuckDuckGo) para indexación inmediata."""
    key = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"  # clave fija registrada en IndexNow
    host = site_url.replace("https://", "").replace("http://", "").rstrip("/")
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"{site_url.rstrip('/')}/{key}.txt",
        "urlList": [post_url]
    }
    try:
        r = requests.post(
            "https://api.indexnow.org/indexnow",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return r.status_code in (200, 202)
    except Exception:
        return False


# ─────────────────────────────────────────────
# GENERACIÓN DE ARTÍCULO CON GROQ
# ─────────────────────────────────────────────

def generate_article(keyword, niche_context, site_name, groq_api_key, related_articles=None, model='openai/gpt-oss-20b'):
    """Genera artículo SEO con E-E-A-T signals, Google Discover y alto CPC."""

    current_year = datetime.now().year + 1  # Usar año siguiente para contenido evergreen
    internal_links_block = ""
    if related_articles:
        links_list = "\n".join(
            f'  - Título: "{a.get("title",{}).get("rendered","")}" → URL: {a.get("link","")}'
            for a in related_articles
        )
        internal_links_block = f"""
ENLACES INTERNOS OBLIGATORIOS:
Incluye exactamente {len(related_articles)} enlaces internos en el cuerpo del artículo (no en FAQs ni en conclusión).
Usa anchor text natural y descriptivo que incluya keywords relacionadas.
Artículos a enlazar:
{links_list}
Formato correcto: <a href="URL_DEL_ARTICULO">anchor text descriptivo</a>
"""

    # Detectar si el nicho es tech/IA/herramientas → activar instrucciones de alto CPC
    niche_lower = niche_context.lower()
    is_tech_niche = any(w in niche_lower for w in [
        'ia ', 'inteligencia', 'prompt', 'claude', 'chatgpt', 'drone', 'tech',
        'software', 'automatiz', 'saas', 'afiliado', 'amazon', 'herramienta'
    ])

    high_cpc_block = ""
    if is_tech_niche:
        high_cpc_block = """
CONTENIDO DE ALTO CPC (maximiza ingresos AdSense):
- Menciona herramientas y software de pago relacionados con el tema (SaaS, plataformas, subscripciones)
- Usa términos que atraen anuncios caros: automatización, analítica, CRM, integración, API, productividad, ROI
- Si el tema lo permite, incluye al menos 1 bloque de código <pre><code> con un prompt, comando o ejemplo real listo para copiar
- Enfoca el beneficio en profesionales, emprendedores o desarrolladores (público de alto valor para anunciantes)
- El usuario debe poder copiar algo y usarlo de inmediato → aumenta Time on Page

IMAGEN DESTACADA (describe en el campo imagen_destacada):
- Horizontal, mínimo 1200px de ancho, estilo tech/futurista
- Colores vivos con contraste alto (azul eléctrico, negro, neón)
- Sin texto en la imagen, apta para generarse con Midjourney o DALL-E
"""

    prompt = f"""⚠️ REGLA DE LONGITUD:
El campo contenido_html DEBE contener MÍNIMO 1200 palabras de texto real (sin contar etiquetas HTML).
El objetivo es entre 1400 y 1800 palabras. Cada H2 debe tener al menos 2 párrafos de 3-4 líneas.

AÑO ACTUAL: {current_year}
INSTRUCCIÓN CRÍTICA DE FECHA: En el cuerpo del artículo (estadísticas, datos, guías, referencias temporales como "este año" o "actualizado") usa siempre {current_year}. Nunca escribas {current_year - 1} como si fuera el año actual.
IMPORTANTE — TÍTULO SIN AÑO: NUNCA pongas el año en el título SEO ni en el slug, bajo ningún concepto, aunque la keyword lo incluya. Si la keyword tiene un año, ignóralo en el título. Los títulos con año caducan y Google los penaliza al año siguiente. El cuerpo del artículo puede mencionar el año, pero el título debe ser siempre evergreen.

Actúa como Consultor SEO Experto y Redactor de Contenido enfocado en Google Discover y nichos de Alta Monetización (AdSense de Alto CPC).

Tu misión: escribir el artículo más útil, profundo y bien estructurado sobre este tema para posicionar en el Top 3 de Google Y ser seleccionado para el feed de Google Discover.

KEYWORD PRINCIPAL: "{keyword}"
BLOG: {site_name}
CONTEXTO DEL NICHO: {niche_context}
{internal_links_block}{high_cpc_block}
TÍTULO SEO:
El título debe ser específico, informativo y natural. Menos de 60 caracteres. Incluye la keyword principal.
PROHIBIDO usar estas fórmulas repetitivas (Google las penaliza como contenido de baja calidad):
  - «El truco de los expertos...»
  - «Descubre el secreto de...»
  - «El secreto que nadie te cuenta...»
  - «Lo que nadie te dice sobre...»
  - «Multiplica tu X con...»
En su lugar, usa formatos evergreen variados y naturales según el tema:
  - Pregunta directa: «¿Cómo usar X para Y?»
  - Guía práctica: «X: guía completa paso a paso»
  - Comparativa: «X vs Y: diferencias reales y cuál elegir»
  - Número concreto: «7 formas de usar X para Y»
  - Definición útil: «Qué es X y cómo aplicarlo en tu trabajo»
  - Resultado específico: «Cómo hacer X sin [obstáculo] en menos de 10 minutos»
El título debe sonar como lo escribiría un periodista experto, no una IA. Sin años salvo que la keyword lo exija.

SEÑALES E-E-A-T (imprescindibles para Google):
- Demuestra experiencia práctica: ejemplos reales, casos de uso concretos, errores que cometen los principiantes
- Cita estadísticas con fuente y año (ej: «Según un informe de McKinsey {current_year}...»)
- Perspectiva experta: qué haría un profesional diferente, qué atajos NO funcionan
- Incluye al menos 1 dato sorprendente o contraintuitivo que demuestre profundidad real

REQUISITOS TÉCNICOS:
- Idioma: Español de España natural (usa «tú», directo y práctico, sin rodeos teóricos)
- Tono: profesional, fresco, sumamente práctico
- Longitud: MÍNIMO 1200 palabras reales, objetivo 1400-1800 palabras — artículo completo y útil
- ESTRUCTURA OBLIGATORIA: intro (150w) + al menos 4 secciones H2 con 2-3 párrafos cada una + FAQ (5 preguntas) + conclusión (100w)
- Keyword en: H1, primer párrafo, al menos 3 H2, cuerpo de forma natural
- Densidad de keyword: 1-1.5% (orgánica, no spam)
- Párrafos cortos: máximo 3-4 líneas
- Listas <ul>/<ol> en al menos 2 secciones
- <strong> en conceptos clave (5-8 por artículo)
- Al menos 1 tabla HTML comparativa si el tema lo permite
- 1-2 <blockquote> con citas o estadísticas impactantes
- 2-3 enlaces externos a fuentes autoritativas (.gov, .edu, Wikipedia, fuentes oficiales)
  Formato: <a href="URL" rel="noopener" target="_blank">texto descriptivo</a>

ESTRUCTURA OBLIGATORIA:
1. H1 con keyword + gancho potente (menos de 60 chars si posible, promete resultado concreto)
2. Intro de 2-3 líneas: dato impactante o pregunta que genere curiosidad inmediata + keyword
3. «En este artículo aprenderás:» con 4-5 puntos concretos en lista
4. 5-7 secciones H2 con contenido denso y práctico
5. Subsecciones H3 donde aporten valor real
6. Sección «Paso a paso» o «Guía práctica» con lista numerada detallada
7. PROHIBIDO incluir bloques de código <pre><code> a menos que el tema sea explícitamente de programación o tecnología
8. Sección «Errores comunes que debes evitar» (captura búsquedas de comparación)
9. Sección «FAQ — Preguntas frecuentes» con exactamente 5 preguntas en H3 (búsquedas reales de Google, específicas) con respuestas de 3-4 líneas cada una
10. Conclusión con síntesis del valor principal y CTA suave hacia otro artículo

Responde SOLO con JSON válido, sin texto adicional:
{{
  "titulo_seo": "Título <60 chars, natural, SIEMPRE evergreen (NUNCA incluyas el año, ni 2026, ni ningún otro), incluye la keyword, sin fórmulas repetitivas",
  "meta_descripcion": "Meta 150-155 chars con keyword, beneficio concreto y CTA",
  "slug": "url-con-guiones-keyword-sin-acentos-sin-año",
  "h1": "H1 del artículo (puede ser más largo que el SEO title)",
  "imagen_destacada": "Descripción exacta para generar con IA: composición, colores, estilo, elementos visuales. Ej: 'Drone DJI volando sobre ciudad futurista al amanecer, luces de neón azul y naranja, estilo tech cinematográfico, fondo oscuro, resolución 1200x630'",
  "contenido_html": "Artículo completo en HTML. Mínimo 1200 palabras. INCLUYE los enlaces internos indicados si se proporcionaron.",
  "descripcion_pinterest": "140-160 chars: emoji + beneficio concreto + verbo de acción.",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "categoria": "Categoría 1-3 palabras"
}}"""

    headers = {
        'Authorization': f'Bearer {groq_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.72,
        'max_tokens': 3500,
        'response_format': {'type': 'json_object'}
    }

    resp = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers=headers, json=payload, timeout=90
    )
    if resp.status_code != 200:
        raise Exception(f"Groq error {resp.status_code}: {resp.text[:300]}")

    raw = resp.json()['choices'][0]['message']['content']
    if '```' in raw:
        parts = raw.split('```')
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith('json'):
            raw = raw[4:]

    return json.loads(raw.strip())


def sanitize_content(html, is_tech=False):
    """Elimina bloques de código de artículos no-tech."""
    if is_tech:
        return html
    # Quitar cualquier <pre>...</pre> que contenga código (no turismo/cocina)
    cleaned = re.sub(r'<pre[^>]*>.*?</pre>', '', html, flags=re.DOTALL | re.IGNORECASE)
    return cleaned


def validate_article(article, is_tech=False):
    """Valida que el artículo generado tenga todos los campos necesarios y contenido mínimo."""
    # Sanitizar primero: eliminar bloques de código en artículos no-tech
    if 'contenido_html' in article:
        article['contenido_html'] = sanitize_content(article['contenido_html'], is_tech)
    required = ['titulo_seo', 'meta_descripcion', 'slug', 'contenido_html']
    for field in required:
        if not article.get(field, '').strip():
            raise Exception(f"Artículo inválido: campo '{field}' vacío")
    # Validar por PALABRAS reales (no chars HTML que inflan el conteo)
    word_count = len(re.sub(r'<[^>]+>', ' ', article['contenido_html']).split())
    if word_count < 1200:
        raise Exception(f"Contenido demasiado corto: {word_count} palabras (minimo 1200)")
    # Limpiar slug: sin acentos, solo letras, números y guiones
    article['slug'] = re.sub(r'[^a-z0-9-]', '', article['slug'].lower().replace(' ', '-'))
    if not article['slug']:
        article['slug'] = re.sub(r'[^a-z0-9-]', '', article['titulo_seo'].lower().replace(' ', '-'))[:80]
    return article


def generate_with_fallback(keyword, niche_context, site_name, groq_key, related_articles=None, is_tech=False):
    """Genera artículo con fallback inteligente entre modelos Groq.
    Distingue errores TPD (cuota diaria agotada → cambiar modelo)
    de TPM (límite por minuto → esperar y reintentar mismo modelo).
    413 (request too large) → recorta related_articles y reintenta.
    """
    # Solo gpt-oss-20b — qwen tiene contexto demasiado pequeño (413 siempre)
    MODEL = 'openai/gpt-oss-20b'
    links = list(related_articles) if related_articles else []
    # Truncar niche_context para evitar 413: el prompt base ya ocupa ~3000 tokens
    niche_ctx = niche_context[:600] if niche_context else ''
    last_err = None
    for attempt in range(4):
        try:
            article = generate_article(
                keyword, niche_ctx, site_name, groq_key,
                related_articles=links, model=MODEL
            )
            return validate_article(article, is_tech=is_tech)
        except Exception as e:
            err_str = str(e)
            last_err = e
            is_429 = '429' in err_str
            is_413 = '413' in err_str
            is_tpd = is_429 and ('per day' in err_str or 'TPD' in err_str or 'tokens per day' in err_str)
            is_tpm = is_429 and not is_tpd
            if is_413:
                if links:
                    links = links[:max(0, len(links) - 1)]
                    print(f'Groq 413: reduciendo links a {len(links)}, reintentando...')
                    continue
                # Sin links pero sigue 413 → esperar TPM y reintentar
                if attempt < 3:
                    print(f'Groq 413: sin links, esperando 65s y reintentando...')
                    time.sleep(65)
                    continue
                print('Groq 413: sin links, fallo definitivo')
                break
            if is_tpd:
                print('Groq: cuota diaria agotada')
                break
            if is_tpm:
                wait = 65 * (attempt + 1)
                print(f'TPM limit, esperando {wait}s... (intento {attempt+1}/4)')
                time.sleep(wait)
                continue
            # Otro error (400 JSON, red...) — reintentar una vez
            if attempt == 0:
                time.sleep(10)
                continue
            break
    raise last_err or Exception("Groq fallo definitivo")


# ─────────────────────────────────────────────
# IMÁGENES — PEXELS
# ─────────────────────────────────────────────

# Queries de imagen por nicho — evita resultados irrelevantes (ej: playa en Ourense)
NICHE_IMAGE_QUERIES = {
    'turismo_ourense': [
        'ourense galicia spain thermal hot springs river',
        'ribeira sacra galicia sil river canyon vineyard',
        'galicia spain green valley mountains village',
        'galicia spain roman bridge cathedral historic',
        'galicia spain wine ribeiro vineyard harvest',
        'galicia spain rural tourism nature forest river',
        'ourense galicia termas aguas termales',
        'galicia spain gastronomy pulpo octopus food',
        'galicia spain semana santa procession festival',
    ],
    'ia_principiantes': [
        'artificial intelligence technology laptop screen',
        'robot technology digital future blue',
        'machine learning data visualization computer',
        'ai chatbot smartphone technology',
        'technology person learning computer',
    ],
    'prompts': [
        'chatgpt ai prompt engineering keyboard computer',
        'artificial intelligence text generation laptop',
        'person typing computer ai technology workspace',
        'creative writing technology inspiration',
    ],
    'claude': [
        'anthropic claude ai assistant technology',
        'artificial intelligence chat interface laptop',
        'ai technology professional business computer',
    ],
    'bengalas_humo': [
        'smoke bomb photography colorful outdoor',
        'color smoke flare photography creative',
        'smoke photography wedding outdoor colorful',
        'flare bomb color photography portrait',
    ],
    'drones': [
        'drone flying aerial photography blue sky',
        'dji drone quadcopter aerial camera',
        'drone aerial view landscape photography',
        'fpv drone racing pilot outdoor',
        'drone photography sunset landscape aerial',
        'quadcopter drone outdoor flight nature',
        'aerial drone view city landscape',
        'drone technology camera flying outdoor',
    ],
    'galicia_conciertos': [
        'rock concert crowd stage lights festival night',
        'music festival outdoor summer crowd stage',
        'latin music concert performance tropical stage',
        'concert singer spotlight stage performance crowd',
        'music festival field crowd summer day spain',
        'heavy metal rock concert crowd fist air stage',
        'indie music concert outdoor festival stage lights',
        'festival crowd hands up music stage night',
        'concert stage smoke lights band performance',
        'music festival audience crowd singing together',
    ],
    'lafotocm': [
        'wedding photography outdoor couple galicia',
        'wedding photographer outdoor nature ceremony',
        'family photography outdoor nature green',
        'couple photography ribeira sacra galicia',
        'drone aerial wedding photography',
        'boda fotografia exterior galicia naturaleza',
    ],
    'cataleya_nails': [
        'nail art manicure colorful design close up',
        'acrylic nails beautiful design salon',
        'gel nails elegant women hands close up',
        'nail art flowers pastel colors manicure',
        'french nails manicure elegant close up',
        'nail salon professional manicure tools',
        'ombre nails gradient pink white beautiful',
        'nail art glitter chrome metallic close up',
        'luxury manicure spa beauty salon hands',
        'nail design marble effect elegant women',
    ],
}

def _concert_image_query(keyword):
    """Convierte un keyword de concierto en una query Pexels relevante."""
    kw = keyword.lower()
    if any(w in kw for w in ['metal', 'iron maiden', 'limp bizkit', 'marilyn manson', 'resurrection', 'rock', 'punk', 'garbage']):
        return 'rock metal concert crowd stage festival headbang'
    if any(w in kw for w in ['juan luis guerra', 'romeo santos', 'prince royce', 'merengue', 'bachata', 'latin', 'salsa', 'gente de zona', 'grupo mania']):
        return 'latin music concert stage performance crowd tropical'
    if any(w in kw for w in ['gaitas', 'folk', 'tradicional', 'celta', 'celtic']):
        return 'folk music traditional outdoor festival performance'
    if any(w in kw for w in ['indie', 'atlantic fest', 'franz ferdinand', 'two door', 'carolina durante', 'planetas']):
        return 'indie rock concert outdoor festival crowd stage'
    if any(w in kw for w in ['sinsal', 'isla', 'san simon']):
        return 'music festival island outdoor stage sea nature'
    if any(w in kw for w in ['portamerica', 'rigoberta', 'hombres g', 'dani martin', 'amaia']):
        return 'pop concert outdoor festival summer crowd stage spain'
    if any(w in kw for w in ['katy perry', 'linkin park', 'dj snake', 'son do camino', 'camiño']):
        return 'music festival crowd stage lights pyrotechnics night'
    if any(w in kw for w in ['pablo alboran', 'alejandro sanz', 'pop', 'ballad']):
        return 'pop concert singer stage spotlight audience crowd'
    if any(w in kw for w in ['rap', 'hip hop', 'urban', 'reggaeton']):
        return 'hip hop rap concert stage crowd urban music'
    if any(w in kw for w in ['festival', 'fest', 'concierto', 'concert']):
        return 'music festival outdoor crowd stage lights summer'
    return 'music concert stage lights performance crowd'


def get_pexels_image(keyword, pexels_api_key, orientation='landscape', site_key=''):
    """
    Busca imagen relevante en Pexels.
    Usa queries específicas por nicho para evitar imágenes irrelevantes
    (ej: no poner playa para Ourense que es ciudad interior).
    """
    headers = {'Authorization': pexels_api_key}

    # Para conciertos: extraer query inteligente del keyword antes de las genéricas
    smart_concert_query = _concert_image_query(keyword) if site_key == 'galicia_conciertos' else None

    # Construir lista de búsquedas: keyword primero, luego queries del nicho, luego fallback genérico
    niche_queries = NICHE_IMAGE_QUERIES.get(site_key, [])
    fallback_generic = {
        'turismo_ourense': ['galicia spain nature tourism', 'spain rural tourism village'],
        'ia_principiantes': ['inteligencia artificial', 'tecnologia digital'],
        'prompts':          ['ai technology writing', 'computer keyboard creative'],
        'claude':           ['artificial intelligence assistant', 'ai technology'],
        'bengalas_humo':    ['smoke photography colorful', 'color powder explosion'],
        'cataleya_nails':   ['nail art manicure beautiful', 'gel nails salon professional'],
        'lafotocm':         ['wedding photography outdoor', 'couple photography nature'],
        'drones':           ['drone aerial photography', 'quadcopter flying outdoor'],
        'galicia_conciertos': ['music concert stage lights', 'festival crowd outdoor'],
    }.get(site_key, ['technology digital', 'business professional'])

    # Para conciertos: smart query va primero (más relevante que el keyword largo en español)
    if smart_concert_query:
        search_terms = [smart_concert_query] + niche_queries[:3] + fallback_generic
    else:
        search_terms = [keyword] + niche_queries[:3] + fallback_generic

    for term in search_terms:
        try:
            resp = requests.get(
                'https://api.pexels.com/v1/search',
                headers=headers,
                params={'query': term, 'per_page': 15, 'orientation': orientation},
                timeout=15
            )
            if resp.status_code == 200:
                photos = resp.json().get('photos', [])
                if photos:
                    photo = random.choice(photos[:8])
                    return {
                        'url_original': photo['src']['original'],
                        'url_large':    photo['src']['large2x'],
                        'url_medium':   photo['src']['large'],
                        'url_portrait': photo['src'].get('portrait', photo['src']['large2x']),
                        'alt':          photo.get('alt') or keyword,
                        'photographer': photo.get('photographer', '')
                    }
        except Exception:
            continue
    return None


def upload_image_to_wp(image_url, alt_text, wp_url, wp_user, wp_pass):
    clean = wp_url.rstrip('/')
    img_data = None
    for attempt in range(3):
        try:
            r = requests.get(image_url, timeout=30)
            if r.status_code == 200:
                img_data = r.content
                break
        except Exception:
            if attempt < 2:
                time.sleep(5)
    if not img_data:
        return None, None

    for attempt in range(3):
        try:
            resp = requests.post(
                f'{clean}/wp-json/wp/v2/media',
                headers={
                    'Content-Disposition': 'attachment; filename=imagen-articulo.jpg',
                    'Content-Type': 'image/jpeg'
                },
                data=img_data,
                auth=(wp_user, wp_pass),
                timeout=60
            )
            if resp.status_code in (200, 201):
                media = resp.json()
                media_id = media['id']
                hosted_url = media.get('source_url', '')
                try:
                    requests.post(
                        f'{clean}/wp-json/wp/v2/media/{media_id}',
                        json={'alt_text': alt_text},
                        auth=(wp_user, wp_pass),
                        timeout=15
                    )
                except Exception:
                    pass
                return media_id, hosted_url
            if attempt < 2:
                time.sleep(5)
        except Exception:
            if attempt < 2:
                time.sleep(5)
    print('     Advertencia: no se pudo subir la imagen a WordPress')
    return None, None


# ─────────────────────────────────────────────
# WORDPRESS — CATEGORÍAS, TAGS, PUBLICACIÓN
# ─────────────────────────────────────────────

def get_or_create_category(name, wp_url, wp_user, wp_pass):
    clean = wp_url.rstrip('/')
    try:
        r = requests.get(
            f'{clean}/wp-json/wp/v2/categories',
            params={'search': name, 'per_page': 5},
            auth=(wp_user, wp_pass), timeout=10
        )
        if r.status_code == 200 and r.json():
            return r.json()[0]['id']
        r2 = requests.post(
            f'{clean}/wp-json/wp/v2/categories',
            json={'name': name},
            auth=(wp_user, wp_pass), timeout=10
        )
        if r2.status_code == 201:
            return r2.json()['id']
    except Exception:
        pass
    return 1


def get_or_create_tags(tag_names, wp_url, wp_user, wp_pass):
    clean = wp_url.rstrip('/')
    ids = []
    for name in tag_names[:5]:
        try:
            r = requests.post(
                f'{clean}/wp-json/wp/v2/tags',
                json={'name': name},
                auth=(wp_user, wp_pass), timeout=10
            )
            if r.status_code in (200, 201):
                ids.append(r.json()['id'])
        except Exception:
            pass
    return ids


AFFILIATE_BLOCKS = {
    'turismo_ourense': """
<div style="background:#f0f7f0;border-left:4px solid #2d6a4f;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#2d6a4f;margin-top:0">🏨 ¿Buscas alojamiento en Ourense?</h3>
<p>Compara precios y encuentra los mejores hoteles, casas rurales y apartamentos con cancelación gratuita.</p>
<p><a href="https://www.booking.com/searchresults.es.html?ss=Ourense" target="_blank" rel="noopener sponsored" style="background:#003580;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold">Ver alojamientos en Ourense →</a></p>
<p style="font-size:12px;color:#666">*Enlace de afiliado. Sin coste extra para ti.</p>
</div>""",
    'bengalas_humo': """
<div style="background:#fff8f0;border-left:4px solid #e07b00;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#e07b00;margin-top:0">🛒 Consigue tus bengalas de humo</h3>
<p>Las mejores bengalas de colores para fotografía, bodas y eventos. Envío rápido a toda España.</p>
<p><a href="https://www.amazon.es/s?k=bengalas+humo+colores+fotografia" target="_blank" rel="noopener sponsored" style="background:#ff9900;color:#111;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold">Ver bengalas en Amazon →</a></p>
<p style="font-size:12px;color:#666">*Enlace de afiliado Amazon. Sin coste extra para ti.</p>
</div>""",
    'ia_principiantes': """
<div style="background:#f0f4ff;border-left:4px solid #4f46e5;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#4f46e5;margin-top:0">Las herramientas de IA que uso cada día</h3>
<p>Después de probar más de 40 herramientas, estas son las que realmente merecen tu tiempo y dinero:</p>
<ul style="margin:10px 0;line-height:1.8">
<li><strong><a href="https://claude.ai" target="_blank" rel="noopener sponsored">Claude Pro (Anthropic)</a></strong> — El mejor para escribir, analizar y programar. Desde €18/mes.</li>
<li><strong><a href="https://chatgpt.com" target="_blank" rel="noopener sponsored">ChatGPT Plus</a></strong> — Acceso a GPT-4o y generación de imágenes. Desde €20/mes.</li>
<li><strong><a href="https://www.hostinger.es" target="_blank" rel="noopener sponsored">Hostinger</a></strong> — Hosting con IA integrada para crear tu web. Desde €2.99/mes.</li>
<li><strong><a href="https://www.canva.com/es_es/pro/" target="_blank" rel="noopener sponsored">Canva Pro</a></strong> — Diseño con IA: elimina fondos, genera imágenes. Desde €12/mes.</li>
</ul>
<p style="font-size:12px;color:#666;margin-top:10px">*Enlaces de afiliado. Sin coste extra para ti. Nos ayuda a seguir publicando contenido gratuito.</p>
</div>""",
    'prompts': """
<div style="background:#f0fff4;border-left:4px solid #059669;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#059669;margin-top:0">Herramientas para sacar el máximo a tus prompts</h3>
<p>Estas plataformas amplifican el resultado de cualquier prompt que uses:</p>
<ul style="margin:10px 0;line-height:1.8">
<li><strong><a href="https://claude.ai" target="_blank" rel="noopener sponsored">Claude Pro</a></strong> — 200K tokens de contexto: ideal para prompts largos y documentos. €18/mes.</li>
<li><strong><a href="https://chatgpt.com" target="_blank" rel="noopener sponsored">ChatGPT Plus</a></strong> — GPT-4o + Custom GPTs para automatizar flujos de trabajo. €20/mes.</li>
<li><strong><a href="https://www.notion.so/es-es/product/ai" target="_blank" rel="noopener sponsored">Notion AI</a></strong> — Prompts integrados en tu base de conocimiento. +€10/mes.</li>
</ul>
<p style="font-size:12px;color:#666;margin-top:10px">*Algunos son enlaces de afiliado. Sin coste extra para ti.</p>
</div>""",
    'claude': """
<div style="background:#faf5ff;border-left:4px solid #7c3aed;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#7c3aed;margin-top:0">¿Vale la pena pagar Claude Pro?</h3>
<p>Si usas Claude más de 20 minutos al día, la respuesta es sí. Esto es lo que incluye la versión de pago:</p>
<ul style="margin:10px 0;line-height:1.8">
<li>Acceso a Claude Opus y Sonnet sin límites de uso</li>
<li>Contexto de 200,000 tokens (equivalente a 150,000 palabras)</li>
<li>Projects: memoria persistente entre conversaciones</li>
<li>Claude Code: programa sin experiencia previa</li>
</ul>
<p><a href="https://claude.ai/upgrade" target="_blank" rel="noopener sponsored" style="background:#7c3aed;color:white;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;margin-top:8px">Probar Claude Pro gratis 1 mes →</a></p>
<p style="font-size:12px;color:#888;margin-top:8px">*Enlace de afiliado. Sin coste extra para ti.</p>
</div>""",
    'drones': """
<div style="background:#0f172a;border-left:4px solid #2563eb;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#60a5fa;margin-top:0">🚁 Encuentra el mejor precio en Amazon</h3>
<p style="color:#94a3b8">Los drones que analizamos en FlyDrones.es los puedes comprar en Amazon España con entrega rápida y garantía oficial.</p>
<p><a href="https://www.amazon.es/s?k=drones+dji&tag=flydrones-21" target="_blank" rel="noopener sponsored" style="background:#ff9900;color:#000;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block">Ver drones en Amazon →</a></p>
<p style="font-size:12px;color:#64748b">*Enlace de afiliado Amazon. Sin coste extra para ti. Nos ayuda a seguir haciendo reviews independientes.</p>
</div>""",
}

def get_affiliate_block(kw_key):
    return AFFILIATE_BLOCKS.get(kw_key, '')


def publish_to_wordpress(article, image_url, image_alt, cat_id, tag_ids, wp_url, wp_user, wp_pass, media_id=None, author_id=None, affiliate_block=''):
    clean = wp_url.rstrip('/')

    content = article['contenido_html']

    # Inyectar bloque de afiliados antes de la conclusión (o al final)
    if affiliate_block:
        if '<h2' in content:
            # Insertar antes de la última sección H2
            last_h2 = content.rfind('<h2')
            content = content[:last_h2] + affiliate_block + content[last_h2:]
        else:
            content += affiliate_block

    if image_url:
        alt = (image_alt or article['titulo_seo']).replace('"', '&quot;')
        # Imagen 1200px mínimo para Google Discover (large2x = 1280px ya está configurado)
        img_html = (
            f'<figure class="wp-block-image size-large">'
            f'<img src="{image_url}" alt="{alt}" '
            f'width="1280" height="853" '
            f'style="width:100%;height:auto;border-radius:8px;margin-bottom:1.5em"/>'
            f'</figure>\n'
        )
        content = img_html + content

    post = {
        'title':      article['titulo_seo'],
        'content':    content,
        'excerpt':    article['meta_descripcion'],
        'slug':       article['slug'],
        'status':     'publish',
        'categories': [cat_id],
        'tags':       tag_ids,
    }
    if author_id:
        post['author'] = author_id

    url = f'{clean}/wp-json/wp/v2/posts'
    resp = None
    for attempt in range(3):
        try:
            resp = requests.post(url, json=post, auth=(wp_user, wp_pass), timeout=60)
            if resp.status_code == 201:
                break
            if resp.status_code == 404 and attempt == 0:
                # Fallback for sites without pretty permalinks
                url = f'{clean}/index.php?rest_route=/wp/v2/posts'
                continue
            if resp.status_code >= 500 and attempt < 2:
                time.sleep(10)
                continue
            break
        except Exception as e:
            if attempt < 2:
                time.sleep(10)
                continue
            raise

    if resp is None or resp.status_code != 201:
        code = resp.status_code if resp is not None else 'N/A'
        body = resp.text[:300] if resp is not None else ''
        raise Exception(f"WordPress {code}: {body}")

    post_data = resp.json()
    # Add featured_media via separate PATCH (direct POST causes PHP fatal on some hosts)
    if media_id:
        post_id = post_data.get('id')
        if post_id:
            try:
                requests.post(
                    f'{clean}/wp-json/wp/v2/posts/{post_id}',
                    json={'featured_media': media_id},
                    auth=(wp_user, wp_pass), timeout=20
                )
            except Exception:
                pass
    return post_data


# ─────────────────────────────────────────────
# PINTEREST
# ─────────────────────────────────────────────

def get_pinterest_boards(access_token):
    resp = requests.get(
        'https://api.pinterest.com/v5/boards',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'page_size': 25},
        timeout=15
    )
    if resp.status_code == 200:
        return resp.json().get('items', [])
    raise Exception(f"Pinterest boards error {resp.status_code}: {resp.text[:200]}")


PINTEREST_HASHTAGS = {
    'ia_principiantes': '#InteligenciaArtificial #IA #ChatGPT #AprendeIA #TecnologiaIA #AIEspanol #Automatizacion #ProductividadIA',
    'prompts':          '#Prompts #PromptEngineering #ChatGPT #Claude #IA #PromptsChatGPT #AITips #InteligenciaArtificial',
    'claude':           '#Claude #Anthropic #ChatGPT #IA #ClaudeAI #InteligenciaArtificial #AITool #TechEspanol',
    'drones':           '#Drones #DJI #FotografiaAerea #Drone #DJIMini #FPV #PhotographyDrone #AerialPhotography #DroneLife #DroneEspaña',
    'turismo_ourense':  '#TurismoOurense #Ourense #Galicia #TermasOurense #ViajarEspaña #TurismoGalicia #RibeiraSacra',
    'bengalas_humo':    '#BengalasDeHumo #Fotografia #HumoColores #FotografiaCreativa #SmokeBomb #ColorSmoke',
}

FB_COOLDOWN_MINS = 90   # minutos mínimos entre posts en Facebook
FB_LOCK_MAX_MINS = 10   # si el lock lleva más de 10 min asumimos proceso colgado

# Archivos de cooldown/lock por página
_FB_STATE = {
    'turismo':  {
        'cooldown': os.path.join(BASE_DIR, 'fb_last_post.txt'),
        'lock':     os.path.join(BASE_DIR, 'fb_posting.lock'),
    },
    'tribu_ia': {
        'cooldown': os.path.join(BASE_DIR, 'fb_tribu_last_post.txt'),
        'lock':     os.path.join(BASE_DIR, 'fb_tribu_posting.lock'),
    },
    'galicia_conciertos': {
        'cooldown': os.path.join(BASE_DIR, 'fb_galicia_last_post.txt'),
        'lock':     os.path.join(BASE_DIR, 'fb_galicia_posting.lock'),
    },
}

# Mantener compatibilidad con referencias antiguas
FB_COOLDOWN_FILE = _FB_STATE['turismo']['cooldown']
FB_LOCK_FILE     = _FB_STATE['turismo']['lock']


def _fb_acquire_and_check(page_key='turismo'):
    """
    Verificación atómica de cooldown + reserva de turno.
    Escribe el timestamp ANTES de llamar a la API para que cualquier otra
    instancia concurrente vea el bloqueo aunque esta aún no haya terminado.
    Devuelve True si se puede publicar (lock activo). False = saltar.
    page_key: 'turismo' | 'tribu_ia'
    """
    state       = _FB_STATE.get(page_key, _FB_STATE['turismo'])
    cooldown_f  = state['cooldown']
    lock_f      = state['lock']

    # 1. Verificar cooldown
    if os.path.exists(cooldown_f):
        try:
            with open(cooldown_f, encoding='utf-8') as f:
                last_ts = float(f.read().strip())
            elapsed = (datetime.now().timestamp() - last_ts) / 60
            if elapsed < FB_COOLDOWN_MINS:
                print(f'Facebook [{page_key}] cooldown: último post hace {elapsed:.0f} min '
                      f'(mín {FB_COOLDOWN_MINS} min). Saltando.')
                return False
        except Exception:
            pass

    # 2. Crear lock file atómicamente (falla si ya existe → otro proceso publicando)
    try:
        fd = os.open(lock_f, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(datetime.now().timestamp()).encode())
        os.close(fd)
    except FileExistsError:
        try:
            age_mins = (datetime.now().timestamp() - os.path.getmtime(lock_f)) / 60
            if age_mins > FB_LOCK_MAX_MINS:
                os.remove(lock_f)
                fd = os.open(lock_f, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(datetime.now().timestamp()).encode())
                os.close(fd)
                print(f'Facebook [{page_key}]: lock antiguo ({age_mins:.0f} min) eliminado, reintentando.')
            else:
                print(f'Facebook [{page_key}]: otra instancia publicando (lock {age_mins:.0f} min). Saltando.')
                return False
        except Exception:
            return False

    return True


def _fb_release_lock(page_key='turismo'):
    """Libera el lock file. Llamar siempre al terminar (éxito o error)."""
    lock_f = _FB_STATE.get(page_key, _FB_STATE['turismo'])['lock']
    try:
        os.remove(lock_f)
    except Exception:
        pass


def _fb_set_cooldown(page_key='turismo'):
    """Escribe el timestamp de cooldown. Llamar SOLO tras post exitoso."""
    cooldown_f = _FB_STATE.get(page_key, _FB_STATE['turismo'])['cooldown']
    try:
        with open(cooldown_f, 'w', encoding='utf-8') as f:
            f.write(str(datetime.now().timestamp()))
    except Exception:
        pass


FB_HASHTAGS = {
    'turismo':  '#TurismoOurense #Ourense #Galicia #TermasOurense #VeranoGalicia #GastronomiaGallega #RibeiraSacra #ViajarEspaña',
    'tribu_ia': '#InteligenciaArtificial #IA #ChatGPT #Claude #Gemini #AprendeIA #AutomatizaIA #TribuIA',
    'galicia_conciertos': '#GaliciaConciertos #Conciertos #Festivales #Galicia #MusicaEnDirecto #OcioGalicia #FestivalesGalicia',
}

# Rotación: link(1 vez/día máx) → imagen → imagen → pregunta → dato → imagen → imagen → pregunta
# El link solo sale si ese día no se ha publicado ya uno con link para esta página
FB_FORMAT_SEQUENCE = ['link', 'imagen', 'imagen', 'pregunta', 'dato', 'imagen', 'imagen', 'pregunta']
FB_FORMAT_FILE = os.path.join(BASE_DIR, 'fb_format_rotation.json')


def _get_next_fb_format(page_key):
    """Devuelve el siguiente formato. Máximo 1 post con link por día y página."""
    try:
        if os.path.exists(FB_FORMAT_FILE):
            with open(FB_FORMAT_FILE, 'r') as f:
                state = json.load(f)
        else:
            state = {}
        idx = state.get(page_key, 0)
        fmt = FB_FORMAT_SEQUENCE[idx % len(FB_FORMAT_SEQUENCE)]

        # Si toca 'link', verificar que no se haya publicado uno hoy ya
        if fmt == 'link':
            today = __import__('datetime').date.today().isoformat()
            last_link_date = state.get(f'{page_key}_last_link_date', '')
            if last_link_date == today:
                fmt = 'dato'  # ya hubo link hoy → post sin link
            else:
                state[f'{page_key}_last_link_date'] = today

        state[page_key] = (idx + 1) % len(FB_FORMAT_SEQUENCE)
        with open(FB_FORMAT_FILE, 'w') as f:
            json.dump(state, f)
        return fmt
    except Exception:
        return 'dato'


def _fb_generate_summary(title, excerpt, page_key, groq_api_key):
    """Genera resumen largo nativo para Facebook (sin link) usando Groq."""
    try:
        import groq as groq_lib
        client = groq_lib.Groq(api_key=groq_api_key)
        prompts = {
            'turismo': f"Eres el community manager de Turismo Ourense. Basándote en este titular y extracto de un artículo, escribe un texto nativo para Facebook de 150-200 palabras que cuente la historia de forma atractiva SIN incluir ningún enlace. Termina con 2-3 emojis relevantes.\n\nTítulo: {title}\nExtracto: {excerpt}",
            'tribu_ia': f"Eres el community manager de Tribu.IA. Basándote en este titular y extracto, escribe un post nativo para Facebook de 150-200 palabras que explique la idea principal de forma práctica y directa SIN incluir ningún enlace. Termina con 2-3 emojis.\n\nTítulo: {title}\nExtracto: {excerpt}",
            'galicia_conciertos': f"Eres el community manager de Galicia Conciertos. Basándote en este titular y extracto, escribe un texto nativo para Facebook de 150-200 palabras que genere emoción y ganas de ir al evento SIN incluir ningún enlace. Incluye detalles como fecha, lugar y ambiente. Termina con 2-3 emojis.\n\nTítulo: {title}\nExtracto: {excerpt}",
        }
        prompt = prompts.get(page_key, prompts['turismo'])
        resp = client.chat.completions.create(
            model='openai/gpt-oss-20b',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=350, temperature=0.8
        )
        content = resp.choices[0].message.content
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        return content
    except Exception:
        return excerpt[:400]


def _fb_generate_question(title, page_key, groq_api_key):
    """Genera una pregunta de engagement para Facebook usando Groq."""
    try:
        import groq as groq_lib
        client = groq_lib.Groq(api_key=groq_api_key)
        prompts = {
            'turismo': f"Eres el community manager de Turismo Ourense. Basándote en este titular, escribe UN post de Facebook con una pregunta directa que invite a los seguidores a comentar su experiencia o opinión. Máximo 3 frases + pregunta + 2 emojis. SIN enlaces.\n\nTítulo: {title}",
            'tribu_ia': f"Eres el community manager de Tribu.IA sobre inteligencia artificial. Basándote en este titular, escribe UN post de Facebook con una pregunta directa que genere debate o comentarios. Máximo 3 frases + pregunta + 2 emojis. SIN enlaces.\n\nTítulo: {title}",
            'galicia_conciertos': f"Eres el community manager de Galicia Conciertos. Basándote en este titular sobre un concierto o festival, escribe UN post de Facebook con una pregunta que invite a los fans a comentar si van, con quién, sus expectativas. Máximo 3 frases + pregunta + 2 emojis. SIN enlaces.\n\nTítulo: {title}",
        }
        prompt = prompts.get(page_key, prompts['turismo'])
        resp = client.chat.completions.create(
            model='openai/gpt-oss-20b',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=150, temperature=0.9
        )
        content = resp.choices[0].message.content
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        return content
    except Exception:
        return f"¿Qué os parece este tema? ¡Comentad! 👇"


def post_to_facebook(title, excerpt, article_url, image_url, page_id, page_token,
                     wp_url=None, wp_user=None, wp_pass=None, page_key='turismo',
                     groq_api_key=None):
    """Publica en Facebook rotando entre 3 formatos: link, imagen+resumen, pregunta."""
    if not page_token or 'PENDIENTE' in str(page_token):
        return ''
    if not _fb_acquire_and_check(page_key):
        return ''
    try:
        hashtags = FB_HASHTAGS.get(page_key, '#IA #InteligenciaArtificial')
        fmt      = _get_next_fb_format(page_key)
        print(f'(formato {fmt})', end=' ', flush=True)

        # ── Construir mensaje según formato ──────────────────────────
        # NOTA: Nunca incluir el link del artículo — Facebook penaliza posts con URLs
        # Máximo 1 post con link por día — el resto sin URL para mejor alcance orgánico
        if fmt == 'pregunta':
            message  = _fb_generate_question(title, page_key, groq_api_key)
            message += f'\n\n{hashtags}'
        elif fmt == 'imagen':
            resumen  = _fb_generate_summary(title, excerpt, page_key, groq_api_key)
            message  = f'{resumen}\n\n{hashtags}'
        elif fmt == 'link':
            gancho  = excerpt[:180].rstrip() + ('...' if len(excerpt) > 180 else '')
            message = (
                f"📰 {title}\n\n"
                f"{gancho}\n\n"
                f"🔗 Leer artículo completo:\n{article_url}\n\n"
                f"{hashtags}"
            )
        else:  # dato — texto engaging sin URL
            gancho  = excerpt[:220].rstrip() + ('...' if len(excerpt) > 220 else '')
            message = (
                f"📍 {title}\n\n"
                f"{gancho}\n\n"
                f"💬 ¿Lo conocías? Cuéntanos en comentarios 👇\n\n"
                f"{hashtags}"
            )

        # ── Descargar imagen ─────────────────────────────────────────
        photo_id = None

        def _try_download(url):
            if not url:
                return None
            try:
                resp = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
                if resp.status_code == 200 and len(resp.content) > 5000:
                    return resp.content
                print(f'Facebook img descarga fallo ({resp.status_code}, {len(resp.content)} bytes): {url[:80]}')
            except Exception as e:
                print(f'Facebook img descarga error: {e}')
            return None

        img_bytes = _try_download(image_url)

        # Fallback: buscar imagen featured vía WP REST API
        if not img_bytes and wp_url and wp_user and wp_pass:
            try:
                slug = article_url.rstrip('/').split('/')[-1]
                r_posts = requests.get(
                    f'{wp_url.rstrip("/")}/wp-json/wp/v2/posts',
                    params={'slug': slug, '_fields': 'featured_media', 'per_page': 1},
                    auth=(wp_user, wp_pass), timeout=10
                )
                if r_posts.ok and r_posts.json():
                    media_id = r_posts.json()[0].get('featured_media')
                    if media_id:
                        r_media = requests.get(
                            f'{wp_url.rstrip("/")}/wp-json/wp/v2/media/{media_id}',
                            params={'_fields': 'source_url'},
                            auth=(wp_user, wp_pass), timeout=10
                        )
                        if r_media.ok:
                            fallback_url = r_media.json().get('source_url', '')
                            img_bytes = _try_download(fallback_url)
                            if img_bytes:
                                print('(imagen WP recuperada via API)', end=' ', flush=True)
            except Exception as e:
                print(f'Facebook img fallback WP error: {e}')

        # ── Subir imagen si hay ───────────────────────────────────────
        if img_bytes:
            r_photo = requests.post(
                f'https://graph.facebook.com/v22.0/{page_id}/photos',
                data={'published': 'false', 'access_token': page_token},
                files={'source': ('photo.jpg', img_bytes, 'image/jpeg')},
                timeout=60
            )
            if r_photo.status_code == 200:
                photo_id = r_photo.json().get('id')
            else:
                print(f'Facebook foto upload error {r_photo.status_code}: {r_photo.text[:120]}')
        else:
            if fmt != 'pregunta':
                print('Facebook AVISO: sin imagen disponible', end=' ', flush=True)

        # ── Publicar ─────────────────────────────────────────────────
        # Máximo 1 link por día — el resto sin URL para mejor alcance orgánico
        post_data = {'message': message, 'access_token': page_token}
        if photo_id:
            post_data['attached_media'] = json.dumps([{'media_fbid': photo_id}])
        elif fmt == 'link' and not photo_id:
            post_data['link'] = article_url

        r = requests.post(
            f'https://graph.facebook.com/v22.0/{page_id}/feed',
            data=post_data, timeout=25
        )
        if r.status_code == 200:
            post_id = r.json().get('id', '')
            _fb_set_cooldown(page_key)
            _fb_release_lock(page_key)
            return f'https://www.facebook.com/{post_id}'
        else:
            print(f'Facebook feed error {r.status_code}: {r.text[:400]}')
            _fb_release_lock(page_key)
    except Exception as e:
        print(f'Facebook error: {e}')
        _fb_release_lock(page_key)
    return ''


def create_pinterest_pin(title, description, article_url, image_url, board_id, access_token, site_key=''):
    hashtags = PINTEREST_HASHTAGS.get(site_key, '#InteligenciaArtificial #IA #ChatGPT')

    # Descripción optimizada: beneficio + CTA + hashtags
    pin_desc = f"{description}\n\n🔗 Lee el artículo completo (link en bio o en el pin)\n\n{hashtags}"

    payload = {
        'title':        title[:100],
        'description':  pin_desc[:500],
        'link':         article_url,
        'board_id':     board_id,
        'alt_text':     title[:500],
        'media_source': {
            'source_type': 'image_url',
            'url':         image_url
        }
    }
    resp = requests.post(
        'https://api.pinterest.com/v5/pins',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type':  'application/json'
        },
        json=payload,
        timeout=30
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        return f"https://pinterest.com/pin/{data.get('id', '')}"
    raise Exception(f"Pinterest pin error {resp.status_code}: {resp.text[:300]}")


# ─────────────────────────────────────────────
# LOG + KEYWORDS
# ─────────────────────────────────────────────

def log_publication(site, title, url, keyword, pinterest_url=''):
    exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(['Fecha', 'Web', 'Título', 'URL Artículo', 'URL Pinterest', 'Keyword'])
        w.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            site, title, url, pinterest_url, keyword
        ])


def mark_keyword_used(keywords_data, key, keyword):
    if keyword in keywords_data.get(key, []):
        keywords_data[key].remove(keyword)
        used_key = f'{key}_usadas'
        if used_key not in keywords_data:
            keywords_data[used_key] = []
        keywords_data[used_key].append(keyword)

        # NO reciclar keywords agotadas — lanzar trend_hunter para buscar temas nuevos
        if not keywords_data[key]:
            print(f'     Keywords agotadas en {key}. Lanzando trend_hunter para buscar temas nuevos...')
            _auto_refill_keywords(keywords_data, key)
            # Si trend_hunter tampoco encontró nada, dejar vacío (no reciclar duplicados)

    save_json(KEYWORDS_FILE, keywords_data)


# ─────────────────────────────────────────────
# ANTI-DUPLICADOS — VERIFICACIÓN ANTES DE PUBLICAR
# ─────────────────────────────────────────────

def _normalize_title(t):
    """Normaliza título para comparación: minúsculas, sin puntuación, sin stopwords."""
    t = re.sub(r'[^\w\s]', '', t.lower())
    words = [w for w in t.split() if len(w) > 3 and w not in STOP_ES and w not in CLUSTER_STOP]
    return set(words)


def get_all_published_titles(wp_url, wp_user, wp_pass):
    """Carga TODOS los títulos publicados para detectar duplicados antes de publicar."""
    clean = wp_url.rstrip('/')
    all_titles = []
    page = 1
    while True:
        try:
            r = requests.get(
                f'{clean}/wp-json/wp/v2/posts',
                auth=(wp_user, wp_pass),
                params={'per_page': 100, 'page': page, 'status': 'publish',
                        '_fields': 'title,slug'},
                timeout=20
            )
            if not r.ok:
                break
            batch = r.json()
            if not batch:
                break
            for p in batch:
                all_titles.append({
                    'title': p.get('title', {}).get('rendered', ''),
                    'slug': p.get('slug', ''),
                })
            if len(batch) < 100:
                break
            page += 1
        except Exception:
            break
    return all_titles


def is_duplicate(new_title, new_slug, existing):
    """
    Devuelve (True, motivo) si el artículo ya existe, (False, '') si es nuevo.
    Compara por slug exacto y por similitud semántica de título (>60% palabras en común).
    """
    slug_clean = re.sub(r'-\d+$', '', new_slug)  # quitar sufijos numéricos al comparar
    new_words = _normalize_title(new_title)

    for ex in existing:
        # 1. Slug idéntico (sin sufijo numérico)
        ex_slug_clean = re.sub(r'-\d+$', '', ex['slug'])
        if slug_clean and slug_clean == ex_slug_clean:
            return True, f"slug duplicado: {ex['slug']}"

        # 2. Similitud de título >= 65%
        ex_words = _normalize_title(ex['title'])
        if not new_words or not ex_words:
            continue
        overlap = len(new_words & ex_words)
        similarity = overlap / max(len(new_words), len(ex_words))
        if similarity >= 0.65:
            return True, f"título similar ({similarity:.0%}) a: «{ex['title'][:60]}»"

    return False, ''


# ─────────────────────────────────────────────
# BUCLE PRINCIPAL
# ─────────────────────────────────────────────

def run(articles_per_site=3, only_site=None):
    # Lock global — evita que dos instancias publiquen a la vez (causa duplicados)
    try:
        fd = os.open(PUBLISHER_LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError:
        try:
            age_mins = (datetime.now().timestamp() - os.path.getmtime(PUBLISHER_LOCK)) / 60
            if age_mins < 30:
                print(f"Ya hay una instancia del publisher corriendo ({age_mins:.0f} min). Saliendo para evitar duplicados.")
                return
            os.remove(PUBLISHER_LOCK)
            fd = os.open(PUBLISHER_LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
        except Exception:
            return

    try:
        _run_inner(articles_per_site, only_site=only_site)
    finally:
        try:
            os.remove(PUBLISHER_LOCK)
        except Exception:
            pass


def _run_inner(articles_per_site=3, only_site=None):
    config        = load_json(CONFIG_FILE)
    keywords_data = load_json(KEYWORDS_FILE)

    groq_key      = config['groq_api_key']
    pexels_key    = config['pexels_api_key']
    sites         = config['sites']

    # Filtrar por site si se pasa --only
    if only_site:
        sites = [s for s in sites if only_site.lower() in s['url'].lower()
                 or only_site.lower() in s['keywords_key'].lower()
                 or only_site.lower() in s['name'].lower()]
        if not sites:
            print(f"ERROR: no se encontro ninguna web que coincida con '{only_site}'")
            return

    use_pinterest = pinterest_configured(config)
    pinterest_cfg = config.get('pinterest', {})

    total_ok  = 0
    total_err = 0

    print(f"\n{'='*54}")
    print(f"  AUTO-PUBLISHER IA  ·  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*54}")
    print(f"  Webs: {len(sites)}  ·  Articulos por web: {articles_per_site}")
    if only_site:
        print(f"  MODO: solo '{sites[0]['name']}'")
    print(f"  SEO Engine: enlaces internos + schema JSON-LD + pings")
    print(f"  Pinterest: {'Activo' if use_pinterest else 'Pendiente configurar'}")
    print(f"{'='*54}\n")

    for site in sites:
        name    = site['name']
        kw_key  = site['keywords_key']
        pin_key = site.get('pinterest_board_key', kw_key)
        wp_url  = site['url']
        wp_user = site['wp_user']
        wp_pass = site['wp_password']

        if not keywords_data.get(kw_key):
            print(f"  {name}: Sin keywords disponibles. Saltando.\n")
            continue

        print(f"  {name}")
        print(f"    {wp_url}")

        # Carga artículos recientes para enlazado interno y clustering
        print(f"    → Cargando articulos publicados para SEO interno...", end=' ', flush=True)
        recent_articles = get_recent_articles(wp_url, wp_user, wp_pass, limit=25)
        print(f"{len(recent_articles)} articulos")

        # Carga TODOS los títulos para detección de duplicados
        print(f"    → Cargando títulos para anti-duplicados...", end=' ', flush=True)
        all_published = get_all_published_titles(wp_url, wp_user, wp_pass)
        print(f"{len(all_published)} títulos cargados")

        published = 0

        for i in range(articles_per_site):
            if not keywords_data.get(kw_key):
                break

            # Selección inteligente de keyword (topic clustering)
            keyword = select_smart_keyword(keywords_data, kw_key, recent_articles)

            # Marcar keyword como usada AHORA (antes de generar) para que otra
            # instancia concurrente no la reutilice aunque esta falle a mitad
            mark_keyword_used(keywords_data, kw_key, keyword)

            try:
                print(f"\n    [{i+1}/{articles_per_site}] Keyword: «{keyword}»")

                # Artículos relacionados para enlazado interno
                related = find_related_articles(keyword, recent_articles, max_results=3)
                if related:
                    print(f"        Links internos disponibles: {len(related)}")

                # 1. GENERAR ARTÍCULO
                print(f"        → Generando articulo con Groq...", end=' ', flush=True)
                niche_lower = site.get('niche_context', '').lower()
                site_is_tech = any(w in niche_lower for w in [
                    'ia ', 'inteligencia', 'prompt', 'claude', 'chatgpt', 'drone',
                    'tech', 'software', 'automatiz', 'saas', 'herramienta', 'dron'
                ])
                article = generate_with_fallback(
                    keyword, site['niche_context'], name, groq_key,
                    related_articles=related, is_tech=site_is_tech
                )
                print(f"OK")
                print(f"        Titulo: {article['titulo_seo'][:60]}...")

                # ANTI-DUPLICADOS: verificar antes de publicar
                dup, reason = is_duplicate(article['titulo_seo'], article['slug'], all_published)
                if dup:
                    print(f"        DUPLICADO DETECTADO — saltando: {reason}")
                    continue

                # 2. IMAGEN
                image_url      = None
                image_alt      = None
                hosted_img_url = None
                media_id_wp    = None
                print(f"        → Buscando imagen Pexels...", end=' ', flush=True)
                img = get_pexels_image(keyword, pexels_key, site_key=kw_key)

                if img:
                    image_url = img['url_large']
                    image_alt = img['alt']
                    print(f"OK  Subiendo a WordPress...", end=' ', flush=True)
                    media_id_wp, hosted_img_url = upload_image_to_wp(
                        image_url, image_alt, wp_url, wp_user, wp_pass
                    )
                    if hosted_img_url:
                        print('OK')
                    else:
                        print('(upload fallido, sin imagen destacada)')
                else:
                    print('(no encontrada)')

                # 3. CATEGORÍA Y ETIQUETAS
                cat_id  = get_or_create_category(article.get('categoria', 'IA'), wp_url, wp_user, wp_pass)
                tag_ids = get_or_create_tags(article.get('tags', []), wp_url, wp_user, wp_pass)

                # 4. SCHEMA MARKUP — al FINAL para no contaminar el excerpt
                temp_url = f"{wp_url.rstrip('/')}/{article['slug']}/"
                schema_html = build_schema_markup(
                    article, temp_url, name, wp_url,
                    hosted_img_url or image_url,
                    site_key=kw_key
                )
                article['contenido_html'] = article['contenido_html'] + schema_html

                # 5. PUBLICAR EN WORDPRESS
                print(f"        → Publicando en WordPress...", end=' ', flush=True)
                riker_id       = site.get('riker_author_id')
                affiliate_html = get_affiliate_block(kw_key)
                # no_featured_media: evita WP 500 en instalaciones que no soportan PATCH featured_media
                media_to_set = None if site.get('no_featured_media') else media_id_wp
                result   = publish_to_wordpress(
                    article, hosted_img_url, image_alt, cat_id, tag_ids,
                    wp_url, wp_user, wp_pass, media_id=media_to_set,
                    author_id=riker_id, affiliate_block=affiliate_html
                )
                post_url = result.get('link', '')
                print(f"OK")
                print(f"        URL: {post_url}")

                # Añadir al cache de títulos publicados para evitar futuros duplicados
                all_published.append({'title': article['titulo_seo'], 'slug': article['slug']})

                # 6. PING A BUSCADORES + INDEXNOW
                print(f"        → Ping sitemap:", end=' ', flush=True)
                ping_search_engines(wp_url)
                if post_url:
                    submit_indexnow(post_url, wp_url)

                # 7. PINTEREST — imagen vertical (2:3) para mayor alcance
                pin_url = ''
                if use_pinterest:
                    board_id = pinterest_cfg.get('boards', {}).get(pin_key, '')
                    if board_id and 'PENDIENTE' not in board_id:
                        try:
                            print(f"        → Creando pin en Pinterest...", end=' ', flush=True)
                            # Busca imagen vertical específica para Pinterest (mejor CTR)
                            pin_img = get_pexels_image(keyword, pexels_key, orientation='portrait', site_key=kw_key)
                            pin_image_url = pin_img['url_portrait'] if pin_img else image_url
                            if not pin_image_url:
                                raise Exception("Sin imagen para Pinterest")
                            pin_url = create_pinterest_pin(
                                title        = article['titulo_seo'],
                                description  = article.get('descripcion_pinterest', article['meta_descripcion']),
                                article_url  = post_url,
                                image_url    = pin_image_url,
                                board_id     = board_id,
                                access_token = pinterest_cfg['access_token'],
                                site_key     = kw_key
                            )
                            print(f"OK  {pin_url}")
                        except Exception as pe:
                            print(f"Error: {str(pe)[:80]}")

                # 8. FACEBOOK
                groq_key = config.get('groq_api_key', '')

                # Turismo Ourense → página propia
                if 'turismoourense' in wp_url:
                    fb_page  = config.get('facebook_page_id', '')
                    fb_token = config.get('facebook_page_token', '')
                    if fb_page and fb_token:
                        print(f"        → Publicando en Facebook (Turismo)...", end=' ', flush=True)
                        fb_url = post_to_facebook(
                            article['titulo_seo'],
                            article['meta_descripcion'],
                            post_url,
                            hosted_img_url or image_url or '',
                            fb_page, fb_token,
                            wp_url=wp_url, wp_user=wp_user, wp_pass=wp_pass,
                            page_key='turismo', groq_api_key=groq_key
                        )
                        print(f"OK  {fb_url}" if fb_url else "Error (continua sin Facebook)")

                # Webs de IA → página Tribu.IA
                if kw_key in ('ia_principiantes', 'prompts', 'claude'):
                    tribu_page  = config.get('tribu_ia_facebook_page_id', '')
                    tribu_token = config.get('tribu_ia_facebook_page_token', '')
                    if tribu_page and tribu_token and 'PENDIENTE' not in tribu_token:
                        print(f"        → Publicando en Facebook (Tribu.IA)...", end=' ', flush=True)
                        fb_url = post_to_facebook(
                            article['titulo_seo'],
                            article['meta_descripcion'],
                            post_url,
                            hosted_img_url or image_url or '',
                            tribu_page, tribu_token,
                            wp_url=wp_url, wp_user=wp_user, wp_pass=wp_pass,
                            page_key='tribu_ia', groq_api_key=groq_key
                        )
                        print(f"OK  {fb_url}" if fb_url else "Error (continua sin Facebook)")

                # Galicia Conciertos → página propia
                if kw_key == 'galicia_conciertos':
                    gc_page  = config.get('galicia_conciertos_facebook_page_id', '')
                    gc_token = config.get('galicia_conciertos_facebook_page_token', '')
                    if gc_page and gc_token and 'PENDIENTE' not in gc_token:
                        print(f"        → Publicando en Facebook (Galicia Conciertos)...", end=' ', flush=True)
                        fb_url = post_to_facebook(
                            article['titulo_seo'],
                            article['meta_descripcion'],
                            post_url,
                            hosted_img_url or image_url or '',
                            gc_page, gc_token,
                            wp_url=wp_url, wp_user=wp_user, wp_pass=wp_pass,
                            page_key='galicia_conciertos', groq_api_key=groq_key
                        )
                        print(f"OK  {fb_url}" if fb_url else "Error (continua sin Facebook)")

                # 9. REGISTRAR (keyword ya marcada como usada al seleccionarla)
                log_publication(name, article['titulo_seo'], post_url, keyword, pin_url)

                # Añadir al contexto local para que los siguientes artículos puedan enlazar a este
                recent_articles.insert(0, {
                    'title': {'rendered': article['titulo_seo']},
                    'link': post_url
                })

                total_ok += 1
                published += 1

                if i < articles_per_site - 1:
                    time.sleep(4)

            except Exception as e:
                print(f"\n        ERROR: {str(e)[:130]}")
                total_err += 1
                time.sleep(3)

        print(f"\n    {name}: {published} articulo(s) publicado(s)\n")

        if site != sites[-1]:
            print(f"    Esperando 70s para que Groq TPM se resetee...")
            time.sleep(70)

    print(f"{'='*54}")
    print(f"  RESUMEN FINAL")
    print(f"  OK  Publicados: {total_ok}")
    print(f"  ERR Errores:    {total_err}")
    print(f"  Log Registro:   publicaciones.csv")
    print(f"{'='*54}\n")


# ─────────────────────────────────────────────
# VERIFICACIÓN DE CONFIGURACIÓN
# ─────────────────────────────────────────────

def check_config():
    print("\nVerificando configuracion...\n")
    config = load_json(CONFIG_FILE)
    ok = True

    if 'PENDIENTE' in config['groq_api_key'] or not config['groq_api_key']:
        print("ERROR Falta la clave de Groq")
        ok = False
    else:
        print("OK Groq API key")

    if 'PENDIENTE' in config['pexels_api_key'] or not config['pexels_api_key']:
        print("ERROR Falta la clave de Pexels")
        ok = False
    else:
        print("OK Pexels API key")

    if pinterest_configured(config):
        print("OK Pinterest configurado")
        try:
            boards = get_pinterest_boards(config['pinterest']['access_token'])
            print(f"   Tableros: {len(boards)}")
            for b in boards:
                print(f"   - {b['name']}  ID: {b['id']}")
        except Exception as e:
            print(f"   Advertencia Pinterest: {e}")
    else:
        print("Pendiente Pinterest (opcional)")

    print()
    for site in config['sites']:
        name = site['name']
        if 'PENDIENTE' in site['wp_user'] or 'PENDIENTE' in site['wp_password']:
            print(f"ERROR WordPress {name}: Faltan credenciales")
            ok = False
        else:
            try:
                r = requests.get(
                    f"{site['url'].rstrip('/')}/wp-json/wp/v2/posts",
                    auth=(site['wp_user'], site['wp_password']),
                    timeout=12
                )
                if r.status_code == 200:
                    print(f"OK WordPress {name}")
                else:
                    print(f"ERROR WordPress {name}: Error {r.status_code}")
                    ok = False
            except Exception as e:
                print(f"ERROR WordPress {name}: {e}")
                ok = False

    print()
    if ok:
        print("Todo correcto. Ejecuta 3-PUBLICAR-3-ARTICULOS.bat para empezar.\n")
    else:
        print("Corrige los errores en config.json y vuelve a verificar.\n")
    return ok


# ─────────────────────────────────────────────
# HERRAMIENTA: LISTAR TABLEROS DE PINTEREST
# ─────────────────────────────────────────────

def list_pinterest_boards():
    config = load_json(CONFIG_FILE)
    token  = config.get('pinterest', {}).get('access_token', '')

    if not token or 'PENDIENTE' in token:
        print("\nPrimero configura el access_token de Pinterest en config.json\n")
        return

    print("\nTableros de Pinterest:\n")
    try:
        boards = get_pinterest_boards(token)
        for b in boards:
            print(f"  Nombre: {b['name']}")
            print(f"  ID:     {b['id']}")
            print()
        print("Copia el ID en config.json bajo pinterest.boards\n")
    except Exception as e:
        print(f"Error: {e}\n")


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]

    # Extraer --only <nombre>
    only_site = None
    if '--only' in args:
        idx = args.index('--only')
        if idx + 1 < len(args):
            only_site = args[idx + 1]
            args.pop(idx + 1)
        args.pop(idx)

    if not args or args[0] == 'run':
        n = int(args[1]) if len(args) > 1 else 3
        run(n, only_site=only_site)

    elif args[0] == 'check':
        check_config()

    elif args[0] == 'pinterest-boards':
        list_pinterest_boards()

    else:
        try:
            run(int(args[0]), only_site=only_site)
        except ValueError:
            print(f"Comando no reconocido: {args[0]}")
            print("Uso: python publisher.py [numero de articulos]")
            print("     python publisher.py --only galiciaconciertos 6")
            print("     python publisher.py check")
            print("     python publisher.py pinterest-boards")
