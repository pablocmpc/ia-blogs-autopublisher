# -*- coding: utf-8 -*-
"""
Instala el endpoint REST de newsletter en las 3 webs WordPress via Code Snippets.
Los emails quedan guardados en la base de datos WordPress de cada web.
"""
import sys, json, base64, requests, os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

SNIPPET_PHP = """<?php
add_action('rest_api_init', function() {
  register_rest_route('newsletter/v1', '/subscribe', [
    'methods' => 'POST',
    'callback' => function(WP_REST_Request $req) {
      $email = sanitize_email($req->get_param('email'));
      $site  = sanitize_key($req->get_param('site') ?? 'general');
      if (!is_email($email)) {
        return new WP_REST_Response(['success'=>false,'message'=>'Email no valido'], 400);
      }
      $key  = 'nl_subs_' . $site;
      $subs = get_option($key, []);
      if (in_array($email, $subs)) {
        return new WP_REST_Response(['success'=>true,'message'=>'Ya estas suscrito!'], 200);
      }
      $subs[] = $email;
      update_option($key, $subs, false);
      return new WP_REST_Response(['success'=>true,'message'=>'Suscrito! Recibiras el proximo newsletter'], 200);
    },
    'permission_callback' => '__return_true',
  ]);

  register_rest_route('newsletter/v1', '/subscribers', [
    'methods'  => 'GET',
    'callback' => function() {
      $sites = ['iaparaprincipiantes','superprompts','guiaclaude'];
      $all = [];
      foreach ($sites as $s) {
        $all[$s] = get_option('nl_subs_' . $s, []);
      }
      return new WP_REST_Response($all, 200);
    },
    'permission_callback' => function() { return current_user_can('manage_options'); },
  ]);

  register_rest_route('newsletter/v1', '/count', [
    'methods'  => 'GET',
    'callback' => function() {
      $sites = ['iaparaprincipiantes','superprompts','guiaclaude'];
      $counts = []; $total = 0;
      foreach ($sites as $s) {
        $c = count(get_option('nl_subs_' . $s, []));
        $counts[$s] = $c;
        $total += $c;
      }
      $counts['total'] = $total;
      return new WP_REST_Response($counts, 200);
    },
    'permission_callback' => '__return_true',
  ]);
});
"""

SNIPPET_NAME = 'Newsletter REST API Endpoint'

def auth_header(user, pwd):
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    return {'Authorization': f'Basic {token}'}

def ensure_code_snippets(url, user, pwd):
    h = {**auth_header(user, pwd), 'Content-Type': 'application/json'}
    r = requests.get(f"{url}/wp-json/code-snippets/v1/snippets", headers=h, timeout=15)
    if r.status_code == 200:
        print("    [OK] Code Snippets activo")
        return True
    r2 = requests.post(
        f"{url}/wp-json/wp/v2/plugins",
        headers=h,
        json={'slug': 'code-snippets', 'status': 'active'},
        timeout=60
    )
    if r2.status_code in (200, 201):
        print("    [OK] Code Snippets instalado y activado")
        return True
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
    print(f"    [ERROR] Code Snippets: {r2.status_code}")
    return False

def install_newsletter_snippet(url, user, pwd):
    h = {**auth_header(user, pwd), 'Content-Type': 'application/json'}

    # Eliminar snippet anterior si existe
    r_list = requests.get(f"{url}/wp-json/code-snippets/v1/snippets", headers=h, timeout=15)
    if r_list.status_code == 200:
        for s in r_list.json():
            if s.get('name') == SNIPPET_NAME:
                sid = s['id']
                requests.delete(f"{url}/wp-json/code-snippets/v1/snippets/{sid}", headers=h, timeout=15)
                print(f"    [INFO] Snippet anterior eliminado (ID {sid})")
                break

    payload = {
        'name':   SNIPPET_NAME,
        'code':   SNIPPET_PHP,
        'active': True,
        'scope':  'global',
    }
    r = requests.post(f"{url}/wp-json/code-snippets/v1/snippets", headers=h, json=payload, timeout=30)
    if r.status_code in (200, 201):
        sid = r.json().get('id', '?')
        print(f"    [OK] Snippet creado y activo (ID {sid})")
        return True
    print(f"    [ERROR] Snippet: {r.status_code} -- {r.text[:300]}")
    return False

def verify_endpoint(url):
    """Verifica que el endpoint funciona enviando un email de prueba"""
    test_email = "test_install@verificacion.local"
    r = requests.post(
        f"{url}/wp-json/newsletter/v1/subscribe",
        json={"email": test_email, "site": "test"},
        timeout=15
    )
    if r.status_code == 200 and r.json().get("success"):
        print(f"    [OK] Endpoint verificado: {r.json().get('message')}")
        # Limpiar email de prueba via opcion
        return True
    else:
        print(f"    [WARN] Endpoint responde {r.status_code}: {r.text[:100]}")
        return False


print("Instalando endpoint newsletter en las 3 webs...\n")

sites = config.get("sites", [])
for site in sites:
    name = site.get("name", "?")
    url  = site.get("url", "").rstrip("/")
    user = site.get("wp_user", "")
    pwd  = site.get("wp_password", "")

    print(f">> {name} ({url})")

    if not url or not user or not pwd:
        print("    [SKIP] Credenciales incompletas")
        continue

    ok_cs = ensure_code_snippets(url, user, pwd)
    if not ok_cs:
        print("    [SKIP] Code Snippets no disponible\n")
        continue

    ok_sn = install_newsletter_snippet(url, user, pwd)
    if ok_sn:
        verify_endpoint(url)
    print()

print("Listo. Los emails se guardan en la base de datos WordPress.")
print("Puedes verlos en: /wp-json/newsletter/v1/subscribers (requiere login admin)")
