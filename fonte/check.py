import os, re, json, sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse, parse_qs
ROOT = sys.argv[1]
pages = {}
for d, _, fs in os.walk(ROOT):
    for f in fs:
        if f == 'index.html':
            rel = os.path.relpath(d, ROOT); rel = '' if rel == '.' else rel + '/'
            pages[rel] = open(os.path.join(d, f), encoding='utf-8').read()
errs = []; titles = {}; descs = {}; inbound = {p: 0 for p in pages}
for p, h in pages.items():
    h1 = len(re.findall(r'<h1[ >]', h))
    if h1 != 1: errs.append(f'{p}: {h1} h1')
    t = re.search(r'<title>(.*?)</title>', h).group(1); titles.setdefault(t, []).append(p)
    ds = re.search(r'<meta name="description" content="(.*?)">', h).group(1); descs.setdefault(ds, []).append(p)
    if len(t) > 70: errs.append(f'{p}: title {len(t)} chars')
    if not (110 <= len(ds) <= 165): errs.append(f'{p}: description {len(ds)} chars')
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try: json.loads(m.group(1).replace('<\\/', '</'))
        except Exception as e: errs.append(f'{p}: JSON-LD inválido {e}')
    for href in re.findall(r'href="([^"]+)"', h):
        if href.startswith('/') and not href.startswith('//'):
            path = urlparse(href).path
            if path.startswith('/assets/'):
                if not os.path.exists(ROOT + path): errs.append(f'{p}: asset ausente {path}')
                continue
            tgt = path.lstrip('/')
            if tgt not in pages: errs.append(f'{p}: link quebrado {href}')
            elif tgt != p: inbound[tgt] += 1
        elif href.startswith('https://wa.me/'):
            if not href.startswith('https://wa.me/5521987576554?text='): errs.append(f'{p}: WhatsApp fora do padrão {href[:60]}')
            msg = unquote(href.split('text=')[1].replace('&amp;', '&'))
            if 'Olá' not in msg: errs.append(f'{p}: mensagem estranha {msg[:40]}')
        elif href.startswith('tel:') and href != 'tel:+5521987576554': errs.append(f'{p}: telefone fora do padrão {href}')
    for src in re.findall(r'src="(/[^"]+)"', h):
        if not os.path.exists(ROOT + src): errs.append(f'{p}: imagem ausente {src}')
    if '(21) 98757-6554' not in h: errs.append(f'{p}: sem telefone visível')
for t, ps in titles.items():
    if len(ps) > 1: errs.append(f'title duplicado: {ps}')
for t, ps in descs.items():
    if len(ps) > 1: errs.append(f'description duplicada: {ps}')
sm = re.findall(r'<loc>https://www\.vidracariadoadilson\.com\.br/(.*?)</loc>', open(ROOT + '/sitemap.xml').read())
for p in pages:
    if p != '404/' and p not in sm: errs.append(f'fora do sitemap: {p}')
orph = [p for p, n in inbound.items() if n == 0 and p not in ('', '404/')]
print('páginas:', len(pages), '| sitemap:', len(sm), '| órfãs:', orph)
# mensagens de WhatsApp por página de serviço
for s in ['box-para-banheiro/', 'espelhos-sob-medida/', 'portas-de-vidro/']:
    m = re.search(r'class="btn btn-wa" href="https://wa.me/5521987576554\?text=([^"]+)"[^>]*data-loc="hero"', pages[s])
    print(s, '->', unquote(m.group(1)))
print('ERROS:' if errs else 'Nenhum erro.'); [print(' -', e) for e in errs]
