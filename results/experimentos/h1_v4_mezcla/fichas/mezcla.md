# v4 (candidato 2): mezcla con la persistencia — validación y decisión

Generado por `GNN_EXPERIMENTO=h1_v4_mezcla python -m src.mezcla`. ŷ_mix = α·ŷ_modelo + (1 − α)·y(t − 1), un α por modelo y ventana (rejilla 0–1, paso 0.05) compartido por las 5 semillas. Modelos de `h1_base` sin reentrenar. MAE en denuncias, media de 5 semillas. Nota. Elaboración propia.

## Validación (decide)

`val_modelo`: MAE de validación del modelo solo. `val_mix`: con el α* elegido en los 12 meses (optimista por construcción, nunca peor que `val_modelo`). `cv_mix`: validación cruzada dejando un mes fuera (el α de cada mes sale de los otros 11): **es la que decide**. `alfa_cv_min/max`: rango de los 12 α de la validación cruzada.

|              |   alfa |   alfa_cv_min |   alfa_cv_max |   val_modelo |   val_mix |   cv_mix |   val_mes_anterior | mix_mejor_cv   |
|:-------------|-------:|--------------:|--------------:|-------------:|----------:|---------:|-------------------:|:---------------|
| ('GE', '1')  |   0.85 |          0.45 |          1    |       25.468 |    25.456 |   25.8   |             25.733 | False          |
| ('GC2', '1') |   0.85 |          0.5  |          1    |       25.456 |    25.443 |   25.781 |             25.733 | False          |
| ('GC1', '1') |   0.8  |          0.65 |          1    |       25.274 |    25.253 |   25.373 |             25.733 | False          |
| ('GE', '2')  |   0.8  |          0    |          1    |       33.34  |    33.334 |   33.636 |             33.436 | False          |
| ('GC2', '2') |   0.75 |          0    |          1    |       33.377 |    33.363 |   33.69  |             33.436 | False          |
| ('GC1', '2') |   0.65 |          0.35 |          0.85 |       33.346 |    33.279 |   33.461 |             33.436 | False          |
| ('GE', '3')  |   0.95 |          0.35 |          1    |       37.754 |    37.748 |   38.925 |             38.977 | False          |
| ('GC2', '3') |   0.85 |          0.35 |          1    |       37.952 |    37.92  |   39.192 |             38.977 | False          |
| ('GC1', '3') |   0.8  |          0.55 |          1    |       37.618 |    37.531 |   38.198 |             38.977 | False          |
| ('GE', '4')  |   1    |          0.8  |          1    |       26.213 |    26.213 |   26.348 |             27.215 | False          |
| ('GC2', '4') |   1    |          0.85 |          1    |       26.217 |    26.217 |   26.318 |             27.215 | False          |
| ('GC1', '4') |   1    |          0.8  |          1    |       25.39  |    25.39  |   25.609 |             27.215 | False          |
| ('GE', 'P')  |   1    |          1    |          1    |       37.978 |    37.978 |   37.978 |             39.078 | False          |
| ('GC2', 'P') |   1    |          1    |          1    |       37.987 |    37.987 |   37.987 |             39.078 | False          |
| ('GC1', 'P') |   0.85 |          0.75 |          1    |       37.822 |    37.747 |   37.972 |             39.078 | False          |

**Decisión.** GE_mix < GE en validación cruzada en 0 de 4 ventanas; α* < 1 en 3 de 4. Regla fijada antes de calcular (≥ 2 de 4, y α* < 1 consistente = en ≥ 3 de 4): **no se adopta**.

Sesgo declarado: las predicciones de validación vienen de modelos cuya parada temprana y cuyos hiperparámetros se eligieron con esa misma validación, así que el modelo se ve en ella mejor de lo que es y α* se inclina hacia 1. El sesgo va en contra de adoptar la mezcla: si aun así α* < 1 ayuda, el resultado es más sólido.

Control: la prueba repredicha con los modelos cargados coincide con la guardada (máx. dif. 5.0e-05), y el MAE de validación coincide con `corridas_neuronales.csv`.

## Prueba (solo se informa; calculada después de fijar la regla)

### Ventanas 1–4 (MAE y RMSE globales, media de 5 semillas)

| modelo       |    MAE |   RMSE |
|:-------------|-------:|-------:|
| GE           | 33.347 | 55.02  |
| GE_mix       | 33.046 | 54.55  |
| GC2          | 33.23  | 54.737 |
| GC2_mix      | 32.727 | 53.981 |
| GC1          | 32.72  | 54.489 |
| GC1_mix      | 32.219 | 53.643 |
| mes_anterior | 31.271 | 51.76  |

### Ventana P (pandemia)

| modelo       |    MAE |   RMSE |
|:-------------|-------:|-------:|
| GE           | 29.223 | 52.69  |
| GE_mix       | 29.223 | 52.69  |
| GC2          | 29.193 | 52.661 |
| GC2_mix      | 29.193 | 52.661 |
| GC1          | 32.153 | 57.639 |
| GC1_mix      | 31.002 | 56.148 |
| mes_anterior | 29.208 | 52.905 |

### Pruebas estadísticas complementarias (n = 43, MAE por distrito promediado entre ventanas y semillas)

No reemplazan la regla principal del AVC3 (GE frente a GC₂ y GC₁ sin mezcla).

| comparacion            |   MAE_a |   MAE_b |   RMSE_a |   RMSE_b | prueba   |      p |   p_RMSE_distrito |   distritos_a_mejor | a_supera   |
|:-----------------------|--------:|--------:|---------:|---------:|:---------|-------:|------------------:|--------------------:|:-----------|
| GE_mix vs GC1_mix      | 33.0464 | 32.2188 |  54.5497 |  53.6435 | Wilcoxon | 0.0071 |            0.0054 |                  14 | no         |
| GE_mix vs GC2_mix      | 33.0464 | 32.7268 |  54.5497 |  53.9813 | Wilcoxon | 0      |            0      |                  12 | no         |
| GE_mix vs mes_anterior | 33.0464 | 31.2706 |  54.5497 |  51.7597 | Wilcoxon | 0      |            0      |                   6 | no         |
| GE_mix vs GE           | 33.0464 | 33.3469 |  54.5497 |  55.0197 | Wilcoxon | 0      |            0      |                  38 | sí         |
