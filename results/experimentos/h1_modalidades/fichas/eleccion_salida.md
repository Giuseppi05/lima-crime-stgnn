# Modelado: elección de la salida de los modelos neuronales

Criterio: menor MAE de validación promedio (mejor configuración de la grilla por modelo y ventana, semilla 0). El conjunto de prueba no intervino.

|              |   directa |   residual |
|:-------------|----------:|-----------:|
| ('GC1', '1') |    29.432 |     25.242 |
| ('GC1', '2') |    50.19  |     32.912 |
| ('GC1', '3') |    38.237 |     35.445 |
| ('GC1', '4') |    29.937 |     24.984 |
| ('GC2', '1') |    33.941 |     25.428 |
| ('GC2', '2') |    69.7   |     32.969 |
| ('GC2', '3') |    51.171 |     37.084 |
| ('GC2', '4') |    46.858 |     25.588 |
| ('GE', '1')  |    32.718 |     25.45  |
| ('GE', '2')  |    68.328 |     32.95  |
| ('GE', '3')  |    50.444 |     36.967 |
| ('GE', '4')  |    46.378 |     25.587 |

Promedio por salida: {'directa': 45.611, 'residual': 30.05}. **Elegida: residual**, aplicada igual a GE, GC₁ y GC₂.

Nota. Elaboración propia.
