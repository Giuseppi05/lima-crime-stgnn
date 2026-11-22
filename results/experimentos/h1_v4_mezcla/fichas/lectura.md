# v4 (candidato 2): mezcla con la persistencia — lectura

Tablas completas en `mezcla.md` (generado por `src.mezcla`). **Decisión: no se adopta.**

## Hipótesis y criterio (fijados antes de calcular)
- Si el modelo acierta la dirección del cambio pero exagera su tamaño, encoger el cambio predicho hacia cero
  (ŷ = y(t − 1) + α·(ŷ_modelo − y(t − 1)), α < 1) debería bajar el MAE.
- Se refuta si GE_mix no baja el MAE del GE en la validación cruzada que deja un mes fuera en al menos 2 de las 4
  ventanas, o si α* < 1 no es consistente (en ≥ 3 de 4).
- Modelos: `h1_base` reentrenado en esta PC (no se commitea). Control: la prueba repredicha coincide con la guardada
  (máx. dif. 5,0e-5, el redondeo del CSV) y el MAE de validación coincide con `corridas_neuronales.csv`.

## Validación (decide). MAE en denuncias, media de 5 semillas
| ventana | α* GE | rango de α en la validación cruzada | GE solo | GE_mix (validación cruzada) | mes anterior |
|---|---|---|---|---|---|
| 1 | 0,85 | 0,45–1,00 | 25,468 | 25,800 | 25,733 |
| 2 | 0,80 | 0,00–1,00 | 33,340 | 33,636 | 33,436 |
| 3 | 0,95 | 0,35–1,00 | 37,754 | 38,925 | 38,977 |
| 4 | 1,00 | 0,80–1,00 | 26,213 | 26,348 | 27,215 |
| P | 1,00 | 1,00–1,00 | 37,978 | 37,978 | 39,078 |

- GE_mix no mejora al GE en ninguna de las 4 ventanas. Con los 12 meses, α* < 1 en 3 de 4 ventanas, pero la mejora
  dentro de la muestra es de 0,006–0,012 y desaparece fuera de ella. En validación cruzada la mezcla es peor que el GE
  en las cuatro (+0,13 a +1,17).
- El α no es estable: según qué mes se deje fuera, va de 0 a 1 en la ventana 2 y de 0,35 a 1 en la ventana 3. Un
  solo mes cambia la elección. No hay un factor de encogimiento que se sostenga mes a mes.
- GC₂ y GC₁ muestran lo mismo: la mezcla no les gana en validación cruzada en ninguna ventana (`mezcla_validacion.csv`).
- Sesgo declarado: la validación ya se usó para la parada temprana y los hiperparámetros, así que el modelo se ve mejor
  ahí de lo que es y α* se inclina hacia 1. El sesgo va en contra de la mezcla. Además, la validación cruzada de la
  mezcla se compara con el MAE de validación del modelo, que es optimista. El rechazo es claro, pero no prueba que la
  mezcla no sirva fuera de muestra.

## Prueba (solo se informa, calculada después de fijar la regla)
- Ventanas 1–4: GE 33,347 → 33,046 · GC₂ 33,230 → 32,727 · GC₁ 32,720 → 32,219 · mes anterior 31,271. Ninguna mezcla
  supera a la persistencia.
- Es el tercer cambio que mejora en prueba y no en validación (v3, candidato 1 y este). En validación, los modelos sin
  mezcla ya quedan por debajo de la persistencia en las 4 ventanas. En prueba, la persistencia gana. El problema
  es de traslado de validación a prueba, no de cuánto se encoge el cambio.
- Pruebas complementarias (n = 43): GE_mix no supera a GC₂_mix ni a GC₁_mix. Ambos tienen menor MAE y RMSE, y la
  diferencia es significativa: Wilcoxon, p < 0,0001 y p = 0,007. No cambian la regla principal.

## Frase sugerida (si se reporta como complementario)
"Como análisis complementario, cada modelo neuronal se combinó con la persistencia, ŷ = α·ŷ_modelo + (1 − α)·y_{t−1},
con α elegido por ventana solo con validación. En validación cruzada dentro de la validación, la combinación no mejoró
a ningún modelo en ninguna ventana, y el α elegido fue inestable entre meses (0–1), por lo que no se adoptó."

Nota. Elaboración propia.
