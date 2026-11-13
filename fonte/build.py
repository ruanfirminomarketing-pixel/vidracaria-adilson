"""Gerador do site da Vidraçaria do Adilson.
uso: python3 build.py <pasta_saida> [preview]
  preview -> links relativos com index.html (para abrir sem servidor)
"""
import sys, os, re, json, html, shutil
from urllib.parse import quote
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services_a import SERVICES_A
from services_b import SERVICES_B
from local_blog import REGIONS, BAIRROS, BLOG_CATS, POSTS
from priority import CAMPO_GRANDE, BANGU, COMBOS, POST_CG, SANTISSIMO
from art import art
from photos import PHOTOS, EXTRA, pex
from local_posts import LOCAL_POSTS
from projects import PROJECTS
from assets import CSS, JS

OUT = sys.argv[1]
PREVIEW = len(sys.argv) > 2 and sys.argv[2] == 'preview'

# ===================== CONFIGURAÇÃO =====================
SITE = {
    "name": "Vidraçaria do Adilson",
    "url": "https://www.vidracariadoadilson.com.br",   # PENDENTE: confirmar o domínio definitivo
    "phone_display": "(21) 98757-6554",
    "phone_intl": "+55 21 98757-6554",
    "tel": "tel:+5521987576554",
    "wa": "https://wa.me/5521987576554",
    "wa_default": "Olá! Encontrei o site da Vidraçaria do Adilson e gostaria de solicitar um orçamento.",
    "gtm": "",          # ex.: GTM-ABC1234  (GA4 e conversões são configurados dentro do GTM)
    "gsc": "",          # código de verificação do Google Search Console (meta tag)
    "gbp": "",          # link do Perfil da Empresa no Google, quando existir
    "instagram": "",    # link do Instagram, quando existir
    # Endereço da vidraçaria (Santíssimo). PENDENTE: rua, número e CEP.
    "street": "Estrada da Posse, 511", "cep": "23092-125", "bairro": "Santíssimo",
    # Busca do mapa. Quando o Perfil da Empresa no Google existir, troque pelo nome exato do perfil (ou endereço completo).
    "maps_query": "Estrada da Posse, 511 - Santíssimo, Rio de Janeiro - RJ, 23092-125",
}
TODAY = date.today().isoformat()
# ========================================================

SERVICES = SERVICES_A + SERVICES_B
SVC = {s['slug']: s for s in SERVICES}
BAIRROS = [CAMPO_GRANDE, BANGU, SANTISSIMO] + [b for b in BAIRROS if b['slug'] != 'vidracaria-campo-grande']
BRR = {b['slug']: b for b in BAIRROS}
POST_CG['bairros'] = ['vidracaria-campo-grande', 'vidracaria-bangu']
LOCAL = [POST_CG] + LOCAL_POSTS
for _p in LOCAL: _p['local'] = True
POSTS = LOCAL + POSTS
PST = {p['slug']: p for p in POSTS}
CMB = {c['slug']: c for c in COMBOS}
ORG_ID = SITE['url'] + '/#empresa'
RIO = {"@type": "City", "name": "Rio de Janeiro", "sameAs": "https://pt.wikipedia.org/wiki/Rio_de_Janeiro",
       "containedInPlace": {"@type": "State", "name": "Rio de Janeiro", "alternateName": "RJ", "containedInPlace": {"@type": "Country", "name": "Brasil"}}}
WIKI = {"Campo Grande": "https://pt.wikipedia.org/wiki/Campo_Grande_(Rio_de_Janeiro)", "Bangu": "https://pt.wikipedia.org/wiki/Bangu",
        "Barra da Tijuca": "https://pt.wikipedia.org/wiki/Barra_da_Tijuca", "Copacabana": "https://pt.wikipedia.org/wiki/Copacabana",
        "Tijuca": "https://pt.wikipedia.org/wiki/Tijuca", "Recreio dos Bandeirantes": "https://pt.wikipedia.org/wiki/Recreio_dos_Bandeirantes",
        "Jacarepaguá": "https://pt.wikipedia.org/wiki/Jacarepagu%C3%A1", "Santíssimo": "https://pt.wikipedia.org/wiki/Sant%C3%ADssimo_(Rio_de_Janeiro)"}
def place(n):
    d = {"@type": "Place", "name": f"{n}, Rio de Janeiro - RJ", "alternateName": f"{n} RJ", "containedInPlace": RIO}
    if n in WIKI: d["sameAs"] = WIKI[n]
    return d

def rj_first(t, names=("Campo Grande", "Bangu")):
    # identifica o primeiro bairro citado como bairro do Rio de Janeiro - RJ
    for n in names:
        i = t.find(n)
        if i >= 0 and not t[i + len(n):].startswith((" (R", " RJ", ", Rio", " no Rio", ", no Rio")):
            return t[:i] + n + " (Rio de Janeiro - RJ)" + t[i + len(n):]
        if i >= 0: return t
    return t

PAGES = {}  # caminho -> html
SITEMAP = []

def esc(s): return html.escape(str(s), quote=True)

def path_of(slug):
    if slug in ('', 'inicio'): return ''
    if slug in PST: return f'blog/{slug}/'
    if slug == 'blog': return 'blog/'
    return f'{slug}/'

def href(cur, slug):
    target = path_of(slug)
    if not PREVIEW:
        return '/' + target
    up = '../' * cur.count('/')
    return (up + target + 'index.html') if (up + target) else 'index.html'

def asset(cur, p):
    return ('/' + p) if not PREVIEW else ('../' * cur.count('/') + p)

def wa(msg): return SITE['wa'] + '?text=' + quote(msg, safe='')

def linkify(text, cur):
    out, last = [], 0
    for m in re.finditer(r'\[\[([a-z0-9\-]+)\|([^\]]+)\]\]', text):
        slug, label = m.group(1), m.group(2)
        assert slug in SVC or slug in BRR or slug in PST or slug in CMB or slug in ('area-de-atendimento', 'contato', 'sobre-nos', 'blog', 'servicos-realizados'), slug
        out.append(esc(text[last:m.start()])); out.append(f'<a href="{href(cur, slug)}">{esc(label)}</a>'); last = m.end()
    out.append(esc(text[last:]))
    return ''.join(out)

def strip_links(text): return re.sub(r'\[\[[a-z0-9\-]+\|([^\]]+)\]\]', r'\1', text)

# ---------- ícones
I = {
 'wa': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91C21.95 6.45 17.5 2 12.04 2Zm5.8 14.02c-.24.68-1.42 1.3-1.96 1.36-.5.06-1.13.09-1.82-.11-.42-.13-.96-.31-1.65-.61-2.9-1.25-4.79-4.17-4.94-4.36-.14-.19-1.18-1.57-1.18-3s.75-2.13 1.02-2.42c.27-.29.58-.36.78-.36h.56c.18 0 .42-.07.66.5.24.58.82 2.01.89 2.16.07.14.12.31.02.5-.1.19-.14.31-.29.48-.14.17-.3.38-.43.51-.14.14-.29.3-.13.59.17.29.74 1.22 1.59 1.98 1.09.97 2.01 1.27 2.3 1.42.29.14.46.12.63-.07.17-.19.72-.84.92-1.13.19-.29.38-.24.65-.14.27.1 1.7.8 1.99.95.29.14.48.22.55.34.07.12.07.7-.17 1.38Z"/></svg>',
 'tel': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2Z"/></svg>',
 'chev': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
 'ok': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg>',
 'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
}

def btn_wa(msg, loc, label='Solicitar orçamento pelo WhatsApp'):
    return f'<a class="btn btn-wa" href="{esc(wa(msg))}" target="_blank" rel="noopener" data-loc="{loc}">{I["wa"]}<span>{label}</span></a>'

def btn_call(loc, label=None):
    return f'<a class="btn btn-call" href="{SITE["tel"]}" data-loc="{loc}">{I["tel"]}<span>{label or "Ligar agora: " + SITE["phone_display"]}</span></a>'

def logo(cur, white=False, stacked=False):
    f = ('logo-c-' if stacked else 'logo-h-') + ('white' if white else 'navy')
    w, h = (151, 90) if stacked else (245, 52)
    return (f'<a class="logo{" logo-c" if stacked else ""}" href="{href(cur, "")}" aria-label="Vidraçaria do Adilson, página inicial">'
            f'<picture><source srcset="{asset(cur, "assets/img/" + f + ".webp")}" type="image/webp"><img src="{asset(cur, "assets/img/" + f + ".png")}" alt="Vidraçaria do Adilson" width="{w}" height="{h}"></picture></a>')

def photo(cur, key, idx=0, eager=False, sizes='(max-width:760px) 100vw, (max-width:1100px) 50vw, 33vw', cap=False, ratio=(4, 3)):
    if key in EXTRA: pid, alt = EXTRA[key]; fb = 'espelhos-sob-medida-1.svg'
    else: pid, alt = PHOTOS[key][idx]; fb = f'{key}-{idx+1}.svg'
    lz = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    rw, rh = ratio
    srcset = ', '.join(f'{pex(pid, w, w * rh // rw)} {w}w' for w in (480, 800, 1200, 1600))
    tag = f'<img src="{pex(pid, 800, 800 * rh // rw)}" srcset="{srcset}" sizes="{sizes}" alt="{esc(alt)}" width="800" height="{800 * rh // rw}" {lz}>'
    return (tag, alt) if cap else tag

def img_tag(cur, name, alt, w=800, h=600, eager=False):
    lz = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<img src="{asset(cur, "assets/img/" + name)}" alt="{esc(alt)}" width="{w}" height="{h}" {lz}>'

# ---------- cabeçalho e rodapé
NAV = [('', 'Início'), ('servicos', 'Serviços'), ('servicos-realizados', 'Serviços realizados'), ('sobre-nos', 'Sobre nós'), ('area-de-atendimento', 'Área de atendimento'), ('blog', 'Blog'), ('contato', 'Contato / Orçamento')]

def header(cur, wa_msg):
    items = ''
    for slug, label in NAV:
        if slug == 'servicos':
            links = ''.join(f'<a href="{href(cur, s["slug"])}">{esc(s["name"])}<small>{esc(s["short"][:62].rsplit(" ",1)[0])}…</small></a>' for s in SERVICES)
            items += (f'<li class="has-dd"><button class="dd-btn" aria-expanded="false" aria-haspopup="true">Serviços {I["chev"]}</button>'
                      f'<div class="dd" role="menu">{links}<a class="all" href="{href(cur, "")}#servicos">Ver todos os serviços →</a></div></li>')
        else:
            cu = ' aria-current="page"' if path_of(slug) == cur else ''
            items += f'<li><a href="{href(cur, slug)}"{cu}>{label}</a></li>'
    msvc = ''.join(f'<li><a href="{href(cur, s["slug"])}">{esc(s["name"])}</a></li>' for s in SERVICES)
    mitems = ''
    for slug, label in NAV:
        if slug == 'servicos':
            mitems += f'<li><details><summary>Serviços</summary><ul>{msvc}</ul></details></li>'
        else:
            mitems += f'<li><a href="{href(cur, slug)}">{label}</a></li>'
    return f'''<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="hdr"><div class="wrap hdr-top">
<div class="hdr-l"><button class="burger" aria-label="Abrir menu" aria-expanded="false" aria-controls="drawer">{I["menu"]}<span>Menu</span></button>
<a class="hdr-tel" href="{SITE["tel"]}" data-loc="header">{I["tel"]}<span>{SITE["phone_display"]}</span></a></div>
{logo(cur, True, True)}
<div class="hdr-r"><a class="hdr-call-m" href="{SITE["tel"]}" aria-label="Ligar agora para {SITE["phone_display"]}" data-loc="header_mobile">{I["tel"]}</a>
<a class="btn btn-wa hdr-wa" href="{esc(wa(wa_msg))}" target="_blank" rel="noopener" data-loc="header">{I["wa"]}<span>Orçamento</span></a></div>
</div>
<nav class="nav" aria-label="Menu principal"><div class="wrap"><ul>{items}</ul></div></nav>
</header>
<div class="drawer" id="drawer"><div class="drawer-in" role="dialog" aria-label="Menu">
<div class="drawer-top">{logo(cur)}<button class="x" aria-label="Fechar menu">×</button></div>
<ul class="mnav">{mitems}</ul>
<div class="ctas">{btn_wa(wa_msg, "menu_mobile")}{btn_call("menu_mobile")}</div>
<p class="note">Atendemos toda a cidade do Rio de Janeiro. WhatsApp e ligações: {SITE["phone_display"]}.</p>
</div></div>'''

def addr_line():
    return f"{SITE['street']} - {SITE['bairro']}, Rio de Janeiro - RJ, {SITE['cep']}" if SITE['street'] else f"{SITE['bairro']}, Rio de Janeiro - RJ"

def footer(cur, wa_msg):
    sv = ''.join(f'<li><a href="{href(cur, s["slug"])}">{esc(s["name"])}</a></li>' for s in SERVICES)
    br = ''.join(f'<li><a href="{href(cur, b["slug"])}">Vidraçaria {"em" if b["name"] in ("Copacabana","Campo Grande","Bangu","Jacarepaguá","Santíssimo") else "na" if b["name"] in ("Barra da Tijuca","Tijuca") else "no"} {esc(b["name"])}</a></li>' for b in BAIRROS)
    cm = ''.join(f'<li><a href="{href(cur, c["slug"])}">{esc(c["h1"].replace(" (Rio de Janeiro - RJ)", " RJ"))}</a></li>' for c in COMBOS)
    return f'''<footer class="ftr"><div class="wrap">
<div>{logo(cur, True)}<p>Vidraçaria no Rio de Janeiro: box para banheiro, espelhos, portas, janelas, guarda-corpos, sacadas e vidros sob medida para residências e empresas em toda a capital.</p>
<p>WhatsApp e ligações:<a class="tel" href="{SITE["tel"]}" data-loc="footer">{SITE["phone_display"]}</a></p>
<div class="ctas">{btn_wa(wa_msg, "footer", "WhatsApp")}</div></div>
<div><h2>Serviços</h2><ul>{sv}</ul></div>
<div><h2>Onde atendemos</h2><ul>{br}{cm}<li><a href="{href(cur, "area-de-atendimento")}">Toda a cidade do Rio de Janeiro →</a></li></ul></div>
<div><h2>Vidraçaria do Adilson</h2><ul><li><a href="{href(cur, "sobre-nos")}">Sobre nós</a></li><li><a href="{href(cur, "area-de-atendimento")}">Área de atendimento</a></li><li><a href="{href(cur, "blog")}">Blog</a></li><li><a href="{href(cur, "contato")}">Contato e orçamento</a></li></ul>
<h2 style="margin-top:20px">Atendimento</h2><p>Rio de Janeiro (RJ) — Zona Sul, Zona Norte, Zona Oeste e Centro.</p></div>
<div class="addr"><strong>Endereço:</strong> {esc(addr_line())}</div>
<div class="bottom"><span>© {date.today().year} Vidraçaria do Adilson · Rio de Janeiro, RJ</span><span>Telefone e WhatsApp: <a href="{SITE["tel"]}" data-loc="footer_bottom">{SITE["phone_display"]}</a></span></div>
</div></footer>
<a class="fab" href="{esc(wa(wa_msg))}" target="_blank" rel="noopener" aria-label="Solicitar orçamento pelo WhatsApp" data-loc="float">{I["wa"]}</a>
'''

def crumbs_html(cur, trail):
    lis = ''
    for i, (slug, label) in enumerate(trail):
        if i == len(trail) - 1:
            lis += f'<li aria-current="page">{esc(label)}</li>'
        else:
            lis += f'<li><a href="{href(cur, slug)}">{esc(label)}</a></li>'
    return f'<nav class="crumbs" aria-label="Você está em"><ol>{lis}</ol></nav>'

def crumbs_ld(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": label, "item": SITE['url'] + '/' + path_of(slug)} for i, (slug, label) in enumerate(trail)]}

def faq_html(faq, cur, title='Perguntas frequentes'):
    q = ''.join(f'<details><summary><h3>{esc(a)}</h3></summary><div class="a"><p>{linkify(b, cur)}</p></div></details>' for a, b in faq)
    return f'<section class="sec alt" id="perguntas"><div class="wrap"><span class="kicker">Dúvidas</span><h2>{title}</h2><div class="faq">{q}</div></div></section>'

def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": a, "acceptedAnswer": {"@type": "Answer", "text": strip_links(b)}} for a, b in faq]}

def cta_band(cur, msg, title='Peça seu orçamento agora', text=None, loc='cta_final'):
    text = text or f'Atendemos toda a cidade do Rio de Janeiro. Envie fotos e medidas pelo WhatsApp ou ligue para {SITE["phone_display"]}.'
    return f'''<section class="sec"><div class="wrap"><div class="cta-band"><div><h2>{title}</h2><p>{esc(text)}</p><a class="tel" href="{SITE["tel"]}" data-loc="{loc}">{SITE["phone_display"]}</a></div>
<div class="ctas">{btn_wa(msg, loc)}{btn_call(loc, "Ligar agora")}</div></div></div></section>'''

def org_ld():
    o = {"@type": ["HomeAndConstructionBusiness", "LocalBusiness"], "@id": ORG_ID, "name": SITE['name'], "url": SITE['url'] + '/',
         "telephone": SITE['phone_intl'], "logo": SITE['url'] + '/assets/img/logo-stacked-navy.png', "image": SITE['url'] + '/assets/img/og.jpg',
         "description": "Vidraçaria no Rio de Janeiro: box para banheiro, espelhos sob medida, portas e janelas de vidro, guarda-corpos, envidraçamento de sacadas, vidros temperados e laminados, instalação e manutenção.",
         "address": {k: v for k, v in {"@type": "PostalAddress", "streetAddress": (SITE['street'] + ' - ' + SITE['bairro']) if SITE['street'] else None, "postalCode": SITE['cep'] or None, "addressLocality": "Rio de Janeiro", "addressRegion": "RJ", "addressCountry": "BR"}.items() if v},
         "areaServed": [RIO, place("Campo Grande"), place("Bangu"), place("Santíssimo")],
         "contactPoint": {"@type": "ContactPoint", "telephone": SITE['phone_intl'], "contactType": "sales", "areaServed": "BR", "availableLanguage": "Portuguese"},
         "knowsAbout": [s['name'] for s in SERVICES],
         "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Serviços de vidraçaria", "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s['name'], "url": SITE['url'] + '/' + path_of(s['slug'])}} for s in SERVICES]}}
    same = [x for x in (SITE['gbp'], SITE['instagram']) if x]
    if same: o['sameAs'] = same
    return o

def page(cur, title, desc, body, ld=None, wa_msg=None, ptype='page', service='', robots='index,follow', og_type='website', geo='Rio de Janeiro'):
    wa_msg = wa_msg or SITE['wa_default']
    if len(title) > 65 and title.endswith(' | Vidraçaria do Adilson'): title = title[:-len(' | Vidraçaria do Adilson')]
    canon = SITE['url'] + '/' + cur
    graph = [{"@type": "WebSite", "@id": SITE['url'] + '/#site', "url": SITE['url'] + '/', "name": SITE['name'], "inLanguage": "pt-BR", "publisher": {"@id": ORG_ID}},
             org_ld(),
             {"@type": "WebPage", "@id": canon + '#pagina', "url": canon, "name": title, "description": desc, "isPartOf": {"@id": SITE['url'] + '/#site'}, "about": {"@id": ORG_ID}, "inLanguage": "pt-BR"}] + (ld or [])
    ldj = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace('</', '<\\/')
    gtm_h = gtm_b = ''
    if SITE['gtm']:
        gtm_h = f"<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{SITE['gtm']}');</script>"
        gtm_b = f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={SITE["gtm"]}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
    gsc = f'<meta name="google-site-verification" content="{esc(SITE["gsc"])}">' if SITE['gsc'] else ''
    doc = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{esc(canon)}">
<meta name="theme-color" content="#0A2342">
<meta name="geo.region" content="BR-RJ"><meta name="geo.placename" content="{esc(geo)}">
<meta property="og:locale" content="pt_BR"><meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{SITE["name"]}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(canon)}">
<meta property="og:image" content="{SITE["url"]}/assets/img/og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{gsc}
<link rel="icon" href="{asset(cur, "assets/img/favicon-48.png")}" type="image/png" sizes="48x48"><link rel="apple-touch-icon" href="{asset(cur, "assets/img/apple-touch-icon.png")}">
<link rel="preconnect" href="https://images.pexels.com">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap">
<link rel="stylesheet" href="{asset(cur, "assets/site.css")}">
<script>window.dataLayer=window.dataLayer||[];</script>
{gtm_h}
<script type="application/ld+json">{ldj}</script>
</head>
<body data-type="{ptype}" data-service="{esc(service)}">
{gtm_b}
{header(cur, wa_msg)}
<main id="conteudo">
{body}
</main>
{footer(cur, wa_msg)}
<script src="{asset(cur, "assets/site.js")}" defer></script>
</body>
</html>
'''
    PAGES[cur] = doc
    if robots.startswith('index'):
        SITEMAP.append(cur)

def svc_cards(cur, slugs, show_img=True):
    out = ''
    for sl in slugs:
        s = SVC[sl]
        im = f'<div class="im">{photo(cur, s["slug"], 0)}</div>' if show_img else ''
        out += f'<a class="card scard" href="{href(cur, sl)}">{im}<div class="tx"><h3>{esc(s["name"])}</h3><p>{esc(s["short"])}</p><span class="more">Ver detalhes e orçamento →</span></div></a>'
    return out

def locs_block(cur, service_name=None):
    head = f'{service_name} em todo o Rio de Janeiro' if service_name else 'Atendemos toda a cidade do Rio de Janeiro'
    zones = ''
    for z, ns in REGIONS.items():
        pills = ''
        for n in ns:
            b = next((x for x in BAIRROS if x['name'] == n), None)
            hl = ' class="hl"' if n in ('Campo Grande', 'Bangu') else ''
            pills += f'<li><a{hl} href="{href(cur, b["slug"])}">{esc(n)}</a></li>' if b else f'<li>{esc(n)}</li>'
        zones += f'<div class="zone"><h3>{z}</h3><ul class="pills">{pills}</ul></div>'
    feat = (f'<div class="featured-loc"><a href="{href(cur, "vidracaria-campo-grande")}"><strong>Campo Grande</strong><span>Vidraçaria em Campo Grande e região: box, portas, janelas, espelhos e varandas →</span></a>'
            f'<a href="{href(cur, "vidracaria-bangu")}"><strong>Bangu</strong><span>Vidraçaria em Bangu e bairros vizinhos da Zona Oeste →</span></a></div>')
    intro = (f'A Vidraçaria do Adilson leva {service_name.lower() if service_name else "seus serviços"} a residências e empresas da Zona Sul, Zona Norte, Zona Oeste e Centro do Rio de Janeiro.'
             ' Abaixo estão alguns dos bairros atendidos — se o seu não aparecer, chame no WhatsApp: atendemos toda a capital.')
    return f'<section class="sec" id="regioes"><div class="wrap"><span class="kicker">Área de atendimento</span><h2>{esc(head)}</h2><p>{esc(intro)}</p>{feat}<div class="zones">{zones}</div>{map_block()}</div></section>'

def map_block():
    q = quote(SITE['maps_query'])
    return (f'<div class="map"><div class="map-tx"><span class="kicker">Onde estamos</span><h3>Vidraçaria do Adilson</h3>'
            f'<p>{esc(addr_line())}</p><p>WhatsApp e ligações: <a href="{SITE["tel"]}" data-loc="mapa">{SITE["phone_display"]}</a></p>'
            f'<a class="btn btn-navy" href="https://www.google.com/maps/search/?api=1&amp;query={q}" target="_blank" rel="noopener" data-loc="mapa">Abrir no Google Maps</a></div>'
            f'<iframe class="map-fr" title="Mapa: localização da Vidraçaria do Adilson em Santíssimo, Rio de Janeiro" src="https://maps.google.com/maps?q={q}&amp;z=15&amp;output=embed" '
            f'loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>')

CHIPS = ['Atendimento em todo o Rio', 'Orçamento pelo WhatsApp', 'Medição no local', 'Vidros de segurança']
def chips(): return '<ul class="chips">' + ''.join(f'<li>{I["ok"]}{c}</li>' for c in CHIPS) + '</ul>'

# ===================== PÁGINAS DE SERVIÇO =====================
def build_service(s):
    cur = path_of(s['slug'])
    trail = [('', 'Início'), (s['slug'], s['name'])]
    apps = ''.join(f'<div class="card"><h3>{esc(a)}</h3><p>{linkify(b, cur)}</p></div>' for a, b in s['apps'])
    gal = ''
    caps = ['vidro incolor', 'vidro fumê', 'vidro jateado']
    for i in range(3):
        tag, alt = photo(cur, s["slug"], i, cap=True)
        gal += f'<figure>{tag}<figcaption>{esc(alt)}</figcaption></figure>'
    combos = [c for c in COMBOS if c['service'] == s['slug']]
    combo_html = ''.join(f'<p><strong>Em Campo Grande:</strong> veja <a href="{href(cur, c["slug"])}">{esc(c["h1"].replace(" (Rio de Janeiro - RJ)", " RJ"))}</a>.</p>' for c in combos)
    body = f'''<section class="hero"><div class="wrap"><div>
{crumbs_html(cur, trail)}<span class="kicker">Vidraçaria do Adilson · Rio de Janeiro</span>
<h1>{esc(s["h1"])}</h1><p class="lead">{esc(s["lead"])}</p>
<div class="answer"><strong>Resposta rápida</strong><p>{esc(s["answer"])}</p></div>
<div class="ctas">{btn_wa(s["wa"], "hero")}{btn_call("hero")}</div>{chips()}
</div><div class="hero-art">{photo(cur, s["slug"], 0, True, "(max-width:900px) 100vw, 40vw")}</div></div></section>
<section class="sec"><div class="wrap cols"><div class="prose">
<h2>{esc(s["name"])} no Rio de Janeiro</h2>{"".join(f"<p>{linkify(p, cur)}</p>" for p in s["intro"])}{combo_html}
</div><div class="prose"><h2>{esc(s["tech_title"])}</h2>{"".join(f"<p>{linkify(p, cur)}</p>" for p in s["tech"])}
<ul class="check">{"".join(f"<li>{esc(x)}</li>" for x in s["tech_list"])}</ul></div></div></section>
<section class="sec alt"><div class="wrap"><span class="kicker">Aplicações</span><h2>{esc(s["apps_title"])}</h2><div class="grid g{2 if len(s["apps"]) in (2,4) else 3}">{apps}</div></div></section>
<section class="sec"><div class="wrap cols"><div><h2>{esc(s["mat_title"])}</h2><ul class="check">{"".join(f"<li>{esc(x)}</li>" for x in s["mat"])}</ul></div>
<div><h2>Benefícios</h2><ul class="check">{"".join(f"<li>{esc(x)}</li>" for x in s["benefits"])}</ul>
<div class="ctas">{btn_wa(s["wa"], "beneficios")}</div></div></div></section>
<section class="sec alt"><div class="wrap prose"><h2>Instalação e manutenção</h2>{"".join(f"<p>{linkify(p, cur)}</p>" for p in s["install"])}</div></section>
<section class="sec"><div class="wrap"><span class="kicker">Galeria</span><h2>Galeria: {esc(s["name"].lower())}</h2><div class="gal">{gal}</div><p class="note">Fotos ilustrativas de banco de imagens.</p></div></section>
{faq_html(s["faq"], cur, "Perguntas frequentes sobre " + s["name"].lower())}
<section class="sec"><div class="wrap"><span class="kicker">Serviços relacionados</span><h2>Você também pode precisar</h2><div class="grid g3">{svc_cards(cur, s["related"])}</div></div></section>
{locs_block(cur, s["name"])}
{cta_band(cur, s["wa"], "Orçamento de " + s["name"].lower() + " no Rio de Janeiro")}'''
    ld = [crumbs_ld(trail), faq_ld(s['faq']),
          {"@type": "Service", "@id": SITE['url'] + '/' + cur + '#servico', "name": s['name'], "serviceType": s['name'], "description": s['desc'],
           "provider": {"@id": ORG_ID}, "url": SITE['url'] + '/' + cur,
           "areaServed": [RIO, place("Campo Grande"), place("Bangu"), place("Santíssimo")],
           "image": {"@type": "ImageObject", "url": pex(PHOTOS[s['slug']][0][0], 1200, 900), "caption": PHOTOS[s['slug']][0][1]},
           "audience": {"@type": "Audience", "audienceType": "Residências e empresas"}}]
    page(cur, s['title'], s['desc'], body, ld, s['wa'], 'servico', s['slug'])

# ===================== BAIRROS E COMBOS =====================
def build_bairro(b):
    cur = path_of(b['slug'])
    trail = [('', 'Início'), ('area-de-atendimento', 'Área de atendimento'), (b['slug'], b['name'])]
    secs = ''.join(f'<h2>{esc(t)}</h2><p>{linkify(x, cur)}</p>' for t, x in b.get('sections', []))
    combos = ''
    if b.get('combos'):
        combos = '<section class="sec alt"><div class="wrap"><span class="kicker">Mais procurados em ' + esc(b['name']) + '</span><h2>Serviços em destaque em ' + esc(b['name']) + '</h2><div class="grid g3">' + \
            ''.join(f'<a class="card" href="{href(cur, c)}"><h3>{esc(CMB[c]["h1"].replace(" (Rio de Janeiro - RJ)", " RJ"))}</h3><p>{esc(CMB[c]["desc"])}</p></a>' for c in b['combos']) + '</div></div></section>'
    near = [x for x in BAIRROS if x['slug'] != b['slug'] and x['zona'] == b['zona']][:4]
    near_html = ''.join(f'<a class="card" href="{href(cur, x["slug"])}"><h3>Vidraçaria — {esc(x["name"])}</h3><p>{esc(x["desc"][:110].rsplit(" ",1)[0])}…</p></a>' for x in near)
    body = f'''<section class="hero"><div class="wrap"><div>{crumbs_html(cur, trail)}<span class="kicker">{esc(b["name"])} · {esc(b["zona"])} do Rio de Janeiro - RJ</span>
<h1>{esc(b["h1"])}</h1><p class="lead">Box para banheiro, espelhos, portas, janelas, varandas e vidros sob medida em {esc(b["name"])}, bairro da {esc(b["zona"])} da cidade do Rio de Janeiro (RJ). Peça seu orçamento pelo WhatsApp ou ligue.</p>
<div class="ctas">{btn_wa(b["wa"], "hero")}{btn_call("hero")}</div>{chips()}</div>
<div class="hero-art">{photo(cur, b["services"][0], 1, True, "(max-width:900px) 100vw, 40vw")}</div></div></section>
<section class="sec"><div class="wrap prose">{"".join(f"<p>{linkify(p, cur)}</p>" for p in b["p"])}{secs}</div></section>
{combos}
<section class="sec{" alt" if not combos else ""}"><div class="wrap"><span class="kicker">Serviços</span><h2>Serviços de vidraçaria em {esc(b["name"])}</h2><div class="grid g3">{svc_cards(cur, b["services"])}</div></div></section>
{guides(cur, b)}
{faq_html(b["faq"], cur, "Perguntas frequentes — vidraçaria em " + b["name"])}
<section class="sec"><div class="wrap"><h2>Bairros próximos</h2><div class="grid g{min(4, max(2, len(near)))}">{near_html}</div><p style="margin-top:18px"><a href="{href(cur, "area-de-atendimento")}">Ver toda a área de atendimento →</a></p></div></section>
{cta_band(cur, b["wa"], "Vidraçaria em " + b["name"] + ": peça seu orçamento")}'''
    ld = [crumbs_ld(trail), faq_ld(b['faq']),
          {"@type": "Service", "name": f"Vidraçaria em {b['name']}", "serviceType": "Vidraçaria", "provider": {"@id": ORG_ID},
           "areaServed": place(b['name']),
           "hasOfferCatalog": {"@type": "OfferCatalog", "name": f"Serviços em {b['name']}", "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": SVC[x]['name']}} for x in b['services']]}}]
    page(cur, b['title'], b['desc'], body, ld, b['wa'], 'bairro', b['slug'], geo=b['name'] + ', Rio de Janeiro')

def guides(cur, b):
    ps = [p for p in POSTS if b['slug'] in p.get('bairros', [])]
    if not ps: return ''
    cards = ''.join(f'<a class="card" href="{href(cur, p["slug"])}"><span class="tag">{esc(p["cat"])}</span><h3 style="margin-top:10px">{esc(p["title"])}</h3><p>{esc(p["desc"])}</p></a>' for p in ps[:6])
    return f'<section class="sec"><div class="wrap"><span class="kicker">Blog</span><h2>Guias para quem está em {esc(b["name"])}</h2><div class="grid g3">{cards}</div></div></section>'

def build_combo(c):
    cur = path_of(c['slug'])
    s, b = SVC[c['service']], BRR[c['bairro']]
    trail = [('', 'Início'), (b['slug'], b['name']), (c['slug'], c['h1'].replace(' (Rio de Janeiro - RJ)', ' RJ'))]
    secs = ''.join(f'<h2>{esc(t)}</h2><p>{linkify(x, cur)}</p>' for t, x in c['sections'])
    rel = ''.join(f'<a class="card" href="{href(cur, r)}"><h3>{esc((SVC.get(r) or CMB.get(r))["name"] if r in SVC else CMB[r]["h1"].replace(" (Rio de Janeiro - RJ)", " RJ"))}</h3><p>{esc((SVC[r]["short"]) if r in SVC else CMB[r]["desc"][:120].rsplit(" ",1)[0] + "…")}</p></a>' for r in c['related'])
    body = f'''<section class="hero"><div class="wrap"><div>{crumbs_html(cur, trail)}<span class="kicker">Campo Grande · Zona Oeste do Rio de Janeiro - RJ</span>
<h1>{esc(c["h1"])}</h1><p class="lead">{esc(s["lead"])}</p>
<div class="answer"><strong>Resposta rápida</strong><p>{esc(c["p"][0])}</p></div>
<div class="ctas">{btn_wa(c["wa"], "hero")}{btn_call("hero")}</div>{chips()}</div>
<div class="hero-art">{photo(cur, c["slug"] if c["slug"] in EXTRA else s["slug"], 2, True, "(max-width:900px) 100vw, 40vw")}</div></div></section>
<section class="sec"><div class="wrap prose">{"".join(f"<p>{linkify(p, cur)}</p>" for p in c["p"][1:])}{secs}
<p>Conheça todos os detalhes do serviço em <a href="{href(cur, s["slug"])}">{esc(s["name"].lower())}</a> e veja a <a href="{href(cur, b["slug"])}">vidraçaria em {esc(b["name"])}</a>.</p>
<div class="ctas">{btn_wa(c["wa"], "conteudo")}</div></div></section>
{faq_html(c["faq"], cur)}
<section class="sec"><div class="wrap"><h2>Veja também</h2><div class="grid g3">{rel}</div></div></section>
{cta_band(cur, c["wa"], c["h1"].replace(" (Rio de Janeiro - RJ)", " RJ") + ": peça seu orçamento")}'''
    ld = [crumbs_ld(trail), faq_ld(c['faq']),
          {"@type": "Service", "name": c['h1'].replace(' (Rio de Janeiro - RJ)', ' RJ'), "serviceType": s['name'], "description": c['desc'], "provider": {"@id": ORG_ID},
           "areaServed": place(b['name']),
           "isRelatedTo": {"@type": "Service", "@id": SITE['url'] + '/' + path_of(s['slug']) + '#servico'}}]
    page(cur, c['title'], c['desc'], body, ld, c['wa'], 'servico_bairro', s['slug'], geo=b['name'] + ', Rio de Janeiro')

# ===================== BLOG =====================
def build_post(p):
    cur = path_of(p['slug'])
    if p.get('local') and not p.get('_rj'):
        p['_rj'] = True
        names = [BRR[x]['name'] for x in p['bairros']]
        if 'RJ' not in p['title']: p['title'] = rj_first(p['title'], tuple(names))
        if 'RJ' not in p['title']: p['title'] += ' — Rio de Janeiro (RJ)'
        if 'Campo Grande e Bangu' in p['answer']: p['answer'] = p['answer'].replace('Campo Grande e Bangu', 'Campo Grande e Bangu (Rio de Janeiro - RJ)', 1)
        elif 'RJ' not in p['answer']: p['answer'] = rj_first(p['answer'], tuple(names))
        lst = ', '.join(names[:-1]) + ' e ' + names[-1] if len(names) > 1 else names[0]
        p['body'] = [['p', f'Este guia é para quem mora ou trabalha em {lst}, na cidade do Rio de Janeiro (RJ). A Vidraçaria do Adilson atende somente a cidade do Rio de Janeiro — WhatsApp e ligações pelo (21) 98757-6554.']] + p['body']
    trail = [('', 'Início'), ('blog', 'Blog'), (p['slug'], p['title'])]
    blocks = ''
    for kind, val in p['body']:
        if kind == 'p': blocks += f'<p>{linkify(val, cur)}</p>'
        elif kind == 'h2': blocks += f'<h2>{esc(val)}</h2>'
        elif kind == 'ul': blocks += '<ul class="check">' + ''.join(f'<li>{linkify(x, cur)}</li>' for x in val) + '</ul>'
    msg = SVC[p['services'][0]]['wa']
    side = f'<aside class="side-cta"><div class="card"><h3>Precisa de orçamento?</h3><p>Atendemos toda a cidade do Rio de Janeiro.</p><div class="ctas">{btn_wa(msg, "blog_lateral", "WhatsApp")}{btn_call("blog_lateral", "Ligar agora")}</div></div>' + \
           '<div class="card" style="margin-top:16px"><h3>Serviços citados</h3><ul class="check">' + ''.join(f'<li><a href="{href(cur, s)}">{esc(SVC[s]["name"])}</a></li>' for s in p['services']) + '</ul></div></aside>'
    dt = date.fromisoformat(p['date']).strftime('%d/%m/%Y')
    body = f'''<section class="sec"><div class="wrap">{crumbs_html(cur, trail)}<div class="layout"><article class="article">
<span class="tag">{esc(p["cat"])}</span><h1>{esc(p["title"])}</h1><p class="post-meta">Por Vidraçaria do Adilson · Publicado em <time datetime="{p["date"]}">{dt}</time></p>
<div class="answer"><strong>Resposta rápida</strong><p>{esc(p["answer"])}</p></div>
{blocks}</article>{side}</div></div></section>
{faq_html(p["faq"], cur)}
{more_posts(cur, p)}
<section class="sec"><div class="wrap"><h2>Serviços relacionados</h2><div class="grid g3">{svc_cards(cur, p["services"] + [x for x in ("instalacao-de-vidros", "manutencao-de-vidros") if x not in p["services"]][:3-len(p["services"])])}</div></div></section>
{cta_band(cur, msg)}'''
    ld = [crumbs_ld(trail), faq_ld(p['faq']),
          {"@type": "BlogPosting", "headline": p['title'], **({"contentLocation": [place(BRR[x]['name']) for x in p['bairros']], "spatialCoverage": [place(BRR[x]['name']) for x in p['bairros']]} if p.get('local') else {}), "description": p['desc'], "datePublished": p['date'], "dateModified": p['date'], "inLanguage": "pt-BR",
           "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}, "mainEntityOfPage": SITE['url'] + '/' + cur, "articleSection": p['cat'],
           "image": SITE['url'] + '/assets/img/og.jpg', "about": [{"@type": "Service", "name": SVC[x]['name']} for x in p['services']]}]
    page(cur, p['seo'] + ' | Vidraçaria do Adilson', p['desc'], body, ld, msg, 'blog', p['services'][0], og_type='article', geo=(BRR[p['bairros'][0]]['name'] + ', Rio de Janeiro') if p.get('local') else 'Rio de Janeiro')

def more_posts(cur, p):
    pool = [x for x in (LOCAL if p.get('local') else POSTS) if x['slug'] != p['slug']][:3]
    cards = ''.join(f'<a class="card" href="{href(cur, x["slug"])}"><span class="tag">{esc(x["cat"])}</span><h3 style="margin-top:10px">{esc(x["title"])}</h3></a>' for x in pool)
    return f'<section class="sec"><div class="wrap"><h2>Leia também</h2><div class="grid g3">{cards}</div></div></section>'

def build_blog_index():
    cur = 'blog/'
    trail = [('', 'Início'), ('blog', 'Blog')]
    cats = [c for c in BLOG_CATS if any(p['cat'] == c for p in POSTS)]
    filt = '<div class="filters"><button data-cat="*" aria-pressed="true">Todos</button>' + ''.join(f'<button data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats) + '</div>'
    def card(p):
        return f'<a class="card" data-cat="{esc(p["cat"])}" href="{href(cur, p["slug"])}"><span class="tag">{esc(p["cat"])}</span><h3 style="margin-top:10px">{esc(p["title"])}</h3><p>{esc(p["desc"])}</p><span class="more" style="display:inline-block;margin-top:10px;font-weight:800">Ler artigo →</span></a>'
    main = ''.join(card(p) for p in POSTS if p.get('local'))
    rest = ''.join(card(p) for p in POSTS if not p.get('local'))
    body = f'''<section class="hero"><div class="wrap" style="grid-template-columns:1fr"><div>{crumbs_html(cur, trail)}<h1>Blog da Vidraçaria do Adilson</h1>
<p class="lead">Guias de vidraçaria para quem mora ou trabalha em Campo Grande, Bangu, na Zona Oeste e em todo o Rio de Janeiro: box, espelhos, portas, janelas, varandas e tipos de vidro.</p></div></div></section>
<section class="sec"><div class="wrap">{filt}<span class="kicker">Artigos principais</span><h2>Campo Grande, Bangu e Zona Oeste</h2><div class="grid g3">{main}</div></div></section>
<section class="sec alt"><div class="wrap"><span class="kicker">Mais guias</span><h2>Guias para escolher o vidro certo</h2><div class="grid g3">{rest}</div></div></section>{cta_band(cur, SITE["wa_default"])}'''
    ld = [crumbs_ld(trail), {"@type": "Blog", "name": "Blog da Vidraçaria do Adilson", "url": SITE['url'] + '/blog/', "publisher": {"@id": ORG_ID},
          "blogPost": [{"@type": "BlogPosting", "headline": p['title'], "url": SITE['url'] + '/' + path_of(p['slug'])} for p in POSTS]}]
    page(cur, 'Blog | Dicas de Vidraçaria, Box, Espelhos e Vidros | Vidraçaria do Adilson', 'Artigos sobre box para banheiro, espelhos, portas, janelas, vidro temperado e laminado, manutenção e vidraçaria no Rio de Janeiro.', body, ld, None, 'blog_index')

# ===================== INSTITUCIONAIS =====================
HOME_FAQ = [
 ["A Vidraçaria do Adilson atende toda a cidade do Rio de Janeiro?", "Sim. Atendemos residências e empresas na Zona Sul, Zona Norte, Zona Oeste e Centro do Rio de Janeiro, incluindo [[vidracaria-campo-grande|Campo Grande]] e [[vidracaria-bangu|Bangu]]."],
 ["Como solicitar um orçamento?", "Pelo WhatsApp ou por ligação no (21) 98757-6554. Envie fotos, medidas aproximadas e o bairro; fazemos uma estimativa e agendamos a medição no local."],
 ["Quais serviços a vidraçaria faz?", "Box para banheiro, espelhos sob medida, portas e janelas de vidro, guarda-corpos, envidraçamento de sacadas, fechamento de varandas, divisórias, tampos de mesa, vidros temperados e laminados, instalação, troca e manutenção de vidros."],
 ["Qual a diferença entre vidro temperado e laminado?", "O temperado é muito mais resistente e, se quebra, vira pequenos fragmentos. O laminado mantém os pedaços presos a uma película e é exigido em guarda-corpos e coberturas. Veja o [[vidro-temperado-ou-laminado|guia completo]]."],
 ["Quanto tempo leva para instalar um box?", "Depois da medição, o vidro temperado é fabricado sob medida, o que leva alguns dias úteis. A instalação costuma ser feita em poucas horas."],
]

def build_home():
    cur = ''
    allsvc = svc_cards(cur, [s['slug'] for s in SERVICES])
    steps = [('Fale com a gente', 'Chame no WhatsApp ou ligue para (21) 98757-6554 e conte o que precisa.'),
             ('Envie fotos e medidas', 'Com fotos e medidas aproximadas, já fazemos uma estimativa.'),
             ('Medição no local', 'Conferimos as medidas exatas, o prumo e o nível no seu endereço.'),
             ('Fabricação e instalação', 'O vidro é produzido sob medida e instalado com acabamento cuidadoso.')]
    st = ''.join(f'<div class="card"><div class="num">{i+1}</div><h3>{a}</h3><p>{b}</p></div>' for i, (a, b) in enumerate(steps))
    difs = [('Toda a cidade do Rio', 'Atendimento na Zona Sul, Norte, Oeste e Centro, com destaque para Campo Grande e Bangu.'),
            ('Tudo sob medida', 'Cada peça é produzida nas medidas exatas do seu espaço.'),
            ('Vidros de segurança', 'Temperado e laminado indicados conforme as normas da ABNT para cada uso.'),
            ('Orçamento rápido', 'Comece pelo WhatsApp com fotos e medidas, sem compromisso.')]
    df = ''.join(f'<div class="card"><h3>{a}</h3><p>{b}</p></div>' for a, b in difs)
    gal = ''.join(f'<figure>{photo(cur, s, 1)}<figcaption>{esc(SVC[s]["name"])}</figcaption></figure>' for s in ['box-para-banheiro', 'espelhos-sob-medida', 'guarda-corpo-de-vidro', 'envidracamento-de-sacadas', 'portas-de-vidro', 'janelas-de-vidro'])
    posts = ''.join(f'<a class="card" href="{href(cur, p["slug"])}"><span class="tag">{esc(p["cat"])}</span><h3 style="margin-top:10px">{esc(p["title"])}</h3><p>{esc(p["desc"])}</p></a>' for p in LOCAL[:6])
    body = f'''<section class="hero hero-c"><div class="wrap"><div><span class="kicker">Vidraçaria no Rio de Janeiro</span>
<h1>Vidraçaria no Rio de Janeiro | Box, Espelhos, Portas e Vidros Sob Medida</h1>
<p class="lead">Soluções em vidros para residências e empresas em toda a cidade do Rio de Janeiro. Solicite seu orçamento com a Vidraçaria do Adilson.</p>
<div class="ctas">{btn_wa(SITE["wa_default"], "hero")}{btn_call("hero", "Ligar agora")}</div>{chips()}</div>
<div class="hero-art">{photo(cur, "box-para-banheiro", 0, True, "(max-width:1000px) 100vw, 960px", ratio=(16, 9))}</div></div></section>
<section class="sec"><div class="wrap cols"><div><span class="kicker">Quem somos</span><h2>Vidraçaria do Adilson: vidros sob medida no Rio</h2>
<p>A Vidraçaria do Adilson é uma vidraçaria do Rio de Janeiro, com base em Santíssimo, na Zona Oeste, que atende residências, condomínios e empresas em toda a capital. Fazemos box para banheiro, espelhos sob medida, portas e janelas de vidro, guarda-corpos, envidraçamento de sacadas, divisórias, tampos de mesa e instalação e manutenção de vidros.</p>
<p>Cada projeto começa por entender o que você precisa e medir o espaço com precisão, para indicar o vidro certo — temperado, laminado ou comum — de acordo com o uso e com as normas técnicas.</p>
<p><a href="{href(cur, "sobre-nos")}">Conheça a Vidraçaria do Adilson →</a></p></div>
<div class="grid g2">{df}</div></div></section>
<section class="sec alt" id="servicos"><div class="wrap"><span class="kicker">Serviços</span><h2>Serviços de vidraçaria no Rio de Janeiro</h2><p>Escolha o serviço para ver detalhes, tipos de vidro, perguntas frequentes e pedir orçamento.</p><div class="grid g3">{allsvc}</div></div></section>
<section class="sec"><div class="wrap"><span class="kicker">Como funciona</span><h2>Do orçamento à instalação</h2><div class="grid g4">{st}</div><div class="ctas">{btn_wa(SITE["wa_default"], "como_funciona")}{btn_call("como_funciona")}</div></div></section>
<section class="sec alt"><div class="wrap"><span class="kicker">Galeria</span><h2>Projetos em vidro</h2><div class="gal">{gal}</div><p class="note">Fotos ilustrativas de banco de imagens.</p></div></section>
{locs_block(cur)}
{faq_html(HOME_FAQ, cur)}
<section class="sec"><div class="wrap"><span class="kicker">Blog</span><h2>Guias de vidraçaria para Campo Grande, Bangu e Zona Oeste</h2><div class="grid g3">{posts}</div><p style="margin-top:18px"><a href="{href(cur, "blog")}">Ver todos os artigos →</a></p></div></section>
{cta_band(cur, SITE["wa_default"])}'''
    page('', 'Vidraçaria no Rio de Janeiro | Box, Espelhos e Vidros Sob Medida | Vidraçaria do Adilson',
         'Vidraçaria no Rio de Janeiro: box para banheiro, espelhos, portas, janelas, guarda-corpos e sacadas sob medida em toda a capital. Orçamento pelo WhatsApp.',
         body, [faq_ld(HOME_FAQ)], None, 'home')

def build_sobre():
    cur = 'sobre-nos/'
    trail = [('', 'Início'), ('sobre-nos', 'Sobre nós')]
    body = f'''<section class="hero"><div class="wrap"><div>{crumbs_html(cur, trail)}<h1>Sobre a Vidraçaria do Adilson</h1>
<p class="lead">Vidraçaria do Rio de Janeiro dedicada a soluções em vidro sob medida para casas, apartamentos, condomínios e empresas.</p>
<div class="ctas">{btn_wa(SITE["wa_default"], "hero")}{btn_call("hero")}</div></div>
<div class="hero-art">{photo(cur, "instalacao-de-vidros", 0, True, "(max-width:900px) 100vw, 40vw")}</div></div></section>
<section class="sec"><div class="wrap cols"><div class="prose"><h2>Quem somos</h2>
<p>A Vidraçaria do Adilson atende toda a cidade do Rio de Janeiro com serviços de vidraçaria para residências e empresas: do box do banheiro ao guarda-corpo da varanda, de um espelho sob medida à divisória de um escritório.</p>
<p>O atendimento é feito diretamente pelo WhatsApp e pelo telefone {SITE["phone_display"]}. Você explica o que precisa, envia fotos e medidas, e combinamos a medição no local para fechar o orçamento com segurança.</p>
<h2>Como trabalhamos</h2><ul class="check"><li>Ouvimos o que você precisa e indicamos a solução adequada.</li><li>Medimos no local para que o vidro encaixe com as folgas corretas.</li><li>Indicamos o tipo de vidro conforme o uso e as normas da ABNT (temperado, laminado ou comum).</li><li>Instalamos com acabamento cuidadoso e orientamos sobre limpeza e manutenção.</li></ul></div>
<div class="prose"><h2>O que fazemos</h2><ul class="check">{"".join(f'<li><a href="{href(cur, s["slug"])}">{esc(s["name"])}</a></li>' for s in SERVICES)}</ul>
<h2>Onde atendemos</h2><p>Toda a capital do Rio de Janeiro, com atenção especial à Zona Oeste — <a href="{href(cur, "vidracaria-campo-grande")}">Campo Grande</a> e <a href="{href(cur, "vidracaria-bangu")}">Bangu</a> — e também Zona Sul, Zona Norte e Centro. <a href="{href(cur, "area-de-atendimento")}">Veja a área de atendimento</a>.</p></div></div></section>
{cta_band(cur, SITE["wa_default"])}'''
    page(cur, 'Sobre Nós | Vidraçaria do Adilson | Vidraçaria no Rio de Janeiro', 'Conheça a Vidraçaria do Adilson: vidraçaria no Rio de Janeiro com box, espelhos, portas, janelas, guarda-corpos e vidros sob medida para casas e empresas.', body, [crumbs_ld(trail), {"@type": "AboutPage", "about": {"@id": ORG_ID}}], None, 'sobre')

def build_area():
    cur = 'area-de-atendimento/'
    trail = [('', 'Início'), ('area-de-atendimento', 'Área de atendimento')]
    locals_ = ''.join(f'<a class="card" href="{href(cur, b["slug"])}"><span class="tag">{esc(b["zona"])}</span><h3 style="margin-top:10px">{esc(b["h1"])}</h3><p>{esc(b["desc"])}</p></a>' for b in BAIRROS)
    body = f'''<section class="hero"><div class="wrap" style="grid-template-columns:1fr"><div>{crumbs_html(cur, trail)}<h1>Área de atendimento: toda a cidade do Rio de Janeiro</h1>
<p class="lead">A Vidraçaria do Adilson atende residências e empresas na Zona Sul, Zona Norte, Zona Oeste e Centro do Rio de Janeiro — com destaque para Campo Grande e Bangu.</p>
<div class="ctas">{btn_wa(SITE["wa_default"], "hero")}{btn_call("hero")}</div></div></div></section>
{locs_block(cur)}
<section class="sec alt"><div class="wrap"><span class="kicker">Páginas por bairro</span><h2>Vidraçaria por bairro</h2><div class="grid g3">{locals_}</div></div></section>
<section class="sec"><div class="wrap prose"><h2>Seu bairro não está na lista?</h2><p>As listas acima mostram alguns dos bairros atendidos. Atendemos toda a capital do Rio de Janeiro: chame no WhatsApp ou ligue para {SITE["phone_display"]} e informe o seu bairro.</p></div></section>
{cta_band(cur, SITE["wa_default"])}'''
    ld = [crumbs_ld(trail), {"@type": "ItemList", "name": "Bairros com página da Vidraçaria do Adilson", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE['url'] + '/' + path_of(b['slug']), "name": b['h1']} for i, b in enumerate(BAIRROS)]}]
    page(cur, 'Área de Atendimento | Vidraçaria em Todo o Rio de Janeiro', 'Vidraçaria em toda a cidade do Rio de Janeiro: Zona Sul, Zona Norte, Zona Oeste (Campo Grande, Bangu, Barra, Recreio) e Centro. Veja os bairros atendidos.', body, ld, None, 'area')

def build_contato():
    cur = 'contato/'
    trail = [('', 'Início'), ('contato', 'Contato / Orçamento')]
    opts = ''.join(f'<option>{esc(s["name"])}</option>' for s in SERVICES) + '<option>Outro serviço</option>'
    body = f'''<section class="hero"><div class="wrap"><div>{crumbs_html(cur, trail)}<h1>Contato e orçamento</h1>
<p class="lead">Fale com a Vidraçaria do Adilson pelo WhatsApp ou por telefone. Atendemos toda a cidade do Rio de Janeiro.</p>
<a class="phone-big" href="{SITE["tel"]}" data-loc="contato_numero">{I["tel"]}{SITE["phone_display"]}</a><p>WhatsApp e ligações no mesmo número.</p>
<div class="ctas">{btn_wa(SITE["wa_default"], "contato")}{btn_call("contato")}</div>
<h2 style="margin-top:30px;font-size:22px">Para agilizar o orçamento</h2><ul class="check"><li>Fotos do local onde o vidro será instalado.</li><li>Medidas aproximadas (largura e altura, em centímetros).</li><li>O serviço desejado e preferência de cor do vidro e da ferragem.</li><li>Seu bairro no Rio de Janeiro.</li></ul></div>
<form class="form" id="orcamento" novalidate><h2 style="font-size:22px">Solicite seu orçamento</h2><p class="note" style="margin-top:0">Preencha e enviaremos sua mensagem pelo WhatsApp.</p>
<label for="f-nome">Nome</label><input id="f-nome" name="nome" autocomplete="name" required>
<div class="row"><div><label for="f-tel">Telefone com DDD</label><input id="f-tel" name="telefone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(21) 9____-____" required></div>
<div><label for="f-bairro">Bairro</label><input id="f-bairro" name="bairro" placeholder="Ex.: Campo Grande" required></div></div>
<label for="f-serv">Serviço</label><select id="f-serv" name="servico" required><option value="">Escolha o serviço</option>{opts}</select>
<label for="f-msg">Detalhes (opcional)</label><textarea id="f-msg" name="mensagem" rows="4" placeholder="Medidas, modelo, cor do vidro…"></textarea>
<button class="btn btn-wa" type="submit">{I["wa"]}<span>Enviar pelo WhatsApp</span></button>
<p class="err" role="alert"></p><p class="ok note" hidden>Abrimos o WhatsApp com sua mensagem. Se não abriu, chame no {SITE["phone_display"]}.</p>
<p class="lgpd">Seus dados são usados só para responder ao seu pedido de orçamento.</p></form></div></section>
{locs_block(cur)}'''
    ld = [crumbs_ld(trail), {"@type": "ContactPage", "about": {"@id": ORG_ID}}]
    page(cur, 'Contato e Orçamento | (21) 98757-6554 | Vidraçaria do Adilson', 'Peça orçamento à Vidraçaria do Adilson pelo WhatsApp ou ligue (21) 98757-6554. Atendemos toda a cidade do Rio de Janeiro.', body, ld, None, 'contato')

def build_portfolio():
    cur = 'servicos-realizados/'
    trail = [('', 'Início'), ('servicos-realizados', 'Serviços realizados')]
    items, ld_items = '', []
    for i, pj in enumerate(PROJECTS):
        sv, br = SVC[pj['service']], BRR.get(pj.get('bairro', ''))
        figs = ''.join(f'<figure><img src="{asset(cur, "assets/img/obras/" + f)}" alt="{esc(alt)}" width="1200" height="900" loading="{"eager" if i == 0 and k == 0 else "lazy"}" decoding="async"></figure>'
                       for k, (f, alt) in enumerate(pj['photos']))
        where = f' em <a href="{href(cur, br["slug"])}">{esc(br["name"])}</a> (Rio de Janeiro - RJ)' if br else ' no Rio de Janeiro (RJ)'
        det = ''.join(f'<li>{esc(x)}</li>' for x in pj.get('details', []))
        items += (f'<article class="obra" id="{pj["slug"]}"><div class="obra-fotos">{figs}</div><div class="obra-tx">'
                  f'<span class="tag">{esc(sv["name"])}</span><h2>{esc(pj["title"])}</h2>'
                  f'<p class="post-meta">Serviço realizado{where}</p><p>{esc(pj["desc"])}</p>'
                  + (f'<ul class="check">{det}</ul>' if det else '') +
                  f'<p><a href="{href(cur, sv["slug"])}">Ver o serviço de {esc(sv["name"].lower())} →</a></p></div></article>')
        ld_items.append({"@type": "CreativeWork", "name": pj['title'], "description": pj['desc'], "about": {"@type": "Service", "name": sv['name']},
                         "creator": {"@id": ORG_ID}, "url": SITE['url'] + '/' + cur + '#' + pj['slug'],
                         "contentLocation": place(br['name']) if br else RIO,
                         "image": [{"@type": "ImageObject", "contentUrl": SITE['url'] + '/assets/img/obras/' + f, "caption": alt} for f, alt in pj['photos']]})
    if not items:
        items = (f'<div class="card" style="text-align:center;padding:40px"><h2>Fotos dos nossos trabalhos em breve</h2>'
                 f'<p>Estamos reunindo as fotos dos serviços realizados em Santíssimo, Campo Grande, Bangu e em todo o Rio de Janeiro.</p>'
                 f'<div class="ctas" style="justify-content:center">{btn_wa(SITE["wa_default"], "obras")}</div></div>')
    body = f'''<section class="hero hero-c"><div class="wrap"><div>{crumbs_html(cur, trail)}<span class="kicker">Portfólio</span><h1>Serviços realizados pela Vidraçaria do Adilson</h1>
<p class="lead">Box, espelhos, portas, janelas, guarda-corpos e outros trabalhos em vidro feitos pela nossa equipe em Santíssimo, Campo Grande, Bangu e em toda a cidade do Rio de Janeiro (RJ).</p>
<div class="ctas">{btn_wa(SITE["wa_default"], "hero")}{btn_call("hero", "Ligar agora")}</div></div></div></section>
<section class="sec"><div class="wrap obras">{items}</div></section>
{cta_band(cur, SITE["wa_default"], "Quer um trabalho assim na sua casa ou empresa?")}'''
    ld = [crumbs_ld(trail), {"@type": "CollectionPage", "name": "Serviços realizados", "about": {"@id": ORG_ID}},
          {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": x} for i, x in enumerate(ld_items)]}]
    page(cur, 'Serviços Realizados | Fotos de Trabalhos | Vidraçaria do Adilson',
         'Fotos de box, espelhos, portas, janelas e guarda-corpos instalados pela Vidraçaria do Adilson em Santíssimo, Campo Grande, Bangu e no Rio de Janeiro (RJ).',
         body, ld, None, 'portfolio', robots='index,follow' if PROJECTS else 'noindex,follow', geo='Santíssimo, Rio de Janeiro')

def build_404():
    cur = '404/'
    body = f'''<section class="hero"><div class="wrap" style="grid-template-columns:1fr"><div><h1>Página não encontrada</h1><p class="lead">O endereço pode ter mudado. Veja nossos serviços ou fale com a gente.</p>
<div class="ctas">{btn_wa(SITE["wa_default"], "404")}{btn_call("404")}</div></div></div></section>
<section class="sec alt"><div class="wrap"><h2>Serviços</h2><div class="grid g3">{svc_cards(cur, [s["slug"] for s in SERVICES], False)}</div></div></section>'''
    page(cur, 'Página não encontrada | Vidraçaria do Adilson', 'Página não encontrada.', body, None, None, '404', robots='noindex,follow')

# ===================== GERAÇÃO =====================
for s in SERVICES: build_service(s)
for b in BAIRROS: build_bairro(b)
for c in COMBOS: build_combo(c)
for p in POSTS: build_post(p)
build_blog_index(); build_portfolio(); build_home(); build_sobre(); build_area(); build_contato(); build_404()

if os.path.exists(OUT): shutil.rmtree(OUT)
for cur, doc in PAGES.items():
    d = os.path.join(OUT, cur)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(doc)
# 404 também na raiz para o servidor
shutil.copy(os.path.join(OUT, '404', 'index.html'), os.path.join(OUT, '404.html'))

os.makedirs(os.path.join(OUT, 'assets/img'), exist_ok=True)
open(os.path.join(OUT, 'assets/site.css'), 'w').write(re.sub(r'\n\s*', '', CSS).strip())
open(os.path.join(OUT, 'assets/site.js'), 'w').write(JS.strip())
LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo')
for f in os.listdir(LOGO_DIR):
    shutil.copy(os.path.join(LOGO_DIR, f), os.path.join(OUT, 'assets/img', f))
if os.path.exists(os.path.join(OUT, 'assets/img', 'og.png')): os.remove(os.path.join(OUT, 'assets/img', 'og.png'))
# fotos dos serviços realizados (já otimizadas em fonte/obras)
OBRAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'obras')
if os.listdir(OBRAS):
    os.makedirs(os.path.join(OUT, 'assets/img/obras'), exist_ok=True)
    for f in os.listdir(OBRAS):
        if f.endswith('.webp'): shutil.copy(os.path.join(OBRAS, f), os.path.join(OUT, 'assets/img/obras', f))

prio = {'': '1.0'}
urls = ''.join(f'<url><loc>{SITE["url"]}/{c}</loc><lastmod>{TODAY}</lastmod></url>' for c in SITEMAP)
open(os.path.join(OUT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /404/\n\nSitemap: {SITE["url"]}/sitemap.xml\n')
open(os.path.join(OUT, '.htaccess'), 'w').write(r'''# Vidraçaria do Adilson — Hostinger / Apache
Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html

RewriteEngine On
# HTTPS obrigatório
RewriteCond %{HTTPS} off
RewriteCond %{HTTP:X-Forwarded-Proto} !https
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
# Domínio único (com www). Se o domínio oficial for sem www, inverta esta regra.
RewriteCond %{HTTP_HOST} !^www\. [NC]
RewriteCond %{HTTP_HOST} !^localhost [NC]
RewriteRule ^ https://www.%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
# /pagina/index.html -> /pagina/ (evita conteúdo duplicado)
RewriteCond %{THE_REQUEST} \s/+(.*/)?index\.html[\s?] [NC]
RewriteRule ^ /%1 [L,R=301]
# /pagina -> /pagina/
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_URI} !/$
RewriteCond %{DOCUMENT_ROOT}%{REQUEST_URI}/ -d
RewriteRule ^(.*)$ /$1/ [L,R=301]

# Redirecionamentos 301 de páginas antigas (exemplo):
# Redirect 301 /servicos.html /#servicos

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/xml text/plain
</IfModule>
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
  ExpiresByType image/svg+xml "access plus 6 months"
  ExpiresByType image/webp "access plus 6 months"
  ExpiresByType image/avif "access plus 6 months"
  ExpiresByType image/png "access plus 6 months"
</IfModule>
<IfModule mod_headers.c>
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set X-Frame-Options "SAMEORIGIN"
</IfModule>
''')
# Cloudflare Pages / Netlify: cabeçalhos de cache e segurança (equivalente ao .htaccess)
open(os.path.join(OUT, '_headers'), 'w').write('''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN

/assets/*
  Cache-Control: public, max-age=604800, stale-while-revalidate=86400

/404/*
  X-Robots-Tag: noindex
''')
print(f'{len(PAGES)} páginas, {len(SITEMAP)} no sitemap')
json.dump({'pages': list(PAGES), 'sitemap': SITEMAP, 'services': [s['slug'] for s in SERVICES]}, open(os.path.join(os.path.dirname(OUT.rstrip('/')), 'manifest-' + ('prev' if PREVIEW else 'prod') + '.json'), 'w'))
