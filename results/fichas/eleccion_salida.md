# Modelado: elección de la salida de los modelos neuronales

Criterio: menor MAE de validación promedio (mejor configuración de la grilla por modelo y ventana, semilla 0). El conjunto de prueba no intervino.

|              |   directa |   residual |
|:-------------|----------:|-----------:|
| ('GC1', 'P') |    40.009 |     37.545 |
| ('GC2', 'P') |    40.111 |     37.994 |
| ('GE', 'P')  |    39.324 |     37.992 |

Promedio por salida: {'directa': 39.815, 'residual': 37.844}. **Elegida: residual**, aplicada igual a GE, GC₁ y GC₂.

Nota. Elaboración propia.
