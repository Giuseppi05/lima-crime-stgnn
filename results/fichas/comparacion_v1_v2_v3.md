# Evaluación: comparación de las versiones 1, 2 y 3

Iteración de CRISP-DM (retorno de Evaluación a Modelado). Versión 3: la grilla de la v2 y la pérdida Huber ponderada por distrito (nivel medio de entrenamiento × desviación del log), para que el entrenamiento pese los distritos como lo hace el MAE en denuncias. La misma ponderación se aplica a GE, GC₁ y GC₂. Arquitectura, entrada, partición, normalización y protocolo sin cambios. Elección de hiperparámetros solo con validación. Nota. Elaboración propia.

## Métricas globales en prueba (4 ventanas, media de 5 semillas)

| modelo                  |   MAE v1 |   MAE v2 |   MAE v3 |   RMSE v1 |   RMSE v2 |   RMSE v3 |   MAE_sd v2 |   MAE_sd v3 |
|:------------------------|---------:|---------:|---------:|----------:|----------:|----------:|------------:|------------:|
| GE                      |   33.414 |   33.469 |   32.186 |    55.289 |    55.335 |    53.195 |       1.368 |       0.319 |
| GC2                     |   33.176 |   33.23  |   32.193 |    54.686 |    54.737 |    53.193 |       0.963 |       0.337 |
| GC1                     |   32.88  |   32.72  |   35.12  |    54.779 |    54.489 |    58.703 |       0.403 |       1.18  |
| xgboost                 |   56.389 |   57.039 |   57.039 |   100.899 |   102.035 |   102.035 |       0     |       0     |
| mes_anterior            |   31.271 |   31.271 |   31.271 |    51.76  |    51.76  |    51.76  |       0     |       0     |
| promedio_movil_3        |   34.05  |   34.05  |   34.05  |    56.397 |    56.397 |    56.397 |       0     |       0     |
| mismo_mes_anio_anterior |   86.808 |   86.808 |   86.808 |   140.319 |   140.319 |   140.319 |       0     |       0     |

## Pruebas estadísticas (n = 43 distritos)

| comparacion        |   p v2 | a favor de (v2)   |   p v3 | a favor de (v3)   |   distritos GE mejor v3 | GE supera v2   | GE supera v3   |
|:-------------------|-------:|:------------------|-------:|:------------------|------------------------:|:---------------|:---------------|
| GE vs GC1          |  0.021 | GC1               | 0      | GE                |                      31 | no             | sí             |
| GE vs GC2          |  0.009 | GC2               | 0.0398 | GE                |                      13 | no             | no             |
| GE vs xgboost      |  0     | GE                | 0      | GE                |                      32 | sí             | sí             |
| GE vs mes_anterior |  0     | mes_anterior      | 0      | mes_anterior      |                       7 | no             | no             |

## MAE por ventana en prueba (v3)

|   ventana |    GC1 |    GC2 |     GE |   mes_anterior |
|----------:|-------:|-------:|-------:|---------------:|
|         1 | 45.614 | 37.146 | 37.11  |         33.436 |
|         2 | 39.537 | 38.76  | 38.75  |         38.977 |
|         3 | 29.547 | 27.236 | 27.245 |         27.215 |
|         4 | 25.747 | 25.603 | 25.611 |         25.432 |

## Validación frente a prueba

Media del MAE de validación de las 20 corridas finales (4 ventanas × 5 semillas), en denuncias, y MAE de prueba.

| modelo   |   MAE validación v2 |   MAE validación v3 |   MAE prueba v2 |   MAE prueba v3 |
|:---------|--------------------:|--------------------:|----------------:|----------------:|
| GC1      |              30.407 |              30.122 |          32.72  |          35.12  |
| GC2      |              30.75  |              30.854 |          33.23  |          32.193 |
| GE       |              30.681 |              30.846 |          33.469 |          32.186 |

## Lectura

- En prueba, la v3 baja el MAE del GE de 33,469 a 32,186 y su desviación entre semillas de 1,368 a 0,319. GE y GC₂ quedan prácticamente iguales (diferencia media −0,007). La diferencia es significativa (p = 0,040), pero el GE no la supera según la regla del estudio porque su RMSE es mayor.
- El GE supera ahora al GC₁ (p < 0,001), pero es porque el GC₁ empeora con la ponderación (de 32,720 a 35,120, sobre todo en la ventana 1). No es una ganancia del grafo.
- El GE sigue sin superar al mes anterior (31,271; p < 0,001; el GE gana solo en 7 de 43 distritos). La brecha baja de 2,2 a 0,9 denuncias por distrito y mes. Casi toda la pérdida restante está en la ventana 1.
- **En validación la v3 no mejora al GE ni al GC₂: su MAE sube de 30,681 a 30,846 y de 30,750 a 30,854.** Con el GC₁ ocurre lo contrario: mejora en validación (30,407 → 30,122) y empeora en prueba. Elegir la v3 por su resultado en prueba sería ajustar con el conjunto de prueba, cosa que el protocolo prohíbe. Según la validación, la v3 no se justifica como configuración del GE.
- Atención: la autoatención no cambia (GE 0,222, GC₂ 0,209). La prueba de fidelidad deja de ser significativa (p = 0,261; 10 de 20 corridas). Casos adversos: quitar aristas o mover coordenadas sigue sin efecto (≤ 0,03 %) y los meses faltantes suben el MAE un 2,93 %.

Corrección de registro: la fase `congelar` de pandemia sobrescribía `eleccion_salida.md` con la tabla de la ventana P. Desde la v3, P se escribe en `eleccion_salida_pandemia.md`. El `results/v2/eleccion_salida.md` guardado tiene solo la tabla de P. La elección de la v2 (residual) consta en el yaml del commit `ca03da1`: directa 44,115 frente a residual 30,288.
