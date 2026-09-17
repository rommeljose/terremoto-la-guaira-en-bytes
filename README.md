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
assets/                          · logo AGHES, lámina de directividad y mapa de ubicación
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

## Créditos

**Lcdo. Físico Rommel Contreras** — Academia de Geohistoria del Estado Sucre (**AGHES**).

La ampliación *de una fuerza puntual a la esfera focal* desarrolla el capítulo 2 de
*Sismofísica Básica* del **Prof. Luis Daniel Beauperthuy Urich** (2008), con enlace al
capítulo original; los errores de esa página son de este sitio y no comprometen al autor.
