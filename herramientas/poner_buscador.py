#!/usr/bin/env python3
"""Inserta el buscador (assets/buscar.js) en la portada y en metodo/*.html.

Idempotente: si la etiqueta ya está, no la duplica. Ejecutar desde la raíz.
"""
import pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MARCA = 'assets/buscar.js'

def poner(p, base):
    s = p.read_text(encoding='utf-8')
    if MARCA in s:
        return False
    tag = f'<script defer src="{base}/assets/buscar.js" data-base="{base}"></script>\n'
    if '</body>' in s:
        s = s.replace('</body>', tag + '</body>', 1)
    else:                                   # estas páginas cierran sin </body>
        s = s.rstrip() + '\n' + tag
    p.write_text(s, encoding='utf-8')
    return True

n = poner(RAIZ / 'index.html', '.')
for q in sorted((RAIZ / 'metodo').glob('*.html')):
    n += poner(q, '..')
print(f'{n} páginas con buscador')
