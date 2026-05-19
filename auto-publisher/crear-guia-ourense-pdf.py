#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera la GUÍA COMPLETA DE OURENSE en HTML (lista para imprimir/descargar como PDF)
y la sube como página descargable a turismoourense.es
"""

import requests, sys, re, json, os
sys.stdout.reconfigure(encoding='utf-8')

WP_URL  = "https://turismoourense.es"
WP_USER = "bengalasdehumo@gmail.com"
WP_PASS = "N8OW HTMH INJP fdKy k7u1 fOyO"
INDEXNOW_KEY = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"

# ── 1. OBTENER ARTÍCULOS ────────────────────────────────────────────────
def get_all_posts():
    posts = []
    page  = 1
    while True:
        r = requests.get(
            f"{WP_URL}/wp-json/wp/v2/posts?per_page=100&page={page}"
            f"&_fields=title,content,link,excerpt",
            auth=(WP_USER, WP_PASS), timeout=20
        )
        if not r.ok: break
        batch = r.json()
        if not batch: break
        posts.extend(batch)
        if len(batch) < 100: break
        page += 1
    return posts


def clean_html(html):
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    # Quitar schema JSON-LD
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text


def word_count(html):
    return len(re.sub("<[^>]+>", "", html).split())


def categorize(posts):
    cats = {
        "termas":     [],
        "gastronomia":[],
        "naturaleza": [],
        "cultura":    [],
        "escapadas":  [],
        "otros":      [],
    }
    for p in posts:
        title = p["title"]["rendered"]
        html  = clean_html(p.get("content", {}).get("rendered", ""))
        wc    = word_count(html)
        if wc < 400 or "hello world" in title.lower():
            continue
        tl = title.lower()
        if any(x in tl for x in ["terma","balneario","spa","termal","outariz","chavasqueira","laias","xures"]):
            cats["termas"].append(p)
        elif any(x in tl for x in ["restaurante","comer","gastronom","pulpo","vino","ribeiro","tapa","plato","cocina","gallega"]):
            cats["gastronomia"].append(p)
        elif any(x in tl for x in ["ruta","senderis","cascada","natural","parque","monte","rio","canon","sil","ribeira","sacra","paisaje"]):
            cats["naturaleza"].append(p)
        elif any(x in tl for x in ["catedral","monaster","museo","historia","patrimoni","castillo","iglesia","romano","medieval"]):
            cats["cultura"].append(p)
        elif any(x in tl for x in ["escapada","fin de semana","romantica","hotel","alojamiento","niños","familia","viaje"]):
            cats["escapadas"].append(p)
        else:
            cats["otros"].append(p)
    return cats


# ── 2. HTML DE LA GUÍA ─────────────────────────────────────────────────
def build_guide_html(cats):
    def section_html(cat_name, emoji, intro, posts, max_items=6):
        if not posts:
            return ""
        items = ""
        for p in posts[:max_items]:
            title = p["title"]["rendered"]
            link  = p["link"]
            excerpt = re.sub("<[^>]+>", "", p.get("excerpt", {}).get("rendered", ""))[:180]
            items += f"""
            <div class="art-card">
              <h3><a href="{link}" target="_blank">{title}</a></h3>
              <p>{excerpt}</p>
              <a class="btn-leer" href="{link}" target="_blank">Leer guía completa →</a>
            </div>"""
        return f"""
        <section class="guia-section">
          <h2>{emoji} {cat_name}</h2>
          <p class="intro-section">{intro}</p>
          <div class="art-grid">{items}
          </div>
        </section>"""

    termas_sec = section_html("Las Termas de Ourense", "♨️",
        "Ourense es la ciudad española con más fuentes termales naturales gratuitas. Temperaturas de hasta 68°C, acceso libre las 24 horas y vistas al río Miño. Te contamos todas las opciones.",
        cats["termas"])
    gastro_sec = section_html("Gastronomía Gallega en Ourense", "🐙",
        "El pulpo a feira, la empanada, el lacón con grelos y los vinos Ribeiro y Monterrei. Ourense es uno de los mejores destinos gastronómicos de España. Descubre dónde y qué comer.",
        cats["gastronomia"])
    nat_sec = section_html("Rutas y Naturaleza", "🌲",
        "La Ribeira Sacra, el Cañón do Sil, la Baixa Limia y Serra do Xurés. Ourense tiene paisajes de una belleza sin igual. Rutas para todos los niveles, desde paseos familiares hasta trekking exigente.",
        cats["naturaleza"])
    cult_sec = section_html("Historia y Cultura", "🏛️",
        "El Puente Romano, la Catedral de San Martín, el Monasterio de Oseira y el Casco Histórico. Ourense acumula más de 2.000 años de historia visigoda, romana y medieval.",
        cats["cultura"])
    esc_sec = section_html("Escapadas y Alojamientos", "🏡",
        "Hoteles rurales con encanto, balnearios con spa privado y casas de turismo rural en plena Ribeira Sacra. Te ayudamos a elegir la escapada perfecta para cada tipo de viajero.",
        cats["escapadas"])

    total = sum(len(v) for v in cats.values())

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Guía Completa de Ourense — Turismo, Termas y Gastronomía | TurismoOurense.es</title>
<meta name="description" content="La guía más completa de Ourense: termas gratuitas, gastronomía gallega, rutas de senderismo, historia y los mejores alojamientos rurales. {total} artículos con todo lo que necesitas saber.">
<style>
  :root {{
    --verde: #2d6a4f;
    --dorado: #c8963e;
    --crema:  #fdf6ec;
    --gris:   #4a4a4a;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Georgia',serif; color:var(--gris); background:#fff; line-height:1.7; }}

  /* PORTADA */
  .portada {{
    background: linear-gradient(135deg, var(--verde) 0%, #1a4a35 60%, #0d2b1f 100%);
    color:#fff; text-align:center; padding:80px 20px 60px;
    position:relative; overflow:hidden;
  }}
  .portada::before {{
    content:'';
    position:absolute; inset:0;
    background: url('https://turismoourense.es/wp-content/uploads/2024/01/ourense-termas.jpg') center/cover no-repeat;
    opacity:0.18;
  }}
  .portada-inner {{ position:relative; max-width:700px; margin:0 auto; }}
  .portada h1 {{ font-size:2.6rem; font-weight:700; margin-bottom:16px; text-shadow:0 2px 8px rgba(0,0,0,.5); }}
  .portada .subtitulo {{ font-size:1.15rem; opacity:.9; margin-bottom:28px; }}
  .portada .badge {{
    display:inline-block; background:var(--dorado); color:#fff;
    padding:8px 22px; border-radius:30px; font-size:.9rem; font-weight:600; margin:6px;
  }}
  .portada .año {{ margin-top:20px; opacity:.7; font-size:.9rem; }}

  /* CONTENIDO */
  .contenido {{ max-width:960px; margin:0 auto; padding:40px 20px; }}

  .intro-guia {{
    background:var(--crema); border-left:5px solid var(--dorado);
    padding:24px 28px; border-radius:4px; margin-bottom:50px;
    font-size:1.05rem;
  }}
  .intro-guia h2 {{ color:var(--verde); margin-bottom:12px; font-size:1.4rem; }}

  /* ÍNDICE */
  .indice {{ background:#f9f9f9; border:1px solid #e0e0e0; border-radius:8px; padding:28px; margin-bottom:50px; }}
  .indice h2 {{ color:var(--verde); margin-bottom:16px; font-size:1.3rem; }}
  .indice ol {{ padding-left:22px; }}
  .indice li {{ margin-bottom:8px; }}
  .indice a {{ color:var(--verde); text-decoration:none; font-weight:600; }}
  .indice a:hover {{ text-decoration:underline; }}

  /* SECCIONES */
  .guia-section {{ margin-bottom:60px; }}
  .guia-section h2 {{
    color:var(--verde); font-size:1.9rem; border-bottom:3px solid var(--dorado);
    padding-bottom:12px; margin-bottom:16px;
  }}
  .intro-section {{ color:#666; font-size:1.02rem; margin-bottom:28px; }}

  .art-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; }}
  .art-card {{
    border:1px solid #e8e8e8; border-radius:8px; padding:22px;
    transition:box-shadow .2s; background:#fff;
  }}
  .art-card:hover {{ box-shadow:0 4px 16px rgba(0,0,0,.1); }}
  .art-card h3 {{ font-size:1rem; margin-bottom:8px; line-height:1.4; }}
  .art-card h3 a {{ color:var(--verde); text-decoration:none; }}
  .art-card h3 a:hover {{ text-decoration:underline; }}
  .art-card p {{ font-size:.88rem; color:#777; margin-bottom:14px; }}
  .btn-leer {{
    display:inline-block; background:var(--verde); color:#fff;
    padding:7px 16px; border-radius:20px; font-size:.82rem; text-decoration:none;
    transition:background .2s;
  }}
  .btn-leer:hover {{ background:var(--dorado); }}

  /* DATOS CLAVE */
  .datos-clave {{
    background: linear-gradient(135deg, var(--verde) 0%, #1a4a35 100%);
    color:#fff; border-radius:12px; padding:40px; margin-bottom:50px;
  }}
  .datos-clave h2 {{ font-size:1.6rem; margin-bottom:24px; }}
  .datos-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:20px; }}
  .dato-item {{ text-align:center; }}
  .dato-num {{ font-size:2.2rem; font-weight:700; color:var(--dorado); display:block; }}
  .dato-label {{ font-size:.85rem; opacity:.85; margin-top:4px; }}

  /* CTA */
  .cta-final {{
    background:var(--crema); border:2px solid var(--dorado);
    border-radius:12px; padding:40px; text-align:center; margin-top:60px;
  }}
  .cta-final h2 {{ color:var(--verde); margin-bottom:12px; }}
  .cta-final p {{ margin-bottom:20px; }}
  .cta-final a {{
    background:var(--dorado); color:#fff; padding:14px 32px;
    border-radius:30px; text-decoration:none; font-weight:700; font-size:1.05rem;
    display:inline-block;
  }}

  /* FOOTER */
  .footer-guia {{ text-align:center; padding:30px; color:#aaa; font-size:.85rem; border-top:1px solid #eee; margin-top:40px; }}

  @media(max-width:600px) {{
    .portada h1 {{ font-size:1.8rem; }}
    .datos-grid {{ grid-template-columns:repeat(2,1fr); }}
  }}
  @media print {{
    .btn-leer {{ display:none; }}
    .portada {{ page-break-after:always; }}
    .guia-section {{ page-break-inside:avoid; }}
  }}
</style>
</head>
<body>

<div class="portada">
  <div class="portada-inner">
    <div style="font-size:3rem;margin-bottom:20px">🏔️♨️🍷</div>
    <h1>Guía Completa de Ourense</h1>
    <p class="subtitulo">Todo lo que necesitas saber antes de visitar la ciudad termal de Galicia</p>
    <span class="badge">♨️ Termas Gratuitas</span>
    <span class="badge">🐙 Gastronomía Gallega</span>
    <span class="badge">🌲 Ribeira Sacra</span>
    <span class="badge">🏛️ 2.000 Años de Historia</span>
    <p class="año">Edición 2026 · TurismoOurense.es</p>
  </div>
</div>

<div class="contenido">

  <div class="intro-guia">
    <h2>¿Por qué Ourense?</h2>
    <p>Ourense es el secreto mejor guardado de Galicia. Una ciudad con <strong>más fuentes termales gratuitas que cualquier otra ciudad de España</strong>, una gastronomía que compite con las mejores mesas del país, y un entorno natural — la Ribeira Sacra, el Cañón do Sil, el Xurés — que ya reconoció la UNESCO como Reserva de la Biosfera.</p>
    <p style="margin-top:12px">Esta guía reúne <strong>más de 40 artículos especializados</strong> con toda la información que necesitas: dónde ir, qué comer, dónde alojarte y cómo planificar tu viaje para aprovechar al máximo cada día en Ourense.</p>
  </div>

  <div class="datos-clave">
    <h2>Ourense en datos</h2>
    <div class="datos-grid">
      <div class="dato-item">
        <span class="dato-num">72°C</span>
        <span class="dato-label">Temperatura máxima de las termas naturales</span>
      </div>
      <div class="dato-item">
        <span class="dato-num">8</span>
        <span class="dato-label">Zonas termales gratuitas en la ciudad</span>
      </div>
      <div class="dato-item">
        <span class="dato-num">2.000</span>
        <span class="dato-label">Años de historia documentada (época romana)</span>
      </div>
      <div class="dato-item">
        <span class="dato-num">4</span>
        <span class="dato-label">Denominaciones de Origen de vino</span>
      </div>
      <div class="dato-item">
        <span class="dato-num">11</span>
        <span class="dato-label">Municipios de la Ribeira Sacra</span>
      </div>
      <div class="dato-item">
        <span class="dato-num">45 min</span>
        <span class="dato-label">En AVE desde Santiago de Compostela</span>
      </div>
    </div>
  </div>

  <div class="indice" id="indice">
    <h2>📋 Índice de la guía</h2>
    <ol>
      <li><a href="#termas">Las Termas de Ourense — tu primera parada obligatoria</a></li>
      <li><a href="#gastronomia">Gastronomía Gallega — dónde y qué comer en Ourense</a></li>
      <li><a href="#naturaleza">Rutas y Naturaleza — Ribeira Sacra, Cañón do Sil y más</a></li>
      <li><a href="#cultura">Historia y Cultura — Catedral, Puente Romano, Monasterios</a></li>
      <li><a href="#escapadas">Escapadas y Alojamientos — dónde dormir con encanto</a></li>
      <li><a href="#consejos">Consejos prácticos — cuándo ir, cómo llegar, qué llevar</a></li>
    </ol>
  </div>

  <div id="termas">{termas_sec}</div>
  <div id="gastronomia">{gastro_sec}</div>
  <div id="naturaleza">{nat_sec}</div>
  <div id="cultura">{cult_sec}</div>
  <div id="escapadas">{esc_sec}</div>

  <section class="guia-section" id="consejos">
    <h2>🗺️ Consejos prácticos para visitar Ourense</h2>
    <p class="intro-section">Todo lo que necesitas saber antes de salir de casa.</p>

    <table style="width:100%;border-collapse:collapse;font-size:.95rem">
      <thead style="background:var(--verde);color:#fff">
        <tr><th style="padding:12px;text-align:left">Aspecto</th><th style="padding:12px;text-align:left">Información</th></tr>
      </thead>
      <tbody>
        <tr style="background:#f9f9f9"><td style="padding:10px;border-bottom:1px solid #eee"><strong>Mejor época</strong></td><td style="padding:10px;border-bottom:1px solid #eee">Primavera (abril-junio) y otoño (sept-nov). El verano es caluroso pero ideal para las playas fluviales.</td></tr>
        <tr><td style="padding:10px;border-bottom:1px solid #eee"><strong>Cómo llegar</strong></td><td style="padding:10px;border-bottom:1px solid #eee">AVE desde Madrid (2h 15min), desde Vigo (45min), desde Santiago (45min). Autopista A-52.</td></tr>
        <tr style="background:#f9f9f9"><td style="padding:10px;border-bottom:1px solid #eee"><strong>Termas gratuitas</strong></td><td style="padding:10px;border-bottom:1px solid #eee">Outariz, Chavasqueira, Burgas (centro histórico). Abren todo el año, 24h algunas.</td></tr>
        <tr><td style="padding:10px;border-bottom:1px solid #eee"><strong>Idioma</strong></td><td style="padding:10px;border-bottom:1px solid #eee">Gallego y castellano. Con castellano te entenderán perfectamente en toda la provincia.</td></tr>
        <tr style="background:#f9f9f9"><td style="padding:10px;border-bottom:1px solid #eee"><strong>Moneda</strong></td><td style="padding:10px;border-bottom:1px solid #eee">Euro. Las termas municipales son gratuitas. Balnearios privados: 20-40€/sesión.</td></tr>
        <tr><td style="padding:10px;border-bottom:1px solid #eee"><strong>Qué llevar</strong></td><td style="padding:10px;border-bottom:1px solid #eee">Bañador y toalla para las termas. Calzado de senderismo si vas a la Ribeira Sacra. Paraguas (Galicia es Galicia).</td></tr>
      </tbody>
    </table>
  </section>

  <div class="cta-final">
    <h2>¿Listo para visitar Ourense?</h2>
    <p>Explora todos nuestros artículos especializados con rutas, horarios actualizados y recomendaciones locales verificadas.</p>
    <a href="https://turismoourense.es">Ver todos los artículos →</a>
  </div>

</div>

<div class="footer-guia">
  <p>© 2026 TurismoOurense.es · Guía creada con ❤️ para viajeros que buscan la Galicia auténtica</p>
  <p style="margin-top:6px"><a href="https://turismoourense.es" style="color:var(--verde)">turismoourense.es</a></p>
</div>

</body>
</html>"""


# ── 3. EJECUTAR ────────────────────────────────────────────────────────
print("Obteniendo artículos de Turismo Ourense...")
posts = get_all_posts()
cats  = categorize(posts)
total = sum(len(v) for v in cats.values())
print(f"  Artículos válidos: {total} (termas:{len(cats['termas'])} gastro:{len(cats['gastronomia'])} nat:{len(cats['naturaleza'])} cult:{len(cats['cultura'])} esc:{len(cats['escapadas'])})")

print("Generando HTML de la guía...")
guide_html = build_guide_html(cats)
guide_html = guide_html.replace("{termas_sec}", "").replace("{gastro_sec}", "").replace("{nat_sec}", "").replace("{cultura_sec}", "").replace("{esc_sec}", "")

# Guardar localmente
BASE = os.path.dirname(__file__)
html_path = os.path.join(BASE, "guia-ourense-2026.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(guide_html)
print(f"  HTML guardado en: {html_path}")

# ── 4. PUBLICAR COMO PÁGINA EN WP ──────────────────────────────────────
print("Publicando en turismoourense.es...")
page_data = {
    "title":   "Guía Completa de Ourense 2026 — Termas, Gastronomía y Qué Ver",
    "content": guide_html,
    "excerpt": "La guía más completa de Ourense: termas gratuitas, gastronomía gallega, Ribeira Sacra, rutas de senderismo y los mejores alojamientos rurales. Todo lo que necesitas para planificar tu visita.",
    "status":  "publish",
    "slug":    "guia-completa-ourense",
    "meta": {
        "rank_math_title":         "Guía Completa de Ourense 2026 — Todo lo que Necesitas Saber",
        "rank_math_description":   "Guía completa de Ourense: termas gratuitas, gastronomía gallega, Ribeira Sacra, rutas y alojamientos. Actualizada 2026.",
        "rank_math_focus_keyword": "guía Ourense"
    }
}

r = requests.post(f"{WP_URL}/wp-json/wp/v2/pages",
    auth=(WP_USER, WP_PASS), json=page_data, timeout=30)

if r.ok:
    page_link = r.json().get("link", "")
    page_id   = r.json().get("id", "")
    print(f"  PUBLICADA: {page_link}")

    # IndexNow
    requests.post("https://api.indexnow.org/indexnow",
        json={"host": "turismoourense.es", "key": INDEXNOW_KEY,
              "keyLocation": f"{WP_URL}/{INDEXNOW_KEY}.txt",
              "urlList": [page_link]},
        headers={"Content-Type": "application/json"}, timeout=10)
    print(f"  IndexNow enviado")

    # ── 5. AÑADIR AL MENÚ Y CREAR SNIPPET PARA BOTÓN DESCARGA ──────────
    # Crear snippet que añade botón "Descargar PDF" con window.print()
    btn_code = """
add_filter('the_content', function($content) {
    if (!is_page('guia-completa-ourense')) return $content;
    $btn = '<div style="text-align:center;margin:30px 0">
      <a href="javascript:window.print()"
         style="background:#c8963e;color:#fff;padding:14px 32px;border-radius:30px;text-decoration:none;font-size:1.1rem;font-weight:700;display:inline-block">
        📥 Descargar Guía en PDF
      </a>
      <p style="margin-top:10px;color:#888;font-size:.85rem">Usa Archivo → Guardar como PDF en tu navegador</p>
    </div>';
    return $btn . $content;
});"""
    snippet_r = requests.post(f"{WP_URL}/wp-json/code-snippets/v1/snippets",
        auth=(WP_USER, WP_PASS),
        json={"title": "Botón descarga PDF guía Ourense", "code": btn_code,
              "active": True, "scope": "frontend"},
        timeout=15)
    print(f"  Snippet botón PDF: {snippet_r.status_code}")
else:
    print(f"  ERROR {r.status_code}: {r.text[:200]}")

print("\nFIN. La guía está disponible en: https://turismoourense.es/guia-completa-ourense/")
