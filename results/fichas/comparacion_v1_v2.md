# Evaluación: comparación de la versión 1 y la versión 2

Iteración de CRISP-DM (retorno de Evaluación a Modelado). Versión 1: grilla de partida (lr 1e-3 y 3e-3), tag git `v1-resultados`. Versión 2: la misma grilla más lr 1e-4 y 3e-4 (48 combinaciones; XGBoost también a 48). Motivo, observado solo en validación: en la versión 1 el mejor MAE de validación llegó en las épocas 1–4. Arquitectura, entrada, partición, normalización y protocolo sin cambios; elección solo con validación. Nota. Elaboración propia.

## Métricas globales en prueba (media de semillas)

| modelo                  |   MAE v1 |   MAE v2 |   RMSE v1 |   RMSE v2 |
|:------------------------|---------:|---------:|----------:|----------:|
| GE                      |   33.414 |   33.469 |    55.289 |    55.335 |
| GC2                     |   33.176 |   33.23  |    54.686 |    54.737 |
| GC1                     |   32.88  |   32.72  |    54.779 |    54.489 |
| xgboost                 |   56.389 |   57.039 |   100.899 |   102.035 |
| mes_anterior            |   31.271 |   31.271 |    51.76  |    51.76  |
| promedio_movil_3        |   34.05  |   34.05  |    56.397 |    56.397 |
| mismo_mes_anio_anterior |   86.808 |   86.808 |   140.319 |   140.319 |

## Pruebas estadísticas

| comparacion        |   p v1 |   p v2 | a favor de (v2)   | GE supera v1   | GE supera v2   |
|:-------------------|-------:|-------:|:------------------|:---------------|:---------------|
| GE vs GC1          | 0.0599 |  0.021 | GC1               | no             | no             |
| GE vs GC2          | 0.012  |  0.009 | GC2               | no             | no             |
| GE vs xgboost      | 0      |  0     | GE                | sí             | sí             |
| GE vs mes_anterior | 0      |  0     | mes_anterior      | no             | no             |

## Tasa de aprendizaje en validación (salida residual, 4 ventanas, 3 modelos)

|     lr |   MAE_validacion_min |   MAE_validacion_mediana |   mejor_epoca_mediana |
|-------:|---------------------:|-------------------------:|----------------------:|
| 0.0001 |                25.24 |                    30.02 |                    23 |
| 0.0003 |                25.23 |                    30.02 |                     8 |
| 0.001  |                25.23 |                    30.18 |                     5 |
| 0.003  |                25.3  |                    30.14 |                     4 |

Con tasas más bajas los modelos entrenan más épocas antes de su mejor validación, pero alcanzan el mismo MAE de validación. El límite no lo pone la tasa de aprendizaje, sino la información que el historial de 6–12 meses aporta sobre el mes siguiente.
