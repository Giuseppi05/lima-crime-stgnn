# Modelado: elección de la salida de los modelos neuronales

Criterio: menor MAE de validación promedio (mejor configuración de la grilla por modelo y ventana, semilla 0). El conjunto de prueba no intervino.

|              |   directa |   residual |
|:-------------|----------:|-----------:|
| ('GC1', '1') |    29.749 |     25.228 |
| ('GC1', '2') |    49.439 |     33.009 |
| ('GC1', '3') |    36.707 |     38.402 |
| ('GC1', '4') |    29.197 |     25.507 |
| ('GC2', '1') |    34.893 |     25.449 |
| ('GC2', '2') |    64.039 |     33.223 |
| ('GC2', '3') |    50.756 |     38.388 |
| ('GC2', '4') |    45.766 |     26.334 |
| ('GE', '1')  |    34.863 |     25.458 |
| ('GE', '2')  |    64.025 |     33.195 |
| ('GE', '3')  |    51.075 |     38.393 |
| ('GE', '4')  |    42.372 |     26.106 |

Promedio por salida: {'directa': 44.407, 'residual': 30.724}. **Elegida: residual**, aplicada igual a GE, GC₁ y GC₂.

Nota. Elaboración propia.
