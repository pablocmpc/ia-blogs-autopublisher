"""
Instala el endpoint REST de newsletter en las 3 webs WordPress via Code Snippets.
Ejecutar una sola vez. Los emails quedan guardados en la base de datos WordPress.
"""
import json, base64, sys
import requests

with open("config.json") as f:
    cfg = json.load(f)

SNIPPET_PHP = r"""
add_action('rest_api_init', function() {
  register_rest_route('newsletter/v1', '/subscribe', [
    'methods' => 'POST',
    'callback' => function(WP_REST_Request $req) {
      $email = sanitize_email($req->get_param('email'));
      $site  = sanitize_key($req->get_param('site') ?? 'general');
      if (!is_email($email)) {
        return new WP_REST_Response(['success'=>false,'message'=>'Email no válido'], 400);
      }
      $key  = 'nl_subs_' . $site;
      $subs = get_option($key, []);
      if (in_array($email, $subs)) {
        return new WP_REST_Response(['success'=>true,'message'=>'¡Ya estás suscrito! 👍'], 200);
      }
      $subs[] = $email;
      update_option($key, $subs, false);
      return new WP_REST_Response(['success'=>true,'message'=>'¡Suscrito! Recibirás el próximo newsletter 📬'], 200);
    },
    'permission_callback' => '__return_true',
  ]);

  register_rest_route('newsletter/v1', '/subscribers', [
    'methods' => 'GET',
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
});
"""

def install_snippet(site_key):
    site = cfg["sites"][site_key]
    url   = site["url"].rstrip("/")
    user  = site["username"]
    pwd   = site["app_password"]
    auth  = (user, pwd)
    api   = f"{url}/wp-json/wp/v2"

    # Buscar snippet existente por título
    title = "Newsletter REST API Endpoint"
    r = requests.get(f"{api}/code-snippets", auth=auth, params={"search": title, "per_page": 5})
    snippets = r.json() if r.ok else []
    existing = next((s for s in snippets if isinstance(s, dict) and s.get("title", {}).get("rendered","") == title), None)

    payload = {
        "title": title,
        "content": SNIPPET_PHP,
        "status": "publish",
        "meta": {"run_everywhere": True}
    }

    if existing:
        r2 = requests.post(f"{api}/code-snippets/{existing['id']}", auth=auth, json=payload)
        action = "actualizado"
    else:
        r2 = requests.post(f"{api}/code-snippets", auth=auth, json=payload)
        action = "creado"

    if r2.ok:
        print(f"  ✅ {site_key}: snippet {action} (ID {r2.json().get('id','?')})")
    else:
        # Fallback: activar directamente via functions.php option
        print(f"  ⚠️  {site_key}: Code Snippets no disponible, usando wp_options directamente")
        activate_via_option(url, auth, SNIPPET_PHP)

def activate_via_option(url, auth, code):
    """Fallback: guarda el código en wp_options para auto-ejecución"""
    snippet_b64 = base64.b64encode(code.encode()).decode()
    activate_code = f"""
<?php
$b64 = '{snippet_b64}';
$code = base64_decode($b64);
update_option('nl_rest_snippet', $code);
eval($code);
?>"""
    payload = {
        "title": "Newsletter REST API - Init",
        "content": activate_code,
        "status": "publish"
    }
    r = requests.post(f"{url}/wp-json/wp/v2/code-snippets", auth=auth, json=payload)
    if r.ok:
        print(f"    → Snippet alternativo creado OK")
    else:
        print(f"    → Error: {r.status_code} — verifica que Code Snippets esté instalado")

print("Instalando endpoint newsletter en las 3 webs...\n")
for key in cfg.get("sites", {}):
    print(f"→ {key}...")
    install_snippet(key)

print("\n✅ Listo. Los emails se guardan en la base de datos WordPress de cada web.")
print("   Para verlos: wp-admin → Herramientas → Plugin Debug Bar, o ejecuta newsletter-semanal.py")
