# v4 (candidato 3b): elegir los hiperparámetros con varios años de validación — propuesta

Estado: **sin entrenar, sin commit, en espera de la aprobación de Josué.** Preparado el 21 nov. 2026 a pedido de gnn-e0.
La verificación previa salió solo de `results/fichas/ajuste_hiperparametros.csv` (v2, commit `ca03da1`, sin cambios
hasta HEAD; su argmin reproduce los 15 hiperparámetros de `h1_base`). La prueba no se tocó. Script:
`verificacion_previa.py` (`PYTHONPATH=. python results/experimentos/h1_v4_validacion_multianual/verificacion_previa.py <salida.csv>`).

## 1. Verificación previa (costo cero, solo validación, semilla 0, salida residual, 48 configuraciones)
Cada procedimiento elige una configuración sin usar el año de validación de la ventana w, y se mide en ese año:
- **A**: elige con un solo año, el de la ventana w − 1.
- **B**: elige con el promedio de los años de validación de todas las ventanas anteriores a w.
- **C**: elige con el mismo año w. Es lo que hace hoy el protocolo, así que es optimista y sirve solo para medir el
  optimismo.

MAE en denuncias en el año de validación de la ventana w. La columna "rango" es el puesto de la configuración elegida
entre las 48 en ese año.

| modelo | w | A | B | B − A | C (mismo año) | mediana de las 48 | rango A / B | Spearman año w−1 vs w | mes anterior |
|---|---|---|---|---|---|---|---|---|---|
| GE | 2 | 34,235 | 34,235 | 0 | 33,180 | 34,086 | 25 / 25 | −0,24 | 33,436 |
| GE | 3 | 38,422 | 38,393 | −0,029 | 37,074 | 38,482 | 7 / 5 | 0,55 | 38,977 |
| GE | 4 | 26,569 | 26,319 | −0,250 | 25,917 | 26,556 | 26 / 18 | 0,19 | 27,215 |
| GC₂ | 2 | 34,227 | 34,227 | 0 | 33,204 | 34,077 | 25 / 25 | −0,20 | 33,436 |
| GC₂ | 3 | 38,402 | 38,388 | −0,014 | 37,117 | 38,478 | 7 / 5 | 0,52 | 38,977 |
| GC₂ | 4 | 26,568 | 26,334 | −0,234 | 25,918 | 26,565 | 25 / 18 | 0,19 | 27,215 |
| GC₁ | 2 | 33,263 | 33,263 | 0 | 32,965 | 33,292 | 20 / 20 | 0,18 | 33,436 |
| GC₁ | 3 | 38,579 | 38,408 | −0,171 | 36,614 | 38,477 | 33 / 9 | −0,44 | 38,977 |
| GC₁ | 4 | 25,381 | 26,406 | **+1,025** | 25,327 | 25,789 | 2 / 45 | −0,32 | 27,215 |

Sensibilidad: promediar el MAE relativo a la persistencia de cada año, en lugar del MAE crudo, elige lo mismo salvo
en GC₁ w = 3 (38,402 en vez de 38,408). No cambia nada.

**Lectura.**
1. **Elegir con un año equivale casi a elegir al azar.** El orden de las 48 configuraciones apenas se repite de un año
   al siguiente (Spearman entre −0,44 y 0,55). La configuración elegida con un año cae, al año siguiente, cerca de la
   mediana de las 48: GE en los puestos 25, 7 y 26, con MAE 34,235 / 38,422 / 26,569 frente a medianas de 34,086 /
   38,482 / 26,556.
2. **Esto explica buena parte de la brecha entre validación y prueba.** Elegir con el mismo año (C, lo de hoy) da un
   MAE entre 0,65 y 1,35 menor que elegir fuera de ese año (A), en el GE. Es optimismo del ganador: el mínimo de 48
   valores ruidosos queda por debajo de lo que la configuración vale en realidad. Ese optimismo es del mismo orden que
   la ventaja que los modelos sacan a la persistencia en validación y pierden en prueba.
3. **B frente a A:**
   - GE y GC₂: B es algo mejor en w = 3 y w = 4 (GE −0,029 y −0,250), pero es menos que el ruido entre semillas. La
     desviación estándar del MAE de validación entre las 5 semillas de `h1_base` local es 1,04 en la ventana 3 y 0,26
     en la ventana 4 para el GE.
   - GC₁: B es mucho peor en w = 4 (+1,025, puesto 45 de 48).
   - **Con 2 comparaciones por modelo y una sola semilla, la verificación no es concluyente.** Es coherente con la
     hipótesis en GE y GC₂ y la contradice en GC₁.
4. **Advertencia sobre el nivel de las cifras.** Los MAE del CSV ya incluyen la parada temprana en ese mismo año. El
   nivel es optimista para todos los procedimientos por igual. La comparación entre A y B no queda sesgada, pero sus
   valores no se pueden comparar directamente con la prueba.

## 2. Propuesta para la versión real
**Selección.** Para la ventana w se elige la configuración con menor MAE de validación promedio (semilla 0, salida
residual) sobre los años de validación de las ventanas 1 … w:
- w = 2 → años 1–2; w = 3 → 1–3; w = 4 → 1–4.
- Sin fuga: todos esos años son anteriores a la prueba de w y están dentro de su entrenamiento o de su validación.
- La salida (residual) se mantiene: ya se elige promediando las 4 ventanas.

**Ventana 1:** no tiene años previos comparables. Propongo que se elija como hoy, solo con su año, y declararlo. La
alternativa sería sumar la validación de P (oct-2019 a mar-2020), pero tiene 6 meses, incluye el inicio de la
cuarentena y un modelo entrenado solo hasta 2019-09: mezcla regímenes. **La ventana P tampoco cambia**: es el caso
adverso y conserva su propia elección.

**¿Combinarlo con la regularización del candidato 3?** No. Es un cambio por versión: si se combinan, no se sabría cuál
produjo el efecto. Además, 3b cuesta cero en selección con la grilla existente, mientras que el candidato 3 exige una
grilla nueva. Si 3b se adopta, el candidato 3 se evaluaría después con la selección multianual.

**Costo:**
- La selección sale del CSV existente: cero entrenamientos.
- Código: una clave `seleccion: multianual` (apagada por defecto) en `fase_congelar`, que promedia
  `mae_validacion` sobre las ventanas ≤ w antes del argmin. `h1_base` se reproduce igual.
- Reentrenar solo `--fase final` de las ventanas 1–4: unos 6 min. La ventana 1 da lo mismo que `h1_base`, así que
  bastan las ventanas 2–4.
- P no cambia.

**Configuraciones que elegiría B en la versión real (con los años ≤ w):** [PENDIENTE: se calculan al implementar,
con el mismo CSV].

## 3. Regla de adopción (fijada antes de entrenar)
El MAE de validación de la ventana w favorece a la selección actual, porque eligió con ese año. Tampoco sirve como
regla la verificación del punto 1: su resultado ya se conoce. Propongo una **confirmación con 5 semillas de esa
misma comparación fuera de muestra**, que todavía nadie ha visto:
- Para w = 3 y 4 y los tres modelos, entrenar con las semillas 0–4 la configuración A (elegida con el año w − 1) y la
  B (elegida con los años < w). Se mide el MAE en el año de validación de w, con la parada temprana en ese año, igual
  para las dos.
- Son 2 procedimientos × 2 ventanas × 3 modelos × 5 semillas = 60 corridas, unos 6–7 min. Hoy no hay código que
  entrene una configuración dada en una ventana dada fuera de la grilla: haría falta un pequeño script de apoyo.
- **Se adopta la selección multianual si**, en el GE:
  - el MAE fuera de muestra de B, en la media de las 5 semillas, es menor que el de A en w = 3 **y** en w = 4;
  - **y** la media de esas dos diferencias es negativa, con al menos 6 de los 10 pares (ventana × semilla) a favor de
    B.
- GC₂ y GC₁ se reportan. Si la selección se adopta, se aplica a los tres modelos para no sesgar la comparación,
  aunque al GC₁ le vaya peor.
- **Después de adoptarla**, se corre la versión real (fase final de las ventanas 2–4), se informa la prueba y se
  aplica la regla de superioridad del AVC3 sin cambios.
- **Si no pasa**, se documenta y la selección de hoy se mantiene.

**Una conclusión que vale aunque 3b no se adopte:** el punto 1 muestra que, con esta grilla, elegir los
hiperparámetros con un año es casi ruido. Conviene declararlo en Resultados o Limitaciones. Frase sugerida: "La
configuración elegida con un año de validación quedó, en el año siguiente, cerca de la mediana de las 48 evaluadas
(Spearman entre años de −0,44 a 0,55), lo que indica que la ventaja de los modelos sobre la persistencia en
validación se debe en parte a la selección [PENDIENTE: confirmar con 5 semillas]."

Nota. Elaboración propia.
