# -*- coding: utf-8 -*-
"""
PILLAR CONTENT GENERATOR
Genera artículos de 3.000-5.000 palabras (pillar articles) para rankear
en el Top 3 de Google en keywords competidas.

Uso:
  python generar-pillar-content.py                    # 1 pillar por cada web
  python generar-pillar-content.py turismoourense      # solo turismo ourense
  python generar-pillar-content.py ia_principiantes 2  # 2 pillars en IA

Los pillar articles se publican con Riker Carmon como autor y bloque de afiliados.
"""
import requests, json, os, sys, time, random, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE   = os.path.join(BASE_DIR, 'config.json')

config = json.load(open(CONFIG_FILE, encoding='utf-8'))

# ─────────────────────────────────────────────
# PILLAR KEYWORDS — Las más importantes por nicho
# ─────────────────────────────────────────────
PILLAR_KEYWORDS = {
    'ia_principiantes': [
        'qué es la inteligencia artificial guía completa para principiantes',
        'cómo ganar dinero con inteligencia artificial en 2025 guía definitiva',
        'mejores herramientas de IA gratuitas para trabajar más rápido',
        'inteligencia artificial para negocios pequeños guía paso a paso',
        'cómo automatizar tu trabajo con IA sin saber programar',
    ],
    'prompts': [
        'guía definitiva de prompt engineering para ChatGPT y Claude 2025',
        'los 100 mejores prompts para ChatGPT que deberías conocer',
        'cómo escribir prompts perfectos para inteligencia artificial',
        'prompts para marketing digital que generan resultados reales',
        'prompt engineering avanzado técnicas profesionales completas',
    ],
    'claude': [
        'guía completa de Claude de Anthropic todo lo que necesitas saber',
        'claude vs chatgpt comparativa definitiva cuál es mejor en 2025',
        'cómo usar la API de Claude para tu negocio guía completa',
        'claude para empresas casos de uso reales y resultados',
        'claude projects y artifacts guía definitiva de uso profesional',
    ],
    'turismo_ourense': [
        'qué ver en ourense la guía definitiva con 25 lugares imprescindibles',
        'termas de ourense guía completa de los mejores balnearios y precios',
        'ribeira sacra ruta completa por el cañón del sil viñedos y monasterios',
        'gastronomía de ourense los 20 platos típicos que tienes que probar',
        'turismo en ourense itinerario de 3 días por la ciudad y provincia',
    ],
    'bengalas_humo': [
        'guía completa bengalas de humo para fotografía técnicas y consejos',
        'mejores bengalas de humo del mercado comparativa completa 2025',
        'fotografía con humo de colores guía definitiva para fotógrafos',
        'cómo usar bengalas de humo en bodas guía para fotógrafos y novios',
        'seguridad con bengalas de humo todo lo que debes saber antes de usarlas',
    ],
}

AFFILIATE_BLOCKS = {
    'turismo_ourense': """
<div style="background:#f0f7f0;border-left:4px solid #2d6a4f;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#2d6a4f;margin-top:0">🏨 ¿Buscas alojamiento en Ourense?</h3>
<p>Compara precios y encuentra los mejores hoteles, casas rurales y apartamentos con cancelación gratuita.</p>
<p><a href="https://www.booking.com/searchresults.es.html?ss=Ourense" target="_blank" rel="noopener sponsored" style="background:#003580;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold">Ver alojamientos en Ourense →</a></p>
</div>""",
    'bengalas_humo': """
<div style="background:#fff8f0;border-left:4px solid #e07b00;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#e07b00;margin-top:0">🛒 Consigue tus bengalas en Amazon</h3>
<p>Las mejores bengalas de colores para fotografía, bodas y eventos con envío rápido.</p>
<p><a href="https://www.amazon.es/s?k=bengalas+humo+colores+fotografia" target="_blank" rel="noopener sponsored" style="background:#ff9900;color:#111;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold">Ver bengalas en Amazon →</a></p>
</div>""",
    'ia_principiantes': """
<div style="background:#f0f4ff;border-left:4px solid #4f46e5;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#4f46e5;margin-top:0">🤖 Herramientas de IA recomendadas</h3>
<ul><li><a href="https://claude.ai" target="_blank" rel="noopener">Claude Pro</a> — El asistente de IA más preciso</li>
<li><a href="https://chatgpt.com" target="_blank" rel="noopener">ChatGPT Plus</a> — Imprescindible para contenido</li></ul>
</div>""",
    'prompts': """
<div style="background:#f0fff4;border-left:4px solid #059669;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#059669;margin-top:0">⚡ Las mejores IAs para tus prompts</h3>
<ul><li><a href="https://claude.ai" target="_blank" rel="noopener">Claude Pro</a> — El mejor para prompt engineering avanzado</li>
<li><a href="https://chatgpt.com" target="_blank" rel="noopener">ChatGPT Plus</a> — Acceso a GPT-4 y plugins</li></ul>
</div>""",
    'claude': """
<div style="background:#faf5ff;border-left:4px solid #7c3aed;border-radius:8px;padding:20px;margin:30px 0">
<h3 style="color:#7c3aed;margin-top:0">🚀 Empieza con Claude hoy</h3>
<p><a href="https://claude.ai/upgrade" target="_blank" rel="noopener" style="background:#7c3aed;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold">Probar Claude Pro →</a></p>
</div>""",
}

def generate_pillar_article(keyword, niche_context, site_name, groq_api_key):
    prompt = f"""Eres el mejor redactor SEO de España. Tu misión: escribir el artículo DEFINITIVO sobre este tema.
Este será el artículo de referencia (pillar content) que posicionará como #1 en Google.

KEYWORD PRINCIPAL: "{keyword}"
BLOG: {site_name}
CONTEXTO: {niche_context}

REQUISITOS DE EXTENSIÓN: Mínimo 3.500 palabras. Este es un artículo COMPLETO y EXHAUSTIVO.

SEÑALES E-E-A-T OBLIGATORIAS:
- Menciona ejemplos reales con nombres, cifras y fechas concretas
- Al menos 5 estadísticas con fuente citada (ej: «Según Statista 2024...»)
- Perspectiva de experto con 10+ años: qué sabe un profesional que un principiante no sabe
- Mínimo 3 «errores que comete el 90% de la gente»
- Al menos 2 datos sorprendentes o contraintuitivos

ESTRUCTURA OBLIGATORIA (artículo largo):
1. H1 con keyword + número grande + power word («definitiva», «completa», «todo lo que necesitas»)
2. Intro con estadística impactante + promesa concreta de lo que aprenderá
3. «Tabla de contenidos» en HTML (lista de anchors)
4. 8-12 secciones H2 con contenido DENSO (mínimo 300 palabras por sección)
5. Subsecciones H3 con ejemplos prácticos paso a paso
6. Al menos 3 tablas comparativas HTML
7. Al menos 5 listas <ul>/<ol> con bullet points accionables
8. Sección «Paso a paso» con mínimo 7 pasos detallados
9. Sección «Errores a evitar» con mínimo 5 errores explicados
10. Sección «Preguntas frecuentes» con 7 preguntas en H3 y respuestas completas
11. Conclusión con resumen ejecutivo + CTA claro

Responde SOLO con JSON válido:
{{
  "titulo_seo": "Título SEO 55-65 chars con keyword + número grande",
  "meta_descripcion": "Meta 150-160 chars urgente y específico con keyword",
  "slug": "url-seo-sin-acentos-con-guiones",
  "h1": "H1 completo del artículo",
  "contenido_html": "Artículo COMPLETO en HTML. MÍNIMO 3500 palabras.",
  "descripcion_pinterest": "160 chars máx con emoji + beneficio concreto",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7"],
  "categoria": "Categoría principal"
}}"""

    resp = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={'Authorization': f'Bearer {groq_api_key}', 'Content-Type': 'application/json'},
        json={
            'model': 'llama-3.3-70b-versatile',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.7,
            'max_tokens': 8000,
            'response_format': {'type': 'json_object'}
        },
        timeout=120
    )
    if resp.status_code != 200:
        raise Exception(f"Groq {resp.status_code}: {resp.text[:200]}")
    raw = resp.json()['choices'][0]['message']['content']
    if '```' in raw:
        parts = raw.split('```')
        raw = parts[1][4:] if parts[1].startswith('json') else parts[1]
    return json.loads(raw.strip())


def get_pexels_image(keyword, pexels_key, site_key=''):
    NICHE_QUERIES = {
        'turismo_ourense': ['ourense galicia spain thermal hot springs', 'ribeira sacra galicia vineyard canyon'],
        'ia_principiantes': ['artificial intelligence technology futuristic', 'machine learning data computer'],
        'prompts': ['ai writing keyboard computer creative', 'person typing laptop workspace'],
        'claude': ['ai assistant technology interface laptop', 'artificial intelligence business computer'],
        'bengalas_humo': ['smoke bomb photography colorful outdoor', 'color smoke flare photography creative'],
    }
    headers = {'Authorization': pexels_key}
    queries = [keyword] + NICHE_QUERIES.get(site_key, ['technology digital'])
    for q in queries:
        try:
            r = requests.get('https://api.pexels.com/v1/search',
                headers=headers, params={'query': q, 'per_page': 15, 'orientation': 'landscape'}, timeout=15)
            if r.status_code == 200:
                photos = r.json().get('photos', [])
                if photos:
                    p = random.choice(photos[:8])
                    return {'url': p['src']['large2x'], 'alt': p.get('alt') or keyword}
        except Exception:
            continue
    return None


def sanitize_content(html):
    """Limpia el HTML generado por Groq para evitar errores PHP en WordPress."""
    # Eliminar etiquetas PHP que puedan colarse en el contenido generado
    html = re.sub(r'<\?(?:php)?.*?\?>', '', html, flags=re.DOTALL)
    # Eliminar caracteres de control excepto \n \t
    html = ''.join(c for c in html if ord(c) >= 32 or c in '\n\t')
    return html.strip()


def get_or_create_term(endpoint, name, auth):
    """Crea o recupera el ID de una categoría/tag, manejando duplicados."""
    r = requests.post(endpoint, json={'name': name}, auth=auth, timeout=10)
    if r.status_code in [200, 201]:
        return r.json()['id']
    if r.status_code == 400:
        data = r.json()
        # WordPress devuelve el ID existente en el campo 'data' o como 'term_id'
        tid = data.get('data', {})
        if isinstance(tid, dict):
            tid = tid.get('term_id') or tid.get('id')
        if tid:
            return int(tid)
        # Buscar por nombre como fallback
        r2 = requests.get(endpoint, params={'search': name, 'per_page': 5}, auth=auth, timeout=10)
        if r2.status_code == 200 and r2.json():
            return r2.json()[0]['id']
    return None


def publish_pillar(article, site, image_data, config):
    clean = site['url'].rstrip('/')
    auth  = (site['wp_user'], site['wp_password'])

    content = sanitize_content(article['contenido_html'])

    # Afiliados antes de la última H2
    affiliate = AFFILIATE_BLOCKS.get(site['keywords_key'], '')
    if affiliate and '<h2' in content:
        last_h2 = content.rfind('<h2')
        content = content[:last_h2] + affiliate + content[last_h2:]

    # Imagen destacada al inicio
    if image_data:
        img_html = (f'<figure class="wp-block-image size-large">'
                    f'<img src="{image_data["url"]}" alt="{image_data["alt"]}" '
                    f'width="1280" height="853" style="width:100%;height:auto;border-radius:8px;margin-bottom:1.5em"/>'
                    f'</figure>\n')
        content = img_html + content

    # Subir imagen a WordPress
    media_id = None
    if image_data:
        try:
            img_bytes = requests.get(image_data['url'], timeout=30).content
            r_media = requests.post(f'{clean}/wp-json/wp/v2/media',
                headers={'Content-Disposition': 'attachment; filename=pillar.jpg',
                         'Content-Type': 'image/jpeg'},
                data=img_bytes, auth=auth, timeout=60)
            if r_media.status_code in [200, 201]:
                media_id = r_media.json()['id']
        except Exception as e:
            print(f'  Imagen warning: {e}')

    # Categoría (maneja duplicados)
    cat_id = 1
    cat_name = article.get('categoria', 'Guías')
    tid = get_or_create_term(f'{clean}/wp-json/wp/v2/categories', cat_name, auth)
    if tid:
        cat_id = tid

    # Tags (maneja duplicados)
    tag_ids = []
    for tag in article.get('tags', [])[:5]:
        tid = get_or_create_term(f'{clean}/wp-json/wp/v2/tags', tag, auth)
        if tid:
            tag_ids.append(tid)

    post = {
        'title':      article['titulo_seo'],
        'content':    content,
        'excerpt':    article['meta_descripcion'],
        'slug':       article['slug'],
        'status':     'publish',
        'categories': [cat_id],
        'tags':       tag_ids,
    }
    if media_id:
        post['featured_media'] = media_id
    if site.get('riker_author_id'):
        post['author'] = site['riker_author_id']

    # Intentar primero /wp-json/, luego ?rest_route= para plain permalinks
    for base_url in [f'{clean}/wp-json/wp/v2/posts',
                     f'{clean}/index.php?rest_route=/wp/v2/posts']:
        r = requests.post(base_url, json=post, auth=auth, timeout=90)
        if r.status_code == 201:
            return r.json().get('link', '')
        if r.status_code == 500:
            # Reintentar sin featured_media (puede causar conflictos con LiteSpeed)
            post_slim = {k: v for k, v in post.items() if k != 'featured_media'}
            r2 = requests.post(base_url, json=post_slim, auth=auth, timeout=90)
            if r2.status_code == 201:
                return r2.json().get('link', '')

    raise Exception(f"WP error {r.status_code}: {r.text[:200]}")


def main():
    args = sys.argv[1:]
    filter_site = args[0] if args else None
    count = int(args[1]) if len(args) > 1 else 1

    groq_key   = config['groq_api_key']
    pexels_key = config['pexels_api_key']
    sites      = config['sites']

    if filter_site:
        sites = [s for s in sites if filter_site.lower() in s['url'].lower() or filter_site in s['keywords_key']]
        if not sites:
            print(f'No se encontró web con "{filter_site}"')
            sys.exit(1)

    print(f'\n{"="*60}')
    print(f'  PILLAR CONTENT GENERATOR')
    print(f'  Webs: {len(sites)}  ·  Artículos por web: {count}')
    print(f'{"="*60}\n')

    for site in sites:
        kw_key   = site['keywords_key']
        keywords = PILLAR_KEYWORDS.get(kw_key, [])
        if not keywords:
            print(f'{site["name"]}: Sin pillar keywords definidas. Saltando.')
            continue

        for i in range(min(count, len(keywords))):
            keyword = keywords[i]
            print(f'\n[{site["name"]}] Keyword: «{keyword}»')

            try:
                print(f'  → Generando pillar article (3500+ palabras)...', end=' ', flush=True)
                article = generate_pillar_article(keyword, site['niche_context'], site['name'], groq_key)
                word_count = len(re.sub('<[^>]+>', '', article['contenido_html']).split())
                print(f'OK  ({word_count} palabras)')
                print(f'  Título: {article["titulo_seo"]}')

                print(f'  → Buscando imagen 1280px...', end=' ', flush=True)
                img = get_pexels_image(keyword, pexels_key, site_key=kw_key)
                print('OK' if img else 'no encontrada')

                print(f'  → Publicando en WordPress...', end=' ', flush=True)
                url = publish_pillar(article, site, img, config)
                print(f'OK')
                print(f'  URL: {url}')

            except Exception as e:
                print(f'\n  ERROR: {e}')

            if i < count - 1:
                time.sleep(5)

        time.sleep(3)

    print(f'\n{"="*60}')
    print('Pillar content publicado.')

if __name__ == '__main__':
    main()
