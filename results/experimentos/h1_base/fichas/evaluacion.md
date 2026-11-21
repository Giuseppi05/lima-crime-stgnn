# Evaluación: desempeño predictivo (OE2), pruebas estadísticas y equidad (OE4)

Generado por `python -m src.evaluar`. Métricas en número de denuncias; se excluyen las 9 celdas sin información. Media ± desviación estándar entre las 5 semillas (las referencias y XGBoost son deterministas: una corrida). Nota. Elaboración propia.

## Métricas globales (4 ventanas de prueba, 48 meses × 43 distritos)

| modelo                                        | MAE            | RMSE           | R2            | MASE          |
|:----------------------------------------------|:---------------|:---------------|:--------------|:--------------|
| GE (ST-GNN vial)                              | 33.469 ± 1.368 | 55.335 ± 2.559 | 0.957 ± 0.004 | 1.067 ± 0.044 |
| GC₂ (ST-GNN geográfica)                       | 33.23 ± 0.963  | 54.737 ± 1.617 | 0.958 ± 0.003 | 1.059 ± 0.031 |
| GC₁ (GRU sin grafo)                           | 32.72 ± 0.403  | 54.489 ± 0.696 | 0.958 ± 0.001 | 1.043 ± 0.013 |
| GE (ST-GNN vial), promedio de semillas        | 32.744 ± 0.0   | 54.026 ± 0.0   | 0.959 ± 0.0   | 1.044 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 32.484 ± 0.0   | 53.681 ± 0.0   | 0.959 ± 0.0   | 1.035 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 32.327 ± 0.0   | 53.875 ± 0.0   | 0.959 ± 0.0   | 1.03 ± 0.0    |
| XGBoost                                       | 57.039 ± 0.0   | 102.035 ± 0.0  | 0.854 ± 0.0   | 1.819 ± 0.0   |
| Mes anterior                                  | 31.271 ± 0.0   | 51.76 ± 0.0    | 0.962 ± 0.0   | 0.997 ± 0.0   |
| Promedio móvil 3 meses                        | 34.05 ± 0.0    | 56.397 ± 0.0   | 0.955 ± 0.0   | 1.086 ± 0.0   |
| Mismo mes del año anterior                    | 86.808 ± 0.0   | 140.319 ± 0.0  | 0.723 ± 0.0   | 2.766 ± 0.0   |


MASE (complementaria): MAE del modelo entre el MAE del 'mes anterior' dentro del entrenamiento de cada ventana; promedio de las 4 ventanas.

## Métricas por ventana

### MAE

| modelo                                        | 1              | 2              | 3              | 4              |
|:----------------------------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 37.229 ± 1.025 | 38.681 ± 0.115 | 32.343 ± 4.445 | 25.593 ± 0.259 |
| GC₂ (ST-GNN geográfica)                       | 37.314 ± 0.996 | 38.671 ± 0.105 | 31.318 ± 3.241 | 25.589 ± 0.26  |
| GC₁ (GRU sin grafo)                           | 38.204 ± 0.58  | 39.162 ± 0.392 | 27.826 ± 0.866 | 25.661 ± 0.322 |
| GE (ST-GNN vial), promedio de semillas        | 37.185 ± 0.0   | 38.471 ± 0.0   | 30.072 ± 0.0   | 25.218 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 37.261 ± 0.0   | 38.472 ± 0.0   | 28.958 ± 0.0   | 25.216 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 38.154 ± 0.0   | 38.571 ± 0.0   | 26.996 ± 0.0   | 25.561 ± 0.0   |
| XGBoost                                       | 85.304 ± 0.0   | 76.455 ± 0.0   | 35.914 ± 0.0   | 30.38 ± 0.0    |
| Mes anterior                                  | 33.436 ± 0.0   | 38.977 ± 0.0   | 27.215 ± 0.0   | 25.432 ± 0.0   |
| Promedio móvil 3 meses                        | 37.44 ± 0.0    | 40.926 ± 0.0   | 31.973 ± 0.0   | 25.829 ± 0.0   |
| Mismo mes del año anterior                    | 115.18 ± 0.0   | 76.866 ± 0.0   | 108.126 ± 0.0  | 46.905 ± 0.0   |

### RMSE

| modelo                                        | 1              | 2              | 3              | 4              |
|:----------------------------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)                              | 61.363 ± 1.416 | 62.893 ± 0.184 | 53.586 ± 8.683 | 40.107 ± 0.316 |
| GC₂ (ST-GNN geográfica)                       | 61.457 ± 1.369 | 62.902 ± 0.176 | 51.161 ± 5.907 | 40.084 ± 0.3   |
| GC₁ (GRU sin grafo)                           | 62.825 ± 0.558 | 63.61 ± 0.521  | 46.621 ± 2.663 | 41.225 ± 0.596 |
| GE (ST-GNN vial), promedio de semillas        | 61.264 ± 0.0   | 62.602 ± 0.0   | 49.285 ± 0.0   | 39.609 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 61.362 ± 0.0   | 62.616 ± 0.0   | 47.628 ± 0.0   | 39.584 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 62.694 ± 0.0   | 62.894 ± 0.0   | 45.094 ± 0.0   | 41.056 ± 0.0   |
| XGBoost                                       | 136.626 ± 0.0  | 124.921 ± 0.0  | 64.412 ± 0.0   | 56.53 ± 0.0    |
| Mes anterior                                  | 56.078 ± 0.0   | 63.471 ± 0.0   | 44.29 ± 0.0    | 39.712 ± 0.0   |
| Promedio móvil 3 meses                        | 61.082 ± 0.0   | 64.585 ± 0.0   | 55.486 ± 0.0   | 41.665 ± 0.0   |
| Mismo mes del año anterior                    | 175.978 ± 0.0  | 124.697 ± 0.0  | 160.293 ± 0.0  | 80.591 ± 0.0   |

### R2

| modelo                                        | 1             | 2             | 3             | 4             |
|:----------------------------------------------|:--------------|:--------------|:--------------|:--------------|
| GE (ST-GNN vial)                              | 0.957 ± 0.002 | 0.959 ± 0.0   | 0.94 ± 0.02   | 0.962 ± 0.001 |
| GC₂ (ST-GNN geográfica)                       | 0.957 ± 0.002 | 0.959 ± 0.0   | 0.946 ± 0.013 | 0.962 ± 0.001 |
| GC₁ (GRU sin grafo)                           | 0.955 ± 0.001 | 0.958 ± 0.001 | 0.955 ± 0.005 | 0.959 ± 0.001 |
| GE (ST-GNN vial), promedio de semillas        | 0.957 ± 0.0   | 0.96 ± 0.0    | 0.95 ± 0.0    | 0.963 ± 0.0   |
| GC₂ (ST-GNN geográfica), promedio de semillas | 0.957 ± 0.0   | 0.96 ± 0.0    | 0.954 ± 0.0   | 0.963 ± 0.0   |
| GC₁ (GRU sin grafo), promedio de semillas     | 0.955 ± 0.0   | 0.959 ± 0.0   | 0.958 ± 0.0   | 0.96 ± 0.0    |
| XGBoost                                       | 0.787 ± 0.0   | 0.839 ± 0.0   | 0.915 ± 0.0   | 0.924 ± 0.0   |
| Mes anterior                                  | 0.964 ± 0.0   | 0.958 ± 0.0   | 0.96 ± 0.0    | 0.962 ± 0.0   |
| Promedio móvil 3 meses                        | 0.957 ± 0.0   | 0.957 ± 0.0   | 0.937 ± 0.0   | 0.959 ± 0.0   |
| Mismo mes del año anterior                    | 0.646 ± 0.0   | 0.84 ± 0.0    | 0.475 ± 0.0   | 0.845 ± 0.0   |

## Pruebas estadísticas (n = 43 distritos; MAE por distrito promediado entre ventanas y semillas)

Regla de éxito del AVC3: el GE supera a un GC si tiene MAE **y** RMSE globales menores y la diferencia del MAE por distrito es significativa (α = 0,05). La prueba (t pareada o Wilcoxon) se eligió con Shapiro-Wilk sobre las diferencias pareadas. Como apoyo se repitió la prueba sobre el RMSE por distrito.

| comparacion            | tipo           |   MAE_GE |   MAE_rival |   RMSE_GE |   RMSE_rival |   media_dif |   mediana_dif |   shapiro_W |   shapiro_p | prueba   |   estadistico |      p |   distritos_GE_mejor |   p_RMSE_distrito | menor_MAE_por_distrito   | prueba_RMSE   | GE_supera   |
|:-----------------------|:---------------|---------:|------------:|----------:|-------------:|------------:|--------------:|------------:|------------:|:---------|--------------:|-------:|---------------------:|------------------:|:-------------------------|:--------------|:------------|
| GE vs GC1              | AVC3           |  33.4689 |     32.72   |   55.3345 |      54.4886 |      0.7482 |        0.4513 |      0.8466 |      0      | Wilcoxon |           283 | 0.021  |                   14 |            0.0301 | GC1                      | Wilcoxon      | no          |
| GE vs GC2              | AVC3           |  33.4689 |     33.2305 |   55.3345 |      54.7368 |      0.2382 |        0.0409 |      0.6362 |      0      | Wilcoxon |           259 | 0.009  |                   15 |            0      | GC2                      | Wilcoxon      | no          |
| GE vs xgboost          | complementaria |  33.4689 |     57.0392 |   55.3345 |     102.035  |    -23.5473 |       -7.2183 |      0.7174 |      0      | Wilcoxon |           107 | 0      |                   31 |            0      | GE                       | Wilcoxon      | sí          |
| GE vs mes_anterior     | complementaria |  33.4689 |     31.2706 |   55.3345 |      51.7597 |      2.1962 |        1.1225 |      0.8195 |      0      | Wilcoxon |            54 | 0      |                    5 |            0      | mes_anterior             | Wilcoxon      | no          |
| GE_ens vs GC1_ens      | extra          |  32.7437 |     32.3268 |   54.0262 |      53.8748 |      0.4166 |        0.095  |      0.9221 |      0.0063 | Wilcoxon |           356 | 0.161  |                   16 |            0.1684 | GC1_ens                  | Wilcoxon      | no          |
| GE_ens vs GC2_ens      | extra          |  32.7437 |     32.4838 |   54.0262 |      53.6806 |      0.2596 |        0.0764 |      0.4899 |      0      | Wilcoxon |           174 | 0.0002 |                   11 |            0.0004 | GC2_ens                  | Wilcoxon      | no          |
| GE_ens vs mes_anterior | extra          |  32.7437 |     31.2706 |   54.0262 |      51.7597 |      1.4717 |        0.7065 |      0.837  |      0      | Wilcoxon |           113 | 0      |                   11 |            0      | mes_anterior             | Wilcoxon      | no          |

## Equidad algorítmica (OE4)

Error relativo del distrito = MAE del distrito / promedio de denuncias del distrito en la prueba, por ventana; luego promedio entre ventanas y semillas. Brecha = máximo − mínimo. Sectores = terciles de distritos según su volumen mensual medio de denuncias en entrenamiento (promedio de las 4 ventanas). 5 distritos cambiarían de tercil si se usara el entrenamiento de una sola ventana.

| modelo                                        |   error_rel_mediana |   min | distrito_min           |   max | distrito_max        |   brecha |   brecha_sin_playa |   media_bajo |   media_medio |   media_alto |
|:----------------------------------------------|--------------------:|------:|:-----------------------|------:|:--------------------|---------:|-------------------:|-------------:|--------------:|-------------:|
| GE (ST-GNN vial)                              |               0.151 | 0.104 | SAN JUAN DE LURIGANCHO | 1.352 | SANTA MARIA DEL MAR |    1.248 |              0.241 |        0.369 |         0.155 |        0.128 |
| GC₂ (ST-GNN geográfica)                       |               0.151 | 0.099 | SAN JUAN DE LURIGANCHO | 1.349 | SANTA MARIA DEL MAR |    1.25  |              0.247 |        0.368 |         0.154 |        0.126 |
| GC₁ (GRU sin grafo)                           |               0.151 | 0.092 | SAN JUAN DE LURIGANCHO | 1.413 | SANTA MARIA DEL MAR |    1.321 |              0.249 |        0.369 |         0.152 |        0.123 |
| GE (ST-GNN vial), promedio de semillas        |               0.15  | 0.101 | SAN JUAN DE LURIGANCHO | 1.35  | SANTA MARIA DEL MAR |    1.25  |              0.243 |        0.366 |         0.151 |        0.124 |
| GC₂ (ST-GNN geográfica), promedio de semillas |               0.149 | 0.095 | SAN JUAN DE LURIGANCHO | 1.347 | SANTA MARIA DEL MAR |    1.252 |              0.251 |        0.366 |         0.151 |        0.123 |
| GC₁ (GRU sin grafo), promedio de semillas     |               0.148 | 0.091 | SAN JUAN DE LURIGANCHO | 1.413 | SANTA MARIA DEL MAR |    1.322 |              0.249 |        0.367 |         0.15  |        0.122 |
| XGBoost                                       |               0.24  | 0.095 | CARABAYLLO             | 1.143 | SANTA MARIA DEL MAR |    1.048 |              0.345 |        0.374 |         0.24  |        0.184 |
| Mes anterior                                  |               0.14  | 0.09  | SAN JUAN DE LURIGANCHO | 1.379 | SANTA MARIA DEL MAR |    1.289 |              0.259 |        0.368 |         0.146 |        0.118 |
| Promedio móvil 3 meses                        |               0.158 | 0.094 | BREÑA                  | 1.262 | SANTA MARIA DEL MAR |    1.168 |              0.173 |        0.345 |         0.156 |        0.132 |
| Mismo mes del año anterior                    |               0.38  | 0.219 | CARABAYLLO             | 1.7   | SANTA MARIA DEL MAR |    1.481 |              0.359 |        0.524 |         0.397 |        0.343 |

### Diferencias entre sectores

ANOVA si los tres grupos pasan Shapiro-Wilk y Levene; si no, Kruskal-Wallis (α = 0,05).

| modelo                                        | prueba         |   estadistico |      p | significativa   |
|:----------------------------------------------|:---------------|--------------:|-------:|:----------------|
| GE (ST-GNN vial)                              | Kruskal-Wallis |       24.5829 | 0      | sí              |
| GC₂ (ST-GNN geográfica)                       | Kruskal-Wallis |       25.0178 | 0      | sí              |
| GC₁ (GRU sin grafo)                           | Kruskal-Wallis |       24.9282 | 0      | sí              |
| GE (ST-GNN vial), promedio de semillas        | Kruskal-Wallis |       24.8384 | 0      | sí              |
| GC₂ (ST-GNN geográfica), promedio de semillas | Kruskal-Wallis |       25.2045 | 0      | sí              |
| GC₁ (GRU sin grafo), promedio de semillas     | Kruskal-Wallis |       24.8259 | 0      | sí              |
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
| PUCUSANA            |              0.339 |                     0.338 |                 0.335 |                                    0.337 |                                           0.336 |                                       0.334 |     0.301 |          0.334 |                    0.321 |                        0.511 |
| PUNTA HERMOSA       |              0.551 |                     0.551 |                 0.568 |                                    0.547 |                                           0.549 |                                       0.558 |     0.499 |          0.564 |                    0.625 |                        0.59  |
| PUNTA NEGRA         |              0.496 |                     0.49  |                 0.479 |                                    0.492 |                                           0.487 |                                       0.461 |     0.418 |          0.485 |                    0.477 |                        0.615 |
| SAN BARTOLO         |              0.428 |                     0.429 |                 0.414 |                                    0.426 |                                           0.427 |                                       0.41  |     0.401 |          0.428 |                    0.4   |                        0.404 |
| SANTA MARIA DEL MAR |              1.352 |                     1.349 |                 1.413 |                                    1.35  |                                           1.347 |                                       1.413 |     1.143 |          1.379 |                    1.262 |                        1.7   |

Los distritos de playa tienen pocas denuncias por mes; un error de pocas denuncias se vuelve un error relativo grande. Por eso la brecha se informa también sin ellos.
