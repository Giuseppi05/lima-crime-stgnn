# Comprensión de los datos: informe de calidad

Generado por `python -m src.datos`. Nota. Elaboración propia.

## Diccionario de datos (archivo crudo)

| Campo | Descripción | Tratamiento |
| --- | --- | --- |
| ANIO, MES | Año y mes del hecho | Se unen en `periodo` (YYYY-MM) |
| DPTO_HECHO_NEW | Departamento del hecho | Filtro `LIMA METROPOLITANA` |
| PROV_HECHO | Provincia del hecho | Solo `LIMA` tras el filtro |
| DIST_HECHO | Distrito del hecho | Nombre; se verifica relación 1:1 con el UBIGEO |
| UBIGEO_HECHO | Código INEI del distrito | Leído como texto, `zfill(6)` |
| P_MODALIDADES | Modalidad del delito | Se conservan Hurto y Robo |
| cantidad | Número de denuncias (ya agregado) | Se suma por distrito y mes |

## Verificaciones

| Comprobación | Resultado |
| --- | --- |
| Filas de Lima Metropolitana en el crudo | 27 064 |
| Duplicados en el crudo (año, mes, ubigeo, modalidad) | 0 |
| Valores nulos en el crudo (Lima) | 0 |
| Cantidades negativas | 0 |
| Nombres distintos por UBIGEO / UBIGEO distintos por nombre (máx.) | 1 / 1 |
| Filas del panel | 4515 (43 × 105) |
| Duplicados distrito-mes en el panel | 0 |
| Total hurto + robo antes de agregar | 957 705 |
| Total hurto + robo en el panel | 957 705 (hurto 603 129; robo 354 576) |

## Cobertura y meses sin hurto ni robo

Estados del panel: observado 4446, cero 60, sin_informacion 9.

- `cero`: el distrito tiene denuncias de otras modalidades ese mes, pero ninguna de hurto ni robo. Se usa como 0 real.
- `sin_informacion`: el distrito no tiene ninguna fila de ninguna modalidad ese mes. Entra al modelo como 0, pero se excluye de todas las métricas.

| distrito            |   cero |   sin_informacion |
|:--------------------|-------:|------------------:|
| PUCUSANA            |      3 |                 0 |
| PUNTA HERMOSA       |      2 |                 0 |
| PUNTA NEGRA         |      9 |                 0 |
| SAN BARTOLO         |      5 |                 0 |
| SANTA MARIA DEL MAR |     41 |                 9 |

Meses sin información: 2018-05, 2018-06, 2018-08, 2020-06, 2021-07, 2022-05, 2022-06, 2026-04, 2026-06

## Distribución por celda observada

Mínimo 1, máximo 1687, media 215.4, mediana 141.

## Totales anuales

| Año | Hurto + robo |
| --- | --- |
| 2018 | 119 391 |
| 2019 | 110 091 |
| 2020 | 60 839 |
| 2021 | 76 940 |
| 2022 | 98 838 |
| 2023 | 163 728 |
| 2024 | 146 055 |
| 2025 | 106 260 |
| 2026 (ene–sep) | 75 563 |

## Quiebres

- Abril de 2020 (estado de emergencia): 1 256 denuncias en Lima, frente a 8 714 en febrero de 2020.
- Salto de 2022 a 2023: 98 838 → 163 728 (+65.7 %). Baja en 2025: 106 260 (-27.2 % frente a 2024).
- El salto de 2023 es un cambio de nivel que el modelo debe absorber; la ventana 1 lo tiene en prueba. No se corrige: se interpreta como cambio en el registro o en el fenómeno, sin poder separarlos con estos datos.

## Concentración desde 2022

Los cuatro distritos con más denuncias desde 2022 suman 30.4 % del total: LIMA (64 520), SAN JUAN DE LURIGANCHO (51 962), SAN MARTIN DE PORRES (34 252), SANTIAGO DE SURCO (28 512).

## Atípicos

Criterio: |z robusto| > 3,5 sobre log1p(objetivo) por distrito (mediana y MAD de los meses sin pandemia). Decisión: se conservan; son registros reales y la pandemia se trata como caso adverso.

Celdas marcadas: 133 (de ellas en pandemia: 125).

| distrito                | periodo   |   objetivo |   z_robusto |
|:------------------------|:----------|-----------:|------------:|
| BREÑA                   | 2020-04   |         11 |      -15.71 |
| BARRANCO                | 2020-06   |          3 |      -13.79 |
| BARRANCO                | 2020-05   |          3 |      -13.79 |
| BARRANCO                | 2020-04   |          3 |      -13.79 |
| BARRANCO                | 2020-10   |          4 |      -12.88 |
| BARRANCO                | 2021-02   |          4 |      -12.88 |
| LIMA                    | 2020-04   |         94 |      -10.91 |
| BREÑA                   | 2020-05   |         27 |      -10.72 |
| BARRANCO                | 2020-09   |          8 |      -10.48 |
| BARRANCO                | 2021-01   |          9 |      -10.05 |
| BARRANCO                | 2020-07   |         10 |       -9.66 |
| ATE                     | 2020-04   |         59 |       -9.33 |
| SANTIAGO DE SURCO       | 2020-04   |         52 |       -8.94 |
| PUEBLO LIBRE            | 2020-04   |          2 |       -8.83 |
| JESUS MARIA             | 2020-04   |          8 |       -8.79 |
| LIMA                    | 2020-05   |        158 |       -8.57 |
| CHORRILLOS              | 2020-04   |         15 |       -8.41 |
| SAN BORJA               | 2020-04   |          6 |       -8.39 |
| RIMAC                   | 2020-04   |         27 |       -8.13 |
| VILLA EL SALVADOR       | 2020-04   |         46 |       -8.13 |
| BARRANCO                | 2021-04   |         16 |       -7.88 |
| BARRANCO                | 2020-08   |         17 |       -7.65 |
| VILLA MARIA DEL TRIUNFO | 2020-04   |         62 |       -7.63 |
| BREÑA                   | 2020-06   |         47 |       -7.55 |
| SAN LUIS                | 2020-04   |         13 |       -7.3  |

## Figuras

- `results/figuras/tendencia_mensual.png`
- `results/figuras/estacionalidad.png`
- `results/figuras/totales_anuales.png`
