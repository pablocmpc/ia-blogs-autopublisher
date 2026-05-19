#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera y publica un artículo de alta calidad con Groq para una keyword específica.
Uso: python publicar-articulo-objetivo.py
"""

import requests, sys, json, re, time
sys.stdout.reconfigure(encoding='utf-8')

# ── CONFIG ─────────────────────────────────────────────────────────────────
GROQ_KEY = "CAMBIA_ESTO_POR_TU_CLAVE_GROQ"  # no hardcodear claves aqui
INDEXNOW_KEY = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"

# Lista de artículos objetivo: (site_name, wp_url, wp_user, wp_pass, keyword, niche_context)
TARGETS = [
    (
        "FlyDrones",
        "https://flydrones.es",
        "bengalasdehumo@gmail.com",
        "8y4i vkwU dVXc nbnZ MzD6 MA7S",
        "cómo sacar el carné de drones en España examen AESA",
        "Blog de drones en español: normativa AESA, guías de compra DJI, fotografía aérea."
    ),
    (
        "IA para Principiantes",
        "https://iaparaprincipiantes.es",
        "bengalasdehumo@gmail.com",
        "ALZ8 5X0b gEKl YJVY CHWC Ldpk",
        "cómo ganar dinero con inteligencia artificial en España 2026",
        "Blog sobre IA para personas sin conocimientos técnicos. Tutoriales, herramientas gratuitas, ideas de negocio con IA."
    ),
    (
        "Turismo Ourense",
        "https://turismoourense.es",
        "bengalasdehumo@gmail.com",
        "N8OW HTMH INJP fdKy k7u1 fOyO",
        "termas gratuitas Ourense guía completa horarios 2026",
        "Blog de turismo sobre Ourense: termas, gastronomía gallega, rutas, alojamientos rurales."
    ),
    (
        "Bengalas de Humo",
        "https://bengalasdehumo.es",
        "bengalasdehumo@gmail.com",
        "RgvQ B927 3dIo tz4N o8r0 8jZL",
        "bengalas de humo para quinceañeras ideas fotos",
        "Blog sobre bengalas de humo y bombas de humo de colores para fotografía y eventos."
    ),
]

GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
]

def groq_generate(prompt):
    for model in GROQ_MODELS:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 4096,
                },
                timeout=120
            )
            if r.ok:
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"    Groq error ({model}): {e}")
            time.sleep(2)
    return None

def publish_article(site_name, wp_url, wp_user, wp_pass, keyword, niche_context):
    import datetime
    year = datetime.datetime.now().year

    print(f"\n{'='*60}")
    print(f"Generando artículo para {site_name}: '{keyword}'")

    prompt = f"""Escribe un artículo SEO completo en español para el blog: {niche_context}

KEYWORD OBJETIVO: {keyword}
AÑO ACTUAL: {year}

ESTRUCTURA OBLIGATORIA:
- Título SEO optimizado (máx 60 caracteres, con el año {year})
- Meta descripción (máx 155 caracteres)
- Artículo completo en HTML con bloques WordPress (<!-- wp:paragraph -->, <!-- wp:heading -->, etc.)
- Mínimo 2200 palabras
- H2 principales (4-6 secciones)
- H3 subsecciones donde sea necesario
- Al menos una tabla HTML informativa
- Lista de preguntas frecuentes con schema FAQPage JSON-LD al final
- 2-3 enlaces externos a fuentes autoritativas (.gov, .edu, Wikipedia, fuentes oficiales)
- Lenguaje natural, informativo, sin relleno

RESPONDE EXACTAMENTE en este formato JSON (sin markdown, sin código adicional):
{{
  "titulo": "...",
  "meta_descripcion": "...",
  "slug": "...",
  "contenido_html": "...html completo del artículo..."
}}"""

    raw = groq_generate(prompt)
    if not raw:
        print(f"  ERROR: no se pudo generar el artículo")
        return None

    # Extraer JSON
    try:
        # Intentar parsear directamente
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Buscar JSON en el texto
        match = re.search(r'\{[\s\S]*"titulo"[\s\S]*"contenido_html"[\s\S]*\}', raw)
        if not match:
            print(f"  ERROR: JSON no encontrado en respuesta")
            return None
        try:
            data = json.loads(match.group(0))
        except:
            print(f"  ERROR: JSON inválido")
            return None

    titulo      = data.get("titulo", keyword[:60])
    meta_desc   = data.get("meta_descripcion", "")
    slug        = data.get("slug", re.sub(r'[^a-z0-9]+', '-', keyword.lower()))[:60]
    contenido   = data.get("contenido_html", "")

    if len(contenido) < 1000:
        print(f"  AVISO: artículo muy corto ({len(contenido)} chars)")

    print(f"  Título: {titulo}")
    print(f"  Longitud: {len(contenido)} chars")

    # Publicar en WP
    post_data = {
        "title":   titulo,
        "content": contenido,
        "excerpt": meta_desc,
        "status":  "publish",
        "slug":    slug,
        "meta": {
            "rank_math_title":         titulo,
            "rank_math_description":   meta_desc,
            "rank_math_focus_keyword": keyword
        }
    }

    r = requests.post(f"{wp_url}/wp-json/wp/v2/posts",
        auth=(wp_user, wp_pass), json=post_data, timeout=30)

    if r.ok:
        post_url = r.json().get("link", "")
        host     = wp_url.replace("https://", "").rstrip("/")
        print(f"  PUBLICADO: {post_url}")

        # IndexNow
        requests.post("https://api.indexnow.org/indexnow",
            json={"host": host, "key": INDEXNOW_KEY,
                  "keyLocation": f"{wp_url}/{INDEXNOW_KEY}.txt",
                  "urlList": [post_url]},
            headers={"Content-Type": "application/json"}, timeout=10)
        return post_url
    else:
        print(f"  ERROR WP {r.status_code}: {r.text[:200]}")
        return None

# ── EJECUTAR ────────────────────────────────────────────────────────────────
results = []
for args in TARGETS:
    url = publish_article(*args)
    results.append((args[0], args[4], url))
    time.sleep(3)  # pausa entre publicaciones

print("\n" + "="*60)
print("RESUMEN:")
for name, kw, url in results:
    status = "OK" if url else "ERROR"
    print(f"  [{status}] {name}: {url or 'falló'}")
