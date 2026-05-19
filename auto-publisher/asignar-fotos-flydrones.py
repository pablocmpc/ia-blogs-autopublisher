#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca fotos de drones en Pexels y las asigna como featured image
a cada artículo de FlyDrones que no tenga imagen o tenga una genérica.
"""

import requests, sys, json, os, time, re
sys.stdout.reconfigure(encoding='utf-8')

WP_URL     = "https://flydrones.es"
WP_USER    = "bengalasdehumo@gmail.com"
WP_PASS    = "8y4i vkwU dVXc nbnZ MzD6 MA7S"
PEXELS_KEY = "IpGQKmCTDX8B7xr0vB3mvcga1U56Eci07f3uq4NL2ZsTJ6bq54rUt4z0"

# Mapa de palabras clave en el título → query Pexels óptimo
QUERY_MAP = [
    # específicos primero
    (["mini 4 pro"],                  "DJI Mini 4 Pro drone flying"),
    (["mini 3"],                      "DJI Mini drone compact"),
    (["air 3s", "air 3"],             "DJI Air drone professional"),
    (["mavic 3 pro", "mavic 3"],      "DJI Mavic drone aerial photography"),
    (["avata", "fpv"],                "FPV racing drone action"),
    (["lito 1", "lito"],              "beginner drone flight"),
    (["autel evo", "autel"],          "Autel drone orange flight"),
    (["mini 5 pro"],                  "DJI drone compact travel"),
    (["mavic 4"],                     "professional drone camera sky"),
    # temáticos
    (["carné", "carnet", "examen",
      "habilitación", "aesa", "licencia", "certificado"], "drone pilot flying legally"),
    (["normativa", "reglamento",
      "legal", "ley", "clase c"],     "drone rules regulations sky"),
    (["ganar dinero", "negocio",
      "trabajo", "profesional"],      "drone professional aerial work"),
    (["errores", "principiantes",
      "consejo", "tips"],             "beginner drone learning"),
    (["cámara 4k", "cámara", "mejor drone",
      "guía", "elegir"],              "drone camera aerial 4K quality"),
    (["comparativa", "vs"],           "drone comparison technology"),
]

DEFAULT_QUERY = "drone flying aerial photography"

def pexels_query(query):
    """Busca en Pexels y devuelve la URL de la mejor imagen horizontal >= 1200px."""
    r = requests.get("https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": 5, "orientation": "landscape",
                "min_width": 1200, "min_height": 630},
        timeout=15
    )
    if not r.ok:
        return None, None, None
    photos = r.json().get("photos", [])
    if not photos:
        return None, None, None
    p = photos[0]
    # Usar 'large2x' (1880px) o 'large' (940px)
    img_url = p["src"].get("large2x") or p["src"].get("large")
    attribution = p.get("photographer", "")
    photo_id = p.get("id", "")
    return img_url, attribution, photo_id

def get_best_query(title):
    tl = title.lower()
    for keywords, query in QUERY_MAP:
        if any(k in tl for k in keywords):
            return query
    return DEFAULT_QUERY

def upload_image_to_wp(img_url, filename, alt_text):
    """Descarga la imagen de Pexels y la sube a la media library de WordPress."""
    r = requests.get(img_url, timeout=30)
    if not r.ok:
        return None

    content_type = r.headers.get("Content-Type", "image/jpeg")
    ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
    fname = f"{filename}.{ext}"

    headers = {
        "Content-Disposition": f'attachment; filename="{fname}"',
        "Content-Type": content_type,
    }
    media_r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=(WP_USER, WP_PASS),
        headers=headers,
        data=r.content,
        timeout=60
    )
    if media_r.ok:
        media_id = media_r.json().get("id")
        # Actualizar alt text
        requests.post(f"{WP_URL}/wp-json/wp/v2/media/{media_id}",
            auth=(WP_USER, WP_PASS),
            json={"alt_text": alt_text, "caption": f"Foto: Pexels"},
            timeout=15
        )
        return media_id
    return None

def set_featured_image(post_id, media_id):
    r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
        auth=(WP_USER, WP_PASS),
        json={"featured_media": media_id},
        timeout=15
    )
    return r.ok

# ── EJECUTAR ────────────────────────────────────────────────────────────────
print("Obteniendo artículos de FlyDrones...")
r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts?per_page=50&_fields=id,title,slug,featured_media",
    auth=(WP_USER, WP_PASS), timeout=20)
posts = r.json()
posts = [p for p in posts if p["title"]["rendered"].lower() != "hello world"]
print(f"  {len(posts)} artículos encontrados\n")

used_queries = set()  # evitar duplicar la misma foto en artículos similares
results = []

for p in posts:
    post_id = p["id"]
    title   = p["title"]["rendered"]
    has_img = bool(p.get("featured_media"))

    print(f"[{'SKIP' if False else 'PROC'}] {title[:55]}")

    query = get_best_query(title)
    # Si el query ya lo usamos, añadir variación para evitar foto duplicada
    base_query = query
    attempt = 0
    while query in used_queries and attempt < 3:
        attempt += 1
        variations = [" outdoor", " sky", " professional", " action shot", " technology"]
        query = base_query + variations[attempt % len(variations)]

    print(f"  Query: {query}")
    img_url, photographer, _ = pexels_query(query)
    if not img_url:
        print(f"  Sin resultados en Pexels, intentando query genérico...")
        img_url, photographer, _ = pexels_query(DEFAULT_QUERY + " sky")

    if not img_url:
        print(f"  ERROR: no se encontró imagen")
        results.append((title, "ERROR"))
        continue

    used_queries.add(query)
    slug = p.get("slug", f"drone-{post_id}")[:40]
    alt_text = f"{title} - FlyDrones.es"

    print(f"  Subiendo imagen de {photographer}...")
    media_id = upload_image_to_wp(img_url, f"flydrones-{slug}", alt_text)
    if not media_id:
        print(f"  ERROR: fallo al subir imagen")
        results.append((title, "ERROR UPLOAD"))
        continue

    ok = set_featured_image(post_id, media_id)
    status = f"OK (media_id={media_id})" if ok else "ERROR SET"
    print(f"  Imagen asignada: {status}")
    results.append((title, status))
    time.sleep(1)  # pausa entre artículos

print("\n" + "="*60)
print("RESUMEN:")
for title, status in results:
    print(f"  [{status[:4]}] {title[:55]}")
