# Análisis del terremoto de La Guaira, en bytes

Sitio estático con la exposición **didáctica y metodológica** del análisis telesísmico de
la fuente del terremoto de La Guaira del **24 de junio de 2026** (evento complejo
M 7,2 + M 7,5): retroproyección, inversión de la tasa de momento, relocalización de
réplicas y los fundamentos físicos necesarios para leerlos.

> **Aclaración.** Las cifras del sitio describen el **procesamiento de datos y el modelado
> de la ruptura** (sismogramas, estaciones, operadores de inversión). **No** son cifras de
> víctimas ni de daños.

**El cómputo se documenta aparte.** El equipo empleado, los tiempos medidos por etapa, la
paralelización de la inversión y su comprobación con CUDA, y las pruebas de regresión
frente al código original están en el repositorio de cómputo
[`Aira_geofisica`](https://github.com/rommeljose/Aira_geofisica) —de acceso restringido
mientras los artículos están en preparación—. Este sitio se ocupa únicamente del método
y del resultado.

## Estructura

```
index.html                       · portada (HTML + CSS + un canvas, sin dependencias)
metodo/sismofisica.html          · 02 · fundamentos: falla, P y S, momento, mecanismo focal
metodo/momento-torque.html       ·  ↳ ampliación: del torque al momento sísmico
metodo/radiacion-doble-par.html  ·  ↳ ampliación avanzada: de la fuerza puntual a la esfera focal
                                      (sobre el cap. 2 de L. D. Beauperthuy Urich, 2008)
metodo/retroproyeccion.html      · 04 · delay-and-stack: dónde y cuándo radía la ruptura
metodo/green.html                · 05 · AxiSEM/Syngine, P+pP+sP y la profundidad
metodo/inversion.html            · 06 · de Aki & Richards a d = G m
metodo/relocalizacion.html       · 07 · hypoDD, con el visor 3-D de réplicas embebido
sim/                             · 09 · simulación interactiva (directividad y balance energético)
assets/                          · logo AGHES, lámina de directividad, mapa de ubicación,
                                   tarjeta social og_card.png
                                   y mapa de estaciones (fig_mapa_estaciones.png, generado en Aira_geofisica
                                   por codigo/aceleracion/fig_mapa_estaciones.py; aquí es una copia)
herramientas/                    · generador del mapa (§01) y sus datos de entrada
```

Todo es autocontenido: sin frameworks ni proceso de compilación. Hay **tema claro y
oscuro** (botón arriba a la derecha) y se respeta `prefers-reduced-motion`.

## Cómo actualizarlo

1. Editar el texto o las cifras directamente en el `.html` correspondiente.
2. Para cambiar una imagen, reemplazar el archivo en `assets/` (mismo nombre).
3. `git commit` + `git push` — GitHub Pages republica solo.

## El mapa de ubicación

El mapa de la sección 01 es un **SVG en línea**, no una imagen: va dentro de `index.html` para
que herede el tema claro/oscuro de la página a través de las clases `.mp-*`. Se regenera con

```bash
python3 herramientas/gen_mapa_ubicacion.py     # reescribe assets/mapa_ubicacion.svg
python3 herramientas/gen_tarjeta_og.py         # reescribe assets/og_card.png (1200x630)
```

y después hay que **volver a pegar** el SVG resultante en `index.html` (entre `<figure class="mapa">`
y `<figcaption>`). Sus datos de entrada están en `herramientas/datos/`:

| Fichero | Origen | Licencia |
|---|---|---|
| `costa_10m_zoom.json`, `costa_50m_region.json` | Natural Earth 1:10 M y 1:50 M, recortadas a las dos ventanas | dominio público |
| `fallas_cercanas.json` | trazas de fallas activas, proyecto Red de Emergencia | propia |
| `traza_principal.json` | enlace San Sebastián–Morón–Boconó, con las anclas de los dos hipocentros sobre el eje *s* | propia |

## Datos y herramientas

- **Registros telesísmicos y catálogo de réplicas:** servicios **FDSN** (EarthScope / IRIS y
  SIGEOS-FUNVISIS). Venezuela cuenta con su propio servicio FDSN, diseñado por Rommel Contreras:
  <https://catalogosismicovenezuela.sigeos.org/> · [API](https://catalogosismicovenezuela.sigeos.org/api.html).
- **Sismogramas sintéticos (funciones de Green):** Syngine / AxiSEM, modelo `ak135f_2s`.
- **Modelo de falla finita del M 7,5:** USGS/NEIC (`us6000t7zp`).

Los registros de movimiento fuerte de FUNVISIS se distribuyen bajo solicitud a esa
institución y no forman parte de este material.

## La tarjeta para compartir

Cuando el enlace se pega en WhatsApp, Telegram, Slack, Facebook, LinkedIn o X, el rastreador
del servicio lee las etiquetas del `<head>`. Hasta septiembre de 2026 las páginas solo
declaraban `charset` y `viewport`: sin `description` ni Open Graph, el rastreador no tenía
nada que citar y caía en lo primero que encontraba como texto, que era el comentario y las
variables del bloque `<style>`. De ahí el `/* Lámina AGHES — tema claro … */ :root{ --ground:#e7eaef;`
que aparecía en la vista previa.

Ahora las nueve páginas (`index.html`, las siete de `metodo/` y `sim/`) llevan `description`,
`canonical`, Open Graph y `twitter:card`, cada una con su propio título y resumen.

La imagen es `assets/og_card.png`, 1200 × 630 (la relación 1,91:1 que piden los rastreadores),
generada por `herramientas/gen_tarjeta_og.py`. La franja de mapa no es decoración: se dibuja
con los mismos ficheros de `herramientas/datos/` que el mapa de la sección 01 —costa de
Natural Earth, `traza_principal.json` y las anclas de los dos hipocentros del USGS—, de modo
que si la traza cambia, la tarjeta cambia con ella.

Si se cambia la tarjeta, los servicios conservan la anterior en caché; hay que forzar el
refresco en el depurador de cada uno (Facebook *Sharing Debugger*, LinkedIn *Post Inspector*)
o cambiar el nombre del fichero.

## Licencia

Contenido propio bajo **Creative Commons Atribución-NoComercial-CompartirIgual 4.0
Internacional (CC BY-NC-SA 4.0)** — ver [`LICENSE`](LICENSE). Se puede compartir y adaptar
con tres condiciones: **citar la autoría** (BY), **no hacer uso comercial** (NC) y
**distribuir las obras derivadas bajo esta misma licencia** (SA). Para un uso comercial hace
falta permiso escrito del autor. No se aplica CC0.

`LICENSE` detalla además lo que **no** cubre: los artículos científicos (que no están aquí),
el capítulo original del Prof. Beauperthuy Urich (que se enlaza, no se redistribuye), los datos
de terceros con su licencia de origen, y los registros de movimiento fuerte de FUNVISIS, que no
se incluyen en ninguna forma.

## Créditos

**Lcdo. Físico Rommel Contreras** — Academia de Geohistoria del Estado Sucre (**AGHES**).

La ampliación *de una fuerza puntual a la esfera focal* desarrolla el capítulo 2 de
*Sismofísica Básica* del **Prof. Luis Daniel Beauperthuy Urich** (2008), con enlace al
capítulo original; los errores de esa página son de este sitio y no comprometen al autor.
