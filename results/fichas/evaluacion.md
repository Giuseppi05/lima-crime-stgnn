# Evaluación: desempeño predictivo (OE2), pruebas estadísticas y equidad (OE4)

Generado por `python -m src.evaluar`. Métricas en número de denuncias; se excluyen las 9 celdas sin información. Media ± desviación estándar entre las 5 semillas (las referencias y XGBoost son deterministas: una corrida). Nota. Elaboración propia.

## Métricas globales (4 ventanas de prueba, 48 meses × 43 distritos)

| modelo                                        | MAE            | RMSE           | R2            | MASE          |
|:----------------------------------------------|:---------------|:---------------|:--------------|:--------------|
| GE (ST-GNN vial)                              | 32.139 ± 0.213 | 53.051 ± 0.385 | 0.96 ± 0.001  | 1.024 ± 0.007 |
| GC₂ (ST-GNN geográfica)                       | 32.162 ± 0.207 | 53.064 ± 0.36  | 0.96 ± 0.001  | 1.025 ± 0.007 |
| GC₁ (GRU sin grafo)                           | 32.566 ± 0.174 | 53.889 ± 0.34  | 0.959 ± 0.001 | 1.038 ± 0.006 |
| GE (ST-GNN vial), promedio de semillas        | 32.047 ± 0.0   | 52.892 ± 0.0   | 0.961 ± 0.0   | 1.021 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 32.052 ± 0.0   | 52.895 ± 0.0   | 0.961 ± 0.0   | 1.021 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 32.152 ± 0.0   | 53.189 ± 0.0   | 0.96 ± 0.0    | 1.024 ± 0.0   |
| XGBoost                                       | 57.039 ± 0.0   | 102.035 ± 0.0  | 0.854 ± 0.0   | 1.819 ± 0.0   |
| Mes anterior                                  | 31.271 ± 0.0   | 51.76 ± 0.0    | 0.962 ± 0.0   | 0.997 ± 0.0   |
| Promedio móvil 3 meses                        | 34.05 ± 0.0    | 56.397 ± 0.0   | 0.955 ± 0.0   | 1.086 ± 0.0   |
| Mismo mes del año anterior                    | 86.808 ± 0.0   | 140.319 ± 0.0  | 0.723 ± 0.0   | 2.766 ± 0.0   |


MASE (complementaria): MAE del modelo entre el MAE del 'mes anterior' dentro del entrenamiento de cada ventana; promedio de las 4 ventanas.

## Métricas por ventana

### MAE

| modelo                                        | 1              | 2              | 3              | 4              |
|:----------------------------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 37.229 ± 1.025 | 38.638 ± 0.117 | 27.25 ± 0.615  | 25.413 ± 0.142 |
| GC₂ (ST-GNN geográfica)                       | 37.314 ± 0.996 | 38.631 ± 0.108 | 27.258 ± 0.581 | 25.417 ± 0.139 |
| GC₁ (GRU sin grafo)                           | 38.204 ± 0.58  | 39.805 ± 0.852 | 26.75 ± 0.529  | 25.479 ± 0.137 |
| GE (ST-GNN vial), promedio de semillas        | 37.185 ± 0.0   | 38.471 ± 0.0   | 27.124 ± 0.0   | 25.381 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 37.261 ± 0.0   | 38.471 ± 0.0   | 27.13 ± 0.0    | 25.321 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 38.154 ± 0.0   | 38.381 ± 0.0   | 26.597 ± 0.0   | 25.452 ± 0.0   |
| XGBoost                                       | 85.304 ± 0.0   | 76.455 ± 0.0   | 35.914 ± 0.0   | 30.38 ± 0.0    |
| Mes anterior                                  | 33.436 ± 0.0   | 38.977 ± 0.0   | 27.215 ± 0.0   | 25.432 ± 0.0   |
| Promedio móvil 3 meses                        | 37.44 ± 0.0    | 40.926 ± 0.0   | 31.973 ± 0.0   | 25.829 ± 0.0   |
| Mismo mes del año anterior                    | 115.18 ± 0.0   | 76.866 ± 0.0   | 108.126 ± 0.0  | 46.905 ± 0.0   |

### RMSE

| modelo                                        | 1              | 2              | 3              | 4              |
|:----------------------------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 61.363 ± 1.416 | 62.813 ± 0.144 | 44.109 ± 1.073 | 39.931 ± 0.179 |
| GC₂ (ST-GNN geográfica)                       | 61.457 ± 1.369 | 62.822 ± 0.132 | 44.09 ± 1.041  | 39.862 ± 0.151 |
| GC₁ (GRU sin grafo)                           | 62.825 ± 0.558 | 63.997 ± 1.021 | 43.712 ± 0.833 | 40.703 ± 0.198 |
| GE (ST-GNN vial), promedio de semillas        | 61.264 ± 0.0   | 62.58 ± 0.0    | 43.88 ± 0.0    | 39.882 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 61.362 ± 0.0   | 62.593 ± 0.0   | 43.868 ± 0.0   | 39.74 ± 0.0    |
| GC₁ (GRU sin grafo), promedio de semillas     | 62.694 ± 0.0   | 61.919 ± 0.0   | 43.513 ± 0.0   | 40.67 ± 0.0    |
| XGBoost                                       | 136.626 ± 0.0  | 124.921 ± 0.0  | 64.412 ± 0.0   | 56.53 ± 0.0    |
| Mes anterior                                  | 56.078 ± 0.0   | 63.471 ± 0.0   | 44.29 ± 0.0    | 39.712 ± 0.0   |
| Promedio móvil 3 meses                        | 61.082 ± 0.0   | 64.585 ± 0.0   | 55.486 ± 0.0   | 41.665 ± 0.0   |
| Mismo mes del año anterior                    | 175.978 ± 0.0  | 124.697 ± 0.0  | 160.293 ± 0.0  | 80.591 ± 0.0   |

### R2

| modelo                                        | 1             | 2             | 3             | 4           |
|:----------------------------------------------|:--------------|:--------------|:--------------|:------------|
| GE (ST-GNN vial)                              | 0.957 ± 0.002 | 0.959 ± 0.0   | 0.96 ± 0.002  | 0.962 ± 0.0 |
| GC₂ (ST-GNN geográfica)                       | 0.957 ± 0.002 | 0.959 ± 0.0   | 0.96 ± 0.002  | 0.962 ± 0.0 |
| GC₁ (GRU sin grafo)                           | 0.955 ± 0.001 | 0.958 ± 0.001 | 0.961 ± 0.001 | 0.96 ± 0.0  |
| GE (ST-GNN vial), promedio de semillas        | 0.957 ± 0.0   | 0.96 ± 0.0    | 0.961 ± 0.0   | 0.962 ± 0.0 |
| GC₂ (ST-GNN geográfica), promedio de semillas | 0.957 ± 0.0   | 0.96 ± 0.0    | 0.961 ± 0.0   | 0.962 ± 0.0 |
| GC₁ (GRU sin grafo), promedio de semillas     | 0.955 ± 0.0   | 0.96 ± 0.0    | 0.961 ± 0.0   | 0.961 ± 0.0 |
| XGBoost                                       | 0.787 ± 0.0   | 0.839 ± 0.0   | 0.915 ± 0.0   | 0.924 ± 0.0 |
| Mes anterior                                  | 0.964 ± 0.0   | 0.958 ± 0.0   | 0.96 ± 0.0    | 0.962 ± 0.0 |
| Promedio móvil 3 meses                        | 0.957 ± 0.0   | 0.957 ± 0.0   | 0.937 ± 0.0   | 0.959 ± 0.0 |
| Mismo mes del año anterior                    | 0.646 ± 0.0   | 0.84 ± 0.0    | 0.475 ± 0.0   | 0.845 ± 0.0 |

## Pruebas estadísticas (n = 43 distritos; MAE por distrito promediado entre ventanas y semillas)

Regla de éxito del AVC3: el GE supera a un GC si tiene MAE **y** RMSE globales menores y la diferencia del MAE por distrito es significativa (α = 0,05). La prueba (t pareada o Wilcoxon) se eligió con Shapiro-Wilk sobre las diferencias pareadas. Como apoyo se repitió la prueba sobre el RMSE por distrito.

| comparacion            | tipo           |   MAE_GE |   MAE_rival |   RMSE_GE |   RMSE_rival |   media_dif |   mediana_dif |   shapiro_W |   shapiro_p | prueba   |   estadistico |      p |   distritos_GE_mejor |   p_RMSE_distrito | menor_MAE_por_distrito   | prueba_RMSE   | GE_supera   |
|:-----------------------|:---------------|---------:|------------:|----------:|-------------:|------------:|--------------:|------------:|------------:|:---------|--------------:|-------:|---------------------:|------------------:|:-------------------------|:--------------|:------------|
| GE vs GC1              | AVC3           |  32.1389 |     32.5663 |   53.0514 |      53.8891 |     -0.4271 |       -0.0304 |      0.6782 |           0 | Wilcoxon |           393 | 0.3406 |                   25 |            0.0144 | GE                       | Wilcoxon      | no          |
| GE vs GC2              | AVC3           |  32.1389 |     32.1617 |   53.0514 |      53.0642 |     -0.0228 |       -0.0036 |      0.6794 |           0 | Wilcoxon |           280 | 0.019  |                   27 |            0.3593 | GE                       | Wilcoxon      | sí          |
| GE vs xgboost          | complementaria |  32.1389 |     57.0392 |   53.0514 |     102.035  |    -24.8761 |       -8.1423 |      0.7219 |           0 | Wilcoxon |            89 | 0      |                   32 |            0      | GE                       | Wilcoxon      | sí          |
| GE vs mes_anterior     | complementaria |  32.1389 |     31.2706 |   53.0514 |      51.7597 |      0.8674 |        0.5042 |      0.8046 |           0 | Wilcoxon |           130 | 0      |                   11 |            0      | mes_anterior             | Wilcoxon      | no          |
| GE_ens vs GC1_ens      | extra          |  32.0467 |     32.1522 |   52.892  |      53.1895 |     -0.1054 |        0.0073 |      0.7973 |           0 | Wilcoxon |           469 | 0.9666 |                   21 |            0.5537 | GE_ens                   | Wilcoxon      | no          |
| GE_ens vs GC2_ens      | extra          |  32.0467 |     32.0522 |   52.892  |      52.895  |     -0.0055 |        0.0003 |      0.7529 |           0 | Wilcoxon |           430 | 0.6112 |                   19 |            0.4258 | GE_ens                   | Wilcoxon      | no          |
| GE_ens vs mes_anterior | extra          |  32.0467 |     31.2706 |   52.892  |      51.7597 |      0.7754 |        0.4191 |      0.8028 |           0 | Wilcoxon |           159 | 0.0001 |                   12 |            0.0002 | mes_anterior             | Wilcoxon      | no          |

## Equidad algorítmica (OE4)

Error relativo del distrito = MAE del distrito / promedio de denuncias del distrito en la prueba, por ventana; luego promedio entre ventanas y semillas. Brecha = máximo − mínimo. Sectores = terciles de distritos según su volumen mensual medio de denuncias en entrenamiento (promedio de las 4 ventanas). 5 distritos cambiarían de tercil si se usara el entrenamiento de una sola ventana.

| modelo                                        |   error_rel_mediana |   min | distrito_min           |   max | distrito_max        |   brecha |   brecha_sin_playa |   media_bajo |   media_medio |   media_alto |
|:----------------------------------------------|--------------------:|------:|:-----------------------|------:|:--------------------|---------:|-------------------:|-------------:|--------------:|-------------:|
| GE (ST-GNN vial)                              |               0.145 | 0.09  | SAN JUAN DE LURIGANCHO | 1.382 | SANTA MARIA DEL MAR |    1.292 |              0.259 |        0.37  |         0.149 |        0.121 |
| GC₂ (ST-GNN geográfica)                       |               0.145 | 0.09  | SAN JUAN DE LURIGANCHO | 1.383 | SANTA MARIA DEL MAR |    1.293 |              0.259 |        0.37  |         0.149 |        0.121 |
| GC₁ (GRU sin grafo)                           |               0.146 | 0.093 | SANTIAGO DE SURCO      | 1.42  | SANTA MARIA DEL MAR |    1.327 |              0.255 |        0.373 |         0.15  |        0.122 |
| GE (ST-GNN vial), promedio de semillas        |               0.145 | 0.09  | SAN JUAN DE LURIGANCHO | 1.381 | SANTA MARIA DEL MAR |    1.291 |              0.259 |        0.369 |         0.149 |        0.121 |
| GC₂ (ST-GNN geográfica), promedio de semillas |               0.145 | 0.09  | SAN JUAN DE LURIGANCHO | 1.382 | SANTA MARIA DEL MAR |    1.292 |              0.259 |        0.37  |         0.149 |        0.121 |
| GC₁ (GRU sin grafo), promedio de semillas     |               0.144 | 0.092 | SANTIAGO DE SURCO      | 1.418 | SANTA MARIA DEL MAR |    1.326 |              0.256 |        0.372 |         0.149 |        0.121 |
| XGBoost                                       |               0.24  | 0.095 | CARABAYLLO             | 1.143 | SANTA MARIA DEL MAR |    1.048 |              0.345 |        0.374 |         0.24  |        0.184 |
| Mes anterior                                  |               0.14  | 0.09  | SAN JUAN DE LURIGANCHO | 1.379 | SANTA MARIA DEL MAR |    1.289 |              0.259 |        0.368 |         0.146 |        0.118 |
| Promedio móvil 3 meses                        |               0.158 | 0.094 | BREÑA                  | 1.262 | SANTA MARIA DEL MAR |    1.168 |              0.173 |        0.345 |         0.156 |        0.132 |
| Mismo mes del año anterior                    |               0.38  | 0.219 | CARABAYLLO             | 1.7   | SANTA MARIA DEL MAR |    1.481 |              0.359 |        0.524 |         0.397 |        0.343 |

### Diferencias entre sectores

ANOVA si los tres grupos pasan Shapiro-Wilk y Levene; si no, Kruskal-Wallis (α = 0,05).

| modelo                                        | prueba         |   estadistico |      p | significativa   |
|:----------------------------------------------|:---------------|--------------:|-------:|:----------------|
| GE (ST-GNN vial)                              | Kruskal-Wallis |       24.8216 | 0      | sí              |
| GC₂ (ST-GNN geográfica)                       | Kruskal-Wallis |       25.0178 | 0      | sí              |
| GC₁ (GRU sin grafo)                           | Kruskal-Wallis |       26.3802 | 0      | sí              |
| GE (ST-GNN vial), promedio de semillas        | Kruskal-Wallis |       24.6404 | 0      | sí              |
| GC₂ (ST-GNN geográfica), promedio de semillas | Kruskal-Wallis |       24.9272 | 0      | sí              |
| GC₁ (GRU sin grafo), promedio de semillas     | Kruskal-Wallis |       26.283  | 0      | sí              |
| XGBoost                                       | Kruskal-Wallis |       19.5819 | 0.0001 | sí              |
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
| PUCUSANA            |              0.336 |                     0.336 |                 0.334 |                                    0.336 |                                           0.336 |                                       0.333 |     0.301 |          0.334 |                    0.321 |                        0.511 |
| PUNTA HERMOSA       |              0.564 |                     0.565 |                 0.565 |                                    0.564 |                                           0.565 |                                       0.565 |     0.499 |          0.564 |                    0.625 |                        0.59  |
| PUNTA NEGRA         |              0.493 |                     0.493 |                 0.49  |                                    0.491 |                                           0.491 |                                       0.489 |     0.418 |          0.485 |                    0.477 |                        0.615 |
| SAN BARTOLO         |              0.431 |                     0.431 |                 0.432 |                                    0.43  |                                           0.43  |                                       0.43  |     0.401 |          0.428 |                    0.4   |                        0.404 |
| SANTA MARIA DEL MAR |              1.382 |                     1.383 |                 1.42  |                                    1.381 |                                           1.382 |                                       1.418 |     1.143 |          1.379 |                    1.262 |                        1.7   |

Los distritos de playa tienen pocas denuncias por mes; un error de pocas denuncias se vuelve un error relativo grande. Por eso la brecha se informa también sin ellos.
