#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publica artículo de alta calidad sobre normativa drones España 2026
en flydrones.es — artículo evergreen que atrae backlinks.
"""

import requests, sys, json
sys.stdout.reconfigure(encoding='utf-8')

WP_URL  = "https://flydrones.es"
WP_USER = "bengalasdehumo@gmail.com"
WP_PASS = "8y4i vkwU dVXc nbnZ MzD6 MA7S"
INDEXNOW_KEY = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"

TITULO = "Normativa Drones España 2026: Todo lo que Necesitas Saber Antes de Volar"

CONTENIDO = """<!-- wp:paragraph -->
<p>Si tienes un dron en España, en 2026 la normativa ha cambiado de manera significativa. Los certificados STS-ES que muchos pilotos obtuvieron en años anteriores han caducado, el reglamento EASA se aplica con plena fuerza, y hay confusión generalizada sobre qué se puede hacer con cada categoría de drone. Esta guía lo explica todo en detalle.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>¿Qué ha cambiado en 2026?</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El 1 de enero de 2026 marcó el final de los certificados <strong>STS-ES-01 y STS-ES-02</strong>, los escenarios estándar específicos que la AESA había creado como puente de transición hacia el reglamento europeo. A partir de ahora, todos los vuelos en España se rigen exclusivamente por el Reglamento (UE) 2019/947 y sus enmiendas.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Lo que esto significa en la práctica:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Si tenías el STS-ES, necesitas revisar si tu actividad encaja en alguna categoría EASA (Abierta, Específica o Certificada)</li>
<li>Los vuelos anteriormente cubiertos por STS-ES pueden requerir ahora una Autorización Operacional específica</li>
<li>La documentación requerida ha cambiado</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Las tres categorías: Abierta, Específica y Certificada</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El sistema europeo divide todos los vuelos de drones en tres categorías según el riesgo que representan:</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Categoría Abierta — La más común</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>La mayoría de usuarios de drones recreativos y semiprofesionales operan en categoría Abierta. Las condiciones son:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Dron de menos de 25 kg</li>
<li>Vuelo a menos de 120 metros de altura</li>
<li>Siempre en línea visual directa (VLOS)</li>
<li>Lejos de concentraciones de personas (salvo A1)</li>
<li>No se transportan materiales peligrosos</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>Dentro de la categoría Abierta hay tres subcategorías:</p>
<!-- /wp:paragraph -->

<!-- wp:table -->
<figure class="wp-block-table"><table><thead><tr><th>Subcategoría</th><th>Drones permitidos</th><th>Habilitación necesaria</th><th>Distancia personas</th></tr></thead><tbody><tr><td><strong>A1</strong></td><td>Clase C0 (&lt;250g) o C1 (&lt;900g)</td><td>Examen online gratuito (A1/A3) para C1</td><td>C0: sin restricción · C1: no sobre concentraciones</td></tr><tr><td><strong>A2</strong></td><td>Clase C2 (&lt;4kg)</td><td>Examen A2 presencial + formación práctica</td><td>Mínimo 30 m (5 m en modo de baja velocidad)</td></tr><tr><td><strong>A3</strong></td><td>Clase C3/C4 (&lt;25kg)</td><td>Examen online gratuito (A1/A3)</td><td>150 m de zonas residenciales/recreativas/industriales</td></tr></tbody></table></figure>
<!-- /wp:table -->

<!-- wp:heading {"level":3} -->
<h3>Categoría Específica — Para usos profesionales complejos</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Si tu actividad no cabe en la categoría Abierta (vuelos sobre personas, BVLOS, operaciones complejas), necesitas entrar en la <strong>Categoría Específica</strong>. Aquí tienes dos opciones:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>Escenarios Estándar Europeos (STS)</strong>: STS-01 (vuelo en zona con baja densidad de población, VLOS) y STS-02 (vuelo sobre una zona urbana controlada, VLOS). Sustituyen a los extintos STS-ES españoles.</li>
<li><strong>Autorización Operacional (PDRA o específica)</strong>: para operaciones que no encajan en los STS. Requiere evaluación de riesgo SORA.</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>El examen de la AESA: A1/A3 y A2</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Para volar legalmente en España necesitas superar los exámenes de la AESA. Aquí el resumen:</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Examen A1/A3 (gratuito y online)</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Este examen lo necesitas si vas a volar un dron de clase C1, C3 o C4. Se hace en la web de la AESA, es gratuito, y tiene 40 preguntas de opción múltiple con un umbral de aprobado del 75% (necesitas acertar al menos 30).</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Temas del examen A1/A3:</strong></p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Seguridad aérea y regulación EASA</li>
<li>Espacio aéreo y procedimientos ATC básicos</li>
<li>Meteorología aplicada al vuelo de drones</li>
<li>Rendimiento del dron</li>
<li>Aspectos técnicos y eléctricos básicos</li>
<li>Privacidad y protección de datos</li>
<li>Seguros obligatorios</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>Tiempo disponible: 30 minutos. Puedes repetirlo sin límite en caso de no aprobarlo.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Examen A2 (presencial, con formación previa)</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El examen A2 te habilita para volar drones de clase C2 (&lt;4 kg) a 30 metros de personas (o 5 metros en modo de baja velocidad). Es más exigente:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Requiere <strong>formación práctica autoestudio</strong> documentada antes del examen</li>
<li>Se realiza en centros autorizados por la AESA</li>
<li>Temas adicionales: meteorología avanzada, rendimiento del dron en condiciones adversas, gestión de fallos</li>
<li>Coste aproximado: 40-80€ según el centro examinador</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>¿Qué dron comprar en 2026?</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>La elección del dron está directamente ligada a la normativa. Aquí la guía rápida:</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Sin carné (Clase C0, menos de 250g)</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El <strong>DJI Mini 4 Pro</strong> (249g exactos) es el rey de esta categoría. Volar sin carné, con cámara de nivel profesional, autonomía de 34 minutos y obstacle avoidance omnidireccional. Precio: alrededor de 600-700€.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Si el presupuesto es más ajustado, el <strong>DJI Mini 3</strong> (también 249g) ofrece muy buena relación calidad-precio alrededor de 400€.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Con habilitación A2 (Clase C2)</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El <strong>DJI Air 3S</strong> es el mejor dron de su categoría: sensor de 1 pulgada, cámara telefoto 3x, 46 minutos de autonomía, obstacle avoidance de nivel profesional. Si vas a trabajar con él, es la mejor inversión del mercado en 2026 (~1.100€).</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Nivel profesional (Clase C3/C4 o mayor)</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>El <strong>DJI Mavic 4 Pro</strong>, presentado a principios de 2025, es la referencia absoluta del mercado: triple cámara con sensor Hasselblad de 1 pulgada, zoom 10x sin pérdida de calidad, 51 minutos de vuelo. Para uso profesional serio (~2.000-2.500€).</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Zonas de vuelo y geofencing</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>No puedes volar en cualquier sitio. La AESA mantiene el sistema <strong>ENAIRE Drones</strong> y la app <strong>DroneSpain</strong> donde puedes consultar las zonas prohibidas, restringidas y condicionadas antes de salir a volar.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Zonas donde no puedes volar sin autorización expresa:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Dentro del CTR de los aeropuertos (radio variable según el aeropuerto)</li>
<li>Espacio aéreo D, R, P o TMA sin coordinación ATC</li>
<li>Zonas urbanas densamente pobladas (sin autorización específica)</li>
<li>Playas con bañistas (temporada)</li>
<li>Parques Nacionales (prohibición general)</li>
<li>Instalaciones penitenciarias, militares y nucleares (prohibición absoluta)</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Seguro obligatorio para drones</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Todos los drones de más de 250g (o cualquiera que se use con fines no exclusivamente recreativos) necesitan <strong>seguro de responsabilidad civil</strong> obligatorio. Las coberturas mínimas según el peso:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Hasta 500g: 750.000 DEG (~1,05M€)</li>
<li>De 500g a 2kg: 1.500.000 DEG (~2,1M€)</li>
<li>De 2kg a 25kg: 3.000.000 DEG (~4,2M€)</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>Hay aseguradoras especializadas como Allianz, Mapfre o startups como Coverdrone que ofrecen seguros específicos para drones desde 60-100€/año.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Preguntas frecuentes sobre la normativa 2026</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>¿Mi habilitación A1/A3 obtenida en 2021 sigue siendo válida?</strong><br>
Sí. Las habilitaciones A1/A3 y A2 no tienen fecha de caducidad. Lo que caducó el 1 de enero de 2026 son los certificados STS-ES-01 y STS-ES-02, no las habilitaciones básicas.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>¿Puedo volar un DJI Mini 4 Pro sobre la playa en verano?</strong><br>
Depende. Si hay bañistas, en la mayoría de municipios costeros hay ordenanzas locales que lo prohíben. Consulta siempre la normativa local antes de volar.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>¿Qué pasa si vuelo sin carné o en zona prohibida?</strong><br>
Las sanciones van desde 3.000€ hasta 225.000€ dependiendo de la infracción. La AESA está intensificando los controles y colabora con Guardia Civil y Policía Local.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>¿Necesito registrarme en la AESA?</strong><br>
Si tienes un dron de más de 250g o lo usas con fines no exclusivamente recreativos (aunque pese menos), sí: debes registrarte como operador UAS en la web de la AESA. Es gratuito y tarda menos de 15 minutos.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>¿Cómo sé si la zona donde voy a volar es legal?</strong><br>
Descarga la app <strong>DroneSpain</strong> o consulta el mapa geográfico de la AESA en drones.enaire.es. Siempre consulta antes de salir — las zonas pueden cambiar con NOTAMs temporales.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Recursos oficiales</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><a href="https://www.seguridadaerea.gob.es/es/ambitos/drones" target="_blank" rel="noopener noreferrer">AESA — Drones (web oficial)</a></li>
<li><a href="https://drones.enaire.es" target="_blank" rel="noopener noreferrer">ENAIRE Drones — Mapa de zonas de vuelo</a></li>
<li><a href="https://www.easa.europa.eu/en/domains/civil-drones" target="_blank" rel="noopener noreferrer">EASA — Civil Drones (reglamento europeo)</a></li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>Si tienes dudas sobre tu caso concreto, la AESA tiene un servicio de consultas en su web. También puedes preguntar en los foros especializados o en los grupos de pilotos de drones en España donde la comunidad suele responder con rapidez.</p>
<!-- /wp:paragraph -->

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Mi habilitación A1/A3 de 2021 sigue siendo válida en 2026?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sí. Las habilitaciones A1/A3 y A2 no tienen fecha de caducidad. Lo que caducó el 1 de enero de 2026 son los certificados STS-ES-01 y STS-ES-02."
      }
    },
    {
      "@type": "Question",
      "name": "¿Necesito carné para volar un DJI Mini 4 Pro?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El DJI Mini 4 Pro pesa 249g (categoría C0, menos de 250g). En subcategoría A1 no se requiere habilitación para C0. Sin embargo, si usas el dron con fines comerciales, debes registrarte como operador UAS en la AESA aunque el dron pese menos de 250g."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto cuesta el examen de drones de la AESA?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El examen A1/A3 es completamente gratuito y se hace online en la web de la AESA. El examen A2 cuesta entre 40 y 80 euros según el centro examinador autorizado."
      }
    }
  ]
}
</script>"""

META_DESC = "Guía completa de la normativa de drones en España 2026: qué ha cambiado con el STS-ES, las tres categorías EASA, cómo obtener el carné y los mejores drones para cada uso."

print("Publicando artículo normativa drones 2026 en FlyDrones...")

# Buscar o crear categoría "Normativa"
cat_r = requests.get(f"{WP_URL}/wp-json/wp/v2/categories?search=Normativa",
    auth=(WP_USER, WP_PASS), timeout=15)
cat_id = None
if cat_r.ok and cat_r.json():
    cat_id = cat_r.json()[0]["id"]
else:
    nc = requests.post(f"{WP_URL}/wp-json/wp/v2/categories",
        auth=(WP_USER, WP_PASS), json={"name": "Normativa"}, timeout=15)
    if nc.ok:
        cat_id = nc.json()["id"]

post_data = {
    "title":   TITULO,
    "content": CONTENIDO,
    "excerpt": META_DESC,
    "status":  "publish",
    "slug":    "normativa-drones-espana-2026",
    "categories": [cat_id] if cat_id else [],
    "meta": {
        "rank_math_title":         f"{TITULO} | FlyDrones.es",
        "rank_math_description":   META_DESC,
        "rank_math_focus_keyword": "normativa drones España 2026"
    }
}

r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts",
    auth=(WP_USER, WP_PASS), json=post_data, timeout=30)

if r.ok:
    data     = r.json()
    post_url = data.get("link", "")
    post_id  = data.get("id", "")
    print(f"  PUBLICADO: {post_url}")

    # IndexNow
    req = requests.post("https://api.indexnow.org/indexnow",
        json={"host": "flydrones.es", "key": INDEXNOW_KEY,
              "keyLocation": f"{WP_URL}/{INDEXNOW_KEY}.txt",
              "urlList": [post_url]},
        headers={"Content-Type": "application/json"}, timeout=10)
    print(f"  IndexNow: {req.status_code}")
else:
    print(f"  ERROR {r.status_code}: {r.text[:300]}")
