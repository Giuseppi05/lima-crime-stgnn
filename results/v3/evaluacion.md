# Evaluación: desempeño predictivo (OE2), pruebas estadísticas y equidad (OE4)

Generado por `python -m src.evaluar`. Métricas en número de denuncias; se excluyen las 9 celdas sin información. Media ± desviación estándar entre las 5 semillas (las referencias y XGBoost son deterministas: una corrida). Nota. Elaboración propia.

## Métricas globales (4 ventanas de prueba, 48 meses × 43 distritos)

| modelo                     | MAE            | RMSE           | R2            | MASE          |
|:---------------------------|:---------------|:---------------|:--------------|:--------------|
| GE (ST-GNN vial)           | 32.186 ± 0.319 | 53.195 ± 0.532 | 0.96 ± 0.001  | 1.026 ± 0.01  |
| GC₂ (ST-GNN geográfica)    | 32.193 ± 0.337 | 53.193 ± 0.556 | 0.96 ± 0.001  | 1.026 ± 0.011 |
| GC₁ (GRU sin grafo)        | 35.12 ± 1.18   | 58.703 ± 2.316 | 0.951 ± 0.004 | 1.118 ± 0.037 |
| XGBoost                    | 57.039 ± 0.0   | 102.035 ± 0.0  | 0.854 ± 0.0   | 1.819 ± 0.0   |
| Mes anterior               | 31.271 ± 0.0   | 51.76 ± 0.0    | 0.962 ± 0.0   | 0.997 ± 0.0   |
| Promedio móvil 3 meses     | 34.05 ± 0.0    | 56.397 ± 0.0   | 0.955 ± 0.0   | 1.086 ± 0.0   |
| Mismo mes del año anterior | 86.808 ± 0.0   | 140.319 ± 0.0  | 0.723 ± 0.0   | 2.766 ± 0.0   |


MASE (complementaria): MAE del modelo entre el MAE del 'mes anterior' dentro del entrenamiento de cada ventana; promedio de las 4 ventanas.

## Métricas por ventana

### MAE

| modelo                     | 1              | 2              | 3              | 4              |
|:---------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)           | 37.11 ± 1.031  | 38.75 ± 0.218  | 27.245 ± 0.298 | 25.611 ± 0.298 |
| GC₂ (ST-GNN geográfica)    | 37.146 ± 1.065 | 38.76 ± 0.238  | 27.236 ± 0.33  | 25.603 ± 0.293 |
| GC₁ (GRU sin grafo)        | 45.614 ± 6.111 | 39.537 ± 0.753 | 29.547 ± 1.071 | 25.747 ± 0.372 |
| XGBoost                    | 85.304 ± 0.0   | 76.455 ± 0.0   | 35.914 ± 0.0   | 30.38 ± 0.0    |
| Mes anterior               | 33.436 ± 0.0   | 38.977 ± 0.0   | 27.215 ± 0.0   | 25.432 ± 0.0   |
| Promedio móvil 3 meses     | 37.44 ± 0.0    | 40.926 ± 0.0   | 31.973 ± 0.0   | 25.829 ± 0.0   |
| Mismo mes del año anterior | 115.18 ± 0.0   | 76.866 ± 0.0   | 108.126 ± 0.0  | 46.905 ± 0.0   |

### RMSE

| modelo                     | 1              | 2              | 3              | 4              |
|:---------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)           | 61.483 ± 1.325 | 62.998 ± 0.418 | 44.186 ± 0.633 | 40.15 ± 0.399  |
| GC₂ (ST-GNN geográfica)    | 61.491 ± 1.385 | 63.037 ± 0.416 | 44.132 ± 0.678 | 40.123 ± 0.374 |
| GC₁ (GRU sin grafo)        | 73.974 ± 8.773 | 64.196 ± 0.987 | 49.301 ± 1.748 | 41.301 ± 0.647 |
| XGBoost                    | 136.626 ± 0.0  | 124.921 ± 0.0  | 64.412 ± 0.0   | 56.53 ± 0.0    |
| Mes anterior               | 56.078 ± 0.0   | 63.471 ± 0.0   | 44.29 ± 0.0    | 39.712 ± 0.0   |
| Promedio móvil 3 meses     | 61.082 ± 0.0   | 64.585 ± 0.0   | 55.486 ± 0.0   | 41.665 ± 0.0   |
| Mismo mes del año anterior | 175.978 ± 0.0  | 124.697 ± 0.0  | 160.293 ± 0.0  | 80.591 ± 0.0   |

### R2

| modelo                     | 1             | 2             | 3            | 4             |
|:---------------------------|:--------------|:--------------|:-------------|:--------------|
| GE (ST-GNN vial)           | 0.957 ± 0.002 | 0.959 ± 0.001 | 0.96 ± 0.001 | 0.962 ± 0.001 |
| GC₂ (ST-GNN geográfica)    | 0.957 ± 0.002 | 0.959 ± 0.001 | 0.96 ± 0.001 | 0.962 ± 0.001 |
| GC₁ (GRU sin grafo)        | 0.937 ± 0.015 | 0.957 ± 0.001 | 0.95 ± 0.004 | 0.959 ± 0.001 |
| XGBoost                    | 0.787 ± 0.0   | 0.839 ± 0.0   | 0.915 ± 0.0  | 0.924 ± 0.0   |
| Mes anterior               | 0.964 ± 0.0   | 0.958 ± 0.0   | 0.96 ± 0.0   | 0.962 ± 0.0   |
| Promedio móvil 3 meses     | 0.957 ± 0.0   | 0.957 ± 0.0   | 0.937 ± 0.0  | 0.959 ± 0.0   |
| Mismo mes del año anterior | 0.646 ± 0.0   | 0.84 ± 0.0    | 0.475 ± 0.0  | 0.845 ± 0.0   |

## Pruebas estadísticas (n = 43 distritos; MAE por distrito promediado entre ventanas y semillas)

Regla de éxito del AVC3: el GE supera a un GC si tiene MAE **y** RMSE globales menores y la diferencia del MAE por distrito es significativa (α = 0,05). La prueba (t pareada o Wilcoxon) se eligió con Shapiro-Wilk sobre las diferencias pareadas. Como apoyo se repitió la prueba sobre el RMSE por distrito.

| comparacion        | tipo           |   MAE_GE |   MAE_rival |   RMSE_GE |   RMSE_rival |   media_dif |   mediana_dif |   shapiro_W |   shapiro_p | prueba   |   estadistico |      p |   distritos_GE_mejor |   p_RMSE_distrito | menor_MAE_por_distrito   | prueba_RMSE   | GE_supera   |
|:-------------------|:---------------|---------:|------------:|----------:|-------------:|------------:|--------------:|------------:|------------:|:---------|--------------:|-------:|---------------------:|------------------:|:-------------------------|:--------------|:------------|
| GE vs GC1          | AVC3           |  32.1856 |     35.1203 |   53.1955 |      58.7033 |     -2.9319 |       -1.3983 |      0.7305 |           0 | Wilcoxon |           112 | 0      |                   31 |            0      | GE                       | Wilcoxon      | sí          |
| GE vs GC2          | AVC3           |  32.1856 |     32.1925 |   53.1955 |      53.1934 |     -0.007  |        0.007  |      0.6306 |           0 | Wilcoxon |           303 | 0.0398 |                   13 |            0.0331 | GE                       | Wilcoxon      | no          |
| GE vs xgboost      | complementaria |  32.1856 |     57.0392 |   53.1955 |     102.035  |    -24.8294 |       -8.0718 |      0.7224 |           0 | Wilcoxon |            90 | 0      |                   32 |            0      | GE                       | Wilcoxon      | sí          |
| GE vs mes_anterior | complementaria |  32.1856 |     31.2706 |   53.1955 |      51.7597 |      0.9141 |        0.3567 |      0.7951 |           0 | Wilcoxon |           104 | 0      |                    7 |            0      | mes_anterior             | Wilcoxon      | no          |

## Equidad algorítmica (OE4)

Error relativo del distrito = MAE del distrito / promedio de denuncias del distrito en la prueba, por ventana; luego promedio entre ventanas y semillas. Brecha = máximo − mínimo. Sectores = terciles de distritos según su volumen mensual medio de denuncias en entrenamiento (promedio de las 4 ventanas). 5 distritos cambiarían de tercil si se usara el entrenamiento de una sola ventana.

| modelo                     |   error_rel_mediana |   min | distrito_min           |   max | distrito_max        |   brecha |   brecha_sin_playa |   media_bajo |   media_medio |   media_alto |
|:---------------------------|--------------------:|------:|:-----------------------|------:|:--------------------|---------:|-------------------:|-------------:|--------------:|-------------:|
| GE (ST-GNN vial)           |               0.144 | 0.089 | SAN JUAN DE LURIGANCHO | 1.383 | SANTA MARIA DEL MAR |    1.294 |              0.26  |        0.37  |         0.149 |        0.122 |
| GC₂ (ST-GNN geográfica)    |               0.144 | 0.09  | SAN JUAN DE LURIGANCHO | 1.383 | SANTA MARIA DEL MAR |    1.293 |              0.26  |        0.37  |         0.149 |        0.121 |
| GC₁ (GRU sin grafo)        |               0.168 | 0.104 | SAN JUAN DE LURIGANCHO | 1.327 | SANTA MARIA DEL MAR |    1.223 |              0.237 |        0.361 |         0.16  |        0.133 |
| XGBoost                    |               0.24  | 0.095 | CARABAYLLO             | 1.143 | SANTA MARIA DEL MAR |    1.048 |              0.345 |        0.374 |         0.24  |        0.184 |
| Mes anterior               |               0.14  | 0.09  | SAN JUAN DE LURIGANCHO | 1.379 | SANTA MARIA DEL MAR |    1.289 |              0.259 |        0.368 |         0.146 |        0.118 |
| Promedio móvil 3 meses     |               0.158 | 0.094 | BREÑA                  | 1.262 | SANTA MARIA DEL MAR |    1.168 |              0.173 |        0.345 |         0.156 |        0.132 |
| Mismo mes del año anterior |               0.38  | 0.219 | CARABAYLLO             | 1.7   | SANTA MARIA DEL MAR |    1.481 |              0.359 |        0.524 |         0.397 |        0.343 |

### Diferencias entre sectores

ANOVA si los tres grupos pasan Shapiro-Wilk y Levene; si no, Kruskal-Wallis (α = 0,05).

| modelo                     | prueba         |   estadistico |      p | significativa   |
|:---------------------------|:---------------|--------------:|-------:|:----------------|
| GE (ST-GNN vial)           | Kruskal-Wallis |       25.2045 | 0      | sí              |
| GC₂ (ST-GNN geográfica)    | Kruskal-Wallis |       25.4007 | 0      | sí              |
| GC₁ (GRU sin grafo)        | Kruskal-Wallis |       24.6385 | 0      | sí              |
| XGBoost                    | Kruskal-Wallis |       19.5819 | 0.0001 | sí              |
| Mes anterior               | Kruskal-Wallis |       25.1103 | 0      | sí              |
| Promedio móvil 3 meses     | Kruskal-Wallis |       20.5053 | 0      | sí              |
| Mismo mes del año anterior | Kruskal-Wallis |        6.7841 | 0.0336 | sí              |

### Composición de los sectores

| sector   | distritos                                                                                                                                                                                                              |
|:---------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bajo     | ANCON, CHACLACAYO, CIENEGUILLA, LA MOLINA, LURIN, MAGDALENA DEL MAR, PACHACAMAC, PUCUSANA, PUNTA HERMOSA, PUNTA NEGRA, SAN BARTOLO, SAN LUIS, SAN MIGUEL, SANTA MARIA DEL MAR, SANTA ROSA                              |
| medio    | BARRANCO, BREÑA, CHORRILLOS, JESUS MARIA, LINCE, LURIGANCHO - CHOSICA, MIRAFLORES, PUEBLO LIBRE, PUENTE PIEDRA, RIMAC, SAN BORJA, SAN ISIDRO, SANTA ANITA, SURQUILLO                                                   |
| alto     | ATE, CARABAYLLO, COMAS, EL AGUSTINO, INDEPENDENCIA, LA VICTORIA, LIMA, LOS OLIVOS, SAN JUAN DE LURIGANCHO, SAN JUAN DE MIRAFLORES, SAN MARTIN DE PORRES, SANTIAGO DE SURCO, VILLA EL SALVADOR, VILLA MARIA DEL TRIUNFO |

### Distritos de bajo volumen (playa), error relativo

| distrito            |   GE (ST-GNN vial) |   GC₂ (ST-GNN geográfica) |   GC₁ (GRU sin grafo) |   XGBoost |   Mes anterior |   Promedio móvil 3 meses |   Mismo mes del año anterior |
|:--------------------|-------------------:|--------------------------:|----------------------:|----------:|---------------:|-------------------------:|-----------------------------:|
| PUCUSANA            |              0.337 |                     0.337 |                 0.341 |     0.301 |          0.334 |                    0.321 |                        0.511 |
| PUNTA HERMOSA       |              0.561 |                     0.562 |                 0.546 |     0.499 |          0.564 |                    0.625 |                        0.59  |
| PUNTA NEGRA         |              0.494 |                     0.494 |                 0.449 |     0.418 |          0.485 |                    0.477 |                        0.615 |
| SAN BARTOLO         |              0.43  |                     0.43  |                 0.396 |     0.401 |          0.428 |                    0.4   |                        0.404 |
| SANTA MARIA DEL MAR |              1.383 |                     1.383 |                 1.327 |     1.143 |          1.379 |                    1.262 |                        1.7   |

Los distritos de playa tienen pocas denuncias por mes; un error de pocas denuncias se vuelve un error relativo grande. Por eso la brecha se informa también sin ellos.
