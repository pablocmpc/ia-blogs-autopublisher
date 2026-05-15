# -*- coding: utf-8 -*-
"""
PUBLICADOR MULTIIDIOMA — Inglés y Portugués para las webs de IA
Genera el mismo artículo en español, inglés y portugués y lo publica en cada web.
Esto multiplica el tráfico orgánico internacional sin webs adicionales.

Estrategia:
  1. Añade hreflang al artículo original para que Google sepa los idiomas
  2. Genera versiones EN y PT del mismo artículo via Groq
  3. Los publica en el mismo WordPress como posts adicionales con slug -en / -pt

Uso:
  python publicar-multiidioma.py                          # 1 artículo EN+PT en cada web IA
  python publicar-multiidioma.py iaparaprincipiantes en   # Solo inglés en IA Principiantes
  python publicar-multiidioma.py superprompts en pt       # EN y PT en SuperPrompts
"""
import requests, json, os, sys, time, random, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

config = json.load(open(CONFIG_FILE, encoding='utf-8'))

# Solo las webs de IA tienen sentido en inglés/portugués
IA_SITES_KEYS = ['ia_principiantes', 'prompts', 'claude']

LANG_CONFIG = {
    'en': {
        'name': 'English',
        'prompt_lang': 'British English',
        'audience': 'English-speaking professionals, entrepreneurs and digital workers worldwide',
        'suffix': '-en',
    },
    'pt': {
        'name': 'Português',
        'prompt_lang': 'Brazilian Portuguese (Portuguese from Brazil)',
        'audience': 'Profissionais, empreendedores e trabalhadores digitais do Brasil e Portugal',
        'suffix': '-pt',
    }
}

MULTILANG_KEYWORDS = {
    'ia_principiantes': {
        'en': [
            'how to use artificial intelligence for beginners complete guide',
            'best free AI tools to boost your productivity',
            'how to make money with AI in 2025 complete guide',
            'AI for small business complete practical guide',
            'how to automate your work with AI no coding required',
        ],
        'pt': [
            'como usar inteligência artificial para iniciantes guia completo',
            'melhores ferramentas de IA gratuitas para aumentar produtividade',
            'como ganhar dinheiro com inteligência artificial em 2025',
            'IA para pequenos negócios guia completo e prático',
            'como automatizar seu trabalho com IA sem programar',
        ]
    },
    'prompts': {
        'en': [
            'complete guide to prompt engineering for ChatGPT and Claude 2025',
            'best 100 ChatGPT prompts you need to know',
            'how to write perfect prompts for AI complete guide',
            'advanced prompt engineering professional techniques',
            'prompts for digital marketing that get real results',
        ],
        'pt': [
            'guia completo de prompt engineering para ChatGPT e Claude 2025',
            'os 100 melhores prompts para ChatGPT que você precisa conhecer',
            'como escrever prompts perfeitos para inteligência artificial',
            'prompt engineering avançado técnicas profissionais completas',
            'prompts para marketing digital que geram resultados reais',
        ]
    },
    'claude': {
        'en': [
            'complete guide to Claude by Anthropic everything you need to know',
            'claude vs chatgpt ultimate comparison which is better in 2025',
            'how to use claude api for your business complete guide',
            'claude for business real use cases and results',
            'claude projects and artifacts complete professional guide',
        ],
        'pt': [
            'guia completo do Claude da Anthropic tudo que você precisa saber',
            'claude vs chatgpt comparação definitiva qual é melhor em 2025',
            'como usar a API do Claude para seu negócio guia completo',
            'claude para empresas casos de uso reais e resultados',
            'claude projects e artifacts guia definitivo de uso profissional',
        ]
    }
}


def generate_multilang_article(keyword, niche_context, site_name, groq_key, lang='en'):
    lang_cfg  = LANG_CONFIG[lang]
    prompt = f"""You are the best SEO content writer for {lang_cfg['name']} speaking markets.
Write a complete, high-quality SEO article about this topic to rank in Top 3 on Google.

MAIN KEYWORD: "{keyword}"
BLOG: {site_name}
LANGUAGE: Write entirely in {lang_cfg['prompt_lang']}
NICHE: {niche_context}
TARGET AUDIENCE: {lang_cfg['audience']}

E-E-A-T REQUIREMENTS:
- Show real practical experience with concrete examples
- Include at least 3 statistics with source and year
- Expert perspective: what a 10-year professional knows that beginners don't
- At least 1 surprising or counterintuitive fact

TECHNICAL REQUIREMENTS:
- Language: {lang_cfg['prompt_lang']} — natural, flowing prose
- Length: 1,800-2,500 words
- Keyword in: H1, first paragraph, at least 3 H2s, naturally in body
- Short paragraphs: max 3-4 lines
- <ul>/<ol> lists in at least 2 sections
- <strong> on key concepts (5-8 per article)
- At least 1 HTML comparison table if topic allows
- SEO title with number or power word

REQUIRED STRUCTURE:
1. H1 with keyword + compelling hook
2. Intro with impactful stat + concrete promise
3. "In this article you will learn:" with 4-5 points
4. 5-7 H2 sections with dense practical content
5. Step-by-step guide section
6. Common mistakes section
7. FAQ section with exactly 5 H3 questions and answers
8. Conclusion with CTA

Respond ONLY with valid JSON:
{{
  "titulo_seo": "SEO Title 55-60 chars with keyword + number or power word",
  "meta_descripcion": "Meta 150-155 chars with keyword + concrete benefit + CTA",
  "slug": "seo-url-no-accents-with-hyphens{lang_cfg['suffix']}",
  "h1": "H1 of the article",
  "contenido_html": "Complete article in HTML. Minimum 1800 words.",
  "tags": ["tag1","tag2","tag3","tag4","tag5"],
  "categoria": "Category 1-3 words"
}}"""

    resp = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'},
        json={
            'model': 'llama-3.3-70b-versatile',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.72,
            'max_tokens': 6000,
            'response_format': {'type': 'json_object'}
        },
        timeout=90
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
        'ia_principiantes': ['artificial intelligence technology laptop', 'machine learning data'],
        'prompts': ['ai writing keyboard creative', 'person typing laptop workspace'],
        'claude': ['ai assistant interface laptop', 'artificial intelligence technology'],
    }
    headers = {'Authorization': pexels_key}
    for q in [keyword] + NICHE_QUERIES.get(site_key, ['technology digital']):
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


def publish_article(article, site, image_data, lang):
    clean   = site['url'].rstrip('/')
    content = article['contenido_html']

    # Hreflang tag para SEO multiidioma
    hreflang = f'<link rel="alternate" hreflang="{lang}" href="{clean}/{article[\"slug\"]}/" />'
    content = f'<!-- hreflang:{lang} -->\n' + content

    if image_data:
        img_html = (f'<figure class="wp-block-image size-large">'
                    f'<img src="{image_data["url"]}" alt="{image_data["alt"]}" '
                    f'width="1280" height="853" style="width:100%;height:auto;border-radius:8px;margin-bottom:1.5em"/>'
                    f'</figure>\n')
        content = img_html + content

    media_id = None
    if image_data:
        try:
            img_bytes = requests.get(image_data['url'], timeout=30).content
            r_m = requests.post(f'{clean}/wp-json/wp/v2/media',
                headers={'Content-Disposition': f'attachment; filename=img-{lang}.jpg', 'Content-Type': 'image/jpeg'},
                data=img_bytes, auth=(site['wp_user'], site['wp_password']), timeout=45)
            if r_m.status_code in [200, 201]:
                media_id = r_m.json()['id']
        except Exception:
            pass

    cat_id = 1
    try:
        r_c = requests.post(f'{clean}/wp-json/wp/v2/categories',
            json={'name': article.get('categoria', 'AI')},
            auth=(site['wp_user'], site['wp_password']), timeout=10)
        if r_c.status_code in [200, 201]:
            cat_id = r_c.json()['id']
    except Exception:
        pass

    tag_ids = []
    for tag in article.get('tags', [])[:5]:
        try:
            r_t = requests.post(f'{clean}/wp-json/wp/v2/tags',
                json={'name': tag}, auth=(site['wp_user'], site['wp_password']), timeout=10)
            if r_t.status_code in [200, 201]:
                tag_ids.append(r_t.json()['id'])
        except Exception:
            pass

    post = {
        'title': article['titulo_seo'],
        'content': content,
        'excerpt': article['meta_descripcion'],
        'slug': article['slug'],
        'status': 'publish',
        'categories': [cat_id],
        'tags': tag_ids,
    }
    if media_id:
        post['featured_media'] = media_id
    if site.get('riker_author_id'):
        post['author'] = site['riker_author_id']

    for url in [f'{clean}/wp-json/wp/v2/posts', f'{clean}/index.php?rest_route=/wp/v2/posts']:
        r = requests.post(url, json=post, auth=(site['wp_user'], site['wp_password']), timeout=45)
        if r.status_code == 201:
            return r.json().get('link', '')
    raise Exception(f"WP {r.status_code}: {r.text[:100]}")


def main():
    args       = sys.argv[1:]
    filter_kw  = args[0] if args else None
    langs      = [l for l in args[1:] if l in ['en', 'pt']] or ['en', 'pt']

    groq_key   = config['groq_api_key']
    pexels_key = config['pexels_api_key']
    sites = [s for s in config['sites'] if s['keywords_key'] in IA_SITES_KEYS]

    if filter_kw:
        sites = [s for s in sites if filter_kw.lower() in s['url'].lower() or filter_kw in s['keywords_key']]

    print(f'\n{"="*60}')
    print(f'  PUBLICADOR MULTIIDIOMA  |  Idiomas: {", ".join(langs).upper()}')
    print(f'  Webs: {len(sites)}')
    print(f'{"="*60}\n')

    for site in sites:
        kw_key   = site['keywords_key']
        kw_langs = MULTILANG_KEYWORDS.get(kw_key, {})

        for lang in langs:
            keywords = kw_langs.get(lang, [])
            if not keywords:
                print(f'{site["name"]} [{lang.upper()}]: Sin keywords definidas')
                continue

            keyword = keywords[0]
            print(f'\n[{site["name"]}] [{lang.upper()}] «{keyword}»')
            try:
                print(f'  → Generando artículo en {LANG_CONFIG[lang]["name"]}...', end=' ', flush=True)
                article = generate_multilang_article(keyword, site['niche_context'], site['name'], groq_key, lang)
                words   = len(re.sub('<[^>]+>', '', article['contenido_html']).split())
                print(f'OK ({words} palabras)')

                print(f'  → Imagen...', end=' ', flush=True)
                img = get_pexels_image(keyword, pexels_key, site_key=kw_key)
                print('OK' if img else 'no encontrada')

                print(f'  → Publicando...', end=' ', flush=True)
                url = publish_article(article, site, img, lang)
                print(f'OK  {url}')

            except Exception as e:
                print(f'\n  ERROR: {e}')

            time.sleep(4)
        time.sleep(3)

    print(f'\n{"="*60}')
    print('Artículos multiidioma publicados.')

if __name__ == '__main__':
    main()
