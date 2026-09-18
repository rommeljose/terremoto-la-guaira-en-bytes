# -*- coding: utf-8 -*-
"""Tarjeta social (Open Graph / Twitter) de bytes.sigeos.org.

Escribe assets/og_card.png a 1200x630, que es la relacion 1,91:1 que piden
Facebook, LinkedIn, WhatsApp, Telegram, Slack y X.

La franja de mapa NO es decoracion: se dibuja con los mismos datos que el mapa
de ubicacion de la seccion 01 -- costa de Natural Earth, traza del enlace
San Sebastian-Moron-Bocono y las dos anclas de los hipocentros del USGS.

Uso (desde la raiz del repositorio):  python3 herramientas/gen_tarjeta_og.py
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'herramientas', 'datos')
SALIDA = os.path.join(RAIZ, 'assets', 'og_card.png')

W, H = 1200, 630

# paleta: el tema oscuro de la hoja (:root[data-theme="dark"])
PAPER = (19, 28, 43)        # --paper  #131c2b
MAR = (13, 43, 72)          # --mar, algo mas azul para que se separe de la tierra
TIERRA = (22, 30, 45)
INK = (230, 237, 246)       # --ink    #e6edf6
STRONG = (246, 249, 253)    # --strong #f6f9fd
MUTED = (147, 164, 188)     # --muted  #93a4bc
LINE = (38, 50, 74)         # --line   #26324a
ORANGE = (242, 129, 74)     # --orange #f2814a
BLUE = (99, 182, 220)       # --blue   #63b6dc

# franja de mapa
MAPA_Y0, MAPA_Y1 = 330, 542
LON0, LON1 = -69.05, -65.65
LAT_MID = 10.50

FUENTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'


def fnt(variante, px):
    return ImageFont.truetype(FUENTE % variante, px)


def carga(nombre):
    with open(os.path.join(DATOS, nombre), encoding='utf-8') as fh:
        return json.load(fh)


# ---- proyeccion equirectangular local, ajustada a la franja ---------------------------------
COSLAT = math.cos(math.radians(LAT_MID))
ESCALA = W / ((LON1 - LON0) * COSLAT)          # px por grado de longitud-equivalente
LAT_SPAN = (MAPA_Y1 - MAPA_Y0) / ESCALA        # la franja recorta en latitud, no en longitud
LAT1 = LAT_MID + LAT_SPAN / 2


def proy(lon, lat):
    return ((lon - LON0) * COSLAT * ESCALA, MAPA_Y0 + (LAT1 - lat) * ESCALA)


def poli(seg):
    return [proy(lon, lat) for lon, lat in seg]


# ---- lienzo ----------------------------------------------------------------------------------
img = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(img)

# franja de mapa: mar de fondo, tierra recortada por la costa
d.rectangle([0, MAPA_Y0, W, MAPA_Y1], fill=MAR)

banda = Image.new('RGB', (W, MAPA_Y1 - MAPA_Y0), MAR)
bd = ImageDraw.Draw(banda)


def poli_banda(seg):
    return [(x, y - MAPA_Y0) for x, y in poli(seg)]


# la costa continental: se cierra por abajo para pintar tierra firme
for seg in carga('costa_10m_zoom.json'):
    pts = poli_banda(seg)
    if len(pts) < 2:
        continue
    if max(p[1] for p in pts) > 0:                      # solo lo que toca la franja
        cerrado = pts + [(pts[-1][0], MAPA_Y1 - MAPA_Y0 + 40),
                         (pts[0][0], MAPA_Y1 - MAPA_Y0 + 40)]
        bd.polygon(cerrado, fill=TIERRA)

for seg in carga('costa_10m_zoom.json'):
    pts = poli_banda(seg)
    if len(pts) > 1:
        bd.line(pts, fill=(72, 96, 128), width=2, joint='curve')

# fallas del entorno, en gris tenue
for tr in carga('fallas_cercanas.json'):
    pts = poli_banda(tr['pts'] if isinstance(tr, dict) else tr)
    if len(pts) > 1:
        bd.line(pts, fill=(56, 72, 102), width=2, joint='curve')

# la traza principal
traza = carga('traza_principal.json')
pts_tr = poli_banda([(lon, lat) for lat, lon in traza['puntos']])
bd.line(pts_tr, fill=ORANGE, width=5, joint='curve')

img.paste(banda, (0, MAPA_Y0))
d = ImageDraw.Draw(img)

# filetes de la franja
d.line([(0, MAPA_Y0), (W, MAPA_Y0)], fill=LINE, width=1)
d.line([(0, MAPA_Y1), (W, MAPA_Y1)], fill=LINE, width=1)


def punto_en_s(s_obj):
    """Interpola sobre la traza la posicion de un ancla dada en km acumulados."""
    s = s_obj if isinstance(s_obj, (int, float)) else s_obj['s']
    ss, pp = traza['s'], traza['puntos']
    for i in range(len(ss) - 1):
        if ss[i] <= s <= ss[i + 1]:
            t = (s - ss[i]) / (ss[i + 1] - ss[i])
            return (pp[i][1] + t * (pp[i + 1][1] - pp[i][1]),
                    pp[i][0] + t * (pp[i + 1][0] - pp[i][0]))
    return (pp[-1][1], pp[-1][0])


def estrella(cx, cy, r, relleno):
    p = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.42
        p.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(p, fill=relleno, outline=PAPER)


f_eti = fnt('-Bold', 21)
for cod, etiqueta, dy in (('us6000t7zc', 'M 7,2', -34), ('us6000t7zp', 'M 7,5', -34)):
    lon, lat = punto_en_s(traza['anclas'][cod])
    x, y = proy(lon, lat)
    estrella(x, y, 15, ORANGE)
    w = d.textlength(etiqueta, font=f_eti)
    d.text((x - w / 2 + 1, y + dy + 1), etiqueta, font=f_eti, fill=(0, 0, 0))
    d.text((x - w / 2, y + dy), etiqueta, font=f_eti, fill=STRONG)

# la union de los dos segmentos cartografiados
lon_u, lat_u = punto_en_s(traza['union_s'])
xu, yu = proy(lon_u, lat_u)
d.ellipse([xu - 6, yu - 6, xu + 6, yu + 6], fill=BLUE, outline=PAPER, width=2)

# ---- texto -------------------------------------------------------------------------------------
X = 64
f_ceja = fnt('-Bold', 17)
f_tit = fnt('-Bold', 49)
f_sub = fnt('', 27)
f_pie = fnt('-Bold', 22)
f_pie2 = fnt('', 19)

ceja = 'A C A D E M I A   D E   G E O H I S T O R I A   D E L   E S T A D O   S U C R E'
d.text((X, 62), ceja, font=f_ceja, fill=MUTED)

y = 98
for linea in ('Análisis del terremoto de', 'La Guaira en bytes'):
    d.text((X, y), linea, font=f_tit, fill=STRONG)
    y += 58

d.rectangle([X, y + 18, X + 62, y + 21], fill=ORANGE)
d.text((X, y + 40), 'y su complejidad físico-matemática', font=f_sub, fill=INK)

# ---- pie ---------------------------------------------------------------------------------------
logo = Image.open(os.path.join(RAIZ, 'assets', 'logo_aghes.png')).convert('RGBA')
logo = logo.resize((46, 46), Image.LANCZOS)
img.paste(logo, (X, MAPA_Y1 + 22), logo)

d.text((X + 62, MAPA_Y1 + 23), 'bytes.sigeos.org', font=f_pie, fill=STRONG)
d.text((X + 62, MAPA_Y1 + 50), 'método, datos y reproducibilidad', font=f_pie2, fill=MUTED)

der = 'Doblete del 24-06-2026  ·  M 7,2 + M 7,5'
w = d.textlength(der, font=f_pie2)
d.text((W - X - w, MAPA_Y1 + 37), der, font=f_pie2, fill=MUTED)

img.save(SALIDA, optimize=True)
print('escrito %s  (%d x %d, %d bytes)'
      % (SALIDA, img.size[0], img.size[1], os.path.getsize(SALIDA)))
