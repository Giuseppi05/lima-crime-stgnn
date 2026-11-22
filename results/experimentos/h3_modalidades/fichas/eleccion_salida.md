# Modelado: elección de la salida de los modelos neuronales

Criterio: menor MAE de validación promedio (mejor configuración de la grilla por modelo y ventana, semilla 0). El conjunto de prueba no intervino.

|              |   directa |   residual |
|:-------------|----------:|-----------:|
| ('GC1', '1') |    33.347 |     33.162 |
| ('GC1', '2') |    88.697 |     47.822 |
| ('GC1', '3') |    43.234 |     46.33  |
| ('GC1', '4') |    42.322 |     37.207 |
| ('GC2', '1') |    36.408 |     33.916 |
| ('GC2', '2') |    92.764 |     48.695 |
| ('GC2', '3') |    51.542 |     46.216 |
| ('GC2', '4') |    47.082 |     39.062 |
| ('GE', '1')  |    36.425 |     33.988 |
| ('GE', '2')  |    94.584 |     48.688 |
| ('GE', '3')  |    51.88  |     46.084 |
| ('GE', '4')  |    46.721 |     39.085 |

Promedio por salida: {'directa': 55.417, 'residual': 41.688}. **Elegida: residual**, aplicada igual a GE, GC₁ y GC₂.

Nota. Elaboración propia.
