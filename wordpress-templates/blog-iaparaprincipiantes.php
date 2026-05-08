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
function iablog_img($id){$c=get_post_field('post_content',$id);preg_match('/<img[^>]+src=["\']([^"\']+)["\']/',$c,$m);return $m[1]??'';}
function iablog_rt($id){return max(1,ceil(str_word_count(strip_tags(get_post_field('post_content',$id)))/200));}
?><!DOCTYPE html><html lang="es"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title><?php echo $s?'Búsqueda: '.esc_html($s).' — ':($cat_id?single_cat_title('',false).' — ':''); ?>Blog IA para Principiantes</title>
<meta name="description" content="Artículos sobre inteligencia artificial en español. Tutoriales, herramientas y guías para aprender IA desde cero.">
<?php wp_head();?>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{--bg:#0f172a;--bg2:#1e293b;--bg3:#263148;--blue:#3b82f6;--blue2:#2563eb;--purple:#8b5cf6;--text:#e2e8f0;--muted:#94a3b8;--border:#334155;}
html{scroll-behavior:smooth;}body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh;}a{color:inherit;text-decoration:none;}
/* NAV */
nav{position:sticky;top:0;z-index:100;background:rgba(15,23,42,.96);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:64px;}
.nav-logo{font-family:'Space Grotesk',sans-serif;font-weight:800;font-size:1.05rem;display:flex;align-items:center;gap:.4rem;}
.nav-logo span{color:var(--blue);}
.nav-links{display:flex;gap:1.5rem;list-style:none;}
.nav-links a{font-size:.84rem;color:var(--muted);transition:color .2s;}
.nav-links a:hover,.nav-links a.active{color:var(--blue);}
.nav-cta{background:var(--blue);color:#fff;padding:.42rem 1rem;border-radius:6px;font-size:.84rem;font-weight:600;}
/* HERO */
.hero{background:linear-gradient(160deg,#1e293b 0%,#0f172a 60%,#13072e 100%);padding:4rem 2rem 3rem;text-align:center;border-bottom:1px solid var(--border);position:relative;overflow:hidden;}
.hero::after{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 60% 40% at 50% 60%,rgba(59,130,246,.07),transparent);pointer-events:none;}
.hero-badge{display:inline-flex;align-items:center;gap:.4rem;background:rgba(59,130,246,.1);border:1px solid rgba(59,130,246,.2);color:var(--blue);padding:.35rem 1rem;border-radius:20px;font-size:.76rem;font-weight:600;margin-bottom:1.2rem;}
.hero h1{font-family:'Space Grotesk',sans-serif;font-size:clamp(1.8rem,4vw,2.8rem);font-weight:800;line-height:1.2;margin-bottom:.75rem;}
.hero h1 em{color:var(--blue);font-style:normal;}
.hero p{color:var(--muted);font-size:.95rem;margin-bottom:2rem;max-width:500px;margin-left:auto;margin-right:auto;}
.search-wrap{display:flex;gap:.5rem;max-width:460px;margin:0 auto 2rem;}
.search-wrap input{flex:1;background:rgba(255,255,255,.05);border:1px solid var(--border);color:var(--text);padding:.7rem 1rem;border-radius:8px;font-size:.88rem;outline:none;transition:border .2s;}
.search-wrap input::placeholder{color:var(--muted);}
.search-wrap input:focus{border-color:var(--blue);}
.search-wrap button{background:var(--blue);color:#fff;border:none;padding:.7rem 1.2rem;border-radius:8px;cursor:pointer;font-weight:600;white-space:nowrap;}
.hero-stats{display:flex;justify-content:center;gap:3rem;}
.hs .n{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;color:var(--blue);}
.hs .l{font-size:.75rem;color:var(--muted);margin-top:.1rem;}
/* CATS */
.cats-bar{background:var(--bg2);border-bottom:1px solid var(--border);padding:.1rem 2rem;overflow-x:auto;white-space:nowrap;}
.cats-bar::-webkit-scrollbar{display:none;}
.cats-bar a{display:inline-flex;align-items:center;gap:.4rem;margin:.6rem .15rem;padding:.42rem .9rem;border-radius:6px;font-size:.8rem;font-weight:500;color:var(--muted);border:1px solid transparent;transition:all .2s;}
.cats-bar a:hover{color:var(--text);background:var(--bg3);}
.cats-bar a.on{background:rgba(59,130,246,.12);color:var(--blue);border-color:rgba(59,130,246,.25);}
.cat-count{font-size:.68rem;opacity:.6;}
/* MAIN */
.main{max-width:1220px;margin:0 auto;padding:2.5rem 1.5rem;}
.results-info{font-size:.85rem;color:var(--muted);margin-bottom:1.5rem;}
.results-info strong{color:var(--text);}
/* GRID */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:1.5rem;margin-bottom:2.5rem;}
/* CARD */
.card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;overflow:hidden;display:flex;flex-direction:column;transition:all .3s;cursor:pointer;}
.card:hover{border-color:rgba(59,130,246,.45);transform:translateY(-5px);box-shadow:0 16px 48px rgba(0,0,0,.5);}
.card-img{height:185px;overflow:hidden;position:relative;flex-shrink:0;}
.card-img img{width:100%;height:100%;object-fit:cover;transition:transform .4s;}
.card:hover .card-img img{transform:scale(1.06);}
.card-img-ph{height:100%;display:flex;align-items:center;justify-content:center;font-size:3rem;}
.card-img-ph.g0{background:linear-gradient(135deg,rgba(59,130,246,.2),rgba(139,92,246,.1));}
.card-img-ph.g1{background:linear-gradient(135deg,rgba(139,92,246,.2),rgba(59,130,246,.1));}
.card-img-ph.g2{background:linear-gradient(135deg,rgba(16,185,129,.15),rgba(59,130,246,.1));}
.card-img-ph.g3{background:linear-gradient(135deg,rgba(249,115,22,.15),rgba(139,92,246,.1));}
.card-body{padding:1.25rem;flex:1;display:flex;flex-direction:column;gap:.6rem;}
.card-top{display:flex;align-items:center;gap:.6rem;}
.card-cat{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--blue);background:rgba(59,130,246,.1);padding:.18rem .55rem;border-radius:4px;}
.card-date{font-size:.74rem;color:var(--muted);}
.card-title{font-family:'Space Grotesk',sans-serif;font-size:.98rem;font-weight:700;line-height:1.4;color:var(--text);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.card-excerpt{font-size:.8rem;color:var(--muted);line-height:1.65;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}
.card-foot{display:flex;justify-content:space-between;align-items:center;padding-top:.75rem;border-top:1px solid var(--border);}
.rt{font-size:.73rem;color:var(--muted);}
.rl{display:inline-flex;align-items:center;gap:.25rem;font-size:.78rem;font-weight:600;color:var(--blue);transition:gap .2s;}
.card:hover .rl{gap:.5rem;}
/* NO POSTS */
.empty{text-align:center;padding:5rem 1rem;color:var(--muted);}
.empty .ico{font-size:3.5rem;margin-bottom:1rem;}
.empty h3{font-size:1.1rem;color:var(--text);margin-bottom:.5rem;}
/* PAGINATION */
.pagi{display:flex;justify-content:center;gap:.4rem;flex-wrap:wrap;}
.pagi .page-numbers{padding:.5rem .9rem;border-radius:6px;border:1px solid var(--border);color:var(--muted);font-size:.83rem;transition:all .2s;}
.pagi .page-numbers:hover,.pagi .page-numbers.current{background:rgba(59,130,246,.12);color:var(--blue);border-color:rgba(59,130,246,.3);}
.pagi .page-numbers.dots{border:none;}
/* FOOTER */
footer{background:var(--bg2);border-top:1px solid var(--border);padding:1.75rem 2rem;margin-top:2rem;}
.fi{max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:1rem;}
.fl{font-family:'Space Grotesk',sans-serif;font-weight:800;font-size:.95rem;}
.fl span{color:var(--blue);}
.flinks{display:flex;gap:1.5rem;list-style:none;}
.flinks a{font-size:.8rem;color:var(--muted);}
.flinks a:hover{color:var(--blue);}
.fc{font-size:.76rem;color:#475569;}
@media(max-width:768px){.nav-links,.nav-cta{display:none;}.grid{grid-template-columns:1fr;}.hero-stats{gap:1.5rem;}}
</style></head><body>
<nav>
  <a href="<?php echo esc_url(home_url('/')); ?>" class="nav-logo">🤖 IA para <span>Principiantes</span></a>
  <ul class="nav-links">
    <li><a href="<?php echo esc_url(home_url('/')); ?>">Inicio</a></li>
    <li><a href="<?php echo esc_url(home_url('/blog')); ?>" class="active">Blog</a></li>
    <li><a href="<?php echo esc_url(home_url('/kit-starter')); ?>">Kit Gratis 🎁</a></li>
    <li><a href="<?php echo esc_url(home_url('/contacto')); ?>">Contacto</a></li>
  </ul>
  <a href="<?php echo esc_url(home_url('/kit-starter')); ?>" class="nav-cta">Kit Gratis 🎁</a>
</nav>

<div class="hero">
  <div class="hero-badge">📚 <?php echo number_format($total); ?> artículos publicados</div>
  <h1>Aprende <em>Inteligencia Artificial</em><br>desde cero, en español</h1>
  <p>Herramientas gratuitas, tutoriales paso a paso y guías para ganar dinero con IA.</p>
  <form class="search-wrap" method="get" action="<?php echo esc_url(home_url('/blog')); ?>">
    <input type="text" name="s" placeholder="Buscar artículos de IA…" value="<?php echo esc_attr($s); ?>">
    <button type="submit">🔍 Buscar</button>
  </form>
  <div class="hero-stats">
    <div class="hs"><div class="n"><?php echo number_format($total); ?></div><div class="l">Artículos</div></div>
    <div class="hs"><div class="n"><?php echo count($cats)+1; ?></div><div class="l">Categorías</div></div>
    <div class="hs"><div class="n">100%</div><div class="l">Gratuito</div></div>
  </div>
</div>

<div class="cats-bar">
  <a href="<?php echo esc_url(home_url('/blog')); ?>" class="<?php echo !$cat_id&&!$s?'on':''; ?>">Todos <?php if(!$cat_id&&!$s):?><span class="cat-count">(<?php echo $total;?>)</span><?php endif;?></a>
  <?php foreach($cats as $c):?>
  <a href="<?php echo esc_url(get_category_link($c->term_id)); ?>" class="<?php echo $cat_id==$c->term_id?'on':''; ?>">
    <?php echo esc_html($c->name);?> <span class="cat-count">(<?php echo $c->count;?>)</span>
  </a>
  <?php endforeach;?>
</div>

<div class="main">
  <?php if($s):?><p class="results-info">Resultados para "<strong><?php echo esc_html($s);?></strong>" — <?php echo $q->found_posts;?> artículo(s) encontrado(s) <a href="<?php echo esc_url(home_url('/blog'));?>" style="color:var(--blue);margin-left:.5rem">✕ Limpiar</a></p><?php endif;?>

  <?php if($q->have_posts()):?>
  <div class="grid">
  <?php $emojis=['🤖','⚡','💡','🚀','🎯','🧠','💻','🌟','🔥','📱','🛠️','✨','🎓','📊','🔮']; $gi=0;
  while($q->have_posts()):$q->the_post();
    $pid=get_the_ID(); $img=iablog_img($pid);
    $pcat=get_the_category($pid); $cn=$pcat?$pcat[0]->name:'IA'; $cl=$pcat?get_category_link($pcat[0]->term_id):home_url('/blog');
    $rt=iablog_rt($pid); $e=$emojis[$gi%count($emojis)]; $g='g'.($gi%4);
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
        <span class="rl">Leer artículo →</span>
      </div>
    </div>
  </article>
  <?php $gi++;endwhile;wp_reset_postdata();?>
  </div>
  <div class="pagi"><?php echo paginate_links(['base'=>str_replace(999999,'%#%',esc_url(get_pagenum_link(999999))),'format'=>'?paged=%#%','current'=>$paged,'total'=>$q->max_num_pages,'prev_text'=>'← Anterior','next_text'=>'Siguiente →']);?></div>
  <?php else:?>
  <div class="empty"><div class="ico">📭</div><h3>No se encontraron artículos</h3><p>Prueba con otra búsqueda o <a href="<?php echo esc_url(home_url('/blog'));?>" style="color:var(--blue)">vuelve al blog</a>.</p></div>
  <?php endif;?>
</div>

<footer><div class="fi">
  <a href="<?php echo esc_url(home_url('/'));?>" class="fl">IA para <span>Principiantes</span></a>
  <ul class="flinks">
    <li><a href="<?php echo esc_url(home_url('/politica-de-privacidad'));?>">Privacidad</a></li>
    <li><a href="<?php echo esc_url(home_url('/aviso-legal'));?>">Aviso Legal</a></li>
    <li><a href="<?php echo esc_url(home_url('/contacto'));?>">Contacto</a></li>
  </ul>
  <p class="fc">© <?php echo date('Y');?> IAparaPrincipiantes.es</p>
</div></footer>
<?php wp_footer();?>
</body></html>
