"""Pestaña 4. Equidad (OE4): error relativo por distrito, brechas, sectores y prueba entre sectores."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import datos as D
from app import formato as F
from app.componentes import COLOR_SECTOR, calculado, cita, figura, layout, nota_predicciones, pendiente, tabla


def mostrar(v: D.Version) -> None:
    st.header("Equidad algorítmica (OE4)")
    cita("oe4", "sectores")
    nota_predicciones()
    epd = D.equidad_por_distrito(v)
    _barras(v, epd)
    _resumen(v)
    _prueba(v, epd)
    _composicion(v, epd)


def _barras(v, epd):
    st.subheader("Error relativo por distrito")
    if epd is None:
        pendiente(f"no existe `equidad_por_distrito.csv` en {v.etiqueta}")
        return
    modelos = [m for m in D.ORDEN if m in set(epd.modelo)]
    m = st.selectbox("Modelo", modelos, format_func=lambda x: D.NOMBRES.get(x, x), key="eq_mod")
    s = epd[epd.modelo == m].sort_values("error_rel", ascending=True).copy()
    s["etiqueta"] = s.distrito + s.distrito.isin(D.PLAYA).map({True: " (playa)", False: ""})
    fig = go.Figure()
    for sec in D.SECTORES:
        g = s[s.sector == sec]
        fig.add_trace(go.Bar(x=g.error_rel, y=g.etiqueta, orientation="h", name=f"Sector {sec}",
                             marker_color=COLOR_SECTOR[sec], marker_line=dict(color="white", width=1),
                             customdata=g.volumen_entrenamiento,
                             hovertemplate="%{y}<br>Error relativo: %{x:.3f}<br>Volumen medio en entrenamiento: "
                                           "%{customdata:.1f}<extra>Sector " + sec + "</extra>"))
    layout(fig, alto=900, xaxis_title="Error relativo (MAE del distrito / promedio de denuncias del distrito)",
           barmode="overlay")
    fig.update_yaxes(categoryorder="array", categoryarray=list(s.etiqueta), tickfont=dict(size=10))
    figura(fig, "equidad_error_rel", f"Error relativo por distrito y sector, {D.NOMBRES.get(m, m)} "
                                     f"(promedio de 4 ventanas y semillas).", alto_export=900)
    st.caption("Error relativo = MAE del distrito / promedio de denuncias del distrito en la prueba, por ventana; "
               "promedio entre ventanas y semillas. «(playa)»: distritos de bajo volumen que se excluyen en la "
               "brecha sin playa. Fuente: `equidad_por_distrito.csv`.")

    fig2 = go.Figure()
    for sec in D.SECTORES:
        g = s[s.sector == sec]
        fig2.add_trace(go.Box(y=g.error_rel, name=f"Sector {sec}", marker_color=COLOR_SECTOR[sec], boxpoints="all",
                              jitter=0.35, pointpos=0, text=g.distrito,
                              hovertemplate="%{text}: %{y:.3f}<extra></extra>"))
    layout(fig2, alto=380, yaxis_title="Error relativo", showlegend=False)
    figura(fig2, "equidad_sectores", f"Distribución del error relativo por sector, {D.NOMBRES.get(m, m)}.")


def _resumen(v):
    st.subheader("Brechas y medias por sector")
    r = D.equidad_resumen(v)
    if r is None:
        pendiente(f"no existe `equidad_resumen.csv` en {v.etiqueta}")
        return
    brecha_sec = D.brecha_entre_sectores(r)
    t = pd.DataFrame({
        "Modelo": r.modelo, "Mediana": r.error_rel_mediana.map(F.num),
        "Mínimo (distrito)": [f"{F.num(a)} ({b})" for a, b in zip(r["min"], r.distrito_min)],
        "Máximo (distrito)": [f"{F.num(a)} ({b})" for a, b in zip(r["max"], r.distrito_max)],
        "Brecha entre distritos": r.brecha.map(F.num), "Brecha sin playa": r.brecha_sin_playa.map(F.num),
        "Media bajo": r.media_bajo.map(F.num), "Media medio": r.media_medio.map(F.num),
        "Media alto": r.media_alto.map(F.num), "Brecha entre sectores": brecha_sec.map(F.num)})
    tabla(t, "equidad_resumen", "Error relativo por distrito: brechas y medias por sector",
          nota="Nota. Elaboración propia. Brecha = máximo − mínimo. Sin playa: sin " + ", ".join(
              F.nombre_propio(x) for x in D.PLAYA) + ".")
    calculado("«Brecha entre sectores» = máximo − mínimo de las columnas media_bajo, media_medio y media_alto de "
              "`equidad_resumen.csv`. El resto de las columnas sale tal cual del archivo.")


def _prueba(v, epd):
    st.subheader("Prueba de diferencias entre sectores")
    cita("anova")
    k = D.equidad_sectores(v)
    if k is None:
        pendiente(f"no existe `equidad_sectores.csv` en {v.etiqueta}")
        return
    st.warning("El AVC3 dice «entre distritos», pero la prueba se hace **entre los tres sectores** (un valor de "
               "error relativo por distrito, agrupado por sector). Queda en Pendientes para ajustar el texto o "
               "la prueba.")
    st.markdown("ANOVA si los tres grupos pasan Shapiro-Wilk y Levene; si no, Kruskal-Wallis (α = 0,05).")
    t = pd.DataFrame({"Modelo": k.modelo, "Prueba": k.prueba, "Estadístico": k.estadistico.map(F.num),
                      "p": k.p.map(F.p_valor), "Significativa": k.significativa})
    if epd is not None:
        n = epd.drop_duplicates("ubigeo").sector.value_counts()
        st.caption("Distritos por sector: " + ", ".join(f"{s} {n.get(s, 0)}" for s in D.SECTORES) + ".")
    tabla(t, "equidad_prueba", "Prueba de diferencias del error relativo entre sectores")


def _composicion(v, epd):
    st.subheader("Composición de los sectores")
    if epd is None:
        pendiente(f"no existe `equidad_por_distrito.csv` en {v.etiqueta}")
        return
    c = D.composicion_sectores(epd)
    t = pd.DataFrame({"Sector": c.sector, "Distritos (n)": c.n.map(str),
                      "Volumen medio mensual en entrenamiento": [f"{F.num(a, 1)} – {F.num(b, 1)}"
                                                                for a, b in zip(c.vol_min, c.vol_max)],
                      "Distritos": c.distritos})
    tabla(t, "equidad_composicion", "Composición de los sectores según el volumen de denuncias en entrenamiento",
          nota="Nota. Elaboración propia. Terciles de los 43 distritos según su volumen mensual medio de denuncias "
               "en entrenamiento (promedio de las 4 ventanas).")
