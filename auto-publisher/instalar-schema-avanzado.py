# -*- coding: utf-8 -*-
"""
Instala schema markup avanzado por nicho en las 5 webs WordPress
"""
import requests, sys, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sites = [
    {
        'name': 'Turismo Ourense',
        'url': 'https://turismoourense.es',
        'pass': 'N8OW HTMH INJP fdKy k7u1 fOyO',
        'schema_type': 'turismo'
    },
    {
        'name': 'IA Principiantes',
        'url': 'https://iaparaprincipiantes.es',
        'pass': 'ALZ8 5X0b gEKl YJVY CHWC Ldpk',
        'schema_type': 'ia'
    },
    {
        'name': 'SuperPrompts',
        'url': 'https://superprompts.es',
        'pass': 'fh7t JV4H fVRt WS12 GwCU hwAp',
        'schema_type': 'prompts'
    },
    {
        'name': 'Guia Claude',
        'url': 'https://guiaclaude.es',
        'pass': '2RBK hzue 6a7C 6n1c hxU4 PXz3',
        'schema_type': 'claude'
    },
    {
        'name': 'Bengalas Humo',
        'url': 'https://bengalasdehumo.es',
        'pass': 'RgvQ B927 3dIo tz4N o8r0 8jZL',
        'schema_type': 'bengalas'
    },
]

def get_schema_code(site):
    url = site['url']
    name = site['name']
    st = site['schema_type']

    if st == 'turismo':
        return r"""add_action('wp_head', function() {
    if (is_front_page()) {
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'TouristDestination',
            'name' => 'Ourense, Galicia',
            'description' => 'Descubre Ourense: termas, Ribeira Sacra, gastronomia gallega y tradiciones unicas',
            'url' => 'https://turismoourense.es',
            'geo' => array('@type'=>'GeoCoordinates','latitude'=>42.3354,'longitude'=>-7.8639),
            'touristType' => array('Turismo rural','Turismo termico','Turismo gastronomico','Turismo cultural'),
            'includesAttraction' => array(
                array('@type'=>'TouristAttraction','name'=>'Termas de Ourense','description'=>'Aguas termales naturales en plena ciudad'),
                array('@type'=>'TouristAttraction','name'=>'Ribeira Sacra','description'=>'Canon del rio Sil con vinedos en pendiente'),
                array('@type'=>'TouristAttraction','name'=>'Catedral de Ourense','description'=>'Catedral romanica del siglo XII')
            )
        );
        echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE) . '</script>' . "\n";
    }
    if (is_singular('post')) {
        global $post;
        $img = get_the_post_thumbnail_url($post->ID, 'large');
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => get_the_title(),
            'author' => array('@type'=>'Person','name'=>'Riker Carmon','url'=>'https://turismoourense.es/sobre-nosotros/'),
            'publisher' => array('@type'=>'Organization','name'=>'Turismo Ourense','url'=>'https://turismoourense.es'),
            'datePublished' => get_the_date('c'),
            'dateModified' => get_the_modified_date('c'),
            'image' => $img ? $img : '',
            'url' => get_permalink()
        );
        echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE) . '</script>' . "\n";
    }
}, 10);"""

    elif st == 'ia':
        return r"""add_action('wp_head', function() {
    if (is_singular('post')) {
        global $post;
        $img = get_the_post_thumbnail_url($post->ID, 'large');
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => get_the_title(),
            'author' => array('@type'=>'Person','name'=>'Riker Carmon','url'=>'https://iaparaprincipiantes.es/sobre-nosotros/'),
            'publisher' => array('@type'=>'Organization','name'=>'IA para Principiantes','url'=>'https://iaparaprincipiantes.es'),
            'datePublished' => get_the_date('c'),
            'dateModified' => get_the_modified_date('c'),
            'image' => $img ? $img : '',
            'about' => array('@type'=>'Thing','name'=>'Inteligencia Artificial','description'=>'Tutoriales y guias de IA para personas sin conocimientos tecnicos')
        );
        echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE) . '</script>' . "\n";
    }
}, 10);"""

    elif st == 'prompts':
        return r"""add_action('wp_head', function() {
    if (is_singular('post')) {
        global $post;
        $img = get_the_post_thumbnail_url($post->ID, 'large');
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => get_the_title(),
            'author' => array('@type'=>'Person','name'=>'Riker Carmon','url'=>'https://superprompts.es/sobre-nosotros/'),
            'publisher' => array('@type'=>'Organization','name'=>'SuperPrompts','url'=>'https://superprompts.es'),
            'datePublished' => get_the_date('c'),
            'dateModified' => get_the_modified_date('c'),
            'image' => $img ? $img : '',
            'about' => array('@type'=>'SoftwareApplication','name'=>'Prompts de IA','applicationCategory'=>'Productivity')
        );
        echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE) . '</script>' . "\n";
    }
}, 10);"""

    elif st == 'claude':
        return r"""add_action('wp_head', function() {
    if (is_singular('post')) {
        global $post;
        $img = get_the_post_thumbnail_url($post->ID, 'large');
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'TechArticle',
            'headline' => get_the_title(),
            'author' => array('@type'=>'Person','name'=>'Riker Carmon','url'=>'https://guiaclaude.es/sobre-nosotros/'),
            'publisher' => array('@type'=>'Organization','name'=>'Guia Claude','url'=>'https://guiaclaude.es'),
            'datePublished' => get_the_date('c'),
            'dateModified' => get_the_modified_date('c'),
            'image' => $img ? $img : '',
            'about' => array('@type'=>'SoftwareApplication','name'=>'Claude by Anthropic','url'=>'https://claude.ai','applicationCategory'=>'Artificial Intelligence')
        );
        echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE) . '</script>' . "\n";
    }
}, 10);"""

    else:  # bengalas
        return r"""add_action('wp_head', function() {
    if (is_singular('post')) {
        global $post;
        $img = get_the_post_thumbnail_url($post->ID, 'large');
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => get_the_title(),
            'author' => array('@type'=>'Person','name'=>'Riker Carmon','url'=>'https://bengalasdehumo.es/sobre-nosotros/'),
            'publisher' => array('@type'=>'Organization','name'=>'Bengalas de Humo','url'=>'https://bengalasdehumo.es'),
            'datePublished' => get_the_date('c'),
            'dateModified' => get_the_modified_date('c'),
            'image' => $img ? $img : '',
            'about' => array('@type'=>'Product','name'=>'Bengalas de Humo','description'=>'Bengalas y bombas de humo para fotografia, bodas y eventos creativos')
        );
        echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE) . '</script>' . "\n";
    }
}, 10);"""


for site in sites:
    code = get_schema_code(site)
    r = requests.post(
        f"{site['url']}/index.php?rest_route=/code-snippets/v1/snippets",
        auth=('bengalasdehumo@gmail.com', site['pass']),
        json={'title': 'Schema Markup Avanzado', 'code': code, 'active': True, 'scope': 'global'},
        timeout=15
    )
    status = 'OK' if r.status_code in [200, 201] else f"Error {r.status_code}: {r.text[:80]}"
    print(f"{site['name']}: {status}")
    time.sleep(1)

print('\nSchema markup instalado en las 5 webs.')
