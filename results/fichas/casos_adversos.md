# Evaluación: casos adversos

Generado por `python -m src.adversos`. GE ya entrenado (4 ventanas × 5 semillas), sin reentrenar; 5 sorteos por nivel. Métricas en la prueba, en denuncias. Nota. Elaboración propia.

|                                        |    MAE |   MAE_sd |   RMSE |    R2 |   cambio_MAE_pct |   corridas_peor |   n |
|:---------------------------------------|-------:|---------:|-------:|------:|-----------------:|----------------:|----:|
| ('limpio', '-')                        | 33.461 |    5.65  | 54.487 | 0.954 |            0     |               0 |  20 |
| ('aristas eliminadas', '10 %')         | 33.457 |    5.542 | 54.498 | 0.954 |           -0.015 |              52 | 100 |
| ('aristas eliminadas', '20 %')         | 33.434 |    5.53  | 54.466 | 0.955 |           -0.079 |              50 | 100 |
| ('aristas eliminadas', '30 %')         | 33.433 |    5.544 | 54.448 | 0.955 |           -0.091 |              45 | 100 |
| ('ruido en coordenadas', 'σ = 500 m')  | 33.461 |    5.535 | 54.487 | 0.954 |           -0     |              40 | 100 |
| ('ruido en coordenadas', 'σ = 1000 m') | 33.461 |    5.535 | 54.487 | 0.954 |            0     |              47 | 100 |
| ('meses faltantes', '10 %')            | 34.377 |    5.839 | 56.569 | 0.951 |            2.667 |              94 | 100 |

`cambio_MAE_pct`: cambio porcentual medio del MAE frente al mismo modelo con datos limpios. `corridas_peor`: casos en que el MAE subió.

### Cambio en los pesos del grafo vial por el ruido en coordenadas

Los tramos que cruzan dependen de los límites y no del centroide, así que el ruido solo cambia la distancia por red y, con ella, el peso; el conjunto de aristas no cambia.

|   sigma_m |   cambio_abs_medio_peso |   cambio_abs_max_peso |
|----------:|------------------------:|----------------------:|
|       500 |                  0.0178 |                0.2428 |
|      1000 |                  0.0228 |                0.208  |

## Pandemia (ventana P)

Entrenamiento 2018-01 – 2019-09, validación 2019-10 – 2020-03, prueba 2020-04 – 2021-03; todos los modelos reentrenados y ajustados con su propia validación. Media y desviación entre semillas.

| modelo                     |   ('MAE', 'mean') |   ('MAE', 'std') |   ('RMSE', 'mean') |   ('RMSE', 'std') |   ('R2', 'mean') |   ('R2', 'std') |
|:---------------------------|------------------:|-----------------:|-------------------:|------------------:|-----------------:|----------------:|
| GE (ST-GNN vial)           |            29.223 |            0.436 |             52.69  |             0.589 |            0.796 |           0.005 |
| GC₂ (ST-GNN geográfica)    |            29.193 |            0.43  |             52.661 |             0.591 |            0.796 |           0.005 |
| GC₁ (GRU sin grafo)        |            32.153 |            1.783 |             57.639 |             3.036 |            0.755 |           0.025 |
| XGBoost                    |           105.8   |          nan     |            160.323 |           nan     |           -0.89  |         nan     |
| Mes anterior               |            29.208 |          nan     |             52.905 |           nan     |            0.794 |         nan     |
| Promedio móvil 3 meses     |            36.922 |          nan     |             77.213 |           nan     |            0.562 |         nan     |
| Mismo mes del año anterior |           108.559 |          nan     |            169.552 |           nan     |           -1.114 |         nan     |
