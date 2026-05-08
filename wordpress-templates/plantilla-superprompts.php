<?php /* Template Name: Página Principal */ ?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SuperPrompts | Los Mejores Prompts en Español para ChatGPT y Claude</title>
  <meta name="description" content="La colección más completa de prompts en español para ChatGPT, Claude, Gemini. Copia, adapta y domina cualquier IA.">
  <?php wp_head(); ?>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body>header,#masthead,.site-header,.ast-header-break-point,.hestia-header,.header-section,.header-wrapper,#site-header,.custom-header,.site-branding,#wpadminbar{display:none!important;}
    html{margin-top:0!important;}body.admin-bar,body.logged-in{margin-top:0!important;padding-top:0!important;}
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    :root{--bg:#030712;--bg2:#060D1A;--bg3:#0A1628;--green:#10B981;--green2:#059669;--cyan:#06B6D4;--yellow:#FBBF24;--text:#F0FDF4;--text2:#6EE7B7;--text3:#374151;--muted:#94A3B8;--border:rgba(16,185,129,0.15);--border2:rgba(16,185,129,0.08);}
    html{scroll-behavior:smooth;}
    body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;line-height:1.6;overflow-x:hidden;margin:0;padding:0;}
    ::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--green);border-radius:3px;}
    body::after{content:'';position:fixed;inset:0;z-index:9999;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.03) 2px,rgba(0,0,0,0.03) 4px);pointer-events:none;}
    nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between;transition:all .3s;}
    nav.scrolled{background:rgba(3,7,18,0.95);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);}
    .nav-logo{font-family:'JetBrains Mono',monospace;font-weight:800;font-size:1rem;text-decoration:none;color:var(--text);display:flex;align-items:center;gap:.6rem;}
    .logo-bracket{color:var(--green);}
    .logo-cursor{display:inline-block;width:8px;height:16px;background:var(--green);animation:blink 1s step-end infinite;vertical-align:-2px;}
    @keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}
    .nav-links{display:flex;gap:2rem;list-style:none;}
    .nav-links a{color:var(--muted);text-decoration:none;font-size:.85rem;font-family:'JetBrains Mono',monospace;transition:color .2s;}
    .nav-links a:hover{color:var(--green);}
    .nav-cta{background:transparent!important;border:1px solid var(--green)!important;color:var(--green)!important;padding:.45rem 1rem;border-radius:4px;}
    #hero{min-height:100vh;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;padding:6rem 2rem 4rem;}
    .hero-matrix{position:absolute;inset:0;z-index:0;overflow:hidden;opacity:.06;}
    .matrix-col{position:absolute;top:-100%;font-family:'JetBrains Mono',monospace;font-size:.7rem;line-height:1.4;color:var(--green);animation:matrixFall linear infinite;white-space:nowrap;}
    @keyframes matrixFall{to{transform:translateY(200vh);}}
    .hero-glow{position:absolute;top:50%;left:50%;transform:translate(-50%,-60%);width:600px;height:400px;background:radial-gradient(ellipse,rgba(16,185,129,0.08) 0%,transparent 70%);pointer-events:none;}
    .hero-content{position:relative;z-index:1;max-width:820px;margin:0 auto;text-align:center;}
    .terminal-badge{display:inline-flex;align-items:center;gap:.5rem;background:rgba(16,185,129,0.05);border:1px solid var(--border);padding:.5rem 1.2rem;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--green);margin-bottom:2rem;animation:fadeDown .6s ease;}
    @keyframes fadeDown{from{opacity:0;transform:translateY(-20px);}to{opacity:1;transform:translateY(0);}}
    .terminal-badge .dot{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pulse 2s infinite;}
    @keyframes pulse{0%,100%{opacity:1;}50%{opacity:.3;}}
    .hero-title{font-family:'JetBrains Mono',monospace;font-size:clamp(2rem,5.5vw,4rem);font-weight:800;line-height:1.15;margin-bottom:1.5rem;animation:fadeUp .7s ease .1s both;}
    .hero-title .green{color:var(--green);}.hero-title .cyan{color:var(--cyan);}.hero-title .dim{color:var(--muted);font-weight:400;}
    @keyframes fadeUp{from{opacity:0;transform:translateY(30px);}to{opacity:1;transform:translateY(0);}}
    .hero-sub{color:var(--muted);font-size:clamp(.9rem,1.8vw,1.05rem);max-width:560px;margin:0 auto 2.5rem;animation:fadeUp .7s ease .2s both;}
    .hero-buttons{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;animation:fadeUp .7s ease .3s both;}
    .btn-primary{background:var(--green);color:var(--bg);text-decoration:none;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:.9rem;padding:.85rem 2rem;border-radius:4px;transition:all .2s;box-shadow:0 0 30px rgba(16,185,129,0.3);}
    .btn-primary:hover{background:var(--green2);box-shadow:0 0 50px rgba(16,185,129,0.5);transform:translateY(-2px);}
    .btn-secondary{background:transparent;border:1px solid var(--border);color:var(--green);text-decoration:none;font-family:'JetBrains Mono',monospace;font-size:.9rem;padding:.85rem 2rem;border-radius:4px;transition:all .2s;}
    .btn-secondary:hover{border-color:var(--green);background:rgba(16,185,129,0.05);}
    .hero-terminal{margin:3rem auto 0;background:rgba(6,13,26,0.8);border:1px solid var(--border);border-radius:8px;padding:1.5rem;text-align:left;max-width:600px;animation:fadeUp .7s ease .5s both;}
    .terminal-bar{display:flex;gap:6px;margin-bottom:1rem;}
    .terminal-dot{width:12px;height:12px;border-radius:50%;}
    .terminal-dot:nth-child(1){background:#FF5F57;}.terminal-dot:nth-child(2){background:#FEBC2E;}.terminal-dot:nth-child(3){background:#28C840;}
    .terminal-line{font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.8;color:var(--muted);}
    .terminal-line .prompt{color:var(--green);}.terminal-line .cmd{color:var(--cyan);}
    .typing-cursor{display:inline-block;width:8px;height:14px;background:var(--green);vertical-align:-2px;animation:blink 1s step-end infinite;}
    #stats{padding:3.5rem 2rem;border-top:1px solid var(--border2);border-bottom:1px solid var(--border2);background:var(--bg2);}
    .stats-inner{max-width:900px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;text-align:center;}
    .stat-num{font-family:'JetBrains Mono',monospace;font-size:2.2rem;font-weight:800;color:var(--green);text-shadow:0 0 20px rgba(16,185,129,0.4);}
    .stat-lbl{font-size:.8rem;color:var(--muted);margin-top:.3rem;}
    section{padding:5rem 2rem;}.container{max-width:1200px;margin:0 auto;}
    .section-header{text-align:center;margin-bottom:3.5rem;}
    .section-tag{font-family:'JetBrains Mono',monospace;font-size:.72rem;color:var(--green);letter-spacing:.12em;text-transform:uppercase;display:inline-block;margin-bottom:.75rem;}
    .section-tag::before{content:'// ';}
    .section-title{font-family:'JetBrains Mono',monospace;font-size:clamp(1.6rem,3vw,2.5rem);font-weight:800;line-height:1.2;}
    .section-title .hl{color:var(--green);}.section-title .hl2{color:var(--cyan);}
    .section-sub{color:var(--muted);font-size:.95rem;margin-top:.75rem;}
    .reveal{opacity:0;transform:translateY(40px);transition:opacity .7s ease,transform .7s ease;}
    .reveal.visible{opacity:1;transform:translateY(0);}
    .stagger:nth-child(1){transition-delay:0s;}.stagger:nth-child(2){transition-delay:.1s;}.stagger:nth-child(3){transition-delay:.2s;}.stagger:nth-child(4){transition-delay:.3s;}
    .cat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.5rem;}
    .cat-card{background:var(--bg2);border:1px solid var(--border2);border-radius:8px;padding:2rem;cursor:pointer;transition:all .3s ease;position:relative;overflow:hidden;}
    .cat-card:hover{border-color:var(--green);transform:translateY(-4px);box-shadow:0 0 30px rgba(16,185,129,0.1),0 20px 40px rgba(0,0,0,0.4);}
    .cat-tag{font-family:'JetBrains Mono',monospace;font-size:.7rem;color:var(--green);background:rgba(16,185,129,0.1);border:1px solid var(--border);padding:.2rem .6rem;border-radius:3px;display:inline-block;margin-bottom:1rem;}
    .cat-title{font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:700;margin-bottom:.5rem;color:var(--text);}
    .cat-desc{font-size:.85rem;color:var(--muted);line-height:1.6;}
    .cat-examples{margin-top:1rem;display:flex;flex-direction:column;gap:.3rem;}
    .cat-ex{font-family:'JetBrains Mono',monospace;font-size:.72rem;color:var(--green);opacity:.7;}
    .cat-ex::before{content:'→ ';}
    .articles-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.5rem;}
    .article-card{background:var(--bg3);border:1px solid var(--border2);border-radius:8px;overflow:hidden;transition:all .3s;text-decoration:none;color:inherit;display:block;}
    .article-card:hover{border-color:rgba(16,185,129,0.4);transform:translateY(-3px);}
    .article-img{height:150px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;}
    .article-card:nth-child(1) .article-img{background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(6,182,212,0.1));}
    .article-card:nth-child(2) .article-img{background:linear-gradient(135deg,rgba(6,182,212,0.15),rgba(16,185,129,0.1));}
    .article-card:nth-child(3) .article-img{background:linear-gradient(135deg,rgba(251,191,36,0.15),rgba(16,185,129,0.1));}
    .article-body{padding:1.2rem;}
    .article-cat{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--green);margin-bottom:.4rem;}
    .article-title{font-family:'JetBrains Mono',monospace;font-size:.9rem;font-weight:700;line-height:1.4;margin-bottom:.4rem;}
    .article-meta{font-size:.72rem;color:var(--text3);margin-top:.75rem;display:flex;gap:1rem;}
    #newsletter{border-top:1px solid var(--border2);border-bottom:1px solid var(--border2);background:var(--bg2);}
    .newsletter-inner{max-width:560px;margin:0 auto;text-align:center;}
    .nl-terminal{font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--green);margin-bottom:1.5rem;}
    .nl-title{font-family:'JetBrains Mono',monospace;font-size:clamp(1.4rem,3vw,2rem);font-weight:800;margin-bottom:.75rem;}
    .nl-sub{color:var(--muted);font-size:.9rem;margin-bottom:2rem;}
    .nl-form{display:flex;gap:.75rem;flex-wrap:wrap;justify-content:center;}
    .nl-form input{flex:1;min-width:240px;background:rgba(16,185,129,0.03);border:1px solid var(--border);border-radius:4px;color:var(--text);padding:.8rem 1rem;font-family:'JetBrains Mono',monospace;font-size:.85rem;outline:none;transition:border-color .2s;}
    .nl-form input:focus{border-color:var(--green);}
    .nl-form input::placeholder{color:var(--text3);}
    .nl-form button{background:var(--green);color:var(--bg);border:none;cursor:pointer;padding:.8rem 1.5rem;border-radius:4px;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:.85rem;transition:all .2s;}
    .nl-form button:hover{background:var(--green2);box-shadow:0 0 30px rgba(16,185,129,0.4);}
    .nl-note{font-family:'JetBrains Mono',monospace;font-size:.7rem;color:var(--text3);margin-top:.75rem;}
    footer{padding:2.5rem 2rem;border-top:1px solid var(--border2);}
    .footer-inner{max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:1.5rem;}
    .footer-logo{font-family:'JetBrains Mono',monospace;font-weight:800;font-size:.9rem;color:var(--green);text-decoration:none;}
    .footer-links{display:flex;gap:1.5rem;list-style:none;flex-wrap:wrap;}
    .footer-links a{color:var(--text3);text-decoration:none;font-size:.78rem;font-family:'JetBrains Mono',monospace;transition:color .2s;}
    .footer-links a:hover{color:var(--green);}
    .footer-copy{font-family:'JetBrains Mono',monospace;font-size:.72rem;color:var(--text3);}
    @media(max-width:768px){.nav-links{display:none;}.stats-inner{grid-template-columns:repeat(2,1fr);}}
  </style>
</head>
<body>
  <nav id="navbar">
    <a href="#" class="nav-logo"><span class="logo-bracket">[</span>SuperPrompts<span class="logo-bracket">]</span><span class="logo-cursor"></span></a>
    <ul class="nav-links">
      <li><a href="#categorias">categorías</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url')); ?>/blog">blog</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url')); ?>/prompts-gratis" style="color:var(--green);font-weight:700;">🎁 prompts-gratis</a></li>
      <li><a href="#newsletter" class="nav-cta">newsletter</a></li>
    </ul>
  </nav>
  <section id="hero">
    <div class="hero-matrix" id="matrix"></div>
    <div class="hero-glow"></div>
    <div class="hero-content">
      <div class="terminal-badge"><span class="dot"></span>superprompts.es — 500+ prompts en español</div>
      <h1 class="hero-title"><span class="dim">// el prompt perfecto</span><br><span class="green">cambia</span> <span class="cyan">todo</span><span class="dim">.</span></h1>
      <p class="hero-sub">La colección más completa de prompts en español para ChatGPT, Claude, Gemini y más. Copia, adapta y domina cualquier IA.</p>
      <div class="hero-buttons">
        <a href="#categorias" class="btn-primary">$ ver_prompts --todos</a>
        <a href="<?php echo esc_url(get_bloginfo('url')); ?>/blog" class="btn-secondary">explorar blog →</a>
      </div>
      <div class="hero-terminal">
        <div class="terminal-bar"><span class="terminal-dot"></span><span class="terminal-dot"></span><span class="terminal-dot"></span></div>
        <div class="terminal-line"><span class="prompt">usuario@superprompts:~$ </span><span class="cmd" id="typed-cmd"></span><span class="typing-cursor" id="tcursor"></span></div>
        <div class="terminal-line" id="typed-output" style="margin-top:.5rem;min-height:1.4em;color:#6EE7B7;"></div>
      </div>
    </div>
  </section>
  <div id="stats">
    <div class="stats-inner">
      <div class="reveal stagger"><div class="stat-num" data-count="500">0</div><div class="stat-lbl">prompts publicados</div></div>
      <div class="reveal stagger"><div class="stat-num" data-count="8">0</div><div class="stat-lbl">categorías</div></div>
      <div class="reveal stagger"><div class="stat-num" data-count="15000">0</div><div class="stat-lbl">usos este mes</div></div>
      <div class="reveal stagger"><div class="stat-num" data-count="5">0</div><div class="stat-lbl">IAs cubiertas</div></div>
    </div>
  </div>
  <!-- BANNER RECURSO GRATUITO -->
  <style>
  .lm-banner{background:rgba(6,13,26,.85);border-top:1px solid rgba(16,185,129,.12);border-bottom:1px solid rgba(16,185,129,.12);padding:3.5rem 2rem;position:relative;overflow:hidden;}
  .lm-scan{position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(16,185,129,.012) 3px,rgba(16,185,129,.012) 4px);pointer-events:none;}
  .lm-inner{max-width:960px;margin:0 auto;display:flex;align-items:center;gap:3rem;flex-wrap:wrap;justify-content:space-between;}
  .lm-left{flex:1;min-width:280px;}
  .lm-etiqueta{display:inline-block;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.22);color:#10B981;padding:.3rem .9rem;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:.72rem;font-weight:700;letter-spacing:.12em;margin-bottom:1.1rem;}
  .lm-titulo{font-family:'JetBrains Mono',monospace;font-size:clamp(1.2rem,3vw,1.85rem);font-weight:800;line-height:1.3;margin-bottom:.7rem;}
  .lm-titulo em{color:#10B981;font-style:normal;}
  .lm-desc{color:#94A3B8;font-size:.88rem;margin-bottom:1.1rem;line-height:1.7;font-family:'Inter',sans-serif;}
  .lm-checks{list-style:none;margin-bottom:1.5rem;}
  .lm-checks li{display:flex;align-items:center;gap:.6rem;font-size:.82rem;color:#94A3B8;padding:.18rem 0;font-family:'JetBrains Mono',monospace;}
  .lm-checks li::before{content:'> ';color:#10B981;font-weight:700;}
  .lm-cta{display:inline-flex;align-items:center;gap:.6rem;background:#10B981;color:#000;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:.95rem;padding:.95rem 2rem;border-radius:4px;text-decoration:none;box-shadow:0 0 28px rgba(16,185,129,.3);transition:all .2s;animation:glowPulse 2.5s ease-in-out infinite;}
  @keyframes glowPulse{0%,100%{box-shadow:0 0 28px rgba(16,185,129,.3);}50%{box-shadow:0 0 50px rgba(16,185,129,.6);}}
  .lm-cta:hover{background:#059669;transform:translateY(-2px);}
  .lm-right{flex-shrink:0;}
  .lm-terminal{background:#000;border:1px solid rgba(16,185,129,.22);border-radius:6px;padding:1.4rem;width:290px;font-family:'JetBrains Mono',monospace;}
  .lm-tbar{display:flex;gap:5px;margin-bottom:1rem;}
  .lm-tdot{width:10px;height:10px;border-radius:50%;}
  .lm-tline{font-size:.75rem;line-height:1.9;color:#6b7280;}
  .lm-tline .g{color:#10B981;}.lm-tline .c{color:#06B6D4;}.lm-tline .w{color:#F0FDF4;}
  @media(max-width:640px){.lm-right{display:none;}}
  </style>
  <div class="lm-banner">
    <div class="lm-scan"></div>
    <div class="lm-inner">
      <div class="lm-left">
        <div class="lm-etiqueta">// FREE_RESOURCE — SIN REGISTRO</div>
        <h2 class="lm-titulo">50 <em>SuperPrompts</em> esenciales<br>— pack gratuito</h2>
        <p class="lm-desc">Los prompts más efectivos para productividad, marketing, programación y negocios. Copia y pega directamente.</p>
        <ul class="lm-checks">
          <li>12 prompts de productividad</li>
          <li>13 prompts de marketing y ventas</li>
          <li>13 prompts de programación</li>
          <li>12 prompts de negocios</li>
        </ul>
        <a href="<?php echo esc_url(get_bloginfo('url')); ?>/prompts-gratis" class="lm-cta">$ get_prompts --free --count=50 →</a>
      </div>
      <div class="lm-right">
        <div class="lm-terminal">
          <div class="lm-tbar"><span class="lm-tdot" style="background:#FF5F57"></span><span class="lm-tdot" style="background:#FEBC2E"></span><span class="lm-tdot" style="background:#28C840"></span></div>
          <div class="lm-tline"><span class="g">$</span> <span class="c">cat</span> <span class="w">prompts-gratis.txt</span></div>
          <div class="lm-tline"><span class="g">✓</span> <span class="w">#001 Daily Review</span></div>
          <div class="lm-tline"><span class="g">✓</span> <span class="w">#013 ICP Definition</span></div>
          <div class="lm-tline"><span class="g">✓</span> <span class="w">#026 Code Review Pro</span></div>
          <div class="lm-tline"><span class="g">✓</span> <span class="w">#039 Business Canvas</span></div>
          <div class="lm-tline" style="margin-top:.3rem;color:#10B981;font-weight:700;">50 prompts encontrados ✓</div>
        </div>
      </div>
    </div>
  </div>
  <section id="categorias"><div class="container">
    <div class="section-header reveal"><span class="section-tag">explorar por tema</span><h2 class="section-title">¿Para qué <span class="hl">necesitas</span> el prompt?</h2></div>
    <div class="cat-grid">
      <?php
      $cat_data = [
        ['tag'=>'trabajo.exe','title'=>'Productividad','desc'=>'Emails, informes, reuniones y todo lo que consume horas.','ex1'=>'Resumir reunión en 5 puntos','ex2'=>'Escribir email difícil','slug'=>'productividad'],
        ['tag'=>'marketing.js','title'=>'Marketing','desc'=>'Posts virales, copies de venta y campañas completas.','ex1'=>'Post viral Instagram','ex2'=>'Copy landing page','slug'=>'marketing'],
        ['tag'=>'code.py','title'=>'Programación','desc'=>'Explica código, corrige bugs y aprende cualquier lenguaje.','ex1'=>'Explica este código','ex2'=>'Encuentra el bug','slug'=>'programacion'],
        ['tag'=>'negocio.sh','title'=>'Negocios','desc'=>'Valida ideas, crea planes y escala tu empresa con IA.','ex1'=>'Valida mi idea','ex2'=>'Plan de negocio','slug'=>'negocios'],
      ];
      $blog_url = esc_url(get_bloginfo('url'));
      foreach($cat_data as $cat):
        $cat_obj = get_category_by_slug($cat['slug']);
        $link = $cat_obj ? esc_url(get_category_link($cat_obj->term_id)) : $blog_url.'/blog/?cat='.$cat['slug'];
      ?>
      <a href="<?php echo $link; ?>" class="cat-card reveal stagger" style="text-decoration:none;display:block;">
        <span class="cat-tag"><?php echo esc_html($cat['tag']); ?></span>
        <div class="cat-title"><?php echo esc_html($cat['title']); ?></div>
        <div class="cat-desc"><?php echo esc_html($cat['desc']); ?></div>
        <div class="cat-examples">
          <span class="cat-ex"><?php echo esc_html($cat['ex1']); ?></span>
          <span class="cat-ex"><?php echo esc_html($cat['ex2']); ?></span>
        </div>
      </a>
      <?php endforeach; ?>
    </div>
  </div></section>
  <section id="articulos" style="background:var(--bg2);"><div class="container">
    <div class="section-header reveal"><span class="section-tag">lo último</span><h2 class="section-title">Prompts <span class="hl">recientes</span></h2></div>
    <div class="articles-grid">
    <?php
    $posts = get_posts(['numberposts'=>3,'post_status'=>'publish']);
    $emojis=['💬','⚡','🎯'];
    foreach($posts as $i=>$p):
      $url=get_permalink($p->ID);
      $cats=get_the_category($p->ID);
      $cat=$cats?$cats[0]->name:'Prompts';
    ?>
      <a href="<?php echo esc_url($url);?>" class="article-card reveal stagger">
        <div class="article-img"><?php echo $emojis[$i%3];?></div>
        <div class="article-body">
          <div class="article-cat"><?php echo esc_html($cat);?></div>
          <div class="article-title"><?php echo esc_html($p->post_title);?></div>
          <div class="article-meta"><span><?php echo get_the_date('d M',$p->ID);?></span></div>
        </div>
      </a>
    <?php endforeach;?>
    </div>
  </div></section>
  <section id="newsletter"><div class="container"><div class="newsletter-inner reveal">
    <div class="nl-terminal">$ iniciando_subscripcion --tipo=gratuita --frecuencia=diaria</div>
    <h2 class="nl-title">1 prompt nuevo<br><span style="color:var(--green)">cada día</span> en tu email</h2>
    <p class="nl-sub">El prompt más útil de la semana con ejemplos reales. Gratis.</p>
    <form class="nl-form" id="nl-form-sp"><input type="email" id="nl-email-sp" placeholder="tu@email.com" required><button type="submit" id="nl-btn-sp">./suscribir</button></form>
    <p class="nl-note" id="nl-msg-sp">// sin spam · baja cuando quieras · 100% gratis</p>
  </div></div></section>
  <footer><div class="footer-inner">
    <a href="#" class="footer-logo">[SuperPrompts]</a>
    <ul class="footer-links">
      <li><a href="<?php echo esc_url(get_bloginfo('url'));?>/sobre-nosotros">about.md</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url'));?>/politica-de-privacidad">privacy.txt</a></li>
      <li><a href="<?php echo esc_url(get_bloginfo('url'));?>/contacto">contact.sh</a></li>
    </ul>
    <p class="footer-copy">// © <?php echo date('Y');?> superprompts.es</p>
  </div></footer>
  <?php wp_footer();?>
  <script>
    const nav=document.getElementById('navbar');
    window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>50);},{passive:true});
    const m=document.getElementById('matrix');
    const chars='abcdefghijklmnopqrstuvwxyz0123456789@#$%&*';
    for(let i=0;i<25;i++){const c=document.createElement('div');c.className='matrix-col';c.style.left=(i*4)+'%';c.style.animationDuration=(Math.random()*8+6)+'s';c.style.animationDelay=(Math.random()*5)+'s';let t='';for(let j=0;j<30;j++)t+=chars[Math.floor(Math.random()*chars.length)]+'\n';c.textContent=t;m.appendChild(c);}
    const cmds=[{cmd:'get_prompt --cat="marketing"',out:'✓ Cargando 47 prompts...'},{cmd:'search "email profesional"',out:'✓ 12 resultados encontrados.'},{cmd:'copy_prompt --id=viral_post',out:'✓ Prompt copiado. ¡Listo para usar!'}];
    let ci=0,ci2=0,phase='cmd';
    const cmdEl=document.getElementById('typed-cmd'),outEl=document.getElementById('typed-output');
    function typeNext(){const c=cmds[ci%cmds.length];if(phase==='cmd'){if(ci2<c.cmd.length){cmdEl.textContent+=c.cmd[ci2++];setTimeout(typeNext,60+Math.random()*40);}else{phase='output';setTimeout(typeNext,500);}}else{outEl.textContent=c.out;setTimeout(()=>{cmdEl.textContent='';outEl.textContent='';ci++;ci2=0;phase='cmd';setTimeout(typeNext,300);},2000);}}
    setTimeout(typeNext,1500);
    const obs=new IntersectionObserver(e=>{e.forEach(el=>{if(el.isIntersecting){el.target.classList.add('visible');obs.unobserve(el.target);}});},{threshold:.1});
    document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
    const cObs=new IntersectionObserver(e=>{e.forEach(entry=>{if(!entry.isIntersecting)return;const el=entry.target,target=+el.dataset.count;let cur=0;const step=target/(1500/16);const t=setInterval(()=>{cur=Math.min(cur+step,target);el.textContent=target>=1000?Math.floor(cur).toLocaleString('es')+'+':Math.floor(cur)+'+';if(cur>=target)clearInterval(t);},16);cObs.unobserve(el);});},{threshold:.5});
    document.querySelectorAll('.stat-num').forEach(el=>cObs.observe(el));
    document.getElementById('nl-form-sp').addEventListener('submit',async function(e){
      e.preventDefault();
      var btn=document.getElementById('nl-btn-sp'),msg=document.getElementById('nl-msg-sp'),email=document.getElementById('nl-email-sp').value.trim();
      btn.textContent='ejecutando...';btn.disabled=true;
      try{
        var r=await fetch('<?php echo esc_url(rest_url("newsletter/v1/subscribe")); ?>',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,site:'superprompts'})});
        var d=await r.json();
        if(d.success){btn.textContent='✓ suscrito';btn.style.background='#22c55e';document.getElementById('nl-email-sp').value='';}
        else{btn.textContent='// error - reintentar';btn.disabled=false;}
        msg.textContent=d.message||msg.textContent;
      }catch(err){btn.textContent='./reintentar';btn.disabled=false;}
    });
  </script>
</body>
</html>
