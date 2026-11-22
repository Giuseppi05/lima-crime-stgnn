"""Pestaña 6. Mapa de riesgo distrital (Despliegue): predicho, desviación entre semillas, real y error."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import datos as D
from app import formato as F
from app.componentes import calculado, cita, figura, figura_archivo, layout, nota_predicciones, pendiente, tabla

# rampa secuencial de un solo tono (claro = poco, oscuro = mucho)
RAMPA = [[0.0, "#cde2fb"], [0.17, "#9ec5f4"], [0.33, "#6da7ec"], [0.5, "#3987e5"], [0.67, "#256abf"],
         [0.83, "#184f95"], [1.0, "#0d366b"]]
VARIABLES = {"predicho": "Predicción del GE (media de semillas)", "sd": "Desviación entre semillas",
             "real": "Denuncias registradas", "error_abs": "Error absoluto"}


def mostrar(v: D.Version) -> None:
    st.header("Mapa de riesgo distrital (Despliegue)")
    cita("despliegue", "no_operativo", "reproducible")
    nota_predicciones()
    st.error("Sin uso operativo: el mapa no se usa para decisiones de patrullaje. Los registros policiales "
             "históricos pueden reforzar sesgos y estigmatizar zonas.", icon="🚫")
    m = D.mapa_riesgo(v)
    if m is None:
        pendiente(f"no existe `mapa_riesgo_distrital.csv` en {v.etiqueta}")
        return
    mes, ventana = _mes_del_mapa(v, m)
    st.markdown(f"Predicción del GE para el último mes de prueba ({mes}, ventana {ventana}), media de 5 semillas, "
                f"frente a las denuncias registradas ese mes.")

    var = st.radio("Variable", list(VARIABLES), horizontal=True, format_func=VARIABLES.get, key="mapa_var")
    nod = D.nodos()
    if nod is None:
        pendiente("no existe `data/processed/nodos.csv`")
        return
    d = m.merge(nod[["ubigeo", "x_utm", "y_utm"]], on="ubigeo")
    poligonos = False
    if D.GPKG_INEI.exists():
        poligonos = st.toggle("Dibujar los polígonos del INEI (geopandas)", value=False, key="mapa_pol")
    fig = _figura_poligonos(d, var) if poligonos else None
    if fig is None:
        fig = _figura_puntos(d, var)
        if not D.GPKG_INEI.exists():
            st.caption("Los límites del INEI (`data/external/inei_distrito_2023/DISTRITO.gpkg`) no están en esta PC: "
                       "se dibuja cada distrito en su punto de `nodos.csv`, sobre las aristas del grafo geográfico.")
    figura(fig, "mapa_riesgo", f"Mapa de riesgo distrital ({VARIABLES[var]}), {mes}. Artefacto de investigación, "
                               f"sin uso operativo.", alto_export=900)

    t = m.sort_values("predicho", ascending=False)
    tab = pd.DataFrame({"Distrito": t.distrito, "Predicho": t.predicho.map(lambda x: F.num(x, 1)),
                        "Desviación entre semillas": t.sd.map(lambda x: F.num(x, 1)),
                        "Real": t.real.map(F.entero),
                        "Error absoluto": [F.num(e, 1) if ok else "sin información" for e, ok in zip(t.error_abs, t.valido)]})
    tabla(tab, "mapa_riesgo", f"Predicción del GE por distrito para {mes}", altura=380,
          nota="Nota. Elaboración propia. Media y desviación de 5 semillas del GE. Se predicen denuncias registradas, no "
               "criminalidad real; sin uso operativo.")
    if v.figuras is not None:
        with st.expander("Figura del repositorio con los límites del INEI (`mapa_riesgo_distrital.png`)"):
            figura_archivo(v.figuras / "mapa_riesgo_distrital.png", "mapa_riesgo_repo",
                           f"Mapa de riesgo distrital, {mes} (figura generada por src.mapa).")
    st.caption("«Se verificó que el mapa pudiera regenerarse a partir del repositorio»: la interfaz es de solo lectura y "
               "no corre `python -m src.mapa`; lo que sí comprueba es que el CSV coincide con las predicciones.")


def _mes_del_mapa(v, m):
    """Recalcula el mapa desde las predicciones del GE (última ventana 1–4, último mes) y lo coteja con el CSV."""
    pred = D.predicciones(v)
    if pred is None:
        pendiente("no hay predicciones para identificar el mes del mapa")
        return "[PENDIENTE: mes]", "—"
    ge = pred[(pred.modelo == "GE") & pred.ventana.isin(D.VENTANAS_PRUEBA)]
    w = max(ge.ventana)
    g = ge[ge.ventana == w]
    ultimo = g.periodo.max()
    u = g[g.periodo == ultimo].groupby("ubigeo").agg(predicho=("predicho", "mean"), sd=("predicho", "std"),
                                                     real=("real", "first"))
    c = m.set_index("ubigeo")
    dif = max((u.predicho.round(2) - c.predicho).abs().max(), (u.sd.round(2) - c.sd).abs().max())
    if dif < 0.011:
        calculado(f"el CSV coincide con la media y la desviación de las 5 semillas del GE en `predicciones/` "
                  f"(ventana {w}, {F.mes(ultimo)}; diferencia máxima {F.num(dif, 2)}, por el redondeo a 2 decimales).")
    else:
        st.error(f"`mapa_riesgo_distrital.csv` no coincide con las predicciones del GE (diferencia {dif:.3f}).")
    return F.mes(ultimo), w


def _figura_puntos(d, var):
    geo = D.aristas("geo")
    pos = {u: (x / 1000, y / 1000) for u, x, y in zip(d.ubigeo, d.x_utm, d.y_utm)}
    fig = go.Figure()
    if geo is not None:
        xs, ys = [], []
        for o, de in zip(geo.origen, geo.destino):
            if o in pos and de in pos:
                xs += [pos[o][0], pos[de][0], None]
                ys += [pos[o][1], pos[de][1], None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#d9d8d2", width=1), hoverinfo="skip",
                                 showlegend=False))
    ok = d[d.valido] if var == "error_abs" else d
    vmax = ok[var].max()
    tam = 10 + 28 * (ok[var] / vmax) ** 0.5 if vmax > 0 else 14
    fig.add_trace(go.Scatter(
        x=ok.x_utm / 1000, y=ok.y_utm / 1000, mode="markers", showlegend=False,
        marker=dict(size=tam, color=ok[var], colorscale=RAMPA, cmin=0, cmax=vmax, line=dict(color="white", width=1),
                    colorbar=dict(title=dict(text=VARIABLES[var], side="right"), thickness=12)),
        text=ok.distrito, customdata=ok[["predicho", "sd", "real", "error_abs"]],
        hovertemplate="%{text}<br>predicho %{customdata[0]:,.1f} (sd %{customdata[1]:.1f})<br>real "
                      "%{customdata[2]:,.0f}<br>error %{customdata[3]:,.1f}<extra></extra>"))
    sin = d[~d.valido]
    if var == "error_abs" and len(sin):
        fig.add_trace(go.Scatter(x=sin.x_utm / 1000, y=sin.y_utm / 1000, mode="markers", name="Sin información",
                                 marker=dict(size=12, color="white", line=dict(color="#898781", width=1.5),
                                             symbol="x-thin-open"), text=sin.distrito,
                                 hovertemplate="%{text}: sin información<extra></extra>"))
    layout(fig, alto=760)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    return fig


def _figura_poligonos(d, var):
    """Polígonos del INEI con geopandas (opcional; solo si existe el gpkg). Misma lectura que `src.grafos`."""
    try:
        import geopandas as gpd
    except ImportError:
        st.warning("geopandas no está instalado en este entorno: se usan los puntos.")
        return None
    try:
        g = gpd.read_file(D.GPKG_INEI)
        g["ubigeo"] = g["ubigeo"].astype(str).str.zfill(6)
        g = gpd.GeoDataFrame(g[["ubigeo", "geometry"]], geometry="geometry", crs="EPSG:4326").to_crs("EPSG:32718")
        g = g.merge(d, on="ubigeo")
    except Exception as e:  # el archivo existe pero no se pudo leer
        st.warning(f"No se pudieron leer los polígonos del INEI ({e}); se usan los puntos.")
        return None
    vmax = g.loc[g.valido, var].max() if var == "error_abs" else g[var].max()
    import plotly.colors as pc
    fig = go.Figure()
    for r in g.itertuples():
        partes = list(r.geometry.geoms) if r.geometry.geom_type == "MultiPolygon" else [r.geometry]
        valor = getattr(r, var)
        color = "#ffffff" if (var == "error_abs" and not r.valido) else pc.sample_colorscale(RAMPA, [valor / vmax])[0]
        for k, poly in enumerate(partes):
            x, y = poly.exterior.xy
            fig.add_trace(go.Scatter(x=[a / 1000 for a in x], y=[b / 1000 for b in y], fill="toself", mode="lines",
                                     fillcolor=color, line=dict(color="white", width=0.8), showlegend=False,
                                     text=f"{r.distrito}: {F.num(valor, 1)}", hoverinfo="text"))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", showlegend=False, marker=dict(
        colorscale=RAMPA, cmin=0, cmax=vmax, color=[0], colorbar=dict(title=dict(text=VARIABLES[var], side="right"),
                                                                       thickness=12))))
    layout(fig, alto=760)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    return fig
