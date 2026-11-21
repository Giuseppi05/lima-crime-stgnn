# Modelado: elección de la salida de los modelos neuronales

Criterio: menor MAE de validación promedio (mejor configuración de la grilla por modelo y ventana, semilla 0). El conjunto de prueba no intervino.

|              |   directa |   residual |
|:-------------|----------:|-----------:|
| ('GC1', '1') |    29.749 |     25.228 |
| ('GC1', '2') |    49.439 |     33.075 |
| ('GC1', '3') |    36.097 |     36.614 |
| ('GC1', '4') |    29.197 |     25.327 |
| ('GC2', '1') |    34.893 |     25.449 |
| ('GC2', '2') |    64.039 |     33.204 |
| ('GC2', '3') |    50.448 |     37.117 |
| ('GC2', '4') |    43.818 |     26.04  |
| ('GE', '1')  |    34.863 |     25.458 |
| ('GE', '2')  |    64.025 |     33.18  |
| ('GE', '3')  |    50.436 |     37.074 |
| ('GE', '4')  |    42.372 |     26.021 |

Promedio por salida: {'directa': 44.115, 'residual': 30.316}. **Elegida: residual**, aplicada igual a GE, GC₁ y GC₂.

Nota. Elaboración propia.
