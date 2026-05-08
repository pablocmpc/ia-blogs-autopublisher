<?php
/*
Template Name: Página Principal
*/
// No cargamos el theme de WordPress — usamos nuestro propio diseño completo
// Para activar: Páginas → Nueva página → Atributos de página → Plantilla: "Página Principal"
?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IA para Principiantes | Aprende Inteligencia Artificial desde Cero en Español</title>
  <meta name="description" content="Aprende inteligencia artificial desde cero, sin tecnicismos. Tutoriales, herramientas gratis y cómo ganar dinero con IA. Todo en español.">
  <meta name="robots" content="index, follow">
  <?php wp_head(); // Necesario para que WordPress añada scripts de SEO, Analytics, etc. ?>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg:#070B14;--bg2:#0D1321;--bg3:#111827;
      --blue:#4F8EF7;--purple:#8B5CF6;--cyan:#22D3EE;
      --text:#F1F5F9;--text2:#94A3B8;--text3:#64748B;
      --border:rgba(79,142,247,0.15);--card:rgba(13,19,33,0.8);
    }
    html{scroll-behavior:smooth;}
    body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;line-height:1.6;overflow-x:hidden;margin:0;padding:0;}
    ::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--blue);border-radius:3px;}
    nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between;transition:all .3s;}
    nav.scrolled{background:rgba(7,11,20,0.9);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:.75rem 2rem;}
    .nav-logo{font-family:'Space Grotesk',sans-serif;font-weight:800;font-size:1.1rem;text-decoration:none;color:var(--text);display:flex;align-items:center;gap:.5rem;}
    .nav-logo span{color:var(--blue);}
    .logo-icon{width:32px;height:32px;background:linear-gradient(135deg,var(--blue),var(--purple));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.9rem;}
    .nav-links{display:flex;gap:2rem;list-style:none;}
    .nav-links a{color:var(--text2);text-decoration:none;font-size:.9rem;font-weight:500;transition:color .2s;}
    .nav-links a:hover{color:var(--blue);}
    .nav-cta{background:linear-gradient(135deg,var(--blue),var(--purple));color:#fff!important;padding:.5rem 1.2rem;border-radius:8px;font-weight:600!important;}
    #hero{min-height:100vh;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;padding:6rem 2rem 4rem;}
    .hero-bg{position:absolute;inset:0;z-index:0;background:radial-gradient(ellipse 80% 60% at 50% 0%,rgba(79,142,247,0.12) 0%,transparent 70%),radial-gradient(ellipse 50% 40% at 80% 60%,rgba(139,92,246,0.1) 0%,transparent 60%);}
    .hero-grid{position:absolute;inset:0;z-index:0;background-image:linear-gradient(rgba(79,142,247,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(79,142,247,0.04) 1px,transparent 1px);background-size:50px 50px;mask-image:radial-gradient(ellipse 80% 80% at 50% 0%,black 40%,transparent 100%);}
    .hero-particles{position:absolute;inset:0;z-index:0;overflow:hidden;}
    .particle{position:absolute;width:2px;height:2px;background:var(--blue);border-radius:50%;animation:float linear infinite;opacity:0;}
    @keyframes float{0%{transform:translateY(100vh) rotate(0deg);opacity:0;}10%{opacity:.6;}90%{opacity:.4;}100%{transform:translateY(-10vh) rotate(720deg);opacity:0;}}
    .hero-content{position:relative;z-index:1;text-align:center;max-width:820px;margin:0 auto;}
    .hero-badge{display:inline-flex;align-items:center;gap:.5rem;background:rgba(79,142,247,0.1);border:1px solid rgba(79,142,247,0.3);padding:.4rem 1rem;border-radius:100px;font-size:.8rem;font-weight:500;color:var(--blue);margin-bottom:1.5rem;animation:fadeDown .6s ease;}
    .hero-badge::before{content:'';width:6px;height:6px;background:var(--blue);border-radius:50%;animation:pulse 2s infinite;}
    @keyframes pulse{0%,100%{opacity:1;}50%{opacity:.3;}}
    @keyframes fadeDown{from{opacity:0;transform:translateY(-20px);}to{opacity:1;transform:translateY(0);}}
    .hero-title{font-family:'Space Grotesk',sans-serif;font-size:clamp(2.5rem,6vw,4.5rem);font-weight:800;line-height:1.1;margin-bottom:1.5rem;animation:fadeUp .7s ease .1s both;}
    .hero-title .gradient{background:linear-gradient(135deg,var(--blue) 0%,var(--purple) 50%,var(--cyan) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    @keyframes fadeUp{from{opacity:0;transform:translateY(30px);}to{opacity:1;transform:translateY(0);}}
    .hero-sub{font-size:clamp(1rem,2vw,1.2rem);color:var(--text2);max-width:580px;margin:0 auto 2.5rem;animation:fadeUp .7s ease .2s both;}
    .hero-buttons{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;animation:fadeUp .7s ease .3s both;}
    .btn-primary{background:linear-gradient(135deg,var(--blue),var(--purple));color:#fff;text-decoration:none;padding:.85rem 2rem;border-radius:10px;font-weight:600;font-size:.95rem;transition:transform .2s,box-shadow .2s;box-shadow:0 0 30px rgba(79,142,247,0.3);}
    .btn-primary:hover{transform:translateY(-2px);box-shadow:0 0 40px rgba(79,142,247,0.5);}
    .btn-secondary{background:transparent;border:1px solid var(--border);color:var(--text2);text-decoration:none;padding:.85rem 2rem;border-radius:10px;font-weight:500;font-size:.95rem;transition:all .2s;}
    .btn-secondary:hover{border-color:var(--blue);color:var(--blue);background:rgba(79,142,247,0.05);}
    #stats{padding:4rem 2rem;background:linear-gradient(180deg,transparent 0%,rgba(79,142,247,0.03) 50%,transparent 100%);border-top:1px solid var(--border);border-bottom:1px solid var(--border);}
    .stats-inner{max-width:1000px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;text-align:center;}
    .stat-number{font-family:'Space Grotesk',sans-serif;font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    .stat-label{font-size:.85rem;color:var(--text2);margin-top:.3rem;}
    section{padding:5rem 2rem;}
    .section-header{text-align:center;margin-bottom:3.5rem;}
    .section-tag{display:inline-block;font-size:.75rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--blue);margin-bottom:.75rem;}
    .section-title{font-family:'Space Grotesk',sans-serif;font-size:clamp(1.8rem,3.5vw,2.8rem);font-weight:700;line-height:1.2;}
    .section-title .hl{background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    .section-sub{margin-top:.75rem;font-size:1rem;color:var(--text2);max-width:520px;margin:.75rem auto 0;}
    .container{max-width:1200px;margin:0 auto;}
    .reveal{opacity:0;transform:translateY(40px);transition:opacity .7s ease,transform .7s ease;}
    .reveal.visible{opacity:1;transform:translateY(0);}
    .stagger:nth-child(1){transition-delay:0s;}.stagger:nth-child(2){transition-delay:.1s;}.stagger:nth-child(3){transition-delay:.2s;}.stagger:nth-child(4){transition-delay:.3s;}
    #categorias{background:var(--bg2);}
    .cat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.5rem;}
    .cat-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:2rem;cursor:pointer;transition:transform .3s ease,border-color .3s ease,box-shadow .3s ease;position:relative;overflow:hidden;}
    .cat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--blue),var(--purple));transform:scaleX(0);transform-origin:left;transition:transform .3s ease;}
    .cat-card:hover{transform:translateY(-6px);border-color:rgba(79,142,247,0.4);box-shadow:0 20px 40px rgba(79,142,247,0.1);}
    .cat-card:hover::before{transform:scaleX(1);}
    .cat-icon{width:52px;height:52px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;margin-bottom:1.2rem;}
    .cat-card:nth-child(1) .cat-icon{background:rgba(79,142,247,0.15);}.cat-card:nth-child(2) .cat-icon{background:rgba(139,92,246,0.15);}.cat-card:nth-child(3) .cat-icon{background:rgba(34,211,238,0.15);}.cat-card:nth-child(4) .cat-icon{background:rgba(16,185,129,0.15);}
    .cat-title{font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:.5rem;}
    .cat-desc{font-size:.88rem;color:var(--text2);line-height:1.6;}
    .cat-count{display:inline-block;margin-top:1rem;font-size:.75rem;font-weight:600;color:var(--blue);background:rgba(79,142,247,0.1);padding:.2rem .7rem;border-radius:100px;}
    .steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:2rem;}
    .step{text-align:center;padding:2.5rem 2rem;background:var(--bg2);border:1px solid var(--border);border-radius:16px;}
    .step-num{font-family:'Space Grotesk',sans-serif;font-size:4rem;font-weight:800;line-height:1;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:1rem;opacity:.4;}
    .step-title{font-family:'Space Grotesk',sans-serif;font-size:1.15rem;font-weight:700;margin-bottom:.5rem;}
    .step-desc{font-size:.88rem;color:var(--text2);}
    #articulos{background:var(--bg2);}
    .articles-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.5rem;}
    .article-card{background:var(--bg3);border:1px solid var(--border);border-radius:16px;overflow:hidden;transition:transform .3s ease,box-shadow .3s ease;text-decoration:none;color:inherit;display:block;}
    .article-card:hover{transform:translateY(-4px);box-shadow:0 20px 40px rgba(0,0,0,0.3);}
    .article-img{height:180px;display:flex;align-items:center;justify-content:center;font-size:3rem;}
    .article-card:nth-child(1) .article-img{background:linear-gradient(135deg,rgba(79,142,247,0.2),rgba(139,92,246,0.2));}
    .article-card:nth-child(2) .article-img{background:linear-gradient(135deg,rgba(139,92,246,0.2),rgba(34,211,238,0.2));}
    .article-card:nth-child(3) .article-img{background:linear-gradient(135deg,rgba(34,211,238,0.2),rgba(79,142,247,0.2));}
    .article-body{padding:1.5rem;}
    .article-cat{font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--blue);margin-bottom:.5rem;}
    .article-title{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;line-height:1.4;margin-bottom:.5rem;}
    .article-desc{font-size:.83rem;color:var(--text2);line-height:1.5;}
    .article-meta{display:flex;align-items:center;gap:1rem;margin-top:1rem;padding-top:1rem;border-top:1px solid var(--border);font-size:.75rem;color:var(--text3);}
    #newsletter{background:linear-gradient(135deg,rgba(79,142,247,0.08),rgba(139,92,246,0.08));border-top:1px solid var(--border);border-bottom:1px solid var(--border);}
    .newsletter-inner{max-width:560px;margin:0 auto;text-align:center;}
    .newsletter-icon{width:64px;height:64px;background:linear-gradient(135deg,var(--blue),var(--purple));border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:1.8rem;margin:0 auto 1.5rem;}
    .newsletter-title{font-family:'Space Grotesk',sans-serif;font-size:clamp(1.5rem,3vw,2rem);font-weight:700;margin-bottom:.75rem;}
    .newsletter-sub{color:var(--text2);font-size:.95rem;margin-bottom:2rem;}
    .newsletter-form{display:flex;gap:.75rem;flex-wrap:wrap;justify-content:center;}
    .newsletter-form input{flex:1;min-width:240px;background:rgba(255,255,255,0.05);border:1px solid var(--border);color:var(--text);padding:.85rem 1.2rem;border-radius:10px;font-size:.9rem;outline:none;transition:border-color .2s;}
    .newsletter-form input:focus{border-color:var(--blue);}
    .newsletter-form input::placeholder{color:var(--text3);}
    .newsletter-form button{background:linear-gradient(135deg,var(--blue),var(--purple));color:#fff;border:none;cursor:pointer;padding:.85rem 1.8rem;border-radius:10px;font-weight:600;font-size:.9rem;transition:transform .2s,box-shadow .2s;}
    .newsletter-form button:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(79,142,247,0.4);}
    .newsletter-note{font-size:.75rem;color:var(--text3);margin-top:.75rem;}
    footer{padding:3rem 2rem;border-top:1px solid var(--border);}
    .footer-inner{max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:1.5rem;}
    .footer-logo{font-family:'Space Grotesk',sans-serif;font-weight:800;font-size:1rem;color:var(--text);text-decoration:none;}
    .footer-logo span{color:var(--blue);}
    .footer-links{display:flex;gap:1.5rem;list-style:none;flex-wrap:wrap;}
    .footer-links a{color:var(--text3);text-decoration:none;font-size:.85rem;transition:color .2s;}
    .footer-links a:hover{color:var(--blue);}
    .footer-copy{font-size:.8rem;color:var(--text3);}
    @media(max-width:768px){.nav-links{display:none;}.stats-inner{grid-template-columns:repeat(2,1fr);}}
  </style>
</head>
<body>
  <nav id="navbar">
    <a href="#" class="nav-logo"><div class="logo-icon">🤖</div>IA para <span>Principiantes</span></a>
    <ul class="nav-links">
      <li><a href="#categorias">Categorías</a></li>
      <li><a href="#articulos">Artículos</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url')); ?>/blog">Blog</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url')); ?>/kit-starter" style="color:var(--blue);font-weight:700;">🎁 Kit Gratis</a></li>
      <li><a href="#newsletter" class="nav-cta">Newsletter gratis</a></li>
    </ul>
  </nav>
  <section id="hero">
    <div class="hero-bg"></div><div class="hero-grid"></div>
    <div class="hero-particles" id="particles"></div>
    <div class="hero-content">
      <div class="hero-badge">Nuevo artículo cada día · En español</div>
      <h1 class="hero-title">La IA no es para genios.<br><span class="gradient">Es para ti.</span></h1>
      <p class="hero-sub">Aprende inteligencia artificial desde cero, sin tecnicismos. Herramientas gratis, tutoriales y cómo ganar dinero con IA.</p>
      <div class="hero-buttons">
        <a href="#categorias" class="btn-primary">🚀 Empezar a aprender</a>
        <a href="<?php echo esc_url(get_bloginfo('url')); ?>/blog" class="btn-secondary">Ver todos los artículos</a>
      </div>
    </div>
  </section>
  <div id="stats">
    <div class="stats-inner">
      <div class="reveal stagger"><div class="stat-number" data-count="150">0</div><div class="stat-label">Artículos publicados</div></div>
      <div class="reveal stagger"><div class="stat-number" data-count="48">0</div><div class="stat-label">Herramientas analizadas</div></div>
      <div class="reveal stagger"><div class="stat-number" data-count="12000">0</div><div class="stat-label">Lectores al mes</div></div>
      <div class="reveal stagger"><div class="stat-number" data-count="100">0</div><div class="stat-label">% gratis para siempre</div></div>
    </div>
  </div>
  <!-- BANNER RECURSO GRATUITO -->
  <style>
  .lm-banner{background:linear-gradient(135deg,rgba(79,142,247,.07),rgba(139,92,246,.05));border-top:1px solid rgba(79,142,247,.18);border-bottom:1px solid rgba(79,142,247,.18);padding:3.5rem 2rem;position:relative;overflow:hidden;}
  .lm-banner::before{content:'';position:absolute;top:-40%;right:-5%;width:380px;height:380px;background:radial-gradient(circle,rgba(79,142,247,.1),transparent 70%);pointer-events:none;}
  .lm-inner{max-width:960px;margin:0 auto;display:flex;align-items:center;gap:3rem;flex-wrap:wrap;justify-content:space-between;}
  .lm-left{flex:1;min-width:280px;}
  .lm-etiqueta{display:inline-flex;align-items:center;gap:.5rem;background:rgba(79,142,247,.1);border:1px solid rgba(79,142,247,.28);color:#4F8EF7;padding:.3rem 1rem;border-radius:20px;font-size:.74rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:1.1rem;}
  .lm-etiqueta span{width:7px;height:7px;background:#4F8EF7;border-radius:50%;animation:pulse 2s infinite;}
  .lm-titulo{font-family:'Space Grotesk',sans-serif;font-size:clamp(1.4rem,3vw,2.1rem);font-weight:800;line-height:1.2;margin-bottom:.7rem;}
  .lm-titulo em{color:#4F8EF7;font-style:normal;}
  .lm-desc{color:#94A3B8;font-size:.9rem;margin-bottom:1.1rem;line-height:1.65;}
  .lm-checks{list-style:none;display:flex;flex-wrap:wrap;gap:.4rem .4rem;margin-bottom:1.5rem;}
  .lm-checks li{display:flex;align-items:center;gap:.35rem;font-size:.82rem;color:#CBD5E1;background:rgba(255,255,255,.03);padding:.25rem .7rem;border-radius:6px;border:1px solid rgba(79,142,247,.1);}
  .lm-checks li::before{content:'✓';color:#4F8EF7;font-weight:800;font-size:.85rem;}
  .lm-cta{display:inline-flex;align-items:center;gap:.6rem;background:linear-gradient(135deg,#4F8EF7,#7C3AED);color:#fff;font-weight:700;font-size:1rem;padding:1rem 2.2rem;border-radius:10px;text-decoration:none;box-shadow:0 6px 28px rgba(79,142,247,.35);transition:all .25s;animation:pulseBtn 2.5s ease-in-out infinite;}
  @keyframes pulseBtn{0%,100%{box-shadow:0 6px 28px rgba(79,142,247,.35);}50%{box-shadow:0 8px 40px rgba(79,142,247,.6);}}
  .lm-cta:hover{transform:translateY(-3px);}
  .lm-right{flex-shrink:0;}
  .lm-card{background:rgba(13,19,33,.9);border:1px solid rgba(79,142,247,.22);border-radius:16px;padding:2rem 1.5rem;width:240px;text-align:center;}
  .lm-card-emoji{font-size:3rem;margin-bottom:.6rem;}
  .lm-card-num{font-family:'Space Grotesk',sans-serif;font-size:3.5rem;font-weight:800;color:#4F8EF7;line-height:1;}
  .lm-card-label{font-size:.78rem;color:#64748B;margin-top:.2rem;margin-bottom:1rem;}
  .lm-card-items{display:flex;flex-direction:column;gap:.35rem;}
  .lm-card-item{font-size:.74rem;color:#94A3B8;background:rgba(79,142,247,.06);padding:.28rem .7rem;border-radius:4px;text-align:left;}
  @media(max-width:640px){.lm-right{display:none;}}
  </style>
  <div class="lm-banner">
    <div class="lm-inner">
      <div class="lm-left">
        <div class="lm-etiqueta"><span></span>100% Gratuito · Sin registro</div>
        <h2 class="lm-titulo">🎁 Kit Starter IA:<br><em>10 herramientas + guía completa</em></h2>
        <p class="lm-desc">Todo lo que necesitas para empezar a usar inteligencia artificial hoy mismo. Sin tarjeta, sin email, sin trampa.</p>
        <ul class="lm-checks">
          <li>10 herramientas de IA gratis</li>
          <li>Guía paso a paso</li>
          <li>20 prompts para principiantes</li>
          <li>Recursos en español</li>
        </ul>
        <a href="<?php echo esc_url(get_bloginfo('url')); ?>/kit-starter" class="lm-cta">📦 Obtener el Kit Gratis →</a>
      </div>
      <div class="lm-right">
        <div class="lm-card">
          <div class="lm-card-emoji">🚀</div>
          <div class="lm-card-num">10</div>
          <div class="lm-card-label">herramientas incluidas</div>
          <div class="lm-card-items">
            <div class="lm-card-item">✓ ChatGPT + Claude AI</div>
            <div class="lm-card-item">✓ Canva AI + Designer</div>
            <div class="lm-card-item">✓ ElevenLabs + Runway</div>
            <div class="lm-card-item">✓ 20 prompts para empezar</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <section id="categorias"><div class="container">
    <div class="section-header reveal"><span class="section-tag">Explora por tema</span><h2 class="section-title">¿Qué quieres <span class="hl">aprender hoy?</span></h2></div>
    <div class="cat-grid">
      <div class="cat-card reveal stagger"><div class="cat-icon">🧠</div><div class="cat-title">IA desde Cero</div><div class="cat-desc">Qué es la IA, cómo funciona y por qué está cambiando el mundo.</div><span class="cat-count">Tutoriales básicos</span></div>
      <div class="cat-card reveal stagger"><div class="cat-icon">🛠️</div><div class="cat-title">Herramientas Gratis</div><div class="cat-desc">ChatGPT, Claude, Midjourney y mucho más. Guías paso a paso.</div><span class="cat-count">+40 herramientas</span></div>
      <div class="cat-card reveal stagger"><div class="cat-icon">💼</div><div class="cat-title">Negocios con IA</div><div class="cat-desc">Ideas reales de negocio usando IA. Desde freelance hasta agencias.</div><span class="cat-count">Ideas de negocio</span></div>
      <div class="cat-card reveal stagger"><div class="cat-icon">💰</div><div class="cat-title">Ganar Dinero con IA</div><div class="cat-desc">Métodos reales y probados para monetizar con inteligencia artificial.</div><span class="cat-count">Estrategias reales</span></div>
    </div>
  </div></section>
  <section id="articulos"><div class="container">
    <div class="section-header reveal"><span class="section-tag">Lo último del blog</span><h2 class="section-title">Artículos <span class="hl">recientes</span></h2></div>
    <?php
    $recent_posts = wp_get_recent_posts(['numberposts' => 3, 'post_status' => 'publish']);
    if ($recent_posts) {
        echo '<div class="articles-grid">';
        $emojis = ['🤖','💡','⚡'];
        foreach ($recent_posts as $i => $post) {
            $url = get_permalink($post['ID']);
            $cats = get_the_category($post['ID']);
            $cat_name = $cats ? $cats[0]->name : 'IA';
            echo '<a href="'.esc_url($url).'" class="article-card reveal stagger">';
            echo '<div class="article-img">'.$emojis[$i % 3].'</div>';
            echo '<div class="article-body">';
            echo '<div class="article-cat">'.esc_html($cat_name).'</div>';
            echo '<div class="article-title">'.esc_html($post['post_title']).'</div>';
            echo '<div class="article-desc">'.wp_trim_words($post['post_excerpt'] ?: $post['post_content'], 15).'</div>';
            echo '<div class="article-meta"><span>📅 '.get_the_date('d M', $post['ID']).'</span><span>⏱ '.ceil(str_word_count(strip_tags($post['post_content'])) / 200).' min</span></div>';
            echo '</div></a>';
        }
        echo '</div>';
    }
    ?>
  </div></section>
  <section id="newsletter"><div class="container"><div class="newsletter-inner reveal">
    <div class="newsletter-icon">📬</div>
    <h2 class="newsletter-title">Un artículo de IA<br>cada día en tu email</h2>
    <p class="newsletter-sub">Gratis, sin spam. Baja cuando quieras.</p>
    <form class="newsletter-form" onsubmit="return false;">
      <input type="email" placeholder="tu@email.com" required>
      <button type="submit">Suscribirme gratis →</button>
    </form>
    <p class="newsletter-note">Sin spam. Baja cuando quieras.</p>
  </div></div></section>
  <footer><div class="footer-inner">
    <a href="#" class="footer-logo">IA para <span>Principiantes</span></a>
    <ul class="footer-links">
      <li><a href="<?php echo esc_url(get_bloginfo('url')); ?>/sobre-nosotros">Sobre nosotros</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url')); ?>/politica-de-privacidad">Privacidad</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url')); ?>/contacto">Contacto</a></li>
    </ul>
    <p class="footer-copy">© <?php echo date('Y'); ?> IAparaPrincipiantes.es</p>
  </div></footer>
  <?php wp_footer(); ?>
  <script>
    const nav=document.getElementById('navbar');
    window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>50);},{passive:true});
    const container=document.getElementById('particles');
    for(let i=0;i<25;i++){const p=document.createElement('div');p.className='particle';p.style.cssText=`left:${Math.random()*100}%;width:${Math.random()*3+1}px;height:${Math.random()*3+1}px;animation-duration:${Math.random()*15+10}s;animation-delay:${Math.random()*10}s;background:${Math.random()>.5?'#4F8EF7':'#8B5CF6'};`;container.appendChild(p);}
    const obs=new IntersectionObserver(entries=>{entries.forEach(el=>{if(el.isIntersecting){el.target.classList.add('visible');obs.unobserve(el.target);}});},{threshold:.1});
    document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
    const cObs=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(!entry.isIntersecting)return;const el=entry.target,target=+el.dataset.count;let cur=0;const step=target/(1800/16);const t=setInterval(()=>{cur=Math.min(cur+step,target);el.textContent=target>=1000?Math.floor(cur).toLocaleString('es'):Math.floor(cur)+(target===100?'%':'+');if(cur>=target)clearInterval(t);},16);cObs.unobserve(el);});},{threshold:.5});
    document.querySelectorAll('.stat-number').forEach(el=>cObs.observe(el));
  </script>
</body>
</html>
