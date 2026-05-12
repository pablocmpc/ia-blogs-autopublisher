# -*- coding: utf-8 -*-
"""
SETUP PINTEREST — Configura Pinterest automáticamente.

Pasos:
  1. Ve a https://developers.pinterest.com/apps/
  2. Abre tu app → Authentication → Generate access token
  3. Marca estos permisos: boards:read, boards:write, pins:read, pins:write
  4. Copia el token y pégalo cuando este script te lo pida
  5. El script crea los tableros, los enlaza a cada web y actualiza config.json

Uso: python setup-pinterest.py
"""

import sys, json, os, time
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

BOARD_DEFINITIONS = [
    {
        "config_key":  "ia_principiantes",
        "name":        "IA para Principiantes",
        "description": "Guías, herramientas y tutoriales de inteligencia artificial explicados paso a paso para todos los niveles. Aprende IA gratis en español.",
        "privacy":     "PUBLIC",
    },
    {
        "config_key":  "prompts",
        "name":        "SuperPrompts — Prompts para ChatGPT y Claude",
        "description": "Los mejores prompts para ChatGPT, Claude y Gemini en español. Prompt engineering, plantillas y trucos para sacar más partido a la IA.",
        "privacy":     "PUBLIC",
    },
    {
        "config_key":  "claude",
        "name":        "Guía Claude — Tutoriales Claude Anthropic",
        "description": "Todo sobre Claude de Anthropic en español. Tutoriales, comparativas, API y casos de uso para profesionales y empresas.",
        "privacy":     "PUBLIC",
    },
]

SITE_URLS = {s['keywords_key']: s['url'] for s in cfg.get('sites', [])}


def api(method, endpoint, token, **kwargs):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    url = f'https://api.pinterest.com/v5{endpoint}'
    r = getattr(requests, method)(url, headers=headers, timeout=20, **kwargs)
    return r


def validate_token(token):
    r = api('get', '/user_account', token)
    if r.status_code == 200:
        data = r.json()
        return data.get('username', ''), data.get('account_type', '')
    return None, None


def get_existing_boards(token):
    boards = {}
    r = api('get', '/boards?page_size=100', token)
    if r.status_code == 200:
        for b in r.json().get('items', []):
            boards[b['name']] = b['id']
    return boards


def create_board(token, name, description, privacy='PUBLIC'):
    r = api('post', '/boards', token, json={
        'name':        name,
        'description': description,
        'privacy':     privacy,
    })
    if r.status_code == 201:
        return r.json()['id']
    print(f"   Error creando tablero '{name}': {r.status_code} {r.text[:200]}")
    return None


def update_board_cover(token, board_id, site_url):
    """Crea un pin de portada con la URL del blog para que aparezca en el tablero."""
    r = api('post', '/pins', token, json={
        'board_id':    board_id,
        'title':       'Visita el blog',
        'description': f'Todos los artículos en {site_url}',
        'link':        site_url,
        'media_source': {
            'source_type': 'image_url',
            'url': 'https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg'
        }
    })
    return r.status_code in (200, 201)


print("=" * 55)
print("  SETUP PINTEREST — Configuración automática")
print("=" * 55)
print()
print("Para obtener el token:")
print("  1. Ve a: https://developers.pinterest.com/apps/")
print("  2. Abre tu app → pestaña 'Authentication'")
print("  3. Clic en 'Generate access token'")
print("  4. Activa: boards:read, boards:write, pins:read, pins:write")
print("  5. Copia el token (empieza por pina_...)")
print()

token = input("Pega tu nuevo token de Pinterest aquí: ").strip()
if not token:
    print("Token vacío. Saliendo.")
    sys.exit(1)

print()
print("Validando token...", end=' ', flush=True)
username, acc_type = validate_token(token)
if not username:
    print("ERROR — Token incorrecto o permisos insuficientes.")
    print("Asegúrate de marcar todos los permisos al generar el token.")
    sys.exit(1)
print(f"OK  (@{username} · {acc_type})")

print()
print("Comprobando tableros existentes...", end=' ', flush=True)
existing = get_existing_boards(token)
print(f"{len(existing)} encontrados")

board_ids = {}

for bd in BOARD_DEFINITIONS:
    key   = bd['config_key']
    name  = bd['name']
    site  = SITE_URLS.get(key, '')

    print(f"\n  [{key}]")
    if name in existing:
        bid = existing[name]
        print(f"   Tablero ya existe — ID: {bid}")
    else:
        print(f"   Creando tablero '{name}'...", end=' ', flush=True)
        bid = create_board(token, name, bd['description'], bd['privacy'])
        if bid:
            print(f"OK  ID: {bid}")
            time.sleep(1)
        else:
            print("FALLO — continuando sin este tablero")
            continue

    board_ids[key] = bid

    if site:
        print(f"   Enlazando con {site}...", end=' ', flush=True)
        ok = update_board_cover(token, bid, site)
        print("OK" if ok else "sin portada (no crítico)")

# Actualizar config.json
print()
print("Actualizando config.json...", end=' ', flush=True)
cfg['pinterest']['access_token'] = token
cfg['pinterest']['boards'] = board_ids
with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)
print("OK")

print()
print("=" * 55)
print("  PINTEREST CONFIGURADO")
print()
for key, bid in board_ids.items():
    print(f"  {key}: {bid}")
print()
print("  Los proximos articulos se publicaran en Pinterest")
print("  automaticamente con foto y enlace al blog.")
print()
print("  IMPORTANTE: actualiza el secret CONFIG_JSON en GitHub")
print("  con el nuevo config.json (tiene el token actualizado).")
print("=" * 55)
