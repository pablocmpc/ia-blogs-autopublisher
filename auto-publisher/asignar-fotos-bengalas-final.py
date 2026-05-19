#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, sys, time
sys.stdout.reconfigure(encoding='utf-8')

WP_URL  = "https://bengalasdehumo.es"
WP_USER = "bengalasdehumo@gmail.com"
WP_PASS = "RgvQ B927 3dIo tz4N o8r0 8jZL"
PEXELS  = "IpGQKmCTDX8B7xr0vB3mvcga1U56Eci07f3uq4NL2ZsTJ6bq54rUt4z0"

KW_MAP = [
    (["boda","novio","novia","casamiento","matrimonio"], "smoke bomb wedding photography romantic"),
    (["quinceañ","quince","fiesta","cumpleaños"],         "colorful smoke party celebration"),
    (["fotografí","fotógrafo","foto","sesión","sesion"],  "smoke photography creative colorful"),
    (["rosa","pink"],                                      "pink smoke bomb photography"),
    (["azul","blue"],                                      "blue smoke bomb photography outdoor"),
    (["verde","green"],                                    "green smoke bomb outdoor nature"),
    (["naranja","amarillo","orange"],                      "orange smoke bomb photography"),
    (["blanco","white"],                                   "white smoke bomb photography ethereal"),
    (["color","colores","arcoiris","multicolor"],          "colorful smoke bomb photography art"),
    (["interior","inside","estudio","studio"],             "smoke bomb indoor photography studio"),
    (["playa","beach","agua","water"],                     "smoke bomb beach photography ocean"),
    (["montaña","mountain","campo","nature","naturaleza"], "smoke bomb nature mountain outdoor"),
    (["seguridad","seguro","usar","cómo","como"],          "smoke bomb safe outdoor use instructions"),
    (["comprar","precio","donde","tienda"],                "smoke bomb product photography buy"),
    (["tendenci","moda","2026","trend"],                   "smoke bomb photography trend creative"),
    (["tips","consejo","truco","técnica","tecnica"],       "smoke photography tips technique"),
    (["niños","ninos","familia","family"],                 "colorful smoke outdoor family fun"),
    (["retrato","portrait"],                               "smoke bomb portrait photography"),
]
DEFAULT = "smoke bomb colored photography outdoor"

used_ids = set()

def query_for(title):
    tl = title.lower()
    for kws, q in KW_MAP:
        if any(k in tl for k in kws):
            return q
    return DEFAULT

def pexels_img(query):
    for page in [1,2,3]:
        r = requests.get("https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS},
            params={"query": query, "per_page": 10, "orientation": "landscape",
                    "min_width": 900, "min_height": 500, "page": page},
            timeout=15)
        if not r.ok: break
        for p in r.json().get("photos", []):
            if p["id"] not in used_ids:
                url = p["src"].get("large2x") or p["src"].get("large")
                return url, p.get("photographer",""), p.get("id")
    return None, None, None

def upload(img_url, slug, alt):
    r = requests.get(img_url, timeout=30)
    if not r.ok: return None
    ct = r.headers.get("Content-Type","image/jpeg")
    ext = "jpg" if "jpeg" in ct else ct.split("/")[-1]
    mr = requests.post(f"{WP_URL}/wp-json/wp/v2/media",
        auth=(WP_USER, WP_PASS),
        headers={"Content-Disposition": f'attachment; filename="bengala-{slug[:30]}.{ext}"', "Content-Type": ct},
        data=r.content, timeout=60)
    if mr.ok:
        mid = mr.json()["id"]
        requests.post(f"{WP_URL}/wp-json/wp/v2/media/{mid}",
            auth=(WP_USER, WP_PASS), json={"alt_text": alt, "caption": "Foto: Pexels"}, timeout=15)
        return mid
    return None

# Obtener todos los posts sin imagen
all_posts = []
page = 1
while True:
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts?per_page=100&page={page}&_fields=id,title,slug,featured_media",
        auth=(WP_USER, WP_PASS), timeout=20)
    if not r.ok or not r.json(): break
    all_posts.extend(r.json())
    if len(r.json()) < 100: break
    page += 1

missing = [p for p in all_posts if not p.get("featured_media")
           and "hello world" not in p["title"]["rendered"].lower()]
print(f"Posts sin imagen: {len(missing)}")

ok = 0
for p in missing:
    title = p["title"]["rendered"]
    slug  = p.get("slug", f"post-{p['id']}")
    q = query_for(title)
    img_url, phot, pid = pexels_img(q)
    if not img_url:
        img_url, phot, pid = pexels_img(DEFAULT)
    if not img_url:
        print(f"  [ERR] Sin foto: {title[:50]}")
        continue
    if pid: used_ids.add(pid)
    mid = upload(img_url, slug, title)
    if not mid:
        print(f"  [ERR] Upload falló: {title[:50]}")
        continue
    r2 = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{p['id']}",
        auth=(WP_USER, WP_PASS), json={"featured_media": mid}, timeout=15)
    if r2.ok:
        print(f"  [OK ] {title[:55]} (de {phot})")
        ok += 1
    else:
        print(f"  [ERR] No asignada: {title[:50]}")
    time.sleep(0.8)

print(f"\nTotal asignadas: {ok}/{len(missing)}")
