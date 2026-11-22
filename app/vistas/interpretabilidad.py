"""Pestaña 3. Interpretabilidad (OE3): atención temporal, autoatención, Spearman, pares de distritos y fidelidad."""
from __future__ import annotations

import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import datos as D
from app import formato as F
from app.componentes import (AVISO_CACHE, COLOR_MODELO, calculado, cita, figura, figura_archivo, layout,
                             nota_predicciones, pendiente, tabla)

ETIQ_ATENCION = {"peso": "Atención media", "peso_x_grado": "Atención × grado"}
ETIQ_CONTRA = {"peso_vial": "Peso vial", "n_tramos": "Tramos viales que cruzan", "limite_km": "Límite compartido (km)",
               "contiguo": "Contigüidad (0/1)"}


def mostrar(v: D.Version) -> None:
    st.header("Interpretabilidad (OE3)")
    cita("oe3", "indicio")
    nota_predicciones()
    _temporal(v)
    _autoatencion(v)
    _spearman(v)
    _pares(v)
    _fidelidad(v)


def _md_num(texto: str | None, patron: str):
    m = re.search(patron, texto or "")
    return m.groups() if m else None


# ---------------------------------------------------------------- temporal
def _temporal(v):
    st.subheader("Atención temporal por desfase")
    cita("interp_variables")
    t = D.atencion_temporal(v)
    if t is None:
        pendiente(f"no existe `atencion_temporal.csv` en {v.etiqueta}")
        return
    cols = [c for c in t.columns if c != "desfase"]
    tab = pd.DataFrame({"Desfase (meses)": t.desfase.map(str)})
    for c in cols:
        tab[c.replace("GC2", "GC₂").replace("GC1", "GC₁")] = t[c].map(F.num)
    tabla(tab, "interp_temporal", "Atención temporal media por desfase, modelo y meses de entrada (L)",
          nota="Nota. Elaboración propia. Media sobre distritos, meses de prueba y semillas de las ventanas en que la "
               "validación eligió cada L. Una atención uniforme vale 1/L (0,167 con L = 6; 0,083 con L = 12).")
    cfg = D.configuracion(v)
    if cfg is not None:
        e = D.entrada_elegida(cfg)
        st.caption("L elegido por la validación (ventanas 1–4): " + "; ".join(
            f"{D.NOMBRES[m]}: " + ", ".join(f"V{r.ventana} = {r.L}" for r in e[e.modelo == m].itertuples())
            for m in D.NEURONALES) + ".")

    fig = go.Figure()
    for c in cols:
        m = re.match(r"^(\w+) \(L=(\d+)\)$", c)
        if not m:
            continue
        mod, L = m.group(1), int(m.group(2))
        s = t[["desfase", c]].dropna()
        nombre = f"{D.NOMBRES.get(mod, mod)}, L = {L}"
        fig.add_trace(go.Scatter(x=s.desfase, y=s[c], mode="lines+markers", name=nombre,
                                 line=dict(color=COLOR_MODELO.get(mod), width=2, dash="solid" if L == 6 else "dot"),
                                 marker=dict(size=8, symbol="circle" if L == 6 else "square"),
                                 hovertemplate=f"{nombre}<br>desfase %{{x}}: %{{y:.3f}}<extra></extra>"))
    for L in (6, 12):
        fig.add_hline(y=1 / L, line=dict(color="#898781", width=1, dash="dash"),
                      annotation_text=f"uniforme 1/{L}", annotation_position="top right")
    layout(fig, alto=440, xaxis_title="Desfase (meses antes del mes predicho)", yaxis_title="Atención temporal media")
    fig.update_xaxes(dtick=1)
    figura(fig, "interp_temporal", "Atención temporal media por desfase, según el modelo y los meses de entrada (L) "
                                   "elegidos en validación.")
    if v.figuras is not None and (v.figuras / "atencion_temporal.png").exists():
        with st.expander("Figura del repositorio (`atencion_temporal.png`)"):
            figura_archivo(v.figuras / "atencion_temporal.png", "interp_temporal_repo",
                           "Atención temporal por desfase (figura generada por src.atencion).")


# ---------------------------------------------------------------- autoatención
def _autoatencion(v):
    st.subheader("Autoatención media en el GAT")
    a = D.autoatencion(v)
    md = D.atencion_md(v)
    ficha = _md_num(md, r"GE (\d+\.\d+); GC₂ (\d+\.\d+)")
    if not a:
        if ficha:
            st.markdown(f"Según `atencion.md`: GE {F.num(float(ficha[0]))}; GC₂ {F.num(float(ficha[1]))}.")
        else:
            pendiente(f"no hay pesos de atención (`atencion/`) ni autoatención en la ficha de {v.etiqueta}")
        return
    t = pd.DataFrame({"Modelo": [D.NOMBRES[m] for m in a], "Autoatención media": [F.num(x) for x in a.values()]})
    st.dataframe(t, hide_index=True)
    calculado("media del peso espacial con origen = destino en `results/atencion/` (ventanas 1–4, 5 semillas). En el "
              "GAT, la atención de cada distrito destino suma 1 entre sus vecinos y él mismo.")
    if ficha:
        ok = [F.num(float(x)) for x in ficha] == [F.num(a.get("GE")), F.num(a.get("GC2"))]
        st.caption("✅ Coincide con `atencion.md`." if ok else f"⚠️ `atencion.md` dice GE {ficha[0]}; GC₂ {ficha[1]}.")


# ---------------------------------------------------------------- Spearman
def _spearman(v):
    st.subheader("Atención espacial frente a la contigüidad y la conectividad vial")
    s = D.atencion_spearman(v)
    if s is None:
        pendiente(f"no existe `atencion_spearman.csv` en {v.etiqueta}")
        return
    t = pd.DataFrame({"Modelo": s.modelo.replace({"GC2": "GC₂"}), "Atención": s.atencion.map(ETIQ_ATENCION),
                      "Frente a": s.contra.map(ETIQ_CONTRA).fillna(s.contra), "ρ de Spearman": s.rho.map(F.num),
                      "p": s.p.map(F.p_valor), "Aristas": s.n_aristas.map(str),
                      "Nota": s.nota.fillna("").replace({"constante": "constante: no se calcula"})})
    tabla(t, "interp_spearman", "Correlación de Spearman entre la atención espacial por arista y la conectividad",
          nota="Nota. Elaboración propia. «Atención × grado» multiplica la atención por el número medio de entradas del "
               "par (vecinos + 1) para quitar el efecto de la normalización por nodo.")
    st.info("Contigüidad: las 89 aristas del GE son contiguas (GE ⊂ GC₂), así que la contigüidad binaria es "
            "constante y su ρ no se puede calcular; en el GC₂ todas las aristas son contiguas por definición. Por eso la "
            "contigüidad se mide además como longitud del límite compartido (km). En el GC₂, 9 pares contiguos no "
            "tienen tramo vial (peso vial 0).", icon="ℹ️")


# ---------------------------------------------------------------- pares
def _pares(v):
    st.subheader("Pares de distritos con más atención")
    c1, c2, c3 = st.columns(3)
    mod = c1.selectbox("Modelo", ["GE", "GC2"], format_func=lambda m: D.NOMBRES[m], key="par_mod")
    orden = c2.selectbox("Ordenar por", ["peso", "peso_x_grado"], format_func=ETIQ_ATENCION.get, key="par_ord")
    n = c3.number_input("Número de pares", 5, 98, 10, key="par_n")
    p = D.atencion_pares(v, mod)
    if p is None:
        pendiente(f"no existe `atencion_espacial_pares_{mod}.csv` en {v.etiqueta}")
        return
    top = p.nlargest(int(n), orden)
    t = pd.DataFrame({"Par": top.par, "Atención media": top.peso.map(F.num),
                      "Atención × grado": top.peso_x_grado.map(F.num), "Peso vial": top.peso_vial.map(F.num),
                      "Tramos": top.n_tramos.map(F.entero), "Límite (km)": top.limite_km.map(lambda x: F.num(x, 2))})
    tabla(t, "interp_pares", f"Pares de distritos con mayor {ETIQ_ATENCION[orden].lower()}, {D.NOMBRES[mod]}",
          nota="Nota. Elaboración propia. Atención espacial media por par no dirigido (promedio de ambos sentidos, "
               "meses, desfases, ventanas y semillas). Se interpreta como indicio, no como causa.")
    s = top.iloc[::-1]
    fig = go.Figure(go.Bar(x=s[orden], y=s.par, orientation="h", marker_color=COLOR_MODELO[mod],
                           customdata=s[["peso_vial", "limite_km"]],
                           hovertemplate="%{y}<br>%{x:.3f}<br>peso vial %{customdata[0]:.3f}; límite "
                                         "%{customdata[1]:.2f} km<extra></extra>"))
    layout(fig, alto=max(320, 28 * int(n) + 80), xaxis_title=ETIQ_ATENCION[orden], showlegend=False)
    fig.update_yaxes(tickfont=dict(size=10))
    figura(fig, "interp_pares", f"Pares de distritos con mayor {ETIQ_ATENCION[orden].lower()} en el "
                                f"{D.NOMBRES[mod]}.", alto_export=max(400, 28 * int(n) + 80))
    st.caption("Fuente: `atencion_espacial_pares_" + mod + ".csv`. Los pares con más atención media suelen ser de "
               "distritos con pocos vecinos (la atención se reparte entre menos entradas); la columna «Atención × "
               "grado» corrige ese efecto.")


# ---------------------------------------------------------------- fidelidad
def _fidelidad(v):
    st.subheader("Prueba de fidelidad de la atención (complementaria)")
    if D.aviso_cache_grafo(v):
        st.warning(AVISO_CACHE)
    f = D.atencion_fidelidad(v)
    if f is None:
        pendiente(f"no existe `atencion_fidelidad.csv` en {v.etiqueta}")
        return
    st.markdown("En cada corrida del GE se quitó el 10 % de las aristas con más atención y, aparte, el mismo número de "
                "aristas al azar; sin reentrenar. Si la atención señala aristas útiles, quitar las de más atención "
                "debería subir más el MAE.")
    g = f.groupby("ventana")[["MAE_base", "dMAE_top", "dMAE_azar"]].mean()
    t = pd.DataFrame({"Ventana": g.index, "MAE base": g.MAE_base.map(F.num), "ΔMAE sin las de más atención":
                      g.dMAE_top.map(F.num), "ΔMAE sin aristas al azar": g.dMAE_azar.map(F.num)}).reset_index(drop=True)
    dif = f.dMAE_top - f.dMAE_azar
    t.loc[len(t)] = ["Todas", F.num(f.MAE_base.mean()), F.num(f.dMAE_top.mean()), F.num(f.dMAE_azar.mean())]
    tabla(t, "interp_fidelidad", "Cambio del MAE al quitar las aristas con más atención o aristas al azar (GE)",
          nota=f"Nota. Elaboración propia. {len(f)} corridas del GE (4 ventanas × 5 semillas); "
               f"{int(f.aristas_quitadas.iloc[0])} aristas quitadas por corrida. ΔMAE en denuncias. En revisión por el "
               f"error de caché del grafo.")
    md = D.atencion_md(v)
    p = _md_num(md, r"Wilcoxon pareado: p = (\d+\.\d+)")
    st.markdown(f"Corridas en que quitar las aristas de más atención dañó más que el azar: **{int((dif > 0).sum())} de "
                f"{len(f)}**." + (f" Wilcoxon pareado (según `atencion.md`): p = {F.p_valor(float(p[0]))}." if p else
                                  " [PENDIENTE: p de Wilcoxon no encontrado en atencion.md]"))
    calculado("medias por ventana y conteo desde `atencion_fidelidad.csv`; el p se toma de `atencion.md`.")
    with st.expander("Corridas una por una"):
        st.dataframe(pd.DataFrame({"Ventana": f.ventana, "Semilla": f.semilla.map(str), "MAE base": f.MAE_base.map(F.num),
                                   "ΔMAE top": f.dMAE_top.map(F.num), "ΔMAE azar": f.dMAE_azar.map(F.num)}),
                     hide_index=True)
