# Evaluación: casos adversos

Generado por `python -m src.adversos`. GE ya entrenado (4 ventanas × 5 semillas), sin reentrenar; 5 sorteos por nivel. Métricas en la prueba, en denuncias. Nota. Elaboración propia.

|                                        |    MAE |   MAE_sd |   RMSE |    R2 |   cambio_MAE_pct |   corridas_peor |   n |
|:---------------------------------------|-------:|---------:|-------:|------:|-----------------:|----------------:|----:|
| ('limpio', '-')                        | 32.132 |    6.036 | 52.054 | 0.96  |            0     |               0 |  20 |
| ('aristas eliminadas', '10 %')         | 32.129 |    5.923 | 52.06  | 0.96  |           -0.016 |              46 | 100 |
| ('aristas eliminadas', '20 %')         | 32.141 |    5.927 | 52.067 | 0.96  |            0.02  |              53 | 100 |
| ('aristas eliminadas', '30 %')         | 32.135 |    5.923 | 52.051 | 0.96  |            0.004 |              52 | 100 |
| ('ruido en coordenadas', 'σ = 500 m')  | 32.132 |    5.913 | 52.054 | 0.96  |           -0     |              43 | 100 |
| ('ruido en coordenadas', 'σ = 1000 m') | 32.132 |    5.913 | 52.054 | 0.96  |            0     |              46 | 100 |
| ('meses faltantes', '10 %')            | 33.076 |    6.146 | 53.885 | 0.957 |            2.917 |              95 | 100 |

`cambio_MAE_pct`: cambio porcentual medio del MAE frente al mismo modelo con datos limpios. `corridas_peor`: casos en que el MAE subió.

**Ruido en coordenadas, con 4 decimales.** MAE limpio 32,1323; con σ = 500 m, 32,1323; con σ = 1000 m, 32,1324. El cambio del MAE es < 0,01 % en las 200 corridas con ruido (el máximo en valor absoluto es 0,0095 %), aunque ninguna dio un MAE idéntico al limpio: los pesos sí cambiaron (`cambio_abs_medio_peso` 0,0178 con σ = 500 m y 0,0228 con σ = 1000 m, tabla siguiente). Con 30 % de aristas eliminadas, los 5 sorteos dan MAE distintos en las 20 corridas; con el error de la caché de `main`, los sorteos 3 y 4 coincidían en 7 de 20.

### Cambio en los pesos del grafo vial por el ruido en coordenadas

Los tramos que cruzan dependen de los límites y no del centroide, así que el ruido solo cambia la distancia por red y, con ella, el peso; el conjunto de aristas no cambia.

|   sigma_m |   cambio_abs_medio_peso |   cambio_abs_max_peso |
|----------:|------------------------:|----------------------:|
|       500 |                  0.0178 |                0.2428 |
|      1000 |                  0.0228 |                0.208  |

## Pandemia (ventana P)

Entrenamiento 2018-01 – 2019-09, validación 2019-10 – 2020-03, prueba 2020-04 – 2021-03; todos los modelos reentrenados y ajustados con su propia validación. Media y desviación entre semillas.

| modelo                                        |   ('MAE', 'mean') |   ('MAE', 'std') |   ('RMSE', 'mean') |   ('RMSE', 'std') |   ('R2', 'mean') |   ('R2', 'std') |
|:----------------------------------------------|------------------:|-----------------:|-------------------:|------------------:|-----------------:|----------------:|
| GE (ST-GNN vial)                              |            29.223 |            0.436 |             52.69  |             0.589 |            0.796 |           0.005 |
| GC₂ (ST-GNN geográfica)                       |            29.193 |            0.43  |             52.661 |             0.591 |            0.796 |           0.005 |
| GC₁ (GRU sin grafo)                           |            32.153 |            1.783 |             57.639 |             3.036 |            0.755 |           0.025 |
| GE (ST-GNN vial), promedio de semillas        |            29.076 |          nan     |             52.556 |           nan     |            0.797 |         nan     |
| GC₂ (ST-GNN geográfica), promedio de semillas |            29.008 |          nan     |             52.501 |           nan     |            0.797 |         nan     |
| GC₁ (GRU sin grafo), promedio de semillas     |            31.51  |          nan     |             56.999 |           nan     |            0.761 |         nan     |
| XGBoost                                       |           105.8   |          nan     |            160.323 |           nan     |           -0.89  |         nan     |
| Mes anterior                                  |            29.208 |          nan     |             52.905 |           nan     |            0.794 |         nan     |
| Promedio móvil 3 meses                        |            36.922 |          nan     |             77.213 |           nan     |            0.562 |         nan     |
| Mismo mes del año anterior                    |           108.559 |          nan     |            169.552 |           nan     |           -1.114 |         nan     |
