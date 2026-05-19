#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publica 4 artículos estratégicos en las webs que más los necesitan.
"""

import requests, sys
sys.stdout.reconfigure(encoding='utf-8')
INDEXNOW_KEY = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"

def pub(wp_url, wp_user, wp_pass, titulo, slug, meta_desc, contenido, keyword):
    host = wp_url.replace("https://", "").rstrip("/")
    post_data = {
        "title": titulo, "content": contenido, "excerpt": meta_desc,
        "status": "publish", "slug": slug,
        "meta": {"rank_math_title": titulo, "rank_math_description": meta_desc,
                 "rank_math_focus_keyword": keyword}
    }
    r = requests.post(f"{wp_url}/wp-json/wp/v2/posts",
        auth=(wp_user, wp_pass), json=post_data, timeout=30)
    if r.ok:
        url = r.json().get("link","")
        requests.post("https://api.indexnow.org/indexnow",
            json={"host": host, "key": INDEXNOW_KEY,
                  "keyLocation": f"{wp_url}/{INDEXNOW_KEY}.txt", "urlList": [url]},
            headers={"Content-Type": "application/json"}, timeout=10)
        print(f"  OK: {url}")
        return url
    else:
        print(f"  ERROR {r.status_code}: {r.text[:200]}")
        return None

# ════════════════════════════════════════════════════════════
# 1. TURISMO OURENSE — Termas gratuitas guía completa
# ════════════════════════════════════════════════════════════
print("\n[1] Turismo Ourense — Termas gratuitas")
pub(
    "https://turismoourense.es", "bengalasdehumo@gmail.com", "N8OW HTMH INJP fdKy k7u1 fOyO",
    "Termas Gratuitas de Ourense 2026: Horarios, Ubicaciones y Consejos para Disfrutarlas",
    "termas-gratuitas-ourense-horarios-2026",
    "Guía completa de las termas gratuitas de Ourense 2026: Outariz, Chavasqueira, Burgas, A Chavasqueira. Horarios actualizados, cómo llegar y qué esperar.",
    """<!-- wp:paragraph -->
<p>Ourense tiene más fuentes termales naturales gratuitas que cualquier otra ciudad de España. El agua mana a temperaturas de entre 38°C y 72°C directamente del subsuelo, y la ciudad ha construido instalaciones gratuitas para que cualquier persona pueda disfrutarlas. Esta guía te da toda la información que necesitas para aprovecharlas al máximo.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Las principales termas gratuitas de Ourense</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3>Termas de Outariz — La más famosa</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las termas de Outariz son las más conocidas y visitadas de Ourense. Situadas junto al río Miño, a unos 4 km del centro, ofrecen tres piscinas termales al aire libre con agua a diferentes temperaturas, desde los 40°C hasta los 65°C en el punto de la fuente. Hay zonas de sombra, vestuarios y servicios. El acceso es completamente gratuito.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Horario Outariz 2026</strong>: Abierto todos los días del año. En verano (junio-septiembre): 8:00 a 22:00. En invierno: 9:00 a 21:00.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Cómo llegar</strong>: Bus urbano línea 13 desde el centro o a pie en 45 minutos por el carril bici del Miño.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Termas de Chavasqueira — La más tranquila</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Chavasqueira es la favorita de los lugareños que quieren evitar la masificación de Outariz. Tiene una piscina principal de agua termal a 38-42°C y una zona de descanso junto al río. Mucho más íntima y familiar.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Horario Chavasqueira 2026</strong>: Abierto todo el año, 8:00-21:00 (ampliado a 22:00 en verano). Gratuito.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>As Burgas — Las termas históricas del centro</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>As Burgas son las fuentes termales más antiguas de Ourense, ubicadas en el corazón del casco histórico, junto a la Plaza Mayor. El agua mana a 67-68°C y los romanos ya la utilizaban hace 2.000 años. Aunque no son piscinas para bañarse (la temperatura es demasiado alta), son un símbolo histórico imprescindible y el agua se puede tocar en las fuentes ornamentales.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>A Chavasqueira Nova — La más moderna</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>La Chavasqueira Nova es la instalación más moderna de la ciudad, inaugurada con piscinas de diferentes temperaturas y duchas termales. Combina diseño contemporáneo con el agua termal natural. Gratuita como el resto.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Termas de Muíño da Veiga</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Situada aguas arriba del Miño, la terma de Muíño da Veiga es un espacio natural menos conocido con pozas naturales de agua termal directamente en la orilla del río. Un poco más salvaje y auténtica que las instalaciones municipales.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Tabla comparativa de termas gratuitas en Ourense</h2>
<!-- /wp:heading -->

<!-- wp:table -->
<figure class="wp-block-table"><table><thead><tr><th>Termas</th><th>Temperatura</th><th>Piscinas</th><th>Horario</th><th>Transporte</th></tr></thead><tbody><tr><td><strong>Outariz</strong></td><td>40-65°C</td><td>3 piscinas</td><td>8:00-22:00 (verano)</td><td>Bus línea 13</td></tr><tr><td><strong>Chavasqueira</strong></td><td>38-42°C</td><td>1 piscina grande</td><td>8:00-21:00</td><td>Bus + 5 min a pie</td></tr><tr><td><strong>Burgas</strong></td><td>67-68°C</td><td>No (fuentes)</td><td>Todo el día</td><td>Centro histórico</td></tr><tr><td><strong>Chavasqueira Nova</strong></td><td>36-45°C</td><td>2 piscinas</td><td>9:00-21:00</td><td>Misma parada Chavasqueira</td></tr><tr><td><strong>Muíño da Veiga</strong></td><td>35-45°C</td><td>Pozas naturales</td><td>Sin horario fijo</td><td>A pie / coche</td></tr></tbody></table></figure>
<!-- /wp:table -->

<!-- wp:heading -->
<h2>Consejos para disfrutar las termas</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>Lleva bañador y toalla</strong>: las instalaciones no alquilan.</li>
<li><strong>Evita festivos y agosto</strong>: las termas se llenan mucho en verano y festivos. Los días entre semana de mañana son los menos concurridos.</li>
<li><strong>Temperatura del agua</strong>: entra progresivamente, especialmente en las pozas más calientes. No es recomendable bañarse en agua a más de 42°C durante más de 15-20 minutos.</li>
<li><strong>Alternativa de pago</strong>: si buscas más servicios (masajes, sauna, spa completo), los balnearios privados como el Hotel Balneario de Laias o el Termas Laias ofrecen instalaciones premium desde 15-40€/entrada.</li>
<li><strong>Climatología</strong>: las termas son especialmente agradables en otoño e invierno, cuando contrastan con el frío exterior. En verano el agua puede parecer demasiado caliente.</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Más allá de las termas: qué ver en Ourense</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Si has venido a Ourense por las termas, no te vayas sin ver el Puente Romano, la Catedral de San Martín (una de las más impresionantes de Galicia), el Casco Histórico y el Parque de San Lázaro. Si tienes más de un día, una excursión a la Ribeira Sacra es imprescindible.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Consulta nuestra <a href="https://turismoourense.es/guia-completa-ourense/">Guía Completa de Ourense 2026</a> con todos los artículos especializados, horarios y rutas.</p>
<!-- /wp:paragraph -->

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"¿Son gratuitas todas las termas de Ourense?","acceptedAnswer":{"@type":"Answer","text":"Sí. Las principales instalaciones termales de Ourense (Outariz, Chavasqueira, Chavasqueira Nova, As Burgas) son completamente gratuitas y de acceso público. Solo los balnearios privados tienen coste."}},{"@type":"Question","name":"¿A qué hora abren las termas de Outariz?","acceptedAnswer":{"@type":"Answer","text":"En 2026, las termas de Outariz abren a las 8:00 de la mañana todos los días. El cierre es a las 22:00 en temporada de verano y a las 21:00 el resto del año."}},{"@type":"Question","name":"¿Cuál es la temperatura del agua en las termas de Ourense?","acceptedAnswer":{"@type":"Answer","text":"Varía según la instalación. En Outariz, las piscinas están entre 40°C y 65°C. En Chavasqueira, entre 38°C y 42°C. Las fuentes de As Burgas manan a 67-68°C y no son aptas para bañarse."}}]}
</script>""",
    "termas gratuitas Ourense horarios 2026"
)

# ════════════════════════════════════════════════════════════
# 2. BENGALAS — Quinceañeras
# ════════════════════════════════════════════════════════════
print("\n[2] Bengalas de Humo — Quinceañeras")
pub(
    "https://bengalasdehumo.es", "bengalasdehumo@gmail.com", "RgvQ B927 3dIo tz4N o8r0 8jZL",
    "Bengalas de Humo para Quinceañeras: Ideas, Colores y Consejos para Fotos Increíbles",
    "bengalas-humo-quincaneras-ideas-fotos",
    "Guía completa de bengalas de humo para quinceañeras: los mejores colores, ideas creativas y consejos de seguridad para fotos memorables.",
    """<!-- wp:paragraph -->
<p>La sesión de fotos de quinceañera es uno de los momentos más especiales en la vida de una joven. Las bengalas de humo de colores se han convertido en el accesorio más creativo y fotogénico de estas sesiones, transformando imágenes bonitas en portadas de revista. Esta guía te da todo lo que necesitas saber para incorporarlas de manera segura y lograr resultados espectaculares.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>¿Por qué usar bengalas de humo en fotos de quinceañeras?</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las quinceañeras tienen una estética muy específica: glamour, color, emoción y un toque de magia. Las bengalas de humo de colores encajan perfectamente en esta estética:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Crean imágenes únicas e irrepetibles — ninguna foto será igual a otra</li>
<li>El humo añade movimiento y dinamismo que no se puede replicar en postproducción</li>
<li>Los colores pueden coordinarse perfectamente con el vestido y la decoración</li>
<li>Las fotos con humo tienen un engagement altísimo en Instagram y TikTok</li>
<li>Son un accesorio muy asequible (3-8€ por bengala) con un resultado visual de nivel profesional</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Mejores colores de humo para quinceañeras según el color del vestido</h2>
<!-- /wp:heading -->

<!-- wp:table -->
<figure class="wp-block-table"><table><thead><tr><th>Color del vestido</th><th>Humo recomendado</th><th>Efecto</th></tr></thead><tbody><tr><td>Rosa / Fucsia</td><td>Blanco o rosa pálido</td><td>Romántico, etéreo, soñador</td></tr><tr><td>Azul / Turquesa</td><td>Azul oscuro o lila</td><td>Dramático, de editorial, impactante</td></tr><tr><td>Rojo / Vino</td><td>Naranja o negro</td><td>Poderoso, sexy, llamativo</td></tr><tr><td>Dorado / Champán</td><td>Amarillo oro o blanco</td><td>Lujoso, de gala, majestuoso</td></tr><tr><td>Verde / Esmeralda</td><td>Verde oscuro o amarillo</td><td>Natural, de fantasía, exótico</td></tr><tr><td>Blanco / Marfil</td><td>Cualquier color saturado</td><td>Contraste fuerte, protagonismo total del humo</td></tr></tbody></table></figure>
<!-- /wp:table -->

<!-- wp:heading -->
<h2>Las 8 mejores ideas de fotos con humo para quinceañeras</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3>1. La corona de humo</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Dos personas sostienen bengalas a ambos lados y ligeramente por encima de la quinceañera, creando un efecto de corona o aureola de humo alrededor de la cabeza y el vestido. Funciona especialmente bien con humo de dos colores complementarios.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>2. Caminando entre nubes</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>La quinceañera camina hacia la cámara mientras personas situadas detrás (fuera del encuadre) sostienen varias bengalas, creando una "nube" de humo que emana desde los pies del vestido. El efecto es espectacular con vestidos con cola larga.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>3. Bengala en mano — el retrato heroico</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>La quinceañera sostiene ella misma la bengala, con el brazo extendido hacia un lado. Esta pose requiere que la bengala apunte siempre hacia AFUERA del cuerpo. El resultado es una imagen de poder y seguridad muy apropiada para el momento.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>4. Efecto espejo con dos colores</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Dos bengalas de colores complementarios (por ejemplo, rosa y azul) a ambos lados crean un efecto de simetría y contraste que resulta muy llamativo en fotografía.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>5. La silueta</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Contraluz: la quinceañera de espaldas o de perfil con el sol poniente detrás. Las bengalas rodean su silueta. Con el ajuste correcto de exposición, el resultado es una silueta oscura perfecta sobre un fondo de humo y luz dorada.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>6. En escaleras o columnas</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las escaleras amplias son un set perfecto para quinceañeras. Con bengalas ubicadas en los escalones inferiores, el humo asciende de manera natural creando una atmósfera cinematográfica.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>7. Grupo de amigas con humo</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Las fotos grupales con todas las damas de honor sosteniendo bengalas de distintos colores crean imágenes festivas y llenas de vida que capturan perfectamente la energía de la celebración.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>8. El giro — foto de movimiento</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Pide a la quinceañera que gire sobre sí misma mientras sostiene una bengala. El humo sigue el movimiento del vestido, creando un efecto de espiral que en modo de alta velocidad produce imágenes de revista.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Consejos de seguridad — imprescindibles</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>Nunca en interiores</strong>: el humo se acumula en minutos en espacios cerrados, activa alarmas y puede causar problemas respiratorios.</li>
<li><strong>La boquilla llega a 200°C</strong>: nunca apuntes la bengala hacia personas o el vestido. Siempre con el extremo activo hacia afuera y hacia arriba.</li>
<li><strong>El vestido a distancia segura</strong>: mantén la bengala a al menos 30 cm del vestido en todo momento.</li>
<li><strong>Cubo de agua listo</strong>: ten siempre un cubo de agua para extinguir las bengalas usadas.</li>
<li><strong>Persona responsable</strong>: que sea siempre un adulto (no la quinceañera cuando está posando) quien sostenga las bengalas activas.</li>
<li><strong>Sin viento fuerte</strong>: con viento de más de 15-20 km/h el humo se dispersa demasiado y puede ir en dirección imprevista.</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>¿Cuántas bengalas necesito para una sesión de quinceañera?</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Para una sesión completa, la recomendación es:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>Sesión básica (1 hora, 2-3 looks): 10-15 bengalas</li>
<li>Sesión completa (2-3 horas, múltiples locaciones): 20-30 bengalas</li>
<li>Incluye siempre 20-30% de extra para repeticiones y fallos de encendido</li>
</ul>
<!-- /wp:list -->

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"¿Son seguras las bengalas de humo para una quinceañera?","acceptedAnswer":{"@type":"Answer","text":"Sí, son seguras si se usan en exteriores y con las precauciones correctas: nunca apuntar hacia el cuerpo o el vestido, mantener distancia mínima de 30 cm, tener agua cerca y que un adulto sea siempre el responsable de las bengalas activas."}},{"@type":"Question","name":"¿Cuántas bengalas de humo necesito para una sesión de fotos de quinceañera?","acceptedAnswer":{"@type":"Answer","text":"Para una sesión básica de 1 hora se recomiendan 10-15 bengalas. Para una sesión completa de 2-3 horas en varias locaciones, entre 20 y 30 bengalas. Siempre incluye un 20-30% de extra para repeticiones."}}]}
</script>""",
    "bengalas de humo quinceañeras fotos"
)

# ════════════════════════════════════════════════════════════
# 3. SUPERPROMPTS — Prompts para ChatGPT marketing
# ════════════════════════════════════════════════════════════
print("\n[3] SuperPrompts — Prompts marketing ChatGPT")
pub(
    "https://superprompts.es", "bengalasdehumo@gmail.com", "fh7t JV4H fVRt WS12 GwCU hwAp",
    "100 Mejores Prompts para ChatGPT en Marketing Digital 2026 (Copia y Pega)",
    "mejores-prompts-chatgpt-marketing-digital-2026",
    "Colección de 100 prompts para ChatGPT enfocados en marketing digital: copy, emails, redes sociales, SEO, anuncios. Listos para copiar y usar.",
    """<!-- wp:paragraph -->
<p>El marketing digital ha cambiado radicalmente con la llegada de ChatGPT y Claude. Los profesionales que saben escribir buenos prompts pueden crear en minutos lo que antes llevaba horas. Esta colección reúne los 100 prompts de marketing más útiles, organizados por área, que puedes copiar directamente y adaptar a tu negocio.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Cómo usar estos prompts eficazmente</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Antes de la colección, tres reglas que harán que cualquier prompt funcione mejor:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>Da contexto siempre</strong>: añade "Eres un experto en [tu sector]" o "Mi empresa es [descripción breve]" al inicio</li>
<li><strong>Pide formato específico</strong>: "Responde en lista numerada" o "Responde en tabla con columnas X, Y, Z"</li>
<li><strong>Itera</strong>: el primer resultado nunca es el definitivo. Pide ajustes: "Hazlo más formal", "Acórtalo a 280 caracteres", "Añade un llamado a la acción"</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Prompts para Copywriting y Textos de Venta</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Los siguientes prompts están diseñados para crear textos persuasivos que convierten. Sustituye los textos entre [corchetes] por la información de tu negocio.</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>1. Escribe un titular de venta para [producto/servicio] usando la fórmula "Cómo [beneficio específico] sin [objeción principal]" en menos de 10 palabras.

2. Crea 5 variaciones del headline para la landing page de [producto]. Target: [descripción del cliente ideal]. Tono: [profesional/amigable/urgente].

3. Escribe el texto para el botón CTA de una landing page de [servicio]. Dame 10 alternativas que transmitan urgencia y valor, sin usar "Comprar" ni "Suscribirse".

4. Redacta un email de venta para [producto] usando la estructura PAS (Problema, Agitación, Solución). Extensión: 250-300 palabras. Producto: [descripción].

5. Crea una propuesta de valor en una frase para [empresa/producto]. La frase debe responder: ¿Qué hacemos? ¿Para quién? ¿Cuál es el resultado principal?

6. Escribe 3 versiones de un texto de hero section para web de [tipo de negocio]: una versión orientada a beneficios, una a resultados y una emocional.

7. Genera las 5 objeciones principales que tiene un cliente antes de comprar [producto] y para cada una escribe una respuesta persuasiva de 2-3 frases.

8. Crea una comparativa de características en formato tabla entre [tu producto] y sus 3 principales competidores. Asegúrate de que tu producto destaque en los aspectos más valorados por el cliente.</code></pre>
<!-- /wp:code -->

<!-- wp:heading -->
<h2>Prompts para Redes Sociales</h2>
<!-- /wp:heading -->

<!-- wp:code -->
<pre class="wp-block-code"><code>9. Crea 10 ideas de posts de Instagram para [tipo de negocio]. Mix de: 3 educativos, 3 inspiracionales, 2 de producto, 2 behind-the-scenes.

10. Escribe el caption de Instagram para una foto de [descripción del producto/servicio]. Incluye hook en las primeras 2 líneas, cuerpo de 50-80 palabras y 3-5 hashtags relevantes.

11. Transforma este artículo de blog en 5 posts para LinkedIn de 150-200 palabras cada uno, cada uno con un ángulo diferente: [pega aquí el artículo].

12. Crea un carrusel de Instagram de 7 slides sobre [tema]. Para cada slide: texto del título (máx 6 palabras), texto del cuerpo (máx 30 palabras) y descripción de la imagen sugerida.

13. Escribe 15 ideas de Reels para [tipo de negocio] que puedan grabarse sin cara y sin hablar (solo texto en pantalla + música). Objetivo: educativo o entretenimiento.

14. Genera un calendario de contenidos de 30 días para [tipo de negocio] con una publicación diaria. Formato: tabla con columna de día, tipo de contenido y tema.

15. Escribe 5 versiones de bio para Instagram de [profesión/negocio], cada una con un énfasis diferente: autoridad, beneficio para el cliente, resultados, personalidad, propuesta única.

16. Crea una secuencia de 3 Stories de Instagram para presentar [nuevo producto/servicio]: historia 1 (problema), historia 2 (solución), historia 3 (llamada a la acción).</code></pre>
<!-- /wp:code -->

<!-- wp:heading -->
<h2>Prompts para Email Marketing</h2>
<!-- /wp:heading -->

<!-- wp:code -->
<pre class="wp-block-code"><code>17. Escribe una secuencia de bienvenida de 5 emails para nuevos suscriptores de [tipo de negocio]. Email 1: bienvenida + regalo prometido. Email 2: tu historia. Email 3: contenido de valor. Email 4: caso de éxito. Email 5: oferta suave.

18. Crea 10 asuntos de email que superen el 30% de tasa de apertura para [tipo de newsletter]. No uses clickbait engañoso. Incluye curiosidad, beneficio o urgencia genuina.

19. Redacta un email de reactivación para suscriptores inactivos (más de 3 meses sin abrir) de [tipo de negocio]. Tono honesto, no manipulador. Ofrece la opción de darse de baja.

20. Escribe un email de "abandono de carrito" para [tipo de tienda online]. Incluye: recordatorio del producto, beneficio principal, prueba social y un pequeño incentivo.

21. Crea una campaña de email de 3 mensajes para el lanzamiento de [producto]: email 1 (anticipación, 7 días antes), email 2 (apertura del carrito, día 1), email 3 (último aviso, cierre en 24h).

22. Genera 5 ideas de newsletter semanal para [tipo de negocio] que no sean simplemente "novedades del sector" sino que aporten valor accionable al lector.</code></pre>
<!-- /wp:code -->

<!-- wp:heading -->
<h2>Prompts para SEO y Contenido</h2>
<!-- /wp:heading -->

<!-- wp:code -->
<pre class="wp-block-code"><code>23. Actúa como experto SEO. Genera un cluster de contenido completo para la keyword principal "[keyword]". Incluye: keyword principal, 5 keywords secundarias, 10 artículos de soporte con sus títulos y 3 páginas pilar.

24. Escribe el meta title y meta description SEO optimizados para una página sobre [tema]. Meta title: máx 60 caracteres con keyword al inicio. Meta description: 150-155 caracteres con CTA.

25. Crea el esquema de un artículo de 2000 palabras optimizado para "[keyword]". Incluye: H1, introducción, 4-5 H2 con sus H3 correspondientes, conclusión y FAQ.

26. Genera 20 preguntas que la gente busca en Google sobre [tema]. Formato: lista numerada ordenada de más a menos volumen de búsqueda estimado.

27. Transforma este texto plano en un artículo SEO de 1500 palabras con estructura correcta de headings, párrafos de 2-3 frases y tono conversacional: [pega el texto].

28. Crea 5 títulos alternativos para el artículo "[título actual]" que sean más clickbait pero honestos. Incorpora números, años, o preguntas donde sea apropiado.</code></pre>
<!-- /wp:code -->

<!-- wp:heading -->
<h2>Prompts para Publicidad (Meta Ads y Google Ads)</h2>
<!-- /wp:heading -->

<!-- wp:code -->
<pre class="wp-block-code"><code>29. Crea 5 copys para anuncio de Facebook/Instagram de [producto], cada uno con un ángulo diferente: dolor, aspiración, prueba social, escasez/urgencia, curiosidad. Cada copy: máx 125 caracteres.

30. Escribe el copy completo para un anuncio de Meta en formato largo (para conversiones) de [producto/servicio]: hook (1 frase), cuerpo (3-5 párrafos), CTA. Target: [descripción del público].

31. Genera 10 variaciones de headline para Google Search Ads para la keyword "[keyword]". Máx 30 caracteres cada uno. Incluye la keyword en al menos 5 de ellos.

32. Crea 5 descripciones para Google Search Ads de [negocio/servicio]. Máx 90 caracteres cada una. Enfatiza beneficios diferenciales.

33. Escribe el guion de un anuncio en vídeo de 15 segundos para [producto]. Estructura: problema (3s), solución (7s), CTA (5s). Solo texto en pantalla + voz en off.</code></pre>
<!-- /wp:code -->

<!-- wp:heading -->
<h2>Prompts para Análisis de Competencia y Estrategia</h2>
<!-- /wp:heading -->

<!-- wp:code -->
<pre class="wp-block-code"><code>34. Actúa como consultor de marketing estratégico. Analiza los mensajes clave de marketing de estas 3 marcas competidoras y propón cómo podría diferenciarse [mi marca]: [lista de competidores con sus taglines o propuestas].

35. Crea un DAFO completo para [tipo de negocio] en el mercado español de 2026. Sé específico con las amenazas del entorno económico actual y las oportunidades digitales.

36. Genera 5 estrategias de contenido no convencionales para hacer crecer la audiencia de [tipo de negocio] de 0 a 10.000 seguidores en 6 meses.

37. ¿Qué canales de marketing debería priorizar [tipo de negocio con presupuesto de X€/mes] para maximizar el ROI? Ordénalos de mayor a menor potencial y explica brevemente por qué.</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>Esta colección se actualiza regularmente. Guarda esta página en favoritos para tener siempre los mejores prompts de marketing a mano.</p>
<!-- /wp:paragraph -->

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"¿Funcionan estos prompts en ChatGPT gratuito?","acceptedAnswer":{"@type":"Answer","text":"Sí, todos los prompts de esta lista funcionan con la versión gratuita de ChatGPT (GPT-3.5 y GPT-4o). Para resultados más específicos y de mayor calidad en tareas complejas, ChatGPT Plus o Claude Pro dan mejores resultados."}},{"@type":"Question","name":"¿Puedo usar estos prompts en Claude de Anthropic?","acceptedAnswer":{"@type":"Answer","text":"Sí, todos los prompts son compatibles con Claude de Anthropic, Gemini de Google y otros modelos de lenguaje. La sintaxis es universal — solo copia y pega sustituyendo los textos entre corchetes."}}]}
</script>""",
    "mejores prompts ChatGPT marketing digital"
)

# ════════════════════════════════════════════════════════════
# 4. GUÍA CLAUDE — Claude para negocios
# ════════════════════════════════════════════════════════════
print("\n[4] Guía Claude — Claude para negocios")
pub(
    "https://guiaclaude.es", "bengalasdehumo@gmail.com", "2RBK hzue 6a7C 6n1c hxU4 PXz3",
    "Claude para Negocios 2026: 10 Casos de Uso que Están Transformando Empresas Españolas",
    "claude-para-negocios-casos-uso-espana-2026",
    "Cómo usar Claude de Anthropic en tu empresa: 10 casos de uso reales con ejemplos prácticos para automatizar, mejorar la atención al cliente y escalar tu negocio.",
    """<!-- wp:paragraph -->
<p>Claude de Anthropic se ha posicionado en 2026 como la herramienta de IA preferida por muchas empresas que priorizan precisión, seguridad y capacidad de razonamiento complejo. A diferencia de ChatGPT, Claude destaca especialmente en el análisis de documentos largos, la redacción de textos con tono consistente y la gestión de tareas con instrucciones detalladas. Esta guía muestra 10 casos de uso concretos que empresas españolas ya están implementando.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>¿Por qué Claude y no ChatGPT para empresas?</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>No es una pregunta de "cuál es mejor" sino de "cuál encaja mejor con tu caso de uso". Dicho esto, Claude tiene ventajas claras en contextos empresariales:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>Ventana de contexto mayor</strong>: Claude 3.5 Sonnet puede procesar hasta 200.000 tokens (≈150.000 palabras). Útil para analizar contratos, informes o bases de conocimiento completas.</li>
<li><strong>Menor alucinación en hechos específicos</strong>: Claude tiende a decir "no sé" antes que inventar, lo que es crítico en contextos jurídicos, médicos o financieros.</li>
<li><strong>Mejor manejo del castellano</strong>: la calidad del español de Claude en tareas de redacción formal es superior en muchos benchmarks.</li>
<li><strong>API más predecible</strong>: los desarrolladores señalan consistencia mayor en las respuestas de Claude vs. GPT-4 para el mismo prompt.</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>10 casos de uso de Claude para empresas en España</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3>1. Análisis de contratos y documentos legales</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Sube un contrato de 50 páginas a Claude y pide: "Identifica los puntos de riesgo para mi empresa, las cláusulas inusuales y cualquier obligación que requiera atención especial." En minutos tienes un análisis que a un paralegal le llevaría horas. Recordatorio: Claude complementa (no sustituye) el trabajo de un abogado.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>2. Atención al cliente con IA contextualizada</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Usando la API de Claude con un system prompt que incluya la información de tu empresa, puedes crear un chatbot de atención al cliente que entiende el contexto de tu negocio, responde en el tono de tu marca y sabe cuándo escalar a un agente humano. Mejor que los chatbots de árbol de decisiones clásicos.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>3. Redacción de informes ejecutivos</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Proporciona a Claude los datos en bruto (resultados de ventas, métricas de marketing, datos de producción) y pide un informe ejecutivo estructurado con conclusiones y recomendaciones. El tiempo de preparación de informes mensuales se reduce de 4-8 horas a menos de 30 minutos.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>4. Traducción y adaptación de materiales</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Claude traduce y adapta materiales al español, catalán, gallego o euskera manteniendo el tono de la marca. Útil para empresas que operan en múltiples comunidades autónomas o en mercados internacionales hispanohablantes.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>5. Generación de contenido para marketing</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Con un prompt bien construido que incluya el tono de voz de la marca, el público objetivo y los mensajes clave, Claude puede generar: posts para LinkedIn, artículos de blog, newsletters, descripciones de producto o guiones de vídeo en el estilo de tu empresa.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>6. Análisis de feedback de clientes</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Si tienes 500 reseñas de Google, comentarios de redes sociales o respuestas de encuestas, Claude puede analizarlas y extraer: los 5 puntos de dolor principales, los atributos más valorados, los temas emergentes y las oportunidades de mejora. Análisis que normalmente requiere un equipo de investigación de mercado.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>7. Programación y depuración de código</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Para equipos de desarrollo, Claude es especialmente útil en: revisión de código (code review automatizado), documentación técnica, depuración de errores y escritura de tests unitarios. Claude destaca sobre otros modelos en tareas de programación en Python, JavaScript y SQL.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>8. Recursos Humanos y selección de personal</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Claude puede ayudar con: redacción de ofertas de empleo optimizadas, análisis de CVs según criterios definidos, creación de guías de entrevista por competencias y elaboración de planes de onboarding personalizados.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>9. Formación interna y creación de materiales</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Proporciona a Claude el contenido que necesitas formar (procedimientos, normativa, habilidades) y pide que cree: módulos de e-learning, quizzes de evaluación, FAQs interactivas o guías de referencia rápida para nuevos empleados.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>10. Investigación de mercado y análisis competitivo</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Proporcionando a Claude información sobre tu mercado, competidores y tendencias del sector, puede estructurar un análisis competitivo detallado, identificar nichos no cubiertos y proponer estrategias de diferenciación. Ideal como primer borrador antes de validar con fuentes primarias.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Cómo empezar con Claude en tu empresa</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>Plan gratuito</strong>: Claude.ai tiene una versión gratuita suficiente para empezar a explorar casos de uso individuales.</li>
<li><strong>Claude Pro (20€/mes)</strong>: acceso a Claude Opus y Sonnet, mayor límite de mensajes y carga de archivos. Para uso profesional individual.</li>
<li><strong>API de Anthropic</strong>: para integraciones en aplicaciones propias. Precio por tokens (aproximadamente 3€ por millón de tokens de entrada con Sonnet). Ideal para automatizaciones.</li>
<li><strong>Claude for Enterprise</strong>: para empresas con necesidades de privacidad, SSO y contratos específicos. Contactar directamente con Anthropic.</li>
</ul>
<!-- /wp:list -->

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"¿Cuánto cuesta usar Claude para una empresa?","acceptedAnswer":{"@type":"Answer","text":"Claude tiene plan gratuito en claude.ai. Claude Pro cuesta 20€/mes para uso individual con límites ampliados. La API de Anthropic para integración en aplicaciones propias se cobra por tokens: aproximadamente 3€/millón de tokens con Claude Sonnet. Para empresas hay opciones Enterprise."}},{"@type":"Question","name":"¿Es Claude mejor que ChatGPT para empresas españolas?","acceptedAnswer":{"@type":"Answer","text":"Depende del caso de uso. Claude destaca en análisis de documentos largos, redacción formal en castellano y precisión factual. ChatGPT es más versátil en creatividad y tiene más integraciones. Lo ideal es probar ambos con tu caso de uso específico."}}]}
</script>""",
    "Claude para negocios España"
)

print("\n=== FIN ===")
