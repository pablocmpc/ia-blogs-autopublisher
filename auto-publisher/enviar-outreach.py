#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Envía los emails de outreach para guest posts y colaboraciones."""

import smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
sys.stdout.reconfigure(encoding='utf-8')

SMTP_USER = "lafotocm@gmail.com"
SMTP_PASS = "itqf mlxl byip hyur"

def send_email(to, subject, body_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_USER
    msg["To"]      = to
    msg["Reply-To"] = SMTP_USER
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [to], msg.as_string())
        print(f"  OK → {to}")
        return True
    except Exception as e:
        print(f"  ERROR → {to}: {e}")
        return False

# ── EMAIL 1: HIPERTEXTUAL — Guest post IA estadísticas ─────────────────────
hipertextual_body = """
<p>Hola,</p>

<p>Os escribo porque creo que tengo un contenido que puede interesaros para Hipertextual.</p>

<p>Llevo meses trabajando en una <strong>guía de estadísticas de inteligencia artificial en España</strong>
con datos reales de fuentes oficiales (ONTSI, INE, DESI 2024), y el resultado es un artículo exhaustivo
que responde preguntas concretas:</p>

<ul>
  <li>¿Cuántas empresas españolas usan IA? (respuesta: 21,1% según INE 2024)</li>
  <li>¿Cuánto invierte España en IA? (€1.847M según ONTSI)</li>
  <li>¿Qué sectores lideran la adopción?</li>
  <li>¿Cómo estamos respecto al resto de Europa? (posición 12ª en DESI)</li>
</ul>

<p>El artículo lo tengo publicado en mis propios blogs de IA (iaparaprincipiantes.es, superprompts.es)
pero creo que en Hipertextual podría llegar a una audiencia mucho mayor y seguir siendo relevante para
vuestros lectores.</p>

<p><strong>Lo que ofrezco:</strong></p>
<ul>
  <li>Artículo exclusivo adaptado al estilo de Hipertextual (3.000+ palabras)</li>
  <li>Todos los datos verificados con fuentes oficiales enlazadas</li>
  <li>Imágenes propias o gráficos personalizados</li>
  <li>Sin compensación económica — simplemente a cambio de byline y enlace a mi site</li>
</ul>

<p>Si os interesa la idea, puedo enviarte el borrador completo esta semana.</p>

<p>Muchas gracias por vuestro tiempo,</p>
<p><strong>Pablo C.M.</strong><br>
iaparaprincipiantes.es · superprompts.es · guiaclaude.es<br>
lafotocm@gmail.com</p>
"""

# ── EMAIL 2: MUYCOMPUTER — Guest post drones normativa AESA 2026 ────────────
muycomputer_body = """
<p>Buenos días,</p>

<p>Me dirijo a MuyComputer porque creo que tengo un tema de actualidad que puede interesaros.</p>

<p>En enero de 2026 caducaron los certificados STS-ES-01 y STS-ES-02 de la AESA para pilotos de drones,
y hay mucha confusión entre los usuarios sobre qué significa esto para sus licencias actuales y cómo
les afecta el nuevo reglamento EASA.</p>

<p>Gestiono <a href="https://flydrones.es">flydrones.es</a>, un blog especializado en drones en español,
y tengo preparado un artículo completo sobre:</p>

<ul>
  <li>Qué ha cambiado en la normativa de drones en España en 2026</li>
  <li>Qué pasa con las licencias antiguas STS-ES</li>
  <li>Cómo está el mercado: DJI Mavic 4 Pro, Mini 5 Pro, los mejores drones ahora mismo</li>
  <li>Guía práctica para el examen A1/A3 de AESA</li>
</ul>

<p>El artículo está bien documentado (fuentes AESA + EASA), tiene gráficos propios y lo puedo
adaptar completamente al estilo de MuyComputer.</p>

<p><strong>Propuesta:</strong> colaboración tipo guest post, sin coste, a cambio de byline +
enlace dofollow a flydrones.es.</p>

<p>¿Os interesa? Puedo enviar el borrador completo antes del viernes.</p>

<p>Gracias,<br>
<strong>Pablo C.M.</strong><br>
flydrones.es<br>
lafotocm@gmail.com</p>
"""

# ── EMAIL 3: AGATUR.ES (Asociación Galega de Turismo Rural) ─────────────────
agatur_body = """
<p>Hola,</p>

<p>Me pongo en contacto con vosotros porque creo que podemos colaborar en beneficio mutuo para
la promoción del turismo rural en Galicia.</p>

<p>Llevo tiempo trabajando en <a href="https://turismoourense.es">turismoourense.es</a>, un blog
de turismo especializado en Ourense que ya cuenta con más de 90 artículos sobre termas, rutas,
gastronomía y alojamientos rurales de la provincia.</p>

<p>Acabamos de publicar una <strong>Guía Completa de Ourense 2026 descargable en PDF</strong>
(<a href="https://turismoourense.es/guia-completa-ourense/">ver guía</a>) que incluye:</p>
<ul>
  <li>Las termas gratuitas de Ourense (Outariz, Chavasqueira, Burgas...)</li>
  <li>Rutas por la Ribeira Sacra y Cañón do Sil</li>
  <li>Gastronomía local con recomendaciones verificadas</li>
  <li>Guía de alojamientos rurales</li>
</ul>

<p>Me gustaría explorar posibles colaboraciones: intercambio de enlaces, menciones mutuas,
o si AGATUR tiene algún directorio de recursos turísticos donde pudiera aparecer TurismoOurense.es.</p>

<p>¿Podríamos hablar?</p>

<p>Un saludo,<br>
<strong>Pablo C.M.</strong><br>
turismoourense.es<br>
lafotocm@gmail.com</p>
"""

emails = [
    ("redaccion@hipertextual.com",    "Propuesta de colaboración — Estadísticas de IA en España 2026", hipertextual_body),
    ("colaborar@hipertextual.com",    "Propuesta de colaboración — Estadísticas de IA en España 2026", hipertextual_body),
    ("redaccion@muycomputer.com",     "Propuesta guest post — Normativa drones España 2026 y mejores modelos", muycomputer_body),
    ("info@agatur.gal",               "Colaboración turismo rural — TurismoOurense.es", agatur_body),
]

print("Enviando emails de outreach...\n")
sent = 0
for to, subj, body in emails:
    print(f"→ {to}")
    if send_email(to, subj, body):
        sent += 1

print(f"\nResultado: {sent}/{len(emails)} emails enviados")
