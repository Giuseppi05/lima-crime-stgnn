# Evaluación: desempeño predictivo (OE2), pruebas estadísticas y equidad (OE4)

Generado por `python -m src.evaluar`. Métricas en número de denuncias; se excluyen las 9 celdas sin información. Media ± desviación estándar entre las 5 semillas (las referencias y XGBoost son deterministas: una corrida). Nota. Elaboración propia.

## Métricas globales (4 ventanas de prueba, 48 meses × 43 distritos)

| modelo                                        | MAE            | RMSE           | R2            | MASE          |
|:----------------------------------------------|:---------------|:---------------|:--------------|:--------------|
| GE (ST-GNN vial)                              | 50.244 ± 0.896 | 82.695 ± 1.554 | 0.904 ± 0.004 | 1.141 ± 0.02  |
| GC₂ (ST-GNN geográfica)                       | 49.627 ± 0.996 | 81.679 ± 1.768 | 0.906 ± 0.004 | 1.127 ± 0.023 |
| GC₁ (GRU sin grafo)                           | 49.915 ± 0.981 | 82.436 ± 1.747 | 0.904 ± 0.004 | 1.134 ± 0.022 |
| GE (ST-GNN vial), promedio de semillas        | 49.576 ± 0.0   | 81.553 ± 0.0   | 0.907 ± 0.0   | 1.125 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 48.897 ± 0.0   | 80.553 ± 0.0   | 0.909 ± 0.0   | 1.11 ± 0.0    |
| GC₁ (GRU sin grafo), promedio de semillas     | 49.291 ± 0.0   | 81.393 ± 0.0   | 0.907 ± 0.0   | 1.119 ± 0.0   |
| XGBoost                                       | 79.029 ± 0.0   | 137.796 ± 0.0  | 0.733 ± 0.0   | 1.798 ± 0.0   |
| Último mes observado (t − 3)                  | 45.662 ± 0.0   | 75.818 ± 0.0   | 0.919 ± 0.0   | 1.038 ± 0.0   |
| Promedio móvil 3 meses                        | 45.985 ± 0.0   | 77.112 ± 0.0   | 0.916 ± 0.0   | 1.044 ± 0.0   |
| Mismo mes del año anterior                    | 86.808 ± 0.0   | 140.319 ± 0.0  | 0.723 ± 0.0   | 1.969 ± 0.0   |


MASE (complementaria): MAE del modelo entre el MAE del 'mes anterior' dentro del entrenamiento de cada ventana; promedio de las 4 ventanas.

## Métricas por ventana

### MAE

| modelo                                        | 1              | 2              | 3              | 4              |
|:----------------------------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 60.41 ± 2.236  | 53.168 ± 0.747 | 51.082 ± 4.149 | 36.26 ± 2.257  |
| GC₂ (ST-GNN geográfica)                       | 60.481 ± 2.213 | 53.169 ± 0.746 | 48.567 ± 3.628 | 36.241 ± 2.282 |
| GC₁ (GRU sin grafo)                           | 61.67 ± 3.267  | 54.12 ± 1.538  | 49.08 ± 1.781  | 34.733 ± 0.579 |
| GE (ST-GNN vial), promedio de semillas        | 60.282 ± 0.0   | 52.346 ± 0.0   | 50.029 ± 0.0   | 35.594 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 60.366 ± 0.0   | 52.342 ± 0.0   | 47.302 ± 0.0   | 35.526 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 61.383 ± 0.0   | 53.238 ± 0.0   | 47.935 ± 0.0   | 34.552 ± 0.0   |
| XGBoost                                       | 124.256 ± 0.0  | 106.175 ± 0.0  | 41.449 ± 0.0   | 44.102 ± 0.0   |
| Último mes observado (t − 3)                  | 50.68 ± 0.0    | 52.756 ± 0.0   | 45.25 ± 0.0    | 33.918 ± 0.0   |
| Promedio móvil 3 meses                        | 55.497 ± 0.0   | 48.916 ± 0.0   | 47.713 ± 0.0   | 31.759 ± 0.0   |
| Mismo mes del año anterior                    | 115.18 ± 0.0   | 76.866 ± 0.0   | 108.126 ± 0.0  | 46.905 ± 0.0   |

### RMSE

| modelo                                        | 1              | 2              | 3              | 4              |
|:----------------------------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 95.951 ± 3.358 | 84.646 ± 1.508 | 86.634 ± 5.616 | 58.513 ± 3.726 |
| GC₂ (ST-GNN geográfica)                       | 95.973 ± 3.326 | 84.651 ± 1.505 | 82.81 ± 5.225  | 58.361 ± 3.672 |
| GC₁ (GRU sin grafo)                           | 98.278 ± 4.653 | 86.128 ± 3.024 | 82.831 ± 2.516 | 56.661 ± 0.785 |
| GE (ST-GNN vial), promedio de semillas        | 95.845 ± 0.0   | 83.027 ± 0.0   | 84.932 ± 0.0   | 57.422 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 95.87 ± 0.0    | 83.03 ± 0.0    | 81.109 ± 0.0   | 57.264 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 97.8 ± 0.0     | 84.446 ± 0.0   | 81.36 ± 0.0    | 56.308 ± 0.0   |
| XGBoost                                       | 192.046 ± 0.0  | 164.823 ± 0.0  | 73.223 ± 0.0   | 80.575 ± 0.0   |
| Último mes observado (t − 3)                  | 81.978 ± 0.0   | 83.781 ± 0.0   | 79.427 ± 0.0   | 54.17 ± 0.0    |
| Promedio móvil 3 meses                        | 88.632 ± 0.0   | 78.942 ± 0.0   | 84.187 ± 0.0   | 50.965 ± 0.0   |
| Mismo mes del año anterior                    | 175.978 ± 0.0  | 124.697 ± 0.0  | 160.293 ± 0.0  | 80.591 ± 0.0   |

### R2

| modelo                                        | 1             | 2             | 3             | 4             |
|:----------------------------------------------|:--------------|:--------------|:--------------|:--------------|
| GE (ST-GNN vial)                              | 0.895 ± 0.007 | 0.926 ± 0.003 | 0.846 ± 0.02  | 0.918 ± 0.01  |
| GC₂ (ST-GNN geográfica)                       | 0.895 ± 0.007 | 0.926 ± 0.003 | 0.859 ± 0.018 | 0.919 ± 0.01  |
| GC₁ (GRU sin grafo)                           | 0.889 ± 0.01  | 0.923 ± 0.005 | 0.86 ± 0.009  | 0.923 ± 0.002 |
| GE (ST-GNN vial), promedio de semillas        | 0.895 ± 0.0   | 0.929 ± 0.0   | 0.852 ± 0.0   | 0.921 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 0.895 ± 0.0   | 0.929 ± 0.0   | 0.865 ± 0.0   | 0.922 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 0.891 ± 0.0   | 0.926 ± 0.0   | 0.865 ± 0.0   | 0.924 ± 0.0   |
| XGBoost                                       | 0.578 ± 0.0   | 0.72 ± 0.0    | 0.89 ± 0.0    | 0.845 ± 0.0   |
| Último mes observado (t − 3)                  | 0.923 ± 0.0   | 0.928 ± 0.0   | 0.871 ± 0.0   | 0.93 ± 0.0    |
| Promedio móvil 3 meses                        | 0.91 ± 0.0    | 0.936 ± 0.0   | 0.855 ± 0.0   | 0.938 ± 0.0   |
| Mismo mes del año anterior                    | 0.646 ± 0.0   | 0.84 ± 0.0    | 0.475 ± 0.0   | 0.845 ± 0.0   |

## Pruebas estadísticas (n = 43 distritos; MAE por distrito promediado entre ventanas y semillas)

Regla de éxito del AVC3: el GE supera a un GC si tiene MAE **y** RMSE globales menores y la diferencia del MAE por distrito es significativa (α = 0,05). La prueba (t pareada o Wilcoxon) se eligió con Shapiro-Wilk sobre las diferencias pareadas. Como apoyo se repitió la prueba sobre el RMSE por distrito.

| comparacion            | tipo           |   MAE_GE |   MAE_rival |   RMSE_GE |   RMSE_rival |   media_dif |   mediana_dif |   shapiro_W |   shapiro_p | prueba   |   estadistico |      p |   distritos_GE_mejor |   p_RMSE_distrito | menor_MAE_por_distrito   | prueba_RMSE   | GE_supera   |
|:-----------------------|:---------------|---------:|------------:|----------:|-------------:|------------:|--------------:|------------:|------------:|:---------|--------------:|-------:|---------------------:|------------------:|:-------------------------|:--------------|:------------|
| GE vs GC1              | AVC3           |  50.2435 |     49.9155 |   82.6946 |      82.4355 |      0.3277 |        0.0409 |      0.897  |      0.001  | Wilcoxon |           428 | 0.5945 |                   21 |            0.4189 | GC1                      | Wilcoxon      | no          |
| GE vs GC2              | AVC3           |  50.2435 |     49.6273 |   82.6946 |      81.6794 |      0.6156 |        0.3966 |      0.6654 |      0      | Wilcoxon |           110 | 0      |                   11 |            0      | GC2                      | Wilcoxon      | no          |
| GE vs xgboost          | complementaria |  50.2435 |     79.0291 |   82.6946 |     137.796  |    -28.7575 |      -21.1381 |      0.8282 |      0      | Wilcoxon |            78 | 0      |                   34 |            0      | GE                       | Wilcoxon      | sí          |
| GE vs mes_anterior     | complementaria |  50.2435 |     45.6625 |   82.6946 |      75.8181 |      4.5766 |        1.8594 |      0.7995 |      0      | Wilcoxon |            40 | 0      |                    6 |            0      | mes_anterior             | Wilcoxon      | no          |
| GE_ens vs GC1_ens      | extra          |  49.5763 |     49.2914 |   81.553  |      81.3931 |      0.2845 |        0.0613 |      0.8925 |      0.0007 | Wilcoxon |           458 | 0.8624 |                   21 |            0.522  | GC1_ens                  | Wilcoxon      | no          |
| GE_ens vs GC2_ens      | extra          |  49.5763 |     48.897  |   81.553  |      80.5533 |      0.6786 |        0.3983 |      0.7095 |      0      | Wilcoxon |           105 | 0      |                   10 |            0      | GC2_ens                  | Wilcoxon      | no          |
| GE_ens vs mes_anterior | extra          |  49.5763 |     45.6625 |   81.553  |      75.8181 |      3.91   |        1.3537 |      0.7876 |      0      | Wilcoxon |            66 | 0      |                    8 |            0      | mes_anterior             | Wilcoxon      | no          |

## Equidad algorítmica (OE4)

Error relativo del distrito = MAE del distrito / promedio de denuncias del distrito en la prueba, por ventana; luego promedio entre ventanas y semillas. Brecha = máximo − mínimo. Sectores = terciles de distritos según su volumen mensual medio de denuncias en entrenamiento (promedio de las 4 ventanas). 5 distritos cambiarían de tercil si se usara el entrenamiento de una sola ventana.

| modelo                                        |   error_rel_mediana |   min | distrito_min   |   max | distrito_max        |   brecha |   brecha_sin_playa |   media_bajo |   media_medio |   media_alto |
|:----------------------------------------------|--------------------:|------:|:---------------|------:|:--------------------|---------:|-------------------:|-------------:|--------------:|-------------:|
| GE (ST-GNN vial)                              |               0.232 | 0.141 | BREÑA          | 1.308 | SANTA MARIA DEL MAR |    1.167 |              0.226 |        0.43  |         0.229 |        0.197 |
| GC₂ (ST-GNN geográfica)                       |               0.228 | 0.138 | BREÑA          | 1.318 | SANTA MARIA DEL MAR |    1.181 |              0.225 |        0.433 |         0.226 |        0.194 |
| GC₁ (GRU sin grafo)                           |               0.222 | 0.139 | CARABAYLLO     | 1.42  | SANTA MARIA DEL MAR |    1.281 |              0.232 |        0.434 |         0.227 |        0.195 |
| GE (ST-GNN vial), promedio de semillas        |               0.231 | 0.138 | BREÑA          | 1.289 | SANTA MARIA DEL MAR |    1.151 |              0.228 |        0.425 |         0.225 |        0.195 |
| GC₂ (ST-GNN geográfica), promedio de semillas |               0.225 | 0.133 | BREÑA          | 1.309 | SANTA MARIA DEL MAR |    1.176 |              0.228 |        0.43  |         0.222 |        0.192 |
| GC₁ (GRU sin grafo), promedio de semillas     |               0.22  | 0.137 | CARABAYLLO     | 1.416 | SANTA MARIA DEL MAR |    1.279 |              0.231 |        0.431 |         0.223 |        0.193 |
| XGBoost                                       |               0.319 | 0.12  | CARABAYLLO     | 1.114 | SANTA MARIA DEL MAR |    0.994 |              0.47  |        0.439 |         0.327 |        0.268 |
| Último mes observado (t − 3)                  |               0.196 | 0.119 | BREÑA          | 1.277 | SANTA MARIA DEL MAR |    1.158 |              0.24  |        0.425 |         0.211 |        0.178 |
| Promedio móvil 3 meses                        |               0.214 | 0.131 | LIMA           | 1.301 | SANTA MARIA DEL MAR |    1.169 |              0.207 |        0.394 |         0.215 |        0.179 |
| Mismo mes del año anterior                    |               0.38  | 0.219 | CARABAYLLO     | 1.7   | SANTA MARIA DEL MAR |    1.481 |              0.359 |        0.524 |         0.397 |        0.343 |

### Diferencias entre sectores

ANOVA si los tres grupos pasan Shapiro-Wilk y Levene; si no, Kruskal-Wallis (α = 0,05).

| modelo                                        | prueba         |   estadistico |      p | significativa   |
|:----------------------------------------------|:---------------|--------------:|-------:|:----------------|
| GE (ST-GNN vial)                              | Kruskal-Wallis |       16.9198 | 0.0002 | sí              |
| GC₂ (ST-GNN geográfica)                       | Kruskal-Wallis |       16.9198 | 0.0002 | sí              |
| GC₁ (GRU sin grafo)                           | Kruskal-Wallis |       16.6363 | 0.0002 | sí              |
| GE (ST-GNN vial), promedio de semillas        | Kruskal-Wallis |       16.5204 | 0.0003 | sí              |
| GC₂ (ST-GNN geográfica), promedio de semillas | Kruskal-Wallis |       17.3152 | 0.0002 | sí              |
| GC₁ (GRU sin grafo), promedio de semillas     | Kruskal-Wallis |       16.0761 | 0.0003 | sí              |
| XGBoost                                       | Kruskal-Wallis |       12.6224 | 0.0018 | sí              |
| Último mes observado (t − 3)                  | Kruskal-Wallis |       18.791  | 0.0001 | sí              |
| Promedio móvil 3 meses                        | Kruskal-Wallis |       14.4604 | 0.0007 | sí              |
| Mismo mes del año anterior                    | Kruskal-Wallis |        6.7841 | 0.0336 | sí              |

### Composición de los sectores

| sector   | distritos                                                                                                                                                                                                              |
|:---------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bajo     | ANCON, CHACLACAYO, CIENEGUILLA, LA MOLINA, LURIN, MAGDALENA DEL MAR, PACHACAMAC, PUCUSANA, PUNTA HERMOSA, PUNTA NEGRA, SAN BARTOLO, SAN LUIS, SAN MIGUEL, SANTA MARIA DEL MAR, SANTA ROSA                              |
| medio    | BARRANCO, BREÑA, CHORRILLOS, JESUS MARIA, LINCE, LURIGANCHO - CHOSICA, MIRAFLORES, PUEBLO LIBRE, PUENTE PIEDRA, RIMAC, SAN BORJA, SAN ISIDRO, SANTA ANITA, SURQUILLO                                                   |
| alto     | ATE, CARABAYLLO, COMAS, EL AGUSTINO, INDEPENDENCIA, LA VICTORIA, LIMA, LOS OLIVOS, SAN JUAN DE LURIGANCHO, SAN JUAN DE MIRAFLORES, SAN MARTIN DE PORRES, SANTIAGO DE SURCO, VILLA EL SALVADOR, VILLA MARIA DEL TRIUNFO |

### Distritos de bajo volumen (playa), error relativo

| distrito            |   GE (ST-GNN vial) |   GC₂ (ST-GNN geográfica) |   GC₁ (GRU sin grafo) |   GE (ST-GNN vial), promedio de semillas |   GC₂ (ST-GNN geográfica), promedio de semillas |   GC₁ (GRU sin grafo), promedio de semillas |   XGBoost |   Último mes observado (t − 3) |   Promedio móvil 3 meses |   Mismo mes del año anterior |
|:--------------------|-------------------:|--------------------------:|----------------------:|-----------------------------------------:|------------------------------------------------:|--------------------------------------------:|----------:|-------------------------------:|-------------------------:|-----------------------------:|
| PUCUSANA            |              0.403 |                     0.402 |                 0.389 |                                    0.399 |                                           0.398 |                                       0.384 |     0.338 |                          0.402 |                    0.378 |                        0.511 |
| PUNTA HERMOSA       |              0.837 |                     0.863 |                 0.858 |                                    0.836 |                                           0.861 |                                       0.853 |     0.573 |                          0.887 |                    0.872 |                        0.59  |
| PUNTA NEGRA         |              0.657 |                     0.664 |                 0.615 |                                    0.641 |                                           0.663 |                                       0.611 |     0.47  |                          0.655 |                    0.522 |                        0.615 |
| SAN BARTOLO         |              0.457 |                     0.469 |                 0.46  |                                    0.45  |                                           0.466 |                                       0.456 |     0.454 |                          0.466 |                    0.39  |                        0.404 |
| SANTA MARIA DEL MAR |              1.308 |                     1.318 |                 1.42  |                                    1.289 |                                           1.309 |                                       1.416 |     1.114 |                          1.277 |                    1.301 |                        1.7   |

Los distritos de playa tienen pocas denuncias por mes; un error de pocas denuncias se vuelve un error relativo grande. Por eso la brecha se informa también sin ellos.
