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
function spblog_img($id){$c=get_post_field('post_content',$id);preg_match('/<img[^>]+src=["\']([^"\']+)["\']/',$c,$m);return $m[1]??'';}
function spblog_rt($id){return max(1,ceil(str_word_count(strip_tags(get_post_field('post_content',$id)))/200));}
$cat_icons=['productividad'=>'⚡','marketing'=>'📈','programacion'=>'💻','negocios'=>'💼','programación'=>'💻'];
?><!DOCTYPE html><html lang="es"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title><?php echo $s?'Búsqueda: '.esc_html($s).' — ':($cat_id?single_cat_title('',false).' — ':''); ?>Blog SuperPrompts — Prompts de IA</title>
<meta name="description" content="Los mejores prompts de inteligencia artificial para productividad, marketing, programación y negocios. Resultados reales, en español.">
<?php wp_head();?>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{--bg:#080f0a;--bg2:#0d1a10;--bg3:#112016;--green:#22c55e;--green2:#16a34a;--green3:#4ade80;--lime:#a3e635;--text:#d1fae5;--muted:#6b7280;--border:#1a2e1e;--term:#00ff41;}
html{scroll-behavior:smooth;}body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh;}a{color:inherit;text-decoration:none;}
/* SCANLINES EFFECT */
body::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.04) 2px,rgba(0,0,0,.04) 4px);pointer-events:none;z-index:9999;}
/* NAV */
nav{position:sticky;top:0;z-index:100;background:rgba(8,15,10,.97);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:64px;}
.nav-logo{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:1rem;display:flex;align-items:center;gap:.5rem;color:var(--term);}
.nav-logo .blink{animation:blink 1.2s step-end infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}
.nav-links{display:flex;gap:1.5rem;list-style:none;}
.nav-links a{font-size:.83rem;color:var(--muted);font-family:'JetBrains Mono',monospace;transition:color .2s;}
.nav-links a:hover,.nav-links a.active{color:var(--green);}
.nav-cta{background:transparent;color:var(--green);padding:.42rem 1rem;border-radius:6px;font-size:.83rem;font-weight:600;font-family:'JetBrains Mono',monospace;border:1px solid var(--green);transition:all .2s;}
.nav-cta:hover{background:rgba(34,197,94,.1);}
/* HERO */
.hero{position:relative;overflow:hidden;padding:4rem 2rem 3.5rem;text-align:center;border-bottom:1px solid var(--border);}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 30%,rgba(34,197,94,.06),transparent);}
.hero-terminal{display:inline-block;background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:.5rem 1.2rem;font-family:'JetBrains Mono',monospace;font-size:.8rem;color:var(--muted);margin-bottom:1.5rem;}
.hero-terminal .prompt{color:var(--green);}
.hero h1{font-size:clamp(1.9rem,4.5vw,3rem);font-weight:800;line-height:1.15;margin-bottom:.8rem;letter-spacing:-.02em;}
.hero h1 em{color:var(--green);font-style:normal;text-shadow:0 0 40px rgba(34,197,94,.25);}
.hero p{color:var(--muted);font-size:.95rem;max-width:520px;margin:0 auto 2rem;line-height:1.7;}
.search-wrap{display:flex;max-width:500px;margin:0 auto 2.5rem;border:1px solid var(--border);border-radius:8px;overflow:hidden;background:var(--bg2);transition:border .2s;}
.search-wrap:focus-within{border-color:rgba(34,197,94,.4);}
.search-prefix{font-family:'JetBrains Mono',monospace;color:var(--green);padding:.75rem 0 .75rem 1rem;font-size:.85rem;flex-shrink:0;}
.search-wrap input{flex:1;background:transparent;border:none;color:var(--text);padding:.75rem .5rem;font-size:.85rem;outline:none;font-family:'JetBrains Mono',monospace;}
.search-wrap input::placeholder{color:var(--muted);}
.search-wrap button{background:var(--green);color:#000;border:none;padding:.75rem 1.25rem;cursor:pointer;font-weight:700;font-family:'JetBrains Mono',monospace;font-size:.82rem;white-space:nowrap;transition:background .2s;}
.search-wrap button:hover{background:var(--green3);}
.hero-stats{display:flex;justify-content:center;gap:3rem;}
.hs .n{font-family:'JetBrains Mono',monospace;font-size:2.2rem;font-weight:700;color:var(--green);text-shadow:0 0 20px rgba(34,197,94,.3);}
.hs .l{font-size:.73rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-top:.2rem;}
/* CATS */
.cats-bar{background:var(--bg2);border-bottom:1px solid var(--border);padding:.1rem 2rem;overflow-x:auto;white-space:nowrap;}
.cats-bar::-webkit-scrollbar{height:3px;background:var(--bg);}
.cats-bar::-webkit-scrollbar-thumb{background:var(--border);}
.cats-bar a{display:inline-flex;align-items:center;gap:.4rem;margin:.5rem .15rem;padding:.4rem .9rem;border-radius:5px;font-size:.8rem;font-weight:500;color:var(--muted);font-family:'JetBrains Mono',monospace;border:1px solid transparent;transition:all .2s;}
.cats-bar a:hover{color:var(--text);background:var(--bg3);}
.cats-bar a.on{background:rgba(34,197,94,.1);color:var(--green);border-color:rgba(34,197,94,.2);}
.cat-count{font-size:.68rem;opacity:.55;}
/* MAIN */
.main{max-width:1240px;margin:0 auto;padding:2.5rem 1.5rem;}
.results-info{font-size:.84rem;color:var(--muted);margin-bottom:1.5rem;font-family:'JetBrains Mono',monospace;}
.results-info strong{color:var(--text);}
/* GRID */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:1.5rem;margin-bottom:2.5rem;}
/* CARD */
.card{background:var(--bg2);border:1px solid var(--border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;transition:all .3s;cursor:pointer;position:relative;}
.card::before{content:'';position:absolute;inset:0;border-radius:10px;opacity:0;transition:opacity .3s;background:linear-gradient(135deg,rgba(34,197,94,.04),transparent);pointer-events:none;}
.card:hover::before{opacity:1;}
.card:hover{border-color:rgba(34,197,94,.35);transform:translateY(-4px);box-shadow:0 0 0 1px rgba(34,197,94,.08),0 20px 50px rgba(0,0,0,.6),0 0 40px rgba(34,197,94,.04);}
.card-img{height:180px;overflow:hidden;position:relative;flex-shrink:0;}
.card-img img{width:100%;height:100%;object-fit:cover;transition:transform .5s;}
.card:hover .card-img img{transform:scale(1.08);}
.card-img-ph{height:100%;display:flex;align-items:center;justify-content:center;font-size:2.8rem;font-family:'JetBrains Mono',monospace;position:relative;overflow:hidden;}
.card-img-ph::before{content:attr(data-text);position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:.7rem;color:rgba(34,197,94,.08);letter-spacing:.15em;line-height:1.4;word-break:break-all;padding:.5rem;font-family:'JetBrains Mono',monospace;}
.card-img-ph.g0{background:linear-gradient(135deg,#080f0a,#0a1a0d);}
.card-img-ph.g1{background:linear-gradient(135deg,#080d10,#0a100a);}
.card-img-ph.g2{background:linear-gradient(135deg,#0a100a,#0d1508);}
.card-img-ph.g3{background:linear-gradient(135deg,#070d0a,#0c1a10);}
.card-badge{position:absolute;top:.6rem;right:.6rem;background:rgba(8,15,10,.9);border:1px solid rgba(34,197,94,.2);color:var(--green);font-family:'JetBrains Mono',monospace;font-size:.65rem;padding:.2rem .5rem;border-radius:4px;}
.card-body{padding:1.2rem;flex:1;display:flex;flex-direction:column;gap:.55rem;}
.card-top{display:flex;align-items:center;gap:.6rem;}
.card-cat{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--green);background:rgba(34,197,94,.08);padding:.18rem .5rem;border-radius:4px;font-family:'JetBrains Mono',monospace;border:1px solid rgba(34,197,94,.12);}
.card-date{font-size:.73rem;color:var(--muted);font-family:'JetBrains Mono',monospace;}
.card-title{font-size:.96rem;font-weight:700;line-height:1.45;color:var(--text);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.card-excerpt{font-size:.8rem;color:var(--muted);line-height:1.65;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}
.card-foot{display:flex;justify-content:space-between;align-items:center;padding-top:.7rem;border-top:1px solid var(--border);}
.rt{font-size:.72rem;color:var(--muted);font-family:'JetBrains Mono',monospace;}
.rl{display:inline-flex;align-items:center;gap:.25rem;font-size:.78rem;font-weight:600;color:var(--green);font-family:'JetBrains Mono',monospace;transition:gap .2s;}
.card:hover .rl{gap:.45rem;}
/* FEATURED */
.featured{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:0;border-radius:12px;overflow:hidden;border:1px solid rgba(34,197,94,.15);}
.featured .card-img{height:260px;}
.featured .card-body{padding:2rem;}
.featured .card-title{font-size:1.25rem;-webkit-line-clamp:3;}
.featured .card-excerpt{-webkit-line-clamp:4;}
.featured-label{display:inline-flex;align-items:center;gap:.3rem;background:rgba(34,197,94,.12);color:var(--green);border:1px solid rgba(34,197,94,.2);padding:.25rem .7rem;border-radius:4px;font-size:.7rem;font-weight:700;font-family:'JetBrains Mono',monospace;margin-bottom:.6rem;}
/* EMPTY */
.empty{text-align:center;padding:5rem 1rem;color:var(--muted);}
.empty .ico{font-size:3rem;margin-bottom:1rem;font-family:'JetBrains Mono',monospace;color:var(--green);}
.empty h3{font-size:1.1rem;color:var(--text);margin-bottom:.5rem;}
/* PAGINATION */
.pagi{display:flex;justify-content:center;gap:.4rem;flex-wrap:wrap;}
.pagi .page-numbers{padding:.45rem .85rem;border-radius:5px;border:1px solid var(--border);color:var(--muted);font-size:.8rem;font-family:'JetBrains Mono',monospace;transition:all .2s;}
.pagi .page-numbers:hover,.pagi .page-numbers.current{background:rgba(34,197,94,.1);color:var(--green);border-color:rgba(34,197,94,.25);}
.pagi .page-numbers.dots{border:none;}
/* FOOTER */
footer{background:var(--bg2);border-top:1px solid var(--border);padding:1.75rem 2rem;margin-top:2rem;}
.fi{max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:1rem;}
.fl{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:.9rem;color:var(--term);}
.flinks{display:flex;gap:1.5rem;list-style:none;}
.flinks a{font-size:.78rem;color:var(--muted);}
.flinks a:hover{color:var(--green);}
.fc{font-size:.74rem;color:#374151;font-family:'JetBrains Mono',monospace;}
@media(max-width:900px){.featured{grid-template-columns:1fr;}.featured .card-img{height:200px;}}
@media(max-width:768px){.nav-links,.nav-cta{display:none;}.grid{grid-template-columns:1fr;}.hero-stats{gap:1.5rem;}.featured{grid-column:auto;}}
</style></head><body>
<nav>
  <a href="<?php echo esc_url(home_url('/')); ?>" class="nav-logo">// Super<span style="color:#fff">Prompts</span><span class="blink">_</span></a>
  <ul class="nav-links">
    <li><a href="<?php echo esc_url(home_url('/')); ?>">~/inicio</a></li>
    <li><a href="<?php echo esc_url(home_url('/blog')); ?>" class="active">~/blog</a></li>
    <li><a href="<?php echo esc_url(home_url('/prompts-gratis')); ?>">~/prompts-gratis 🎁</a></li>
    <li><a href="<?php echo esc_url(home_url('/contacto')); ?>">~/contacto</a></li>
  </ul>
  <a href="<?php echo esc_url(home_url('/prompts-gratis')); ?>" class="nav-cta">50 Prompts Gratis 🎁</a>
</nav>

<div class="hero">
  <div class="hero-terminal"><span class="prompt">$</span> find prompts/ -type best --results=<?php echo $total;?></div>
  <h1>Prompts que <em>realmente funcionan</em><br>para cada tarea</h1>
  <p>Más de <?php echo number_format($total); ?> prompts probados para productividad, marketing, código y negocios. Sin relleno, solo resultados.</p>
  <form class="search-wrap" method="get" action="<?php echo esc_url(home_url('/blog')); ?>">
    <span class="search-prefix">grep -i "</span>
    <input type="text" name="s" placeholder="buscar prompts..." value="<?php echo esc_attr($s); ?>">
    <button type="submit">ejecutar</button>
  </form>
  <div class="hero-stats">
    <div class="hs"><div class="n"><?php echo number_format($total); ?></div><div class="l">Prompts</div></div>
    <div class="hs"><div class="n"><?php echo count($cats)+1; ?></div><div class="l">Categorías</div></div>
    <div class="hs"><div class="n">0€</div><div class="l">Precio</div></div>
  </div>
</div>

<div class="cats-bar">
  <a href="<?php echo esc_url(home_url('/blog')); ?>" class="<?php echo !$cat_id&&!$s?'on':''; ?>">⚡ todos <?php if(!$cat_id&&!$s):?><span class="cat-count">(<?php echo $total;?>)</span><?php endif;?></a>
  <?php foreach($cats as $c):
    $slug=strtolower($c->slug);
    $ico=isset($cat_icons[$slug])?$cat_icons[$slug]:'📝';
  ?>
  <a href="<?php echo esc_url(get_category_link($c->term_id)); ?>" class="<?php echo $cat_id==$c->term_id?'on':''; ?>">
    <?php echo $ico.' '.esc_html($c->name);?> <span class="cat-count">(<?php echo $c->count;?>)</span>
  </a>
  <?php endforeach;?>
</div>

<div class="main">
  <?php if($s):?><p class="results-info">// <?php echo $q->found_posts;?> resultado(s) para "<strong><?php echo esc_html($s);?></strong>" <a href="<?php echo esc_url(home_url('/blog'));?>" style="color:var(--green);margin-left:.75rem">rm -f filtro</a></p><?php endif;?>

  <?php if($q->have_posts()):?>
  <div class="grid">
  <?php
  $ph_texts=['const ai=require("claude");','import openai','def prompt():','for prompt in list:','<AIComponent/>','SELECT * FROM prompts','git commit -m "wow"','npm i superprompts','python -m magic','console.log("🤖")'];
  $emojis=['⚡','💡','🚀','🎯','🧠','💻','📈','🔥','🛠️','✨'];
  $gi=0;
  while($q->have_posts()):$q->the_post();
    $pid=get_the_ID(); $img=spblog_img($pid);
    $pcat=get_the_category($pid); $cn=$pcat?$pcat[0]->name:'Prompts'; $cl=$pcat?get_category_link($pcat[0]->term_id):home_url('/blog');
    $rt=spblog_rt($pid); $e=$emojis[$gi%count($emojis)]; $g='g'.($gi%4);
    $ph=$ph_texts[$gi%count($ph_texts)];
    $is_first=$gi===0&&$paged===1&&!$cat_id&&!$s;
  ?>
  <?php if($is_first):?>
  <article class="card featured" onclick="location.href='<?php the_permalink();?>'">
    <div class="card-img">
      <?php if($img):?><img src="<?php echo esc_url($img);?>" alt="<?php the_title_attribute();?>" loading="lazy">
      <?php else:?><div class="card-img-ph g0" data-text="<?php echo esc_attr($ph);?>"><?php echo $e;?></div><?php endif;?>
      <div class="card-badge">DESTACADO</div>
    </div>
    <div class="card-body">
      <div class="featured-label">✦ prompt del momento</div>
      <div class="card-top">
        <a href="<?php echo esc_url($cl);?>" class="card-cat" onclick="event.stopPropagation()"><?php echo esc_html($cn);?></a>
        <span class="card-date"><?php echo get_the_date('d M Y');?></span>
      </div>
      <h2 class="card-title"><a href="<?php the_permalink();?>"><?php the_title();?></a></h2>
      <p class="card-excerpt"><?php echo wp_trim_words(get_the_excerpt()?:strip_tags(get_the_content()),30);?></p>
      <div class="card-foot">
        <span class="rt">⏱ <?php echo $rt;?> min</span>
        <span class="rl">ver_prompt() →</span>
      </div>
    </div>
  </article>
  <?php else:?>
  <article class="card" onclick="location.href='<?php the_permalink();?>'">
    <div class="card-img">
      <?php if($img):?><img src="<?php echo esc_url($img);?>" alt="<?php the_title_attribute();?>" loading="lazy">
      <?php else:?><div class="card-img-ph <?php echo $g;?>" data-text="<?php echo esc_attr($ph);?>"><?php echo $e;?></div><?php endif;?>
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
        <span class="rl">ver_prompt() →</span>
      </div>
    </div>
  </article>
  <?php endif; $gi++;endwhile;wp_reset_postdata();?>
  </div>
  <div class="pagi"><?php echo paginate_links(['base'=>str_replace(999999,'%#%',esc_url(get_pagenum_link(999999))),'format'=>'?paged=%#%','current'=>$paged,'total'=>$q->max_num_pages,'prev_text'=>'← prev','next_text'=>'next →']);?></div>
  <?php else:?>
  <div class="empty"><div class="ico">404</div><h3>No se encontraron prompts</h3><p>Prueba con otro término o <a href="<?php echo esc_url(home_url('/blog'));?>" style="color:var(--green)">vuelve al índice</a>.</p></div>
  <?php endif;?>
</div>

<footer><div class="fi">
  <a href="<?php echo esc_url(home_url('/'));?>" class="fl">// SuperPrompts_</a>
  <ul class="flinks">
    <li><a href="<?php echo esc_url(home_url('/politica-de-privacidad'));?>">Privacidad</a></li>
    <li><a href="<?php echo esc_url(home_url('/aviso-legal'));?>">Aviso Legal</a></li>
    <li><a href="<?php echo esc_url(home_url('/contacto'));?>">Contacto</a></li>
  </ul>
  <p class="fc">// © <?php echo date('Y');?> SuperPrompts.es</p>
</div></footer>
<?php wp_footer();?>
</body></html>
