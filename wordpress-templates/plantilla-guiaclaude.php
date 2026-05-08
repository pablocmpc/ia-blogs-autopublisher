<?php /* Template Name: Página Principal */ ?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Guía Claude | La Guía Definitiva de Claude en Español</title>
  <meta name="description" content="Tutoriales, comparativas y guías de Claude de Anthropic en español. Aprende Claude desde cero o domina la API avanzada.">
  <?php wp_head(); ?>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body>header,#masthead,.site-header,.ast-header-break-point,.hestia-header,.header-section,.header-wrapper,#site-header,.custom-header,.site-branding,#wpadminbar{display:none!important;}
    html{margin-top:0!important;}body.admin-bar,body.logged-in{margin-top:0!important;padding-top:0!important;}
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    :root{--bg:#0C0C0E;--bg2:#141416;--bg3:#1C1C20;--orange:#F97316;--orange2:#EA580C;--amber:#FBBF24;--coral:#FB923C;--text:#FAFAFA;--text2:#A1A1AA;--text3:#52525B;--border:rgba(249,115,22,0.15);--border2:rgba(249,115,22,0.08);}
    html{scroll-behavior:smooth;}
    body{background:var(--bg);color:var(--text);font-family:'Plus Jakarta Sans',sans-serif;line-height:1.6;overflow-x:hidden;margin:0;padding:0;}
    ::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--orange);border-radius:3px;}
    nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between;transition:all .3s;}
    nav.scrolled{background:rgba(12,12,14,0.92);backdrop-filter:blur(24px);border-bottom:1px solid var(--border2);}
    .nav-logo{text-decoration:none;color:var(--text);display:flex;align-items:center;gap:.6rem;font-weight:800;font-size:1rem;}
    .logo-mark{width:34px;height:34px;background:linear-gradient(135deg,var(--orange),var(--amber));border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;}
    .logo-name span{color:var(--orange);}
    .nav-links{display:flex;gap:2rem;list-style:none;}
    .nav-links a{color:var(--text2);text-decoration:none;font-size:.88rem;font-weight:500;transition:color .2s;}
    .nav-links a:hover{color:var(--orange);}
    .nav-cta{background:linear-gradient(135deg,var(--orange),var(--amber))!important;color:#fff!important;padding:.45rem 1.1rem;border-radius:8px;font-weight:600!important;}
    #hero{min-height:100vh;position:relative;overflow:hidden;display:flex;align-items:center;padding:6rem 2rem 4rem;}
    .hero-bg{position:absolute;inset:0;z-index:0;background:radial-gradient(ellipse 70% 50% at 70% 30%,rgba(249,115,22,0.1) 0%,transparent 60%),radial-gradient(ellipse 50% 40% at 20% 70%,rgba(251,191,36,0.06) 0%,transparent 60%);}
    .orb{position:absolute;border-radius:50%;filter:blur(100px);pointer-events:none;z-index:0;}
    .hero-inner{position:relative;z-index:1;max-width:1200px;margin:0 auto;width:100%;display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center;}
    .hero-eyebrow{display:inline-flex;align-items:center;gap:.5rem;background:rgba(249,115,22,0.1);border:1px solid rgba(249,115,22,0.25);padding:.4rem 1rem;border-radius:100px;font-size:.78rem;font-weight:600;color:var(--orange);margin-bottom:1.5rem;animation:fadeUp .6s ease;}
    @keyframes fadeUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
    .hero-title{font-size:clamp(2.2rem,4.5vw,3.8rem);font-weight:800;line-height:1.15;margin-bottom:1.5rem;animation:fadeUp .6s ease .1s both;}
    .hero-title .hl{background:linear-gradient(135deg,var(--orange),var(--amber));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    .hero-sub{font-size:1rem;color:var(--text2);line-height:1.7;margin-bottom:2.5rem;animation:fadeUp .6s ease .2s both;}
    .hero-buttons{display:flex;gap:1rem;flex-wrap:wrap;animation:fadeUp .6s ease .3s both;}
    .btn-primary{background:linear-gradient(135deg,var(--orange),var(--amber));color:#fff;text-decoration:none;font-weight:700;padding:.9rem 2rem;border-radius:10px;transition:all .2s;box-shadow:0 0 40px rgba(249,115,22,0.25);}
    .btn-primary:hover{transform:translateY(-2px);box-shadow:0 0 60px rgba(249,115,22,0.4);}
    .btn-secondary{background:transparent;border:1px solid var(--border);color:var(--text2);text-decoration:none;font-weight:500;padding:.9rem 2rem;border-radius:10px;transition:all .2s;}
    .btn-secondary:hover{border-color:var(--orange);color:var(--orange);}
    .hero-right{display:flex;justify-content:center;align-items:center;animation:fadeUp .7s ease .4s both;}
    .claude-card{background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:2.5rem;width:100%;max-width:420px;position:relative;overflow:hidden;}
    .claude-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--orange),var(--amber),var(--coral));}
    .claude-card-head{display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;}
    .claude-avatar{width:48px;height:48px;background:linear-gradient(135deg,var(--orange),var(--amber));border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.4rem;}
    .claude-name{font-weight:700;font-size:1rem;}
    .claude-version{font-size:.72rem;color:var(--orange);background:rgba(249,115,22,0.1);border:1px solid var(--border);padding:.15rem .5rem;border-radius:4px;display:inline-block;margin-top:.2rem;}
    .claude-message{background:var(--bg3);border-radius:12px;padding:1rem 1.2rem;font-size:.88rem;color:var(--text2);line-height:1.7;margin-bottom:1rem;border:1px solid var(--border2);}
    .claude-message strong{color:var(--text);}
    .claude-features{display:flex;flex-direction:column;gap:.5rem;}
    .claude-feat{display:flex;align-items:center;gap:.6rem;font-size:.82rem;color:var(--text2);}
    .feat-icon{width:24px;height:24px;background:rgba(249,115,22,0.1);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:.75rem;flex-shrink:0;}
    #stats{padding:3.5rem 2rem;border-top:1px solid var(--border2);border-bottom:1px solid var(--border2);background:var(--bg2);}
    .stats-inner{max-width:900px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;text-align:center;}
    .stat-num{font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,var(--orange),var(--amber));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    .stat-lbl{font-size:.82rem;color:var(--text2);margin-top:.3rem;}
    section{padding:5rem 2rem;}.container{max-width:1200px;margin:0 auto;}
    .section-header{text-align:center;margin-bottom:3.5rem;}
    .section-tag{font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--orange);display:inline-block;margin-bottom:.75rem;}
    .section-title{font-size:clamp(1.8rem,3.5vw,2.8rem);font-weight:800;line-height:1.2;}
    .section-title .hl{background:linear-gradient(135deg,var(--orange),var(--amber));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    .section-sub{font-size:.95rem;color:var(--text2);margin-top:.75rem;}
    .reveal{opacity:0;transform:translateY(40px);transition:opacity .7s ease,transform .7s ease;}
    .reveal.visible{opacity:1;transform:translateY(0);}
    .stagger:nth-child(1){transition-delay:0s;}.stagger:nth-child(2){transition-delay:.1s;}.stagger:nth-child(3){transition-delay:.2s;}.stagger:nth-child(4){transition-delay:.3s;}.stagger:nth-child(5){transition-delay:.4s;}.stagger:nth-child(6){transition-delay:.5s;}
    .guias-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;}
    .guia-card{background:var(--bg2);border:1px solid var(--border2);border-radius:16px;padding:1.8rem;cursor:pointer;transition:all .3s;text-decoration:none;color:inherit;display:block;}
    .guia-card:hover{border-color:rgba(249,115,22,0.4);transform:translateY(-4px);box-shadow:0 20px 40px rgba(249,115,22,0.08);}
    .guia-icon{width:48px;height:48px;background:rgba(249,115,22,0.1);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;margin-bottom:1rem;}
    .guia-level{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem;}
    .guia-level.principiante{color:#10B981;}.guia-level.intermedio{color:var(--amber);}.guia-level.avanzado{color:var(--orange);}
    .guia-title{font-size:1rem;font-weight:700;margin-bottom:.4rem;line-height:1.4;}
    .guia-desc{font-size:.83rem;color:var(--text2);line-height:1.5;}
    .comp-table{max-width:800px;margin:0 auto;background:var(--bg3);border:1px solid var(--border2);border-radius:16px;overflow:hidden;}
    .comp-head{display:grid;grid-template-columns:2fr 1fr 1fr;background:rgba(249,115,22,0.05);border-bottom:1px solid var(--border2);}
    .comp-head div{padding:1rem 1.5rem;font-weight:700;font-size:.9rem;}
    .comp-head div:not(:first-child){text-align:center;}
    .comp-head .highlight{color:var(--orange);}
    .comp-row{display:grid;grid-template-columns:2fr 1fr 1fr;border-bottom:1px solid var(--border2);}
    .comp-row:last-child{border-bottom:none;}
    .comp-row:hover{background:rgba(249,115,22,0.03);}
    .comp-row div{padding:.9rem 1.5rem;font-size:.88rem;}
    .comp-row div:first-child{color:var(--text2);}
    .comp-row div:not(:first-child){text-align:center;}
    .tick{color:#10B981;}.cross{color:#EF4444;}.partial{color:var(--amber);font-size:.8rem;}
    #newsletter{background:linear-gradient(135deg,rgba(249,115,22,0.06),rgba(251,191,36,0.04));border-top:1px solid var(--border2);border-bottom:1px solid var(--border2);}
    .newsletter-inner{max-width:580px;margin:0 auto;text-align:center;}
    .nl-icon{width:64px;height:64px;background:linear-gradient(135deg,var(--orange),var(--amber));border-radius:16px;margin:0 auto 1.5rem;display:flex;align-items:center;justify-content:center;font-size:1.8rem;}
    .nl-title{font-size:clamp(1.5rem,3vw,2.2rem);font-weight:800;margin-bottom:.75rem;}
    .nl-sub{color:var(--text2);font-size:.95rem;margin-bottom:2rem;}
    .nl-form{display:flex;gap:.75rem;flex-wrap:wrap;justify-content:center;}
    .nl-form input{flex:1;min-width:240px;background:rgba(255,255,255,0.04);border:1px solid var(--border2);color:var(--text);padding:.85rem 1.2rem;border-radius:10px;font-size:.9rem;outline:none;transition:border-color .2s;}
    .nl-form input:focus{border-color:var(--orange);}
    .nl-form input::placeholder{color:var(--text3);}
    .nl-form button{background:linear-gradient(135deg,var(--orange),var(--amber));color:#fff;border:none;cursor:pointer;padding:.85rem 1.8rem;border-radius:10px;font-weight:700;font-size:.9rem;transition:all .2s;}
    .nl-form button:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(249,115,22,0.4);}
    footer{padding:3rem 2rem;border-top:1px solid var(--border2);}
    .footer-inner{max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:1.5rem;}
    .footer-logo{font-weight:800;font-size:1rem;color:var(--text);text-decoration:none;}
    .footer-logo span{color:var(--orange);}
    .footer-links{display:flex;gap:1.5rem;list-style:none;flex-wrap:wrap;}
    .footer-links a{color:var(--text3);text-decoration:none;font-size:.83rem;transition:color .2s;}
    .footer-links a:hover{color:var(--orange);}
    .footer-copy{font-size:.78rem;color:var(--text3);}
    @media(max-width:900px){.hero-inner{grid-template-columns:1fr;}.hero-right{display:none;}}
    @media(max-width:768px){.nav-links{display:none;}.stats-inner{grid-template-columns:repeat(2,1fr);}}
  </style>
</head>
<body>
  <nav id="navbar">
    <a href="#" class="nav-logo"><div class="logo-mark">🧡</div><div class="logo-name">Guía<span>Claude</span></div></a>
    <ul class="nav-links">
      <li><a href="#guias">Guías</a></li>
      <li><a href="#comparativa">Claude vs ChatGPT</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url'));?>/blog">Blog</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url'));?>/recursos-gratis" style="color:var(--orange);font-weight:700;">🎁 Recursos</a></li>
      <li><a href="#newsletter" class="nav-cta">Newsletter</a></li>
    </ul>
  </nav>
  <section id="hero">
    <div class="hero-bg"></div>
    <div class="orb" style="width:500px;height:500px;background:rgba(249,115,22,0.07);top:-100px;right:-100px;"></div>
    <div class="orb" style="width:300px;height:300px;background:rgba(251,191,36,0.05);bottom:0;left:0;"></div>
    <div class="hero-inner">
      <div class="hero-left">
        <div class="hero-eyebrow">🧡 La referencia de Claude en español</div>
        <h1 class="hero-title">Domina <span class="hl">Claude</span>,<br>la IA más avanzada<br>del mundo.</h1>
        <p class="hero-sub">Tutoriales paso a paso, comparativas honestas y guías prácticas sobre Claude de Anthropic. Todo en español, actualizado cada semana.</p>
        <div class="hero-buttons">
          <a href="#guias" class="btn-primary">Explorar guías →</a>
          <a href="#comparativa" class="btn-secondary">Claude vs ChatGPT</a>
        </div>
      </div>
      <div class="hero-right">
        <div class="claude-card">
          <div class="claude-card-head"><div class="claude-avatar">🧡</div><div><div class="claude-name">Claude 3.5 Sonnet</div><span class="claude-version">Anthropic · 2025</span></div></div>
          <div class="claude-message">Hola, soy Claude. Puedo ayudarte con escritura, análisis, programación y razonamiento complejo. <strong>¿En qué puedo ayudarte?</strong></div>
          <div class="claude-features">
            <div class="claude-feat"><div class="feat-icon">🧠</div>Razonamiento superior en tareas complejas</div>
            <div class="claude-feat"><div class="feat-icon">📄</div>200K tokens de contexto</div>
            <div class="claude-feat"><div class="feat-icon">🔒</div>El más seguro y honesto del mercado</div>
            <div class="claude-feat"><div class="feat-icon">🆓</div>Versión gratuita en claude.ai</div>
          </div>
        </div>
      </div>
    </div>
  </section>
  <div id="stats">
    <div class="stats-inner">
      <div class="reveal stagger"><div class="stat-num" data-count="80">0</div><div class="stat-lbl">Guías publicadas</div></div>
      <div class="reveal stagger"><div class="stat-num" data-count="4">0</div><div class="stat-lbl">Modelos analizados</div></div>
      <div class="reveal stagger"><div class="stat-num" data-count="200">0</div><div class="stat-lbl">Casos de uso</div></div>
      <div class="reveal stagger"><div class="stat-num" data-count="100">0</div><div class="stat-lbl">% en español</div></div>
    </div>
  </div>
  <!-- BANNER RECURSO GRATUITO -->
  <style>
  .lm-banner{background:linear-gradient(135deg,rgba(249,115,22,.06),rgba(251,191,36,.03));border-top:1px solid rgba(249,115,22,.15);border-bottom:1px solid rgba(249,115,22,.15);padding:3.5rem 2rem;position:relative;overflow:hidden;}
  .lm-banner::before{content:'';position:absolute;top:-30%;right:-5%;width:340px;height:340px;background:radial-gradient(circle,rgba(249,115,22,.1),transparent 70%);pointer-events:none;}
  .lm-inner{max-width:960px;margin:0 auto;display:flex;align-items:center;gap:3rem;flex-wrap:wrap;justify-content:space-between;}
  .lm-left{flex:1;min-width:280px;}
  .lm-etiqueta{display:inline-flex;align-items:center;gap:.4rem;background:rgba(249,115,22,.1);border:1px solid rgba(249,115,22,.25);color:#fb923c;padding:.3rem 1rem;border-radius:6px;font-size:.74rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;margin-bottom:1.1rem;}
  .lm-titulo{font-family:'Plus Jakarta Sans',sans-serif;font-size:clamp(1.4rem,3vw,2.1rem);font-weight:800;line-height:1.2;margin-bottom:.7rem;}
  .lm-titulo em{color:#f97316;font-style:normal;}
  .lm-desc{color:#6b7280;font-size:.9rem;margin-bottom:1.1rem;line-height:1.7;}
  .lm-checks{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:.35rem;margin-bottom:1.5rem;}
  .lm-checks li{display:flex;align-items:center;gap:.35rem;font-size:.82rem;color:#374151;}.lm-checks li::before{content:'✓';color:#f97316;font-weight:800;}
  .lm-cta{display:inline-flex;align-items:center;gap:.6rem;background:linear-gradient(135deg,#f97316,#ea580c);color:#fff;font-weight:700;font-size:1rem;padding:1rem 2.2rem;border-radius:10px;text-decoration:none;box-shadow:0 6px 28px rgba(249,115,22,.3);transition:all .25s;animation:orangePulse 2.5s ease-in-out infinite;}
  @keyframes orangePulse{0%,100%{box-shadow:0 6px 28px rgba(249,115,22,.3);}50%{box-shadow:0 8px 44px rgba(249,115,22,.6);}}
  .lm-cta:hover{transform:translateY(-3px);}
  .lm-right{flex-shrink:0;text-align:center;}
  .lm-card{background:rgba(249,115,22,.05);border:1px solid rgba(249,115,22,.18);border-radius:16px;padding:1.8rem 1.5rem;width:230px;}
  .lm-card-emoji{font-size:2.8rem;margin-bottom:.5rem;}
  .lm-card-num{font-family:'Plus Jakarta Sans',sans-serif;font-size:3.5rem;font-weight:800;color:#f97316;line-height:1;}
  .lm-card-label{font-size:.78rem;color:#6b7280;margin-top:.2rem;margin-bottom:.8rem;}
  .lm-card-tags{display:flex;flex-wrap:wrap;gap:.35rem;justify-content:center;}
  .lm-card-tag{font-size:.7rem;background:rgba(249,115,22,.1);color:#fb923c;padding:.2rem .6rem;border-radius:4px;}
  @media(max-width:640px){.lm-right{display:none;}.lm-checks{grid-template-columns:1fr;}}
  </style>
  <div class="lm-banner">
    <div class="lm-inner">
      <div class="lm-left">
        <div class="lm-etiqueta">🎁 Recurso gratuito · Sin registro</div>
        <h2 class="lm-titulo">40 Comandos y Plantillas<br>de <em>Claude AI</em> — gratis</h2>
        <p class="lm-desc">Los system prompts y plantillas más efectivos para escritura, código, análisis y productividad. Listos para copiar.</p>
        <ul class="lm-checks">
          <li>Escritura y contenido</li>
          <li>Productividad</li>
          <li>Programación y código</li>
          <li>Análisis de datos</li>
          <li>Plantillas creativas</li>
          <li>4 tips avanzados</li>
        </ul>
        <a href="<?php echo esc_url(get_bloginfo('url')); ?>/recursos-gratis" class="lm-cta">📋 Ver los 40 comandos gratis →</a>
      </div>
      <div class="lm-right">
        <div class="lm-card">
          <div class="lm-card-emoji">📋</div>
          <div class="lm-card-num">40</div>
          <div class="lm-card-label">plantillas incluidas</div>
          <div class="lm-card-tags">
            <span class="lm-card-tag">Escritura</span>
            <span class="lm-card-tag">Código</span>
            <span class="lm-card-tag">Análisis</span>
            <span class="lm-card-tag">Marketing</span>
            <span class="lm-card-tag">Creatividad</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <section id="guias"><div class="container">
    <div class="section-header reveal"><span class="section-tag">Todo sobre Claude</span><h2 class="section-title">¿Qué quieres <span class="hl">aprender?</span></h2></div>
    <div class="guias-grid">
      <?php
      $posts=get_posts(['numberposts'=>6,'post_status'=>'publish']);
      $icons=['🚀','⚔️','💼','⚡','🎯','🔬'];
      $levels=['principiante','principiante','intermedio','avanzado','intermedio','avanzado'];
      if($posts){foreach($posts as $i=>$p){$cats=get_the_category($p->ID);$cat=$cats?$cats[0]->name:'Tutorial';echo '<a href="'.esc_url(get_permalink($p->ID)).'" class="guia-card reveal stagger"><div class="guia-icon">'.$icons[$i%6].'</div><div class="guia-level '.$levels[$i%6].'">'.ucfirst($levels[$i%6]).'</div><div class="guia-title">'.esc_html($p->post_title).'</div><div class="guia-desc">'.wp_trim_words($p->post_excerpt?:$p->post_content,12).'</div></a>';}}
      else{$guias=[['🚀','principiante','Cómo usar Claude gratis paso a paso','Empieza desde cero. Crea tu cuenta y saca el máximo partido a la versión gratuita.'],['⚔️','intermedio','Claude vs ChatGPT: Comparativa honesta 2025','Analizamos ambas IAs en 10 categorías. ¿Cuál es mejor para ti?'],['💼','intermedio','Claude para negocios: 20 casos de uso reales','Cómo empresas reales usan Claude para automatizar y aumentar ingresos.'],['⚡','avanzado','Claude API: Tutorial completo en español','Integra Claude en tus apps con ejemplos listos para usar.'],['🎯','principiante','Los mejores prompts para Claude en español','50 prompts testados específicamente para Claude.'],['🔬','avanzado','Claude Projects: Tu IA personalizada','Configura Claude Projects para que trabaje en tu contexto.']];
      foreach($guias as $g){echo '<div class="guia-card reveal stagger"><div class="guia-icon">'.$g[0].'</div><div class="guia-level '.$g[1].'">'.ucfirst($g[1]).'</div><div class="guia-title">'.$g[2].'</div><div class="guia-desc">'.$g[3].'</div></div>';}}
      ?>
    </div>
  </div></section>
  <section id="comparativa" style="background:var(--bg2);"><div class="container">
    <div class="section-header reveal"><span class="section-tag">La pregunta más buscada</span><h2 class="section-title">Claude vs ChatGPT — <span class="hl">¿cuál gana?</span></h2></div>
    <div class="comp-table reveal">
      <div class="comp-head"><div>Característica</div><div class="highlight">Claude 3.5</div><div>ChatGPT-4o</div></div>
      <div class="comp-row"><div>Razonamiento complejo</div><div><span class="tick">✓ Superior</span></div><div><span class="tick">✓ Bueno</span></div></div>
      <div class="comp-row"><div>Escritura y redacción</div><div><span class="tick">✓ Excelente</span></div><div><span class="tick">✓ Muy bueno</span></div></div>
      <div class="comp-row"><div>Contexto largo</div><div><span class="tick">✓ 200K tokens</span></div><div><span class="partial">~ 128K tokens</span></div></div>
      <div class="comp-row"><div>Honestidad / sin alucinaciones</div><div><span class="tick">✓ Más honesto</span></div><div><span class="partial">~ Regular</span></div></div>
      <div class="comp-row"><div>Generación de imágenes</div><div><span class="cross">✗ No</span></div><div><span class="tick">✓ DALL-E 3</span></div></div>
      <div class="comp-row"><div>Precio Pro</div><div>20€/mes</div><div>20€/mes</div></div>
    </div>
  </div></section>
  <section id="newsletter"><div class="container"><div class="newsletter-inner reveal">
    <div class="nl-icon">🧡</div>
    <h2 class="nl-title">Lo mejor de Claude<br><span style="color:var(--orange)">cada semana en tu email</span></h2>
    <p class="nl-sub">Novedades, tutoriales y trucos de Claude antes que nadie. En español y gratis.</p>
    <form class="nl-form" id="nl-form-gc"><input type="email" id="nl-email-gc" placeholder="tu@email.com" required><button type="submit" id="nl-btn-gc">Suscribirme →</button></form>
    <p id="nl-msg-gc" style="font-size:.75rem;color:var(--text3);margin-top:.75rem;">Sin spam · Baja cuando quieras</p>
  </div></div></section>
  <footer><div class="footer-inner">
    <a href="#" class="footer-logo">Guía<span>Claude</span></a>
    <ul class="footer-links">
      <li><a href="<?php echo esc_url(get_bloginfo('url'));?>/sobre-nosotros">Sobre nosotros</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url'));?>/politica-de-privacidad">Privacidad</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url'));?>/contacto">Contacto</a></li>
    </ul>
    <p class="footer-copy">© <?php echo date('Y');?> GuiaClaude.es — Proyecto independiente, no afiliado a Anthropic</p>
  </div></footer>
  <?php wp_footer();?>
  <script>
    const nav=document.getElementById('navbar');
    window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>50);},{passive:true});
    const obs=new IntersectionObserver(e=>{e.forEach(el=>{if(el.isIntersecting){el.target.classList.add('visible');obs.unobserve(el.target);}});},{threshold:.1});
    document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
    const cObs=new IntersectionObserver(e=>{e.forEach(entry=>{if(!entry.isIntersecting)return;const el=entry.target,target=+el.dataset.count;let cur=0;const step=target/(1500/16);const t=setInterval(()=>{cur=Math.min(cur+step,target);el.textContent=target===100?Math.floor(cur)+'%':Math.floor(cur)+'+';if(cur>=target)clearInterval(t);},16);cObs.unobserve(el);});},{threshold:.5});
    document.querySelectorAll('.stat-num').forEach(el=>cObs.observe(el));
    window.addEventListener('scroll',()=>{document.querySelectorAll('.orb').forEach((o,i)=>{o.style.transform=`translateY(${window.scrollY*(i===0?.15:-.1)}px)`;});},{passive:true});
    document.getElementById('nl-form-gc').addEventListener('submit',async function(e){
      e.preventDefault();
      var btn=document.getElementById('nl-btn-gc'),msg=document.getElementById('nl-msg-gc'),email=document.getElementById('nl-email-gc').value.trim();
      btn.textContent='Enviando...';btn.disabled=true;
      try{
        var r=await fetch('<?php echo esc_url(rest_url("newsletter/v1/subscribe")); ?>',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,site:'guiaclaude'})});
        var d=await r.json();
        if(d.success){btn.textContent='✓ ¡Suscrito!';btn.style.background='#22c55e';document.getElementById('nl-email-gc').value='';}
        else{btn.textContent='Error - Reintentar';btn.disabled=false;}
        msg.textContent=d.message||msg.textContent;
      }catch(err){btn.textContent='Reintentar';btn.disabled=false;}
    });
  </script>
</body>
</html>
