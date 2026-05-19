#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKLINK OUTREACH — Gestor de oportunidades de enlaces
Rastrea, prioriza y envía emails de guest post / mención a sitios objetivo.
"""

import json, csv, os, smtplib, time, requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BASE_DIR   = os.path.dirname(__file__)
CONFIG     = os.path.join(BASE_DIR, 'config.json')
TRACKER    = os.path.join(BASE_DIR, 'backlinks-tracker.csv')

# ─────────────────────────────────────────────
# BASE DE DATOS DE OBJETIVOS POR NICHO
# ─────────────────────────────────────────────

TARGETS = {
    "ia_principiantes": [
        # MEDIOS TECH — acepta colaboraciones o tiene sección de opinión
        {"site": "xataka.com",           "url": "https://www.xataka.com",           "tipo": "medio",       "contacto": "redaccion@xataka.com",     "da": 80, "estado": "pendiente"},
        {"site": "genbeta.com",          "url": "https://www.genbeta.com",           "tipo": "medio",       "contacto": "redaccion@genbeta.com",    "da": 72, "estado": "pendiente"},
        {"site": "hipertextual.com",     "url": "https://hipertextual.com",          "tipo": "medio",       "contacto": "hola@hipertextual.com",    "da": 68, "estado": "pendiente"},
        {"site": "adslzone.net",         "url": "https://www.adslzone.net",          "tipo": "medio",       "contacto": "redaccion@adslzone.net",   "da": 65, "estado": "pendiente"},
        {"site": "computerhoy.com",      "url": "https://computerhoy.com",           "tipo": "medio",       "contacto": "redaccion@computerhoy.com","da": 63, "estado": "pendiente"},
        # BLOGS INDEPENDIENTES — más fácil conseguir guest post
        {"site": "noticias.ai",          "url": "https://noticias.ai",               "tipo": "blog",        "contacto": "contacto@noticias.ai",     "da": 35, "estado": "pendiente"},
        {"site": "bigml.com/blog",       "url": "https://blog.bigml.com",            "tipo": "blog",        "contacto": "info@bigml.com",           "da": 58, "estado": "pendiente"},
        # DIRECTORIOS Y LISTAS
        {"site": "blogsco.net",          "url": "https://www.blogsco.net",           "tipo": "directorio",  "contacto": "",                         "da": 30, "estado": "pendiente"},
        {"site": "bitacoras.com",        "url": "https://bitacoras.com",             "tipo": "directorio",  "contacto": "",                         "da": 48, "estado": "pendiente"},
    ],
    "prompts": [
        {"site": "marketingdirecto.com", "url": "https://www.marketingdirecto.com",  "tipo": "medio",       "contacto": "redaccion@marketingdirecto.com","da": 62, "estado": "pendiente"},
        {"site": "puromarketing.com",    "url": "https://www.puromarketing.com",     "tipo": "medio",       "contacto": "info@puromarketing.com",   "da": 58, "estado": "pendiente"},
        {"site": "socialancer.com",      "url": "https://www.socialancer.com",       "tipo": "blog",        "contacto": "hola@socialancer.com",     "da": 52, "estado": "pendiente"},
        {"site": "ciudadano2cero.com",   "url": "https://ciudadano2cero.com",        "tipo": "blog",        "contacto": "contacto@ciudadano2cero.com","da": 45, "estado": "pendiente"},
        {"site": "romuald-fons.com",     "url": "https://romuald-fons.com",          "tipo": "blog",        "contacto": "contacto@romuald-fons.com","da": 48, "estado": "pendiente"},
    ],
    "claude": [
        {"site": "genbeta.com",          "url": "https://www.genbeta.com",           "tipo": "medio",       "contacto": "redaccion@genbeta.com",    "da": 72, "estado": "pendiente"},
        {"site": "hipertextual.com",     "url": "https://hipertextual.com",          "tipo": "medio",       "contacto": "hola@hipertextual.com",    "da": 68, "estado": "pendiente"},
        {"site": "applesfera.com",       "url": "https://www.applesfera.com",        "tipo": "medio",       "contacto": "contacto@applesfera.com",  "da": 65, "estado": "pendiente"},
        {"site": "wwwhat's-new.com",     "url": "https://wwwhatsnew.com",            "tipo": "blog",        "contacto": "hola@wwwhatsnew.com",      "da": 55, "estado": "pendiente"},
    ],
    "turismo_ourense": [
        # TURISMO — más fácil porque es hiperlocal, poca competencia
        {"site": "turgalicia.es",        "url": "https://www.turismo.gal",           "tipo": "institucional","contacto": "turismo@xunta.gal",        "da": 55, "estado": "pendiente"},
        {"site": "spain.info",           "url": "https://www.spain.info",            "tipo": "institucional","contacto": "info@tourspain.es",        "da": 72, "estado": "pendiente"},
        {"site": "civitatis.com",        "url": "https://www.civitatis.com",         "tipo": "plataforma",  "contacto": "partners@civitatis.com",   "da": 70, "estado": "pendiente"},
        {"site": "laregion.es",          "url": "https://www.laregion.es",           "tipo": "periodico",   "contacto": "digital@laregion.es",      "da": 48, "estado": "pendiente"},
        {"site": "farodevigo.es",        "url": "https://www.farodevigo.es",         "tipo": "periodico",   "contacto": "redaccion@farodevigo.es",  "da": 55, "estado": "pendiente"},
        {"site": "galiciamaxica.eu",     "url": "https://www.galiciamaxica.eu",      "tipo": "blog-viajes", "contacto": "contacto@galiciamaxica.eu","da": 38, "estado": "pendiente"},
        {"site": "viajeros.com",         "url": "https://www.viajeros.com",          "tipo": "foro",        "contacto": "",                         "da": 52, "estado": "pendiente"},
        {"site": "minube.com",           "url": "https://www.minube.com",            "tipo": "plataforma",  "contacto": "info@minube.com",          "da": 60, "estado": "pendiente"},
        {"site": "losviajeros.com",      "url": "https://www.losviajeros.com",       "tipo": "foro",        "contacto": "",                         "da": 45, "estado": "pendiente"},
        {"site": "tripadvisor.es",       "url": "https://www.tripadvisor.es",        "tipo": "plataforma",  "contacto": "",                         "da": 93, "estado": "pendiente"},
    ],
    "bengalas_humo": [
        {"site": "bodas.net",            "url": "https://www.bodas.net",             "tipo": "plataforma",  "contacto": "info@bodas.net",           "da": 68, "estado": "pendiente"},
        {"site": "zankyou.es",           "url": "https://www.zankyou.es",            "tipo": "plataforma",  "contacto": "hola@zankyou.es",          "da": 62, "estado": "pendiente"},
        {"site": "elmundofotos.es",      "url": "https://www.elmundofotos.es",       "tipo": "blog-foto",   "contacto": "info@elmundofotos.es",     "da": 35, "estado": "pendiente"},
        {"site": "fotografosbodas.net",  "url": "https://www.fotografosbodas.net",   "tipo": "directorio",  "contacto": "info@fotografosbodas.net", "da": 38, "estado": "pendiente"},
        {"site": "fotografia.net",       "url": "https://www.fotografia.net",        "tipo": "comunidad",   "contacto": "contacto@fotografia.net",  "da": 50, "estado": "pendiente"},
        {"site": "diezminutos.es",       "url": "https://www.diezminutos.es",        "tipo": "medio",       "contacto": "redaccion@diezminutos.es", "da": 65, "estado": "pendiente"},
    ],
    "drones": [
        {"site": "aesa.gob.es",          "url": "https://www.aesa.gob.es",           "tipo": "institucional","contacto": "aesa@seguridadaerea.es",   "da": 62, "estado": "pendiente"},
        {"site": "dronespain.es",        "url": "https://dronespain.es",             "tipo": "comunidad",   "contacto": "info@dronespain.es",       "da": 32, "estado": "pendiente"},
        {"site": "aerovisual.es",        "url": "https://aerovisual.es",             "tipo": "blog",        "contacto": "hola@aerovisual.es",       "da": 28, "estado": "pendiente"},
        {"site": "forofpv.es",           "url": "https://forofpv.es",               "tipo": "foro",        "contacto": "",                         "da": 25, "estado": "pendiente"},
        {"site": "amazon.es-afiliados",  "url": "https://afiliados.amazon.es",       "tipo": "programa",    "contacto": "",                         "da": 96, "estado": "pendiente"},
        {"site": "reviews.es",           "url": "https://reviews.es",               "tipo": "blog",        "contacto": "contacto@reviews.es",      "da": 38, "estado": "pendiente"},
        {"site": "muycomputer.com",      "url": "https://www.muycomputer.com",       "tipo": "medio",       "contacto": "redaccion@muycomputer.com","da": 60, "estado": "pendiente"},
    ],
}

# ─────────────────────────────────────────────
# EMAIL TEMPLATES POR TIPO
# ─────────────────────────────────────────────

TEMPLATES = {
    "guest_post": {
        "asunto": "Propuesta de artículo para {site} — {tema}",
        "cuerpo": """Hola equipo de {site},

Me llamo {nombre} y llevo el blog {mi_blog} ({mi_url}), especializado en {nicho}.

He leído varios artículos vuestros sobre {tema_relacionado} y creo que vuestros lectores disfrutarían de un artículo sobre:

**"{titulo_propuesto}"**

Un adelanto del contenido:
- {punto1}
- {punto2}
- {punto3}

El artículo tendría entre 1.500 y 2.000 palabras, con datos actualizados, ejemplos prácticos y estructura clara.

A cambio, solo pediría incluir 1-2 enlaces contextuales hacia recursos relacionados en mi blog.

¿Os interesa? Puedo tenerlo listo en menos de una semana.

Un saludo,
{nombre}
{mi_url}"""
    },
    "enlace_recurso": {
        "asunto": "Recurso gratuito sobre {tema} para vuestros lectores",
        "cuerpo": """Hola,

He creado una guía/herramienta gratuita sobre {tema} que creo que sería muy útil para los lectores de {site}:

**{titulo_recurso}** → {url_recurso}

{descripcion_breve}

La mencionáis porque encaja perfectamente con vuestro artículo sobre {articulo_suyo} ({url_articulo_suyo}).

No pido nada a cambio, solo que si os parece útil lo compartáis con vuestros lectores.

Gracias,
{nombre}
{mi_blog} — {mi_url}"""
    },
    "mencion_sin_enlace": {
        "asunto": "Gracias por mencionar {mi_blog} — ¿Podéis añadir el enlace?",
        "cuerpo": """Hola equipo de {site},

Acabo de ver que mencionáis "{mi_blog}" en vuestro artículo:
{url_articulo_suyo}

¡Muchas gracias! Para que vuestros lectores puedan encontrar el recurso fácilmente, ¿os importaría añadir el enlace directo?

La URL correcta es: {mi_url}

Un saludo y gracias de nuevo,
{nombre}"""
    }
}

# ─────────────────────────────────────────────
# TRACKER CSV
# ─────────────────────────────────────────────

def init_tracker():
    if not os.path.exists(TRACKER):
        with open(TRACKER, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([
                'Fecha', 'Nicho', 'Sitio', 'DA', 'Tipo', 'Contacto',
                'Plantilla', 'Estado', 'Respuesta', 'URL_obtenida', 'Notas'
            ])

def log_outreach(nicho, target, plantilla, estado="enviado", notas=""):
    init_tracker()
    with open(TRACKER, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([
            datetime.now().strftime('%Y-%m-%d'),
            nicho, target['site'], target['da'], target['tipo'],
            target['contacto'], plantilla, estado, '', '', notas
        ])

def show_tracker():
    if not os.path.exists(TRACKER):
        print("No hay outreach registrado todavía.")
        return
    with open(TRACKER, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    print(f"\n{'BACKLINK OUTREACH TRACKER':^70}")
    print("="*70)

    by_estado = {}
    for r in rows:
        estado = r.get('Estado', 'pendiente')
        by_estado.setdefault(estado, []).append(r)

    for estado, items in by_estado.items():
        print(f"\n  [{estado.upper()}] ({len(items)})")
        for r in items:
            da_str = f"DA{r['DA']}" if r['DA'] else ""
            print(f"    {r['Fecha']} | {r['Nicho']:<15} | {r['Sitio']:<30} {da_str}")

    print(f"\n  Total: {len(rows)} contactos | Obtenidos: {sum(1 for r in rows if r.get('URL_obtenida'))}")

# ─────────────────────────────────────────────
# ENVÍO DE EMAIL
# ─────────────────────────────────────────────

def send_outreach_email(target, template_key, variables, config_path=CONFIG):
    config = json.load(open(config_path, encoding='utf-8'))
    smtp_user = config.get('smtp_email', '')
    smtp_pass = config.get('smtp_password', '')

    template = TEMPLATES[template_key]
    asunto = template['asunto'].format(**variables)
    cuerpo = template['cuerpo'].format(**variables)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = asunto
    msg['From']    = smtp_user
    msg['To']      = target['contacto']
    msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, target['contacto'], msg.as_bytes())
        print(f"  Email enviado a {target['contacto']}")
        return True
    except Exception as e:
        print(f"  Error email: {e}")
        return False

# ─────────────────────────────────────────────
# ACCIONES QUICK WIN
# ─────────────────────────────────────────────

QUICK_WINS = [
    # DIRECTORIOS GRATUITOS — enlace automático al registrarse
    {"nombre": "Bitácoras",       "url": "https://bitacoras.com/register",        "descripcion": "Mayor directorio blogs hispanohablantes. DA48. Enlace dofollow."},
    {"nombre": "Blogsco",         "url": "https://www.blogsco.net/anadir-blog",   "descripcion": "Directorio blogs español. DA30. Enlace dofollow."},
    {"nombre": "Feedspot ES",     "url": "https://www.feedspot.com/submit",       "descripcion": "Listas de top blogs. DA72. Mención con enlace."},
    {"nombre": "AllTop",          "url": "https://alltop.com/submit",             "descripcion": "Directorio RSS global. DA65."},
    {"nombre": "BlogLovin",       "url": "https://www.bloglovin.com/claim",       "descripcion": "Red de blogs. DA75. Perfil con enlace."},
    # COMUNIDADES — compartir contenido genera tráfico + backlinks indirectos
    {"nombre": "Reddit ES-IA",    "url": "https://www.reddit.com/r/inteligenciaartificial/", "descripcion": "Comunidad IA en español. Compartir artículos relevantes."},
    {"nombre": "Forocoches",      "url": "https://www.forocoches.com",             "descripcion": "Mayor foro español. Nichos: drones, tecnología."},
    {"nombre": "HN España",       "url": "https://www.meneame.net",               "descripcion": "Meneame — agregador noticias tech España. DA60."},
    {"nombre": "Medium ES",       "url": "https://medium.com",                    "descripcion": "Publicar resumen + enlace al blog original. DA95."},
    {"nombre": "Linkedin Pulse",  "url": "https://www.linkedin.com",              "descripcion": "Artículos en LinkedIn con enlace al blog. Alto DA."},
    # TURISMO OURENSE ESPECÍFICO
    {"nombre": "WikiViajes",      "url": "https://es.wikivoyage.org",             "descripcion": "Wikipedia viajes. Editar artículo Ourense, enlazar guía."},
    {"nombre": "TripAdvisor",     "url": "https://www.tripadvisor.es",            "descripcion": "Perfil empresa + publicar en foros. DA93."},
    {"nombre": "Minube",          "url": "https://www.minube.com",                "descripcion": "Red social viajes española. DA60. Reseñas con enlaces."},
    # FOTOGRAFIA / BENGALAS
    {"nombre": "Flickr",          "url": "https://www.flickr.com",               "descripcion": "Subir fotos con bengalas, enlazar al blog en descripción. DA94."},
    {"nombre": "500px",           "url": "https://500px.com",                    "descripcion": "Portfolio fotográfico. Enlace en bio. DA72."},
    # DRONES
    {"nombre": "RCGroups",        "url": "https://www.rcgroups.com",             "descripcion": "Mayor foro drones/RC del mundo. DA62."},
    {"nombre": "DroneDJ",         "url": "https://dronedj.com",                  "descripcion": "Medios drones en inglés — cobertura de reviews."},
]

def print_quick_wins():
    print("\n" + "="*70)
    print("  QUICK WINS — Backlinks fáciles esta semana")
    print("="*70)
    for qw in QUICK_WINS:
        print(f"\n  {qw['nombre']:<20} {qw['url']}")
        print(f"  → {qw['descripcion']}")

def print_targets_by_priority(nicho=None, min_da=0):
    print("\n" + "="*70)
    print("  OBJETIVOS DE OUTREACH (ordenados por DA)")
    print("="*70)

    nichos = [nicho] if nicho else list(TARGETS.keys())
    all_targets = []
    for n in nichos:
        for t in TARGETS.get(n, []):
            if t['da'] >= min_da and t['estado'] == 'pendiente':
                all_targets.append((n, t))

    all_targets.sort(key=lambda x: x[1]['da'], reverse=True)

    for n, t in all_targets[:30]:
        contacto = t['contacto'] or '(sin email — manual)'
        print(f"  DA{t['da']:>2} | {t['tipo']:<15} | {t['site']:<30} | {n}")
        if t['contacto']:
            print(f"       Email: {contacto}")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "lista":
        nicho_filter = sys.argv[2] if len(sys.argv) > 2 else None
        print_targets_by_priority(nicho=nicho_filter)

    elif cmd == "quickwins":
        print_quick_wins()

    elif cmd == "tracker":
        show_tracker()

    elif cmd == "resumen":
        total = sum(len(v) for v in TARGETS.values())
        print(f"\nOBJETIVOS TOTALES: {total} sitios en {len(TARGETS)} nichos")
        for nicho, targets in TARGETS.items():
            medios  = [t for t in targets if t['tipo'] in ('medio', 'periodico')]
            blogs   = [t for t in targets if t['tipo'] == 'blog']
            dirs    = [t for t in targets if t['tipo'] in ('directorio', 'comunidad', 'foro', 'plataforma')]
            print(f"  {nicho:<25}: {len(medios)} medios | {len(blogs)} blogs | {len(dirs)} directorios/plataformas")

    else:
        print("""
BACKLINK OUTREACH MANAGER
Uso:
  python backlink-outreach.py lista [nicho]    # Objetivos por DA
  python backlink-outreach.py quickwins        # Links fáciles esta semana
  python backlink-outreach.py tracker          # Ver estado del outreach
  python backlink-outreach.py resumen          # Resumen por nicho

Nichos: ia_principiantes | prompts | claude | turismo_ourense | bengalas_humo | drones
""")
