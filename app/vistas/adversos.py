"""Pestaña 5. Casos adversos: pandemia (ventana P) y perturbaciones del grafo y de los datos."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import datos as D
from app import formato as F
from app.componentes import (AVISO_CACHE, COLOR_MODELO, COLOR_REAL, calculado, cita, figura, layout,
                             nota_predicciones, pendiente, tabla)

VALIDO = "Válido: no depende del grafo"
REVISION = "En revisión (caché del grafo)"


def mostrar(v: D.Version) -> None:
    st.header("Casos adversos")
    cita("adversos", "pandemia")
    nota_predicciones()
    _pandemia(v)
    _perturbaciones(v)


# ---------------------------------------------------------------- pandemia
def _pandemia(v):
    st.subheader("Pandemia (ventana P)")
    st.success(f"{VALIDO}. Todos los modelos se reentrenaron y ajustaron con su propia validación en esta ventana.",
               icon="✅")
    per = D.periodos_prueba().get("P")
    cfg = D.configuracion(v)
    if cfg and "ventana_pandemia" in cfg:
        w = cfg["ventana_pandemia"]["P"]
        st.markdown(f"Entrenamiento {F.mes(w['entrenamiento'][0])} – {F.mes(w['entrenamiento'][1])}; validación "
                    f"{F.mes(w['validacion'][0])} – {F.mes(w['validacion'][1])}; prueba {F.mes(w['prueba'][0])} – "
                    f"{F.mes(w['prueba'][1])}.")
    pa = D.pandemia(v)
    if pa is None:
        pendiente(f"no existe `pandemia.csv` en {v.etiqueta}")
        return
    g = D.metricas_global(v)
    g = g.set_index("modelo") if g is not None else None
    filas = []
    for r in pa.itertuples():
        clave = D.CLAVE_DE_NOMBRE.get(r.modelo, r.modelo)
        fila = {"Modelo": r.modelo, "MAE (ventana P)": F.ms(r.MAE, r.MAE_sd), "RMSE (ventana P)": F.ms(r.RMSE, r.RMSE_sd),
                "R² (ventana P)": F.ms(r.R2, r.R2_sd)}
        if g is not None and clave in g.index:
            fila["MAE (4 ventanas normales)"] = F.ms(g.loc[clave, "MAE"], g.loc[clave, "MAE_sd"])
        filas.append(fila)
    tabla(pd.DataFrame(filas), "adversos_pandemia", "Desempeño en la ventana de pandemia (abril de 2020 a marzo de 2021)",
          nota="Nota. Elaboración propia. Media ± desviación estándar entre 5 semillas en los modelos neuronales; "
               "XGBoost y las referencias simples son deterministas. MAE y RMSE en denuncias. La columna de las 4 "
               "ventanas normales viene de metricas_global.csv.")
    _verificar_pandemia(v, pa)

    pred = D.predicciones(v)
    if pred is None or "P" not in set(pred.ventana):
        pendiente(f"no hay predicciones de la ventana P en {v.etiqueta}")
        return
    pp = pred[(pred.ventana == "P") & pred.valido]
    modelos = [m for m in D.ORDEN if m in set(pp.modelo)]
    sel = st.multiselect("Modelos", modelos, default=[m for m in ["GE", "GC2", "GC1", "mes_anterior"] if m in modelos],
                         format_func=lambda m: D.NOMBRES.get(m, m), key="pand_mod")
    real = pp.drop_duplicates(["ubigeo", "periodo"]).groupby("periodo").real.sum()
    fig = go.Figure(go.Scatter(x=real.index, y=real.values, name="Real (denuncias registradas)", mode="lines+markers",
                               line=dict(color=COLOR_REAL, width=2), marker=dict(size=6),
                               hovertemplate="Real %{x}: %{y:,.0f}<extra></extra>"))
    for m in sel:
        s = pp[pp.modelo == m].groupby(["semilla", "periodo"]).predicho.sum().groupby("periodo").mean()
        fig.add_trace(go.Scatter(x=s.index, y=s.values, name=D.NOMBRES.get(m, m), mode="lines",
                                 line=dict(color=COLOR_MODELO.get(m), width=2),
                                 hovertemplate=f"{D.NOMBRES.get(m, m)} %{{x}}: %{{y:,.0f}}<extra></extra>"))
    layout(fig, alto=420, yaxis_title="Denuncias de hurto + robo (43 distritos)", xaxis_title="Mes")
    meses = list(real.index)
    fig.update_xaxes(type="category", tickvals=meses[::2], ticktext=[F.mes(m) for m in meses[::2]])
    figura(fig, "adversos_pandemia", "Total mensual de Lima Metropolitana, real y predicho, en la ventana de pandemia "
                                     "(media de semillas).")
    calculado("suma de los 43 distritos por mes desde `predicciones/*_P_*.csv` (celdas válidas); en los modelos "
              "neuronales, media de las 5 semillas.")
    c = D.corridas_pandemia(v)
    if c is not None:
        with st.expander("Corridas por semilla en la ventana P"):
            st.dataframe(pd.DataFrame({"Modelo": c.modelo.map(D.NOMBRES), "Semilla": c.semilla.map(str),
                                       "MAE validación": c.mae_validacion.map(F.num), "Épocas": c.epocas.map(F.entero),
                                       "MAE": c.MAE.map(F.num), "RMSE": c.RMSE.map(F.num), "R²": c.R2.map(F.num)}),
                         hide_index=True)


def _verificar_pandemia(v, pa):
    c, r = D.corridas_pandemia(v), D.metricas_referencias_pandemia(v)
    diffs = []
    pa = pa.set_index(pa.modelo.map(lambda x: D.CLAVE_DE_NOMBRE.get(x, x)))
    if c is not None:
        for m, g in c.groupby("modelo"):
            if m in pa.index:
                diffs.append(abs(round(g.MAE.mean(), 3) - pa.loc[m, "MAE"]))
    if r is not None:
        for t in r[r.ventana == "P"].itertuples():
            if t.modelo in pa.index:
                diffs.append(abs(round(t.MAE, 3) - pa.loc[t.modelo, "MAE"]))
    if diffs and max(diffs) < 1e-9:
        calculado(f"el MAE de `pandemia.csv` coincide con `corridas_neuronales_pandemia.csv` y con las filas P de "
                  f"`metricas_referencias_pandemia.csv` ({len(diffs)} modelos).")
    elif diffs:
        st.error(f"El MAE de `pandemia.csv` difiere de las corridas o referencias (máx. {max(diffs):.3f}).")


# ---------------------------------------------------------------- perturbaciones
def _perturbaciones(v):
    st.subheader("Perturbaciones del grafo y de los datos (GE)")
    c = D.casos_adversos(v)
    if c is None:
        pendiente(f"no existe `casos_adversos.csv` en {v.etiqueta}")
        return
    if D.aviso_cache_grafo(v):
        st.warning(AVISO_CACHE + " Afecta a «aristas eliminadas» y «ruido en coordenadas»; «meses faltantes» no "
                                 "depende del grafo.")
    st.markdown("Sin reentrenar: el GE ya entrenado (4 ventanas × 5 semillas) predice la prueba con el grafo o la "
                "entrada perturbados; 5 sorteos por nivel. `casos_adversos.csv` no tiene columna de modelo: las "
                "perturbaciones se aplicaron **solo al GE** (queda en Pendientes).")
    r = D.resumen_adversos(c)
    revision = D.aviso_cache_grafo(v)

    def estado(caso):
        if caso == "limpio":
            return "Referencia"
        if caso in D.CASOS_GRAFO:
            return REVISION if revision else "Válido (corrección declarada)"
        return VALIDO

    t = pd.DataFrame({"Caso": r.caso.str.capitalize(), "Nivel": r.nivel, "Estado": r.caso.map(estado),
                      "MAE": [F.ms(a, b) for a, b in zip(r.MAE, r.MAE_sd)], "RMSE": r.RMSE.map(F.num),
                      "R²": r.R2.map(F.num), "Cambio del MAE (%)": r.cambio_MAE_pct.map(F.num),
                      "Corridas con más error": [f"{a} de {b}" for a, b in zip(r.corridas_peor, r.n)]})
    tabla(t, "adversos_perturbaciones", "Desempeño del GE ante perturbaciones del grafo y de los datos",
          nota="Nota. Elaboración propia. Cambio del MAE: media del cambio porcentual frente al mismo modelo, ventana y "
               "semilla con datos limpios. MAE: media ± desviación entre corridas. Los casos del grafo están en "
               "revisión por un error de caché del grafo.")
    calculado("misma agregación que `src.adversos`, recalculada desde `casos_adversos.csv`.")
    md = D.casos_adversos_md(v)
    if md is not None:
        tm = D.tablas_md(md)
        if tm:
            mae_md = [float(x) for x in tm[0][1]["MAE"]]
            ok = [f"{x:.3f}" for x in mae_md] == [f"{x:.3f}" for x in r.MAE]
            st.caption("✅ El MAE coincide con `casos_adversos.md`." if ok else "⚠️ El MAE no coincide con "
                                                                              "`casos_adversos.md`.")
    ruido = r[r.caso == "ruido en coordenadas"]
    limpio = r[r.caso == "limpio"].MAE.iloc[0]
    if len(ruido) and all(f"{x:.3f}" == f"{limpio:.3f}" for x in ruido.MAE):
        st.caption(f"El MAE medio con ruido en coordenadas es igual al limpio ({F.num(limpio)}) en ambos σ: coherente "
                   f"con que la perturbación del grafo no se haya aplicado por el error de caché.")

    base = c[c.caso == "limpio"].set_index(["ventana", "semilla"]).MAE
    d = c[c.caso != "limpio"].join(base.rename("MAE_limpio"), on=["ventana", "semilla"])
    d["cambio"] = (d.MAE / d.MAE_limpio - 1) * 100
    d["etiqueta"] = d.caso.str.capitalize() + ", " + d.nivel
    fig = go.Figure()
    for et, g in d.groupby("etiqueta", sort=False):
        en_rev = g.caso.iloc[0] in D.CASOS_GRAFO and revision
        fig.add_trace(go.Box(y=g.cambio, name=et, boxpoints="all", jitter=0.4, pointpos=0,
                             marker=dict(size=4, color="#898781" if en_rev else COLOR_MODELO["GE"]),
                             line=dict(color="#898781" if en_rev else COLOR_MODELO["GE"]),
                             hovertemplate=f"{et}<br>%{{y:.2f}} %<extra></extra>"))
    fig.add_hline(y=0, line=dict(color="#52514e", width=1))
    layout(fig, alto=420, yaxis_title="Cambio del MAE frente al caso limpio (%)", showlegend=False)
    figura(fig, "adversos_perturbaciones", "Cambio porcentual del MAE del GE ante cada perturbación (100 corridas por "
                                           "nivel; en gris, los casos del grafo en revisión).")
    if md is not None:
        cp = D.tabla_md(md, "Cambio en los pesos del grafo vial por el ruido en coordenadas")
        if cp is not None:
            with st.expander("Cambio en los pesos del grafo vial por el ruido en coordenadas (`casos_adversos.md`)"):
                st.markdown("El ruido solo cambia la distancia por red y, con ella, el peso; el conjunto de aristas no "
                            "cambia.")
                st.dataframe(cp.map(D.decimal_es), hide_index=True)
