<?php
$paged=$max=1;
if(get_query_var('paged'))$paged=get_query_var('paged');
$cat_id=isset($_GET['cat'])?intval($_GET['cat']):0;
$s=isset($_GET['s'])?sanitize_text_field($_GET['s']):'';
$args=['post_type'=>'post','post_status'=>'publish','posts_per_page'=>12,'paged'=>$paged];
if($cat_id)$args['cat']=$cat_id;
if($s)$args['s']=$s;
$q=new WP_Query($args);
$total=wp_count_posts()->publish;
$cats=get_categories(['hide_empty'=>true,'orderby'=>'count','order'=>'DESC','number'=>8]);
function gcblog_img($id){$c=get_post_field('post_content',$id);preg_match('/<img[^>]+src=["\']([^"\']+)["\']/',$c,$m);return $m[1]??'';}
function gcblog_rt($id){return max(1,ceil(str_word_count(strip_tags(get_post_field('post_content',$id)))/200));}
?><!DOCTYPE html><html lang="es"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title><?php echo $s?'Búsqueda: '.esc_html($s).' — ':($cat_id?single_cat_title('',false).' — ':''); ?>Blog Guía Claude — Domina Claude AI</title>
<meta name="description" content="Guías completas, trucos avanzados y casos de uso reales de Claude AI. Aprende a sacarle el máximo partido en español.">
<?php wp_head();?>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{--bg:#0c0a07;--bg2:#161310;--bg3:#1e1a14;--orange:#f97316;--orange2:#ea6c0b;--amber:#fbbf24;--red:#ef4444;--text:#fef3e2;--muted:#9ca3af;--border:#2a2318;--warm:#e8d5b7;}
html{scroll-behavior:smooth;}body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh;}a{color:inherit;text-decoration:none;}
/* TOP BAR */
.topbar{background:var(--orange);padding:.35rem 2rem;text-align:center;font-size:.78rem;font-weight:600;color:#000;letter-spacing:.03em;}
.topbar a{color:#000;text-decoration:underline;}
/* NAV */
nav{position:sticky;top:0;z-index:100;background:rgba(12,10,7,.97);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:64px;}
.nav-logo{font-family:'Playfair Display',serif;font-weight:900;font-size:1.1rem;display:flex;align-items:center;gap:.3rem;}
.nav-logo em{color:var(--orange);font-style:normal;}
.nav-links{display:flex;gap:2rem;list-style:none;}
.nav-links a{font-size:.84rem;color:var(--muted);letter-spacing:.02em;transition:color .2s;}
.nav-links a:hover,.nav-links a.active{color:var(--orange);}
.nav-cta{background:var(--orange);color:#000;padding:.42rem 1.1rem;border-radius:4px;font-size:.83rem;font-weight:700;transition:background .2s;}
.nav-cta:hover{background:var(--amber);}
/* HERO */
.hero{position:relative;overflow:hidden;background:var(--bg2);padding:4rem 2rem 0;border-bottom:1px solid var(--border);}
.hero::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--orange),var(--amber),var(--orange));}
.hero-inner{max-width:900px;margin:0 auto;display:grid;grid-template-columns:1fr auto;gap:3rem;align-items:end;}
.hero-left{padding-bottom:3rem;}
.hero-eyebrow{display:inline-flex;align-items:center;gap:.5rem;font-size:.74rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--orange);margin-bottom:1.2rem;}
.hero-eyebrow::before{content:'';width:24px;height:2px;background:var(--orange);}
.hero h1{font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,3.5rem);font-weight:900;line-height:1.1;margin-bottom:1rem;color:var(--text);}
.hero h1 span{color:var(--orange);position:relative;}
.hero h1 span::after{content:'';position:absolute;bottom:-4px;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--orange),var(--amber));border-radius:2px;}
.hero p{color:var(--muted);font-size:.96rem;line-height:1.75;max-width:540px;margin-bottom:2rem;}
.hero-actions{display:flex;gap:.75rem;flex-wrap:wrap;}
.btn-primary{background:var(--orange);color:#000;padding:.65rem 1.5rem;border-radius:4px;font-weight:700;font-size:.88rem;transition:all .2s;}
.btn-primary:hover{background:var(--amber);transform:translateY(-1px);}
.btn-ghost{border:1px solid var(--border);color:var(--muted);padding:.65rem 1.5rem;border-radius:4px;font-size:.88rem;transition:all .2s;}
.btn-ghost:hover{border-color:rgba(249,115,22,.3);color:var(--text);}
.hero-right{display:flex;flex-direction:column;gap:.1rem;padding-bottom:3rem;}
.issue-badge{background:var(--bg3);border:1px solid var(--border);border-radius:6px;padding:1.25rem;min-width:180px;text-align:center;}
.issue-num{font-family:'Playfair Display',serif;font-size:2.5rem;font-weight:900;color:var(--orange);}
.issue-label{font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-top:.2rem;}
.issue-sub{font-size:.76rem;color:var(--warm);margin-top:.6rem;}
/* SEARCH STRIP */
.search-strip{background:var(--bg3);border-bottom:1px solid var(--border);padding:.75rem 2rem;}
.search-form{max-width:600px;margin:0 auto;display:flex;gap:.5rem;}
.search-form input{flex:1;background:var(--bg2);border:1px solid var(--border);color:var(--text);padding:.62rem 1rem;border-radius:4px;font-size:.86rem;outline:none;transition:border .2s;}
.search-form input::placeholder{color:var(--muted);}
.search-form input:focus{border-color:rgba(249,115,22,.35);}
.search-form button{background:var(--orange);color:#000;border:none;padding:.62rem 1.2rem;border-radius:4px;cursor:pointer;font-weight:700;font-size:.84rem;white-space:nowrap;transition:background .2s;}
.search-form button:hover{background:var(--amber);}
/* CATS */
.cats-bar{background:var(--bg);border-bottom:1px solid var(--border);padding:.1rem 2rem;overflow-x:auto;white-space:nowrap;}
.cats-bar::-webkit-scrollbar{height:2px;background:var(--bg);}
.cats-bar::-webkit-scrollbar-thumb{background:var(--border);}
.cats-bar a{display:inline-block;margin:.55rem .2rem;padding:.38rem .9rem;border-radius:3px;font-size:.79rem;font-weight:600;color:var(--muted);letter-spacing:.03em;border-bottom:2px solid transparent;transition:all .2s;}
.cats-bar a:hover{color:var(--text);}
.cats-bar a.on{color:var(--orange);border-bottom-color:var(--orange);}
.cat-count{font-size:.68rem;opacity:.5;margin-left:.2rem;}
/* MAIN */
.main{max-width:1240px;margin:0 auto;padding:2.5rem 1.5rem;}
.results-info{font-size:.84rem;color:var(--muted);margin-bottom:1.5rem;}
.results-info strong{color:var(--text);}
/* LAYOUT: featured + grid */
.content-layout{display:grid;grid-template-columns:2fr 1fr;gap:2rem;margin-bottom:2.5rem;}
.primary-col{}
.sidebar-col{}
/* FEATURED POST */
.featured-post{margin-bottom:1.75rem;}
.featured-post .card{display:grid;grid-template-columns:1fr 1fr;border-radius:8px;overflow:hidden;border:1px solid var(--border);transition:all .3s;cursor:pointer;background:var(--bg2);}
.featured-post .card:hover{border-color:rgba(249,115,22,.35);box-shadow:0 20px 60px rgba(0,0,0,.5);}
.featured-post .card-img{height:260px;overflow:hidden;}
.featured-post .card-img img{width:100%;height:100%;object-fit:cover;transition:transform .5s;}
.featured-post .card:hover .card-img img{transform:scale(1.07);}
.featured-post .card-img-ph{height:100%;display:flex;align-items:center;justify-content:center;font-size:4rem;background:linear-gradient(135deg,#1e1a14,#2a1f10);}
.featured-post .card-body{padding:2rem;display:flex;flex-direction:column;justify-content:center;gap:.8rem;}
.featured-tag{display:inline-flex;align-items:center;gap:.4rem;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--orange);}
.featured-tag::before{content:'';width:16px;height:2px;background:var(--orange);}
.featured-title{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:800;line-height:1.35;color:var(--text);}
.featured-excerpt{font-size:.84rem;color:var(--muted);line-height:1.7;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}
.featured-meta{display:flex;justify-content:space-between;align-items:center;}
.featured-date{font-size:.76rem;color:var(--muted);}
.featured-rl{font-size:.82rem;font-weight:700;color:var(--orange);transition:gap .2s;display:inline-flex;align-items:center;gap:.3rem;}
/* MINI GRID */
.mini-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:6px;overflow:hidden;display:flex;flex-direction:column;transition:all .3s;cursor:pointer;}
.card:hover{border-color:rgba(249,115,22,.3);transform:translateY(-3px);box-shadow:0 12px 40px rgba(0,0,0,.4);}
.card-img{height:150px;overflow:hidden;flex-shrink:0;position:relative;}
.card-img img{width:100%;height:100%;object-fit:cover;transition:transform .4s;}
.card:hover .card-img img{transform:scale(1.08);}
.card-img-ph{height:100%;display:flex;align-items:center;justify-content:center;font-size:2.4rem;}
.card-img-ph.g0{background:linear-gradient(135deg,#1a1208,#261a0a);}
.card-img-ph.g1{background:linear-gradient(135deg,#100f0c,#1e1512);}
.card-img-ph.g2{background:linear-gradient(135deg,#0e1218,#1a1208);}
.card-img-ph.g3{background:linear-gradient(135deg,#120a0a,#1e1206);}
.card-body{padding:1rem;flex:1;display:flex;flex-direction:column;gap:.45rem;}
.card-top{display:flex;align-items:center;gap:.5rem;}
.card-cat{font-size:.67rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--orange);background:rgba(249,115,22,.08);padding:.15rem .45rem;border-radius:3px;}
.card-date{font-size:.72rem;color:var(--muted);}
.card-title{font-family:'Playfair Display',serif;font-size:.88rem;font-weight:700;line-height:1.4;color:var(--text);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.card-excerpt{font-size:.78rem;color:var(--muted);line-height:1.6;flex:1;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.card-foot{display:flex;justify-content:space-between;align-items:center;padding-top:.6rem;border-top:1px solid var(--border);}
.rt{font-size:.7rem;color:var(--muted);}
.rl{font-size:.76rem;font-weight:700;color:var(--orange);display:inline-flex;align-items:center;gap:.25rem;transition:gap .2s;}
.card:hover .rl{gap:.45rem;}
/* SIDEBAR */
.sidebar-sticky{position:sticky;top:80px;}
.sidebar-section{background:var(--bg2);border:1px solid var(--border);border-radius:6px;overflow:hidden;margin-bottom:1.5rem;}
.sidebar-head{padding:.9rem 1.2rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:.5rem;}
.sidebar-head h3{font-family:'Playfair Display',serif;font-size:.95rem;font-weight:800;color:var(--text);}
.sidebar-head::before{content:'';width:3px;height:18px;background:var(--orange);border-radius:2px;}
.sidebar-list{list-style:none;}
.sidebar-list li{border-bottom:1px solid var(--border);}
.sidebar-list li:last-child{border:none;}
.sidebar-list a{display:flex;align-items:flex-start;gap:.75rem;padding:.9rem 1.2rem;transition:background .2s;font-size:.82rem;line-height:1.5;color:var(--warm);}
.sidebar-list a:hover{background:var(--bg3);}
.sidebar-list .sn{font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:900;color:rgba(249,115,22,.25);min-width:28px;line-height:1;}
.sidebar-list .st{flex:1;}
.sidebar-list .st strong{display:block;color:var(--text);font-size:.82rem;margin-bottom:.1rem;}
.sidebar-list .sc{font-size:.71rem;color:var(--muted);}
.newsletter-box{background:linear-gradient(135deg,var(--bg2),#1a1308);border:1px solid rgba(249,115,22,.15);border-radius:6px;padding:1.5rem;text-align:center;}
.newsletter-box h4{font-family:'Playfair Display',serif;font-size:1rem;font-weight:800;margin-bottom:.5rem;}
.newsletter-box p{font-size:.78rem;color:var(--muted);margin-bottom:1rem;line-height:1.6;}
.nl-input{width:100%;background:var(--bg);border:1px solid var(--border);color:var(--text);padding:.62rem .9rem;border-radius:4px;font-size:.83rem;margin-bottom:.6rem;outline:none;}
.nl-input:focus{border-color:rgba(249,115,22,.3);}
.nl-btn{width:100%;background:var(--orange);color:#000;border:none;padding:.65rem;border-radius:4px;font-weight:700;font-size:.85rem;cursor:pointer;transition:background .2s;}
.nl-btn:hover{background:var(--amber);}
/* FULL GRID (when no featured) */
.full-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1.5rem;margin-bottom:2.5rem;}
/* EMPTY */
.empty{text-align:center;padding:5rem 1rem;color:var(--muted);}
.empty .ico{font-size:3rem;margin-bottom:1rem;}
.empty h3{font-family:'Playfair Display',serif;font-size:1.2rem;color:var(--text);margin-bottom:.5rem;}
/* PAGINATION */
.pagi{display:flex;justify-content:center;gap:.4rem;flex-wrap:wrap;}
.pagi .page-numbers{padding:.45rem .85rem;border-radius:4px;border:1px solid var(--border);color:var(--muted);font-size:.83rem;transition:all .2s;}
.pagi .page-numbers:hover,.pagi .page-numbers.current{background:rgba(249,115,22,.1);color:var(--orange);border-color:rgba(249,115,22,.25);}
.pagi .page-numbers.dots{border:none;}
/* FOOTER */
footer{background:var(--bg2);border-top:1px solid var(--border);padding:1.75rem 2rem;margin-top:2rem;}
.fi{max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:1rem;}
.fl{font-family:'Playfair Display',serif;font-weight:900;font-size:1rem;}
.fl em{color:var(--orange);font-style:normal;}
.flinks{display:flex;gap:1.5rem;list-style:none;}
.flinks a{font-size:.8rem;color:var(--muted);}
.flinks a:hover{color:var(--orange);}
.fc{font-size:.76rem;color:#374151;}
@media(max-width:1024px){.content-layout{grid-template-columns:1fr;}.sidebar-col{display:none;}}
@media(max-width:900px){.featured-post .card{grid-template-columns:1fr;}.hero-inner{grid-template-columns:1fr;}.hero-right{display:none;}}
@media(max-width:768px){.nav-links,.nav-cta{display:none;}.mini-grid{grid-template-columns:1fr;}.hero{padding:2.5rem 1.5rem 0;}}
</style></head><body>
<div class="topbar">Nueva guía: Cómo usar Claude Projects para negocios → <a href="<?php echo esc_url(home_url('/blog')); ?>">leer ahora</a></div>
<nav>
  <a href="<?php echo esc_url(home_url('/')); ?>" class="nav-logo">Guía <em>Claude</em></a>
  <ul class="nav-links">
    <li><a href="<?php echo esc_url(home_url('/')); ?>">Inicio</a></li>
    <li><a href="<?php echo esc_url(home_url('/blog')); ?>" class="active">Artículos</a></li>
    <li><a href="<?php echo esc_url(home_url('/recursos-gratis')); ?>">Recursos 🎁</a></li>
    <li><a href="<?php echo esc_url(home_url('/contacto')); ?>">Contacto</a></li>
  </ul>
  <a href="<?php echo esc_url(home_url('/recursos-gratis')); ?>" class="nav-cta">40 Plantillas 🎁</a>
</nav>

<div class="hero">
  <div class="hero-inner">
    <div class="hero-left">
      <div class="hero-eyebrow">La guía definitiva de Claude AI</div>
      <h1>Domina <span>Claude AI</span><br>en español</h1>
      <p>Guías detalladas, casos de uso reales y técnicas avanzadas para sacarle el máximo partido a Claude. <?php echo number_format($total); ?> artículos publicados.</p>
      <div class="hero-actions">
        <a href="#articulos" class="btn-primary">Ver artículos →</a>
        <a href="<?php echo esc_url(home_url('/')); ?>#newsletter" class="btn-ghost">Suscribirme gratis</a>
      </div>
    </div>
    <div class="hero-right">
      <div class="issue-badge">
        <div class="issue-num"><?php echo number_format($total); ?></div>
        <div class="issue-label">artículos</div>
        <div class="issue-sub">Actualizado hoy</div>
      </div>
    </div>
  </div>
</div>

<div class="search-strip">
  <form class="search-form" method="get" action="<?php echo esc_url(home_url('/blog')); ?>">
    <input type="text" name="s" placeholder="Buscar guías de Claude AI…" value="<?php echo esc_attr($s); ?>">
    <button type="submit">Buscar</button>
  </form>
</div>

<div class="cats-bar">
  <a href="<?php echo esc_url(home_url('/blog')); ?>" class="<?php echo !$cat_id&&!$s?'on':''; ?>">Todos<?php if(!$cat_id&&!$s):?><span class="cat-count">(<?php echo $total;?>)</span><?php endif;?></a>
  <?php foreach($cats as $c):?>
  <a href="<?php echo esc_url(get_category_link($c->term_id)); ?>" class="<?php echo $cat_id==$c->term_id?'on':''; ?>">
    <?php echo esc_html($c->name);?><span class="cat-count">(<?php echo $c->count;?>)</span>
  </a>
  <?php endforeach;?>
</div>

<div class="main" id="articulos">
  <?php if($s):?><p class="results-info">Resultados para "<strong><?php echo esc_html($s);?></strong>" — <?php echo $q->found_posts;?> artículo(s) <a href="<?php echo esc_url(home_url('/blog'));?>" style="color:var(--orange);margin-left:.5rem">✕ Limpiar búsqueda</a></p><?php endif;?>

  <?php if($q->have_posts()):
    $posts_data=[];
    while($q->have_posts()):$q->the_post();$posts_data[]=get_the_ID();endwhile;
    wp_reset_postdata();
    $query2=new WP_Query($args);
    $gi=0;
    $emojis=['🤖','⚡','💡','🚀','🎯','🧠','💻','🌟','🔥','📊','🔮','✨','🎓','🛠️','📈'];
  ?>

  <?php if(!$cat_id&&!$s&&$paged===1): // Magazine layout on main page ?>
  <div class="content-layout">
    <div class="primary-col">
      <!-- Featured post -->
      <div class="featured-post">
      <?php $query2->the_post(); $pid=get_the_ID(); $img=gcblog_img($pid);
        $pcat=get_the_category($pid); $cn=$pcat?$pcat[0]->name:'Claude AI'; $cl=$pcat?get_category_link($pcat[0]->term_id):home_url('/blog');
        $rt=gcblog_rt($pid);
      ?>
      <article class="card" onclick="location.href='<?php the_permalink();?>'">
        <div class="card-img">
          <?php if($img):?><img src="<?php echo esc_url($img);?>" alt="<?php the_title_attribute();?>" loading="lazy">
          <?php else:?><div class="card-img-ph"><?php echo $emojis[0];?></div><?php endif;?>
        </div>
        <div class="card-body">
          <div class="featured-tag"><?php echo esc_html($cn);?></div>
          <h2 class="featured-title"><a href="<?php the_permalink();?>"><?php the_title();?></a></h2>
          <p class="featured-excerpt"><?php echo wp_trim_words(get_the_excerpt()?:strip_tags(get_the_content()),30);?></p>
          <div class="featured-meta">
            <span class="featured-date"><?php echo get_the_date('d M Y');?> · <?php echo $rt;?> min</span>
            <span class="featured-rl">Leer guía →</span>
          </div>
        </div>
      </article>
      </div>
      <!-- Mini grid -->
      <div class="mini-grid">
      <?php $gi=1;while($query2->have_posts()&&$gi<5):$query2->the_post();
        $pid=get_the_ID(); $img=gcblog_img($pid);
        $pcat=get_the_category($pid); $cn=$pcat?$pcat[0]->name:'Claude AI'; $cl=$pcat?get_category_link($pcat[0]->term_id):home_url('/blog');
        $rt=gcblog_rt($pid); $e=$emojis[$gi%count($emojis)]; $g='g'.($gi%4);
      ?>
      <article class="card" onclick="location.href='<?php the_permalink();?>'">
        <div class="card-img">
          <?php if($img):?><img src="<?php echo esc_url($img);?>" alt="<?php the_title_attribute();?>" loading="lazy">
          <?php else:?><div class="card-img-ph <?php echo $g;?>"><?php echo $e;?></div><?php endif;?>
        </div>
        <div class="card-body">
          <div class="card-top">
            <a href="<?php echo esc_url($cl);?>" class="card-cat" onclick="event.stopPropagation()"><?php echo esc_html($cn);?></a>
            <span class="card-date"><?php echo get_the_date('d M');?></span>
          </div>
          <h2 class="card-title"><a href="<?php the_permalink();?>"><?php the_title();?></a></h2>
          <p class="card-excerpt"><?php echo wp_trim_words(get_the_excerpt()?:strip_tags(get_the_content()),16);?></p>
          <div class="card-foot">
            <span class="rt">⏱ <?php echo $rt;?> min</span>
            <span class="rl">Leer →</span>
          </div>
        </div>
      </article>
      <?php $gi++;endwhile;?>
      </div>
    </div><!-- /primary-col -->

    <div class="sidebar-col">
      <div class="sidebar-sticky">
        <?php $recent=new WP_Query(['post_status'=>'publish','posts_per_page'=>6,'offset'=>5]);?>
        <?php if($recent->have_posts()):?>
        <div class="sidebar-section">
          <div class="sidebar-head"><h3>Más artículos</h3></div>
          <ul class="sidebar-list">
          <?php $rn=1;while($recent->have_posts()):$recent->the_post();?>
          <li><a href="<?php the_permalink();?>">
            <span class="sn"><?php echo str_pad($rn,2,'0',STR_PAD_LEFT);?></span>
            <span class="st">
              <strong><?php the_title();?></strong>
              <span class="sc"><?php echo get_the_date('d M Y');?> · <?php echo gcblog_rt(get_the_ID());?> min</span>
            </span>
          </a></li>
          <?php $rn++;endwhile;wp_reset_postdata();?>
          </ul>
        </div>
        <?php endif;?>
        <div class="newsletter-box">
          <h4>✉️ Newsletter semanal</h4>
          <p>Recibe las mejores guías de Claude AI cada semana. Sin spam.</p>
          <a href="<?php echo esc_url(home_url('/')); ?>#newsletter">
            <input class="nl-input" type="email" placeholder="tu@email.com" disabled>
            <button class="nl-btn" onclick="window.location='<?php echo esc_url(home_url('/')); ?>#newsletter'">Suscribirme gratis</button>
          </a>
        </div>
      </div>
    </div>
  </div><!-- /content-layout -->

  <!-- Rest of posts -->
  <?php if($query2->have_posts()):?>
  <h3 style="font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:800;margin-bottom:1.25rem;color:var(--warm);display:flex;align-items:center;gap:.6rem;"><span style="width:20px;height:2px;background:var(--orange);display:inline-block"></span>Más guías</h3>
  <div class="full-grid">
  <?php while($query2->have_posts()):$query2->the_post();
    $pid=get_the_ID(); $img=gcblog_img($pid);
    $pcat=get_the_category($pid); $cn=$pcat?$pcat[0]->name:'Claude AI'; $cl=$pcat?get_category_link($pcat[0]->term_id):home_url('/blog');
    $rt=gcblog_rt($pid); $e=$emojis[$gi%count($emojis)]; $g='g'.($gi%4);
  ?>
  <article class="card" onclick="location.href='<?php the_permalink();?>'">
    <div class="card-img">
      <?php if($img):?><img src="<?php echo esc_url($img);?>" alt="<?php the_title_attribute();?>" loading="lazy">
      <?php else:?><div class="card-img-ph <?php echo $g;?>"><?php echo $e;?></div><?php endif;?>
    </div>
    <div class="card-body">
      <div class="card-top">
        <a href="<?php echo esc_url($cl);?>" class="card-cat" onclick="event.stopPropagation()"><?php echo esc_html($cn);?></a>
        <span class="card-date"><?php echo get_the_date('d M Y');?></span>
      </div>
      <h2 class="card-title"><a href="<?php the_permalink();?>"><?php the_title();?></a></h2>
      <p class="card-excerpt"><?php echo wp_trim_words(get_the_excerpt()?:strip_tags(get_the_content()),22);?></p>
      <div class="card-foot">
        <span class="rt">⏱ <?php echo $rt;?> min</span>
        <span class="rl">Leer guía →</span>
      </div>
    </div>
  </article>
  <?php $gi++;endwhile;wp_reset_postdata();?>
  </div>
  <?php endif;?>

  <?php else: // Category / search / paged — simple grid ?>
  <div class="full-grid">
  <?php while($query2->have_posts()):$query2->the_post();
    $pid=get_the_ID(); $img=gcblog_img($pid);
    $pcat=get_the_category($pid); $cn=$pcat?$pcat[0]->name:'Claude AI'; $cl=$pcat?get_category_link($pcat[0]->term_id):home_url('/blog');
    $rt=gcblog_rt($pid); $e=$emojis[$gi%count($emojis)]; $g='g'.($gi%4);
  ?>
  <article class="card" onclick="location.href='<?php the_permalink();?>'">
    <div class="card-img">
      <?php if($img):?><img src="<?php echo esc_url($img);?>" alt="<?php the_title_attribute();?>" loading="lazy">
      <?php else:?><div class="card-img-ph <?php echo $g;?>"><?php echo $e;?></div><?php endif;?>
    </div>
    <div class="card-body">
      <div class="card-top">
        <a href="<?php echo esc_url($cl);?>" class="card-cat" onclick="event.stopPropagation()"><?php echo esc_html($cn);?></a>
        <span class="card-date"><?php echo get_the_date('d M Y');?></span>
      </div>
      <h2 class="card-title"><a href="<?php the_permalink();?>"><?php the_title();?></a></h2>
      <p class="card-excerpt"><?php echo wp_trim_words(get_the_excerpt()?:strip_tags(get_the_content()),22);?></p>
      <div class="card-foot">
        <span class="rt">⏱ <?php echo $rt;?> min</span>
        <span class="rl">Leer guía →</span>
      </div>
    </div>
  </article>
  <?php $gi++;endwhile;wp_reset_postdata();?>
  </div>
  <?php endif;?>

  <div class="pagi"><?php echo paginate_links(['base'=>str_replace(999999,'%#%',esc_url(get_pagenum_link(999999))),'format'=>'?paged=%#%','current'=>$paged,'total'=>$q->max_num_pages,'prev_text'=>'← Anterior','next_text'=>'Siguiente →']);?></div>
  <?php else:?>
  <div class="empty"><div class="ico">📭</div><h3>No se encontraron artículos</h3><p>Prueba con otra búsqueda o <a href="<?php echo esc_url(home_url('/blog'));?>" style="color:var(--orange)">vuelve al blog</a>.</p></div>
  <?php endif;?>
</div>

<footer><div class="fi">
  <a href="<?php echo esc_url(home_url('/'));?>" class="fl">Guía <em>Claude</em></a>
  <ul class="flinks">
    <li><a href="<?php echo esc_url(home_url('/politica-de-privacidad'));?>">Privacidad</a></li>
    <li><a href="<?php echo esc_url(home_url('/aviso-legal'));?>">Aviso Legal</a></li>
    <li><a href="<?php echo esc_url(home_url('/contacto'));?>">Contacto</a></li>
  </ul>
  <p class="fc">© <?php echo date('Y');?> GuiaClaude.es</p>
</div></footer>
<?php wp_footer();?>
</body></html>
