"""Pestaña 2. Desempeño (OE2): métricas globales, por ventana y por semilla, pruebas, real frente a predicho y R²
por distrito."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import datos as D
from app import formato as F
from app.componentes import (COLOR_MODELO, COLOR_REAL, calculado, cita, figura, layout, nota_predicciones,
                             pendiente, tabla)


def _orden(modelos) -> list[str]:
    return [m for m in D.ORDEN if m in set(modelos)] + sorted(set(modelos) - set(D.ORDEN))


def _nombre(m: str) -> str:
    return D.NOMBRES.get(m, m)


def _etiqueta_ventana(w: str) -> str:
    per = D.periodos_prueba().get(str(w))
    return f"Ventana {w} ({F.mes(per[0])} – {F.mes(per[1])})" if per else f"Ventana {w}"


def mostrar(v: D.Version) -> None:
    st.header("Desempeño predictivo (OE2)")
    cita("oe2", "ventanas_semillas")
    nota_predicciones()
    pred = D.predicciones(v)

    _global(v, pred)
    _por_ventana(v)
    _por_semilla(v)
    _mismo_conjunto(v, pred)
    _pruebas(v)
    _real_predicho(v, pred)
    _r2_distrito(v, pred)


# ---------------------------------------------------------------- global
def _global(v, pred):
    st.subheader("Métricas globales en prueba")
    g = D.metricas_global(v)
    if g is None:
        pendiente(f"no existe `metricas_global.csv` en {v.etiqueta}")
        return
    g = g.set_index("modelo").loc[_orden(g.modelo)]
    t = pd.DataFrame({
        "Modelo": [_nombre(m) for m in g.index],
        "MAE": [F.ms(r.MAE, r.MAE_sd) for r in g.itertuples()],
        "RMSE": [F.ms(r.RMSE, r.RMSE_sd) for r in g.itertuples()],
        "R²": [F.ms(r.R2, r.R2_sd) for r in g.itertuples()],
        "MASE": [F.ms(r.MASE, r.MASE_sd) for r in g.itertuples()] if "MASE" in g else "—",
    })
    tabla(t, "desempeno_global", "Métricas globales en prueba por modelo (4 ventanas, 43 distritos)",
          nota="Nota. Elaboración propia. MAE y RMSE en número de denuncias; media ± desviación estándar entre "
               "5 semillas. XGBoost y las referencias simples son deterministas (una corrida).")
    st.caption("MASE (complementaria): MAE del modelo entre el MAE del «mes anterior» dentro del entrenamiento de "
               "cada ventana; promedio de las 4 ventanas. Fuente: `metricas_global.csv`.")
    if pred is not None:
        r = D.metricas_global_desde_predicciones(pred)
        comunes = [m for m in g.index if m in r.index]
        dif = (r.loc[comunes, ["MAE", "RMSE", "R2"]] - g.loc[comunes, ["MAE", "RMSE", "R2"]]).abs().max().max()
        if comunes and dif < 1e-6:
            st.success(f"Verificación: MAE, RMSE y R² recalculados desde `predicciones/` coinciden con el archivo "
                       f"({len(comunes)} modelos, diferencia máxima {dif:.1e}).", icon="✅")
        else:
            st.error(f"Verificación: las métricas recalculadas desde `predicciones/` difieren del archivo "
                     f"(diferencia máxima {dif:.4f}). Revisar que ambos sean de la misma versión.")


# ---------------------------------------------------------------- por ventana
def _por_ventana(v):
    st.subheader("Métricas por ventana de prueba")
    pv = D.metricas_por_ventana(v)
    if pv is None:
        pendiente(f"no existe `metricas_por_ventana.csv` en {v.etiqueta}")
        return
    pv = pv[pv.ventana.isin(D.VENTANAS_PRUEBA)]
    met = st.radio("Métrica", ["MAE", "RMSE", "R2", "MASE"], horizontal=True, key="pv_met",
                   format_func=lambda m: "R²" if m == "R2" else m)
    modelos = _orden(pv.modelo)
    vent = sorted(pv.ventana.unique())
    t = pd.DataFrame({"Modelo": [_nombre(m) for m in modelos]})
    for w in vent:
        sub = pv[pv.ventana == w].set_index("modelo")
        t[_etiqueta_ventana(w)] = [F.ms(sub.loc[m, met], sub.loc[m, f"{met}_sd"]) if m in sub.index else "—"
                                   for m in modelos]
    nombre_met = "R²" if met == "R2" else met
    tabla(t, "desempeno_ventana", f"{nombre_met} en prueba por modelo y ventana")

    fig = go.Figure()
    for m in modelos:
        s = pv[pv.modelo == m].sort_values("ventana")
        sd = s[f"{met}_sd"].where(s[f"{met}_sd"] > 0)
        fig.add_trace(go.Scatter(x=[f"V{w}" for w in s.ventana], y=s[met], name=_nombre(m), mode="lines+markers",
                                 line=dict(color=COLOR_MODELO.get(m), width=2), marker=dict(size=8),
                                 error_y=dict(type="data", array=sd, visible=True, thickness=1.2, width=4),
                                 hovertemplate=f"{_nombre(m)}<br>%{{x}}: %{{y:.3f}}<extra></extra>"))
    layout(fig, yaxis_title=nombre_met + (" (denuncias)" if met in ("MAE", "RMSE") else ""),
           xaxis_title="Ventana de prueba")
    figura(fig, "desempeno_ventana", f"{nombre_met} en prueba por modelo y ventana (media ± desviación entre "
                                     f"semillas).")


# ---------------------------------------------------------------- por semilla
def _por_semilla(v):
    st.subheader("Corridas por semilla (modelos neuronales)")
    c = D.corridas_neuronales(v)
    if c is None:
        pendiente(f"no existe `corridas_neuronales.csv` en {v.etiqueta}")
        return
    modelos = _orden(c.modelo)
    sel = st.multiselect("Modelos", modelos, default=modelos, format_func=_nombre, key="sem_mod")
    c = c[c.modelo.isin(sel)].copy()
    c["_o"] = c.modelo.map({m: i for i, m in enumerate(modelos)})
    c = c.sort_values(["_o", "ventana", "semilla"])
    n = c.groupby("modelo").size()
    st.caption("Corridas por modelo: " + ", ".join(f"{_nombre(m)} {n[m]}" for m in sel if m in n) +
               " (4 ventanas × 5 semillas = 20).")
    t = pd.DataFrame({"Modelo": c.modelo.map(_nombre), "Ventana": c.ventana, "Semilla": c.semilla.astype(str),
                      "MAE validación": c.mae_validacion.map(F.num), "Épocas": c.epocas.map(F.entero),
                      "MAE": c.MAE.map(F.num), "RMSE": c.RMSE.map(F.num), "R²": c.R2.map(F.num)})
    tabla(t, "desempeno_semilla", "Métricas en prueba por modelo neuronal, ventana y semilla", altura=380)


# ---------------------------------------------------------------- mismo conjunto de prueba
def _mismo_conjunto(v, pred):
    st.subheader("Verificación: mismo conjunto de prueba para todos los modelos")
    cita("mismo_conjunto")
    if pred is None:
        pendiente(f"no hay carpeta `predicciones/` para {v.etiqueta}")
        return
    r = D.verificar_mismo_conjunto(pred[pred.ventana.isin(D.VENTANAS_PRUEBA)])
    t = pd.DataFrame({"Ventana": r.ventana.map(_etiqueta_ventana), "Archivos": r.archivos.map(str),
                      "Celdas": r.celdas.map(F.entero), "Celdas válidas": r.validas.map(F.entero),
                      "Distritos": r.distritos.map(str), "Meses": r.meses.map(str),
                      "Mismas celdas, válidas y reales": r.iguales.map({True: "sí", False: "no"}),
                      "Archivos distintos": r.distintos.replace("", "—")})
    calculado("se comparan, por ventana, las columnas ubigeo, periodo, valido y real de cada archivo de "
              "`predicciones/` (modelo × semilla).")
    tabla(t, "desempeno_mismo_conjunto", "Verificación del conjunto de prueba por ventana")


# ---------------------------------------------------------------- pruebas estadísticas
def _pruebas(v):
    st.subheader("Pruebas estadísticas (n = 43 distritos)")
    cita("pruebas")
    p = D.pruebas_estadisticas(v)
    if p is None:
        pendiente(f"no existe `pruebas_estadisticas.csv` en {v.etiqueta}")
        return
    st.markdown("Regla del estudio: el GE supera a un GC si su MAE **y** su RMSE globales son menores y la "
                "diferencia del MAE por distrito es significativa (α = 0,05). Shapiro-Wilk sobre las diferencias "
                "pareadas decide entre t pareada y Wilcoxon. Las comparaciones con XGBoost y el mes anterior son "
                "complementarias.")
    t = pd.DataFrame({
        "Comparación": p.comparacion.str.replace("GC1", "GC₁").str.replace("GC2", "GC₂")
                        .str.replace("xgboost", "XGBoost").str.replace("mes_anterior", "mes anterior"),
        "Tipo": p.tipo, "MAE GE": p.MAE_GE.map(F.num), "MAE rival": p.MAE_rival.map(F.num),
        "RMSE GE": p.RMSE_GE.map(F.num), "RMSE rival": p.RMSE_rival.map(F.num),
        "Mediana de la dif.": p.mediana_dif.map(F.num), "Shapiro-Wilk p": p.shapiro_p.map(F.p_valor),
        "Prueba": p.prueba, "Estadístico": p.estadistico.map(lambda x: F.num(x, 1)), "p": p.p.map(F.p_valor),
        "Distritos con GE mejor": p.distritos_GE_mejor.map(F.entero),
        "GE supera": p.GE_supera})
    tabla(t, "desempeno_pruebas", "Comparación del GE con cada grupo de control y referencia")
    reglas = p.apply(D.regla_avc3, axis=1)
    if (reglas == p.GE_supera).all():
        calculado("la regla, aplicada a las columnas MAE, RMSE y p del propio archivo, da lo mismo que "
                  "`GE_supera` en todas las filas.")
    else:
        st.error("La regla recalculada no coincide con `GE_supera` en: " +
                 ", ".join(p.comparacion[reglas != p.GE_supera]))
    if "p_RMSE_distrito" in p:
        st.caption("Como apoyo, la misma prueba sobre el RMSE por distrito da p = " +
                   "; ".join(f"{c}: {F.p_valor(x)}" for c, x in zip(p.comparacion, p.p_RMSE_distrito)) + ".")


# ---------------------------------------------------------------- real frente a predicho
def _real_predicho(v, pred):
    st.subheader("Real frente a predicho por distrito y mes")
    if pred is None:
        pendiente(f"no hay carpeta `predicciones/` para {v.etiqueta}")
        return
    pred = pred[pred.ventana.isin(D.VENTANAS_PRUEBA)]
    nod = D.nodos()
    nombres = dict(zip(nod.ubigeo, nod.distrito)) if nod is not None else {}
    ubigeos = sorted(pred.ubigeo.unique(), key=lambda u: nombres.get(u, u))
    c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
    ubi = c1.selectbox("Distrito", ubigeos, format_func=lambda u: nombres.get(u, u),
                       index=ubigeos.index("150132") if "150132" in ubigeos else 0, key="rp_dist")
    modelos = _orden(pred.modelo)
    sel = c2.multiselect("Modelos", modelos, default=[m for m in ["GE", "GC2", "GC1", "mes_anterior"] if m in modelos],
                         format_func=_nombre, key="rp_mod")
    vent = c3.selectbox("Ventana", ["Todas"] + sorted(pred.ventana.unique()), key="rp_vent",
                        format_func=lambda w: "Todas (1–4)" if w == "Todas" else _etiqueta_ventana(w))
    semillas = sorted(pred[pred.modelo.isin(sel)].semilla.unique()) if sel else [0]
    sem = c4.selectbox("Semilla", ["media"] + semillas, key="rp_sem",
                       format_func=lambda s: "Media de semillas" if s == "media" else str(s))

    d = pred[(pred.ubigeo == ubi) & pred.valido]
    if vent != "Todas":
        d = d[d.ventana == vent]
    real = d.drop_duplicates("periodo").sort_values("periodo")
    fig = go.Figure(go.Scatter(x=real.periodo, y=real.real, name="Real (denuncias registradas)", mode="lines+markers",
                               line=dict(color=COLOR_REAL, width=2), marker=dict(size=6),
                               hovertemplate="Real %{x}: %{y:,.0f}<extra></extra>"))
    avisos = []
    for m in sel:
        dm = d[d.modelo == m]
        if sem == "media":
            dm = dm.groupby("periodo", as_index=False).predicho.mean()
        elif sem in set(dm.semilla):
            dm = dm[dm.semilla == sem]
        else:
            avisos.append(_nombre(m))
            dm = dm[dm.semilla == dm.semilla.min()]
        dm = dm.sort_values("periodo")
        fig.add_trace(go.Scatter(x=dm.periodo, y=dm.predicho, name=_nombre(m), mode="lines",
                                 line=dict(color=COLOR_MODELO.get(m), width=2),
                                 hovertemplate=f"{_nombre(m)} %{{x}}: %{{y:,.1f}}<extra></extra>"))
    layout(fig, alto=440, yaxis_title="Denuncias de hurto + robo", xaxis_title="Mes")
    # eje de meses como categorías con etiquetas en español (las fechas de Plotly salen en inglés)
    meses = sorted(real.periodo)
    paso = 1 if len(meses) <= 12 else 6
    marcas = [m for m in meses if (int(m[5:7]) - int(meses[0][5:7])) % paso == 0]
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=meses, tickvals=marcas,
                     ticktext=[F.mes(m) for m in marcas])
    if avisos:
        st.caption(f"Sin semilla {sem} (deterministas, una corrida): {', '.join(avisos)}; se muestra su única corrida.")
    excl = pred[(pred.ubigeo == ubi) & ~pred.valido].periodo.unique()
    if len(excl):
        st.caption(f"Meses sin información excluidos: {', '.join(sorted(excl))}.")
    dist = nombres.get(ubi, ubi)
    figura(fig, "desempeno_real_predicho",
           f"Denuncias registradas y predichas en {F.nombre_propio(dist)}, "
           f"{'ventanas 1–4' if vent == 'Todas' else 'ventana ' + vent}"
           f"{', media de semillas' if sem == 'media' else ', semilla ' + str(sem)}.")


# ---------------------------------------------------------------- R² por distrito
NOTA_R2 = ("**Por qué sale negativo:** el R² de un distrito compara su error con la variación de ese mismo distrito "
           "dentro de los 12 meses de cada ventana. Esa variación es pequeña frente al error de un mes a otro, así que "
           "errar unas decenas de denuncias basta para que el R² sea menor que 0; al mes anterior le pasa lo mismo. "
           "**Por qué el global es alto:** el R² global usa los 43 distritos juntos, y la diferencia de nivel entre "
           "distritos es enorme (de 1 a 1 687 denuncias por celda observada, según `calidad.md`); acertar el nivel de "
           "cada distrito ya explica casi toda esa varianza.")


def _r2_distrito(v, pred):
    st.subheader("R² por distrito")
    cita("ficha_metricas")
    if pred is None:
        pendiente(f"no hay carpeta `predicciones/` para {v.etiqueta}; el R² por distrito no existe como archivo")
        return
    nod = D.nodos()
    nombres = dict(zip(nod.ubigeo, nod.distrito)) if nod is not None else {}
    r = D.r2_por_distrito(pred, "ventana")
    calculado("R² de cada distrito en los 12 meses de cada ventana y semilla; promedio de las 4 ventanas; media ± "
              "desviación entre semillas (la misma agregación que `metricas_por_distrito.csv`).")
    st.markdown(NOTA_R2)

    modelos = [m for m in _orden(r.modelo) if m != "mes_anterior"]
    m = st.selectbox("Modelo (siempre junto al mes anterior)", modelos, format_func=_nombre, key="r2_mod")
    piv_m = r.pivot(index="ubigeo", columns="modelo", values="R2")
    piv_s = r.pivot(index="ubigeo", columns="modelo", values="R2_sd")
    orden_u = list(piv_m[m].sort_values(ascending=False).index)
    t = pd.DataFrame({"Distrito": [nombres.get(u, u) for u in orden_u],
                      _nombre(m): [F.ms(piv_m.loc[u, m], piv_s.loc[u, m]) for u in orden_u],
                      "Mes anterior": [F.num(piv_m.loc[u, "mes_anterior"]) for u in orden_u]})
    med = r.groupby("modelo").R2.median()
    neg = r[r.R2 < 0].groupby("modelo").size()
    st.caption(f"Mediana entre distritos: {_nombre(m)} {F.num(med[m])} (R² < 0 en {neg.get(m, 0)} de 43); "
               f"mes anterior {F.num(med['mes_anterior'])} (R² < 0 en {neg.get('mes_anterior', 0)} de 43).")
    tabla(t, "desempeno_r2_distrito", f"R² en prueba por distrito: {_nombre(m)} y mes anterior", altura=380,
          nota="Nota. Elaboración propia. Calculado desde las predicciones válidas de las ventanas 1–4: R² por ventana "
               "(12 meses) y promedio de las 4 ventanas; media ± desviación entre semillas.")

    s = pd.DataFrame({"ubigeo": orden_u[::-1]})
    s["distrito"] = s.ubigeo.map(nombres)
    fig = go.Figure()
    for clave, nombre in [(m, _nombre(m)), ("mes_anterior", "Mes anterior")]:
        sd = piv_s.loc[s.ubigeo, clave].where(piv_s.loc[s.ubigeo, clave] > 0)
        fig.add_trace(go.Bar(x=piv_m.loc[s.ubigeo, clave], y=s.distrito, orientation="h", name=nombre,
                             marker_color=COLOR_MODELO.get(clave), marker_line=dict(color="white", width=1),
                             error_x=dict(type="data", array=sd, visible=True, thickness=1, width=2),
                             hovertemplate=f"{nombre}<br>%{{y}}: %{{x:.3f}}<extra></extra>"))
    layout(fig, alto=1000, xaxis_title="R² (por ventana, promedio de las 4)", barmode="group", bargap=0.25)
    fig.update_yaxes(tickfont=dict(size=10))
    figura(fig, "desempeno_r2_distrito", f"R² en prueba por distrito, {_nombre(m)} y mes anterior (R² por ventana, "
                                         f"promedio de las 4 ventanas).", alto_export=1000)

    with st.expander("Alternativa: R² con los 48 meses juntos (todos los modelos)"):
        r48 = D.r2_por_distrito(pred, "48")
        calculado("R² de cada distrito con los 48 meses de prueba juntos, por semilla; media ± desviación entre "
                  "semillas. El cambio de nivel entre ventanas aumenta la varianza total del distrito y eleva este R².")
        m48 = r48.pivot(index="ubigeo", columns="modelo", values="R2")
        s48 = r48.pivot(index="ubigeo", columns="modelo", values="R2_sd")
        orden48 = sorted(m48.index, key=lambda u: nombres.get(u, u))
        t48 = pd.DataFrame({"Distrito": [nombres.get(u, u) for u in orden48]})
        for mm in _orden(r48.modelo):
            t48[_nombre(mm)] = [F.ms(m48.loc[u, mm], s48.loc[u, mm]) for u in orden48]
        st.caption("Medianas entre distritos: " + "; ".join(
            f"{_nombre(mm)} {F.num(x)}" for mm, x in r48.groupby("modelo").R2.median().reindex(_orden(r48.modelo)).items()))
        tabla(t48, "desempeno_r2_distrito_48", "R² en prueba por distrito y modelo (48 meses juntos)", altura=380,
              nota="Nota. Elaboración propia. Calculado desde las predicciones válidas de las ventanas 1–4, con los 48 "
                   "meses juntos por semilla; media ± desviación entre semillas.")
