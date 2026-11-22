# Modelado: elección de la salida de los modelos neuronales

Criterio: menor MAE de validación promedio (mejor configuración de la grilla por modelo y ventana, semilla 0). El conjunto de prueba no intervino.

|              |   directa |   residual |
|:-------------|----------:|-----------:|
| ('GC1', '1') |    33.98  |     31.183 |
| ('GC1', '2') |    82.268 |     47.451 |
| ('GC1', '3') |    40.935 |     43.654 |
| ('GC1', '4') |    41.18  |     37.609 |
| ('GC2', '1') |    36.375 |     34.051 |
| ('GC2', '2') |    88.926 |     49.519 |
| ('GC2', '3') |    49.901 |     47.511 |
| ('GC2', '4') |    46.213 |     39.84  |
| ('GE', '1')  |    36.406 |     34.097 |
| ('GE', '2')  |    89.803 |     49.524 |
| ('GE', '3')  |    49.382 |     47.57  |
| ('GE', '4')  |    45.615 |     39.83  |

Promedio por salida: {'directa': 53.415, 'residual': 41.82}. **Elegida: residual**, aplicada igual a GE, GC₁ y GC₂.

Nota. Elaboración propia.
