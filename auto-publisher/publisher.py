"""
AUTO-PUBLISHER IA — Sistema de publicación automática con Pinterest
Genera artículos SEO con Groq (gratis), los publica en WordPress
y crea el pin en Pinterest automáticamente.
"""

import requests
import json
import csv
import os
import sys
import time
import random
from datetime import datetime

# Forzar UTF-8 en la consola de Windows para que los emojis no den error
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE  = os.path.join(BASE_DIR, 'config.json')
KEYWORDS_FILE = os.path.join(BASE_DIR, 'keywords.json')
LOG_FILE     = os.path.join(BASE_DIR, 'publicaciones.csv')


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
    """Devuelve True si Pinterest tiene credenciales reales."""
    p = config.get('pinterest', {})
    token = p.get('access_token', '')
    return token and 'PENDIENTE' not in token and len(token) > 20


# ─────────────────────────────────────────────
# GENERACIÓN DE ARTÍCULO CON GROQ
# ─────────────────────────────────────────────

def generate_article(keyword, niche_context, site_name, groq_api_key):
    """Genera un artículo SEO completo en español usando Groq (gratis)."""

    prompt = f"""Eres el mejor redactor SEO de España especializado en inteligencia artificial. Escribe un artículo largo, profundo y bien estructurado que posicione en Google.

KEYWORD PRINCIPAL: "{keyword}"
BLOG: {site_name}
CONTEXTO DEL NICHO: {niche_context}

REQUISITOS OBLIGATORIOS:
- Idioma: Español de España natural (usa «tú», evita latinismos)
- Longitud: entre 1.500 y 2.200 palabras (artículo largo para SEO)
- La keyword aparece en: título H1, primer párrafo, al menos 3 H2, texto del cuerpo de forma natural
- Densidad de keyword: 1-1.5% (natural, no forzada)
- Tono: experto pero accesible — como si lo explicara un amigo que sabe mucho de IA
- Párrafos cortos: máximo 3-4 líneas cada uno
- Incluye datos reales, estadísticas (con año), ejemplos concretos y casos de uso
- Usa listas <ul>/<ol> en al menos 2 secciones
- Añade negritas <strong> en conceptos clave (3-5 por artículo)
- Añade al menos una tabla HTML comparativa si tiene sentido para el tema

ESTRUCTURA OBLIGATORIA:
1. H1 con la keyword exacta
2. Párrafo introductorio de gancho (2-3 líneas) con keyword
3. Párrafo «En este artículo aprenderás:» con lista de puntos
4. 5-7 secciones H2 con contenido denso y útil
5. Subsecciones H3 dentro de los H2 donde aporte valor
6. Sección «Consejos prácticos» o «Paso a paso» con lista numerada
7. Sección «Errores comunes» o «Qué evitar» (posiciona en búsquedas de comparación)
8. FAQ con exactamente 5 preguntas frecuentes reales (no genéricas) con respuestas de 3-4 líneas cada una
9. Párrafo de conclusión con CTA suave («Si quieres profundizar más, explora nuestros artículos sobre X»)

Responde SOLO con este JSON válido, sin texto adicional:
{{
  "titulo_seo": "Título SEO de 55-60 caracteres con keyword al inicio",
  "meta_descripcion": "Meta descripción de 150-155 caracteres con keyword, beneficio claro y CTA",
  "slug": "url-con-guiones-keyword-incluida-sin-acentos",
  "h1": "Título H1 del artículo (puede ser ligeramente más largo que el SEO title)",
  "contenido_html": "Artículo completo en HTML con toda la estructura indicada. Mínimo 1500 palabras.",
  "descripcion_pinterest": "Descripción Pinterest 120-150 caracteres con emoji inicial y CTA",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "categoria": "Categoría corta (1-3 palabras)"
}}"""

    headers = {
        'Authorization': f'Bearer {groq_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'llama-3.3-70b-versatile',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.72,
        'max_tokens': 4000,
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


# ─────────────────────────────────────────────
# IMÁGENES — PEXELS
# ─────────────────────────────────────────────

def get_pexels_image(keyword, pexels_api_key):
    """Busca una imagen relevante y gratuita en Pexels."""

    fallbacks = [keyword, 'inteligencia artificial', 'tecnologia', 'computadora', 'digital']
    headers = {'Authorization': pexels_api_key}

    for term in fallbacks:
        try:
            resp = requests.get(
                'https://api.pexels.com/v1/search',
                headers=headers,
                params={'query': term, 'per_page': 15, 'orientation': 'landscape'},
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
                        'alt':          photo.get('alt') or keyword,
                        'photographer': photo.get('photographer', '')
                    }
        except Exception:
            continue
    return None


def upload_image_to_wp(image_url, alt_text, wp_url, wp_user, wp_pass):
    """Descarga imagen, la sube a WordPress y devuelve (media_id, hosted_url).
    El tema Hostinger tiene un bug con featured_media, así que embebemos
    la imagen en el contenido HTML en lugar de usarla como destacada."""
    try:
        img = requests.get(image_url, timeout=30)
        if img.status_code != 200:
            return None, image_url

        clean = wp_url.rstrip('/')
        resp = requests.post(
            f'{clean}/wp-json/wp/v2/media',
            headers={
                'Content-Disposition': 'attachment; filename=imagen-articulo.jpg',
                'Content-Type': 'image/jpeg'
            },
            data=img.content,
            auth=(wp_user, wp_pass),
            timeout=45
        )
        if resp.status_code in (200, 201):
            media = resp.json()
            media_id = media['id']
            hosted_url = media.get('source_url', image_url)
            requests.post(
                f'{clean}/wp-json/wp/v2/media/{media_id}',
                json={'alt_text': alt_text},
                auth=(wp_user, wp_pass),
                timeout=15
            )
            return media_id, hosted_url
    except Exception as e:
        print(f'     ⚠️  Error subiendo imagen: {e}')
    return None, image_url


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


def publish_to_wordpress(article, image_url, image_alt, cat_id, tag_ids, wp_url, wp_user, wp_pass):
    clean = wp_url.rstrip('/')

    # Prepend image to content (avoids Hostinger theme bug with featured_media)
    content = article['contenido_html']
    if image_url:
        alt = (image_alt or article['titulo_seo']).replace('"', '&quot;')
        img_html = (
            f'<figure class="wp-block-image size-large">'
            f'<img src="{image_url}" alt="{alt}" style="width:100%;height:auto;border-radius:8px;margin-bottom:1.5em"/>'
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

    resp = requests.post(
        f'{clean}/wp-json/wp/v2/posts',
        json=post, auth=(wp_user, wp_pass), timeout=45
    )
    if resp.status_code == 201:
        return resp.json()
    raise Exception(f"WordPress {resp.status_code}: {resp.text[:300]}")


# ─────────────────────────────────────────────
# PINTEREST
# ─────────────────────────────────────────────

def get_pinterest_boards(access_token):
    """Lista todos los tableros del usuario para obtener los IDs."""
    resp = requests.get(
        'https://api.pinterest.com/v5/boards',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'page_size': 25},
        timeout=15
    )
    if resp.status_code == 200:
        return resp.json().get('items', [])
    raise Exception(f"Pinterest boards error {resp.status_code}: {resp.text[:200]}")


def create_pinterest_pin(title, description, article_url, image_url, board_id, access_token):
    """
    Crea un pin en Pinterest enlazando al artículo del blog.
    La imagen viene de Pexels (vertical se adapta sola).
    """
    # Pinterest necesita imagen vertical idealmente.
    # Usamos la URL de Pexels directamente — Pinterest la descarga y cachea.

    pin_title = title[:100]
    pin_desc  = description[:500] if description else title[:500]

    payload = {
        'title':        pin_title,
        'description':  pin_desc,
        'link':         article_url,
        'board_id':     board_id,
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

    if resp.status_code == 201:
        data = resp.json()
        return f"https://pinterest.com/pin/{data.get('id', '')}"

    # Pinterest a veces devuelve 200 también
    if resp.status_code == 200:
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
            print(f'     ♻️  Keywords agotadas en {key}, reciclando...')
            keywords_data[key] = keywords_data[used_key]
            keywords_data[used_key] = []

    save_json(KEYWORDS_FILE, keywords_data)


# ─────────────────────────────────────────────
# BUCLE PRINCIPAL
# ─────────────────────────────────────────────

def run(articles_per_site=3):
    config        = load_json(CONFIG_FILE)
    keywords_data = load_json(KEYWORDS_FILE)

    groq_key    = config['groq_api_key']
    pexels_key  = config['pexels_api_key']
    sites       = config['sites']
    use_pinterest = pinterest_configured(config)
    pinterest_cfg = config.get('pinterest', {})

    total_ok  = 0
    total_err = 0

    print(f"\n{'═'*54}")
    print(f"  AUTO-PUBLISHER IA  ·  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'═'*54}")
    print(f"  Webs: {len(sites)}  ·  Artículos por web: {articles_per_site}")
    print(f"  Pinterest: {'✅ Activo' if use_pinterest else '⏳ Pendiente configurar'}")
    print(f"{'═'*54}\n")

    for site in sites:
        name    = site['name']
        kw_key  = site['keywords_key']
        pin_key = site.get('pinterest_board_key', kw_key)

        if not keywords_data.get(kw_key):
            print(f"⚠️  {name}: Sin keywords. Saltando.\n")
            continue

        print(f"📝  {name}")
        print(f"    {site['url']}")

        published = 0

        for i in range(articles_per_site):
            if not keywords_data.get(kw_key):
                break

            keyword = random.choice(keywords_data[kw_key])

            try:
                print(f"\n    [{i+1}/{articles_per_site}] Keyword: «{keyword}»")

                # 1. GENERAR ARTÍCULO
                print(f"        → Generando artículo con Groq...", end=' ', flush=True)
                article = generate_article(keyword, site['niche_context'], name, groq_key)
                print(f"✓")
                print(f"        Título: {article['titulo_seo'][:55]}...")

                # 2. IMAGEN
                image_id       = None
                image_url      = None
                image_alt      = None
                hosted_img_url = None
                print(f"        → Buscando imagen en Pexels...", end=' ', flush=True)
                img = get_pexels_image(keyword, pexels_key)

                if img:
                    image_url = img['url_large']
                    image_alt = img['alt']
                    print(f"✓  Subiendo a WordPress...", end=' ', flush=True)
                    image_id, hosted_img_url = upload_image_to_wp(
                        image_url, image_alt,
                        site['url'], site['wp_user'], site['wp_password']
                    )
                    print('✓' if image_id else '(usando URL Pexels)')
                else:
                    print('(no encontrada, continuando sin imagen)')

                # 3. CATEGORÍA Y ETIQUETAS
                cat_id  = get_or_create_category(
                    article.get('categoria', 'IA'),
                    site['url'], site['wp_user'], site['wp_password']
                )
                tag_ids = get_or_create_tags(
                    article.get('tags', []),
                    site['url'], site['wp_user'], site['wp_password']
                )

                # 4. PUBLICAR EN WORDPRESS
                print(f"        → Publicando en WordPress...", end=' ', flush=True)
                result   = publish_to_wordpress(
                    article, hosted_img_url, image_alt, cat_id, tag_ids,
                    site['url'], site['wp_user'], site['wp_password']
                )
                post_url = result.get('link', '')
                print(f"✓")
                print(f"        ✅ {post_url}")

                # 5. PINTEREST
                pin_url = ''
                if use_pinterest and image_url:
                    board_id = pinterest_cfg.get('boards', {}).get(pin_key, '')
                    if board_id and 'PENDIENTE' not in board_id:
                        try:
                            print(f"        → Creando pin en Pinterest...", end=' ', flush=True)
                            pin_desc = article.get(
                                'descripcion_pinterest',
                                article['meta_descripcion']
                            )
                            pin_url = create_pinterest_pin(
                                title       = article['titulo_seo'],
                                description = pin_desc,
                                article_url = post_url,
                                image_url   = image_url,
                                board_id    = board_id,
                                access_token= pinterest_cfg['access_token']
                            )
                            print(f"✓")
                            print(f"        📌 {pin_url}")
                        except Exception as pe:
                            print(f"⚠️  {str(pe)[:80]}")

                # 6. REGISTRAR
                log_publication(name, article['titulo_seo'], post_url, keyword, pin_url)
                mark_keyword_used(keywords_data, kw_key, keyword)

                total_ok += 1
                published += 1

                if i < articles_per_site - 1:
                    time.sleep(4)

            except Exception as e:
                print(f"\n        ❌ Error: {str(e)[:130]}")
                total_err += 1
                time.sleep(3)

        print(f"\n    📊 {name}: {published} artículo(s) publicado(s)\n")

        if site != sites[-1]:
            time.sleep(6)

    print(f"{'═'*54}")
    print(f"  RESUMEN FINAL")
    print(f"  ✅ Publicados:  {total_ok}")
    print(f"  ❌ Errores:     {total_err}")
    print(f"  📋 Registro:    publicaciones.csv")
    print(f"{'═'*54}\n")


# ─────────────────────────────────────────────
# VERIFICACIÓN DE CONFIGURACIÓN
# ─────────────────────────────────────────────

def check_config():
    print("\n🔍 Verificando configuración...\n")
    config = load_json(CONFIG_FILE)
    ok = True

    # Groq
    if 'PENDIENTE' in config['groq_api_key'] or not config['groq_api_key']:
        print("❌ Falta la clave de Groq")
        ok = False
    else:
        print("✅ Groq API key → OK")

    # Pexels
    if 'PENDIENTE' in config['pexels_api_key'] or not config['pexels_api_key']:
        print("❌ Falta la clave de Pexels")
        ok = False
    else:
        print("✅ Pexels API key → OK")

    # Pinterest (opcional)
    if pinterest_configured(config):
        print("✅ Pinterest → Configurado")
        try:
            boards = get_pinterest_boards(config['pinterest']['access_token'])
            print(f"   Tableros encontrados: {len(boards)}")
            for b in boards:
                print(f"   - {b['name']}  →  ID: {b['id']}")
        except Exception as e:
            print(f"   ⚠️  Error conectando Pinterest: {e}")
    else:
        print("⏳ Pinterest → Pendiente (opcional, el sistema funciona sin él)")

    # WordPress
    print()
    for site in config['sites']:
        name = site['name']
        if 'PENDIENTE' in site['wp_user'] or 'PENDIENTE' in site['wp_password']:
            print(f"❌ WordPress {name}: Faltan credenciales")
            ok = False
        else:
            try:
                r = requests.get(
                    f"{site['url'].rstrip('/')}/wp-json/wp/v2/posts",
                    auth=(site['wp_user'], site['wp_password']),
                    timeout=12
                )
                if r.status_code == 200:
                    print(f"✅ WordPress {name} → Conectado")
                else:
                    print(f"❌ WordPress {name} → Error {r.status_code} (revisa usuario/contraseña)")
                    ok = False
            except Exception as e:
                print(f"❌ WordPress {name} → No conecta: {e}")
                ok = False

    print()
    if ok:
        print("✅ Todo correcto. Ejecuta 3-PUBLICAR-3-ARTICULOS.bat para empezar.\n")
    else:
        print("⚠️  Corrige los ❌ en config.json y vuelve a verificar.\n")

    return ok


# ─────────────────────────────────────────────
# HERRAMIENTA: LISTAR TABLEROS DE PINTEREST
# ─────────────────────────────────────────────

def list_pinterest_boards():
    """Muestra los IDs de los tableros de Pinterest del usuario."""
    config = load_json(CONFIG_FILE)
    token  = config.get('pinterest', {}).get('access_token', '')

    if not token or 'PENDIENTE' in token:
        print("\n⚠️  Primero configura el access_token de Pinterest en config.json\n")
        return

    print("\n📌 Tableros de Pinterest:\n")
    try:
        boards = get_pinterest_boards(token)
        for b in boards:
            print(f"  Nombre: {b['name']}")
            print(f"  ID:     {b['id']}")
            print()
        print("Copia el ID del tablero que corresponde a cada web en config.json\n")
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
            print("Uso: python publisher.py [número de artículos]")
            print("     python publisher.py check")
            print("     python publisher.py pinterest-boards")
