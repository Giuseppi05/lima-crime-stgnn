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
}

# Orden previsto de las tablas y figuras de Resultados (incluye las pestañas aún no construidas para que la
# numeración sugerida no cambie al agregarlas).
TABLAS = [
    "datos_cobertura", "datos_validacion_grafos", "datos_solapamiento", "modelado_configuracion",
    "desempeno_global", "desempeno_ventana", "desempeno_semilla", "desempeno_mismo_conjunto",
    "desempeno_pruebas", "desempeno_r2_distrito", "desempeno_r2_distrito_48",
    "interp_temporal", "interp_spearman", "interp_pares", "interp_fidelidad",
    "equidad_resumen", "equidad_prueba", "equidad_composicion",
    "adversos_pandemia", "adversos_perturbaciones",
    "mapa_riesgo",
    "comparar_global", "comparar_pruebas",
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
    return str(7 + FIGURAS.index(clave)) if clave in FIGURAS else ""
