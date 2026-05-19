#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inserta imágenes Pexels dentro del contenido de los artículos de FlyDrones.
Añade 3 imágenes por artículo: inicio, medio y final del contenido.
"""

import requests, sys, re, time
sys.stdout.reconfigure(encoding='utf-8')

WP_URL     = "https://flydrones.es"
WP_USER    = "bengalasdehumo@gmail.com"
WP_PASS    = "8y4i vkwU dVXc nbnZ MzD6 MA7S"
PEXELS_KEY = "IpGQKmCTDX8B7xr0vB3mvcga1U56Eci07f3uq4NL2ZsTJ6bq54rUt4z0"

# Artículos a procesar: (post_id, [query1, query2, query3])
ARTICLES = [
    (38, [  # DJI Mini 4 Pro review
        "DJI Mini drone compact white flying",
        "drone aerial photography landscape mountain",
        "drone outdoor pilot nature"
    ]),
    (36, [  # DJI Air 3S review
        "professional drone camera aerial",
        "cinematic drone photography sunset",
        "drone aerial video filming"
    ]),
    (40, [  # DJI Mini 3 review
        "small drone flying outdoors",
        "drone compact travel photography",
        "aerial drone photo city"
    ]),
    (34, [  # DJI Mavic 3 Pro review
        "DJI Mavic drone professional photography",
        "aerial drone landscape cinematic",
        "drone photography golden hour"
    ]),
    (42, [  # DJI Avata 2 FPV review
        "FPV racing drone pilot action",
        "drone fpv flying fast speed",
        "drone racing first person view"
    ]),
    (52, [  # Normativa drones 2026
        "drone pilot rules law documentation",
        "drone flying regulation zone",
        "drone operator safety outdoor"
    ]),
    (53, [  # Carné drones AESA
        "drone pilot exam certification test",
        "drone license certificate flying",
        "drone school training flying"
    ]),
    (32, [  # DJI Lito 1 review
        "beginner drone easy flight",
        "drone first flight outdoor",
        "drone beginner photography"
    ]),
    (28, [  # Guía elegir drone cámara 4K
        "drone camera quality 4K video",
        "different drones comparison technology",
        "best drone flying landscape photography"
    ]),
    (26, [  # Clases C0, C1, C2 Europa
        "drone categories classes europe",
        "drone regulation europe sky",
        "drone flying city buildings"
    ]),
    (24, [  # DJI Mini 4 Pro precio y compra
        "DJI drone store buy new",
        "drone shopping technology gadget",
        "drone unboxing new product"
    ]),
]

used_img_ids = set()

def pexels_search(query, exclude_ids=None):
    """Busca imagen en Pexels, evitando IDs ya usados."""
    for page in [1, 2]:
        r = requests.get("https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 10, "orientation": "landscape",
                    "min_width": 1000, "min_height": 600, "page": page},
            timeout=15
        )
        if not r.ok:
            continue
        photos = r.json().get("photos", [])
        for p in photos:
            if exclude_ids and p["id"] in exclude_ids:
                continue
            img_url = p["src"].get("large2x") or p["src"].get("large")
            return img_url, p.get("photographer", ""), p.get("id")
    return None, None, None

def upload_to_wp(img_url, slug, alt_text):
    """Sube imagen a WP media library y devuelve (media_id, media_url)."""
    r = requests.get(img_url, timeout=30)
    if not r.ok:
        return None, None
    ct = r.headers.get("Content-Type", "image/jpeg")
    ext = "jpg" if "jpeg" in ct else ct.split("/")[-1]
    fname = f"flydrones-{slug[:40]}.{ext}"
    headers = {"Content-Disposition": f'attachment; filename="{fname}"', "Content-Type": ct}
    mr = requests.post(f"{WP_URL}/wp-json/wp/v2/media",
        auth=(WP_USER, WP_PASS), headers=headers, data=r.content, timeout=60)
    if mr.ok:
        media_id  = mr.json().get("id")
        media_url = mr.json().get("source_url", "")
        requests.post(f"{WP_URL}/wp-json/wp/v2/media/{media_id}",
            auth=(WP_USER, WP_PASS),
            json={"alt_text": alt_text, "caption": "Foto: Pexels"},
            timeout=15)
        return media_id, media_url
    return None, None

def make_img_block(media_id, media_url, alt_text, caption=""):
    """Genera bloque Gutenberg wp:image."""
    return f"""
<!-- wp:image {{"id":{media_id},"sizeSlug":"large","linkDestination":"none"}} -->
<figure class="wp-block-image size-large"><img src="{media_url}" alt="{alt_text}" class="wp-image-{media_id}"{(' title="'+caption+'"') if caption else ''}/>
{('<figcaption class="wp-element-caption">'+caption+'</figcaption>') if caption else ''}
</figure>
<!-- /wp:image -->
"""

def insert_images_in_content(content, img_blocks):
    """
    Inserta imágenes en 3 posiciones estratégicas del contenido:
    - img_blocks[0]: tras el primer párrafo
    - img_blocks[1]: tras el tercer H2
    - img_blocks[2]: antes del último H2 / sección de cierre
    """
    # Encontrar posiciones de los bloques <!-- wp:heading --> de nivel H2
    h2_positions = [m.start() for m in re.finditer(r'<!-- wp:heading(?! \{"level":3)', content)]

    # Encontrar fin del primer párrafo
    first_para_end = content.find("<!-- /wp:paragraph -->")
    if first_para_end != -1:
        first_para_end += len("<!-- /wp:paragraph -->")

    insertions = []  # list of (position, block_text)

    # Inserción 1: tras primer párrafo
    if len(img_blocks) > 0 and first_para_end > 0:
        insertions.append((first_para_end, img_blocks[0]))

    # Inserción 2: tras el 3er H2 (si existe)
    if len(img_blocks) > 1 and len(h2_positions) >= 3:
        pos = h2_positions[2]
        # Buscar el fin del párrafo que sigue al H2
        next_para_end = content.find("<!-- /wp:paragraph -->", pos)
        if next_para_end != -1:
            insertions.append((next_para_end + len("<!-- /wp:paragraph -->"), img_blocks[1]))
        else:
            insertions.append((pos, img_blocks[1]))

    # Inserción 3: antes del último H2
    if len(img_blocks) > 2 and len(h2_positions) >= 2:
        last_h2_pos = h2_positions[-1]
        insertions.append((last_h2_pos, img_blocks[2]))

    if not insertions:
        return content + "\n".join(img_blocks)

    # Insertar en orden inverso para no desplazar posiciones
    insertions.sort(key=lambda x: x[0], reverse=True)
    for pos, block in insertions:
        content = content[:pos] + "\n" + block + "\n" + content[pos:]

    return content

# ── EJECUTAR ────────────────────────────────────────────────────────────────
for post_id, queries in ARTICLES:
    print(f"\nProcesando post {post_id}...")

    # Obtener artículo
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}?_fields=id,title,content,slug",
        auth=(WP_USER, WP_PASS), timeout=15)
    if not r.ok:
        print(f"  ERROR al obtener post: {r.status_code}")
        continue
    post     = r.json()
    title    = post["title"]["rendered"]
    content  = post["content"]["rendered"]
    slug     = post.get("slug", f"post-{post_id}")

    print(f"  Título: {title[:55]}")

    # Verificar si ya tiene imágenes
    existing_imgs = re.findall(r'wp:image', content)
    if len(existing_imgs) >= 2:
        print(f"  Ya tiene {len(existing_imgs)} imágenes, omitiendo")
        continue

    img_blocks = []
    local_used = set()

    for i, query in enumerate(queries):
        img_url, photographer, img_id = pexels_search(
            query, exclude_ids=used_img_ids | local_used)

        if not img_url:
            img_url, photographer, img_id = pexels_search(
                "drone flying outdoor", exclude_ids=used_img_ids | local_used)

        if not img_url:
            print(f"  Sin imagen para query: {query[:40]}")
            continue

        if img_id:
            local_used.add(img_id)
            used_img_ids.add(img_id)

        alt_text = f"{title} — FlyDrones.es"
        print(f"  [{i+1}/3] {query[:35]} → foto de {photographer}")
        media_id, media_url = upload_to_wp(img_url, f"{slug}-img{i+1}", alt_text)

        if not media_id:
            print(f"  ERROR subiendo imagen {i+1}")
            continue

        block = make_img_block(media_id, media_url, alt_text)
        img_blocks.append(block)
        time.sleep(0.5)

    if not img_blocks:
        print(f"  No se subió ninguna imagen")
        continue

    new_content = insert_images_in_content(content, img_blocks)

    # Actualizar post
    upd = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
        auth=(WP_USER, WP_PASS),
        json={"content": new_content},
        timeout=30)
    if upd.ok:
        print(f"  OK — {len(img_blocks)} imágenes insertadas en el artículo")
    else:
        print(f"  ERROR actualizando post: {upd.status_code}")

    time.sleep(1)

print("\n=== COMPLETADO ===")
