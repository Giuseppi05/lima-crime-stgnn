# Evaluación: desempeño predictivo (OE2), pruebas estadísticas y equidad (OE4)

Generado por `python -m src.evaluar`. Métricas en número de denuncias; se excluyen las 9 celdas sin información. Media ± desviación estándar entre las 5 semillas (las referencias y XGBoost son deterministas: una corrida). Nota. Elaboración propia.

## Métricas globales (4 ventanas de prueba, 48 meses × 43 distritos)

| modelo                                        | MAE            | RMSE           | R2            | MASE          |
|:----------------------------------------------|:---------------|:---------------|:--------------|:--------------|
| GE (ST-GNN vial)                              | 33.839 ± 0.675 | 55.394 ± 1.094 | 0.957 ± 0.002 | 1.079 ± 0.022 |
| GC₂ (ST-GNN geográfica)                       | 33.473 ± 0.724 | 54.922 ± 1.125 | 0.958 ± 0.002 | 1.067 ± 0.023 |
| GC₁ (GRU sin grafo)                           | 33.75 ± 0.413  | 56.002 ± 0.396 | 0.956 ± 0.001 | 1.076 ± 0.013 |
| GE (ST-GNN vial), promedio de semillas        | 32.907 ± 0.0   | 53.936 ± 0.0   | 0.959 ± 0.0   | 1.049 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 32.774 ± 0.0   | 53.905 ± 0.0   | 0.959 ± 0.0   | 1.044 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 33.304 ± 0.0   | 55.426 ± 0.0   | 0.957 ± 0.0   | 1.061 ± 0.0   |
| XGBoost                                       | 56.186 ± 0.0   | 100.499 ± 0.0  | 0.858 ± 0.0   | 1.792 ± 0.0   |
| Mes anterior                                  | 31.271 ± 0.0   | 51.76 ± 0.0    | 0.962 ± 0.0   | 0.997 ± 0.0   |
| Promedio móvil 3 meses                        | 34.05 ± 0.0    | 56.397 ± 0.0   | 0.955 ± 0.0   | 1.086 ± 0.0   |
| Mismo mes del año anterior                    | 86.808 ± 0.0   | 140.319 ± 0.0  | 0.723 ± 0.0   | 2.766 ± 0.0   |


MASE (complementaria): MAE del modelo entre el MAE del 'mes anterior' dentro del entrenamiento de cada ventana; promedio de las 4 ventanas.

## Métricas por ventana

### MAE

| modelo                                        | 1              | 2              | 3              | 4              |
|:----------------------------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 38.558 ± 1.019 | 39.703 ± 0.889 | 31.089 ± 3.534 | 25.975 ± 0.835 |
| GC₂ (ST-GNN geográfica)                       | 38.468 ± 1.079 | 39.396 ± 0.499 | 30.03 ± 2.487  | 25.969 ± 0.811 |
| GC₁ (GRU sin grafo)                           | 39.14 ± 0.956  | 39.212 ± 0.341 | 30.729 ± 1.983 | 25.888 ± 0.832 |
| GE (ST-GNN vial), promedio de semillas        | 38.543 ± 0.0   | 38.505 ± 0.0   | 28.685 ± 0.0   | 25.868 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 38.441 ± 0.0   | 38.603 ± 0.0   | 28.155 ± 0.0   | 25.871 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 39.031 ± 0.0   | 38.694 ± 0.0   | 29.862 ± 0.0   | 25.596 ± 0.0   |
| XGBoost                                       | 85.934 ± 0.0   | 75.846 ± 0.0   | 33.496 ± 0.0   | 29.365 ± 0.0   |
| Mes anterior                                  | 33.436 ± 0.0   | 38.977 ± 0.0   | 27.215 ± 0.0   | 25.432 ± 0.0   |
| Promedio móvil 3 meses                        | 37.44 ± 0.0    | 40.926 ± 0.0   | 31.973 ± 0.0   | 25.829 ± 0.0   |
| Mismo mes del año anterior                    | 115.18 ± 0.0   | 76.866 ± 0.0   | 108.126 ± 0.0  | 46.905 ± 0.0   |

### RMSE

| modelo                                        | 1              | 2              | 3              | 4              |
|:----------------------------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 62.577 ± 1.585 | 64.287 ± 1.389 | 50.455 ± 5.62  | 40.594 ± 1.209 |
| GC₂ (ST-GNN geográfica)                       | 62.512 ± 1.658 | 64.064 ± 0.564 | 48.871 ± 4.252 | 40.573 ± 1.184 |
| GC₁ (GRU sin grafo)                           | 64.365 ± 1.446 | 63.727 ± 0.646 | 51.156 ± 2.693 | 41.354 ± 1.145 |
| GE (ST-GNN vial), promedio de semillas        | 62.49 ± 0.0    | 62.58 ± 0.0    | 46.713 ± 0.0   | 40.347 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 62.417 ± 0.0   | 62.882 ± 0.0   | 46.27 ± 0.0    | 40.335 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 64.148 ± 0.0   | 63.069 ± 0.0   | 50.144 ± 0.0   | 40.937 ± 0.0   |
| XGBoost                                       | 137.203 ± 0.0  | 123.328 ± 0.0  | 58.301 ± 0.0   | 54.215 ± 0.0   |
| Mes anterior                                  | 56.078 ± 0.0   | 63.471 ± 0.0   | 44.29 ± 0.0    | 39.712 ± 0.0   |
| Promedio móvil 3 meses                        | 61.082 ± 0.0   | 64.585 ± 0.0   | 55.486 ± 0.0   | 41.665 ± 0.0   |
| Mismo mes del año anterior                    | 175.978 ± 0.0  | 124.697 ± 0.0  | 160.293 ± 0.0  | 80.591 ± 0.0   |

### R2

| modelo                                        | 1             | 2             | 3             | 4             |
|:----------------------------------------------|:--------------|:--------------|:--------------|:--------------|
| GE (ST-GNN vial)                              | 0.955 ± 0.002 | 0.957 ± 0.002 | 0.947 ± 0.011 | 0.961 ± 0.002 |
| GC₂ (ST-GNN geográfica)                       | 0.955 ± 0.002 | 0.958 ± 0.001 | 0.951 ± 0.008 | 0.961 ± 0.002 |
| GC₁ (GRU sin grafo)                           | 0.953 ± 0.002 | 0.958 ± 0.001 | 0.946 ± 0.006 | 0.959 ± 0.002 |
| GE (ST-GNN vial), promedio de semillas        | 0.955 ± 0.0   | 0.96 ± 0.0    | 0.955 ± 0.0   | 0.961 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 0.955 ± 0.0   | 0.959 ± 0.0   | 0.956 ± 0.0   | 0.961 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 0.953 ± 0.0   | 0.959 ± 0.0   | 0.949 ± 0.0   | 0.96 ± 0.0    |
| XGBoost                                       | 0.785 ± 0.0   | 0.843 ± 0.0   | 0.93 ± 0.0    | 0.93 ± 0.0    |
| Mes anterior                                  | 0.964 ± 0.0   | 0.958 ± 0.0   | 0.96 ± 0.0    | 0.962 ± 0.0   |
| Promedio móvil 3 meses                        | 0.957 ± 0.0   | 0.957 ± 0.0   | 0.937 ± 0.0   | 0.959 ± 0.0   |
| Mismo mes del año anterior                    | 0.646 ± 0.0   | 0.84 ± 0.0    | 0.475 ± 0.0   | 0.845 ± 0.0   |

## Pruebas estadísticas (n = 43 distritos; MAE por distrito promediado entre ventanas y semillas)

Regla de éxito del AVC3: el GE supera a un GC si tiene MAE **y** RMSE globales menores y la diferencia del MAE por distrito es significativa (α = 0,05). La prueba (t pareada o Wilcoxon) se eligió con Shapiro-Wilk sobre las diferencias pareadas. Como apoyo se repitió la prueba sobre el RMSE por distrito.

| comparacion            | tipo           |   MAE_GE |   MAE_rival |   RMSE_GE |   RMSE_rival |   media_dif |   mediana_dif |   shapiro_W |   shapiro_p | prueba   |   estadistico |      p |   distritos_GE_mejor |   p_RMSE_distrito | menor_MAE_por_distrito   | prueba_RMSE   | GE_supera   |
|:-----------------------|:---------------|---------:|------------:|----------:|-------------:|------------:|--------------:|------------:|------------:|:---------|--------------:|-------:|---------------------:|------------------:|:-------------------------|:--------------|:------------|
| GE vs GC1              | AVC3           |  33.8387 |     33.7498 |   55.3941 |      56.0019 |      0.0888 |        0.0003 |      0.8581 |      0.0001 | Wilcoxon |           472 | 0.9952 |                   21 |            0.8064 | GC1                      | Wilcoxon      | no          |
| GE vs GC2              | AVC3           |  33.8387 |     33.4731 |   55.3941 |      54.9223 |      0.3652 |        0.183  |      0.6306 |      0      | Wilcoxon |           136 | 0      |                    8 |            0.0003 | GC2                      | Wilcoxon      | no          |
| GE vs xgboost          | complementaria |  33.8387 |     56.1864 |   55.3941 |     100.499  |    -22.3259 |       -7.5226 |      0.7367 |      0      | Wilcoxon |           132 | 0      |                   29 |            0      | GE                       | Wilcoxon      | sí          |
| GE vs mes_anterior     | complementaria |  33.8387 |     31.2706 |   55.3941 |      51.7597 |      2.5656 |        1.3565 |      0.8471 |      0      | Wilcoxon |            40 | 0      |                    6 |            0      | mes_anterior             | Wilcoxon      | no          |
| GE_ens vs GC1_ens      | extra          |  32.9072 |     33.3036 |   53.9356 |      55.4265 |     -0.396  |       -0.0932 |      0.8973 |      0.001  | Wilcoxon |           348 | 0.1338 |                   25 |            0.0155 | GE_ens                   | Wilcoxon      | no          |
| GE_ens vs GC2_ens      | extra          |  32.9072 |     32.7742 |   53.9356 |      53.9048 |      0.1328 |        0.0075 |      0.691  |      0      | Wilcoxon |           391 | 0.3285 |                   20 |            0.7514 | GC2_ens                  | Wilcoxon      | no          |
| GE_ens vs mes_anterior | extra          |  32.9072 |     31.2706 |   53.9356 |      51.7597 |      1.635  |        0.7014 |      0.8317 |      0      | Wilcoxon |            97 | 0      |                   11 |            0.0001 | mes_anterior             | Wilcoxon      | no          |

## Equidad algorítmica (OE4)

Error relativo del distrito = MAE del distrito / promedio de denuncias del distrito en la prueba, por ventana; luego promedio entre ventanas y semillas. Brecha = máximo − mínimo. Sectores = terciles de distritos según su volumen mensual medio de denuncias en entrenamiento (promedio de las 4 ventanas). 5 distritos cambiarían de tercil si se usara el entrenamiento de una sola ventana.

| modelo                                        |   error_rel_mediana |   min | distrito_min           |   max | distrito_max        |   brecha |   brecha_sin_playa |   media_bajo |   media_medio |   media_alto |
|:----------------------------------------------|--------------------:|------:|:-----------------------|------:|:--------------------|---------:|-------------------:|-------------:|--------------:|-------------:|
| GE (ST-GNN vial)                              |               0.163 | 0.101 | SAN JUAN DE LURIGANCHO | 1.361 | SANTA MARIA DEL MAR |    1.26  |              0.247 |        0.369 |         0.157 |        0.129 |
| GC₂ (ST-GNN geográfica)                       |               0.159 | 0.095 | SAN JUAN DE LURIGANCHO | 1.363 | SANTA MARIA DEL MAR |    1.268 |              0.252 |        0.368 |         0.156 |        0.127 |
| GC₁ (GRU sin grafo)                           |               0.166 | 0.098 | SAN JUAN DE LURIGANCHO | 1.377 | SANTA MARIA DEL MAR |    1.279 |              0.238 |        0.365 |         0.159 |        0.129 |
| GE (ST-GNN vial), promedio de semillas        |               0.154 | 0.098 | SAN JUAN DE LURIGANCHO | 1.358 | SANTA MARIA DEL MAR |    1.26  |              0.25  |        0.365 |         0.153 |        0.125 |
| GC₂ (ST-GNN geográfica), promedio de semillas |               0.151 | 0.093 | SAN JUAN DE LURIGANCHO | 1.361 | SANTA MARIA DEL MAR |    1.267 |              0.254 |        0.365 |         0.153 |        0.125 |
| GC₁ (GRU sin grafo), promedio de semillas     |               0.163 | 0.096 | SAN JUAN DE LURIGANCHO | 1.375 | SANTA MARIA DEL MAR |    1.28  |              0.239 |        0.363 |         0.156 |        0.128 |
| XGBoost                                       |               0.235 | 0.112 | CARABAYLLO             | 1.106 | SANTA MARIA DEL MAR |    0.994 |              0.283 |        0.375 |         0.238 |        0.18  |
| Mes anterior                                  |               0.14  | 0.09  | SAN JUAN DE LURIGANCHO | 1.379 | SANTA MARIA DEL MAR |    1.289 |              0.259 |        0.368 |         0.146 |        0.118 |
| Promedio móvil 3 meses                        |               0.158 | 0.094 | BREÑA                  | 1.262 | SANTA MARIA DEL MAR |    1.168 |              0.173 |        0.345 |         0.156 |        0.132 |
| Mismo mes del año anterior                    |               0.38  | 0.219 | CARABAYLLO             | 1.7   | SANTA MARIA DEL MAR |    1.481 |              0.359 |        0.524 |         0.397 |        0.343 |

### Diferencias entre sectores

ANOVA si los tres grupos pasan Shapiro-Wilk y Levene; si no, Kruskal-Wallis (α = 0,05).

| modelo                                        | prueba         |   estadistico |      p | significativa   |
|:----------------------------------------------|:---------------|--------------:|-------:|:----------------|
| GE (ST-GNN vial)                              | Kruskal-Wallis |       24.9153 | 0      | sí              |
| GC₂ (ST-GNN geográfica)                       | Kruskal-Wallis |       25.2197 | 0      | sí              |
| GC₁ (GRU sin grafo)                           | Kruskal-Wallis |       23.7798 | 0      | sí              |
| GE (ST-GNN vial), promedio de semillas        | Kruskal-Wallis |       24.8216 | 0      | sí              |
| GC₂ (ST-GNN geográfica), promedio de semillas | Kruskal-Wallis |       24.9153 | 0      | sí              |
| GC₁ (GRU sin grafo), promedio de semillas     | Kruskal-Wallis |       23.8668 | 0      | sí              |
| XGBoost                                       | Kruskal-Wallis |       20.0127 | 0      | sí              |
| Mes anterior                                  | Kruskal-Wallis |       25.1103 | 0      | sí              |
| Promedio móvil 3 meses                        | Kruskal-Wallis |       20.5053 | 0      | sí              |
| Mismo mes del año anterior                    | Kruskal-Wallis |        6.7841 | 0.0336 | sí              |

### Composición de los sectores

| sector   | distritos                                                                                                                                                                                                              |
|:---------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bajo     | ANCON, CHACLACAYO, CIENEGUILLA, LA MOLINA, LURIN, MAGDALENA DEL MAR, PACHACAMAC, PUCUSANA, PUNTA HERMOSA, PUNTA NEGRA, SAN BARTOLO, SAN LUIS, SAN MIGUEL, SANTA MARIA DEL MAR, SANTA ROSA                              |
| medio    | BARRANCO, BREÑA, CHORRILLOS, JESUS MARIA, LINCE, LURIGANCHO - CHOSICA, MIRAFLORES, PUEBLO LIBRE, PUENTE PIEDRA, RIMAC, SAN BORJA, SAN ISIDRO, SANTA ANITA, SURQUILLO                                                   |
| alto     | ATE, CARABAYLLO, COMAS, EL AGUSTINO, INDEPENDENCIA, LA VICTORIA, LIMA, LOS OLIVOS, SAN JUAN DE LURIGANCHO, SAN JUAN DE MIRAFLORES, SAN MARTIN DE PORRES, SANTIAGO DE SURCO, VILLA EL SALVADOR, VILLA MARIA DEL TRIUNFO |

### Distritos de bajo volumen (playa), error relativo

| distrito            |   GE (ST-GNN vial) |   GC₂ (ST-GNN geográfica) |   GC₁ (GRU sin grafo) |   GE (ST-GNN vial), promedio de semillas |   GC₂ (ST-GNN geográfica), promedio de semillas |   GC₁ (GRU sin grafo), promedio de semillas |   XGBoost |   Mes anterior |   Promedio móvil 3 meses |   Mismo mes del año anterior |
|:--------------------|-------------------:|--------------------------:|----------------------:|-----------------------------------------:|------------------------------------------------:|--------------------------------------------:|----------:|---------------:|-------------------------:|-----------------------------:|
| PUCUSANA            |              0.334 |                     0.334 |                 0.343 |                                    0.332 |                                           0.332 |                                       0.341 |     0.323 |          0.334 |                    0.321 |                        0.511 |
| PUNTA HERMOSA       |              0.55  |                     0.545 |                 0.557 |                                    0.544 |                                           0.544 |                                       0.553 |     0.519 |          0.564 |                    0.625 |                        0.59  |
| PUNTA NEGRA         |              0.49  |                     0.492 |                 0.474 |                                    0.481 |                                           0.486 |                                       0.466 |     0.457 |          0.485 |                    0.477 |                        0.615 |
| SAN BARTOLO         |              0.431 |                     0.429 |                 0.406 |                                    0.425 |                                           0.426 |                                       0.404 |     0.39  |          0.428 |                    0.4   |                        0.404 |
| SANTA MARIA DEL MAR |              1.361 |                     1.363 |                 1.377 |                                    1.358 |                                           1.361 |                                       1.375 |     1.106 |          1.379 |                    1.262 |                        1.7   |

Los distritos de playa tienen pocas denuncias por mes; un error de pocas denuncias se vuelve un error relativo grande. Por eso la brecha se informa también sin ellos.
