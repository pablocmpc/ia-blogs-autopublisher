#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asigna featured images de Pexels a todos los artículos sin imagen
en todas las webs del portfolio.
"""

import requests, sys, re, time, json
sys.stdout.reconfigure(encoding='utf-8')

PEXELS_KEY = "IpGQKmCTDX8B7xr0vB3mvcga1U56Eci07f3uq4NL2ZsTJ6bq54rUt4z0"

SITES = [
    {
        "name": "IA para Principiantes",
        "url":  "https://iaparaprincipiantes.es",
        "user": "bengalasdehumo@gmail.com",
        "pass": "ALZ8 5X0b gEKl YJVY CHWC Ldpk",
        "default_query": "artificial intelligence technology computer",
        "keyword_map": [
            (["chatgpt", "gpt"],            "ChatGPT AI conversation technology"),
            (["claude"],                     "Claude AI anthropic technology"),
            (["gemini"],                     "Google AI technology futuristic"),
            (["prompt"],                     "AI writing creative technology keyboard"),
            (["negocio", "empresa", "emprender", "dinero", "ganar"],
                                             "business technology entrepreneur AI"),
            (["automatizar", "automatización", "automatico"],
                                             "automation technology business computer"),
            (["imagen", "foto", "diseño", "arte", "crear"],
                                             "AI art design creative digital"),
            (["video", "vídeo"],             "AI video technology screen computer"),
            (["texto", "escrib", "redacc"],  "writing technology laptop creative"),
            (["herramienta", "tool", "app"], "AI tools software technology"),
            (["estadístic", "dato", "informe"], "data statistics technology chart"),
            (["trabajo", "profesional", "laboral"], "professional work technology laptop"),
            (["principiante", "básico", "empezar", "guía"],
                                             "learning technology digital beginner"),
        ]
    },
    {
        "name": "SuperPrompts",
        "url":  "https://superprompts.es",
        "user": "bengalasdehumo@gmail.com",
        "pass": "fh7t JV4H fVRt WS12 GwCU hwAp",
        "default_query": "AI prompt writing technology creative",
        "keyword_map": [
            (["chatgpt", "gpt"],            "ChatGPT conversation AI assistant"),
            (["claude"],                     "AI chat conversation technology"),
            (["midjourney", "imagen", "arte", "diseño"],
                                             "AI art generation creative digital"),
            (["marketing", "ventas", "copy"], "marketing copywriting professional"),
            (["programación", "código", "developer", "programar"],
                                             "programming code developer laptop"),
            (["negocio", "empresa"],         "business AI technology productivity"),
            (["escritura", "texto", "redacc"], "writing creative technology"),
            (["seo"],                         "SEO search engine digital marketing"),
            (["instagram", "redes", "social"], "social media content creator phone"),
            (["estadístic", "dato"],          "data technology AI analytics"),
        ]
    },
    {
        "name": "Guía Claude",
        "url":  "https://guiaclaude.es",
        "user": "bengalasdehumo@gmail.com",
        "pass": "2RBK hzue 6a7C 6n1c hxU4 PXz3",
        "default_query": "artificial intelligence Claude anthropic computer",
        "keyword_map": [
            (["claude 3", "claude opus", "claude sonnet", "claude haiku"],
                                             "AI technology futuristic screen interface"),
            (["api", "integración", "developer", "programa"],
                                             "API developer coding technology"),
            (["vs", "comparativa", "comparar", "chatgpt"],
                                             "AI comparison technology computer"),
            (["negocio", "empresa"],         "business AI productivity technology"),
            (["prompt", "instruccion"],      "AI writing prompt technology keyboard"),
            (["novedades", "nuevo", "lanzamiento"],
                                             "AI technology innovation future"),
            (["estadístic", "dato"],         "data technology analytics chart"),
        ]
    },
    {
        "name": "Bengalas de Humo",
        "url":  "https://bengalasdehumo.es",
        "user": "bengalasdehumo@gmail.com",
        "pass": "RgvQ B927 3dIo tz4N o8r0 8jZL",
        "default_query": "smoke bomb colored photography outdoor",
        "keyword_map": [
            (["boda", "casamiento", "novio", "novia"],
                                             "smoke bomb wedding photography romantic"),
            (["quinceañera", "quince", "fiesta", "cumpleaños"],
                                             "colorful smoke party celebration photography"),
            (["fotografía", "fotógrafo", "foto", "sesión"],
                                             "smoke photography creative colorful"),
            (["humo", "bengala"],            "smoke bomb colorful outdoor photo"),
            (["color", "colores"],           "colorful smoke bomb photography art"),
            (["seguridad", "usar", "cómo"], "smoke bomb safe outdoor use"),
            (["tendencia", "moda", "2026"],  "smoke photography trend creative"),
        ]
    },
    {
        "name": "Turismo Ourense",
        "url":  "https://turismoourense.es",
        "user": "bengalasdehumo@gmail.com",
        "pass": "N8OW HTMH INJP fdKy k7u1 fOyO",
        "default_query": "Galicia Spain tourism medieval architecture",
        "keyword_map": [
            (["terma", "balneario", "spa", "baño termal", "outariz", "chavasqueira"],
                                             "thermal hot springs spa natural water"),
            (["gastronomía", "comer", "pulpo", "vino", "restaurante"],
                                             "Spanish food Galicia traditional restaurant"),
            (["ribeira sacra", "cañón", "sil", "naturaleza", "ruta"],
                                             "Galicia nature landscape river canyon"),
            (["catedral", "iglesia", "monasterio", "historia"],
                                             "medieval church cathedral Spain architecture"),
            (["alojamiento", "hotel", "rural", "escapada"],
                                             "rural hotel Spain stone cottage cozy"),
            (["feria", "fiesta", "festival", "carnaval"],
                                             "Spain traditional festival celebration"),
            (["senderismo", "monte", "camino"],
                                             "hiking trail Galicia mountain nature"),
        ]
    },
]

# ────────────────────────────────────────────────────────────────────────────

used_pexels_ids = set()

def get_query(title, keyword_map, default_query):
    tl = title.lower()
    for keywords, query in keyword_map:
        if any(k in tl for k in keywords):
            return query
    return default_query

def pexels_search(query, exclude_ids):
    """Devuelve (img_url, photographer, photo_id) o (None,None,None)."""
    for page in [1, 2, 3]:
        try:
            r = requests.get("https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": query, "per_page": 10, "orientation": "landscape",
                        "min_width": 900, "min_height": 500, "page": page},
                timeout=15
            )
            if not r.ok:
                break
            for p in r.json().get("photos", []):
                if p["id"] not in exclude_ids:
                    url = p["src"].get("large2x") or p["src"].get("large")
                    return url, p.get("photographer",""), p.get("id")
        except Exception:
            break
    return None, None, None

def upload_featured_image(wp_url, wp_user, wp_pass, img_url, slug, alt_text):
    """Sube la imagen y devuelve media_id, o None si falla."""
    try:
        r = requests.get(img_url, timeout=30)
        if not r.ok:
            return None
        ct  = r.headers.get("Content-Type", "image/jpeg")
        ext = "jpg" if "jpeg" in ct else ct.split("/")[-1]
        fname = f"{slug[:40]}.{ext}"
        mr = requests.post(f"{wp_url}/wp-json/wp/v2/media",
            auth=(wp_user, wp_pass),
            headers={"Content-Disposition": f'attachment; filename="{fname}"', "Content-Type": ct},
            data=r.content, timeout=60)
        if mr.ok:
            mid = mr.json().get("id")
            requests.post(f"{wp_url}/wp-json/wp/v2/media/{mid}",
                auth=(wp_user, wp_pass),
                json={"alt_text": alt_text, "caption": "Foto: Pexels"},
                timeout=15)
            return mid
    except Exception as e:
        print(f"    upload error: {e}")
    return None

def set_featured(wp_url, wp_user, wp_pass, post_id, media_id):
    r = requests.post(f"{wp_url}/wp-json/wp/v2/posts/{post_id}",
        auth=(wp_user, wp_pass), json={"featured_media": media_id}, timeout=15)
    return r.ok

# ── MAIN ────────────────────────────────────────────────────────────────────
total_ok = 0
total_err = 0

for site in SITES:
    name = site["name"]
    url  = site["url"]
    user = site["user"]
    pw   = site["pass"]
    default_q = site["default_query"]
    kw_map = site["keyword_map"]

    print(f"\n{'='*60}")
    print(f"SITIO: {name} ({url})")
    print("="*60)

    # Obtener TODOS los posts (paginar)
    all_posts = []
    page = 1
    while True:
        r = requests.get(
            f"{url}/wp-json/wp/v2/posts?per_page=100&page={page}"
            "&_fields=id,title,slug,featured_media",
            auth=(user, pw), timeout=20)
        if not r.ok:
            break
        batch = r.json()
        if not batch:
            break
        all_posts.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    # Filtrar los sin imagen y sin "hello world"
    missing = [p for p in all_posts
               if not p.get("featured_media")
               and "hello world" not in p["title"]["rendered"].lower()]

    print(f"  {len(missing)} artículos sin imagen featured")

    site_used_ids = set()

    for p in missing:
        post_id = p["id"]
        title   = p["title"]["rendered"]
        slug    = p.get("slug", f"post-{post_id}")
        query   = get_query(title, kw_map, default_q)

        # Intentar con el query específico, luego el default
        img_url, photographer, pid = pexels_search(
            query, used_pexels_ids | site_used_ids)

        if not img_url:
            img_url, photographer, pid = pexels_search(
                default_q, used_pexels_ids | site_used_ids)

        if not img_url:
            print(f"  [ERR] Sin imagen: {title[:45]}")
            total_err += 1
            continue

        if pid:
            site_used_ids.add(pid)
            used_pexels_ids.add(pid)

        alt = f"{title}"
        mid = upload_featured_image(url, user, pw, img_url, f"{name[:5].lower()}-{slug}", alt)
        if not mid:
            print(f"  [ERR] Upload fallido: {title[:45]}")
            total_err += 1
            continue

        ok = set_featured(url, user, pw, post_id, mid)
        if ok:
            print(f"  [OK ] {title[:50]} (de {photographer})")
            total_ok += 1
        else:
            print(f"  [ERR] No se asignó imagen: {title[:45]}")
            total_err += 1
        time.sleep(0.8)

print(f"\n{'='*60}")
print(f"TOTAL: {total_ok} OK, {total_err} errores")
