#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMERGENCIA: Elimina los posts de spam (casino/poker/slots) de bengalasdehumo.es
Mantiene solo los posts legítimos sobre bengalas de humo y fotografía.
"""

import requests, sys, time
sys.stdout.reconfigure(encoding='utf-8')

WP_URL  = "https://bengalasdehumo.es"
WP_USER = "bengalasdehumo@gmail.com"
WP_PASS = "RgvQ B927 3dIo tz4N o8r0 8jZL"

# Palabras que identifican posts LEGÍTIMOS (bengalas, fotografía, bodas, etc.)
LEGIT_KEYWORDS = [
    "bengala", "humo", "smoke", "bomb", "fotografía", "fotógraf",
    "boda", "quinceañer", "evento", "color", "fotografo",
    "fotografia", "sesion", "sesión", "creativ", "arte",
    "seguridad", "usar", "comprar", "mejor", "guia", "guía",
    "tendenci", "tips", "consejo", "efecto", "técnica"
]

# Palabras que identifican SPAM de casino
SPAM_KEYWORDS = [
    "poker", "casino", "slot", "tragamoneda", "ruleta", "blackjack",
    "bingo", "tragaperras", "apuesta", "bono", "deposito", "jackpot",
    "maquina", "juego de azar", "fichas", "cartas", "holdem", "apuestas"
]

def is_spam(title):
    tl = title.lower()
    # Si contiene palabras legítimas, NO es spam
    if any(k in tl for k in LEGIT_KEYWORDS):
        return False
    # Si contiene palabras de casino, ES spam
    if any(k in tl for k in SPAM_KEYWORDS):
        return True
    return False

# Obtener TODOS los posts
print("Obteniendo posts de bengalasdehumo.es...")
all_posts = []
page = 1
while True:
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts?per_page=100&page={page}&_fields=id,title,status",
        auth=(WP_USER, WP_PASS), timeout=20)
    if not r.ok or not r.json():
        break
    batch = r.json()
    all_posts.extend(batch)
    print(f"  Página {page}: {len(batch)} posts ({len(all_posts)} total)")
    if len(batch) < 100:
        break
    page += 1

# Clasificar
spam_posts  = []
legit_posts = []
unclear     = []

for p in all_posts:
    title = p["title"]["rendered"]
    if title.lower() in ["hello world", "hello world!"]:
        spam_posts.append(p)
    elif is_spam(title):
        spam_posts.append(p)
    elif any(k in title.lower() for k in LEGIT_KEYWORDS):
        legit_posts.append(p)
    else:
        unclear.append(p)

print(f"\nClasificación:")
print(f"  SPAM a eliminar: {len(spam_posts)}")
print(f"  Legítimos:       {len(legit_posts)}")
print(f"  Sin clasificar:  {len(unclear)}")

print("\nMuestra de posts legítimos (primeros 10):")
for p in legit_posts[:10]:
    print(f"  OK: {p['title']['rendered'][:60]}")

print("\nMuestra de posts sin clasificar (primeros 10):")
for p in unclear[:10]:
    print(f"  ?: {p['title']['rendered'][:60]}")

# Confirmar antes de eliminar
print(f"\n{'='*60}")
print(f"Eliminando {len(spam_posts)} posts de SPAM...")
print(f"Se conservan {len(legit_posts) + len(unclear)} posts.")

deleted_ok  = 0
deleted_err = 0

for p in spam_posts:
    pid = p["id"]
    title = p["title"]["rendered"]
    # force=True para eliminar permanentemente (no papelera)
    r = requests.delete(
        f"{WP_URL}/wp-json/wp/v2/posts/{pid}?force=true",
        auth=(WP_USER, WP_PASS), timeout=15
    )
    if r.ok:
        deleted_ok += 1
        if deleted_ok % 20 == 0:
            print(f"  Eliminados: {deleted_ok}/{len(spam_posts)}...")
    else:
        deleted_err += 1
        print(f"  ERROR eliminando ID {pid}: {r.status_code}")
    time.sleep(0.2)  # pausa mínima para no saturar el servidor

print(f"\n{'='*60}")
print(f"COMPLETADO:")
print(f"  Eliminados OK:   {deleted_ok}")
print(f"  Errores:         {deleted_err}")
print(f"  Posts restantes: {len(legit_posts) + len(unclear)}")
print(f"\nRecuerda también:")
print(f"  1. Cambiar contraseña de WordPress de bengalasdehumo.es")
print(f"  2. Actualizar todos los plugins y el tema")
print(f"  3. Instalar un plugin de seguridad (Wordfence o Sucuri)")
print(f"  4. Verificar que no hay usuarios admin desconocidos")
