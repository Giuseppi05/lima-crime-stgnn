# Evaluación: casos adversos

Generado por `python -m src.adversos`. GE ya entrenado (4 ventanas × 5 semillas), sin reentrenar; 5 sorteos por nivel. Métricas en la prueba, en denuncias. Nota. Elaboración propia.

|                                        |    MAE |   MAE_sd |   RMSE |    R2 |   cambio_MAE_pct |   corridas_peor |   n |
|:---------------------------------------|-------:|---------:|-------:|------:|-----------------:|----------------:|----:|
| ('limpio', '-')                        | 32.179 |    5.983 | 52.204 | 0.959 |            0     |               0 |  20 |
| ('aristas eliminadas', '10 %')         | 32.178 |    5.869 | 52.215 | 0.959 |           -0.008 |              46 | 100 |
| ('aristas eliminadas', '20 %')         | 32.191 |    5.878 | 52.218 | 0.959 |            0.027 |              56 | 100 |
| ('aristas eliminadas', '30 %')         | 32.185 |    5.881 | 52.186 | 0.959 |            0.006 |              43 | 100 |
| ('ruido en coordenadas', 'σ = 500 m')  | 32.179 |    5.86  | 52.204 | 0.959 |           -0     |              39 | 100 |
| ('ruido en coordenadas', 'σ = 1000 m') | 32.179 |    5.861 | 52.204 | 0.959 |            0     |              49 | 100 |
| ('meses faltantes', '10 %')            | 33.131 |    6.113 | 54.044 | 0.956 |            2.93  |              95 | 100 |

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
| GE (ST-GNN vial)           |            29.36  |            0.538 |             53.145 |             0.97  |            0.792 |           0.008 |
| GC₂ (ST-GNN geográfica)    |            29.086 |            0.256 |             52.777 |             0.446 |            0.795 |           0.003 |
| GC₁ (GRU sin grafo)        |            30.917 |            1.718 |             56.414 |             3.91  |            0.765 |           0.033 |
| XGBoost                    |           105.8   |          nan     |            160.323 |           nan     |           -0.89  |         nan     |
| Mes anterior               |            29.208 |          nan     |             52.905 |           nan     |            0.794 |         nan     |
| Promedio móvil 3 meses     |            36.922 |          nan     |             77.213 |           nan     |            0.562 |         nan     |
| Mismo mes del año anterior |           108.559 |          nan     |            169.552 |           nan     |           -1.114 |         nan     |
