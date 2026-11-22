# v4 (candidato 3b): confirmación de la selección multianual con 5 semillas

Generado por `GNN_EXPERIMENTO=h1_v4_validacion_multianual python -m src.confirmar_seleccion`. MAE en denuncias en el año de validación de la ventana w, que ni A ni B usaron para elegir. A: elegida con el año de validación de w − 1. B: elegida con el promedio de los años de validación de las ventanas 1 … w − 1. Grilla de la v2 (`results/fichas/ajuste_hiperparametros.csv`, salida residual). La prueba no intervino. Nota. Elaboración propia.

## Configuraciones (oculto/lr/dropout/L)

|              | A                | B               |
|:-------------|:-----------------|:----------------|
| ('GC1', '3') | 32/0.0003/0.1/12 | 64/0.0001/0.3/6 |
| ('GC1', '4') | 64/0.003/0.3/12  | 64/0.0001/0.1/6 |
| ('GC2', '3') | 32/0.003/0.3/12  | 32/0.003/0.1/12 |
| ('GC2', '4') | 64/0.003/0.1/6   | 32/0.003/0.1/12 |
| ('GE', '3')  | 32/0.003/0.3/12  | 32/0.003/0.1/12 |
| ('GE', '4')  | 64/0.003/0.1/6   | 32/0.003/0.1/12 |

## MAE fuera de muestra (media entre semillas)

|              |   A (5 sem.) |   B (5 sem.) |   B − A |   sd A |   sd B |   A (sem. 1–4) |   B (sem. 1–4) |   B − A (sem. 1–4) |
|:-------------|-------------:|-------------:|--------:|-------:|-------:|---------------:|---------------:|-------------------:|
| ('GC1', '3') |       38.621 |       38.813 |   0.192 |  0.214 |  0.614 |         38.632 |         38.915 |              0.283 |
| ('GC1', '4') |       25.441 |       26.191 |   0.75  |  0.161 |  0.268 |         25.456 |         26.138 |              0.682 |
| ('GC2', '3') |       38.456 |       38.433 |  -0.023 |  0.09  |  0.084 |         38.469 |         38.444 |             -0.025 |
| ('GC2', '4') |       26.674 |       26.065 |  -0.609 |  0.288 |  0.231 |         26.7   |         25.997 |             -0.703 |
| ('GE', '3')  |       38.476 |       38.445 |  -0.031 |  0.108 |  0.096 |         38.489 |         38.459 |             -0.031 |
| ('GE', '4')  |       26.729 |       26.043 |  -0.687 |  0.221 |  0.233 |         26.769 |         25.973 |             -0.796 |

## Decisión (regla fijada antes de correr, sobre el GE)

- 5 semillas: B − A medio en w = 3 -0.030, en w = 4 -0.687; 9 de 10 pares a favor de B (mínimo 6) → cumple.
- sin la semilla 0: B − A medio en w = 3 -0.031, en w = 4 -0.796; 7 de 8 pares a favor de B (mínimo 5) → cumple.

**Se adopta la selección multianual.**

Control: la semilla 0 reproduce el MAE de la grilla de la v2 con una diferencia máxima de 0.0000 (la grilla se corrió en otra PC).
