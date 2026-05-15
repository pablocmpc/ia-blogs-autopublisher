# -*- coding: utf-8 -*-
"""
SECUENCIA DE EMAIL AUTOMÁTICA POR NICHO
Envía una secuencia de bienvenida personalizada a nuevos suscriptores.

Funciona con el plugin Newsletter de WordPress (guarda suscriptores en WP DB).
También funciona con cualquier CSV de suscriptores.

Flujo por web:
  Email 1 (inmediato al suscribirse): Bienvenida + regalo gratis
  Email 2 (día 3): Artículo de valor + tip exclusivo
  Email 3 (día 7): Oferta del producto de pago
  Email semanal (lunes): Resumen de artículos de la semana

Uso:
  python secuencia-email.py welcome turismoourense.es  # Envía email 1 a nuevos suscriptores
  python secuencia-email.py day3 iaparaprincipiantes.es
  python secuencia-email.py day7 superprompts.es
  python secuencia-email.py weekly                      # Resumen semanal a todos
"""
import smtplib, json, os, sys, requests, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
config      = json.load(open(CONFIG_FILE, encoding='utf-8'))

SMTP_EMAIL    = config['smtp_email']
SMTP_PASSWORD = config['smtp_password']

# ─────────────────────────────────────────────
# TEMPLATES DE EMAIL POR NICHO
# ─────────────────────────────────────────────

SEQUENCES = {
    'turismoourense.es': {
        'from_name':   'Riker Carmon | Turismo Ourense',
        'site_name':   'Turismo Ourense',
        'site_url':    'https://turismoourense.es',
        'color':       '#2d6a4f',
        'product_url': 'https://pablocm.gumroad.com/l/xjqjov',
        'product_name':'Guía Premium de Ourense (PDF)',
        'product_price':'5€',
        'welcome': {
            'subject': '¡Bienvenido a Turismo Ourense! 🌿 Tu regalo está dentro',
            'preview': 'Los 5 secretos de Ourense que nadie te cuenta...',
            'body': """
<h2 style="color:#2d6a4f">¡Hola! Bienvenido a la familia de Turismo Ourense 🌿</h2>
<p>Soy <strong>Riker Carmon</strong>, guía local y escritor de viajes. Llevo más de 10 años explorando cada rincón de Ourense y hoy quiero compartir contigo mis mejores secretos.</p>
<h3>🎁 Tu regalo de bienvenida: Los 5 secretos de Ourense</h3>
<ol>
<li><strong>Las termas secretas</strong>: Las de As Burgas están en plena ciudad y son gratis</li>
<li><strong>El mirador que nadie conoce</strong>: Monte Aloia tiene las mejores vistas de la Ribeira Sacra</li>
<li><strong>La mejor hora para las termas</strong>: A las 8:00 AM hay 0 turistas y el ambiente es mágico</li>
<li><strong>El vino que debes probar</strong>: Pide siempre Treixadura blanco, no encontrarás nada igual</li>
<li><strong>El restaurante local</strong>: Evita los del centro histórico, busca los de la Rúa do Pasatiempo</li>
</ol>
<p>En los próximos días te enviaré más consejos exclusivos. ¡Bienvenido!</p>
<p style="margin-top:20px"><a href="https://turismoourense.es" style="background:#2d6a4f;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Ver artículos recientes →</a></p>
"""
        },
        'day3': {
            'subject': '📍 Las termas de Ourense: guía completa de precios y horarios',
            'preview': 'Todo lo que necesitas saber antes de ir...',
            'body': """
<h2 style="color:#2d6a4f">Las termas de Ourense: lo que tienes que saber</h2>
<p>Ourense tiene más de 70 manantiales termales naturales. Eso la convierte en la ciudad con más termas por habitante de España.</p>
<p>Pero hay un error que comete el 80% de los turistas: van a las que aparecen en Google sin saber que hay opciones mucho mejores.</p>
<h3>Las 3 mejores termas según mi experiencia:</h3>
<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%">
<tr style="background:#2d6a4f;color:white"><th>Termas</th><th>Precio</th><th>Mejor para</th></tr>
<tr><td>As Burgas (ciudad)</td><td>Gratis</td><td>Experiencia auténtica local</td></tr>
<tr><td>Outariz</td><td>6,95€</td><td>Piscinas al aire libre, vistas al río</td></tr>
<tr><td>Chavasqueira</td><td>3€</td><td>Ambiente tranquilo, menos turistas</td></tr>
</table>
<p style="margin-top:20px"><a href="https://turismoourense.es" style="background:#2d6a4f;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Leer la guía completa →</a></p>
"""
        },
        'day7': {
            'subject': '🗺️ La guía que todo viajero a Ourense necesita (oferta especial)',
            'preview': 'Solo para suscriptores: 5€ con todo lo que necesitas saber...',
            'body': """
<h2 style="color:#2d6a4f">He creado algo especial para ti</h2>
<p>Durante estos 7 días te he compartido algunos secretos de Ourense. Pero la verdad es que solo he podido contarte una pequeña parte.</p>
<p>Por eso he creado la <strong>Guía Premium de Ourense en PDF</strong>: 18 páginas con todo lo que sé después de 10 años viviendo y guiando en esta ciudad.</p>
<h3>¿Qué incluye la guía?</h3>
<ul>
<li>✅ Los 25 lugares imprescindibles con ubicaciones exactas</li>
<li>✅ Itinerario de 3 días optimizado</li>
<li>✅ Guía completa de termas (precios, horarios, secretos)</li>
<li>✅ Los 10 errores que cometen los turistas y cómo evitarlos</li>
<li>✅ Secretos de local que no encontrarás en TripAdvisor</li>
<li>✅ Guía gastronómica con restaurantes recomendados</li>
</ul>
<p><strong>Precio: solo 5€</strong></p>
<p><a href="https://pablocm.gumroad.com/l/xjqjov" style="background:#2d6a4f;color:white;padding:14px 28px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:16px">Conseguir la guía por 5€ →</a></p>
<p style="font-size:12px;color:#666">Descarga inmediata en PDF. Sin suscripciones ni cargos adicionales.</p>
"""
        }
    },
    'iaparaprincipiantes.es': {
        'from_name':   'Riker Carmon | IA para Principiantes',
        'site_name':   'IA para Principiantes',
        'site_url':    'https://iaparaprincipiantes.es',
        'color':       '#4f46e5',
        'product_url': 'https://claude.ai',
        'product_name':'Claude Pro',
        'product_price':'18€/mes',
        'welcome': {
            'subject': '¡Bienvenido! 🤖 5 herramientas de IA gratuitas que cambiarán tu trabajo',
            'preview': 'Las herramientas que yo uso cada día...',
            'body': """
<h2 style="color:#4f46e5">¡Bienvenido a IA para Principiantes! 🤖</h2>
<p>Soy <strong>Riker Carmon</strong> y llevo 10 años ayudando a personas como tú a incorporar la IA en su trabajo diario.</p>
<h3>🎁 Las 5 herramientas de IA gratuitas que uso cada día:</h3>
<ol>
<li><strong>Claude</strong> (claude.ai) — El mejor asistente de texto, gratis con límites generosos</li>
<li><strong>ChatGPT</strong> (chatgpt.com) — Imprescindible, versión gratis suficiente para empezar</li>
<li><strong>Canva IA</strong> — Diseño profesional sin saber diseño</li>
<li><strong>Perplexity</strong> — Búsquedas con IA más precisas que Google</li>
<li><strong>Notion IA</strong> — Organización y escritura asistida por IA</li>
</ol>
<p><a href="https://iaparaprincipiantes.es" style="background:#4f46e5;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Ver todos los tutoriales →</a></p>
"""
        },
        'day3': {
            'subject': '⚡ Cómo uso la IA para trabajar 3x más rápido (con ejemplos reales)',
            'preview': 'Los prompts exactos que yo uso...',
            'body': """
<h2 style="color:#4f46e5">Cómo multipliqué mi productividad x3 con IA</h2>
<p>Te cuento las 3 tareas en las que la IA me ahorra más tiempo cada semana:</p>
<h3>1. Redactar emails profesionales (5 min → 30 segundos)</h3>
<p>Prompt que uso: <em>"Escribe un email profesional para [situación]. Tono formal pero cercano. Máximo 3 párrafos."</em></p>
<h3>2. Resumir documentos largos (1 hora → 5 minutos)</h3>
<p>Pego el documento en Claude y escribo: <em>"Resume este documento en 10 puntos clave con los datos más importantes."</em></p>
<h3>3. Crear contenido para redes sociales (2 horas → 20 minutos)</h3>
<p>Prompt: <em>"Crea 10 posts para LinkedIn sobre [tema]. Tono experto pero accesible. Con emojis."</em></p>
<p><a href="https://iaparaprincipiantes.es" style="background:#4f46e5;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Ver más tutoriales →</a></p>
"""
        },
        'day7': {
            'subject': '🚀 El siguiente paso para dominar la IA (sin pagar mucho)',
            'preview': 'La inversión que más me ha rentado...',
            'body': """
<h2 style="color:#4f46e5">El siguiente paso en tu camino con la IA</h2>
<p>Llevas una semana con nosotros y ya conoces las bases. Es momento de dar el siguiente paso.</p>
<p>La única herramienta de pago que recomiendo a principiantes es <strong>Claude Pro</strong> por 18€/mes.</p>
<h3>¿Por qué Claude Pro y no ChatGPT Plus?</h3>
<ul>
<li>✅ Contexto de 200.000 tokens (analiza documentos enteros)</li>
<li>✅ Projects: organiza diferentes trabajos por cliente</li>
<li>✅ Sin límites diarios en horas punta</li>
<li>✅ Los modelos más avanzados sin restricciones</li>
</ul>
<p><a href="https://claude.ai/upgrade" style="background:#4f46e5;color:white;padding:14px 28px;border-radius:6px;text-decoration:none;font-weight:bold">Probar Claude Pro →</a></p>
<p style="font-size:12px;color:#666">Puedes cancelar cuando quieras. Sin compromiso.</p>
"""
        }
    },
    'superprompts.es': {
        'from_name':   'Riker Carmon | SuperPrompts',
        'site_name':   'SuperPrompts',
        'site_url':    'https://superprompts.es',
        'color':       '#059669',
        'welcome': {
            'subject': '🎯 Tus 10 primeros prompts profesionales (lista de regalo)',
            'preview': 'Los prompts que uso cada semana para ahorrar horas...',
            'body': """
<h2 style="color:#059669">¡Bienvenido a SuperPrompts! 🎯</h2>
<p>Soy <strong>Riker Carmon</strong>, especialista en prompt engineering. Aquí tienes tu regalo: los 10 prompts que yo uso cada semana.</p>
<h3>🎁 10 prompts que deberías guardar ahora mismo:</h3>
<ol>
<li><strong>Análisis de competencia:</strong> "Analiza los 5 principales competidores de [empresa] en España. Incluye fortalezas, debilidades y oportunidades que ellos no están aprovechando."</li>
<li><strong>Email de ventas:</strong> "Escribe un email de ventas para [producto] dirigido a [audiencia]. Usa el método PAS (Problem, Agitation, Solution). Máximo 200 palabras."</li>
<li><strong>Contenido LinkedIn:</strong> "Escribe un post de LinkedIn sobre [tema] que genere debate. Empieza con una afirmación controvertida. Termina con una pregunta."</li>
<li><strong>Resumen ejecutivo:</strong> "Resume este texto en un executive summary de máximo 5 bullet points con los datos clave: [pegar texto]"</li>
<li><strong>Brainstorming:</strong> "Dame 20 ideas de contenido sobre [nicho] que no se hayan publicado todavía o estén poco explotadas en español."</li>
</ol>
<p><a href="https://superprompts.es" style="background:#059669;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Ver todos los prompts →</a></p>
"""
        },
        'day3': {
            'subject': '⚡ El prompt que más me ha ahorrado tiempo este mes',
            'preview': 'Un prompt que vale su peso en oro...',
            'body': """
<h2 style="color:#059669">El prompt más poderoso que conozco</h2>
<p>Después de probar miles de prompts, hay uno que uso constantemente para cualquier tarea:</p>
<blockquote style="background:#f0fff4;padding:15px;border-left:4px solid #059669;font-style:italic">
"Actúa como [experto en X] con 20 años de experiencia. Explícame [tema] como si yo fuera [nivel de experiencia]. Dame los 5 pasos más importantes para [objetivo]. Incluye los errores más comunes y cómo evitarlos. Sé específico con ejemplos reales."
</blockquote>
<p>Este prompt funciona para cualquier cosa: marketing, código, diseño, ventas, finanzas...</p>
<p><a href="https://superprompts.es" style="background:#059669;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Ver más prompts →</a></p>
"""
        },
        'day7': {
            'subject': '🔥 Los prompts que usan los profesionales (nivel avanzado)',
            'preview': 'Techniques que marca la diferencia entre amateur y pro...',
            'body': """
<h2 style="color:#059669">Técnicas avanzadas de prompting que marcan la diferencia</h2>
<p>Después de una semana, estás listo para subir de nivel. Aquí van las técnicas que usan los profesionales:</p>
<ul>
<li><strong>Chain of Thought:</strong> "Piensa paso a paso antes de responder..."</li>
<li><strong>Few-shot prompting:</strong> Dar 2-3 ejemplos de lo que quieres antes de pedir</li>
<li><strong>Role + Context + Task:</strong> Define siempre quién es la IA, qué contexto tiene y qué tarea hace</li>
<li><strong>Output format:</strong> Especifica siempre el formato de salida (tabla, lista, párrafos, JSON...)</li>
</ul>
<p>Para dominar estas técnicas, lo mejor es practicar con <strong>Claude Pro</strong> que permite contextos muy largos perfectos para prompts complejos.</p>
<p><a href="https://claude.ai/upgrade" style="background:#059669;color:white;padding:14px 28px;border-radius:6px;text-decoration:none;font-weight:bold">Probar Claude Pro →</a></p>
"""
        }
    },
    'guiaclaude.es': {
        'from_name':   'Riker Carmon | Guía Claude',
        'site_name':   'Guía Claude',
        'site_url':    'https://guiaclaude.es',
        'color':       '#7c3aed',
        'welcome': {
            'subject': '🤖 Bienvenido: los 7 trucos de Claude que cambiarán tu forma de trabajar',
            'preview': 'El 90% de usuarios de Claude no conoce estos trucos...',
            'body': """
<h2 style="color:#7c3aed">¡Bienvenido a Guía Claude! 🤖</h2>
<p>Soy <strong>Riker Carmon</strong>, especialista en Claude de Anthropic. Aquí van los 7 trucos que el 90% de usuarios no conoce:</p>
<ol>
<li><strong>Projects:</strong> Organiza conversaciones por cliente o proyecto con contexto persistente</li>
<li><strong>Artifacts:</strong> Claude puede crear documentos, código y diseños en tiempo real</li>
<li><strong>200K contexto:</strong> Puedes pegar documentos enteros de 100 páginas y Claude los analiza</li>
<li><strong>Análisis de imágenes:</strong> Claude ve y analiza cualquier imagen que le adjuntes</li>
<li><strong>Coding avanzado:</strong> Claude es mejor que GPT-4 para debugging y arquitectura de código</li>
<li><strong>Subagentes:</strong> Claude puede usar herramientas externas y hacer tareas en tu nombre</li>
<li><strong>System prompts:</strong> Configura la personalidad y reglas de Claude para cada uso</li>
</ol>
<p><a href="https://guiaclaude.es" style="background:#7c3aed;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Ver todos los tutoriales →</a></p>
"""
        },
        'day3': {
            'subject': '🆚 Claude vs ChatGPT: la comparativa honesta que nadie hace',
            'preview': 'Después de usar ambos durante 2 años, esta es mi conclusión...',
            'body': """
<h2 style="color:#7c3aed">Claude vs ChatGPT: mi veredicto después de 2 años usando ambos</h2>
<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%">
<tr style="background:#7c3aed;color:white"><th>Tarea</th><th>Claude</th><th>ChatGPT</th></tr>
<tr><td>Redacción larga</td><td>✅ Mejor</td><td>Bueno</td></tr>
<tr><td>Análisis de documentos</td><td>✅ Mucho mejor</td><td>Limitado</td></tr>
<tr><td>Código / programación</td><td>✅ Mejor en debug</td><td>✅ Mejor en generación</td></tr>
<tr><td>Imágenes (generación)</td><td>❌ No genera</td><td>✅ DALL-E integrado</td></tr>
<tr><td>Contexto largo</td><td>✅ 200K tokens</td><td>128K tokens</td></tr>
<tr><td>Honestidad</td><td>✅ Menos alucinaciones</td><td>Más alucinaciones</td></tr>
</table>
<p><strong>Mi conclusión:</strong> Para texto, análisis y código → Claude. Para imágenes y plugins → ChatGPT.</p>
<p><a href="https://guiaclaude.es" style="background:#7c3aed;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Leer comparativa completa →</a></p>
"""
        },
        'day7': {
            'subject': '🚀 ¿Vale la pena Claude Pro? Mi opinión honesta',
            'preview': 'Te digo exactamente cuándo merece la pena y cuándo no...',
            'body': """
<h2 style="color:#7c3aed">¿Vale la pena Claude Pro por 18€/mes?</h2>
<p><strong>Para el 80% de los usuarios: SÍ, absolutamente.</strong></p>
<p>¿Por qué? Porque el plan gratuito tiene límites que te cortan justo cuando más lo necesitas. Con Pro:</p>
<ul>
<li>✅ Sin límites en horas punta</li>
<li>✅ Projects con memoria persistente por cliente</li>
<li>✅ Contexto de 200K tokens (el doble que ChatGPT Plus)</li>
<li>✅ Prioridad en nuevos modelos y funciones</li>
</ul>
<p><strong>¿Cuándo NO merece la pena?</strong> Si solo lo usas 2-3 veces por semana para tareas pequeñas. En ese caso el plan gratuito es suficiente.</p>
<p><a href="https://claude.ai/upgrade" style="background:#7c3aed;color:white;padding:14px 28px;border-radius:6px;text-decoration:none;font-weight:bold">Probar Claude Pro gratis 1 mes →</a></p>
"""
        }
    },
    'bengalasdehumo.es': {
        'from_name':   'Riker Carmon | Bengalas de Humo',
        'site_name':   'Bengalas de Humo',
        'site_url':    'https://bengalasdehumo.es',
        'color':       '#e07b00',
        'welcome': {
            'subject': '💨 Bienvenido: los 5 secretos de la fotografía con humo que nadie enseña',
            'preview': 'Lo que aprendí después de 150 bodas con bengalas...',
            'body': """
<h2 style="color:#e07b00">¡Bienvenido a Bengalas de Humo! 💨</h2>
<p>Soy <strong>Riker Carmon</strong>, fotógrafo con 8 años usando bengalas de humo en bodas, sesiones y eventos. Aquí van mis 5 secretos:</p>
<ol>
<li><strong>La hora dorada + humo = magia:</strong> Las mejores fotos son 30 minutos antes del atardecer, la luz suave difumina el humo perfectamente</li>
<li><strong>Viento a favor:</strong> Siempre coloca al modelo con el viento de frente, el humo irá hacia atrás y no tapará la cara</li>
<li><strong>Color complementario:</strong> Para pelo rubio usa azul o verde, para moreno usa naranja o rojo</li>
<li><strong>Distancia mínima:</strong> Nunca menos de 1 metro entre el modelo y la bengala activa</li>
<li><strong>Movimiento circular:</strong> Pide al modelo que gire lentamente mientras la bengala está activa, el efecto es espectacular</li>
</ol>
<p><a href="https://bengalasdehumo.es" style="background:#e07b00;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Ver todos los tutoriales →</a></p>
"""
        },
        'day3': {
            'subject': '🎨 Las mejores bengalas de humo del mercado (probadas por mí)',
            'preview': 'Después de probar más de 20 marcas, estas son mis favoritas...',
            'body': """
<h2 style="color:#e07b00">Las bengalas que uso y recomiendo</h2>
<p>He probado más de 20 marcas diferentes. Estas son las que realmente funcionan:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%">
<tr style="background:#e07b00;color:white"><th>Marca</th><th>Duración</th><th>Ideal para</th><th>Precio</th></tr>
<tr><td>Enola Gaye WP40</td><td>90 seg</td><td>Bodas, exterior</td><td>~4€/u</td></tr>
<tr><td>Smoking Bombs</td><td>60 seg</td><td>Sesiones, eventos</td><td>~2€/u</td></tr>
<tr><td>Distress Signal</td><td>120 seg</td><td>Vídeo, mucho humo</td><td>~6€/u</td></tr>
</table>
<p><a href="https://www.amazon.es/s?k=bengalas+humo+colores" target="_blank" rel="noopener" style="background:#e07b00;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Ver bengalas en Amazon →</a></p>
"""
        },
        'day7': {
            'subject': '📸 Cómo cobrar más por tus fotos con bengalas de humo',
            'preview': 'La técnica que me permitió subir mis precios un 40%...',
            'body': """
<h2 style="color:#e07b00">Cómo las bengalas de humo cambiaron mi negocio de fotografía</h2>
<p>Cuando empecé a ofrecer sesiones con bengalas de humo, algo cambió: mis clientes empezaron a pagar un 40% más sin rechistar.</p>
<p>¿Por qué? Porque las fotos con humo generan algo que las fotos normales no pueden: <strong>emoción visual inmediata</strong>.</p>
<h3>Cómo monetizarlo:</h3>
<ul>
<li>Crea un «Pack Premium» de tu sesión que incluya 30 min con bengalas de humo</li>
<li>Sube el precio 150-200€ sobre tu tarifa normal</li>
<li>Muestra en Instagram los resultados → los clientes te piden el pack solos</li>
</ul>
<p>El coste de las bengalas es de 15-20€ por sesión. El beneficio adicional es de 150-200€.</p>
<p><a href="https://bengalasdehumo.es" style="background:#e07b00;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">Ver más técnicas →</a></p>
"""
        }
    }
}


def get_html_email(from_name, site_name, site_url, color, subject, body_html):
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{subject}</title></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif">
<div style="max-width:600px;margin:20px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08)">
  <div style="background:{color};padding:24px 32px">
    <div style="color:white;font-size:20px;font-weight:700">{site_name}</div>
    <div style="color:rgba(255,255,255,.8);font-size:13px;margin-top:4px">{site_url}</div>
  </div>
  <div style="padding:32px;color:#1f2937;font-size:15px;line-height:1.7">
    {body_html}
    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
    <p style="font-size:13px;color:#6b7280">
    Un saludo,<br><strong>{from_name}</strong><br>
    <a href="{site_url}" style="color:{color}">{site_url}</a>
    </p>
  </div>
  <div style="background:#f9fafb;padding:16px 32px;text-align:center;border-top:1px solid #e5e7eb">
    <p style="font-size:11px;color:#9ca3af;margin:0">
    Recibiste este email porque te suscribiste en {site_url}.<br>
    <a href="{{unsubscribe_url}}" style="color:#9ca3af">Darse de baja</a>
    </p>
  </div>
</div>
</body></html>"""


def send_email(to_email, subject, html_body, from_name, from_email=SMTP_EMAIL):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'{from_name} <{from_email}>'
    msg['To']      = to_email
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f'  Error enviando a {to_email}: {e}')
        return False


def get_subscribers(site_url, wp_user, wp_pass):
    """Obtiene suscriptores del plugin Newsletter de WordPress."""
    subscribers = []
    try:
        r = requests.get(
            f'{site_url.rstrip("/")}/index.php?rest_route=/newsletter/v1/subscribers&status=confirmed',
            auth=(wp_user, wp_pass), timeout=15
        )
        if r.status_code == 200:
            subscribers = r.json()
    except Exception:
        pass
    return subscribers


def main():
    args      = sys.argv[1:]
    step      = args[0] if args else 'welcome'
    filter_kw = args[1] if len(args) > 1 else None

    sites = config['sites']
    if filter_kw:
        sites = [s for s in sites if filter_kw.lower() in s['url'].lower()]

    for site in sites:
        domain  = site['url'].replace('https://', '')
        seq_cfg = SEQUENCES.get(domain)
        if not seq_cfg:
            print(f'Sin secuencia configurada para {domain}')
            continue

        step_data = seq_cfg.get(step)
        if not step_data:
            print(f'{domain}: paso "{step}" no definido')
            continue

        print(f'\n{domain} — Enviando: {step}')

        subscribers = get_subscribers(site['url'], site['wp_user'], site['wp_password'])
        if not subscribers:
            print(f'  Sin suscriptores o plugin Newsletter no encontrado.')
            print(f'  Para probar: añade manualmente emails en la lista de abajo.')
            test_emails = []  # Añade emails aquí para probar
            subscribers = [{'email': e} for e in test_emails]

        html = get_html_email(
            seq_cfg['from_name'], seq_cfg['site_name'],
            seq_cfg['site_url'], seq_cfg['color'],
            step_data['subject'], step_data['body']
        )

        sent = 0
        for sub in subscribers:
            email = sub.get('email', '')
            if not email:
                continue
            ok = send_email(email, step_data['subject'], html, seq_cfg['from_name'])
            if ok:
                sent += 1
                print(f'  ✓ {email}')
            time.sleep(0.5)

        print(f'  Enviados: {sent}/{len(subscribers)}')


if __name__ == '__main__':
    main()
