# Modelado: elección de la salida de los modelos neuronales

Criterio: menor MAE de validación promedio (mejor configuración de la grilla por modelo y ventana, semilla 0). El conjunto de prueba no intervino.

|              |   directa |   residual |
|:-------------|----------:|-----------:|
| ('GC1', '1') |    27.399 |     24.503 |
| ('GC1', '2') |    47.701 |     32.976 |
| ('GC1', '3') |    36.794 |     35.68  |
| ('GC1', '4') |    28.415 |     25.335 |
| ('GC2', '1') |    35.492 |     25.467 |
| ('GC2', '2') |    64.46  |     33.114 |
| ('GC2', '3') |    50.023 |     38.341 |
| ('GC2', '4') |    41.533 |     25.91  |
| ('GE', '1')  |    35.204 |     25.477 |
| ('GE', '2')  |    63.793 |     33.095 |
| ('GE', '3')  |    50.092 |     38.338 |
| ('GE', '4')  |    41.637 |     25.91  |

Promedio por salida: {'directa': 43.545, 'residual': 30.346}. **Elegida: residual**, aplicada igual a GE, GC₁ y GC₂.

Nota. Elaboración propia.
