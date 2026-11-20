# Preparación de los datos: validación de los grafos

Generado por `python -m src.grafos`. Nota. Elaboración propia.

## Fuentes

- Límites: INEI, IDE, capa distrital actualizada al 2023 (`external\inei_distrito_2023\DISTRITO.gpkg`).
- Red vial: OpenStreetMap vía OSMnx 2.2.0, `network_type='drive'`, `osm_lima_drive_2026-11-20.graphml`.

## Cruce por UBIGEO

Ubigeos del panel que cruzan con la capa INEI: 43 de 43. Sin cruce: ninguno.

## Nodos

- Centroides que cayeron fuera de su polígono y se reemplazaron con `representative_point()`: 2 (LIMA, EL AGUSTINO).
- Puntos finales dentro de su polígono: 43 de 43.

## Red vial

- Nodos OSM: 145 431; tramos (no dirigidos): 216 361.
- Nodos OSM asignados a uno de los 43 distritos: 136 993; fuera (Callao; mar o margen): 8 438.
- Distancia de acceso centroide → nodo vial más cercano: mediana 58 m, máxima 4265 m.

## Grafos

| Grafo | Aristas | Conectado | Grado medio | Grado mín. | Grado máx. |
| --- | --- | --- | --- | --- | --- |
| Geográfico (GC₂) | 98 | sí | 4.56 | 1 | 11 |
| Vial (GE) | 89 | sí | 4.14 | 1 | 10 |

Aristas solo en el geográfico: 9; solo en el vial: 0.

Peso vial: mínimo 0.149, mediana 0.697, máximo 0.912. Tramos que cruzan por arista: mediana 17, máximo 105.

## Distancia por red frente a distancia recta

Pares (de 903) con distancia por red menor que la recta: 0. Cociente red/recta: mínimo 1.038, mediana 1.215.

## Aristas viales de mayor peso

| par                                              |   n_tramos |   d_red_km |   peso |
|:-------------------------------------------------|-----------:|-----------:|-------:|
| SAN JUAN DE MIRAFLORES – VILLA MARIA DEL TRIUNFO |        105 |      6.99  |  0.912 |
| LOS OLIVOS – SAN MARTIN DE PORRES                |         64 |      3.26  |  0.906 |
| MIRAFLORES – SURQUILLO                           |         44 |      2.558 |  0.876 |
| LINCE – SAN ISIDRO                               |         39 |      1.603 |  0.875 |
| MIRAFLORES – SAN ISIDRO                          |         44 |      2.977 |  0.871 |
| LIMA – LA VICTORIA                               |         42 |      2.81  |  0.868 |
| LIMA – BREÑA                                     |         39 |      3.359 |  0.853 |
| LIMA – EL AGUSTINO                               |         43 |      4.464 |  0.849 |
| SAN JUAN DE MIRAFLORES – SANTIAGO DE SURCO       |         39 |      5.03  |  0.832 |
| BARRANCO – SANTIAGO DE SURCO                     |         39 |      5.392 |  0.827 |

## Aristas viales con un solo tramo

| par                                |   d_red_km |   peso |
|:-----------------------------------|-----------:|-------:|
| ATE – SANTIAGO DE SURCO            |     20.238 |  0.319 |
| CHACLACAYO – CIENEGUILLA           |     26.189 |  0.243 |
| EL AGUSTINO – LURIGANCHO - CHOSICA |     27.394 |  0.228 |

## Revisión visual

`results/figuras/mapa_grafos.png`
