#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publica artículo de bengalas de humo para bodas en bengalasdehumo.es
Altamente enlazable por wedding planners y fotógrafos.
"""

import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

WP_URL  = "https://bengalasdehumo.es"
WP_USER = "bengalasdehumo@gmail.com"
WP_PASS = "RgvQ B927 3dIo tz4N o8r0 8jZL"
INDEXNOW_KEY = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"

TITULO = "Bengalas de Humo para Bodas: Guía Completa para Fotógrafos y Wedding Planners"

CONTENIDO = """<!-- wp:paragraph -->
<p>Las bengalas de humo de colores se han convertido en uno de los accesorios más creativos y fotogénicos de las bodas modernas. Un simple tiro de humo puede transformar una foto convencional en una imagen de portada de revista. Pero usarlas bien requiere saber elegir el producto, planificar el momento y trabajar con seguridad. Esta guía lo cubre todo.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>¿Por qué las bengalas de humo son perfectas para bodas?</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El boom de las bengalas de humo en fotografía de bodas no es casualidad. Hay razones técnicas y estéticas muy claras:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>Añaden dimensión y movimiento</strong>: el humo crea capas, texturas y dinamismo que ningún filtro puede replicar</li>
<li><strong>Definen el ambiente cromático</strong>: un humo rosa pastel o azul marino puede fijar el tono emocional de toda la sesión</li>
<li><strong>Generan imágenes únicas</strong>: el humo nunca se repite — cada disparo es diferente, lo que garantiza originalidad</li>
<li><strong>Funcionan en exteriores e interiores</strong>: en jardines, playas, fincas rurales o incluso naves industriales rehabilitadas</li>
<li><strong>Son muy compartibles en redes</strong>: las fotos con humo tienen tasas de engagement muy superiores en Instagram</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Mejores colores de humo para bodas</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>La elección del color depende del estilo de la boda, la paleta cromática y el entorno. Estas son las combinaciones que mejor funcionan:</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Blanco — El clásico atemporal</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El humo blanco es el más versátil y el más demandado en bodas. Crea un efecto etéreo y romántico, especialmente al contraluz o con luz dorada de hora mágica. Combina perfectamente con todos los estilos de vestido y se integra sin competir con el protagonismo de los novios.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Mejor para</strong>: bodas en exterior, entornos naturales, sesiones de tarde</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Rosa y Malva — Romanticismo puro</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El humo en tonos rosas y malvas complementa los colores pastel y funciona extraordinariamente bien en bodas con ambientación floral. Para sesiones en jardines de flores o bodas provenzales, el rosa es la elección instintiva de la mayoría de fotógrafos.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Mejor para</strong>: bodas garden party, estilos boho-chic, sesiones de mañana</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Azul profundo y Lavanda — Elegancia moderna</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Los tonos azulados y lavanda aportan un aire más sofisticado y editorial. Funcionan bien en bodas urbanas o industriales, y contrastan con eficacia sobre fondos claros o fachadas de piedra.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Mejor para</strong>: bodas urbanas, locales industriales, sesiones de tarde-noche</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Naranja y Amarillo — Impacto visual máximo</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Para parejas que quieren romper con lo convencional, los humos cálidos como el naranja y el amarillo oro crean imágenes con un impacto visual espectacular, especialmente sobre fondos oscuros o en entornos industriales.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Cómo planificar el momento del humo en una boda</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El timing lo es todo. Estos son los mejores momentos durante una boda para usar bengalas de humo:</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>La salida de la iglesia o el registro civil</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>La salida de los novios es el momento más icónico de la boda. Integrar humo de colores (1-2 bengalas en manos de invitados o en postes) mientras los novios avanzan hacia los invitados crea imágenes dinámicas e inmediatamente emotivas.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Consejo</strong>: usa dos colores complementarios (por ejemplo, blanco + rosa) a ambos lados del pasillo para crear un arco de humo natural.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>La sesión de pareja (post-boda o after)</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>La sesión de pareja es el momento de mayor libertad creativa para el fotógrafo. Con la prisa de la celebración terminada, novios más relajados y luz de tarde dorada, las bengalas de humo lucen en todo su esplendor.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Ideas para la sesión</strong>:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Novios caminando mientras el humo se disipa detrás — foto de espaldas icónica</li>
<li>Abrazo rodeado por humo de dos colores complementarios</li>
<li>La novia sosteniendo la bengala con el vestido fluyendo (viento leve ayuda mucho)</li>
<li>Contraluz con el sol poniente y el humo creando aureola alrededor de la pareja</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading {"level":3} -->
<h3>La primera copa y los aperitivos</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Si el venue lo permite, algunas bengalas durante la hora del cóctel crean un ambiente festivo y dan a los fotógrafos material para las fotos grupales y ambientales.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Seguridad: lo que todo fotógrafo y wedding planner debe saber</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El mayor error que cometen los que se inician con bengalas de humo es subestimar los aspectos de seguridad. Son productos seguros si se usan correctamente, pero requieren precaución:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>Consultar siempre con el venue</strong>: muchas fincas tienen suelos de hierba seca en verano o tejados de madera que no permiten bengalas</li>
<li><strong>Nunca en interiores cerrados</strong>: el humo se acumula rápidamente y puede activar alarmas o crear problemas respiratorios</li>
<li><strong>Distancia mínima de personas</strong>: la boquilla de salida del humo puede llegar a 200-300°C; nunca apuntes hacia personas ni mascotas</li>
<li><strong>Tener agua cerca</strong>: siempre ten un cubo con agua para extinguir la bengala usada de manera segura</li>
<li><strong>No usar con viento fuerte</strong>: con rachas de más de 20 km/h el humo se disipa demasiado rápido y puede ir hacia invitados</li>
<li><strong>Una persona responsable</strong>: designa siempre a alguien del equipo como responsable de las bengalas, nunca las dejes en manos de invitados sin supervisión</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Qué bengalas comprar para bodas</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>No todas las bengalas de humo son iguales. Para uso en bodas, estos son los criterios clave de selección:</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Duración: 60 o 90 segundos</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Para fotografía de bodas, las bengalas de 60 a 90 segundos son las más versátiles. Las de 30 segundos son demasiado cortas para muchas composiciones; las de 3-5 minutos pueden ser excesivas y más difíciles de manejar.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Densidad del humo</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las bengalas de alta densidad crean nubes más visibles y fotogénicas. Busca productos que especifiquen "alta densidad" o "dense smoke" — notarás la diferencia en las fotos.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Colores sólidos y saturados</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Los mejores resultados fotográficos se obtienen con bengalas que ofrecen colores puros y saturados, no tonos pastel desvaídos. Las marcas más reconocidas en el sector de la fotografía suelen especificar la saturación cromática del humo.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Tendencias 2026: bengalas de humo en bodas</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El mercado no para de evolucionar. Estas son las tendencias más fuertes que estamos viendo en 2026:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>Humo bicolor</strong>: bengalas que emiten dos colores simultáneos, muy valoradas para composiciones dramáticas</li>
<li><strong>Colores metálicos y dorados</strong>: el humo dorado-champán funciona perfectamente para bodas de estilo lujoso</li>
<li><strong>Bengalas de mano vs. poste</strong>: los weddings planners cada vez más integran las bengalas como elemento decorativo instalado en arcos florales o pérgolas</li>
<li><strong>Integración en vídeo</strong>: con la proliferación de vídeos de boda en Reels e Instagram, las bengalas se usan específicamente pensando en el videomaker, no solo en el fotógrafo</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Presupuesto orientativo para bengalas en bodas</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Una boda completa bien equipada con bengalas de humo debería incluir:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Salida de iglesia: 4-6 bengalas (2-3 de cada color)</li>
<li>Sesión de pareja: 6-10 bengalas (variedad de colores)</li>
<li>Buffer para repeticiones y fallos: 4-6 bengalas extra</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>Total orientativo: 14-22 bengalas. Con precios de 3-8€ por unidad según la calidad y el proveedor, el presupuesto total para bengalas de una boda completa oscila entre <strong>50 y 180€</strong> — un coste mínimo para el valor fotográfico que aportan.</p>
<!-- /wp:paragraph -->

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Son seguras las bengalas de humo para bodas?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sí, son seguras si se usan correctamente. Deben usarse en exteriores o espacios muy bien ventilados, manteniendo distancia de personas y mascotas, y siempre consultando previamente con el venue. Nunca usar en interiores cerrados."
      }
    },
    {
      "@type": "Question",
      "name": "¿Qué colores de bengalas de humo quedan mejor en fotos de boda?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El blanco es el más versátil y fotogénico. Para bodas románticas, los tonos rosa y malva funcionan muy bien. Para un efecto más dramático y editorial, el azul profundo o el lavanda. Los colores cálidos como naranja y amarillo crean el máximo impacto visual."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuántas bengalas de humo necesito para una boda?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Para una boda completa (salida + sesión de pareja) se recomienda entre 14 y 22 bengalas, incluyendo un buffer para repeticiones. El presupuesto total suele estar entre 50 y 180 euros según la calidad del producto."
      }
    }
  ]
}
</script>"""

META_DESC = "Guía completa de bengalas de humo para bodas: mejores colores, cómo planificar el momento perfecto, consejos de seguridad y cuántas bengalas necesitas para la sesión."

print("Publicando artículo bengalas para bodas en bengalasdehumo.es...")

# Categoría
cat_r = requests.get(f"{WP_URL}/wp-json/wp/v2/categories?search=Bodas",
    auth=(WP_USER, WP_PASS), timeout=15)
cat_id = None
if cat_r.ok and cat_r.json():
    cat_id = cat_r.json()[0]["id"]
else:
    nc = requests.post(f"{WP_URL}/wp-json/wp/v2/categories",
        auth=(WP_USER, WP_PASS), json={"name": "Bodas y Eventos"}, timeout=15)
    if nc.ok:
        cat_id = nc.json()["id"]

post_data = {
    "title":   TITULO,
    "content": CONTENIDO,
    "excerpt": META_DESC,
    "status":  "publish",
    "slug":    "bengalas-humo-bodas-guia-fotografos",
    "categories": [cat_id] if cat_id else [],
    "meta": {
        "rank_math_title":         f"{TITULO} | BengalasDeHumo.es",
        "rank_math_description":   META_DESC,
        "rank_math_focus_keyword": "bengalas de humo bodas"
    }
}

r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts",
    auth=(WP_USER, WP_PASS), json=post_data, timeout=30)

if r.ok:
    post_url = r.json().get("link", "")
    print(f"  PUBLICADO: {post_url}")
    req = requests.post("https://api.indexnow.org/indexnow",
        json={"host": "bengalasdehumo.es", "key": INDEXNOW_KEY,
              "keyLocation": f"{WP_URL}/{INDEXNOW_KEY}.txt",
              "urlList": [post_url]},
        headers={"Content-Type": "application/json"}, timeout=10)
    print(f"  IndexNow: {req.status_code}")
else:
    print(f"  ERROR {r.status_code}: {r.text[:300]}")
