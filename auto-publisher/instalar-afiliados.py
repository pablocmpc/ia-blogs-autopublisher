# -*- coding: utf-8 -*-
"""
Instala banners y links de afiliados en las 3 webs.
Los links apuntan a programas con pago real y aprobacion facil.
"""
import sys, json, os, requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

# ====================================================================
# PROGRAMA DE AFILIADOS — COMO REGISTRARSE Y COBRAR
# ====================================================================
# 1. HOSTINGER (alojamiento web) → hostinger.es/afiliados
#    - Comision: hasta 60% por venta (aprox 60-150 euros por cliente)
#    - Pago: PayPal o transferencia, umbral 100 euros
#    - Aprobacion: inmediata, enlace propio desde panel
#    - Tu link: https://www.hostinger.es/afiliados -> registrate con espiacm@gmail.com
#
# 2. JASPER AI (generador de contenido IA) → jasper.ai/affiliate
#    - Comision: 25% recurrente mensual (pagas 49$/mes → tu cobras 12$/mes por siempre)
#    - Pago: PayPal, umbral 25$
#    - Aprobacion: 1-2 dias, formulario en jasper.ai/affiliate
#
# 3. WRITESONIC → writesonic.com/affiliate
#    - Comision: 30% recurrente
#    - Pago: PayPal
#    - Aprobacion: inmediata
#
# 4. SEMRUSH → semrush.com/partner/affiliate/
#    - Comision: 200$ por primera venta + 10$ por trial
#    - Pago: PayPal o tarjeta
#    - Aprobacion: 1-3 dias
# ====================================================================

# SUSTITUYE estos links con TUS links reales de afiliado
# (los obtienes al registrarte en cada programa)
AFFILIATE_LINKS = {
    "hostinger": "https://www.hostinger.es/?REFERRALCODE=TUCODIGO",   # reemplazar
    "jasper":    "https://www.jasper.ai/?fpr=TUCODIGO",               # reemplazar
    "writesonic":"https://writesonic.com/?via=TUCODIGO",              # reemplazar
    "semrush":   "https://www.semrush.com/sem/?ref=TUCODIGO",         # reemplazar
}

# ---- BANNER HTML AFILIADOS (va en el footer de todas las webs) ----
AFFILIATES_SNIPPET = """
<style>
.af-bar{background:linear-gradient(135deg,#0f0f28,#1a0a3a);border-top:1px solid #3d2b80;padding:32px 20px;margin-top:40px;}
.af-bar h3{color:#b39ddb;text-align:center;margin:0 0 20px;font-size:1em;letter-spacing:.1em;text-transform:uppercase;}
.af-tools{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;max-width:900px;margin:0 auto;}
.af-tool{display:flex;flex-direction:column;align-items:center;background:#1d1840;border:1px solid #3d2b80;border-radius:10px;padding:14px 20px;text-decoration:none;transition:border-color .2s,transform .2s;min-width:140px;}
.af-tool:hover{border-color:#7c4dff;transform:translateY(-3px);}
.af-tool .af-name{color:#fff;font-weight:700;font-size:.95em;margin-bottom:4px;}
.af-tool .af-desc{color:#888;font-size:.78em;text-align:center;}
.af-tool .af-badge{background:#7c4dff;color:#fff;border-radius:50px;padding:2px 10px;font-size:.7em;font-weight:700;margin-top:6px;}
</style>
<div class="af-bar">
  <h3>Herramientas recomendadas</h3>
  <div class="af-tools">
    <a href="HOSTINGER_LINK" class="af-tool" target="_blank" rel="nofollow">
      <span class="af-name">Hostinger</span>
      <span class="af-desc">Mejor alojamiento web para empezar</span>
      <span class="af-badge">Desde 2,99€/mes</span>
    </a>
    <a href="JASPER_LINK" class="af-tool" target="_blank" rel="nofollow">
      <span class="af-name">Jasper AI</span>
      <span class="af-desc">IA para escribir contenido profesional</span>
      <span class="af-badge">Prueba gratis</span>
    </a>
    <a href="WRITESONIC_LINK" class="af-tool" target="_blank" rel="nofollow">
      <span class="af-name">Writesonic</span>
      <span class="af-desc">Genera articulos SEO con IA</span>
      <span class="af-badge">Plan gratuito</span>
    </a>
    <a href="SEMRUSH_LINK" class="af-tool" target="_blank" rel="nofollow">
      <span class="af-name">SEMrush</span>
      <span class="af-desc">La herramienta SEO que usan los pros</span>
      <span class="af-badge">Trial gratuito</span>
    </a>
    <a href="GUMROAD_LINK" class="af-tool" target="_blank">
      <span class="af-name">50 Prompts Premium</span>
      <span class="af-desc">PDF con los mejores prompts para IA</span>
      <span class="af-badge">9,99€ — Descarga ya</span>
    </a>
  </div>
</div>
""".replace("HOSTINGER_LINK",  AFFILIATE_LINKS["hostinger"]) \
   .replace("JASPER_LINK",     AFFILIATE_LINKS["jasper"]) \
   .replace("WRITESONIC_LINK", AFFILIATE_LINKS["writesonic"]) \
   .replace("SEMRUSH_LINK",    AFFILIATE_LINKS["semrush"]) \
   .replace("GUMROAD_LINK",    "https://superprompts.gumroad.com/l/50-prompts-premium")

def cs_post(site, data):
    url  = f"{site['url']}/wp-json/code-snippets/v1/snippets"
    auth = (site['wp_user'], site['wp_password'])
    r    = requests.post(url, json=data, auth=auth, timeout=20)
    return r

print()
print("=" * 60)
print("  INSTALANDO BANNERS DE AFILIADOS EN LAS 3 WEBS")
print("=" * 60)

for site in cfg['sites']:
    print(f"\n  [{site['name']}]")
    r = cs_post(site, {
        'name':     'Barra herramientas afiliados',
        'code':     AFFILIATES_SNIPPET,
        'scope':    'footer-content',
        'active':   True,
        'priority': 11,
    })
    if r.status_code in (200, 201):
        snip_id = r.json().get('id', '?')
        print(f"  ✓ Banner afiliados instalado (snippet #{snip_id})")
    else:
        print(f"  ! Error {r.status_code}: {r.text[:120]}")

print()
print("=" * 60)
print("  GUIA RAPIDA — COMO COBRAR POR AFILIADOS")
print()
print("  PASO 1: Registrate en cada programa")
print("  - Hostinger: hostinger.es/afiliados -> con espiacm@gmail.com")
print("  - Jasper:    jasper.ai/affiliate")
print("  - Writesonic: writesonic.com/affiliate")
print("  - SEMrush:   semrush.com/partner/affiliate/")
print()
print("  PASO 2: Copia tu link unico de cada programa")
print("  PASO 3: Reemplaza los links en AFFILIATE_LINKS en este script")
print("  PASO 4: Ejecuta este script de nuevo para actualizar las webs")
print()
print("  COMO COBRAS:")
print("  - Cuando alguien hace clic en tu link y compra")
print("  - El programa registra la venta a tu cuenta")
print("  - Cada 2 semanas/mes te pagan por PayPal o banco")
print("  - Hostinger: 60-150 euros por cliente")
print("  - Jasper/Writesonic: 10-15 euros/mes por cliente activo")
print("  - SEMrush: 200 euros por primera venta")
print("=" * 60)
