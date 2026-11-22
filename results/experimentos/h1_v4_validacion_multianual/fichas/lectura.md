# v4 (candidato 3b): selección de hiperparámetros con varios años de validación — lectura

> Reentrenada en la PC de Giuseppi (2026-11-22): GE MAE 32,139; en la PC de Josué, 32,139. Las 60 corridas pararon
> en la misma época; las predicciones difieren como mucho en 0,005 denuncias. Atención (OE3) y casos adversos
> calculados en esa PC con la corrección de la caché del grafo.

**Decisión: se adopta como v4**, con la regla fijada antes de correr (confirmación fuera de muestra, sección 2). La
línea base es `h1_base` (v2) reentrenada en esta PC. MAE en denuncias por distrito y mes. Nota. Elaboración propia.

## 1. Hallazgos sobre la selección (verificación previa, `../verificacion_previa.csv`)
- **El orden de las 48 configuraciones de la grilla casi no se repite de un año de validación al siguiente.**
  Spearman entre años consecutivos de −0,44 a 0,55 en los tres modelos.
- **La configuración elegida con un año queda, al año siguiente, cerca de la mediana de las 48.** En el GE cae en los
  puestos 25, 7 y 26 de 48 (w = 2, 3, 4).
- **Optimismo del ganador.** Elegir con el mismo año (lo que hace el protocolo de la v2) da en el GE un MAE de
  validación entre 0,65 y 1,35 menor que elegir con el año anterior. Es del mismo orden que la ventaja de los modelos
  sobre la persistencia en validación, que en prueba desaparece. Con una grilla de 48 configuraciones y un solo año,
  la selección recoge sobre todo ruido.

## 2. Confirmación con 5 semillas (`confirmacion_seleccion.md`, commit 487a1eb)
- A: elegida con el año de validación de w − 1. B: elegida con el promedio de los años anteriores. Las dos se miden
  en el año de validación de w, que ninguna usó para elegir.

| modelo | w = 3: A → B | w = 4: A → B |
|---|---|---|
| GE | 38,476 → 38,445 (−0,031) | 26,729 → 26,043 (−0,687) |
| GC₂ | 38,456 → 38,433 (−0,023) | 26,674 → 26,065 (−0,609) |
| GC₁ | 38,621 → 38,813 (**+0,192**) | 25,441 → 26,191 (**+0,750**) |

- **Regla, en el GE:**
  - Con 5 semillas, B − A = −0,030 y −0,687, con 9 de 10 pares a favor de B.
  - Sin la semilla 0 (ya vista), −0,031 y −0,796, con 7 de 8 pares.
  - Cumple las dos condiciones: **se adopta**.
- La ganancia en w = 3 es mínima. La decisión se apoya sobre todo en w = 4.
- **Con B, el GC₁ empeora en las dos ventanas.** La selección se aplica igual a los tres modelos para no sesgar la
  comparación.

## 3. Versión real: para la ventana w, configuración con el menor MAE de validación promedio de las ventanas 1 … w
- La ventana 1 (sin años previos) y la P conservan la elección de la v2. Sus corridas salieron idénticas a las de
  `h1_base` local.
- La salida sigue siendo residual. Cambian 3 configuraciones por modelo, en las ventanas 2–4
  (`configs/experimentos/h1_v4_validacion_multianual.yaml`).
  - **GE y GC₂:** en las ventanas 2 y 3 quedan iguales (d 32, lr 3e-3, dropout 0,1, L 12). En la ventana 4 el GE
    usa d 16 y el GC₂ d 32.
  - **Parámetros del GE:** en la ventana 4 pasa de 34 433 (d = 64) a 2 465.
- **Código:** `seleccion: multianual` en `fase_congelar` (apagada por defecto). La grilla es la de la v2 (copia de
  `results/fichas/ajuste_hiperparametros.csv`): no se entrenó ninguna grilla nueva.

### Validación (MAE del año de validación de cada ventana, media de 5 semillas)
| modelo | versión | V1 | V2 | V3 | V4 | media | sd entre semillas (media de las 4 ventanas) |
|---|---|---|---|---|---|---|---|
| GE | v2 local | 25,468 | 33,340 | 37,754 | 26,213 | 30,694 | 0,438 |
| GE | v4 (3b) | 25,468 | 33,348 | 38,445 | 26,062 | 30,831 | 0,182 |
| GC₂ | v2 local | 25,456 | 33,377 | 37,952 | 26,217 | 30,750 | 0,372 |
| GC₂ | v4 (3b) | 25,456 | 33,388 | 38,433 | 26,065 | 30,836 | 0,185 |
| GC₁ | v2 local | 25,274 | 33,346 | 37,618 | 25,390 | 30,407 | 0,420 |
| GC₁ | v4 (3b) | 25,274 | 35,249 | 38,821 | 25,583 | 31,232 | 0,680 |

- Este MAE de validación empeora, y era de esperar: la v2 eligió justamente con ese año (optimismo del ganador,
  sección 1). Por eso no decide; decide la confirmación fuera de muestra (sección 2). Se declaró en la propuesta antes
  de correr.
- La dispersión entre semillas del GE y el GC₂ baja a menos de la mitad. Las configuraciones elegidas con varios años
  son más estables.

### Prueba (se informa después de decidir). Ventanas 1–4, media ± sd entre las 5 semillas
| modelo | versión | MAE | RMSE | R² | MASE |
|---|---|---|---|---|---|
| GE | v2 local | 33,347 ± 1,145 | 55,020 ± 1,992 | 0,957 ± 0,003 | 1,063 ± 0,037 |
| GE | v4 (3b) | **32,139 ± 0,213** | **53,051 ± 0,385** | 0,960 ± 0,001 | 1,024 ± 0,007 |
| GC₂ | v2 local | 33,230 ± 0,963 | 54,737 ± 1,617 | 0,958 ± 0,003 | 1,059 ± 0,031 |
| GC₂ | v4 (3b) | 32,162 ± 0,207 | 53,064 ± 0,360 | 0,960 ± 0,001 | 1,025 ± 0,007 |
| GC₁ | v2 local | 32,720 ± 0,403 | 54,489 ± 0,696 | 0,958 ± 0,001 | 1,043 ± 0,013 |
| GC₁ | v4 (3b) | 32,566 ± 0,174 | 53,889 ± 0,340 | 0,959 ± 0,001 | 1,038 ± 0,006 |
| Mes anterior | — | 31,271 | 51,760 | 0,962 | 0,997 |
| XGBoost | — | 57,039 | 102,035 | 0,854 | 1,819 |

- **MAE de prueba por ventana, GE (v2 local → v4):**
  - V1 37,229 → 37,229 (sin cambio).
  - V2 38,681 → 38,638.
  - V3 31,855 → 27,250.
  - V4 25,593 → 25,413.
- **Frente al mes anterior** (33,436 / 38,977 / 27,215 / 25,432): el GE v4 lo supera en las ventanas 2 y 4, queda
  0,035 por encima en la 3 y pierde por mucho en la 1. La ventana 1 no cambia porque no tiene años previos para elegir. Ningún modelo
  supera al mes anterior en el global.
- **Ventana P:** idéntica a la v2 (GE 29,223; GC₂ 29,193; GC₁ 32,153).

### Pruebas estadísticas (n = 43 distritos; MAE por distrito promediado entre ventanas y semillas)
| comparación | v2 local: MAE GE / rival · p | v4: MAE GE / rival · p | ¿GE supera en v4? |
|---|---|---|---|
| GE vs GC₁ | 33,347 / 32,720 · 0,046 (gana GC₁) | 32,139 / 32,566 · 0,341 | no (MAE y RMSE menores, pero p > 0,05) |
| GE vs GC₂ | 33,347 / 33,230 · 0,134 | 32,139 / 32,162 · **0,019** | **sí, por la regla** |
| GE vs mes anterior | 33,347 / 31,271 · < 0,001 | 32,139 / 31,271 · < 0,001 | no (gana el mes anterior) |
| GE_ens vs GC₂_ens (extra) | 32,655 / 32,484 · < 0,001 | 32,047 / 32,052 · 0,611 | no |

**Cómo leer el "GE supera a GC₂":**
- **Viene de que mejoran los dos, no de que empeore el GC₂.** En prueba, el GE baja 1,208 (33,347 → 32,139) y el GC₂
  1,068 (33,230 → 32,162). No se repite el artefacto de la v3.
- **Es una diferencia mínima.**
  - Global: MAE 0,023 y RMSE 0,013.
  - Por distrito: diferencia media −0,023 y mediana −0,004. En 37 de 43 distritos es menor que 0,1 en valor absoluto.
  - La prueba sobre el RMSE por distrito no es significativa (p = 0,359).
  - Con el promedio de semillas desaparece (p = 0,611).
  - En las ventanas 2 y 3 los dos usan la misma configuración, y el GE es un subgrafo del GC₂ con pesos distintos.
- **Conclusión prudente:** cumple la regla del AVC3 al pie de la letra, pero en la práctica el GE y el GC₂ no se
  distinguen. Hay que informarlo así y no como evidencia de que la vialidad aporte.
- **GE frente a GC₁:** el GE tiene ahora MAE y RMSE globales menores. Es porque el GE mejoró (−1,208) más que el GC₁
  (−0,154), no porque el GC₁ empeorara en prueba. La diferencia por distrito no es significativa (p = 0,341), así que
  no lo supera. Ojo: en validación el GC₁ sí empeora con la nueva selección (30,407 → 31,232; la ventana 2 sube a
  35,249 con sd 1,964).

## 4. Para el texto (no se corrigió el código para que calce)
- **Metodología:** "Los hiperparámetros de cada ventana se eligieron con el MAE de validación promedio de los años de
  validación disponibles hasta esa ventana (de la ventana 1 a la w), y no solo con el de la ventana w. La ventana 1,
  sin años previos, y la ventana de pandemia se eligieron con su propio año. El procedimiento se adoptó porque, en una
  comparación fuera de muestra dentro de la validación, generalizó mejor que la selección con un solo año
  [PENDIENTE: decidir si la v4 reemplaza a la v2 en el artículo]."
- **Resultados o Limitaciones:** "Con un solo año de validación, el orden de las configuraciones apenas se repitió
  entre años (ρ de Spearman de −0,44 a 0,55), y la configuración elegida quedó al año siguiente cerca de la mediana
  de las 48 evaluadas. Esto indica que la ventaja de los modelos sobre la persistencia observada en validación se
  debe en parte al procedimiento de selección."
- Si la v4 pasa al artículo, la superioridad del GE sobre el GC₂ debe ir con la salvedad del tamaño de la diferencia
  (0,023 denuncias) y con la prueba complementaria del promedio de semillas (p = 0,611).
- **Pendiente:** `src.atencion` y `src.adversos` (OE3) no se corrieron para la v4.
