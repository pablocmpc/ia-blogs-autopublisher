# -*- coding: utf-8 -*-
"""
Genera informe semanal HTML para enviar por email.
Se ejecuta via GitHub Actions cada lunes.
"""
import sys, os, json, csv, base64, requests
from datetime import datetime, timedelta
from collections import defaultdict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
LOG_FILE    = os.path.join(BASE_DIR, 'publicaciones.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'informe-email.html')

def auth(u, p):
    return {'Authorization': 'Basic ' + base64.b64encode(f'{u}:{p}'.encode()).decode()}

def read_pubs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def get_site_posts(site):
    try:
        r = requests.get(f"{site['url']}/wp-json/wp/v2/posts?per_page=1",
                         headers=auth(site['wp_user'], site['wp_password']), timeout=15)
        return int(r.headers.get('X-WP-Total', 0))
    except Exception:
        return 0

config = json.load(open(CONFIG_FILE, encoding='utf-8'))
pubs   = read_pubs()

today     = datetime.now()
week_ago  = today - timedelta(days=7)
month_ago = today - timedelta(days=30)

by_site = defaultdict(list)
for p in pubs:
    by_site[p.get('Web','')].append(p)

week_pubs  = [p for p in pubs if p.get('Fecha','')[:10] >= week_ago.strftime('%Y-%m-%d')]
month_pubs = [p for p in pubs if p.get('Fecha','')[:10] >= month_ago.strftime('%Y-%m-%d')]

colors = {'IA para Principiantes': '#3b82f6', 'SuperPrompts': '#22c55e', 'Guía Claude': '#f97316'}

rows = ''
for p in sorted(week_pubs, key=lambda x: x.get('Fecha',''), reverse=True)[:20]:
    c = colors.get(p.get('Web',''), '#6366f1')
    rows += f"""<tr>
        <td style="padding:8px 12px;border-bottom:1px solid #e5e7eb">
          <span style="background:{c}20;color:{c};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700">{p.get('Web','')}</span>
        </td>
        <td style="padding:8px 12px;border-bottom:1px solid #e5e7eb">
          <a href="{p.get('URL Artículo','#')}" style="color:#1d4ed8;text-decoration:none">{p.get('Título','')[:60]}{'…' if len(p.get('Título',''))>60 else ''}</a>
        </td>
        <td style="padding:8px 12px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:12px">{p.get('Fecha','')[:16]}</td>
      </tr>"""

site_blocks = ''
for site in config['sites']:
    n = site['name']
    c = colors.get(n, '#6366f1')
    total = get_site_posts(site)
    week_c  = sum(1 for p in by_site.get(n,[]) if p.get('Fecha','')[:10] >= week_ago.strftime('%Y-%m-%d'))
    month_c = sum(1 for p in by_site.get(n,[]) if p.get('Fecha','')[:10] >= month_ago.strftime('%Y-%m-%d'))
    site_blocks += f"""
    <td style="width:33%;padding:0 8px;vertical-align:top">
      <div style="background:#f8fafc;border-radius:12px;padding:20px;border-top:4px solid {c}">
        <div style="font-weight:700;font-size:16px;color:{c};margin-bottom:4px">{n}</div>
        <div style="font-size:13px;color:#6b7280;margin-bottom:16px"><a href="{site['url']}" style="color:#6b7280">{site['url']}</a></div>
        <div style="display:flex;justify-content:space-between;text-align:center">
          <div><div style="font-size:28px;font-weight:800;color:{c}">{week_c}</div><div style="font-size:11px;color:#9ca3af">esta semana</div></div>
          <div><div style="font-size:28px;font-weight:800;color:{c}">{month_c}</div><div style="font-size:11px;color:#9ca3af">este mes</div></div>
          <div><div style="font-size:28px;font-weight:800;color:{c}">{total}</div><div style="font-size:11px;color:#9ca3af">total</div></div>
        </div>
      </div>
    </td>"""

html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif">
<div style="max-width:700px;margin:20px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08)">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);padding:32px;text-align:center">
    <h1 style="color:#fff;font-size:22px;margin:0 0 8px">📊 Informe Semanal — IA Blogs</h1>
    <p style="color:#94a3b8;margin:0;font-size:14px">Semana del {week_ago.strftime('%d/%m/%Y')} al {today.strftime('%d/%m/%Y')}</p>
    <div style="margin-top:20px;background:rgba(255,255,255,.1);border-radius:12px;padding:16px">
      <div style="font-size:42px;font-weight:900;color:#22c55e">{len(week_pubs)}</div>
      <div style="color:#94a3b8;font-size:14px">artículos publicados esta semana</div>
    </div>
  </div>

  <!-- Site stats -->
  <div style="padding:24px">
    <h2 style="font-size:14px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;margin:0 0 16px">Por sitio web</h2>
    <table style="width:100%;border-collapse:collapse"><tr>{site_blocks}</tr></table>
  </div>

  <!-- Recent articles -->
  <div style="padding:0 24px 24px">
    <h2 style="font-size:14px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;margin:0 0 16px">Artículos publicados esta semana</h2>
    <table style="width:100%;border-collapse:collapse;font-size:13px">
      <thead>
        <tr style="background:#f8fafc">
          <th style="text-align:left;padding:10px 12px;color:#6b7280;font-size:11px;text-transform:uppercase">Web</th>
          <th style="text-align:left;padding:10px 12px;color:#6b7280;font-size:11px;text-transform:uppercase">Artículo</th>
          <th style="text-align:left;padding:10px 12px;color:#6b7280;font-size:11px;text-transform:uppercase">Fecha</th>
        </tr>
      </thead>
      <tbody>{rows if rows else '<tr><td colspan="3" style="padding:20px;text-align:center;color:#9ca3af">Sin publicaciones esta semana</td></tr>'}</tbody>
    </table>
  </div>

  <!-- SEO reminder -->
  <div style="background:#eff6ff;margin:0 24px 24px;border-radius:12px;padding:20px;border-left:4px solid #3b82f6">
    <h3 style="font-size:14px;color:#1d4ed8;margin:0 0 8px">🔍 Checklist SEO semanal</h3>
    <ul style="margin:0;padding-left:20px;color:#374151;font-size:13px;line-height:2">
      <li>Revisar Google Search Console → ¿nuevas keywords indexadas?</li>
      <li>Ver Ubersuggest → posiciones en top 50</li>
      <li>Comprobar AdSense → ¿primeras impresiones?</li>
      <li>Verificar que el publisher corrió los 7 turnos de hoy</li>
    </ul>
  </div>

  <!-- Footer -->
  <div style="background:#f8fafc;padding:20px;text-align:center;border-top:1px solid #e5e7eb">
    <p style="color:#9ca3af;font-size:12px;margin:0">Sistema automatizado con Groq (gratis) + WordPress REST API<br>
    <strong style="color:#22c55e">0 créditos de Claude consumidos en publicaciones</strong></p>
  </div>

</div>
</body>
</html>"""

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Informe generado: {OUTPUT_FILE}')
print(f'Artículos esta semana: {len(week_pubs)}')
print(f'Artículos este mes: {len(month_pubs)}')
print(f'Total en log: {len(pubs)}')
