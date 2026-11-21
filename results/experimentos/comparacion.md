# Evaluación (opciones extra, fuera del AVC3): comparación de experimentos

Generado por `python -m src.comparar_experimentos`. Todos parten de la v2 (sin pérdida ponderada). Horizonte H: se predice el mes t con datos hasta t − H; la persistencia es el último mes observado (t − H). Modalidades: hurto, robo y la suma de las otras cinco como entradas. `GE_ens`: promedio de las 5 semillas. Hiperparámetros elegidos solo con validación. MAE en denuncias por distrito y mes, 4 ventanas. Nota. Elaboración propia.

## Validación (decide) — media de las 20 corridas finales

| experimento    |   horizonte | modalidades   |   val_GE |   val_GC2 |   val_GC1 |   val_persistencia |
|:---------------|------------:|:--------------|---------:|----------:|----------:|-------------------:|
| h1_base        |           1 | False         |   30.681 |    30.75  |    30.407 |             31.34  |
| h1_modalidades |           1 | True          |   30.788 |    30.854 |    30.104 |             31.34  |
| h3_base        |           3 | False         |   43.174 |    43.159 |    41.716 |             45.965 |
| h3_modalidades |           3 | True          |   43.118 |    43.44  |    41.698 |             45.965 |

## Prueba (solo se informa)

| experimento    |   prueba_GE |   prueba_GE_ens |   prueba_GC2 |   prueba_GC1 |   prueba_xgboost |   prueba_mes_anterior |
|:---------------|------------:|----------------:|-------------:|-------------:|-----------------:|----------------------:|
| h1_base        |      33.469 |          32.744 |       33.23  |       32.72  |           57.039 |                31.271 |
| h1_modalidades |      33.839 |          32.907 |       33.473 |       33.75  |           56.186 |                31.271 |
| h3_base        |      48.16  |          47.682 |       48.2   |       52.689 |           78.457 |                45.662 |
| h3_modalidades |      50.244 |          49.576 |       49.627 |       49.915 |           79.029 |                45.662 |

## Pruebas estadísticas (n = 43 distritos)

|                                              |   MAE_GE |   MAE_rival |      p |   distritos_GE_mejor | GE_supera   |
|:---------------------------------------------|---------:|------------:|-------:|---------------------:|:------------|
| ('h1_base', 'GE vs GC1')                     |  33.4689 |     32.72   | 0.021  |                   14 | no          |
| ('h1_base', 'GE vs GC2')                     |  33.4689 |     33.2305 | 0.009  |                   15 | no          |
| ('h1_base', 'GE vs xgboost')                 |  33.4689 |     57.0392 | 0      |                   31 | sí          |
| ('h1_base', 'GE vs mes_anterior')            |  33.4689 |     31.2706 | 0      |                    5 | no          |
| ('h1_base', 'GE_ens vs GC1_ens')             |  32.7437 |     32.3268 | 0.161  |                   16 | no          |
| ('h1_base', 'GE_ens vs GC2_ens')             |  32.7437 |     32.4838 | 0.0002 |                   11 | no          |
| ('h1_base', 'GE_ens vs mes_anterior')        |  32.7437 |     31.2706 | 0      |                   11 | no          |
| ('h1_modalidades', 'GE vs GC1')              |  33.8387 |     33.7498 | 0.9952 |                   21 | no          |
| ('h1_modalidades', 'GE vs GC2')              |  33.8387 |     33.4731 | 0      |                    8 | no          |
| ('h1_modalidades', 'GE vs xgboost')          |  33.8387 |     56.1864 | 0      |                   29 | sí          |
| ('h1_modalidades', 'GE vs mes_anterior')     |  33.8387 |     31.2706 | 0      |                    6 | no          |
| ('h1_modalidades', 'GE_ens vs GC1_ens')      |  32.9072 |     33.3036 | 0.1338 |                   25 | no          |
| ('h1_modalidades', 'GE_ens vs GC2_ens')      |  32.9072 |     32.7742 | 0.3285 |                   20 | no          |
| ('h1_modalidades', 'GE_ens vs mes_anterior') |  32.9072 |     31.2706 | 0      |                   11 | no          |
| ('h3_base', 'GE vs GC1')                     |  48.1604 |     52.6889 | 0      |                   33 | sí          |
| ('h3_base', 'GE vs GC2')                     |  48.1604 |     48.1997 | 0.9001 |                   20 | no          |
| ('h3_base', 'GE vs xgboost')                 |  48.1604 |     78.4574 | 0      |                   35 | sí          |
| ('h3_base', 'GE vs mes_anterior')            |  48.1604 |     45.6625 | 0      |                    9 | no          |
| ('h3_base', 'GE_ens vs GC1_ens')             |  47.6822 |     51.7554 | 0      |                   30 | sí          |
| ('h3_base', 'GE_ens vs GC2_ens')             |  47.6822 |     47.7083 | 0.7243 |                   18 | no          |
| ('h3_base', 'GE_ens vs mes_anterior')        |  47.6822 |     45.6625 | 0.0004 |                   13 | no          |
| ('h3_modalidades', 'GE vs GC1')              |  50.2435 |     49.9155 | 0.5945 |                   21 | no          |
| ('h3_modalidades', 'GE vs GC2')              |  50.2435 |     49.6273 | 0      |                   11 | no          |
| ('h3_modalidades', 'GE vs xgboost')          |  50.2435 |     79.0291 | 0      |                   34 | sí          |
| ('h3_modalidades', 'GE vs mes_anterior')     |  50.2435 |     45.6625 | 0      |                    6 | no          |
| ('h3_modalidades', 'GE_ens vs GC1_ens')      |  49.5763 |     49.2914 | 0.8624 |                   21 | no          |
| ('h3_modalidades', 'GE_ens vs GC2_ens')      |  49.5763 |     48.897  | 0      |                   10 | no          |
| ('h3_modalidades', 'GE_ens vs mes_anterior') |  49.5763 |     45.6625 | 0      |                    8 | no          |
