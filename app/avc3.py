"""Lo que el AVC3 promete informar en Resultados: citas cortas (literales de la Metodología) y numeración.

El AVC3 ya usa la TABLA I y la TABLA II y las Fig. 1 a Fig. 6; las tablas de Resultados empiezan en la
TABLA III y las figuras en la Fig. 7. El orden de abajo es el de la sección Resultados
(OE1 → OE2 → OE3 → OE4 → casos adversos → despliegue). El número es solo una sugerencia: se edita en cada
exportación porque depende del orden final del artículo.
"""
from __future__ import annotations

from app.formato import romano

# clave → (sección del AVC3, cita corta literal)
CITAS = {
    "oe2": ("OE2 y 3.1, variables",
            "la variable dependiente fue el desempeño predictivo, medido a través del MAE y el RMSE, ambos "
            "expresados en número de denuncias, junto con el R²"),
    "ficha_metricas": ("3.1, instrumentos",
                       "la ficha de métricas registró el MAE, el RMSE y el R² por modelo, ventana, semilla y distrito"),
    "ventanas_semillas": ("3.1, procedimiento",
                          "todos los modelos fueron evaluados en cuatro ventanas sucesivas de prueba de 12 meses cada "
                          "una, y cada modelo neuronal fue entrenado con cinco semillas aleatorias distintas"),
    "pruebas": ("3.1, procedimiento",
                "Se consideró que el GE superó a un GC cuando obtuvo un MAE y un RMSE menores y la diferencia "
                "resultó significativa"),
    "mismo_conjunto": ("3.2, Evaluación (Tabla II)",
                       "Se verificó que todos los modelos se evaluaran con el mismo conjunto de prueba"),
    "oe4": ("3.1, variables",
            "la equidad algorítmica se evaluó con el MAE de cada distrito dividido entre su promedio de denuncias, "
            "junto con la diferencia entre el mayor y el menor de estos valores, calculada entre distritos y sectores"),
    "sectores": ("3.2, Evaluación",
                 "sectores, definidos como tres grupos de distritos según su volumen de denuncias en el periodo de "
                 "entrenamiento"),
    "anova": ("3.1, procedimiento",
              "las diferencias de error entre distritos se contrastaron mediante análisis de varianza (ANOVA) o "
              "Kruskal-Wallis, con un nivel de significación de 0,05"),
    "versiones": ("3.2, Evaluación",
                  "Si la evaluación revelaba un fallo en los datos o en la configuración, se regresaba a la fase "
                  "correspondiente"),
    # OE1: comprensión y preparación de los datos, modelado
    "comprension": ("3.2, Comprensión de los datos",
                    "Se midió la cobertura frente al panel esperado de 43 distritos por 105 meses y se identificaron "
                    "meses faltantes, registros duplicados, nombres de distrito inconsistentes y valores atípicos"),
    "diccionario": ("3.2, Comprensión de los datos",
                    "El entregable fue la caracterización de las denuncias, compuesta por un diccionario de datos y "
                    "un informe de calidad"),
    "tendencia": ("3.2, Comprensión de los datos",
                  "También se exploraron la tendencia, la estacionalidad y los posibles quiebres de las series, como "
                  "el que llegó a suceder en el estado de emergencia en marzo del 2020"),
    "informe_resultados": ("3.2, Validaciones",
                           "La tabla de cobertura, el mapa y el número de aristas se informan en los resultados"),
    "panel_total": ("3.2, Validaciones",
                    "En el panel se verificó que no hubiera duplicados por distrito y por mes, así como que el total de "
                    "denuncias no se viera alterado antes y después de la agregación"),
    "validaciones_grafos": ("3.2, Validaciones",
                            "se comprobó que todos los centroides quedaran dentro de su polígono, que cada grafo "
                            "estuviera conectado, que ninguna distancia por la red fuera más pequeña que la distancia "
                            "en línea recta entre los mismos centroides"),
    "dos_grafos": ("3.2, Preparación de los datos",
                   "la comparación entre ambos permitió aislar el aporte de la conectividad vial"),
    "modelado": ("3.2, Modelado",
                 "Se verificó que todos usaran la misma partición y la misma variable objetivo, y que el conjunto de "
                 "prueba no interviniera en el ajuste de hiperparámetros"),
    # OE3
    "oe3": ("3.2, Evaluación",
            "Para el OE3 se extrajeron los pesos de atención de la ST-GNN, se agregaron por par de distritos y por "
            "desfase temporal y se contrastaron con la contigüidad y la conectividad vial"),
    "indicio": ("3.2, Evaluación",
                "Estos pesos se interpretaron como indicio de las relaciones que el modelo utiliza, no como "
                "explicación causal"),
    "interp_variables": ("3.1, variables",
                         "la interpretabilidad se analizó a partir de los pesos de atención asignados por el modelo a "
                         "cada par de distritos y a cada mes previo"),
    # casos adversos
    "adversos": ("3.1, procedimiento",
                 "También se evaluó cómo respondieron los modelos ante casos adversos como el periodo de pandemia, la "
                 "eliminación de aristas del grafo, el ruido en las coordenadas y los meses faltantes"),
    "pandemia": ("3.1, validez",
                 "El periodo de pandemia, que modificó el comportamiento habitual de las denuncias, se analizó como "
                 "caso adverso"),
    # despliegue
    "despliegue": ("3.2, Despliegue", "Se elaboró un mapa de riesgo distrital con las predicciones del modelo"),
    "no_operativo": ("3.2, Despliegue",
                     "No se contempló el uso operativo del modelo en una institución, porque se trata de un artefacto "
                     "de investigación"),
    "reproducible": ("3.2, Despliegue", "Se verificó que el mapa pudiera regenerarse a partir del repositorio"),
}

# Orden de las tablas y figuras en la sección Resultados (OE1 → OE2 → OE3 → OE4 → casos adversos → despliegue).
# Las de apoyo (pendientes, comparación de versiones) van al final. Una figura «_repo» (la PNG del repositorio) es
# alternativa de su gráfico y lleva el mismo número.
TABLAS = [
    # OE1: datos, grafos y modelado
    "datos_cobertura", "datos_cobertura_distritos", "datos_calidad", "datos_diccionario", "datos_totales_tabla",
    "datos_grafos", "datos_validacion_grafos", "datos_solapamiento",
    "modelado_particion", "modelado_configuracion", "modelado_xgboost",
    # OE2
    "desempeno_global", "desempeno_ventana", "desempeno_semilla", "desempeno_mismo_conjunto", "desempeno_pruebas",
    "desempeno_r2_distrito", "desempeno_r2_distrito_48",
    # OE3
    "interp_temporal", "interp_spearman", "interp_pares", "interp_fidelidad",
    # OE4
    "equidad_resumen", "equidad_prueba", "equidad_composicion",
    # casos adversos y despliegue
    "adversos_pandemia", "adversos_perturbaciones", "mapa_riesgo",
    # apoyo
    "pendientes", "comparar_global", "comparar_pruebas",
]
FIGURAS = [
    "datos_tendencia", "datos_estacionalidad", "datos_totales", "datos_mapa_grafos",
    "desempeno_ventana", "desempeno_real_predicho", "desempeno_r2_distrito",
    "interp_temporal", "interp_pares",
    "equidad_error_rel", "equidad_sectores",
    "adversos_pandemia", "adversos_perturbaciones",
    "mapa_riesgo",
]


def numero_tabla(clave: str) -> str:
    return romano(3 + TABLAS.index(clave)) if clave in TABLAS else ""


def numero_figura(clave: str) -> str:
    clave = clave.removesuffix("_repo")
    return str(7 + FIGURAS.index(clave)) if clave in FIGURAS else ""
