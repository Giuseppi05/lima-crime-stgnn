"""Pestaña 7. Pendientes del artículo: lo que el AVC3 promete y falta, está parcial o pide una decisión.

Cada estado se comprueba contra los archivos al abrir la pestaña (no es una lista fija), salvo el hallazgo de la
reproducción en otra PC, que no está en un archivo de métricas y se muestra solo como texto con su fuente.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app import datos as D
from app import formato as F
from app.componentes import tabla

FUENTE_REPRO = "reproducción local, 21 nov."
FUENTE_REPRO_V4 = "nota del 22 nov. en lectura.md de la v4"
_REPRO_V2 = ["Al reentrenar la v2 en otra PC, **59 de 60** corridas salieron iguales.",
             "Una sola (**GE, ventana 3, semilla 1**) paró en otra época por ruido de punto flotante entre máquinas.",
             "Con eso, el p de **GE vs GC₂** pasa de **0,009** a **0,134**.",
             "El GE sigue sin superar a nadie, pero esa comparación es frágil y hay que decidir cómo mencionarlo."]
_REPRO_V4 = ["La v4 se entrenó en la PC de Josué y se reentrenó en la PC de la v2: las **60 de 60** corridas pararon en "
             "la misma época.",
             "56 dan el mismo MAE de prueba y las otras 4 difieren en menos de 0,00003; las predicciones cambian como "
             "mucho 0,005 denuncias.",
             "El MAE del GE es **32,139** en las dos PCs y el p de **GE vs GC₂** es **0,019** en las dos. La diferencia "
             "GE–GC₂ es de 0,023 denuncias y con el promedio de semillas no es significativa (p = 0,611)."]


def es_v4(v: D.Version) -> bool:
    return v.clave in ("v4", "exp:h1_v4_validacion_multianual")


def reproduccion(v: D.Version) -> tuple[str, list[str]]:
    return (FUENTE_REPRO_V4, _REPRO_V4) if es_v4(v) else (FUENTE_REPRO, _REPRO_V2)


def _fila(tema, promesa, estado, detalle, fuente):
    return {"Tema": tema, "Promesa o sección del AVC3": promesa, "Estado": estado, "Detalle": detalle,
            "Fuente": fuente}


def items(v: D.Version) -> list[dict]:
    filas = []

    # 1. Jaccard
    geo, vial = D.aristas("geo"), D.aristas("vial")
    vg = D.validacion_grafos_md(v) or ""
    if geo is not None and vial is not None:
        s = D.solapamiento(geo, vial)
        en_ficha = "jaccard" in vg.lower()
        filas.append(_fila("Solapamiento GE–GC₂ (Jaccard)", "3.2 Preparación: comparar las dos vecindades",
                           "Cubierto en la ficha" if en_ficha else "Parcial",
                           f"Calculado en la interfaz: {s['comunes']} aristas comunes, {s['solo_geo']} solo "
                           f"geográficas, {s['solo_vial']} solo viales, Jaccard {F.num(s['jaccard'])}."
                           + ("" if en_ficha else " No figura en `validacion_grafos.md`: llevarlo al texto o a una ficha."),
                           "aristas_geo.csv, aristas_vial.csv"))

    # 2. R² por distrito
    pred = D.predicciones(v)
    if pred is not None:
        r = D.r2_por_distrito(pred, "ventana")
        med = r.groupby("modelo").R2.median()
        neg = r[r.R2 < 0].groupby("modelo").size()
        filas.append(_fila("R² por distrito", "3.1 Instrumentos: ficha de métricas por distrito", "Parcial",
                           f"No existe como archivo; la interfaz lo calcula. Por ventana sale negativo: mediana GE "
                           f"{F.num(med.get('GE'))} (R² < 0 en {neg.get('GE', 0)} de 43) y mes anterior "
                           f"{F.num(med.get('mes_anterior'))} ({neg.get('mes_anterior', 0)} de 43). Decidir la "
                           f"definición y cómo explicarlo frente al R² global.", "predicciones/"))
    else:
        filas.append(_fila("R² por distrito", "3.1 Instrumentos", "Falta",
                           f"No hay predicciones en {v.etiqueta} para calcularlo.", "—"))

    # 3. Fig. 1 y Fig. 2
    faltan = [n for n in ("Fig1", "Fig2") if not list(D.FIGURAS_METODO.glob(f"{n}*"))]
    filas.append(_fila("Fig. 1 y Fig. 2", "Introducción y Trabajos relacionados",
                       "Falta" if faltan else "Cubierto",
                       ("No están en `figuras/`: " + ", ".join(faltan) + ".") if faltan else "Están en `figuras/`.",
                       "figuras/"))

    # 4. Casos adversos de grafo solo en el GE
    c = D.casos_adversos(v)
    if c is not None:
        solo_ge = "modelo" not in c.columns
        filas.append(_fila("Casos adversos de grafo", "3.1 Procedimiento: «cómo respondieron los modelos»",
                           "Parcial" if solo_ge else "Cubierto",
                           "Las perturbaciones (aristas eliminadas, ruido en coordenadas, meses faltantes) se aplicaron "
                           "solo al GE: `casos_adversos.csv` no tiene columna de modelo." if solo_ge else
                           "El archivo distingue modelos.", "casos_adversos.csv, casos_adversos.md"))

    # 5. Caché del grafo
    aviso = D.aviso_cache_grafo(v)
    filas.append(_fila("Error de caché del grafo", "OE3 (fidelidad) y casos adversos de grafo",
                       "En revisión" if aviso else "Corregido (declarado en el yaml)",
                       "Corrección en la rama fix/cache-grafo (commit 68cce0e). La atención y los casos adversos se "
                       "recalcularán como el experimento h1_base; después se agrega `correccion_cache_grafo: true` al "
                       "yaml de esa versión y el aviso desaparece. La pandemia y los meses faltantes no dependen del "
                       "grafo." if aviso else "El yaml de la versión declara la corrección.",
                       "src/modelos.py (_lote_grafo); CONTEXTO_GNN.md"))

    # 6. ANOVA/Kruskal entre distritos
    k = D.equidad_sectores(v)
    if k is not None:
        filas.append(_fila("Prueba «entre distritos»", "3.1 Procedimiento: ANOVA o Kruskal-Wallis",
                           "Redacción", f"El texto dice «entre distritos»; la prueba se hizo entre los 3 sectores "
                           f"({', '.join(sorted(set(k.prueba)))}). Ajustar el texto o agregar la prueba.",
                           "equidad_sectores.csv"))

    # 7. Quiebre de marzo de 2020
    cal = D.calidad_md(v) or ""
    if cal:
        menciona_marzo = "marzo" in cal.lower()
        filas.append(_fila("Quiebre de 2020", "3.2 Comprensión: «quiebres… marzo del 2020»",
                           "Cubierto" if menciona_marzo else "Redacción",
                           "La ficha compara abril de 2020 (1 256) con febrero de 2020 (8 714); no informa marzo. "
                           "Alinear el texto con la cifra o agregar marzo." if not menciona_marzo else
                           "La ficha menciona marzo.", "calidad.md"))

    # 8. metricas_referencias.csv desactualizado
    ref, pv = D._leer_csv(str(v.archivo("metricas_referencias.csv")), dtype={"ventana": str}), D.metricas_por_ventana(v)
    if ref is not None and pv is not None:
        a = ref[(ref.modelo == "xgboost") & (ref.ventana == "1")].MAE
        b = pv[(pv.modelo == "xgboost") & (pv.ventana == "1")].MAE
        if len(a) and len(b) and f"{a.iloc[0]:.3f}" != f"{b.iloc[0]:.3f}":
            filas.append(_fila("`metricas_referencias.csv` desactualizado", "Fichas de métricas (3.2 Evaluación)",
                               "Archivo desactualizado",
                               f"XGBoost, ventana 1: {F.num(a.iloc[0])} en `metricas_referencias.csv` frente a "
                               f"{F.num(b.iloc[0])} en `metricas_por_ventana.csv`. Quedó de la v1; la interfaz usa "
                               f"`metricas_por_ventana.csv`.", "metricas_referencias.csv"))

    # 9. eleccion_salida.md
    es = D.leer_texto(str(v.archivo("eleccion_salida.md")))
    if es is not None and "('GE', 'P')" in es and "('GE', '1')" not in es:
        filas.append(_fila("`eleccion_salida.md` incompleto", "3.2 Modelado: configuración documentada",
                           "Archivo desactualizado",
                           "Solo muestra la ventana P (la corrida de pandemia lo sobrescribió). La elección de las "
                           "ventanas 1–4 (residual 30,288 frente a directa 44,115) está en el yaml y la interfaz la "
                           "recalcula desde `ajuste_hiperparametros.csv`.", "eleccion_salida.md, ventanas.yaml"))

    # 10. Contigüidad constante en el GE
    sp = D.atencion_spearman(v)
    if sp is not None and (sp.nota == "constante").any():
        filas.append(_fila("Contraste con la contigüidad", "3.2 Evaluación (OE3)", "Redacción",
                           "En el GE todas las aristas son contiguas: la contigüidad binaria es constante y su ρ no se "
                           "calcula. El contraste se hace con la longitud del límite compartido; decir eso en el texto.",
                           "atencion_spearman.csv"))

    # 11. Mapa reproducible
    inei = ("Los límites del INEI no están en esta PC." if not D.GPKG_INEI.exists() else
            "Los límites del INEI están en esta PC.")
    if D.mapa_riesgo(v) is None:
        filas.append(_fila("Mapa reproducible", "3.2 Despliegue: mapa de riesgo distrital", "Falta",
                           "No hay `mapa_riesgo_distrital.csv` para esta versión: correr `python -m src.mapa` en la PC "
                           "con `data/external/inei_distrito_2023/DISTRITO.gpkg`. " + inei, "mapa_riesgo_distrital.csv"))
    else:
        filas.append(_fila("Mapa reproducible", "3.2 Despliegue: «se verificó que el mapa pudiera regenerarse»",
                           "No verificable aquí",
                           "La interfaz no ejecuta `src.mapa`; comprueba que el CSV coincide con las predicciones. "
                           + inei, "mapa_riesgo_distrital.csv"))

    # 12. Selección multianual: la Metodología del AVC3 no la describe
    if D.multianual(D.configuracion(v)):
        filas.append(_fila("Selección multianual de hiperparámetros", "3.2 Modelado: «elegidos solo con validación»",
                           "Redacción",
                           "La configuración de la ventana w se eligió con el MAE de validación promedio de las ventanas "
                           "1…w, no solo con el de w. Agregar a la Metodología la frase propuesta en `lectura.md` "
                           "(sección 4) del experimento h1_v4_validacion_multianual.", "ventanas.yaml (seleccion)"))

    # 13. Fidelidad de la atención
    fi = D.atencion_fidelidad(v)
    if fi is not None and not D.aviso_cache_grafo(v):
        filas.append(_fila("Fidelidad de la atención", "3.2 Evaluación (OE3): «indicio, no causa»", "Redacción",
                           f"Al quitar el 10 % de las aristas con más atención, el ΔMAE medio es "
                           f"{F.num(fi.dMAE_top.mean())}, frente a {F.num(fi.dMAE_azar.mean())} al quitarlas al azar; "
                           f"dañó más que el azar en {int((fi.dMAE_top > fi.dMAE_azar).sum())} de {len(fi)} corridas "
                           "(prueba en `atencion.md`). Si no es significativo, presentar la atención solo como "
                           "descripción.", "atencion_fidelidad.csv, atencion.md"))

    # 14. Reproducción en otra PC (solo texto)
    fuente, texto = reproduccion(v)
    filas.append(_fila("Reproducción en otra PC", "3.1 Validez y repositorio reproducible",
                       "Cubierto" if es_v4(v) else "Decisión del equipo", " ".join(t.replace("**", "") for t in texto),
                       fuente))
    return filas


def mostrar(v: D.Version) -> None:
    st.header("Pendientes del artículo")
    st.markdown("Lo que el AVC3 promete y falta, está parcial o necesita una decisión de redacción. Cada estado se "
                "comprueba contra los archivos de la versión elegida al abrir esta pestaña. Las interpretaciones van en "
                "Conclusiones, no en Resultados.")
    filas = items(v)
    t = pd.DataFrame(filas)
    t.insert(0, "N.º", [str(i + 1) for i in range(len(t))])
    resumen = t.Estado.value_counts()
    st.caption(" · ".join(f"{e}: {n}" for e, n in resumen.items()))
    fuente, texto = reproduccion(v)
    tabla(t, "pendientes", "Pendientes del artículo frente a lo que promete el AVC3", altura=520,
          nota="Nota. Elaboración propia. Estado comprobado contra los archivos del repositorio, salvo la reproducción "
               f"en otra PC ({fuente}).")

    st.subheader("Hallazgo de la reproducción")
    st.markdown(f"Fuente: **{fuente}** (estas cifras no se cargan de un archivo de métricas).\n\n"
                + "\n".join(f"- {t}" for t in texto))
    p = D.pruebas_estadisticas(v)
    if p is not None and "GE vs GC2" in set(p.comparacion):
        pv = p.set_index("comparacion").loc["GE vs GC2", "p"]
        st.caption(f"En `pruebas_estadisticas.csv` de {v.etiqueta}: p (GE vs GC₂) = {F.p_valor(pv)}.")
