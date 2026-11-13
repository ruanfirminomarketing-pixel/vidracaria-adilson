# Ilustrações vetoriais (SVG) de cada serviço. São provisórias: trocar por fotos reais em WebP.

NAVY = "#0A2342"; NAVY2 = "#13315C"; SKY = "#5DA9E9"; PALE = "#EAF4FC"; MID = "#B9DDF7"

TINTS = [  # (vidro, opacidade, fundo da parede)
 ("#9FD3F5", .38, "#F4F9FE"),
 ("#5E6B7A", .42, "#EEF3F8"),   # fumê
 ("#E6F1FA", .78, "#E9F2FB"),   # jateado
]

def _glass(x, y, w, h, t, rx=2):
    c, o, _ = t
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{c}" fill-opacity="{o}" stroke="{NAVY2}" stroke-opacity=".55" stroke-width="3"/>'
            f'<path d="M{x+w*.18} {y+h*.08} L{x+w*.42} {y+h*.08} L{x+w*.12} {y+h*.62} L{x+w*.06} {y+h*.62} Z" fill="#fff" opacity=".45"/>'
            f'<path d="M{x+w*.5} {y+h*.1} L{x+w*.58} {y+h*.1} L{x+w*.3} {y+h*.6} L{x+w*.26} {y+h*.6} Z" fill="#fff" opacity=".3"/>')

def _room(t, floor=470):
    return (f'<rect width="800" height="600" fill="{t[2]}"/>'
            f'<rect y="{floor}" width="800" height="{600-floor}" fill="#DCE8F3"/>'
            f'<rect y="{floor}" width="800" height="6" fill="{MID}"/>')

def _tiles(x, y, w, h):
    s = ''
    for i in range(int(w // 60) + 1):
        s += f'<line x1="{x+i*60}" y1="{y}" x2="{x+i*60}" y2="{y+h}" stroke="#D3E2EF" stroke-width="2"/>'
    for j in range(int(h // 60) + 1):
        s += f'<line x1="{x}" y1="{y+j*60}" x2="{x+w}" y2="{y+j*60}" stroke="#D3E2EF" stroke-width="2"/>'
    return s

def art(kind, v=0):
    t = TINTS[v % 3]
    g = ''
    if kind in ('box', 'box2'):
        g += _room(t) + _tiles(180, 60, 440, 410)
        g += f'<path d="M520 110 h40 v20" fill="none" stroke="{NAVY2}" stroke-width="8" stroke-linecap="round"/><circle cx="560" cy="140" r="16" fill="{NAVY2}"/>'
        if kind == 'box':
            g += f'<rect x="180" y="96" width="440" height="10" rx="3" fill="{NAVY2}"/>' + _glass(186, 106, 220, 360, t) + _glass(392, 112, 222, 354, t)
            g += f'<rect x="400" y="260" width="8" height="70" rx="4" fill="{NAVY2}"/>'
        else:
            g += f'<path d="M180 470 L330 420 L330 70 L180 100 Z" fill="{t[0]}" fill-opacity="{t[1]}" stroke="{NAVY2}" stroke-width="3"/>'
            g += _glass(330, 70, 290, 350, t) + f'<rect x="330" y="62" width="290" height="10" rx="3" fill="{NAVY2}"/>'
    elif kind == 'mirror':
        g += _room(t, 500) + f'<rect x="150" y="380" width="500" height="120" rx="8" fill="#FFFFFF" stroke="#C9DAEA" stroke-width="3"/><rect x="330" y="360" width="140" height="26" rx="12" fill="#F2F6FA" stroke="#C9DAEA" stroke-width="3"/>'
        g += f'<rect x="200" y="70" width="400" height="270" rx="10" fill="#CFE3F4" stroke="#9DBBD6" stroke-width="10"/><rect x="214" y="84" width="372" height="242" rx="4" fill="#E8F3FC"/>'
        g += f'<path d="M260 100 L330 100 L240 300 L220 300 Z" fill="#fff" opacity=".7"/><path d="M380 100 L405 100 L330 270 L318 270 Z" fill="#fff" opacity=".5"/>'
    elif kind == 'door':
        g += _room(t) + f'<rect x="250" y="60" width="300" height="410" fill="none" stroke="{NAVY2}" stroke-width="10"/>' + _glass(260, 70, 280, 400, t, 0)
        g += f'<rect x="500" y="230" width="10" height="90" rx="5" fill="{NAVY}"/><rect x="250" y="250" width="300" height="10" fill="{NAVY2}" opacity=".25"/>'
    elif kind == 'window':
        g += _room(t, 520) + f'<rect x="170" y="90" width="460" height="320" fill="#BFE0F8"/><path d="M170 330 Q300 260 420 310 T630 290 V410 H170 Z" fill="#8CC0E6"/>'
        g += f'<rect x="170" y="90" width="460" height="320" fill="none" stroke="{NAVY2}" stroke-width="12"/>' + _glass(176, 96, 228, 308, t, 0) + _glass(396, 96, 228, 308, t, 0)
        g += f'<rect x="150" y="410" width="500" height="18" rx="4" fill="#C9DAEA"/>'
    elif kind == 'rail':
        g += f'<rect width="800" height="600" fill="#CDE6F8"/><rect y="250" width="800" height="120" fill="#7FB7E3"/><path d="M0 250 Q200 230 400 250 T800 245 V250 H0Z" fill="#9CC9EC"/>'
        g += f'<rect y="440" width="800" height="160" fill="#E4EDF5"/><rect y="440" width="800" height="10" fill="{NAVY2}" opacity=".5"/>'
        for i in range(4):
            g += _glass(40 + i * 185, 250, 175, 190, t, 0)
        g += f'<rect x="30" y="236" width="740" height="16" rx="8" fill="#C4CED8"/>'
    elif kind == 'balcony':
        g += f'<rect width="800" height="600" fill="#E9F2FB"/><rect x="120" y="40" width="560" height="560" fill="#F7FAFD" stroke="#C9DAEA" stroke-width="4"/>'
        for row in (80, 330):
            g += f'<rect x="150" y="{row+200}" width="500" height="14" fill="#C9DAEA"/>'
            for i in range(5):
                g += _glass(156 + i * 98, row + 20, 96, 180, t, 0)
            g += f'<rect x="150" y="{row+10}" width="500" height="10" fill="{NAVY2}" opacity=".7"/>'
    elif kind == 'veranda':
        g += f'<rect width="800" height="600" fill="#DDEFFC"/><rect y="470" width="800" height="130" fill="#9CCB8F"/><rect x="140" y="200" width="520" height="270" fill="#FFFFFF" stroke="#C9DAEA" stroke-width="4"/>'
        g += f'<path d="M110 200 L400 90 L690 200 Z" fill="{t[0]}" fill-opacity="{t[1]+.1}" stroke="{NAVY2}" stroke-width="4"/>'
        g += _glass(170, 250, 150, 220, t, 0) + _glass(325, 250, 150, 220, t, 0) + _glass(480, 250, 150, 220, t, 0)
    elif kind == 'tempered':
        g += f'<rect width="800" height="600" fill="{t[2]}"/>'
        for i in range(3):
            g += f'<g transform="translate({140+i*40} {80+i*40}) skewY(-6)">' + _glass(0, 0, 380, 300, t, 6) + '</g>'
        g += f'<rect x="560" y="420" width="160" height="64" rx="14" fill="{NAVY}"/><text x="640" y="462" font-family="Arial" font-size="30" font-weight="700" fill="#fff" text-anchor="middle">8 mm</text>'
    elif kind == 'laminated':
        g += f'<rect width="800" height="600" fill="{t[2]}"/>'
        g += f'<rect x="120" y="150" width="560" height="90" rx="6" fill="{t[0]}" fill-opacity="{t[1]+.1}" stroke="{NAVY2}" stroke-width="3"/>'
        g += f'<rect x="120" y="244" width="560" height="22" fill="{SKY}" opacity=".85"/>'
        g += f'<rect x="120" y="270" width="560" height="90" rx="6" fill="{t[0]}" fill-opacity="{t[1]+.1}" stroke="{NAVY2}" stroke-width="3"/>'
        g += f'<text x="400" y="430" font-family="Arial" font-size="28" font-weight="700" fill="{NAVY}" text-anchor="middle">vidro + película PVB + vidro</text>'
    elif kind == 'partition':
        g += _room(t) + f'<rect x="80" y="60" width="640" height="10" fill="{NAVY2}"/><rect x="80" y="464" width="640" height="8" fill="{NAVY2}"/>'
        g += _glass(84, 70, 200, 394, t, 0) + _glass(292, 70, 200, 394, t, 0) + _glass(500, 70, 216, 394, t, 0)
        g += f'<rect x="84" y="240" width="632" height="26" fill="#fff" opacity=".55"/><rect x="470" y="250" width="8" height="80" rx="4" fill="{NAVY}"/>'
    elif kind == 'table':
        g += _room(t, 430) + f'<ellipse cx="400" cy="300" rx="280" ry="70" fill="{t[0]}" fill-opacity="{t[1]+.15}" stroke="{NAVY2}" stroke-width="4"/>'
        g += f'<path d="M380 320 L360 520 M420 320 L440 520" stroke="{NAVY2}" stroke-width="16" stroke-linecap="round"/><ellipse cx="330" cy="285" rx="80" ry="12" fill="#fff" opacity=".6"/>'
    elif kind == 'install':
        g += _room(t, 520) + f'<rect x="160" y="80" width="420" height="380" fill="none" stroke="{NAVY2}" stroke-width="14"/>'
        g += f'<g transform="rotate(-8 400 280)">' + _glass(200, 110, 360, 330, t, 0) + f'<circle cx="380" cy="270" r="34" fill="{NAVY}"/><rect x="372" y="200" width="16" height="50" rx="6" fill="{NAVY}"/></g>'
    elif kind == 'tools':
        g += f'<rect width="800" height="600" fill="{t[2]}"/>' + _glass(80, 90, 280, 400, t, 4)
        g += f'<rect x="80" y="70" width="280" height="22" rx="6" fill="{NAVY2}"/><circle cx="150" cy="81" r="18" fill="#fff" stroke="{NAVY}" stroke-width="6"/><circle cx="290" cy="81" r="18" fill="#fff" stroke="{NAVY}" stroke-width="6"/>'
        g += f'<g transform="translate(470 180) rotate(35)"><rect x="-14" y="0" width="28" height="200" rx="10" fill="{NAVY}"/><path d="M-40 -10 a40 40 0 1 1 80 0 l-20 0 a20 20 0 1 0 -40 0 Z" fill="{NAVY2}"/></g>'
        g += f'<circle cx="610" cy="420" r="60" fill="#fff" stroke="{SKY}" stroke-width="16"/><circle cx="610" cy="420" r="18" fill="{NAVY}"/>'
    else:  # genérico
        g += _room(t) + _glass(200, 80, 400, 380, t)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img">{g}</svg>'

LOGO_MARK = ('<svg class="logo-mark" viewBox="0 0 48 48" aria-hidden="true"><rect x="2" y="2" width="44" height="44" rx="11" fill="#0A2342"/>'
             '<rect x="10" y="10" width="28" height="28" rx="3" fill="#5DA9E9" fill-opacity=".35" stroke="#8EC5F0" stroke-width="2"/>'
             '<path d="M15 33 L30 13 L35 13 L20 33 Z" fill="#fff" opacity=".85"/><path d="M26 33 L35 21 L35 26 L30 33 Z" fill="#fff" opacity=".55"/></svg>')

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect x="2" y="2" width="44" height="44" rx="11" fill="#0A2342"/>'
           '<rect x="10" y="10" width="28" height="28" rx="3" fill="#5DA9E9" fill-opacity=".35" stroke="#8EC5F0" stroke-width="2"/>'
           '<path d="M15 33 L30 13 L35 13 L20 33 Z" fill="#fff" opacity=".85"/></svg>')
