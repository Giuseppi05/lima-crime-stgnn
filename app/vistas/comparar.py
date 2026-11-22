"""Pestaña Comparar versiones: MAE y RMSE por modelo lado a lado, diferencia y qué decidió la validación."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app import datos as D
from app import formato as F
from app.componentes import cita, pendiente, tabla


def _mae_validacion(v: D.Version) -> pd.Series | None:
    """MAE de validación medio por modelo (4 ventanas × 5 semillas) desde `corridas_neuronales.csv`."""
    c = D.corridas_neuronales(v)
    if c is None or "mae_validacion" not in c:
        return None
    return c[c.ventana.isin(D.VENTANAS_PRUEBA)].groupby("modelo").mae_validacion.mean()


def mostrar(versiones: list[D.Version], actual: D.Version) -> None:
    st.header("Comparar versiones")
    cita("versiones")
    if len(versiones) < 2:
        pendiente("solo hay una versión de resultados")
        return
    etiquetas = [v.etiqueta for v in versiones]
    i_b = etiquetas.index(actual.etiqueta)
    i_a = 0 if i_b != 0 else 1
    c1, c2 = st.columns(2)
    a = versiones[etiquetas.index(c1.selectbox("Versión A", etiquetas, index=i_a, key="cmp_a"))]
    b = versiones[etiquetas.index(c2.selectbox("Versión B", etiquetas, index=i_b, key="cmp_b"))]
    ga, gb = D.metricas_global(a), D.metricas_global(b)
    if ga is None or gb is None:
        for v, g in [(a, ga), (b, gb)]:
            if g is None:
                pendiente(f"no existe `metricas_global.csv` en {v.etiqueta}")
        return

    ga, gb = ga.set_index("modelo"), gb.set_index("modelo")
    modelos = [m for m in D.ORDEN if m in ga.index or m in gb.index]
    va, vb = _mae_validacion(a), _mae_validacion(b)
    na, nb = a.clave, b.clave
    filas = []
    for m in modelos:
        fila = {"Modelo": D.NOMBRES.get(m, m)}
        for met in ["MAE", "RMSE"]:
            x = ga[met].get(m)
            y = gb[met].get(m)
            fila[f"{met} {na}"] = F.num(x)
            fila[f"{met} {nb}"] = F.num(y)
            fila[f"Δ {met} ({nb} − {na})"] = F.num(y - x) if x is not None and y is not None else "—"
        if m in D.NEURONALES:
            if va is not None and vb is not None and m in va and m in vb:
                d = vb[m] - va[m]
                fila["MAE validación"] = f"{F.num(va[m])} → {F.num(vb[m])}"
                fila["Validación favorece"] = nb if d < 0 else na if d > 0 else "igual"
            else:
                faltan = [v.clave for v, s in [(a, va), (b, vb)] if s is None or m not in s]
                fila["MAE validación"] = f"[PENDIENTE: sin mae_validacion en {', '.join(faltan)}]"
                fila["Validación favorece"] = "—"
        else:
            fila["MAE validación"] = "XGBoost: ver yaml" if m == "xgboost" else "sin ajuste"
            fila["Validación favorece"] = "—"
        filas.append(fila)
    t = pd.DataFrame(filas)
    tabla(t, "comparar_global", f"MAE y RMSE en prueba por modelo, {na} frente a {nb}",
          nota="Nota. Elaboración propia. Media de 5 semillas en los modelos neuronales; MAE y RMSE en denuncias. "
               "La columna de validación compara el MAE de validación medio (4 ventanas × 5 semillas).")
    st.caption("«Validación favorece» compara solo el MAE de validación (de `corridas_neuronales.csv`); el de prueba "
               "se informa, pero no decide. Δ negativo = la versión B tiene menos error en prueba.")

    pa, pb = D.pruebas_estadisticas(a), D.pruebas_estadisticas(b)
    if pa is not None and pb is not None:
        st.subheader("Pruebas estadísticas en ambas versiones")
        m = pa.set_index("comparacion")[["p", "GE_supera"]].add_suffix("_a").join(
            pb.set_index("comparacion")[["p", "GE_supera"]].add_suffix("_b"), how="outer")
        t2 = pd.DataFrame({"Comparación": m.index, f"p {na}": m.p_a.map(F.p_valor), f"p {nb}": m.p_b.map(F.p_valor),
                           f"GE supera {na}": m.GE_supera_a.fillna("—"), f"GE supera {nb}": m.GE_supera_b.fillna("—")})
        tabla(t2, "comparar_pruebas", f"Pruebas estadísticas, {na} frente a {nb}")

    docs = D.comparaciones_md(a, b)
    st.subheader("Decisión documentada")
    relevantes = {k: txt for k, txt in docs.items()
                  if all(str(x).lower() in k.lower() for x in [na, nb] if not str(x).startswith("exp:"))}
    if relevantes:
        for k in relevantes:
            st.success(f"La comparación {na} – {nb} está documentada en `{k}` (elección solo con validación).", icon="📝")
    else:
        pendiente(f"no hay un `comparacion_*.md` que nombre {na} y {nb}")
    for k, txt in docs.items():
        with st.expander(f"Ver `{k}`"):
            st.markdown(txt)
