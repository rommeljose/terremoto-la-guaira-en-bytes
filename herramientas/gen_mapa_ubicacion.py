#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el mapa de ubicación de la portada (SVG en línea, sin dependencias).

Produce `assets/mapa_ubicacion.svg`, que index.html incrusta tal cual para que
herede el tema claro/oscuro de la página a través de las clases `.mp-*`.

Dos paneles:
  · principal — costa central de Venezuela, las trazas de falla activas
    cercanas, el sistema Puerto Cabello + San Sebastián sobre el que discurre
    la secuencia, y los dos epicentros del catálogo USGS.
  · recuadro  — el Caribe y el norte de Suramérica, para situar al lector que
    no conozca la región, con el marco del panel principal.

Datos de entrada, todos en `herramientas/datos/` (ver README):
  costa_10m_zoom.json     Natural Earth 1:10 m, recortada  (dominio público)
  costa_50m_region.json   Natural Earth 1:50 m, recortada  (dominio público)
  fallas_cercanas.json    trazas de fallas activas (proyecto Red de Emergencia)
  traza_principal.json    el sistema Puerto Cabello + San Sebastián, con las
                          anclas de los dos hipocentros sobre el eje s

Ejecutar desde la raíz del repositorio:  python3 herramientas/gen_mapa_ubicacion.py
"""
import json, math, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent
DAT  = RAIZ / "datos"
SAL  = RAIZ.parent / "assets" / "mapa_ubicacion.svg"

# --- epicentros del catálogo USGS (codigo/common.py del repositorio de análisis)
EPI = [("us6000t7zc", "M 7,2", 10.3713, -68.5564),
       ("us6000t7zp", "M 7,5", 10.6221, -67.1935)]

# --- localidades de referencia (dx, dy: desplazamiento del rótulo en píxeles)
CIUDADES = [("Puerto Cabello", 10.4731, -68.0125,   8, 14),
            ("Morón",          10.4869, -68.1958,  -7, -8, "fin"),
            ("Valencia",       10.1620, -68.0077,   7,  5),
            ("Maracay",        10.2469, -67.5958,   7,  5),
            ("La Victoria",    10.2272, -67.3306,   7, 13),
            ("Caracas",        10.4806, -66.9036,   8, 15),
            ("La Guaira",      10.5997, -66.9344,  10, -11),
            ("Higuerote",      10.4833, -66.0967,  -7,  5, "fin")]

# ---------------------------------------------------------------- geometría
def marco(lon0, lon1, lat0, lat1, ancho, x0, y0):
    """Proyección equirectangular local; devuelve la función lon,lat -> px,py."""
    latm = (lat0 + lat1) / 2.0
    k = math.cos(math.radians(latm))
    w, h = (lon1 - lon0) * k, (lat1 - lat0)
    sc = ancho / w
    def p(lon, lat):
        return (x0 + (lon - lon0) * k * sc, y0 + (lat1 - lat) * sc)
    return p, ancho, h * sc, sc, k

def camino(pts, p, dec=1):
    d = []
    for i, (lon, lat) in enumerate(pts):
        x, y = p(lon, lat)
        d.append("%s%.*f %.*f" % ("M" if i == 0 else "L", dec, x, dec, y))
    return " ".join(d)

def km_por_grado(lat):
    return 111.32 * math.cos(math.radians(lat)), 110.57

# ---------------------------------------------------------------- lienzo
W, H = 1040, 600
MX, MY = 0, 0
ZOOM = (-69.15, -65.55, 9.62, 11.32)      # lon0, lon1, lat0, lat1
pz, zw, zh, zsc, zk = marco(*ZOOM, ancho=W, x0=MX, y0=MY)
H = int(round(zh))

o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
  'role="img" aria-labelledby="mp-tit mp-des" class="mapa-ubic">' % (W, H))
a('<title id="mp-tit">Mapa de ubicación de la secuencia sísmica del 24 de junio de 2026</title>')
a('<desc id="mp-des">Costa central de Venezuela. Se muestran las trazas de fallas activas, '
  'el sistema Puerto Cabello + San Sebastián sobre el que discurre la secuencia, los dos '
  'epicentros del catálogo USGS (M 7,2 al oeste y M 7,5 al este, separados 158 kilómetros '
  'medidos sobre la falla) y las localidades de referencia. Un recuadro sitúa la zona en el '
  'Caribe y el norte de Suramérica.</desc>')

# Todo el panel principal se recorta al marco: la costa continental entra y sale
# de él, y sin recorte los tramos de fuera (Paraguaná, Curazao) desbordarían.
a('<clipPath id="mp-clip-pral"><rect x="0" y="0" width="%d" height="%d"/></clipPath>' % (W, H))
a('<g clip-path="url(#mp-clip-pral)">')

# ---- mar: la costa continental, recortada en longitud al marco y cerrada por el
# borde superior. Fuera de ese rango la costa se sale de la caja, y cerrarla sobre
# sus extremos brutos dejaba esquinas de mar sin pintar.
costa = json.load(open(DAT / "costa_10m_zoom.json"))
costa.sort(key=len, reverse=True)
princ = costa[0]
if princ[0][0] > princ[-1][0]:
    princ = princ[::-1]

def recorta_lon(pts, lo0, lo1):
    """Tramo continuo de costa dentro de la franja de longitudes, con los extremos
    interpolados justo sobre los bordes del marco."""
    idx = [i for i, (lon, _) in enumerate(pts) if lo0 <= lon <= lo1]
    i0, i1 = idx[0], idx[-1]
    def cruce(pa, pb, lon):
        t = (lon - pa[0]) / (pb[0] - pa[0])
        return [lon, pa[1] + t * (pb[1] - pa[1])]
    tramo = pts[i0:i1 + 1]
    if i0 > 0:            tramo = [cruce(pts[i0 - 1], pts[i0], lo0)] + tramo
    if i1 < len(pts) - 1: tramo = tramo + [cruce(pts[i1], pts[i1 + 1], lo1)]
    return tramo

princ = recorta_lon(princ, ZOOM[0], ZOOM[1])
d = camino(princ, pz)
a('<path class="mp-mar" d="%s L%d %d L%d %d Z"/>' % (d, W, MY, MX, MY))
a('<path class="mp-costa" d="%s"/>' % d)
for seg in costa[1:]:
    cerrada = abs(seg[0][0] - seg[-1][0]) < 1e-6 and abs(seg[0][1] - seg[-1][1]) < 1e-6
    a('<path class="mp-costa %s" d="%s%s"/>'
      % ("mp-isla" if cerrada else "mp-isla-abierta", camino(seg, pz), " Z" if cerrada else ""))

# ---- fallas activas del entorno
for f in json.load(open(DAT / "fallas_cercanas.json")):
    a('<path class="mp-falla" d="%s"/>' % camino(f["pts"], pz))

# ---- el sistema sobre el que discurre la secuencia
tr = json.load(open(DAT / "traza_principal.json"))
pts = [(lon, lat) for lat, lon in tr["puntos"]]          # el fichero va (lat, lon)

def en_s(s_obj):
    """Punto (lon, lat) a la distancia s_obj km a lo largo de la traza."""
    S, P = tr["s"], pts
    for i in range(len(S) - 1):
        if S[i] <= s_obj <= S[i + 1]:
            t = (s_obj - S[i]) / (S[i + 1] - S[i])
            return (P[i][0] + t * (P[i + 1][0] - P[i][0]),
                    P[i][1] + t * (P[i + 1][1] - P[i][1]))
    return P[-1]

# ---- tramo entre los dos hipocentros, medido sobre la traza
s1, s2 = tr["anclas"]["us6000t7zc"]["s"], tr["anclas"]["us6000t7zp"]["s"]
sub = [en_s(s1)] + [p for p, s in zip(pts, tr["s"]) if s1 < s < s2] + [en_s(s2)]
a('<path class="mp-tramo" d="%s"/>' % camino(sub, pz))          # halo, debajo
a('<path class="mp-traza" d="%s"/>' % camino(pts, pz))          # la traza, encima
xu, yu = pz(*en_s(tr["union_s"]))                               # unión de las dos fallas
a('<circle class="mp-union" cx="%.1f" cy="%.1f" r="4"/>' % (xu, yu))
xm, ym = pz(*en_s((s1 + s2) / 2))
a('<text class="mp-cota" x="%.1f" y="%.1f" text-anchor="middle">%.0f km sobre la falla</text>'
  % (xm, ym - 36, s2 - s1))

# ---- epicentros
def estrella(cx, cy, r):
    p = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.42
        p.append("%.1f,%.1f" % (cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return " ".join(p)

for eid, rot, lat, lon in EPI:
    x, y = pz(lon, lat)
    a('<polygon class="mp-epi" points="%s"/>' % estrella(x, y, 11))
    a('<text class="mp-epi-rot" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
      % (x, y - 16, rot))

# ---- localidades
for c in CIUDADES:
    nom, lat, lon, dx, dy = c[:5]
    anc = "end" if len(c) > 5 else "start"
    x, y = pz(lon, lat)
    a('<circle class="mp-ciudad" cx="%.1f" cy="%.1f" r="3.2"/>' % (x, y))
    a('<text class="mp-ciudad-rot" x="%.1f" y="%.1f" text-anchor="%s">%s</text>'
      % (x + dx, y + dy, anc, nom))

# ---- rótulos de contexto
a('<text class="mp-agua" x="%.1f" y="%.1f">MAR CARIBE</text>' % pz(-68.75, 11.12))
a('<text class="mp-tierra-rot" x="%.1f" y="%.1f">VENEZUELA</text>' % pz(-67.25, 9.82))

# ---- leyenda
lx, ly = 42, H - 122
a('<g class="mp-leyenda">')
a('<polygon class="mp-epi" points="%s"/>' % estrella(lx + 8, ly, 8))
a('<text class="mp-ley-txt" x="%d" y="%d">epicentro del catálogo USGS</text>' % (lx + 30, ly + 4))
a('<path class="mp-traza" d="M%d %d H%d"/>' % (lx, ly + 22, lx + 22))
a('<text class="mp-ley-txt" x="%d" y="%d">sistema Puerto Cabello + San Sebastián (296 km)</text>'
  % (lx + 30, ly + 26))
a('<path class="mp-falla" d="M%d %d H%d"/>' % (lx, ly + 44, lx + 22))
a('<text class="mp-ley-txt" x="%d" y="%d">otras trazas de fallas activas</text>' % (lx + 30, ly + 48))
a('</g>')

# ---- escala y norte
kx, ky = km_por_grado((ZOOM[2] + ZOOM[3]) / 2)
px_km = zsc * zk / kx                      # píxeles por km en horizontal
L = 50.0 * px_km
bx, by = 42, H - 34
a('<g class="mp-escala"><path d="M%.1f %.1f H%.1f M%.1f %.1f V%.1f M%.1f %.1f V%.1f"/>'
  '<text x="%.1f" y="%.1f" text-anchor="middle">50 km</text></g>'
  % (bx, by, bx + L, bx, by - 5, by + 5, bx + L, by - 5, by + 5, bx + L / 2, by - 11))
nx, ny = W - 46, 40
a('<g class="mp-norte"><path d="M%d %d L%d %d L%d %d Z"/>'
  '<text x="%d" y="%d" text-anchor="middle">N</text></g>'
  % (nx, ny - 18, nx - 7, ny + 4, nx + 7, ny + 4, nx, ny + 22))

a('</g>')   # fin del panel principal recortado

# ---------------------------------------------------------------- recuadro regional
RW = 232
REG = (-84.0, -58.0, -1.5, 19.5)
rx0, ry0 = W - RW - 14, H - 14
pr, rw, rh, rsc, rk = marco(*REG, ancho=RW, x0=rx0, y0=0)
ry0 = H - rh - 14
pr, rw, rh, rsc, rk = marco(*REG, ancho=RW, x0=rx0, y0=ry0)
a('<g class="mp-inset">')
a('<rect class="mp-inset-caja" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
  % (rx0, ry0, rw, rh))
a('<clipPath id="mp-clip"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/></clipPath>'
  % (rx0, ry0, rw, rh))
a('<g clip-path="url(#mp-clip)">')
for seg in json.load(open(DAT / "costa_50m_region.json")):
    a('<path class="mp-costa-reg" d="%s"/>' % camino(seg, pr, dec=1))
x1, y1 = pr(ZOOM[0], ZOOM[3]); x2, y2 = pr(ZOOM[1], ZOOM[2])
a('<rect class="mp-marco-zoom" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
  % (x1, y1, x2 - x1, y2 - y1))
a('<text class="mp-inset-rot" x="%.1f" y="%.1f">Caribe</text>' % pr(-77.0, 16.2))
a('<text class="mp-inset-rot" x="%.1f" y="%.1f">Venezuela</text>' % pr(-67.5, 7.4))
a('<text class="mp-inset-rot" x="%.1f" y="%.1f">Colombia</text>' % pr(-75.5, 5.0))
a('<text class="mp-inset-rot" x="%.1f" y="%.1f">Brasil</text>' % pr(-64.0, 1.2))
a('</g>')
a('<text class="mp-inset-pie" x="%.1f" y="%.1f" text-anchor="end">el recuadro rojo es '
  'este mapa</text>' % (rx0 + rw, ry0 - 7))
a('</g>')

a('</svg>')
SAL.write_text("\n".join(o), encoding="utf-8")
print("escrito %s  (%.1f kB)" % (SAL, SAL.stat().st_size / 1024))
