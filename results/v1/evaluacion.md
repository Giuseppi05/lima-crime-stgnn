# Evaluación: desempeño predictivo (OE2), pruebas estadísticas y equidad (OE4)

Generado por `python -m src.evaluar`. Métricas en número de denuncias; se excluyen las 9 celdas sin información. Media ± desviación estándar entre las 5 semillas (las referencias y XGBoost son deterministas: una corrida). Nota. Elaboración propia.

## Métricas globales (4 ventanas de prueba, 48 meses × 43 distritos)

| modelo                     | MAE            | RMSE           | R2            | MASE          |
|:---------------------------|:---------------|:---------------|:--------------|:--------------|
| GE (ST-GNN vial)           | 33.414 ± 1.398 | 55.289 ± 2.57  | 0.957 ± 0.004 | 1.065 ± 0.045 |
| GC₂ (ST-GNN geográfica)    | 33.176 ± 1.024 | 54.686 ± 1.662 | 0.958 ± 0.003 | 1.058 ± 0.033 |
| GC₁ (GRU sin grafo)        | 32.88 ± 0.562  | 54.779 ± 0.805 | 0.958 ± 0.001 | 1.048 ± 0.018 |
| XGBoost                    | 56.389 ± 0.0   | 100.899 ± 0.0  | 0.857 ± 0.0   | 1.798 ± 0.0   |
| Mes anterior               | 31.271 ± 0.0   | 51.76 ± 0.0    | 0.962 ± 0.0   | 0.997 ± 0.0   |
| Promedio móvil 3 meses     | 34.05 ± 0.0    | 56.397 ± 0.0   | 0.955 ± 0.0   | 1.086 ± 0.0   |
| Mismo mes del año anterior | 86.808 ± 0.0   | 140.319 ± 0.0  | 0.723 ± 0.0   | 2.766 ± 0.0   |


MASE (complementaria): MAE del modelo entre el MAE del 'mes anterior' dentro del entrenamiento de cada ventana; promedio de las 4 ventanas.

## Métricas por ventana

### MAE

| modelo                     | 1              | 2              | 3              | 4              |
|:---------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)           | 37.229 ± 1.025 | 38.681 ± 0.115 | 32.343 ± 4.445 | 25.372 ± 0.205 |
| GC₂ (ST-GNN geográfica)    | 37.314 ± 0.996 | 38.671 ± 0.105 | 31.318 ± 3.241 | 25.369 ± 0.201 |
| GC₁ (GRU sin grafo)        | 38.204 ± 0.58  | 39.8 ± 1.122   | 27.826 ± 0.866 | 25.661 ± 0.322 |
| XGBoost                    | 84.443 ± 0.0   | 77.623 ± 0.0   | 31.804 ± 0.0   | 31.59 ± 0.0    |
| Mes anterior               | 33.436 ± 0.0   | 38.977 ± 0.0   | 27.215 ± 0.0   | 25.432 ± 0.0   |
| Promedio móvil 3 meses     | 37.44 ± 0.0    | 40.926 ± 0.0   | 31.973 ± 0.0   | 25.829 ± 0.0   |
| Mismo mes del año anterior | 115.18 ± 0.0   | 76.866 ± 0.0   | 108.126 ± 0.0  | 46.905 ± 0.0   |

### RMSE

| modelo                     | 1              | 2              | 3              | 4              |
|:---------------------------|:---------------|:---------------|:---------------|:---------------|
| GE (ST-GNN vial)           | 61.363 ± 1.416 | 62.893 ± 0.184 | 53.586 ± 8.683 | 39.854 ± 0.284 |
| GC₂ (ST-GNN geográfica)    | 61.457 ± 1.369 | 62.902 ± 0.176 | 51.161 ± 5.907 | 39.809 ± 0.263 |
| GC₁ (GRU sin grafo)        | 62.825 ± 0.558 | 64.597 ± 1.203 | 46.621 ± 2.663 | 41.225 ± 0.596 |
| XGBoost                    | 132.945 ± 0.0  | 127.961 ± 0.0  | 55.51 ± 0.0    | 59.727 ± 0.0   |
| Mes anterior               | 56.078 ± 0.0   | 63.471 ± 0.0   | 44.29 ± 0.0    | 39.712 ± 0.0   |
| Promedio móvil 3 meses     | 61.082 ± 0.0   | 64.585 ± 0.0   | 55.486 ± 0.0   | 41.665 ± 0.0   |
| Mismo mes del año anterior | 175.978 ± 0.0  | 124.697 ± 0.0  | 160.293 ± 0.0  | 80.591 ± 0.0   |

### R2

| modelo                     | 1             | 2             | 3             | 4             |
|:---------------------------|:--------------|:--------------|:--------------|:--------------|
| GE (ST-GNN vial)           | 0.957 ± 0.002 | 0.959 ± 0.0   | 0.94 ± 0.02   | 0.962 ± 0.001 |
| GC₂ (ST-GNN geográfica)    | 0.957 ± 0.002 | 0.959 ± 0.0   | 0.946 ± 0.013 | 0.962 ± 0.001 |
| GC₁ (GRU sin grafo)        | 0.955 ± 0.001 | 0.957 ± 0.002 | 0.955 ± 0.005 | 0.959 ± 0.001 |
| XGBoost                    | 0.798 ± 0.0   | 0.831 ± 0.0   | 0.937 ± 0.0   | 0.915 ± 0.0   |
| Mes anterior               | 0.964 ± 0.0   | 0.958 ± 0.0   | 0.96 ± 0.0    | 0.962 ± 0.0   |
| Promedio móvil 3 meses     | 0.957 ± 0.0   | 0.957 ± 0.0   | 0.937 ± 0.0   | 0.959 ± 0.0   |
| Mismo mes del año anterior | 0.646 ± 0.0   | 0.84 ± 0.0    | 0.475 ± 0.0   | 0.845 ± 0.0   |

## Pruebas estadísticas (n = 43 distritos; MAE por distrito promediado entre ventanas y semillas)

Regla de éxito del AVC3: el GE supera a un GC si tiene MAE **y** RMSE globales menores y la diferencia del MAE por distrito es significativa (α = 0,05). La prueba (t pareada o Wilcoxon) se eligió con Shapiro-Wilk sobre las diferencias pareadas. Como apoyo se repitió la prueba sobre el RMSE por distrito.

| comparacion        | tipo           |   MAE_GE |   MAE_rival |   RMSE_GE |   RMSE_rival |   media_dif |   mediana_dif |   shapiro_W |   shapiro_p | prueba   |   estadistico |      p |   distritos_GE_mejor |   p_RMSE_distrito | menor_MAE_por_distrito   | prueba_RMSE   | GE_supera   |
|:-------------------|:---------------|---------:|------------:|----------:|-------------:|------------:|--------------:|------------:|------------:|:---------|--------------:|-------:|---------------------:|------------------:|:-------------------------|:--------------|:------------|
| GE vs GC1          | AVC3           |  33.4137 |     32.8797 |   55.2885 |      54.7793 |      0.5335 |        0.2469 |      0.8451 |           0 | Wilcoxon |           317 | 0.0599 |                   15 |            0.1469 | GC1                      | Wilcoxon      | no          |
| GE vs GC2          | AVC3           |  33.4137 |     33.1757 |   55.2885 |      54.6856 |      0.2378 |        0.0411 |      0.6378 |           0 | Wilcoxon |           267 | 0.012  |                   16 |            0      | GC2                      | Wilcoxon      | no          |
| GE vs xgboost      | complementaria |  33.4137 |     56.3892 |   55.2885 |     100.899  |    -22.9531 |       -7.513  |      0.7377 |           0 | Wilcoxon |           125 | 0      |                   31 |            0      | GE                       | Wilcoxon      | sí          |
| GE vs mes_anterior | complementaria |  33.4137 |     31.2706 |   55.2885 |      51.7597 |      2.141  |        0.9958 |      0.8139 |           0 | Wilcoxon |            56 | 0      |                    5 |            0      | mes_anterior             | Wilcoxon      | no          |

## Equidad algorítmica (OE4)

Error relativo del distrito = MAE del distrito / promedio de denuncias del distrito en la prueba, por ventana; luego promedio entre ventanas y semillas. Brecha = máximo − mínimo. Sectores = terciles de distritos según su volumen mensual medio de denuncias en entrenamiento (promedio de las 4 ventanas). 5 distritos cambiarían de tercil si se usara el entrenamiento de una sola ventana.

| modelo                     |   error_rel_mediana |   min | distrito_min           |   max | distrito_max        |   brecha |   brecha_sin_playa |   media_bajo |   media_medio |   media_alto |
|:---------------------------|--------------------:|------:|:-----------------------|------:|:--------------------|---------:|-------------------:|-------------:|--------------:|-------------:|
| GE (ST-GNN vial)           |               0.151 | 0.104 | SAN JUAN DE LURIGANCHO | 1.351 | SANTA MARIA DEL MAR |    1.246 |              0.24  |        0.369 |         0.154 |        0.127 |
| GC₂ (ST-GNN geográfica)    |               0.152 | 0.1   | SAN JUAN DE LURIGANCHO | 1.348 | SANTA MARIA DEL MAR |    1.248 |              0.247 |        0.368 |         0.154 |        0.126 |
| GC₁ (GRU sin grafo)        |               0.151 | 0.093 | SAN JUAN DE LURIGANCHO | 1.415 | SANTA MARIA DEL MAR |    1.322 |              0.249 |        0.37  |         0.153 |        0.124 |
| XGBoost                    |               0.244 | 0.1   | CARABAYLLO             | 1.067 | SANTA MARIA DEL MAR |    0.967 |              0.307 |        0.364 |         0.241 |        0.181 |
| Mes anterior               |               0.14  | 0.09  | SAN JUAN DE LURIGANCHO | 1.379 | SANTA MARIA DEL MAR |    1.289 |              0.259 |        0.368 |         0.146 |        0.118 |
| Promedio móvil 3 meses     |               0.158 | 0.094 | BREÑA                  | 1.262 | SANTA MARIA DEL MAR |    1.168 |              0.173 |        0.345 |         0.156 |        0.132 |
| Mismo mes del año anterior |               0.38  | 0.219 | CARABAYLLO             | 1.7   | SANTA MARIA DEL MAR |    1.481 |              0.359 |        0.524 |         0.397 |        0.343 |

### Diferencias entre sectores

ANOVA si los tres grupos pasan Shapiro-Wilk y Levene; si no, Kruskal-Wallis (α = 0,05).

| modelo                     | prueba         |   estadistico |      p | significativa   |
|:---------------------------|:---------------|--------------:|-------:|:----------------|
| GE (ST-GNN vial)           | Kruskal-Wallis |       24.6663 | 0      | sí              |
| GC₂ (ST-GNN geográfica)    | Kruskal-Wallis |       24.9272 | 0      | sí              |
| GC₁ (GRU sin grafo)        | Kruskal-Wallis |       25.1164 | 0      | sí              |
| XGBoost                    | Kruskal-Wallis |       18.7139 | 0.0001 | sí              |
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
| PUCUSANA            |              0.338 |                     0.337 |                 0.336 |     0.313 |          0.334 |                    0.321 |                        0.511 |
| PUNTA HERMOSA       |              0.551 |                     0.552 |                 0.569 |     0.489 |          0.564 |                    0.625 |                        0.59  |
| PUNTA NEGRA         |              0.496 |                     0.489 |                 0.482 |     0.417 |          0.485 |                    0.477 |                        0.615 |
| SAN BARTOLO         |              0.428 |                     0.429 |                 0.414 |     0.364 |          0.428 |                    0.4   |                        0.404 |
| SANTA MARIA DEL MAR |              1.351 |                     1.348 |                 1.415 |     1.067 |          1.379 |                    1.262 |                        1.7   |

Los distritos de playa tienen pocas denuncias por mes; un error de pocas denuncias se vuelve un error relativo grande. Por eso la brecha se informa también sin ellos.
