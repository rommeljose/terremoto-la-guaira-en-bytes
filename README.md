# Terremoto de La Guaira — en bytes

Página estática (una lámina) con las **cifras del análisis y el cómputo** de la fuente
del terremoto de La Guaira del **24 de junio de 2026** (doblete M 7,2 + M 7,5):
retroproyección telesísmica, inversión de la tasa de momento y las pruebas de robustez.

> **Aclaración importante.** Estas son cifras del **procesamiento de datos y el modelado
> de la ruptura** (sismogramas, estaciones, operadores de inversión). **No** son cifras de
> víctimas ni de daños.

Lo llamativo: todo el estudio se resolvió en **una sola APU de escritorio de consumo**
(AMD Ryzen 5 3400G, 2019), sin clúster ni HPC.

## Estructura

```
index.html                     · la lámina (HTML + CSS + un canvas, sin dependencias)
assets/lamina_directividad.png · lámina divulgativa de directividad Doppler / polarización S
assets/logo_aghes.png          · logo de la Academia de Geohistoria del Estado Sucre (AGHES)
```

La página es autocontenida: no usa frameworks ni build. Tiene **tema claro y oscuro**
(botón arriba a la derecha) y respeta `prefers-reduced-motion`.

## Cómo actualizarla

1. Editar el texto/cifras directamente en `index.html`.
2. Para cambiar una imagen, reemplazar el archivo en `assets/` (mismo nombre).
3. `git commit` + `git push` — GitHub Pages republica solo.

## Datos y herramientas

- **Registros telesísmicos y catálogo de réplicas:** servicios **FDSN** (EarthScope / IRIS y
  SIGEOS-FUNVISIS). Venezuela cuenta con su propio servicio FDSN, diseñado por Rommel Contreras:
  <https://catalogosismicovenezuela.sigeos.org/> · [API](https://catalogosismicovenezuela.sigeos.org/api.html).
- **Sismogramas sintéticos (funciones de Green):** Syngine / AxiSEM, modelo `ak135f_2s`.

## Créditos

**Lcdo. Físico Rommel Contreras** — Academia de Geohistoria del Estado Sucre (**AGHES**).
