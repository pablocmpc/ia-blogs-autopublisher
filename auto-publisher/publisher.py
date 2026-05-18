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
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE   = os.path.join(BASE_DIR, 'config.json')
KEYWORDS_FILE = os.path.join(BASE_DIR, 'keywords.json')
LOG_FILE      = os.path.join(BASE_DIR, 'publicaciones.csv')

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


def select_smart_keyword(keywords_data, kw_key, recent_articles):
    """
    Selecciona keyword priorizando temas no cubiertos recientemente.
    Esto construye autoridad tópica en lugar de repetir el mismo tema.
    """
    available = keywords_data.get(kw_key, [])
    if not available:
        return None
    if not recent_articles:
        return random.choice(available)

    recent_words = set()
    for art in recent_articles[:12]:
        title = art.get('title', {}).get('rendered', '')
        recent_words |= _words(title)

    best_kw, best_score = None, -1
    for kw in available:
        kw_words = _words(kw)
        novelty = len(kw_words - recent_words)
        if novelty > best_score:
            best_score = novelty
            best_kw = kw

    return best_kw or random.choice(available)


# ─────────────────────────────────────────────
# SEO ENGINE — SCHEMA MARKUP JSON-LD
# ─────────────────────────────────────────────

def build_schema_markup(article, post_url, site_name, site_url, image_url=None):
    """Genera JSON-LD para Article + FAQPage (rich results en Google)."""
    now_iso = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

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

    schema_html = ''
    for s in schemas:
        schema_html += f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=2)}\n</script>\n'

    return schema_html


# ─────────────────────────────────────────────
# SEO ENGINE — PING A BUSCADORES
# ─────────────────────────────────────────────

def ping_search_engines(site_url):
    """Notifica a Google y Bing que hay contenido nuevo en el sitemap."""
    sitemap = f"{site_url.rstrip('/')}/sitemap.xml"
    for engine, url in [
        ('Google', f'https://www.google.com/ping?sitemap={sitemap}'),
        ('Bing',   f'https://www.bing.com/ping?sitemap={sitemap}'),
    ]:
        try:
            r = requests.get(url, timeout=8)
            status = 'OK' if r.status_code == 200 else r.status_code
            print(f"          {engine}: {status}", end='  ')
        except Exception:
            print(f"          {engine}: timeout", end='  ')
    print()


# ─────────────────────────────────────────────
# GENERACIÓN DE ARTÍCULO CON GROQ
# ─────────────────────────────────────────────

def generate_article(keyword, niche_context, site_name, groq_api_key, related_articles=None, model='llama-3.3-70b-versatile'):
    """Genera artículo SEO con E-E-A-T signals, Google Discover y alto CPC."""

    current_year = datetime.now().year
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

    prompt = f"""AÑO ACTUAL: {current_year}
INSTRUCCIÓN CRÍTICA DE FECHA: Siempre que escribas un año en cualquier parte del artículo (título, subtítulos, estadísticas, datos, guías, referencias temporales como "este año", "en {current_year}", "actualizado {current_year}") DEBES usar {current_year}. Nunca escribas {current_year - 1} ni ningún año anterior como si fuera el año actual.

Actúa como Consultor SEO Experto y Redactor de Contenido enfocado en Google Discover y nichos de Alta Monetización (AdSense de Alto CPC).

Tu misión: escribir el artículo más útil, profundo y bien estructurado sobre este tema para posicionar en el Top 3 de Google Y ser seleccionado para el feed de Google Discover.

KEYWORD PRINCIPAL: "{keyword}"
BLOG: {site_name}
CONTEXTO DEL NICHO: {niche_context}
{internal_links_block}{high_cpc_block}
TÍTULO PARA GOOGLE DISCOVER:
El título debe usar «clickbait sano»: curiosidad + alto beneficio, menos de 60 caracteres.
Ejemplos de fórmulas ganadoras:
  - «La función oculta de X que nadie usa»
  - «Por qué el 90% de Y falla (y cómo evitarlo)»
  - «Haz X en 5 minutos sin [obstáculo común]»
  - «El truco de los expertos para X»

SEÑALES E-E-A-T (imprescindibles para Google):
- Demuestra experiencia práctica: ejemplos reales, casos de uso concretos, errores que cometen los principiantes
- Cita estadísticas con fuente y año (ej: «Según un informe de McKinsey {current_year}...»)
- Perspectiva experta: qué haría un profesional diferente, qué atajos NO funcionan
- Incluye al menos 1 dato sorprendente o contraintuitivo que demuestre profundidad real

REQUISITOS TÉCNICOS:
- Idioma: Español de España natural (usa «tú», directo y práctico, sin rodeos teóricos)
- Tono: profesional, fresco, sumamente práctico
- Longitud: entre 1.800 y 2.500 palabras — artículo largo y completo
- Keyword en: H1, primer párrafo, al menos 3 H2, cuerpo de forma natural
- Densidad de keyword: 1-1.5% (orgánica, no spam)
- Párrafos cortos: máximo 3-4 líneas
- Listas <ul>/<ol> en al menos 2 secciones
- <strong> en conceptos clave (5-8 por artículo)
- Al menos 1 tabla HTML comparativa si el tema lo permite
- 1-2 <blockquote> con citas o estadísticas impactantes

ESTRUCTURA OBLIGATORIA:
1. H1 con keyword + gancho potente (menos de 60 chars si posible, promete resultado concreto)
2. Intro de 2-3 líneas: dato impactante o pregunta que genere curiosidad inmediata + keyword
3. «En este artículo aprenderás:» con 4-5 puntos concretos en lista
4. 5-7 secciones H2 con contenido denso y práctico
5. Subsecciones H3 donde aporten valor real
6. Sección «Paso a paso» o «Guía práctica» con lista numerada detallada
7. Si es nicho tech/IA: incluir bloque <pre><code> con prompt o ejemplo listo para copiar
8. Sección «Errores comunes que debes evitar» (captura búsquedas de comparación)
9. Sección «FAQ — Preguntas frecuentes» con exactamente 5 preguntas en H3 (búsquedas reales de Google, específicas) con respuestas de 3-4 líneas cada una
10. Conclusión con síntesis del valor principal y CTA suave hacia otro artículo

Responde SOLO con JSON válido, sin texto adicional:
{{
  "titulo_seo": "Título <60 chars con clickbait sano + keyword + curiosidad/beneficio",
  "meta_descripcion": "Meta 150-155 chars con keyword, beneficio concreto y CTA",
  "slug": "url-con-guiones-keyword-sin-acentos",
  "h1": "H1 del artículo (puede ser más largo que el SEO title)",
  "imagen_destacada": "Descripción exacta para generar con IA: composición, colores, estilo, elementos visuales. Ej: 'Drone DJI volando sobre ciudad futurista al amanecer, luces de neón azul y naranja, estilo tech cinematográfico, fondo oscuro, resolución 1200x630'",
  "contenido_html": "Artículo completo en HTML. Mínimo 1800 palabras. INCLUYE los enlaces internos indicados si se proporcionaron.",
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
        'max_tokens': 6000,
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


def validate_article(article):
    """Valida que el artículo generado tenga todos los campos necesarios y contenido mínimo."""
    required = ['titulo_seo', 'meta_descripcion', 'slug', 'contenido_html']
    for field in required:
        if not article.get(field, '').strip():
            raise Exception(f"Artículo inválido: campo '{field}' vacío")
    if len(article['contenido_html']) < 800:
        raise Exception(f"Contenido demasiado corto: {len(article['contenido_html'])} chars")
    # Limpiar slug: sin acentos, solo letras, números y guiones
    article['slug'] = re.sub(r'[^a-z0-9-]', '', article['slug'].lower().replace(' ', '-'))
    if not article['slug']:
        article['slug'] = re.sub(r'[^a-z0-9-]', '', article['titulo_seo'].lower().replace(' ', '-'))[:80]
    return article


def generate_with_fallback(keyword, niche_context, site_name, groq_key, related_articles=None):
    """Genera artículo con fallback inteligente entre modelos Groq.
    Distingue errores TPD (cuota diaria agotada → cambiar modelo)
    de TPM (límite por minuto → esperar y reintentar mismo modelo).
    """
    models = [
        'llama-3.3-70b-versatile',
        'openai/gpt-oss-120b',
        'meta-llama/llama-4-scout-17b-16e-instruct',
    ]
    last_err = None
    for model in models:
        for attempt in range(2):
            try:
                article = generate_article(
                    keyword, niche_context, site_name, groq_key,
                    related_articles=related_articles, model=model
                )
                return validate_article(article)
            except Exception as e:
                err_str = str(e)
                last_err = e
                is_429 = '429' in err_str
                is_tpd = is_429 and ('per day' in err_str or 'TPD' in err_str or 'tokens per day' in err_str)
                is_tpm = is_429 and not is_tpd
                if is_tpd:
                    break  # Cuota diaria agotada → probar siguiente modelo
                if is_tpm:
                    wait = 65 if attempt == 0 else 0
                    if wait:
                        print(f'TPM limit {model.split("/")[-1][:12]}, esperando {wait}s...')
                        time.sleep(wait)
                        continue
                    break  # Ya reintentamos, saltar al siguiente modelo
                if is_429:
                    break  # Otro tipo de 429, saltar modelo
                # Error no relacionado con rate limit → saltar al siguiente modelo
                break
    raise last_err or Exception("Todos los modelos Groq fallaron")


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
}

def get_pexels_image(keyword, pexels_api_key, orientation='landscape', site_key=''):
    """
    Busca imagen relevante en Pexels.
    Usa queries específicas por nicho para evitar imágenes irrelevantes
    (ej: no poner playa para Ourense que es ciudad interior).
    """
    headers = {'Authorization': pexels_api_key}

    # Construir lista de búsquedas: keyword primero, luego queries del nicho, luego fallback genérico
    niche_queries = NICHE_IMAGE_QUERIES.get(site_key, [])
    fallback_generic = {
        'turismo_ourense': ['galicia spain nature tourism', 'spain rural tourism village'],
        'ia_principiantes': ['inteligencia artificial', 'tecnologia digital'],
        'prompts':          ['ai technology writing', 'computer keyboard creative'],
        'claude':           ['artificial intelligence assistant', 'ai technology'],
        'bengalas_humo':    ['smoke photography colorful', 'color powder explosion'],
    }.get(site_key, ['technology digital', 'business professional'])

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
<h3 style="color:#4f46e5;margin-top:0">🤖 Herramientas de IA recomendadas</h3>
<p>Estas son las herramientas que uso personalmente para multiplicar mi productividad con inteligencia artificial.</p>
<ul style="margin:10px 0">
<li><a href="https://claude.ai" target="_blank" rel="noopener">Claude (Anthropic)</a> — El asistente de IA más preciso del mercado</li>
<li><a href="https://chatgpt.com" target="_blank" rel="noopener">ChatGPT Plus</a> — Imprescindible para contenido y código</li>
</ul>
</div>""",
    'prompts': """
<div style="background:#f0fff4;border-left:4px solid #059669;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#059669;margin-top:0">⚡ Potencia tus prompts con estas herramientas</h3>
<p>Las herramientas que uso para crear y probar prompts profesionales cada día.</p>
<ul style="margin:10px 0">
<li><a href="https://claude.ai" target="_blank" rel="noopener">Claude Pro</a> — El mejor modelo para prompt engineering avanzado</li>
<li><a href="https://chatgpt.com" target="_blank" rel="noopener">ChatGPT Plus</a> — Acceso a GPT-4 y generación de imágenes</li>
</ul>
</div>""",
    'claude': """
<div style="background:#faf5ff;border-left:4px solid #7c3aed;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#7c3aed;margin-top:0">🚀 Prueba Claude Pro ahora</h3>
<p>Accede a los modelos más avanzados de Anthropic, contexto de 200K tokens, Projects y mucho más.</p>
<p><a href="https://claude.ai/upgrade" target="_blank" rel="noopener" style="background:#7c3aed;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold">Actualizar a Claude Pro →</a></p>
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

def post_to_facebook(title, excerpt, article_url, image_url, page_id, page_token):
    """
    Solo para Turismo Ourense — Make.com gestiona este paso automáticamente.
    """
    if 'turismoourense' not in str(article_url):
        return ''  # solo Turismo Ourense usa Facebook directo
    if not page_token or page_token == 'PENDIENTE':
        return ''
    try:
        # Construir mensaje llamativo con emojis y CTA
        # Primeras 2 frases del excerpt como gancho
        gancho = excerpt[:180].rstrip() + ('...' if len(excerpt) > 180 else '')

        # Detectar hashtags según la URL del sitio
        if 'turismoourense' in article_url:
            hashtags = '#TurismoOurense #Ourense #Galicia #TermasOurense #ViajarEspaña #TurismoGalicia #RibeiraSacra'
        elif 'superprompts' in article_url:
            hashtags = '#Prompts #ChatGPT #IA #PromptEngineering #InteligenciaArtificial #AITips'
        elif 'guiaclaude' in article_url:
            hashtags = '#Claude #Anthropic #IA #InteligenciaArtificial #ChatGPT #AIEspanol'
        elif 'bengalasdehumo' in article_url:
            hashtags = '#BengalasDeHumo #Fotografia #FotografiaCreativa #HumoColores #Bodas #Eventos'
        elif 'flydrones' in article_url or 'teal-meerkat' in article_url:
            hashtags = '#Drones #DJI #FotografiaAerea #DroneLife #DroneEspaña #FPV #AerialPhotography'
        else:
            hashtags = '#InteligenciaArtificial #IA #TecnologiaIA #AIEspanol'

        message = (
            f"📰 {title}\n\n"
            f"{gancho}\n\n"
            f"🔗 Leer artículo completo:\n{article_url}\n\n"
            f"{hashtags}"
        )

        photo_id = None

        # Descargar imagen y subirla como bytes (evita bloqueo de hotlinking de Pexels/WP)
        if image_url:
            try:
                img_bytes = requests.get(image_url, timeout=30,
                    headers={'User-Agent': 'Mozilla/5.0'}).content
                r_photo = requests.post(
                    f'https://graph.facebook.com/v22.0/{page_id}/photos',
                    data={'published': 'false', 'access_token': page_token},
                    files={'source': ('photo.jpg', img_bytes, 'image/jpeg')},
                    timeout=60
                )
                if r_photo.status_code == 200:
                    photo_id = r_photo.json().get('id')
            except Exception:
                pass  # Si falla la foto, publicar sin imagen

        # Publicar post con foto adjunta o solo con link preview
        post_data = {
            'message':      message,
            'access_token': page_token,
        }
        if photo_id:
            post_data['attached_media'] = json.dumps([{'media_fbid': photo_id}])
        else:
            post_data['link'] = article_url  # Fallback: link preview

        r = requests.post(
            f'https://graph.facebook.com/v22.0/{page_id}/feed',
            data=post_data, timeout=25
        )
        if r.status_code == 200:
            post_id = r.json().get('id', '')
            return f'https://www.facebook.com/{post_id}'
        else:
            print(f'Facebook error {r.status_code}: {r.text[:150]}')
    except Exception as e:
        print(f'Facebook error: {e}')
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

        if not keywords_data[key]:
            print(f'     Keywords agotadas en {key}, reciclando...')
            keywords_data[key] = keywords_data[used_key]
            keywords_data[used_key] = []

    save_json(KEYWORDS_FILE, keywords_data)


# ─────────────────────────────────────────────
# BUCLE PRINCIPAL
# ─────────────────────────────────────────────

def run(articles_per_site=3):
    config        = load_json(CONFIG_FILE)
    keywords_data = load_json(KEYWORDS_FILE)

    groq_key      = config['groq_api_key']
    pexels_key    = config['pexels_api_key']
    sites         = config['sites']
    use_pinterest = pinterest_configured(config)
    pinterest_cfg = config.get('pinterest', {})

    total_ok  = 0
    total_err = 0

    print(f"\n{'='*54}")
    print(f"  AUTO-PUBLISHER IA  ·  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*54}")
    print(f"  Webs: {len(sites)}  ·  Articulos por web: {articles_per_site}")
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

        published = 0

        for i in range(articles_per_site):
            if not keywords_data.get(kw_key):
                break

            # Selección inteligente de keyword (topic clustering)
            keyword = select_smart_keyword(keywords_data, kw_key, recent_articles)

            try:
                print(f"\n    [{i+1}/{articles_per_site}] Keyword: «{keyword}»")

                # Artículos relacionados para enlazado interno
                related = find_related_articles(keyword, recent_articles, max_results=3)
                if related:
                    print(f"        Links internos disponibles: {len(related)}")

                # 1. GENERAR ARTÍCULO
                print(f"        → Generando articulo con Groq...", end=' ', flush=True)
                article = generate_with_fallback(
                    keyword, site['niche_context'], name, groq_key,
                    related_articles=related
                )
                print(f"OK")
                print(f"        Titulo: {article['titulo_seo'][:60]}...")

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

                # 4. SCHEMA MARKUP — añade JSON-LD al inicio del contenido
                temp_url = f"{wp_url.rstrip('/')}/{article['slug']}/"
                schema_html = build_schema_markup(
                    article, temp_url, name, wp_url,
                    hosted_img_url or image_url
                )
                article['contenido_html'] = schema_html + article['contenido_html']

                # 5. PUBLICAR EN WORDPRESS
                print(f"        → Publicando en WordPress...", end=' ', flush=True)
                riker_id       = site.get('riker_author_id')
                affiliate_html = get_affiliate_block(kw_key)
                result   = publish_to_wordpress(
                    article, hosted_img_url, image_alt, cat_id, tag_ids,
                    wp_url, wp_user, wp_pass, media_id=media_id_wp,
                    author_id=riker_id, affiliate_block=affiliate_html
                )
                post_url = result.get('link', '')
                print(f"OK")
                print(f"        URL: {post_url}")

                # 6. PING A BUSCADORES
                print(f"        → Ping sitemap:", end=' ', flush=True)
                ping_search_engines(wp_url)

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

                # 8. REGISTRAR (Facebook gestionado por Make.com automáticamente)
                log_publication(name, article['titulo_seo'], post_url, keyword, pin_url)
                mark_keyword_used(keywords_data, kw_key, keyword)

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
            time.sleep(6)

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

    if not args or args[0] == 'run':
        n = int(args[1]) if len(args) > 1 else 3
        run(n)

    elif args[0] == 'check':
        check_config()

    elif args[0] == 'pinterest-boards':
        list_pinterest_boards()

    else:
        try:
            run(int(args[0]))
        except ValueError:
            print(f"Comando no reconocido: {args[0]}")
            print("Uso: python publisher.py [numero de articulos]")
            print("     python publisher.py check")
            print("     python publisher.py pinterest-boards")
