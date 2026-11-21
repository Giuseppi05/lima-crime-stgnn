# Modelado: elección de la salida de los modelos neuronales

Criterio: menor MAE de validación promedio (mejor configuración de la grilla por modelo y ventana, semilla 0). El conjunto de prueba no intervino.

|              |   directa |   residual |
|:-------------|----------:|-----------:|
| ('GC1', 'P') |    38.448 |     37.281 |
| ('GC2', 'P') |    37.314 |     37.812 |
| ('GE', 'P')  |    36.976 |     37.821 |

Promedio por salida en P: {'directa': 37.58, 'residual': 37.638}. No decide: **se hereda residual**, elegida con las ventanas 1–4 (`eleccion_salida.md`).

Nota. Elaboración propia.
