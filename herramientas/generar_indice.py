#!/usr/bin/env python3
"""Construye assets/buscar.json, el índice del buscador del sitio.

Recorre la portada y las páginas de metodo/, parte cada una por sus encabezados
con ancla y guarda un registro por sección: página, título, ancla, encabezado y
texto plano. No hace falta servidor: el buscador lo lee desde el navegador.
Ejecutar desde la raíz del repositorio; es determinista.
"""
import re, html, json, pathlib, unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'assets' / 'buscar.json'

def limpiar(frag):
    """HTML -> texto plano legible, sin fórmulas ni marcado."""
    f = re.sub(r'(?is)<(script|style|svg|canvas|iframe)\b.*?</\1>', ' ', frag)
    f = re.sub(r'(?is)<figcaption\b', ' <figcaption', f)      # los pies sí se indexan
    f = re.sub(r'(?s)\$\$.*?\$\$', ' ', f)                    # matemática en bloque
    f = re.sub(r'(?s)\\\[.*?\\\]', ' ', f)
    f = re.sub(r'\$[^$\n]{1,120}\$', ' ', f)                  # matemática en línea
    f = re.sub(r'(?s)<[^>]+>', ' ', f)
    f = html.unescape(f)
    f = f.replace('­', '').replace('​', '')
    return re.sub(r'\s+', ' ', f).strip()

def titulo(s, defecto):
    m = re.search(r'(?is)<title>(.*?)</title>', s)
    return limpiar(m.group(1)) if m else defecto

def secciones(ruta, url):
    s = ruta.read_text(encoding='utf-8')
    # estas páginas no llevan <body>: se corta por </head> para no indexar el <title>
    cuerpo = s.split('<body', 1)[-1] if '<body' in s else s.split('</head>', 1)[-1]
    tit = titulo(s, url)
    marcas = [(m.start(), m.group('id'), limpiar(m.group('t')), m.group(0)[2])
              for m in re.finditer(
                  r'<(?P<tag>h2|h3|section)\s[^>]*id="(?P<id>[^"]+)"[^>]*>(?P<t>.*?)</(?P=tag)>',
                  cuerpo, re.S)]
    # la portada ancla en <section>: el encabezado va dentro, se toma del .sh
    out = []
    for i, (pos, anc, txt, nivel) in enumerate(marcas):
        fin = marcas[i + 1][0] if i + 1 < len(marcas) else len(cuerpo)
        frag = cuerpo[pos:fin]
        enc = crudo = txt
        if nivel == 'e':                                       # <section> de la portada
            m = re.search(r'(?s)<div class="sh">.*?<h2>(.*?)</h2>', frag)
            crudo = limpiar(m.group(1)) if m else anc
            num = re.match(r'(\d+)-', anc)
            enc = f'{num.group(1)} · {crudo}' if num else crudo
        texto = limpiar(frag)
        # el texto de la sección no repite su propio encabezado (ni su número)
        sinnum = lambda x: re.sub(r'^\s*\d{1,2}\s*[·.\-]?\s*', '', x)
        for a_, b_ in ((texto, crudo), (sinnum(texto), sinnum(crudo))):
            if b_ and a_.startswith(b_):
                texto = a_[len(b_):].lstrip(' ·—-')
                break
        if len(texto) < 40:
            continue
        out.append({'u': f'{url}#{anc}', 'p': tit, 'h': enc,
                    'n': 2 if nivel in ('2', 'e') else 3, 't': texto})
    # preámbulo de la página (lo que va antes del primer encabezado anclado)
    if marcas:
        pre = limpiar(cuerpo[:marcas[0][0]])
        if pre.startswith(tit):                                # el <title> repetido
            pre = pre[len(tit):].lstrip(' ·—-')
        pre = re.sub(r'^\s*←[^·]{0,40}', '', pre).lstrip(' ·—-')   # el enlace de vuelta
        pre = re.sub(r'^\s*◐\s*tema\s*', '', pre)                  # el conmutador de tema
        if len(pre) > 120:
            out.insert(0, {'u': url, 'p': tit, 'h': tit, 'n': 1, 't': pre})
    return out

reg = []
reg += secciones(RAIZ / 'index.html', 'index.html')
for p in sorted((RAIZ / 'metodo').glob('*.html')):
    reg += secciones(p, f'metodo/{p.name}')

SALIDA.write_text(json.dumps(reg, ensure_ascii=False, separators=(',', ':')),
                  encoding='utf-8')
pal = sum(len(r['t'].split()) for r in reg)
print(f'{len(reg)} secciones · {pal} palabras · {SALIDA.stat().st_size/1024:.0f} KB '
      f'-> {SALIDA.relative_to(RAIZ)}')
