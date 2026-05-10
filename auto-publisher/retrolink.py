# -*- coding: utf-8 -*-
"""
RETROLINK — Añade enlazado interno a artículos ya publicados.

Para cada artículo, busca 3 artículos relacionados temáticamente y añade
una sección "Artículos relacionados" al final si no la tiene ya.
Esto mejora el SEO de los 60+ artículos existentes en una sola ejecución.

Uso: python retrolink.py
"""

import sys, json, os, re, time
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

STOP_ES = {
    'de','la','el','en','y','a','los','las','con','para','por','que','es',
    'se','un','una','del','al','como','lo','su','le','si','no','mas','pero',
    'este','esta','esto','son','tiene','hacer','puede','sobre','entre','hasta',
    'desde','sin','que','como','cual','cuales','tambien','qué','cómo','cuál'
}

def words(text):
    clean = re.sub(r'[áàäâ]','a', re.sub(r'[éèëê]','e', re.sub(r'[íìïî]','i',
            re.sub(r'[óòöô]','o', re.sub(r'[úùüû]','u', text.lower())))))
    return set(clean.replace('-',' ').split()) - STOP_ES


def get_all_articles(wp_url, wp_user, wp_pass):
    """Descarga todos los artículos publicados (paginados)."""
    clean = wp_url.rstrip('/')
    articles = []
    page = 1
    while True:
        r = requests.get(
            f'{clean}/wp-json/wp/v2/posts',
            auth=(wp_user, wp_pass),
            params={
                'per_page': 50,
                'page': page,
                'status': 'publish',
                'orderby': 'date',
                'order': 'desc',
                '_fields': 'id,title,link,content'
            },
            timeout=20
        )
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        articles.extend(batch)
        total_pages = int(r.headers.get('X-WP-TotalPages', 1))
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.5)
    return articles


def find_related(article, all_articles, max_r=3):
    """Encuentra artículos relacionados por solapamiento de palabras en el título."""
    title = article.get('title', {}).get('rendered', '')
    art_id = article.get('id')
    kw = words(title)

    scored = []
    for other in all_articles:
        if other.get('id') == art_id:
            continue
        other_title = other.get('title', {}).get('rendered', '')
        overlap = len(kw & words(other_title))
        if overlap > 0:
            scored.append((overlap, other))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [a for _, a in scored[:max_r]]


def already_has_related_section(content_html):
    return 'articulos-relacionados' in content_html.lower() or \
           'artículos relacionados' in content_html.lower() or \
           'articulosrelacionados' in content_html.lower()


def build_related_section(related_articles, accent_color='#3b82f6'):
    items = ''
    for art in related_articles:
        title = art.get('title', {}).get('rendered', 'Artículo relacionado')
        link  = art.get('link', '#')
        items += (
            f'<li style="margin-bottom:.6rem">'
            f'<a href="{link}" style="color:{accent_color};text-decoration:none;font-weight:500">'
            f'→ {title}'
            f'</a></li>\n'
        )

    return f"""
<div class="articulos-relacionados" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:1.5rem;margin-top:2rem">
  <h3 style="font-size:1.1rem;font-weight:700;color:#1e293b;margin:0 0 1rem">📚 Artículos relacionados</h3>
  <ul style="list-style:none;padding:0;margin:0">
{items}  </ul>
</div>
"""


def update_article_content(post_id, new_content, wp_url, wp_user, wp_pass):
    clean = wp_url.rstrip('/')
    r = requests.post(
        f'{clean}/wp-json/wp/v2/posts/{post_id}',
        auth=(wp_user, wp_pass),
        json={'content': new_content},
        timeout=20
    )
    return r.status_code in (200, 201)


SITE_COLORS = {
    'ia_principiantes': '#3b82f6',
    'prompts':          '#10b981',
    'claude':           '#f97316',
}

print("=== RETROLINK — Enlazado interno retroactivo ===\n")
print("Esto añade una seccion 'Articulos relacionados' a los articulos existentes.")
print("Solo modifica articulos que NO la tengan ya.\n")

total_updated = 0
total_skipped = 0

for site in cfg.get('sites', []):
    name    = site.get('name', '?')
    url     = site.get('url', '').rstrip('/')
    user    = site.get('wp_user', '')
    pwd     = site.get('wp_password', '')
    kw_key  = site.get('keywords_key', '')
    color   = SITE_COLORS.get(kw_key, '#3b82f6')

    print(f">> {name} ({url})")

    if not url or not user or not pwd:
        print("   SKIP credenciales incompletas\n")
        continue

    print("   Descargando todos los articulos...", end=' ', flush=True)
    articles = get_all_articles(url, user, pwd)
    print(f"{len(articles)} articulos encontrados")

    if len(articles) < 2:
        print("   Pocos articulos para enlazar, saltando.\n")
        continue

    site_updated = 0
    site_skipped = 0

    for art in articles:
        post_id = art.get('id')
        title   = art.get('title', {}).get('rendered', '')
        content_raw = art.get('content', {}).get('rendered', '')

        if already_has_related_section(content_raw):
            site_skipped += 1
            continue

        related = find_related(art, articles, max_r=3)
        if not related:
            site_skipped += 1
            continue

        related_html = build_related_section(related, color)
        new_content  = content_raw + related_html

        ok = update_article_content(post_id, new_content, url, user, pwd)
        if ok:
            print(f"   OK  [{post_id}] {title[:55]}...")
            site_updated += 1
        else:
            print(f"   ERR [{post_id}] {title[:55]}...")
            site_skipped += 1

        time.sleep(0.8)  # Rate limiting — respeta el servidor

    total_updated += site_updated
    total_skipped += site_skipped
    print(f"\n   {name}: {site_updated} actualizados · {site_skipped} sin cambios\n")

print(f"=== Resumen ===")
print(f"Articulos actualizados: {total_updated}")
print(f"Sin cambios:            {total_skipped}")
print(f"")
print(f"Efecto SEO: los articulos ahora se enlazan entre si,")
print(f"construyendo autoridad topica en los 3 dominios.")
