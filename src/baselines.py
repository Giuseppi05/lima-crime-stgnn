"""Modelado: referencias simples (mes anterior, mismo mes del año anterior, promedio móvil de 3 meses) y XGBoost.

Uso: python -m src.baselines [--rapido] [--pandemia]
"""
from __future__ import annotations

import argparse
import itertools
import json

import numpy as np
import pandas as pd
import xgboost as xgb

from src.comun import FICHAS, PREDICCIONES, fijar_semilla, guardar_config, leer_config
from src.protocolo import COLUMNAS_MODALIDADES, H, Datos, Transformacion, cargar_datos, indices, metricas, tabla_predicciones, ventanas

REZAGOS = [1, 2, 3, 6, 12]


def referencias(d: Datos, idx: np.ndarray) -> dict[str, np.ndarray]:
    """Solo usan meses hasta t − H. Con H > 1, 'mes_anterior' es el último mes observado (t − H)."""
    return {
        "mes_anterior": d.y[idx - H],
        "mismo_mes_anio_anterior": d.y[idx - 12],
        "promedio_movil_3": np.mean([d.y[idx - H - k] for k in (0, 1, 2)], axis=0),
    }


def rasgos(d: Datos, z: np.ndarray, idx: np.ndarray, zx: np.ndarray | None = None) -> pd.DataFrame:
    """Una fila por (mes objetivo, distrito); todo rasgo sale de meses ≤ t − H salvo el calendario y la pandemia."""
    n = len(d.ubigeos)
    s = H - 1  # con H = 1 el rezago k es t − k, como en el AVC3
    filas = {}
    for k in REZAGOS:
        filas[f"rezago_{k}"] = z[idx - s - k].ravel()
    filas["media_3"] = np.mean([z[idx - s - k] for k in range(1, 4)], axis=0).ravel()
    filas["media_12"] = np.mean([z[idx - s - k] for k in range(1, 13)], axis=0).ravel()
    if zx is not None:  # las modalidades entran igual que en la ST-GNN: último mes observado y media de 3 meses
        for j, c in enumerate(COLUMNAS_MODALIDADES):
            filas[f"{c}_rezago_1"] = zx[idx - s - 1, :, j].ravel()
            filas[f"{c}_media_3"] = np.mean([zx[idx - s - k, :, j] for k in range(1, 4)], axis=0).ravel()
    mes = np.repeat(d.mes[idx], n)
    filas["mes_sin"] = np.sin(2 * np.pi * mes / 12)
    filas["mes_cos"] = np.cos(2 * np.pi * mes / 12)
    filas["distrito"] = pd.Categorical(np.tile(np.arange(n), len(idx)), categories=range(n))
    filas["pandemia"] = np.repeat(d.pandemia[idx], n)
    return pd.DataFrame(filas)


def xgboost_ventana(d: Datos, v: dict, rapido: bool, semilla: int = 0):
    cfg = leer_config()
    i_tr, i_va, i_te = (indices(d, v[k]) for k in ("entrenamiento", "validacion", "prueba"))
    tr = Transformacion(d, i_tr)
    z = tr.directa(d.y)
    zx = tr.directa_extra(d.extra) if d.extra is not None else None
    i_tr = i_tr[i_tr >= 12 + H - 1]  # los rezagos de 12 meses exigen un año previo
    X_tr, X_va, X_te = (rasgos(d, z, i, zx) for i in (i_tr, i_va, i_te))
    y_tr, y_va = z[i_tr].ravel(), z[i_va].ravel()
    m_tr, m_va = d.valido[i_tr].ravel(), d.valido[i_va].ravel()

    g = cfg["grilla_xgboost"]
    combos = [dict(zip(g, c)) for c in itertools.product(*g.values())]
    if rapido:
        combos = combos[:1]
    fx = cfg["fijos_xgboost"]
    mejor = None
    for c in combos:
        mod = xgb.XGBRegressor(
            n_estimators=fx["n_estimators_max"] if not rapido else 50,
            early_stopping_rounds=fx["early_stopping_rounds"], colsample_bytree=fx["colsample_bytree"],
            reg_lambda=fx["reg_lambda"], objective="reg:pseudohubererror", eval_metric="mae",
            tree_method="hist", enable_categorical=True, random_state=semilla, n_jobs=1, **c)
        mod.fit(X_tr[m_tr], y_tr[m_tr], eval_set=[(X_va[m_va], y_va[m_va])], verbose=False)
        p_va = tr.inversa(mod.predict(X_va).reshape(len(i_va), -1))
        mae = metricas(d.y[i_va][d.valido[i_va]], p_va[d.valido[i_va]])["MAE"]
        if mejor is None or mae < mejor[0]:
            mejor = (mae, c, mod)
    mae_va, c, mod = mejor
    p_te = tr.inversa(mod.predict(X_te).reshape(len(i_te), -1))
    return p_te, i_te, {**c, "n_arboles": int(mod.best_iteration) + 1, "mae_validacion": round(mae_va, 4)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rapido", action="store_true", help="1 ventana, 1 configuración: solo prueba de humo")
    ap.add_argument("--pandemia", action="store_true", help="incluye la ventana adversa de pandemia")
    a = ap.parse_args()
    fijar_semilla(0)
    d = cargar_datos()
    vs = ventanas(incluir_pandemia=a.pandemia)
    if a.rapido:
        vs = {"1": vs["1"]}
    resumen, elegidos = [], {}
    for w, v in vs.items():
        i_te = indices(d, v["prueba"])
        for nombre, p in referencias(d, i_te).items():
            tabla_predicciones(d, i_te, p).to_csv(PREDICCIONES / f"{nombre}_{w}_0.csv", index=False)
            resumen.append({"modelo": nombre, "ventana": w, **metricas(d.y[i_te][d.valido[i_te]], p[d.valido[i_te]])})
        p, i_te, conf = xgboost_ventana(d, v, a.rapido)
        tabla_predicciones(d, i_te, p).to_csv(PREDICCIONES / f"xgboost_{w}_0.csv", index=False)
        resumen.append({"modelo": "xgboost", "ventana": w, **metricas(d.y[i_te][d.valido[i_te]], p[d.valido[i_te]])})
        elegidos[w] = conf
        print(f"ventana {w}: xgboost {conf}")
    r = pd.DataFrame(resumen)
    print(r.round(3).to_string(index=False))
    if not a.rapido:
        cfg = leer_config()
        cfg.setdefault("hiperparametros", {}).setdefault("xgboost", {}).update(
            {k: json.loads(json.dumps(v)) for k, v in elegidos.items()})
        guardar_config(cfg)
        r.to_csv(FICHAS / f"metricas_referencias{'_pandemia' if a.pandemia else ''}.csv", index=False)


if __name__ == "__main__":
    main()
