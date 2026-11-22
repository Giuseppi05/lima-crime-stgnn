# Evaluación: desempeño predictivo (OE2), pruebas estadísticas y equidad (OE4)

Generado por `python -m src.evaluar`. Métricas en número de denuncias; se excluyen las 9 celdas sin información. Media ± desviación estándar entre las 5 semillas (las referencias y XGBoost son deterministas: una corrida). Nota. Elaboración propia.

## Métricas globales (4 ventanas de prueba, 48 meses × 43 distritos)

| modelo                                        | MAE            | RMSE           | R2           | MASE          |
|:----------------------------------------------|:---------------|:---------------|:-------------|:--------------|
| GE (ST-GNN vial)                              | 48.16 ± 0.72   | 80.064 ± 1.405 | 0.91 ± 0.003 | 1.094 ± 0.017 |
| GC₂ (ST-GNN geográfica)                       | 48.2 ± 0.988   | 80.087 ± 1.935 | 0.91 ± 0.004 | 1.095 ± 0.023 |
| GC₁ (GRU sin grafo)                           | 52.689 ± 4.519 | 88.066 ± 8.639 | 0.89 ± 0.021 | 1.195 ± 0.102 |
| GE (ST-GNN vial), promedio de semillas        | 47.682 ± 0.0   | 79.169 ± 0.0   | 0.912 ± 0.0  | 1.083 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 47.708 ± 0.0   | 79.174 ± 0.0   | 0.912 ± 0.0  | 1.084 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 51.755 ± 0.0   | 85.94 ± 0.0    | 0.896 ± 0.0  | 1.174 ± 0.0   |
| XGBoost                                       | 78.457 ± 0.0   | 136.572 ± 0.0  | 0.738 ± 0.0  | 1.783 ± 0.0   |
| Último mes observado (t − 3)                  | 45.662 ± 0.0   | 75.818 ± 0.0   | 0.919 ± 0.0  | 1.038 ± 0.0   |
| Promedio móvil 3 meses                        | 45.985 ± 0.0   | 77.112 ± 0.0   | 0.916 ± 0.0  | 1.044 ± 0.0   |
| Mismo mes del año anterior                    | 86.808 ± 0.0   | 140.319 ± 0.0  | 0.723 ± 0.0  | 1.969 ± 0.0   |


MASE (complementaria): MAE del modelo entre el MAE del 'mes anterior' dentro del entrenamiento de cada ventana; promedio de las 4 ventanas.

## Métricas por ventana

### MAE

| modelo                                        | 1               | 2              | 3              | 4              |
|:----------------------------------------------|:----------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 58.261 ± 0.933  | 53.61 ± 3.078  | 46.276 ± 0.669 | 34.441 ± 0.819 |
| GC₂ (ST-GNN geográfica)                       | 58.561 ± 1.848  | 53.608 ± 3.099 | 46.177 ± 0.7   | 34.399 ± 0.738 |
| GC₁ (GRU sin grafo)                           | 72.992 ± 15.193 | 53.192 ± 2.336 | 49.551 ± 1.686 | 34.953 ± 0.478 |
| GE (ST-GNN vial), promedio de semillas        | 58.123 ± 0.0    | 52.445 ± 0.0   | 46.25 ± 0.0    | 33.857 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 58.426 ± 0.0    | 52.44 ± 0.0    | 46.139 ± 0.0   | 33.774 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 70.947 ± 0.0    | 52.32 ± 0.0    | 48.845 ± 0.0   | 34.843 ± 0.0   |
| XGBoost                                       | 127.127 ± 0.0   | 97.101 ± 0.0   | 43.879 ± 0.0   | 45.595 ± 0.0   |
| Último mes observado (t − 3)                  | 50.68 ± 0.0     | 52.756 ± 0.0   | 45.25 ± 0.0    | 33.918 ± 0.0   |
| Promedio móvil 3 meses                        | 55.497 ± 0.0    | 48.916 ± 0.0   | 47.713 ± 0.0   | 31.759 ± 0.0   |
| Mismo mes del año anterior                    | 115.18 ± 0.0    | 76.866 ± 0.0   | 108.126 ± 0.0  | 46.905 ± 0.0   |

### RMSE

| modelo                                        | 1                | 2              | 3              | 4              |
|:----------------------------------------------|:-----------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 93.203 ± 1.46    | 85.641 ± 5.826 | 80.497 ± 1.071 | 55.702 ± 1.294 |
| GC₂ (ST-GNN geográfica)                       | 93.408 ± 2.852   | 85.668 ± 5.842 | 80.384 ± 1.106 | 55.616 ± 1.136 |
| GC₁ (GRU sin grafo)                           | 116.132 ± 23.396 | 84.346 ± 3.667 | 83.045 ± 2.171 | 57.381 ± 1.121 |
| GE (ST-GNN vial), promedio de semillas        | 93.071 ± 0.0     | 83.458 ± 0.0   | 80.456 ± 0.0   | 54.384 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 93.274 ± 0.0     | 83.48 ± 0.0    | 80.345 ± 0.0   | 54.192 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 112.471 ± 0.0    | 82.77 ± 0.0    | 82.229 ± 0.0   | 57.138 ± 0.0   |
| XGBoost                                       | 196.508 ± 0.0    | 152.251 ± 0.0  | 77.418 ± 0.0   | 82.295 ± 0.0   |
| Último mes observado (t − 3)                  | 81.978 ± 0.0     | 83.781 ± 0.0   | 79.427 ± 0.0   | 54.17 ± 0.0    |
| Promedio móvil 3 meses                        | 88.632 ± 0.0     | 78.942 ± 0.0   | 84.187 ± 0.0   | 50.965 ± 0.0   |
| Mismo mes del año anterior                    | 175.978 ± 0.0    | 124.697 ± 0.0  | 160.293 ± 0.0  | 80.591 ± 0.0   |

### R2

| modelo                                        | 1             | 2             | 3             | 4             |
|:----------------------------------------------|:--------------|:--------------|:--------------|:--------------|
| GE (ST-GNN vial)                              | 0.901 ± 0.003 | 0.924 ± 0.01  | 0.867 ± 0.004 | 0.926 ± 0.003 |
| GC₂ (ST-GNN geográfica)                       | 0.9 ± 0.006   | 0.924 ± 0.011 | 0.868 ± 0.004 | 0.926 ± 0.003 |
| GC₁ (GRU sin grafo)                           | 0.841 ± 0.062 | 0.926 ± 0.006 | 0.859 ± 0.007 | 0.921 ± 0.003 |
| GE (ST-GNN vial), promedio de semillas        | 0.901 ± 0.0   | 0.928 ± 0.0   | 0.868 ± 0.0   | 0.929 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 0.9 ± 0.0     | 0.928 ± 0.0   | 0.868 ± 0.0   | 0.93 ± 0.0    |
| GC₁ (GRU sin grafo), promedio de semillas     | 0.855 ± 0.0   | 0.929 ± 0.0   | 0.862 ± 0.0   | 0.922 ± 0.0   |
| XGBoost                                       | 0.558 ± 0.0   | 0.761 ± 0.0   | 0.877 ± 0.0   | 0.838 ± 0.0   |
| Último mes observado (t − 3)                  | 0.923 ± 0.0   | 0.928 ± 0.0   | 0.871 ± 0.0   | 0.93 ± 0.0    |
| Promedio móvil 3 meses                        | 0.91 ± 0.0    | 0.936 ± 0.0   | 0.855 ± 0.0   | 0.938 ± 0.0   |
| Mismo mes del año anterior                    | 0.646 ± 0.0   | 0.84 ± 0.0    | 0.475 ± 0.0   | 0.845 ± 0.0   |

## Pruebas estadísticas (n = 43 distritos; MAE por distrito promediado entre ventanas y semillas)

Regla de éxito del AVC3: el GE supera a un GC si tiene MAE **y** RMSE globales menores y la diferencia del MAE por distrito es significativa (α = 0,05). La prueba (t pareada o Wilcoxon) se eligió con Shapiro-Wilk sobre las diferencias pareadas. Como apoyo se repitió la prueba sobre el RMSE por distrito.

| comparacion            | tipo           |   MAE_GE |   MAE_rival |   RMSE_GE |   RMSE_rival |   media_dif |   mediana_dif |   shapiro_W |   shapiro_p | prueba   |   estadistico |      p |   distritos_GE_mejor |   p_RMSE_distrito | menor_MAE_por_distrito   | prueba_RMSE   | GE_supera   |
|:-----------------------|:---------------|---------:|------------:|----------:|-------------:|------------:|--------------:|------------:|------------:|:---------|--------------:|-------:|---------------------:|------------------:|:-------------------------|:--------------|:------------|
| GE vs GC1              | AVC3           |  48.1604 |     52.6889 |   80.0645 |      88.0655 |     -4.5242 |       -1.9646 |      0.7894 |      0      | Wilcoxon |           100 | 0      |                   33 |            0      | GE                       | Wilcoxon      | sí          |
| GE vs GC2              | AVC3           |  48.1604 |     48.1997 |   80.0645 |      80.0868 |     -0.0393 |        0.0092 |      0.8526 |      0.0001 | Wilcoxon |           462 | 0.9001 |                   20 |            0.7243 | GE                       | Wilcoxon      | no          |
| GE vs xgboost          | complementaria |  48.1604 |     78.4574 |   80.0645 |     136.572  |    -30.2675 |      -12.3162 |      0.7872 |      0      | Wilcoxon |            62 | 0      |                   35 |            0      | GE                       | Wilcoxon      | sí          |
| GE vs mes_anterior     | complementaria |  48.1604 |     45.6625 |   80.0645 |      75.8181 |      2.4955 |        0.5915 |      0.7728 |      0      | Wilcoxon |            76 | 0      |                    9 |            0      | mes_anterior             | Wilcoxon      | no          |
| GE_ens vs GC1_ens      | extra          |  47.6822 |     51.7554 |   79.1692 |      85.9404 |     -4.0692 |       -1.6145 |      0.789  |      0      | Wilcoxon |           131 | 0      |                   30 |            0.0001 | GE_ens                   | Wilcoxon      | sí          |
| GE_ens vs GC2_ens      | extra          |  47.6822 |     47.7083 |   79.1692 |      79.1736 |     -0.0261 |        0.0138 |      0.8777 |      0.0003 | Wilcoxon |           443 | 0.7243 |                   18 |            0.7514 | GE_ens                   | Wilcoxon      | no          |
| GE_ens vs mes_anterior | extra          |  47.6822 |     45.6625 |   79.1692 |      75.8181 |      2.0178 |        0.3449 |      0.7698 |      0      | Wilcoxon |           187 | 0.0004 |                   13 |            0      | mes_anterior             | Wilcoxon      | no          |

## Equidad algorítmica (OE4)

Error relativo del distrito = MAE del distrito / promedio de denuncias del distrito en la prueba, por ventana; luego promedio entre ventanas y semillas. Brecha = máximo − mínimo. Sectores = terciles de distritos según su volumen mensual medio de denuncias en entrenamiento (promedio de las 4 ventanas). 5 distritos cambiarían de tercil si se usara el entrenamiento de una sola ventana.

| modelo                                        |   error_rel_mediana |   min | distrito_min   |   max | distrito_max        |   brecha |   brecha_sin_playa |   media_bajo |   media_medio |   media_alto |
|:----------------------------------------------|--------------------:|------:|:---------------|------:|:--------------------|---------:|-------------------:|-------------:|--------------:|-------------:|
| GE (ST-GNN vial)                              |               0.215 | 0.13  | BREÑA          | 1.304 | SANTA MARIA DEL MAR |    1.175 |              0.23  |        0.427 |         0.22  |        0.188 |
| GC₂ (ST-GNN geográfica)                       |               0.216 | 0.13  | BREÑA          | 1.305 | SANTA MARIA DEL MAR |    1.175 |              0.23  |        0.427 |         0.219 |        0.188 |
| GC₁ (GRU sin grafo)                           |               0.231 | 0.142 | CARABAYLLO     | 1.375 | SANTA MARIA DEL MAR |    1.233 |              0.235 |        0.426 |         0.236 |        0.204 |
| GE (ST-GNN vial), promedio de semillas        |               0.212 | 0.126 | BREÑA          | 1.298 | SANTA MARIA DEL MAR |    1.172 |              0.233 |        0.425 |         0.217 |        0.187 |
| GC₂ (ST-GNN geográfica), promedio de semillas |               0.213 | 0.127 | BREÑA          | 1.298 | SANTA MARIA DEL MAR |    1.172 |              0.233 |        0.425 |         0.216 |        0.187 |
| GC₁ (GRU sin grafo), promedio de semillas     |               0.228 | 0.138 | CARABAYLLO     | 1.347 | SANTA MARIA DEL MAR |    1.209 |              0.235 |        0.419 |         0.232 |        0.201 |
| XGBoost                                       |               0.314 | 0.132 | CARABAYLLO     | 1.083 | SANTA MARIA DEL MAR |    0.951 |              0.439 |        0.435 |         0.322 |        0.269 |
| Último mes observado (t − 3)                  |               0.196 | 0.119 | BREÑA          | 1.277 | SANTA MARIA DEL MAR |    1.158 |              0.24  |        0.425 |         0.211 |        0.178 |
| Promedio móvil 3 meses                        |               0.214 | 0.131 | LIMA           | 1.301 | SANTA MARIA DEL MAR |    1.169 |              0.207 |        0.394 |         0.215 |        0.179 |
| Mismo mes del año anterior                    |               0.38  | 0.219 | CARABAYLLO     | 1.7   | SANTA MARIA DEL MAR |    1.481 |              0.359 |        0.524 |         0.397 |        0.343 |

### Diferencias entre sectores

ANOVA si los tres grupos pasan Shapiro-Wilk y Levene; si no, Kruskal-Wallis (α = 0,05).

| modelo                                        | prueba         |   estadistico |      p | significativa   |
|:----------------------------------------------|:---------------|--------------:|-------:|:----------------|
| GE (ST-GNN vial)                              | Kruskal-Wallis |       16.6816 | 0.0002 | sí              |
| GC₂ (ST-GNN geográfica)                       | Kruskal-Wallis |       16.4452 | 0.0003 | sí              |
| GC₁ (GRU sin grafo)                           | Kruskal-Wallis |       16.1067 | 0.0003 | sí              |
| GE (ST-GNN vial), promedio de semillas        | Kruskal-Wallis |       16.6779 | 0.0002 | sí              |
| GC₂ (ST-GNN geográfica), promedio de semillas | Kruskal-Wallis |       16.5257 | 0.0003 | sí              |
| GC₁ (GRU sin grafo), promedio de semillas     | Kruskal-Wallis |       16.017  | 0.0003 | sí              |
| XGBoost                                       | Kruskal-Wallis |       13.089  | 0.0014 | sí              |
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
| PUCUSANA            |              0.397 |                     0.395 |                 0.364 |                                    0.395 |                                           0.393 |                                       0.358 |     0.342 |                          0.402 |                    0.378 |                        0.511 |
| PUNTA HERMOSA       |              0.873 |                     0.873 |                 0.824 |                                    0.872 |                                           0.871 |                                       0.806 |     0.556 |                          0.887 |                    0.872 |                        0.59  |
| PUNTA NEGRA         |              0.651 |                     0.65  |                 0.559 |                                    0.648 |                                           0.646 |                                       0.551 |     0.452 |                          0.655 |                    0.522 |                        0.615 |
| SAN BARTOLO         |              0.465 |                     0.466 |                 0.466 |                                    0.463 |                                           0.464 |                                       0.46  |     0.476 |                          0.466 |                    0.39  |                        0.404 |
| SANTA MARIA DEL MAR |              1.304 |                     1.305 |                 1.375 |                                    1.298 |                                           1.298 |                                       1.347 |     1.083 |                          1.277 |                    1.301 |                        1.7   |

Los distritos de playa tienen pocas denuncias por mes; un error de pocas denuncias se vuelve un error relativo grande. Por eso la brecha se informa también sin ellos.
