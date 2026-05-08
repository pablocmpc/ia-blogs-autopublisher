# -*- coding: utf-8 -*-
"""
Instala los diseños premium en los 3 WordPress
Método: Code Snippets (desde WP.org) + template PHP escrito en wp-content
"""
import sys, json, base64, requests, os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, '..', 'wordpress-templates')
CONFIG_PATH  = os.path.join(SCRIPT_DIR, 'config.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

def read_template(filename):
    path = os.path.join(TEMPLATES_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

templates = {
    'ia_principiantes': read_template('plantilla-iaparaprincipiantes.php'),
    'prompts':          read_template('plantilla-superprompts.php'),
    'claude':           read_template('plantilla-guiaclaude.php'),
}

def auth_header(user, pwd):
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    return {'Authorization': f'Basic {token}'}

# ── Paso 1: Instalar Code Snippets si no está ─────────────────────────────────
def ensure_code_snippets(url, user, pwd):
    h = {**auth_header(user, pwd), 'Content-Type': 'application/json'}
    # Check if API is already available
    r = requests.get(f"{url}/wp-json/code-snippets/v1/snippets", headers=h, timeout=15)
    if r.status_code == 200:
        print("    [OK] Code Snippets ya activo")
        return True
    # Install + activate from WP.org
    r2 = requests.post(
        f"{url}/wp-json/wp/v2/plugins",
        headers=h,
        json={'slug': 'code-snippets', 'status': 'active'},
        timeout=60
    )
    if r2.status_code in (200, 201):
        print("    [OK] Code Snippets instalado y activado")
        return True
    # Maybe already installed but inactive
    if 'already' in r2.text.lower() or r2.status_code == 400:
        r3 = requests.put(
            f"{url}/wp-json/wp/v2/plugins/code-snippets%2Fcode-snippets",
            headers=h,
            json={'status': 'active'},
            timeout=30
        )
        if r3.status_code in (200, 201):
            print("    [OK] Code Snippets activado")
            return True
    print(f"    [ERROR] Code Snippets: {r2.status_code} — {r2.text[:200]}")
    return False

# ── Paso 2: Crear snippet que registra e inyecta la plantilla ─────────────────
def install_template_snippet(url, user, pwd, template_content):
    h = {**auth_header(user, pwd), 'Content-Type': 'application/json'}
    b64 = base64.b64encode(template_content.encode('utf-8')).decode()

    snippet_code = r"""<?php
add_filter('theme_page_templates', function($t){
    $t['ia-premium-home'] = 'Pagina Principal';
    return $t;
});
add_action('template_redirect', function(){
    if (!is_page()) return;
    if (get_post_meta(get_the_ID(), '_wp_page_template', true) !== 'ia-premium-home') return;
    $file = WP_CONTENT_DIR . '/ia-home-template.php';
    $b64 = '""" + b64 + r"""';
    file_put_contents($file, base64_decode($b64));
    if (file_exists($file)) {
        include $file;
        exit;
    }
});
"""

    # Delete existing snippet with same name first
    r_list = requests.get(f"{url}/wp-json/code-snippets/v1/snippets", headers=h, timeout=15)
    if r_list.status_code == 200:
        for s in r_list.json():
            if s.get('name') == 'IA Premium Home Template':
                sid = s['id']
                requests.delete(f"{url}/wp-json/code-snippets/v1/snippets/{sid}", headers=h, timeout=15)
                print(f"    [INFO] Snippet anterior eliminado (ID {sid})")
                break

    payload = {
        'name': 'IA Premium Home Template',
        'code': snippet_code,
        'active': True,
        'scope': 'global',
    }
    r = requests.post(f"{url}/wp-json/code-snippets/v1/snippets", headers=h, json=payload, timeout=30)
    if r.status_code in (200, 201):
        sid = r.json().get('id', '?')
        print(f"    [OK] Snippet creado y activo (ID {sid})")
        return True
    print(f"    [ERROR] Snippet: {r.status_code} — {r.text[:300]}")
    return False

# ── Paso 3: Crear/actualizar página Inicio ────────────────────────────────────
def create_inicio_page(url, user, pwd):
    h = {**auth_header(user, pwd), 'Content-Type': 'application/json'}

    r = requests.get(f"{url}/wp-json/wp/v2/pages?slug=inicio&per_page=1", headers=h, timeout=15)
    existing = r.json() if r.status_code == 200 else []

    # Create/update page first without template (snippet must be active first)
    payload_base = {
        'title': 'Inicio',
        'slug': 'inicio',
        'status': 'publish',
    }

    if existing:
        pid = existing[0]['id']
        r2 = requests.post(f"{url}/wp-json/wp/v2/pages/{pid}", headers=h, json=payload_base, timeout=30)
    else:
        r2 = requests.post(f"{url}/wp-json/wp/v2/pages", headers=h, json=payload_base, timeout=30)

    if r2.status_code in (200, 201):
        pid = r2.json()['id']
        # Now assign template (snippet is already active so ia-premium-home is registered)
        r3 = requests.post(
            f"{url}/wp-json/wp/v2/pages/{pid}",
            headers=h,
            json={'template': 'ia-premium-home'},
            timeout=30
        )
        tpl = r3.json().get('template', '?') if r3.status_code in (200, 201) else f'ERROR {r3.status_code}'
        print(f"    [OK] Pagina 'Inicio' lista (ID: {pid}) | template: {tpl}")
        return pid
    print(f"    [ERROR] Pagina: {r2.status_code} — {r2.text[:200]}")
    return None

# ── Paso 4: Establecer como portada ──────────────────────────────────────────
def set_homepage(url, user, pwd, page_id):
    h = {**auth_header(user, pwd), 'Content-Type': 'application/json'}
    r = requests.post(
        f"{url}/wp-json/wp/v2/settings",
        headers=h,
        json={'show_on_front': 'page', 'page_on_front': page_id},
        timeout=30
    )
    if r.status_code in (200, 201):
        print(f"    [OK] Configurada como portada del sitio")
        return True
    print(f"    [WARN] Portada: {r.status_code} — {r.text[:200]}")
    return False

def check_reachable(url):
    try:
        r = requests.get(f"{url}/wp-json/wp/v2/", timeout=10)
        return r.status_code < 500
    except Exception:
        return False

# ── MAIN ──────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  INSTALANDO DISENOS PREMIUM — 3 SITIOS")
print("="*60)

for site in config['sites']:
    name = site['name']
    url  = site['url']
    user = site['wp_user']
    pwd  = site['wp_password']
    key  = site['keywords_key']

    print(f"\n{'─'*50}")
    print(f"  {name}  ({url})")
    print(f"{'─'*50}")

    if not check_reachable(url):
        print(f"  [!] No se puede conectar a {url}")
        continue

    template_content = templates.get(key)
    if not template_content:
        print(f"  [ERROR] Plantilla no encontrada para clave '{key}'")
        continue

    print(f"  Paso 1: Verificando Code Snippets...")
    if not ensure_code_snippets(url, user, pwd):
        print(f"  [FALLO] No se pudo instalar Code Snippets.")
        continue

    print(f"  Paso 2: Instalando snippet de plantilla...")
    if not install_template_snippet(url, user, pwd, template_content):
        print(f"  [FALLO] No se pudo crear el snippet.")
        continue

    print(f"  Paso 3: Creando pagina de inicio...")
    page_id = create_inicio_page(url, user, pwd)
    if not page_id:
        print(f"  [FALLO] No se pudo crear la pagina de inicio.")
        continue

    print(f"  Paso 4: Estableciendo como portada...")
    set_homepage(url, user, pwd, page_id)

    print(f"\n  Abre {url} en el navegador para ver el diseno.")

print("\n" + "="*60)
print("  Proceso completado.")
print("="*60 + "\n")
