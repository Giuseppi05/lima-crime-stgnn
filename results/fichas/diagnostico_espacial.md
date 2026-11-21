# Evaluación (complementaria): diagnóstico de dependencia espacial

Generado por `python -m src.diagnostico`. Se analizan los datos, no un modelo. Matrices de pesos estandarizadas por filas; prueba de Moran por permutación (999 permutaciones, dos colas, α = 0,05). Valor esperado de I sin dependencia: −1/(n−1) = -0.024. Nota. Elaboración propia.

## 1. Autocorrelación espacial mensual (I de Moran)

El nivel mide si los distritos con muchas denuncias están junto a otros con muchas. El cambio mensual mide si, cuando un distrito sube o baja respecto del mes anterior, sus vecinos se mueven igual: es la parte que el 'mes anterior' no predice y la única que un grafo podría aportar.

| grafo            | variable            | periodo           |   I_media |   meses |   meses_significativos |   meses_sig_positivos |
|:-----------------|:--------------------|:------------------|----------:|--------:|-----------------------:|----------------------:|
| geográfico (GC₂) | nivel log1p         | 2018-02 – 2026-09 |     0.679 |     105 |                    105 |                   105 |
| geográfico (GC₂) | nivel log1p         | 2022-01 – 2026-09 |     0.682 |      57 |                     57 |                    57 |
| geográfico (GC₂) | cambio mensual Δlog | 2018-02 – 2026-09 |     0.026 |     104 |                     45 |                    26 |
| geográfico (GC₂) | cambio mensual Δlog | 2022-01 – 2026-09 |    -0.011 |      57 |                     21 |                    10 |
| vial (GE)        | nivel log1p         | 2018-02 – 2026-09 |     0.681 |     105 |                    105 |                   105 |
| vial (GE)        | nivel log1p         | 2022-01 – 2026-09 |     0.686 |      57 |                     57 |                    57 |
| vial (GE)        | cambio mensual Δlog | 2018-02 – 2026-09 |     0.021 |     104 |                     41 |                    23 |
| vial (GE)        | cambio mensual Δlog | 2022-01 – 2026-09 |    -0.014 |      57 |                     20 |                     9 |

## 2. Choque común a toda la ciudad

Proporción de la varianza del cambio mensual (Δlog) explicada por el cambio medio de los 43 distritos ese mes. Un grafo entre distritos no aporta nada sobre ese componente común.

- Todo el periodo: 0.259
- Sin pandemia (excluye 2020-03 – 2021-12): 0.071
- Desde 2022: 0.097

## 3. ¿El cambio de los vecinos ayuda a predecir el cambio propio?

Regresión lineal por mínimos cuadrados del cambio propio del mes t (sin el choque común) sobre el cambio propio y el cambio medio de los vecinos del mes t−1. Se ajusta con el entrenamiento de cada ventana y se mide el MAE en Δlog en su prueba. Este análisis no ajusta ningún modelo del estudio.

|   ventana | grafo            |   coef_propio |   coef_vecinos |   t_vecinos |   MAE_cero |   MAE_propio |   MAE_propio_vecinos |   mejora_por_vecinos_pct |
|----------:|:-----------------|--------------:|---------------:|------------:|-----------:|-------------:|---------------------:|-------------------------:|
|         1 | geográfico (GC₂) |       -0.4037 |         0.1062 |      3.2544 |     0.179  |       0.1701 |               0.171  |                  -0.5051 |
|         1 | vial (GE)        |       -0.4026 |         0.0999 |      3.1513 |     0.179  |       0.1701 |               0.1707 |                  -0.3508 |
|         2 | geográfico (GC₂) |       -0.3942 |         0.1142 |      3.8718 |     0.1707 |       0.1588 |               0.1592 |                  -0.2169 |
|         2 | vial (GE)        |       -0.3931 |         0.1074 |      3.7568 |     0.1707 |       0.1588 |               0.1593 |                  -0.2654 |
|         3 | geográfico (GC₂) |       -0.3888 |         0.0916 |      3.5316 |     0.187  |       0.179  |               0.1786 |                   0.2045 |
|         3 | vial (GE)        |       -0.388  |         0.0876 |      3.4773 |     0.187  |       0.179  |               0.1786 |                   0.2457 |
|         4 | geográfico (GC₂) |       -0.3861 |         0.0817 |      3.4146 |     0.1908 |       0.1782 |               0.1776 |                   0.3225 |
|         4 | vial (GE)        |       -0.3854 |         0.0779 |      3.3467 |     0.1908 |       0.1782 |               0.1775 |                   0.3846 |

Mejora media del MAE al agregar los vecinos: {'geográfico (GC₂)': -0.049, 'vial (GE)': 0.004} %.

## Lectura

El nivel tiene una autocorrelación espacial fuerte y estable: los distritos con muchas denuncias están juntos. Esa estructura es fija y ya está contenida en el historial de cada distrito. El cambio mensual, en cambio, tiene una I de Moran media cercana a cero: hay meses con dependencia significativa, pero su signo alterna (positiva en unos, negativa en otros), de modo que no deja un patrón estable que un modelo pueda aprender. El cambio de los vecinos en t−1 tiene un coeficiente pequeño y significativo dentro del entrenamiento, pero al predecir fuera de muestra su aporte al MAE es despreciable. Es una propiedad de los datos a escala distrito-mes, no de una arquitectura en particular. El Δlog de los distritos de muy bajo volumen es muy ruidoso y pesa en la I de Moran igual que el de los grandes, por lo que los meses significativos deben leerse con cautela.

Figura: `results/figuras/diagnostico_moran.png`
