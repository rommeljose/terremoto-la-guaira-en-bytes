# -*- coding: utf-8 -*-
"""Figura de la ley de escala para bytes.sigeos.org.

Ejecutar desde la raíz del repositorio:  python3 herramientas/gen_ley_escala.py

Panel a: duración de la fuente contra magnitud, con el corredor de la escala.
Panel b: la fuente múltiple de Caracas 1967 (Suárez y Nábělek, 1990, tabla 4)."""
import os

W, H = 760, 700
BG = "#fbfbf9"
MUT, GREY = "#5a6675", "#8a95a3"
BLU, RED, GRN, AMB = "#2b6cb0", "#d94d3a", "#2f9e6a", "#bf6a17"

srl = lambda M: 10 ** (-3.55 + 0.74 * M)
rld = lambda M: 10 ** (-2.57 + 0.62 * M)
tmin = lambda M: srl(M) / 3.0
tmax = lambda M: rld(M) / 2.5

o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"\n'
  ' aria-label="Dos paneles. Arriba, la duración de la fuente contra la magnitud: una franja verde marca la '
  'duración que la ley de escala concede a cada magnitud, entre la longitud de ruptura superficial dividida por '
  'tres kilómetros por segundo y la longitud en profundidad dividida por dos y medio. Los cuatro subeventos del '
  'sismo de Caracas de 1967 caen dentro de la franja; el sismo completo, magnitud 6,6, dura entre 57 y 65 '
  'segundos, de cuatro a nueve veces los 7 a 13 segundos que le corresponderían. La radiación del M 7,2 de La '
  'Guaira, 20 segundos, cae dentro de la franja, y la envolvente del par, unos 70 segundos, queda poco por '
  'encima. Abajo, la secuencia de Caracas 1967 en el tiempo: cuatro pulsos de 6, 9, 4 y 6 segundos separados por '
  'huecos sin radiación, repartidos a lo largo de 57 segundos y de 91 kilómetros.">')
a('<style>\n text{font-family:\'IBM Plex Sans\',Arial,Helvetica,sans-serif;font-size:12px;fill:#3a4553}'
  ' .t{font-size:11px;fill:#5a6675} .s{font-size:10px;fill:#5a6675}'
  ' .b{font-weight:700;fill:#182231} .hd{font-size:13px;font-weight:700;fill:#182231}\n</style>')
a(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
a('<defs>'
  f'<marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{RED}"/></marker>'
  '</defs>')
a('<text class="b" x="44" y="30" style="font-size:14px">La ley de escala: cuánto debe medir y cuánto debe durar cada magnitud</text>')
a('<text class="t" x="44" y="48">Longitudes de Wells y Coppersmith (1994) para falla de rumbo; duración τ ≈ L/V'
  '<tspan baseline-shift="sub" font-size="9">r</tspan>. Caracas 1967, de Suárez y Nábělek (1990, tabla 4).</text>')

# ------------------------------------------------------------------ panel a
X0, X1, Y0, Y1 = 96, 700, 112, 336
M0_, M1_, T1_ = 5.85, 7.75, 76.0
fx = lambda M: X0 + (M - M0_) / (M1_ - M0_) * (X1 - X0)
fy = lambda t: Y1 - t / T1_ * (Y1 - Y0)
a('<text class="hd" x="44" y="82">a · La duración delata el número de fuentes</text>')

ms = [M0_ + i * (M1_ - M0_) / 60 for i in range(61)]
up = " ".join(f"{fx(m):.1f},{fy(tmax(m)):.1f}" for m in ms)
lo = " ".join(f"{fx(m):.1f},{fy(tmin(m)):.1f}" for m in ms)
a(f'<polygon points="{up} {" ".join(reversed(lo.split()))}" fill="{GRN}" opacity=".18"/>')
a(f'<polyline points="{up}" fill="none" stroke="{GRN}" stroke-width="1.4"/>')
a(f'<polyline points="{lo}" fill="none" stroke="{GRN}" stroke-width="1.4"/>')
a(f'<text class="s" x="{fx(7.68):.0f}" y="{fy(tmax(7.68))+15:.0f}" text-anchor="end" style="fill:{GRN}">RLD / 2,5 km/s</text>')
a(f'<text class="s" x="{fx(7.68):.0f}" y="{fy(tmin(7.68))-7:.0f}" text-anchor="end" style="fill:{GRN}">SRL / 3,0 km/s</text>')
a(f'<text class="s" x="{X0+6}" y="{fy(74):.0f}" style="fill:{GRN};font-weight:600">franja verde: lo que la escala concede a una sola ruptura</text>')

a(f'<line x1="{X0}" y1="{Y1}" x2="{X1+18}" y2="{Y1}" stroke="{GREY}" stroke-width="1.2"/>')
a(f'<line x1="{X0}" y1="{Y1}" x2="{X0}" y2="{Y0-10}" stroke="{GREY}" stroke-width="1.2"/>')
for t in range(0, 80, 10):
    y = fy(t)
    a(f'<line x1="{X0-5}" y1="{y:.1f}" x2="{X0}" y2="{y:.1f}" stroke="{GREY}"/>')
    a(f'<text class="s" x="{X0-9}" y="{y+3.5:.1f}" text-anchor="end">{t}</text>')
a(f'<text class="s" x="{X0-34}" y="{(Y0+Y1)/2:.0f}" text-anchor="middle" transform="rotate(-90 {X0-34} {(Y0+Y1)/2:.0f})" style="font-weight:600">duración de la fuente (s)</text>')
for i in range(8):
    M = 6.0 + i * 0.25
    x = fx(M); mayor = abs(M * 2 - round(M * 2)) < 1e-9
    a(f'<line x1="{x:.1f}" y1="{Y1}" x2="{x:.1f}" y2="{Y1 + (6 if mayor else 3)}" stroke="{GREY}"/>')
    if mayor:
        a(f'<text class="s" x="{x:.1f}" y="{Y1+20}" text-anchor="middle">{("%.1f"%M).replace(".",",")}</text>')
a(f'<text class="s" x="{X1+18}" y="{Y1+20}" text-anchor="end" style="font-weight:600">M<tspan baseline-shift="sub" font-size="8">w</tspan></text>')

for M, t, n in [(6.26, 6, "1"), (6.37, 9, "2"), (6.01, 4, "3"), (6.07, 6, "4")]:
    a(f'<circle cx="{fx(M):.1f}" cy="{fy(t):.1f}" r="4.6" fill="{BLU}"/>')
    a(f'<text class="s" x="{fx(M):.1f}" y="{fy(t)-8:.1f}" text-anchor="middle" style="fill:{BLU};font-weight:600">{n}</text>')
a(f'<text class="s" x="{fx(5.92):.0f}" y="{fy(17):.0f}" style="fill:{BLU}">los cuatro subeventos de 1967, uno a uno</text>')

xc = fx(6.6)
a(f'<line x1="{xc:.1f}" y1="{fy(15):.1f}" x2="{xc:.1f}" y2="{fy(54):.1f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#ar)"/>')
a(f'<rect x="{xc-7:.1f}" y="{fy(65):.1f}" width="14" height="{fy(57)-fy(65):.1f}" fill="{RED}" opacity=".85"/>')
a(f'<text class="s" x="{xc-14:.1f}" y="{fy(65):.0f}" text-anchor="end" style="fill:{RED};font-weight:600">Caracas 1967 completo</text>')
a(f'<text class="s" x="{xc-14:.1f}" y="{fy(58):.0f}" text-anchor="end" style="fill:{RED}">M<tspan baseline-shift="sub" font-size="8">w</tspan> 6,6 · 57–65 s · de cuatro a nueve veces</text>')
a(f'<text class="s" x="{xc-14:.1f}" y="{fy(51):.0f}" text-anchor="end" style="fill:{RED}">los 7–13 s que le tocarían</text>')

a(f'<circle cx="{fx(7.2):.1f}" cy="{fy(20):.1f}" r="5" fill="{AMB}"/>')
a(f'<text class="s" x="{fx(7.2)+10:.1f}" y="{fy(20)+4:.1f}" style="fill:{AMB};font-weight:600">M 7,2 de La Guaira: 20 s</text>')
a(f'<circle cx="{fx(7.54):.1f}" cy="{fy(70):.1f}" r="5" fill="none" stroke="{AMB}" stroke-width="1.8"/>')
a(f'<text class="s" x="{fx(7.54)-11:.1f}" y="{fy(72):.0f}" text-anchor="end" style="fill:{AMB};font-weight:600">el par completo, ≈70 s:</text>')
a(f'<text class="s" x="{fx(7.54)-11:.1f}" y="{fy(66):.0f}" text-anchor="end" style="fill:{AMB}">aquí la duración sola no decide</text>')

# ------------------------------------------------------------------ panel b
BY, TX0, TX1, MH = 620, 96, 700, 88.0
gt = lambda s: TX0 + s / 70.0 * (TX1 - TX0)
a('<text class="hd" x="44" y="394">b · Caracas 1967 en el tiempo: cuatro fuentes, no una</text>')
a('<text class="t" x="44" y="412">Pulsos de liberación de momento. La altura es proporcional a M'
  '<tspan baseline-shift="sub" font-size="9">0</tspan>; la anchura, a la duración medida de cada uno.</text>')

a(f'<line x1="{TX0}" y1="{BY}" x2="{TX1+18}" y2="{BY}" stroke="{GREY}" stroke-width="1.2"/>')
for s in range(0, 71, 10):
    x = gt(s)
    a(f'<line x1="{x:.1f}" y1="{BY}" x2="{x:.1f}" y2="{BY+5}" stroke="{GREY}"/>')
    a(f'<text class="s" x="{x:.1f}" y="{BY+18}" text-anchor="middle">{s}</text>')
a(f'<text class="s" x="{(TX0+TX1)/2:.0f}" y="{BY+62}" text-anchor="middle" style="font-weight:600">segundos desde el inicio de la secuencia</text>')

for i, (t0, d, m, mw, prof, dist) in enumerate(
        [(0.0, 6, 3.1, "6,3", "14 km", "0 km"), (14.8, 9, 4.5, "6,4", "14 km", "42 km"),
         (36.5, 4, 1.3, "6,0", "8 km", "89 km"), (50.6, 6, 1.6, "6,1", "21 km", "91 km")]):
    x, w, h = gt(t0), gt(t0 + d) - gt(t0), m / 4.5 * MH
    a(f'<rect x="{x:.1f}" y="{BY-h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{BLU}" opacity=".78"/>')
    a(f'<text class="s" x="{x+w/2:.1f}" y="{BY-h-20:.1f}" text-anchor="middle" style="fill:{BLU};font-weight:600">{i+1} · M<tspan baseline-shift="sub" font-size="8">w</tspan> {mw}</text>')
    a(f'<text class="s" x="{x+w/2:.1f}" y="{BY-h-8:.1f}" text-anchor="middle">{d} s · {prof}</text>')
    a(f'<text class="s" x="{x+w/2:.1f}" y="{BY+34:.1f}" text-anchor="middle" style="fill:{AMB}">{dist}</text>')
a(f'<text class="s" x="{TX1+18}" y="{BY+34}" text-anchor="end" style="fill:{AMB};font-weight:600">distancia al primer foco</text>')

for t0, t1 in [(6, 14.8), (23.8, 36.5), (40.5, 50.6)]:
    xa, xb = gt(t0), gt(t1)
    a(f'<line x1="{xa:.1f}" y1="{BY-16}" x2="{xb:.1f}" y2="{BY-16}" stroke="{GREY}" stroke-width="1" stroke-dasharray="3 3"/>')
    a(f'<text class="s" x="{(xa+xb)/2:.1f}" y="{BY-21:.1f}" text-anchor="middle">sin radiación</text>')

xa, xb = gt(0), gt(13.3)
a(f'<rect x="{xa:.1f}" y="{BY-152:.1f}" width="{xb-xa:.1f}" height="16" fill="{GRN}" opacity=".22"/>')
a(f'<rect x="{xa:.1f}" y="{BY-152:.1f}" width="{xb-xa:.1f}" height="16" fill="none" stroke="{GRN}" stroke-width="1.2"/>')
a(f'<text class="s" x="{xb+8:.1f}" y="{BY-141:.1f}" style="fill:{GRN};font-weight:600">un solo M<tspan baseline-shift="sub" font-size="8">w</tspan> 6,6, según la escala: 7–13 s</text>')

xa, xb = gt(0), gt(57)
a(f'<path d="M{xa:.1f},{BY-170:.1f} v-8 H{xb:.1f} v8" fill="none" stroke="{RED}" stroke-width="1.3"/>')
a(f'<text class="s" x="{(xa+xb)/2:.1f}" y="{BY-184:.1f}" text-anchor="middle" style="fill:{RED};font-weight:600">57 s: la duración del tensor de momento sumado — 65 s, la ventana completa</text>')

a('</svg>')
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fig_ley_escala.svg"), "w", encoding="utf-8").write("\n".join(o))
print("ok")
