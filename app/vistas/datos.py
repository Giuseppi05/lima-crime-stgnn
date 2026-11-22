"""Pestaña 1. Datos (OE1): comprensión y preparación de los datos, validación de los grafos y configuración elegida
en el Modelado."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import datos as D
from app import formato as F
from app.componentes import (COLOR_MODELO, calculado, cita, figura, figura_archivo, layout, pendiente, tabla)


def mostrar(v: D.Version) -> None:
    st.header("Datos (OE1): comprensión y preparación")
    cita("comprension", "informe_resultados")
    _cobertura(v)
    _calidad(v)
    _figuras(v)
    _validacion_grafos(v)
    _solapamiento()
    _mapa()
    _modelado(v)


# ---------------------------------------------------------------- cobertura
def _cobertura(v):
    st.subheader("Cobertura del panel distrito × mes")
    p = D.panel()
    if p is None:
        pendiente("no existe `data/processed/panel.csv`")
        return
    c = D.cobertura(p)
    t = pd.DataFrame({"Estado": c.estado.map({"observado": "Observado", "cero": "Cero (sin hurto ni robo)",
                                              "sin_informacion": "Sin información"}),
                      "Celdas": c.celdas.map(F.entero), "%": c.pct.map(lambda x: F.num(x, 1))})
    t.loc[len(t)] = ["Total", F.entero(len(p)), F.num(100, 1)]
    st.markdown(f"Panel esperado: {p.ubigeo.nunique()} distritos × {p.periodo.nunique()} meses "
                f"({F.mes(p.periodo.min())} – {F.mes(p.periodo.max())}) = {F.entero(len(p))} celdas.")
    tabla(t, "datos_cobertura", "Cobertura del panel distrito × mes",
          nota="Nota. Elaboración propia. «Cero»: el distrito tiene denuncias de otras modalidades ese mes, pero ninguna "
               "de hurto ni robo (se usa como 0 real). «Sin información»: ninguna fila de ninguna modalidad; entra al "
               "modelo como 0 y se excluye de todas las métricas.")
    calculado("conteo de la columna `estado` de `data/processed/panel.csv`.")
    md = D.calidad_md(v)
    if md is not None:
        import re
        m = re.search(r"observado (\d+), cero (\d+), sin_informacion (\d+)", md)
        if m and [int(x) for x in m.groups()] == list(c.celdas):
            st.caption("✅ Coincide con «Estados del panel» de `calidad.md`.")
        elif m:
            st.error(f"No coincide con `calidad.md`: {m.group(0)}")
    cd = D.cobertura_por_distrito(p)
    meses_si = sorted(p[p.estado == "sin_informacion"].periodo.unique())
    t2 = pd.DataFrame({"Distrito": cd.distrito, "Meses en cero": cd.cero.map(str),
                       "Meses sin información": cd.sin_informacion.map(str)})
    tabla(t2, "datos_cobertura_distritos", "Distritos con meses en cero o sin información",
          nota="Nota. Elaboración propia. Meses sin información: " + ", ".join(F.mes(m) for m in meses_si) + ".")


# ---------------------------------------------------------------- calidad
def _calidad(v):
    st.subheader("Calidad de los datos")
    cita("panel_total")
    md = D.calidad_md(v)
    if md is None:
        pendiente(f"no existe `calidad.md` en {v.etiqueta}")
        return
    ver = D.tabla_md(md, "Verificaciones")
    if ver is not None:
        tabla(ver, "datos_calidad", "Verificaciones de calidad del registro y del panel")
    p = D.panel()
    if p is not None:
        total = int(p.objetivo.sum())
        dup = int(p.duplicated(["ubigeo", "periodo"]).sum())
        calculado(f"en `panel.csv`: {F.entero(len(p))} filas, {dup} duplicados distrito-mes, total hurto + robo "
                  f"{F.entero(total)} (hurto {F.entero(p.hurto.sum())}; robo {F.entero(p.robo.sum())}). El total "
                  f"antes de agregar solo está en `calidad.md` (el crudo no está en el repositorio).")
        if ver is not None and F.entero(total) not in " ".join(ver.iloc[:, 1]):
            st.error("El total del panel no coincide con `calidad.md`.")

    with st.expander("Diccionario de datos (archivo crudo)"):
        cita("diccionario")
        dic = D.tabla_md(md, "Diccionario de datos (archivo crudo)")
        if dic is None:
            pendiente("no hay diccionario de datos en `calidad.md`")
        else:
            tabla(dic, "datos_diccionario", "Diccionario de datos del registro de denuncias")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Atípicos**")
        st.markdown(D.decimal_es(D.seccion_md(md, "Atípicos") or "[PENDIENTE: sin sección de atípicos]"))
        st.markdown("**Distribución por celda observada**")
        st.markdown(D.decimal_es(D.seccion_md(md, "Distribución por celda observada") or "—"))
    with c2:
        st.markdown("**Quiebres**")
        st.markdown(D.decimal_es(D.seccion_md(md, "Quiebres") or "[PENDIENTE: sin sección de quiebres]"))
        st.markdown("**Concentración**")
        st.markdown(D.decimal_es(D.seccion_md(md, "Concentración desde 2022") or "—"))
    st.caption("El AVC3 menciona el quiebre de «marzo del 2020»; la ficha compara abril de 2020 con febrero de 2020. "
               "Queda en Pendientes del artículo.")


# ---------------------------------------------------------------- figuras de comprensión
def _figuras(v):
    st.subheader("Tendencia, estacionalidad y totales anuales")
    cita("tendencia")
    if v.figuras is None:
        pendiente(f"no hay carpeta de figuras para {v.etiqueta}")
        return
    md = D.calidad_md(v)
    tot = D.tabla_md(md, "Totales anuales") if md else None
    for nombre, clave, pie in [
        ("tendencia_mensual.png", "datos_tendencia", "Denuncias mensuales de hurto y robo en Lima Metropolitana, "
                                                     "enero de 2018 a septiembre de 2026."),
        ("estacionalidad.png", "datos_estacionalidad", "Estacionalidad mensual de las denuncias de hurto y robo."),
        ("totales_anuales.png", "datos_totales", "Totales anuales de denuncias de hurto y robo.")]:
        st.markdown(f"**{pie}**")
        figura_archivo(v.figuras / nombre, clave, pie)
        if clave == "datos_totales" and tot is not None:
            tabla(tot, "datos_totales_tabla", "Totales anuales de denuncias de hurto y robo")


# ---------------------------------------------------------------- validación de grafos
def _validacion_grafos(v):
    st.subheader("Validación de los grafos")
    cita("validaciones_grafos")
    nod, geo, vial = D.nodos(), D.aristas("geo"), D.aristas("vial")
    if nod is None or geo is None or vial is None:
        pendiente("faltan `nodos.csv` o `aristas_*.csv` en `data/processed/`")
        return
    ub = list(nod.ubigeo)
    rg, rv = D.resumen_grafo(geo, ub), D.resumen_grafo(vial, ub)
    dist = D.distancia_red_vs_recta(nod)
    md = D.validacion_grafos_md(v)
    filas = []
    for nombre, r in [("Geográfico (GC₂)", rg), ("Vial (GE)", rv)]:
        filas.append({"Grafo": nombre, "Nodos": str(len(ub)), "Aristas": str(r["aristas"]),
                      "Conectado": "sí" if r["conectado"] else "no", "Grado medio": F.num(r["grado_medio"], 2),
                      "Grado mín.": str(r["grado_min"]), "Grado máx.": str(r["grado_max"])})
    tabla(pd.DataFrame(filas), "datos_grafos", "Características de los grafos geográfico y vial",
          nota="Nota. Elaboración propia. Aristas no dirigidas entre los 43 distritos.")
    calculado("aristas, conexión (búsqueda en anchura) y grados desde `aristas_geo.csv` y `aristas_vial.csv`.")
    if md is not None:
        gmd = D.tabla_md(md, "Grafos")
        if gmd is not None:
            ok = list(gmd["Aristas"]) == [str(rg["aristas"]), str(rv["aristas"])]
            st.caption("✅ Coincide con `validacion_grafos.md`." if ok else "⚠️ No coincide con `validacion_grafos.md`.")

    rep = nod.punto.eq("representative_point")
    comp = [
        {"Comprobación": "Ubigeos del panel que cruzan con la capa INEI 2023",
         "Resultado": _extraer(md, r"cruzan con la capa INEI: (\d+ de \d+)"), "Fuente": "validacion_grafos.md"},
        {"Comprobación": "Puntos de nodo dentro de su polígono",
         "Resultado": _extraer(md, r"Puntos finales dentro de su polígono: (\d+ de \d+)"), "Fuente": "validacion_grafos.md"},
        {"Comprobación": "Centroides fuera del polígono reemplazados por un punto interior",
         "Resultado": f"{int(rep.sum())} ({', '.join(nod.distrito[rep])})", "Fuente": "nodos.csv (columna punto)"},
        {"Comprobación": "Grafo geográfico conectado", "Resultado": "sí" if rg["conectado"] else "no",
         "Fuente": "aristas_geo.csv"},
        {"Comprobación": "Grafo vial conectado", "Resultado": "sí" if rv["conectado"] else "no",
         "Fuente": "aristas_vial.csv"},
    ]
    if dist is not None:
        comp += [{"Comprobación": f"Pares con distancia por red menor que la recta (de {dist['pares']})",
                  "Resultado": str(dist["violaciones"]), "Fuente": "matriz_distancia_red_m.csv + nodos.csv"},
                 {"Comprobación": "Cociente red / recta: mínimo y mediana",
                  "Resultado": f"{F.num(dist['cociente_min'])} y {F.num(dist['cociente_mediana'])}",
                  "Fuente": "matriz_distancia_red_m.csv + nodos.csv"}]
    tabla(pd.DataFrame(comp), "datos_validacion_grafos", "Validaciones de los nodos y de los grafos")
    calculado("conexión, punto interior y distancia por red frente a la recta (entre los puntos UTM de `nodos.csv`) "
              "se recalculan aquí; la ubicación dentro del polígono se toma de `validacion_grafos.md`, porque los "
              "límites del INEI no están en esta PC.")
    if md is not None:
        with st.expander("Ver `validacion_grafos.md` (fuentes, red vial y aristas de mayor peso)"):
            st.markdown(D.decimal_es(md))


def _extraer(md, patron):
    import re
    if md is None:
        return "[PENDIENTE: sin validacion_grafos.md]"
    m = re.search(patron, md)
    return m.group(1) if m else "[PENDIENTE: no figura en validacion_grafos.md]"


# ---------------------------------------------------------------- solapamiento
def _solapamiento():
    st.subheader("Solapamiento entre el grafo vial (GE) y el geográfico (GC₂)")
    cita("dos_grafos")
    geo, vial, nod = D.aristas("geo"), D.aristas("vial"), D.nodos()
    if geo is None or vial is None:
        pendiente("faltan `aristas_geo.csv` o `aristas_vial.csv`")
        return
    s = D.solapamiento(geo, vial)
    t = pd.DataFrame({"Medida": ["Aristas del grafo geográfico (GC₂)", "Aristas del grafo vial (GE)",
                                 "Aristas comunes", "Solo en el geográfico", "Solo en el vial", "Unión",
                                 "Índice de Jaccard (comunes / unión)"],
                      "Valor": [str(s["geo"]), str(s["vial"]), str(s["comunes"]), str(s["solo_geo"]),
                                str(s["solo_vial"]), str(s["union"]), F.num(s["jaccard"])]})
    tabla(t, "datos_solapamiento", "Solapamiento de aristas entre el grafo vial y el geográfico",
          nota="Nota. Elaboración propia. Aristas no dirigidas; Jaccard = aristas comunes / aristas de la unión.")
    calculado("desde `aristas_geo.csv` y `aristas_vial.csv` (el Jaccard no figura en las fichas).")
    if s["solo_vial"] == 0:
        st.markdown(f"Todas las aristas viales son también geográficas (GE ⊂ GC₂). Los dos grafos difieren solo en "
                    f"{s['solo_geo']} pares contiguos sin tramo vial que cruce, y en los pesos de las aristas.")
    nombres = dict(zip(nod.ubigeo, nod.distrito)) if nod is not None else {}
    st.caption("Pares solo geográficos: " + "; ".join(f"{nombres.get(a, a)} – {nombres.get(b, b)}"
                                                      for a, b in s["pares_solo_geo"]) + ".")


# ---------------------------------------------------------------- mapa de nodos y aristas
def _mapa():
    st.subheader("Mapa de nodos y aristas")
    nod, geo, vial = D.nodos(), D.aristas("geo"), D.aristas("vial")
    if nod is None or geo is None or vial is None:
        pendiente("faltan `nodos.csv` o `aristas_*.csv`")
        return
    pos = {u: (x / 1000, y / 1000) for u, x, y in zip(nod.ubigeo, nod.x_utm, nod.y_utm)}
    pv = {tuple(sorted(k)): p for k, p in zip(zip(vial.origen, vial.destino), vial.peso)}
    fig = go.Figure()
    leyenda = {"comun": True, "geo": True}
    for o, d in sorted({tuple(sorted(k)) for k in zip(geo.origen, geo.destino)} | set(pv)):
        (x0, y0), (x1, y1) = pos[o], pos[d]
        if (o, d) in pv:
            w = pv[(o, d)]
            fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", name="GE y GC₂ (grosor = peso vial)",
                                     legendgroup="comun", showlegend=leyenda.pop("comun", False),
                                     line=dict(color=COLOR_MODELO["GE"], width=0.8 + 4.5 * w),
                                     hoverinfo="skip"))
        else:
            fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", name="Solo GC₂ (sin tramo vial)",
                                     legendgroup="geo", showlegend=leyenda.pop("geo", False),
                                     line=dict(color=COLOR_MODELO["GC2"], width=1.6, dash="dash"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=nod.x_utm / 1000, y=nod.y_utm / 1000, mode="markers", name="Nodo (distrito)",
                             marker=dict(size=8, color="#0b0b0b", line=dict(color="white", width=1.5)),
                             text=nod.distrito, customdata=nod.punto,
                             hovertemplate="%{text}<br>%{customdata}<extra></extra>"))
    layout(fig, alto=720)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    figura(fig, "datos_mapa_grafos", "Nodos (43 distritos) y aristas de los grafos vial y geográfico de Lima "
                                     "Metropolitana.", alto_export=900)
    st.caption("Posición de cada nodo: centroide del distrito en UTM 18 S (o punto interior en 2 distritos), de "
               "`nodos.csv`. Grosor: peso vial de `aristas_vial.csv`.")
    with st.expander("Figura del repositorio con los límites del INEI (`mapa_grafos.png`)"):
        figura_archivo(D.RESULTS / "figuras" / "mapa_grafos.png", "datos_mapa_grafos_repo",
                       "Revisión visual de los grafos sobre los límites distritales del INEI.")


# ---------------------------------------------------------------- modelado
def _modelado(v):
    st.subheader("Modelado (OE1): partición y configuración elegida con validación")
    cita("modelado")
    cfg = D.configuracion(v)
    if cfg is None:
        pendiente(f"no hay yaml de configuración para {v.etiqueta} (la v1 no guarda su `ventanas.yaml` en results/)")
        return
    vs = {**(cfg.get("ventanas") or {}), **(cfg.get("ventana_pandemia") or {})}
    t = pd.DataFrame([{"Ventana": str(w), "Entrenamiento": f"{F.mes(x['entrenamiento'][0])} – {F.mes(x['entrenamiento'][1])}",
                       "Validación": f"{F.mes(x['validacion'][0])} – {F.mes(x['validacion'][1])}",
                       "Prueba": f"{F.mes(x['prueba'][0])} – {F.mes(x['prueba'][1])}"} for w, x in vs.items()])
    tabla(t, "modelado_particion", "Partición cronológica en ventanas rodantes y ventana de pandemia (P)",
          nota=f"Nota. Elaboración propia. Semillas: {', '.join(map(str, cfg.get('semillas', [])))}. Horizonte: "
               f"{cfg.get('horizonte_meses', '—')} mes. Transformación: {cfg.get('transformacion', '—')}.")

    hp = cfg.get("hiperparametros") or {}
    filas = []
    for m in D.NEURONALES:
        for w, h in (hp.get(m) or {}).items():
            filas.append({"Modelo": D.NOMBRES[m], "Ventana": str(w), "Neuronas ocultas": str(h["oculto"]),
                          "Tasa de aprendizaje": F.num(h["lr"], 4), "Dropout": F.num(h["dropout"], 1),
                          "Meses de entrada (L)": str(h["entrada_meses"]),
                          "MAE de validación": F.num(h["mae_validacion"])})
    if filas:
        fij = cfg.get("fijos_neuronales") or {}
        tabla(pd.DataFrame(filas), "modelado_configuracion", "Configuración de los modelos neuronales elegida con "
                                                             "validación",
              nota=f"Nota. Elaboración propia. Fijos: {fij.get('optimizador', '—')}, weight decay "
                   f"{fij.get('weight_decay', '—')}, pérdida {fij.get('perdida', '—')}, hasta {fij.get('epocas_max', '—')} "
                   f"épocas, paciencia {fij.get('paciencia', '—')}, {fij.get('gat_heads', '—')} cabezas GAT, lote "
                   f"{fij.get('tam_lote', '—')}. MAE de validación de la semilla 0, en denuncias.")
    xg = hp.get("xgboost") or {}
    if xg:
        tx = pd.DataFrame([{"Ventana": str(w), "Profundidad máx.": str(h["max_depth"]),
                            "Tasa de aprendizaje": F.num(h["learning_rate"], 2), "Submuestreo": F.num(h["subsample"], 1),
                            "Peso mín. por hoja": str(h["min_child_weight"]), "Árboles": str(h["n_arboles"]),
                            "MAE de validación": F.num(h["mae_validacion"])} for w, h in xg.items()])
        tabla(tx, "modelado_xgboost", "Configuración de XGBoost elegida con validación")

    sal = cfg.get("salida_neuronal") or {}
    if sal:
        prom = sal.get("mae_validacion_promedio", {})
        st.markdown(f"**Salida de los modelos neuronales:** elegida **{sal.get('elegida', '—')}** por menor MAE de "
                    f"validación promedio (residual {F.num(prom.get('residual'))} frente a directa "
                    f"{F.num(prom.get('directa'))}), aplicada igual a GE, GC₂ y GC₁.")
    aj = D.ajuste_hiperparametros(v)
    if aj is None:
        pendiente(f"no existe `ajuste_hiperparametros.csv` en {v.etiqueta}; no se puede verificar la elección")
        return
    ver = D.verificar_configuracion(cfg, aj, sal.get("elegida", "residual"))
    prom_aj = D.eleccion_salida_desde_ajuste(aj)
    columnas_prueba = [c for c in aj.columns if c not in ("mae_validacion",) and
                       any(k in c.lower() for k in ("mae", "rmse", "r2", "prueba"))]
    if len(ver) and ver.coincide.all() and not columnas_prueba:
        st.success(f"Verificación: las {len(ver)} configuraciones neuronales del yaml son las de menor MAE de "
                   f"validación en `ajuste_hiperparametros.csv` ({ver.combinaciones.iloc[0]} combinaciones por modelo, "
                   f"ventana y salida), y ese archivo no tiene columnas de prueba. Recalculado desde la grilla: residual "
                   f"{F.num(prom_aj.get('residual'), 4)}, directa {F.num(prom_aj.get('directa'), 4)}.", icon="✅")
    else:
        st.error("La configuración del yaml no coincide con el mínimo de validación de la grilla en: " +
                 ", ".join(f"{r.modelo} {r.ventana}" for r in ver.itertuples() if not r.coincide) +
                 (f"; columnas de prueba en el ajuste: {columnas_prueba}" if columnas_prueba else ""))
    es = D.leer_texto(str(v.archivo("eleccion_salida.md")))
    if es is not None and "('GE', '1')" not in es and "('GE', 'P')" in es:
        st.warning("`eleccion_salida.md` solo muestra la ventana P (la corrida de pandemia lo sobrescribió); la elección "
                   "de las ventanas 1–4 está en el yaml y se recalcula arriba. Queda en Pendientes.")
