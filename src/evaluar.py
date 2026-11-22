"""Evaluación: métricas (OE2), pruebas estadísticas y equidad algorítmica (OE4).

Uso: python -m src.evaluar
Lee results/predicciones/ y escribe results/fichas/. Las celdas sin_informacion no entran en ninguna métrica.
"""
from __future__ import annotations

import argparse
import re

import numpy as np
import pandas as pd
from scipy import stats

from src.comun import FICHAS, PREDICCIONES, leer_config
from src.protocolo import H, cargar_datos, indices, ventanas

ALFA = 0.05
NEURONALES = ["GE", "GC1", "GC2"]
ORDEN = ["GE", "GC2", "GC1", "GE_ens", "GC2_ens", "GC1_ens", "xgboost", "mes_anterior", "promedio_movil_3",
         "mismo_mes_anio_anterior"]
NOMBRES = {"GE": "GE (ST-GNN vial)", "GC2": "GC₂ (ST-GNN geográfica)", "GC1": "GC₁ (GRU sin grafo)",
           "xgboost": "XGBoost", "mes_anterior": "Mes anterior", "promedio_movil_3": "Promedio móvil 3 meses",
           "mismo_mes_anio_anterior": "Mismo mes del año anterior"}
if H > 1:  # con horizonte H la referencia de persistencia es el último mes observado, no el mes anterior
    NOMBRES["mes_anterior"] = f"Último mes observado (t − {H})"
NOMBRES.update({f"{m}_ens": f"{NOMBRES[m]}, promedio de semillas" for m in NEURONALES})
ENSAMBLE = bool(leer_config().get("ensamble_semillas", False))
PLAYA = ["SANTA MARIA DEL MAR", "PUNTA NEGRA", "SAN BARTOLO", "PUCUSANA", "PUNTA HERMOSA"]


def cargar_predicciones(ventanas_ok=("1", "2", "3", "4")) -> pd.DataFrame:
    filas = []
    patron = re.compile(r"^(.+)_([0-9P]+)_(\d+)\.csv$")
    for f in sorted(PREDICCIONES.glob("*.csv")):
        m = patron.match(f.name)
        if not m or "_rapido" in f.name or m.group(2) not in ventanas_ok:
            continue
        t = pd.read_csv(f, dtype={"ubigeo": str})
        filas.append(t.assign(modelo=m.group(1), ventana=m.group(2), semilla=int(m.group(3))))
    p = pd.concat(filas, ignore_index=True)
    if ENSAMBLE:
        # opción extra: una sola predicción por modelo, el promedio de sus 5 semillas
        ens = (p[p.modelo.isin(NEURONALES)].groupby(["modelo", "ventana", "ubigeo", "periodo"], as_index=False)
               .agg(real=("real", "first"), predicho=("predicho", "mean"), valido=("valido", "first")))
        p = pd.concat([p, ens.assign(modelo=ens.modelo + "_ens", semilla=0)], ignore_index=True)
    return p[p["valido"]].copy()


def _met(g):
    e = g["predicho"] - g["real"]
    ss = ((g["real"] - g["real"].mean()) ** 2).sum()
    return pd.Series({"MAE": e.abs().mean(), "RMSE": np.sqrt((e ** 2).mean()), "R2": 1 - (e ** 2).sum() / ss})


def escala_mase(d, vs) -> dict:
    """MASE: denominador = MAE del 'mes anterior' dentro del entrenamiento de cada ventana (todos los distritos)."""
    esc = {}
    for w, v in vs.items():
        i = indices(d, v["entrenamiento"])[H:]
        ok = d.valido[i] & d.valido[i - H]
        esc[w] = np.abs(d.y[i] - d.y[i - H])[ok].mean()
    return esc


def media_de(t: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    """Media ± desviación entre semillas (las referencias deterministas tienen una sola corrida: desviación 0)."""
    g = t.groupby(por + ["semilla"]).mean(numeric_only=True).groupby(por)
    m, s = g.mean(), g.std(ddof=1).fillna(0.0)
    return m.join(s, rsuffix="_sd")


def formato_ms(df, cols, dec=2):
    out = pd.DataFrame(index=df.index)
    for c in cols:
        out[c] = df[c].round(dec).astype(str) + " ± " + df[f"{c}_sd"].round(dec).astype(str)
    return out


def comparar(a: np.ndarray, b: np.ndarray) -> dict:
    """Diferencias pareadas a − b: Shapiro-Wilk decide entre t pareada y Wilcoxon."""
    dif = a - b
    w, p_sw = stats.shapiro(dif)
    if p_sw > ALFA:
        prueba, r = "t pareada", stats.ttest_rel(a, b)
    else:
        prueba, r = "Wilcoxon", stats.wilcoxon(a, b)
    return {"media_dif": dif.mean(), "mediana_dif": np.median(dif), "shapiro_W": w, "shapiro_p": p_sw,
            "prueba": prueba, "estadistico": r.statistic, "p": r.pvalue,
            "distritos_GE_mejor": int((dif < 0).sum())}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rapido", action="store_true", help="lee y escribe en results_rapido/")
    ap.parse_args()
    d = cargar_datos()
    vs = ventanas()
    p = cargar_predicciones()
    modelos = [m for m in ORDEN if m in p.modelo.unique()]
    nom_d = dict(zip(d.ubigeos, d.distritos))
    md = []

    # ---------------- OE2: métricas global, por ventana y por distrito
    glob = p.groupby(["modelo", "semilla"]).apply(_met, include_groups=False).reset_index()
    vent = p.groupby(["modelo", "ventana", "semilla"]).apply(_met, include_groups=False).reset_index()
    esc = escala_mase(d, vs)
    vent["MASE"] = vent["MAE"] / vent["ventana"].map(esc)
    glob = glob.merge(vent.groupby(["modelo", "semilla"]).MASE.mean().reset_index(), on=["modelo", "semilla"])
    g_ms = media_de(glob.drop(columns="semilla").assign(semilla=glob.semilla), ["modelo"]).loc[modelos]
    v_ms = media_de(vent, ["modelo", "ventana"])
    g_ms.to_csv(FICHAS / "metricas_global.csv")
    v_ms.to_csv(FICHAS / "metricas_por_ventana.csv")

    dist = p.groupby(["modelo", "ventana", "semilla", "ubigeo"]).apply(_met, include_groups=False).reset_index()
    # por distrito: promedio entre ventanas y semillas (n = 43), base de las pruebas estadísticas
    dmed = dist.groupby(["modelo", "ubigeo"])[["MAE", "RMSE"]].mean().reset_index()
    dmed["distrito"] = dmed.ubigeo.map(nom_d)
    dmed.to_csv(FICHAS / "metricas_por_distrito.csv", index=False)

    md += ["# Evaluación: desempeño predictivo (OE2), pruebas estadísticas y equidad (OE4)\n",
           "Generado por `python -m src.evaluar`. Métricas en número de denuncias; se excluyen las 9 celdas sin información. "
           "Media ± desviación estándar entre las 5 semillas (las referencias y XGBoost son deterministas: una corrida). "
           "Nota. Elaboración propia.\n",
           "## Métricas globales (4 ventanas de prueba, 48 meses × 43 distritos)\n",
           formato_ms(g_ms, ["MAE", "RMSE", "R2", "MASE"], 3).rename(index=NOMBRES).to_markdown(), "\n",
           "MASE (complementaria): MAE del modelo entre el MAE del 'mes anterior' dentro del entrenamiento de cada ventana; "
           "promedio de las 4 ventanas.\n",
           "## Métricas por ventana\n"]
    for met in ["MAE", "RMSE", "R2"]:
        t = formato_ms(v_ms, [met], 3)[met].unstack("ventana").loc[modelos].rename(index=NOMBRES)
        md += [f"### {met}\n", t.to_markdown(), ""]

    # ---------------- Estadística
    piv_mae = dmed.pivot(index="ubigeo", columns="modelo", values="MAE")
    piv_rmse = dmed.pivot(index="ubigeo", columns="modelo", values="RMSE")
    filas = []
    pares = [("GE", "GC1", "AVC3"), ("GE", "GC2", "AVC3"), ("GE", "xgboost", "complementaria"),
             ("GE", "mes_anterior", "complementaria")]
    if ENSAMBLE:
        pares += [("GE_ens", "GC1_ens", "extra"), ("GE_ens", "GC2_ens", "extra"), ("GE_ens", "mes_anterior", "extra")]
    for a_, rival, tipo in pares:
        if rival not in piv_mae or a_ not in piv_mae:
            continue
        c = comparar(piv_mae[a_].values, piv_mae[rival].values)
        c_r = comparar(piv_rmse[a_].values, piv_rmse[rival].values)
        mae_ok = g_ms.loc[a_, "MAE"] < g_ms.loc[rival, "MAE"]
        rmse_ok = g_ms.loc[a_, "RMSE"] < g_ms.loc[rival, "RMSE"]
        exito = mae_ok and rmse_ok and c["p"] < ALFA
        filas.append({"comparacion": f"{a_} vs {rival}", "tipo": tipo, "MAE_GE": g_ms.loc[a_, "MAE"],
                      f"MAE_rival": g_ms.loc[rival, "MAE"], "RMSE_GE": g_ms.loc[a_, "RMSE"],
                      "RMSE_rival": g_ms.loc[rival, "RMSE"], **c, "p_RMSE_distrito": c_r["p"],
                      "menor_MAE_por_distrito": a_ if c["media_dif"] < 0 else rival,
                      "prueba_RMSE": c_r["prueba"], "GE_supera": "sí" if exito else "no"})
    est = pd.DataFrame(filas)
    est.to_csv(FICHAS / "pruebas_estadisticas.csv", index=False)
    md += ["## Pruebas estadísticas (n = 43 distritos; MAE por distrito promediado entre ventanas y semillas)\n",
           "Regla de éxito del AVC3: el GE supera a un GC si tiene MAE **y** RMSE globales menores y la diferencia del "
           "MAE por distrito es significativa (α = 0,05). La prueba (t pareada o Wilcoxon) se eligió con Shapiro-Wilk "
           "sobre las diferencias pareadas. Como apoyo se repitió la prueba sobre el RMSE por distrito.\n",
           est.round(4).to_markdown(index=False), ""]

    # ---------------- OE4: equidad
    vol = {}
    for w, v in vs.items():
        i = indices(d, v["entrenamiento"])
        vol[w] = pd.Series(np.nanmean(np.where(d.valido[i], d.y[i], np.nan), 0), index=d.ubigeos)
    vol_ent = pd.concat(vol, axis=1).mean(1)  # volumen mensual medio en entrenamiento, promedio de las 4 ventanas
    sector = pd.qcut(vol_ent.rank(method="first"), 3, labels=["bajo", "medio", "alto"])
    estab = pd.concat({w: pd.qcut(s.rank(method="first"), 3, labels=["bajo", "medio", "alto"]) for w, s in vol.items()}, axis=1)
    cambian = int((estab.nunique(axis=1) > 1).sum())

    # error relativo: MAE del distrito / promedio de denuncias del distrito en prueba (por ventana), promedio entre ventanas y semillas
    prom = p[p.modelo == p.modelo.iloc[0]].drop_duplicates(["ubigeo", "periodo"]).groupby(["ventana", "ubigeo"]).real.mean()
    dr = dist.merge(prom.rename("media_real").reset_index(), on=["ventana", "ubigeo"])
    dr["error_rel"] = dr.MAE / dr.media_real
    er = dr.groupby(["modelo", "ubigeo"]).error_rel.mean().reset_index()
    er["distrito"] = er.ubigeo.map(nom_d)
    er["sector"] = er.ubigeo.map(sector)
    er["volumen_entrenamiento"] = er.ubigeo.map(vol_ent).round(1)
    er.to_csv(FICHAS / "equidad_por_distrito.csv", index=False)

    eq, kw = [], []
    for m in modelos:
        e = er[er.modelo == m]
        e_np = e[~e.distrito.isin(PLAYA)]
        eq.append({"modelo": NOMBRES[m], "error_rel_mediana": e.error_rel.median(),
                   "min": e.error_rel.min(), "distrito_min": e.loc[e.error_rel.idxmin(), "distrito"],
                   "max": e.error_rel.max(), "distrito_max": e.loc[e.error_rel.idxmax(), "distrito"],
                   "brecha": e.error_rel.max() - e.error_rel.min(),
                   "brecha_sin_playa": e_np.error_rel.max() - e_np.error_rel.min(),
                   **{f"media_{s}": e[e.sector == s].error_rel.mean() for s in ["bajo", "medio", "alto"]}})
        grupos = [e[e.sector == s].error_rel.values for s in ["bajo", "medio", "alto"]]
        normal = all(stats.shapiro(g)[1] > ALFA for g in grupos) and stats.levene(*grupos)[1] > ALFA
        r = stats.f_oneway(*grupos) if normal else stats.kruskal(*grupos)
        kw.append({"modelo": NOMBRES[m], "prueba": "ANOVA" if normal else "Kruskal-Wallis",
                   "estadistico": r.statistic, "p": r.pvalue, "significativa": "sí" if r.pvalue < ALFA else "no"})
    eq, kw = pd.DataFrame(eq), pd.DataFrame(kw)
    eq.to_csv(FICHAS / "equidad_resumen.csv", index=False)
    kw.to_csv(FICHAS / "equidad_sectores.csv", index=False)
    playa = er[er.distrito.isin(PLAYA)].pivot(index="distrito", columns="modelo", values="error_rel")[modelos]
    sect = er[er.modelo == "GE"].groupby("sector", observed=True).distrito.apply(lambda s: ", ".join(sorted(s)))
    md += ["## Equidad algorítmica (OE4)\n",
           "Error relativo del distrito = MAE del distrito / promedio de denuncias del distrito en la prueba, por ventana; "
           "luego promedio entre ventanas y semillas. Brecha = máximo − mínimo. Sectores = terciles de distritos según su "
           f"volumen mensual medio de denuncias en entrenamiento (promedio de las 4 ventanas). {cambian} distritos cambiarían "
           "de tercil si se usara el entrenamiento de una sola ventana.\n",
           eq.round(3).to_markdown(index=False), "",
           "### Diferencias entre sectores\n",
           "ANOVA si los tres grupos pasan Shapiro-Wilk y Levene; si no, Kruskal-Wallis (α = 0,05).\n",
           kw.round(4).to_markdown(index=False), "",
           "### Composición de los sectores\n", sect.to_frame("distritos").to_markdown(), "",
           "### Distritos de bajo volumen (playa), error relativo\n",
           playa.rename(columns=NOMBRES).round(3).to_markdown(), "",
           "Los distritos de playa tienen pocas denuncias por mes; un error de pocas denuncias se vuelve un error relativo "
           "grande. Por eso la brecha se informa también sin ellos.\n"]
    (FICHAS / "evaluacion.md").write_text("\n".join(md), encoding="utf-8")
    print(formato_ms(g_ms, ["MAE", "RMSE", "R2", "MASE"], 3).to_string())
    print(est[["comparacion", "prueba", "p", "GE_supera"]].to_string(index=False))


if __name__ == "__main__":
    main()
