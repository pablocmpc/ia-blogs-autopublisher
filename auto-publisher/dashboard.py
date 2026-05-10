# -*- coding: utf-8 -*-
"""
Dashboard en tiempo real para el auto-publisher.
Abre una web local que muestra el estado de la automatizacion.
Sin dependencias extra — usa solo la libreria estandar de Python.
"""
import http.server, socketserver, threading, webbrowser
import json, csv, os, sys, base64
from datetime import datetime, timezone, timedelta
try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CSV_FILE      = os.path.join(BASE_DIR, 'publicaciones.csv')
KEYWORDS_FILE = os.path.join(BASE_DIR, 'keywords.json')
CONFIG_FILE   = os.path.join(BASE_DIR, 'config.json')

GITHUB_REPO   = 'pablocmpc/ia-blogs-autopublisher'
PORT          = 8787

# ── Leer datos locales ──────────────────────────────────────────────────────

def get_publications():
    """Lee artículos reales desde WordPress API (datos en vivo, no CSV local)."""
    if not HAS_REQUESTS or not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception:
        return []
    pubs = []
    hoy = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    for site in cfg.get('sites', []):
        url  = site.get('url','').rstrip('/')
        user = site.get('wp_user','')
        pwd  = site.get('wp_password','')
        if not url: continue
        tok = base64.b64encode(f'{user}:{pwd}'.encode()).decode()
        h   = {'Authorization': f'Basic {tok}'}
        try:
            r = _requests.get(f'{url}/wp-json/wp/v2/posts', headers=h, timeout=8,
                params={'per_page':20,'orderby':'date','order':'desc',
                        '_fields':'id,title,link,date,categories'})
            if r.ok:
                for p in r.json():
                    pubs.append({
                        'Fecha':       p.get('date','')[:16].replace('T',' '),
                        'Web':         site.get('name','?')[:16],
                        'Titulo':      p.get('title',{}).get('rendered','?'),
                        'URL Articulo':p.get('link',''),
                        'URL Pinterest':'',
                    })
        except Exception:
            pass
    pubs.sort(key=lambda x: x['Fecha'], reverse=True)
    return pubs

def get_keywords_stats():
    if not os.path.exists(KEYWORDS_FILE):
        return {}
    with open(KEYWORDS_FILE, encoding='utf-8') as f:
        data = json.load(f)
    stats = {}
    for k, v in data.items():
        if not k.endswith('_usadas'):
            used_key = f'{k}_usadas'
            used = len(data.get(used_key, []))
            total = len(v) + used
            stats[k] = {'disponibles': len(v), 'usadas': used, 'total': total}
    return stats

def get_sites():
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE, encoding='utf-8') as f:
        cfg = json.load(f)
    return [{'name': s['name'], 'url': s['url']} for s in cfg.get('sites', [])]

# ── Proximas ejecuciones ────────────────────────────────────────────────────

SCHEDULES_ESP = [
    ('07:00', 5, 0),
    ('09:30', 7, 30),
    ('12:00', 10, 0),
    ('14:30', 12, 30),
    ('17:00', 15, 0),
    ('19:30', 17, 30),
    ('21:30', 19, 30),
]

def next_schedules():
    now_esp = datetime.now(timezone.utc) + timedelta(hours=2)
    upcoming = []
    for label, h, m in SCHEDULES_ESP:
        run = now_esp.replace(hour=h, minute=m, second=0, microsecond=0)
        if run > now_esp:
            diff = run - now_esp
            mins = int(diff.total_seconds() // 60)
            s = f'{mins // 60}h {mins % 60}m' if mins >= 60 else f'{mins}m'
            upcoming.append({'hora': label, 'en': s})
    return upcoming[:3]

# ── HTML ────────────────────────────────────────────────────────────────────

def build_html():
    pubs   = get_publications()
    kwds   = get_keywords_stats()
    sites  = get_sites()
    nexts  = next_schedules()

    hoy_str     = (datetime.now(timezone.utc) + timedelta(hours=2)).strftime('%Y-%m-%d')
    hoy_arts    = sum(1 for p in pubs if p.get('Fecha','').startswith(hoy_str))
    # Total real desde WP (X-WP-Total header)
    total_arts  = 0
    if HAS_REQUESTS and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding='utf-8') as f:
                _cfg = json.load(f)
            for _s in _cfg.get('sites',[]):
                _tok = base64.b64encode(f'{_s.get("wp_user","")}:{_s.get("wp_password","")}'.encode()).decode()
                _r = _requests.get(f'{_s.get("url","").rstrip("/")}/wp-json/wp/v2/posts',
                    headers={'Authorization':f'Basic {_tok}'}, timeout=6,
                    params={'per_page':1,'_fields':'id'})
                total_arts += int(_r.headers.get('X-WP-Total', 0)) if _r.ok else 0
        except Exception:
            total_arts = len(pubs)
    else:
        total_arts = len(pubs)
    sites_count = len(sites)

    # Publicaciones rows
    pub_rows = ''
    for p in pubs[:60]:
        url = p.get('URL Articulo', p.get('URL Artículo', ''))
        pin = p.get('URL Pinterest','')
        pin_badge = (f'<a href="{pin}" target="_blank" style="color:#e60023">📌</a>'
                     if pin else '<span style="color:#334155">—</span>')
        title = p.get('Titulo', p.get('Título', ''))
        pub_rows += f'''<tr>
          <td style="color:#94a3b8;white-space:nowrap;font-size:.75rem">{p.get("Fecha","")}</td>
          <td style="font-weight:600;color:#3b82f6;white-space:nowrap">{p.get("Web","")}</td>
          <td><a href="{url}" target="_blank" style="color:#e2e8f0;text-decoration:none">{title[:65]}</a></td>
          <td style="text-align:center">{pin_badge}</td>
        </tr>'''
    if not pub_rows:
        pub_rows = '<tr><td colspan="4" style="text-align:center;color:#334155;padding:2rem">Sin publicaciones todavía — ejecuta el publisher primero</td></tr>'

    # Keywords
    kw_colors = {'ia_principiantes':'#3b82f6','prompts':'#22c55e','claude':'#f97316'}
    kw_html = ''
    for k, s in kwds.items():
        c   = kw_colors.get(k, '#8b5cf6')
        pct = int(s['disponibles'] / s['total'] * 100) if s['total'] else 0
        kw_html += f'''<div style="margin-bottom:.9rem">
          <div style="display:flex;justify-content:space-between;margin-bottom:.3rem">
            <span style="font-size:.82rem;font-weight:600">{k}</span>
            <span style="font-size:.78rem;color:{c}">{s["disponibles"]} / {s["total"]}</span>
          </div>
          <div style="background:#0f172a;border-radius:4px;height:5px">
            <div style="background:{c};width:{pct}%;height:100%;border-radius:4px"></div>
          </div>
        </div>'''

    # Proximas
    next_html = ''
    for n in nexts:
        next_html += f'''<div style="display:flex;justify-content:space-between;align-items:center;padding:.55rem 0;border-bottom:1px solid #1e293b">
          <span style="font-size:.84rem">⏰ {n["hora"]} España</span>
          <span style="color:#22c55e;font-weight:700;font-size:.82rem">en {n["en"]}</span>
        </div>'''
    if not next_html:
        next_html = '<div style="color:#475569;font-size:.82rem;padding:.5rem 0">Todas las ejecuciones de hoy completadas. Mañana desde 07:00.</div>'

    # Webs
    sites_html = ''.join(f'<a href="{s["url"]}" target="_blank" style="display:flex;align-items:center;gap:.4rem;color:#60a5fa;font-size:.82rem;padding:.35rem 0;text-decoration:none">↗ {s["url"]}</a>' for s in sites)

    now_esp_str = (datetime.now(timezone.utc) + timedelta(hours=2)).strftime('%d/%m/%Y %H:%M')

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard — Auto-Publisher IA</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0f172a;color:#e2e8f0;font-family:system-ui,-apple-system,sans-serif;min-height:100vh}}
.bar{{background:#1e293b;border-bottom:1px solid #334155;padding:.8rem 2rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap}}
.bar-l{{display:flex;align-items:center;gap:.75rem}}
.live-dot{{width:9px;height:9px;background:#22c55e;border-radius:50%;animation:lp 1.8s ease-in-out infinite}}
@keyframes lp{{0%,100%{{box-shadow:0 0 0 0 rgba(34,197,94,.5)}}60%{{box-shadow:0 0 0 7px rgba(34,197,94,0)}}}}
.logo{{font-weight:800;font-size:1rem}}.logo em{{color:#3b82f6;font-style:normal}}
.badge{{background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.25);color:#22c55e;padding:.18rem .65rem;border-radius:4px;font-size:.7rem;font-weight:700;letter-spacing:.05em}}
.bar-r{{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap}}
.clock{{font-size:.8rem;color:#475569;font-variant-numeric:tabular-nums}}
.btn{{display:inline-flex;align-items:center;gap:.4rem;padding:.55rem 1.1rem;border-radius:8px;font-size:.82rem;font-weight:700;text-decoration:none;transition:all .2s}}
.btn-blue{{background:linear-gradient(135deg,#3b82f6,#6366f1);color:#fff}}
.btn-green{{background:linear-gradient(135deg,#22c55e,#16a34a);color:#000}}
.btn:hover{{transform:translateY(-1px);opacity:.92}}
.wrap{{max-width:1280px;margin:0 auto;padding:1.5rem}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:.9rem;margin-bottom:1.5rem}}
.stat{{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:1.1rem 1.3rem}}
.stat-v{{font-size:2.4rem;font-weight:800;line-height:1;margin-bottom:.2rem}}
.stat-l{{font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.07em}}
.row2{{display:grid;grid-template-columns:1fr 320px;gap:1.2rem;margin-bottom:1.2rem}}
.card{{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:1.3rem}}
.card-ttl{{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:#475569;margin-bottom:1rem}}
table{{width:100%;border-collapse:collapse}}
th{{font-size:.68rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:.07em;padding:.45rem .7rem;text-align:left;border-bottom:1px solid #334155}}
td{{padding:.55rem .7rem;border-bottom:1px solid #1e293b;vertical-align:middle}}
tr:last-child td{{border-bottom:none}}
tr:hover td{{background:rgba(255,255,255,.015)}}
.sidebar{{display:flex;flex-direction:column;gap:1.2rem}}
.note{{font-size:.75rem;color:#334155;margin-top:.8rem;padding:.6rem;background:#0f172a;border-radius:6px;line-height:1.6}}
.gh-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:.6rem}}
.gh-item{{background:#0f172a;border:1px solid #334155;border-radius:7px;padding:.7rem 1rem;display:flex;align-items:center;gap:.7rem}}
@media(max-width:880px){{.row2{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="bar">
  <div class="bar-l">
    <div class="live-dot"></div>
    <div class="logo">Auto-Publisher <em>IA</em></div>
    <span class="badge">EN VIVO</span>
  </div>
  <div class="bar-r">
    <span class="clock" id="clk">🕐 {now_esp_str}</span>
    <a href="https://github.com/{GITHUB_REPO}/actions" target="_blank" class="btn btn-blue">📊 Ver logs GitHub</a>
    <a href="https://github.com/{GITHUB_REPO}/actions/workflows/publicar-articulos.yml" target="_blank" class="btn btn-green">⚡ Publicar ahora</a>
  </div>
</div>

<div class="wrap">

  <div class="stats">
    <div class="stat"><div class="stat-v" style="color:#3b82f6">{total_arts}</div><div class="stat-l">Total publicados</div></div>
    <div class="stat"><div class="stat-v" style="color:#22c55e">{hoy_arts}</div><div class="stat-l">Publicados hoy</div></div>
    <div class="stat"><div class="stat-v" style="color:#f97316">{sites_count}</div><div class="stat-l">Webs activas</div></div>
    <div class="stat"><div class="stat-v" style="color:#8b5cf6">7</div><div class="stat-l">Turnos por día</div></div>
    <div class="stat"><div class="stat-v" style="color:#06b6d4">21</div><div class="stat-l">Artículos/día</div></div>
  </div>

  <div class="row2">
    <div class="card">
      <div class="card-ttl">📋 Últimas publicaciones</div>
      <div style="overflow-x:auto">
        <table>
          <thead><tr><th>Fecha</th><th>Web</th><th>Artículo</th><th>Pin</th></tr></thead>
          <tbody>{pub_rows}</tbody>
        </table>
      </div>
    </div>

    <div class="sidebar">
      <div class="card">
        <div class="card-ttl">⏰ Próximas publicaciones</div>
        {next_html}
        <div class="note">⚙️ GitHub Actions puede tener hasta 90 min de delay. La página se auto-refresca.</div>
      </div>
      <div class="card">
        <div class="card-ttl">🔑 Keywords disponibles</div>
        {kw_html if kw_html else '<span style="color:#334155;font-size:.82rem">No se puede leer keywords.json</span>'}
      </div>
      <div class="card">
        <div class="card-ttl">🌐 Tus webs</div>
        {sites_html}
        <div style="border-top:1px solid #334155;margin-top:.8rem;padding-top:.8rem">
          <a href="https://github.com/{GITHUB_REPO}" target="_blank" style="color:#475569;font-size:.75rem;text-decoration:none">↗ Repositorio en GitHub</a>
        </div>
      </div>
    </div>
  </div>

  <!-- GitHub Actions en tiempo real -->
  <div class="card" style="margin-bottom:1.2rem">
    <div class="card-ttl">🔄 Ejecuciones recientes GitHub Actions &nbsp;<span id="gh-st" style="font-weight:400;color:#334155;font-size:.7rem">cargando...</span></div>
    <div id="gh-runs" class="gh-grid" style="min-height:60px">
      <div style="color:#334155;font-size:.82rem;padding:.5rem">Consultando API de GitHub...</div>
    </div>
  </div>

</div>

<script>
// Reloj
function tick(){{
  const d=new Date();
  const e=new Date(d.toLocaleString('en-US',{{timeZone:'Europe/Madrid'}}));
  const p=n=>String(n).padStart(2,'0');
  document.getElementById('clk').textContent=
    '🕐 '+p(e.getDate())+'/'+p(e.getMonth()+1)+'/'+e.getFullYear()+
    ' '+p(e.getHours())+':'+p(e.getMinutes())+':'+p(e.getSeconds())+' España';
}}
setInterval(tick,1000); tick();

// GitHub Actions
const ICONS={{completed:'✅',success:'✅',in_progress:'🔄',queued:'⏳',failure:'❌',cancelled:'⚫',skipped:'➖'}};
const COLORS={{completed:'#22c55e',success:'#22c55e',in_progress:'#3b82f6',queued:'#f59e0b',failure:'#ef4444',cancelled:'#475569',skipped:'#475569'}};

async function loadRuns(){{
  try{{
    const r=await fetch('https://api.github.com/repos/{GITHUB_REPO}/actions/runs?per_page=10',{{
      headers:{{'Accept':'application/vnd.github.v3+json'}}
    }});
    if(!r.ok) throw new Error('HTTP '+r.status);
    const data=await r.json();
    const runs=data.workflow_runs||[];
    document.getElementById('gh-st').textContent=runs.length+' ejecuciones encontradas';
    let html='';
    for(const run of runs){{
      const status=run.conclusion||run.status||'queued';
      const icon=ICONS[status]||'❓';
      const color=COLORS[status]||'#64748b';
      const esp=new Date(run.created_at).toLocaleString('es-ES',{{timeZone:'Europe/Madrid',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}});
      html+=`<div class="gh-item">
        <span style="font-size:1.3rem">${{icon}}</span>
        <div style="flex:1;min-width:0">
          <div style="font-size:.79rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#e2e8f0">${{run.name||run.display_title}}</div>
          <div style="font-size:.71rem;color:#475569;margin-top:.1rem">${{esp}} · <span style="color:${{color}}">${{status}}</span></div>
        </div>
        <a href="${{run.html_url}}" target="_blank" style="color:#3b82f6;font-size:.72rem;white-space:nowrap;text-decoration:none">logs →</a>
      </div>`;
    }}
    document.getElementById('gh-runs').innerHTML=html||'<div style="color:#334155;font-size:.82rem">Sin ejecuciones recientes</div>';
  }}catch(e){{
    document.getElementById('gh-runs').innerHTML='<div style="color:#ef4444;font-size:.8rem">Error: '+e.message+'</div>';
    document.getElementById('gh-st').textContent='error';
  }}
}}
loadRuns();
setInterval(loadRuns,30000);

// Auto-refresh completo cada 60s
setTimeout(()=>location.reload(),60000);
</script>
</body>
</html>'''

# ── Servidor HTTP ────────────────────────────────────────────────────────────

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        html = build_html().encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html)
    def log_message(self, *a):
        pass

def open_browser():
    import time; time.sleep(1.2)
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == '__main__':
    print(f'\n{"="*50}')
    print(f'  DASHBOARD AUTO-PUBLISHER IA')
    print(f'  Abriendo http://localhost:{PORT} ...')
    print(f'  Ctrl+C para cerrar')
    print(f'{"="*50}\n')
    threading.Thread(target=open_browser, daemon=True).start()
    with socketserver.TCPServer(('', PORT), Handler) as srv:
        srv.allow_reuse_address = True
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print('\n  Dashboard cerrado.\n')
