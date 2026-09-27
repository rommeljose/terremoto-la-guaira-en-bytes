#!/usr/bin/env python3
"""Da un id estable a cada <h2> de metodo/ y a cada <section> de la portada.

El id se deriva del texto del encabezado (sin tildes, en minúsculas y con
guiones). Es idempotente: si el id ya existe, no lo toca. Se ejecuta desde la
raíz del repositorio.
"""
import re, html, unicodedata, pathlib, sys

def slug(t):
    t = re.sub(r'(?s)<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = unicodedata.normalize('NFD', t)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = t.lower().replace('ñ', 'n')
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return re.sub(r'-+', '-', t)[:48] or 'seccion'

def unicos(base, usados):
    s, n = base, 2
    while s in usados:
        s, n = f'{base}-{n}', n + 1
    usados.add(s)
    return s

def procesar(p, patron, plantilla):
    s = orig = p.read_text(encoding='utf-8')
    usados = set(re.findall(r'\bid="([^"]+)"', s))
    salida, pos = [], 0
    for m in re.finditer(patron, s):
        salida.append(s[pos:m.start()])
        if 'id=' in m.group(0).split('>')[0]:
            salida.append(m.group(0))
        else:
            salida.append(plantilla(m, unicos(slug(m.group('t')), usados)))
        pos = m.end()
    salida.append(s[pos:])
    s = ''.join(salida)
    if s != orig:
        p.write_text(s, encoding='utf-8')
        return True
    return False

raiz = pathlib.Path(__file__).resolve().parent.parent
tocados = 0

# páginas internas: <h2><span class="no">N</span> Título</h2> y <h3 class="sub-h">
for p in sorted((raiz / 'metodo').glob('*.html')):
    cambio = procesar(p, r'<h2(?P<attrs>[^>]*)>(?P<t>.*?)</h2>',
                      lambda m, i: f'<h2 id="{i}"{m.group("attrs")}>{m.group("t")}</h2>')
    cambio |= procesar(p, r'<h3(?P<attrs>(?: [^>]*)?)>(?P<t>.*?)</h3>',
                       lambda m, i: f'<h3 id="{i}"{m.group("attrs")}>{m.group("t")}</h3>')
    if cambio:
        tocados += 1

# portada: <section> ... <div class="sh"><span class="n">NN</span><h2>Título</h2>
p = raiz / 'index.html'
if procesar(p, r'<section>(?P<resto>\s*<div class="sh"><span class="n">(?P<n>\d+)</span><h2>(?P<t>.*?)</h2>)',
            lambda m, i: f'<section id="{m.group("n")}-{i}">{m.group("resto")}'):
    tocados += 1

print(f'{tocados} archivos actualizados')
