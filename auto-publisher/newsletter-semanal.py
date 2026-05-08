"""
Envía el newsletter semanal a todos los suscriptores.
Recoge los últimos 7 artículos de cada web y los envía por email via SMTP.
Requiere en config.json: smtp_email, smtp_password (Gmail App Password)

Para obtener Gmail App Password:
  1. myaccount.google.com → Seguridad → Verificación en 2 pasos (activar)
  2. myaccount.google.com → Seguridad → Contraseñas de aplicaciones
  3. Crear una contraseña para "Correo" → copiar los 16 caracteres
"""
import json, smtplib, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import requests

with open("config.json") as f:
    cfg = json.load(f)

SMTP_EMAIL    = cfg.get("smtp_email", "")
SMTP_PASSWORD = cfg.get("smtp_password", "")
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587

if not SMTP_EMAIL or not SMTP_PASSWORD:
    print("ERROR: Añade smtp_email y smtp_password al config.json")
    print('  "smtp_email": "tumail@gmail.com",')
    print('  "smtp_password": "xxxx xxxx xxxx xxxx"  ← Gmail App Password')
    sys.exit(1)

def get_recent_posts(site_url, auth, days=7, count=5):
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    r = requests.get(
        f"{site_url.rstrip('/')}/wp-json/wp/v2/posts",
        auth=auth,
        params={"per_page": count, "after": since, "orderby": "date", "order": "desc", "_fields": "id,title,link,excerpt,date"}
    )
    return r.json() if r.ok else []

def get_subscribers(site_url, auth):
    r = requests.get(
        f"{site_url.rstrip('/')}/wp-json/newsletter/v1/subscribers",
        auth=auth
    )
    if r.ok:
        data = r.json()
        # Devuelve todos los emails de esta web (unificados)
        all_emails = set()
        for emails in data.values():
            all_emails.update(emails)
        return list(all_emails)
    return []

def build_html_email(site_name, site_url, posts, accent_color="#3b82f6", logo_emoji="🤖"):
    week = datetime.now().strftime("%-d de %B de %Y")
    posts_html = ""
    for p in posts:
        title = p.get("title", {}).get("rendered", "Sin título")
        link  = p.get("link", site_url)
        excerpt_raw = p.get("excerpt", {}).get("rendered", "")
        # Strip HTML tags from excerpt
        import re
        excerpt = re.sub('<[^>]+>', '', excerpt_raw).strip()[:160]
        date_str = p.get("date", "")[:10] if p.get("date") else ""
        posts_html += f"""
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:20px;margin-bottom:16px;">
          <p style="font-size:11px;color:#9ca3af;margin:0 0 8px">{date_str}</p>
          <h3 style="font-size:17px;font-weight:700;color:#111827;margin:0 0 8px;line-height:1.4">
            <a href="{link}" style="color:#111827;text-decoration:none">{title}</a>
          </h3>
          <p style="font-size:14px;color:#6b7280;margin:0 0 12px;line-height:1.6">{excerpt}...</p>
          <a href="{link}" style="display:inline-block;background:{accent_color};color:#fff;padding:8px 18px;border-radius:6px;font-size:13px;font-weight:600;text-decoration:none">Leer artículo →</a>
        </div>"""

    if not posts_html:
        posts_html = '<p style="color:#6b7280;font-size:14px">Esta semana no hay artículos nuevos.</p>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:system-ui,-apple-system,sans-serif;">
<div style="max-width:600px;margin:0 auto;padding:32px 16px;">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,{accent_color},{accent_color}dd);border-radius:16px;padding:32px;text-align:center;margin-bottom:24px;">
    <div style="font-size:48px;margin-bottom:12px">{logo_emoji}</div>
    <h1 style="color:#fff;font-size:24px;font-weight:800;margin:0 0 8px">{site_name}</h1>
    <p style="color:rgba(255,255,255,0.85);font-size:14px;margin:0">Newsletter semanal · {week}</p>
  </div>

  <!-- Artículos -->
  <h2 style="font-size:18px;font-weight:700;color:#111827;margin:0 0 16px">📰 Artículos de esta semana</h2>
  {posts_html}

  <!-- CTA -->
  <div style="text-align:center;margin:24px 0;">
    <a href="{site_url}" style="display:inline-block;background:{accent_color};color:#fff;padding:14px 32px;border-radius:10px;font-size:15px;font-weight:700;text-decoration:none">
      Ver todos los artículos →
    </a>
  </div>

  <!-- Footer -->
  <div style="border-top:1px solid #e5e7eb;padding-top:20px;text-align:center;">
    <p style="font-size:12px;color:#9ca3af;margin:0">
      Recibiste este email porque te suscribiste en {site_url}<br>
      <a href="{site_url}" style="color:{accent_color}">Visitar web</a> · Este email es generado automáticamente
    </p>
  </div>
</div>
</body>
</html>"""

SITE_CONFIG = {
    "iaparaprincipiantes": {"name": "IA para Principiantes", "color": "#3b82f6", "emoji": "🤖"},
    "superprompts":         {"name": "SuperPrompts.es",       "color": "#10b981", "emoji": "⚡"},
    "guiaclaude":           {"name": "GuiaClaude.es",          "color": "#f97316", "emoji": "🧡"},
}

print("=== Newsletter Semanal ===\n")

total_sent = 0
errors = []

for site_key, site in cfg.get("sites", {}).items():
    url  = site["url"].rstrip("/")
    auth = (site["username"], site["app_password"])
    scfg = SITE_CONFIG.get(site_key, {"name": site_key, "color": "#3b82f6", "emoji": "📬"})

    print(f"→ {site_key}: recogiendo artículos y suscriptores...")

    posts = get_recent_posts(url, auth)
    subscribers = get_subscribers(url, auth)

    print(f"   {len(posts)} artículos nuevos · {len(subscribers)} suscriptores")

    if not subscribers:
        print(f"   Sin suscriptores todavía — saltando\n")
        continue

    html_body = build_html_email(scfg["name"], url, posts, scfg["color"], scfg["emoji"])
    subject   = f"📬 {scfg['name']} — Newsletter {datetime.now().strftime('%d/%m/%Y')}"

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
            sent = 0
            for email_to in subscribers:
                msg = MIMEMultipart("alternative")
                msg["From"]    = f"{scfg['name']} <{SMTP_EMAIL}>"
                msg["To"]      = email_to
                msg["Subject"] = subject
                msg.attach(MIMEText(html_body, "html", "utf-8"))
                smtp.sendmail(SMTP_EMAIL, email_to, msg.as_string())
                sent += 1
            print(f"   ✅ Enviados {sent} emails\n")
            total_sent += sent
    except Exception as e:
        err = f"Error en {site_key}: {e}"
        errors.append(err)
        print(f"   ❌ {err}\n")

print(f"\n=== Resumen: {total_sent} emails enviados ===")
if errors:
    print("Errores:")
    for e in errors:
        print(f"  - {e}")
