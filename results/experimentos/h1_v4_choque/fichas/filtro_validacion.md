# v4 (candidato 1): choque común de la ciudad como entrada — filtro de validación

**Decisión: no se adopta y no se corre la grilla.** El GE mejora en validación en 1 de 4 ventanas, y la regla
acordada antes de correr pedía al menos 2.

## Qué se probó
- Hipótesis: parte del cambio mensual es un choque común a toda la ciudad (7–26 % de la varianza de Δlog,
  `src/diagnostico.py`), y un grafo entre distritos no lo capta. Si se da la media de la ciudad como entrada, los tres
  modelos podrían anticipar parte de ese componente.
- Rasgo (clave `choque_comun`, apagada por defecto): c_s = media, sobre los distritos válidos del mes s, del objetivo
  transformado z_{s,n} = (log1p y_{s,n} − media_n) / desv_n, con la media y la desviación de entrenamiento de cada
  ventana. Se repite en los 43 nodos como 5.º canal: X ∈ ℝ^{T×N×5} → ventana de entrada ∈ ℝ^{B×L×N×5} (meses
  t − L … t − 1 para el objetivo t). Entra igual a GE, GC₂ y GC₁. XGBoost y las referencias no cambian.
- Sin fuga: `tests/test_choque_comun.py` comprueba que cambiar las denuncias de t en adelante no altera la ventana de
  entrada de t (L = 6 y 12).
- Parámetros (5 frente a 4 rasgos): d = 16 → 2 497 (antes 2 465), GC₁ 2 289 (2 273) · d = 32 → 9 089 (9 025),
  GC₁ 8 673 (8 641) · d = 64 → 34 561 (34 433), GC₁ 33 729 (33 665).
- Filtro: hiperparámetros de la v2 (los de `h1_base`), solo `--fase final`, ventanas 1–4, 5 semillas, sin la
  ventana P. Línea base: `h1_base` reentrenado en esta misma PC (GE validación 30,694; no se commitea).
- Verificación previa (numpy, solo con entrenamiento y validación): el choque común de t − 1 casi no anticipa el de t.
  La autocorrelación a 1 mes es −0,155 (entrenamiento de la ventana 4, sin pandemia). Al agregarlo a una regresión de
  Δlog por distrito, el R² de validación sube entre 0,001 y 0,032 en las ventanas 1–4 y baja en P. Ya anticipaba un
  efecto pequeño.

## Validación (decide). MAE en denuncias, media de 5 semillas
| modelo | ventana | h1_base local | v4 choque | diferencia | semillas que mejoran |
|---|---|---|---|---|---|
| GE | 1 | 25,468 | 25,451 | −0,017 | 4 de 5 |
| GE | 2 | 33,340 | 33,494 | +0,154 | 1 de 5 |
| GE | 3 | 37,754 | 38,559 | +0,804 | 2 de 5 |
| GE | 4 | 26,213 | 26,404 | +0,191 | 2 de 5 |
| GC₂ | 1 | 25,456 | 25,445 | −0,011 | 4 de 5 |
| GC₂ | 2 | 33,377 | 33,513 | +0,136 | 1 de 5 |
| GC₂ | 3 | 37,952 | 38,538 | +0,586 | 2 de 5 |
| GC₂ | 4 | 26,217 | 26,412 | +0,195 | 2 de 5 |
| GC₁ | 1 | 25,274 | 25,345 | +0,071 | 2 de 5 |
| GC₁ | 2 | 33,346 | 33,166 | −0,180 | 3 de 5 |
| GC₁ | 3 | 37,618 | 37,993 | +0,375 | 2 de 5 |
| GC₁ | 4 | 25,390 | 25,520 | +0,130 | 2 de 5 |

Media de las 20 corridas: GE 30,694 → 30,977 (+0,283) · GC₂ 30,750 → 30,977 (+0,227) · GC₁ 30,407 → 30,506 (+0,099).

## Prueba (solo se informa, no decide)
GE 33,339 → 32,581 · GC₂ 33,223 → 32,499 · GC₁ 32,713 → 32,607 (`h1_base` local frente a v4).

## Lectura
- El rasgo empeora la validación de los tres modelos. La única mejora del GE (ventana 1, −0,017) es ruido frente a la
  dispersión entre semillas.
- En prueba los tres bajan entre 0,1 y 0,8. Es el mismo patrón de la v3: mejora en prueba y empeora en validación. Con
  el protocolo no se adopta.
- En validación de las ventanas 2 y 3, la media de la ciudad queda ≈ 1 desviación por encima de la de entrenamiento
  (en la prueba de la ventana 2, 1,3). El modelo extrapola en este rasgo, y la ventana 3 es justo la que más empeora.
- Límite del filtro: los hiperparámetros no se reajustaron para la nueva entrada. Con la regla acordada y la
  verificación previa, la grilla (~2 h) no se justifica.
- Las predicciones de atención (54 MB) no se commitean: se regeneran exactas con
  `GNN_EXPERIMENTO=h1_v4_choque python -m src.entrenar --fase final`.

Nota. Elaboración propia.
