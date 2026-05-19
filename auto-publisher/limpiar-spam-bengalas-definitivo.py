#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpieza DEFINITIVA de bengalasdehumo.es.
Lógica inversa: ELIMINAR todo lo que NO tenga al menos una palabra
de los temas legítimos del sitio (bengalas, humo, fotografía, eventos).
"""
import requests, sys, time, re
sys.stdout.reconfigure(encoding='utf-8')

WP_URL  = "https://bengalasdehumo.es"
WP_USER = "bengalasdehumo@gmail.com"
WP_PASS = "RgvQ B927 3dIo tz4N o8r0 8jZL"

# Solo se mantienen posts cuyo título contenga AL MENOS UNA de estas palabras
KEEP_WORDS = [
    "bengala","humo","smoke","bomb","fotografí","fotograf","foto",
    "boda","quinceañ","quince","evento","color","sesion","sesión",
    "retrato","portrait","artes","creativ","arte","visual",
    "party","fiesta","cumpleaños","celebración","celebracion",
    "comprar","precio","donde","tienda","españa","calidad",
    "efectos","efecto","técnica","tecnica","tips","consejo",
    "seguridad","seguro","usar","cómo usar","como usar",
    "tendencia","moda","guía","guia","mejor",
    "playa","montaña","naturaleza","aire libre","exteriores",
    "instagram","redes","viral","tiktok",
    "bodas","parejas","novios","graduación","graduacion",
    "polvos","polvo","flash","luz","iluminación",
    "niños","familia","infantil","comunión",
    "halloween","navidad","año nuevo",
    "profesional","amateur","principiante",
    "colores","rosa","azul","verde","naranja","rojo","blanco","negro","amarillo",
    "duración","duracion","minutos","segundos",
    "interior","exterior","estudio","studio",
    "cámara","camara","objetivo","lente","dslr","mirrorless",
]

def html_decode(text):
    """Decodifica entidades HTML básicas."""
    replacements = {
        "&oacute;": "o", "&aacute;": "a", "&ntilde;": "n",
        "&iacute;": "i", "&eacute;": "e", "&uacute;": "u",
        "&Aacute;": "a", "&Eacute;": "e", "&Iacute;": "i",
        "&Oacute;": "o", "&Uacute;": "u", "&Ntilde;": "n",
        "&amp;": "&", "&quot;": '"',
    }
    for ent, char in replacements.items():
        text = text.replace(ent, char)
    return text

def should_keep(title):
    if not title or title.lower().strip() in ["hello world", "hello world!", ""]:
        return False
    decoded = html_decode(title.lower())
    return any(w in decoded for w in KEEP_WORDS)

# Obtener TODOS los posts
all_posts = []
page = 1
while True:
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts?per_page=100&page={page}&_fields=id,title",
        auth=(WP_USER, WP_PASS), timeout=20)
    if not r.ok or not r.json():
        break
    batch = r.json()
    all_posts.extend(batch)
    print(f"  Página {page}: {len(batch)} posts ({len(all_posts)} total)")
    if len(batch) < 100:
        break
    page += 1

print(f"\nTotal: {len(all_posts)} posts")

keep = [p for p in all_posts if should_keep(p["title"]["rendered"])]
delete = [p for p in all_posts if not should_keep(p["title"]["rendered"])]

print(f"\nA CONSERVAR: {len(keep)}")
print(f"A ELIMINAR:  {len(delete)}")

print("\nEjemplos a CONSERVAR (primeros 15):")
for p in keep[:15]:
    print(f"  KEEP: {html_decode(p['title']['rendered'])[:60]}")

print("\nEjemplos a ELIMINAR (primeros 15):")
for p in delete[:15]:
    print(f"  DEL:  {html_decode(p['title']['rendered'])[:60]}")

print(f"\nEliminando {len(delete)} posts de spam...")
deleted = 0
errors  = 0
for p in delete:
    r = requests.delete(
        f"{WP_URL}/wp-json/wp/v2/posts/{p['id']}?force=true",
        auth=(WP_USER, WP_PASS), timeout=15)
    if r.ok:
        deleted += 1
        if deleted % 10 == 0:
            print(f"  Eliminados: {deleted}/{len(delete)}...")
    else:
        errors += 1
    time.sleep(0.15)

print(f"\n=== RESULTADO ===")
print(f"  Eliminados: {deleted}")
print(f"  Errores:    {errors}")

r2 = requests.get(f"{WP_URL}/wp-json/wp/v2/posts?per_page=1",
    auth=(WP_USER, WP_PASS), timeout=10)
print(f"  Posts restantes: {r2.headers.get('X-WP-Total','?')}")
print(f"\nACCIONES URGENTES PARA EL USUARIO:")
print(f"  1. Cambiar contraseña de WordPress de bengalasdehumo.es AHORA")
print(f"  2. Revisar usuarios admin: WordPress > Usuarios > Todos los usuarios")
print(f"  3. Instalar Wordfence o Sucuri Security")
print(f"  4. Actualizar todos los plugins y temas")
print(f"  5. Revisar si otros sitios del mismo hosting fueron comprometidos")
