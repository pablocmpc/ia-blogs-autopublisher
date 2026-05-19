#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, sys, time
sys.stdout.reconfigure(encoding='utf-8')

WP_URL  = "https://bengalasdehumo.es"
WP_USER = "bengalasdehumo@gmail.com"
WP_PASS = "RgvQ B927 3dIo tz4N o8r0 8jZL"

EXTRA_SPAM = [
    "blackjack","loteria","lotería","dado","dados","probabilidad",
    "ganar dinero","fichas","maquinas","máquinas","tragaper","casino",
    "apuesta","bono","deposito","depósito","spins","ruleta","poker",
    "póker","bingo","slots","slot","jackpot","holdem","tiradas",
    "jugar gratis","juego gratis","juegos gratis","juegos de casino",
    "sitios de","sitio de","azar","maquina"
]
LEGIT = [
    "bengala","humo","smoke","fotografí","fotograf","boda","quinceañ",
    "evento","color","creativ","arte","seguridad","usar","comprar",
    "mejor","guia","guía","tendenci","tips","consejo","efecto","técnica",
    "sesion","sesión","fotos","foto","fotografo"
]

all_posts = []
page = 1
while True:
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts?per_page=100&page={page}&_fields=id,title",
        auth=(WP_USER, WP_PASS), timeout=20)
    if not r.ok or not r.json():
        break
    all_posts.extend(r.json())
    if len(r.json()) < 100:
        break
    page += 1

print(f"Posts restantes: {len(all_posts)}")

to_delete = []
for p in all_posts:
    title = p["title"]["rendered"]
    tl = title.lower()
    for esc in ["&oacute;","&aacute;","&ntilde;","&iacute;","&eacute;"]:
        tl = tl.replace(esc, "")
    if any(k in tl for k in LEGIT):
        continue
    if tl.strip() in ["", "estadisticas", "hello world"]:
        to_delete.append(p)
        continue
    if any(k in tl for k in EXTRA_SPAM):
        to_delete.append(p)

print(f"Spam adicional: {len(to_delete)}")
for p in to_delete[:5]:
    print(f"  Ejemplo: {p['title']['rendered'][:60]}")

deleted = 0
for p in to_delete:
    r = requests.delete(
        f"{WP_URL}/wp-json/wp/v2/posts/{p['id']}?force=true",
        auth=(WP_USER, WP_PASS), timeout=15)
    if r.ok:
        deleted += 1
    time.sleep(0.15)

print(f"Eliminados: {deleted}")
r2 = requests.get(f"{WP_URL}/wp-json/wp/v2/posts?per_page=1&_fields=id",
    auth=(WP_USER, WP_PASS), timeout=10)
total = r2.headers.get("X-WP-Total", "?")
print(f"Posts legítimos restantes: {total}")
