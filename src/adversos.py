"""Evaluación: casos adversos sobre el GE ya entrenado (sin reentrenar) y resumen de la ventana de pandemia.

Uso: python -m src.adversos [--rapido]
- Aristas: se elimina al azar el 10, 20 y 30 % de las aristas del grafo vial.
- Coordenadas: ruido gaussiano de σ = 500 y 1 000 m en los centroides; se reconstruye el grafo vial (distancias por red).
- Meses faltantes: se enmascara al azar el 10 % de las celdas distrito-mes de entrada y se rellenan con el valor anterior.
- Pandemia: la ventana P (entrenada aparte con src.baselines --pandemia y src.entrenar --pandemia) se resume aquí.
Que algunos casos empeoren el error es lo esperado: se reporta tal cual.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from src.comun import FICHAS, PROCESADOS
from src.entrenar import cargar_entrenado, predecir_con
from src.evaluar import NOMBRES, ORDEN, cargar_predicciones
from src.protocolo import cargar_datos, metricas

SORTEOS = 5
FRACCIONES_ARISTAS = [0.10, 0.20, 0.30]
SIGMAS_M = [500, 1000]
FRACCION_MESES = 0.10


def matriz_vial() -> np.ndarray:
    return pd.read_csv(PROCESADOS / "matriz_vial.csv", index_col=0).to_numpy(float)


def quitar_aristas(A, frac, rng):
    B = A.copy()
    i, j = np.nonzero(np.triu(B, 1))
    k = int(round(frac * len(i)))
    sel = rng.choice(len(i), k, replace=False)
    B[i[sel], j[sel]] = B[j[sel], i[sel]] = 0
    return B


def enmascarar_meses(d, i_te, L, frac, rng):
    """Celdas de entrada (meses previos a cada mes de prueba) enmascaradas y rellenadas con el valor anterior."""
    y = d.y.copy()
    ini, fin = i_te[0] - L, i_te[-1]  # meses que pueden entrar como insumo de la prueba
    T, N = fin - ini, y.shape[1]
    mask = rng.random((T, N)) < frac
    for t in range(T):
        for n in np.nonzero(mask[t])[0]:
            y[ini + t, n] = y[ini + t - 1, n]  # en orden: si el anterior también falta, arrastra el ya rellenado
    return y, int(mask.sum()), T * N


def grafos_ruido(sigmas, sorteos, rng):
    """Reconstruye el grafo vial con centroides desplazados; los tramos que cruzan no dependen del centroide."""
    import osmnx as ox

    from src.grafos import cargar_limites, construir_vial, descargar_red

    lim, _ = cargar_limites()
    G, _ = descargar_red(lim)
    Gu = ox.convert.to_undirected(G)
    nodos = pd.read_csv(PROCESADOS / "nodos.csv", dtype={"ubigeo": str})
    xy = nodos[["x_utm", "y_utm"]].to_numpy()
    cruces = pd.read_csv(PROCESADOS / "matriz_tramos_cruce.csv", index_col=0).to_numpy()
    salida = {}
    for s in sigmas:
        for k in range(sorteos):
            xy_r = xy + rng.normal(0, s, xy.shape)
            w, *_ = construir_vial(Gu, None, xy_r, len(xy), cruces=cruces)
            salida[(s, k)] = w
    return salida


def cambio_pesos(ruido, A) -> pd.DataFrame:
    m = A > 0
    return pd.DataFrame([{"sigma_m": s, "sorteo": k, "cambio_abs_medio_peso": float(np.abs(W - A)[m].mean()),
                          "cambio_abs_max_peso": float(np.abs(W - A)[m].max())} for (s, k), W in ruido.items()])


def _coma(x: float, nd: int) -> str:
    return f"{x:.{nd}f}".replace(".", ",")


def detalle_grafo(r: pd.DataFrame, cp: pd.DataFrame) -> str:
    """Párrafo con 4 decimales para los casos de grafo, cuyo cambio redondea a 0 con 3 decimales.

    `r` tiene una fila por corrida y caso, con `MAE`, `MAE_limpio` y `dMAE_%`; `cp` es la salida de `cambio_pesos`.
    Los sorteos repetidos (mismo MAE exacto con aristas distintas) eran la huella del error de caché del grafo.
    """
    limpio = r[r.caso == "limpio"].MAE.mean()
    ru = r[r.caso == "ruido en coordenadas"]
    partes = [f"**Casos de grafo, con 4 decimales.** MAE limpio {_coma(limpio, 4)}"]
    if len(ru):
        por_nivel = ru.groupby("nivel", sort=False).MAE.mean()
        partes[0] += "; " + "; ".join(f"con {n}, {_coma(x, 4)}" for n, x in por_nivel.items()) + "."
        pesos = cp.groupby("sigma_m").cambio_abs_medio_peso.mean()
        partes.append(
            f"Ruido en coordenadas: el cambio del MAE es < 0,01 % en {int((ru['dMAE_%'].abs() < 0.01).sum())} de "
            f"{len(ru)} corridas (máximo en valor absoluto {_coma(ru['dMAE_%'].abs().max(), 4)} %), y "
            f"{int((ru.MAE == ru.MAE_limpio).sum())} dieron un MAE idéntico al limpio. Cambio absoluto medio de los "
            "pesos: " + "; ".join(f"{_coma(x, 4)} con σ = {s} m" for s, x in pesos.items()) + ".")
    ar = r[r.caso == "aristas eliminadas"]
    if len(ar):
        rep = ar.groupby(["nivel", "ventana", "semilla"], sort=False).MAE.agg(lambda x: x.nunique() < len(x))
        rep = rep.groupby(level="nivel", sort=False).agg(["sum", "size"])
        partes.append("Aristas eliminadas: corridas con dos sorteos o más de igual MAE, " + "; ".join(
            f"{n}: {int(t['sum'])} de {int(t['size'])}" for n, t in rep.iterrows()) + ".")
    return " ".join(partes) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rapido", action="store_true")
    a = ap.parse_args()
    d = cargar_datos()
    rng = np.random.default_rng(0)
    A = matriz_vial()
    corridas = [(w, s) for w in ["1", "2", "3", "4"] for s in range(5)]
    sorteos, sigmas = SORTEOS, SIGMAS_M
    if a.rapido:
        corridas, sorteos, sigmas = [("1", 0)], 1, [500]
    ruido = grafos_ruido(sigmas, sorteos, rng)
    cp = cambio_pesos(ruido, A)
    print(cp.groupby("sigma_m")[["cambio_abs_medio_peso", "cambio_abs_max_peso"]].mean().round(4).to_string())
    filas = []
    for w, s in corridas:
        m, tr, L, i_te = cargar_entrenado(d, "GE", w, s)
        ok = d.valido[i_te]
        real = d.y[i_te][ok]

        def reg(caso, nivel, p, sorteo=0):
            filas.append({"ventana": w, "semilla": s, "caso": caso, "nivel": nivel, "sorteo": sorteo,
                          **metricas(real, p[ok])})

        reg("limpio", "-", predecir_con(m, d, tr, L, i_te, A))
        for f in FRACCIONES_ARISTAS:
            for k in range(sorteos):
                reg("aristas eliminadas", f"{int(f*100)} %", predecir_con(m, d, tr, L, i_te, quitar_aristas(A, f, rng)), k)
        for (sg, k), W in ruido.items():
            reg("ruido en coordenadas", f"σ = {sg} m", predecir_con(m, d, tr, L, i_te, W), k)
        for k in range(sorteos):
            y_m, n_m, n_tot = enmascarar_meses(d, i_te, L, FRACCION_MESES, rng)
            reg("meses faltantes", f"{int(FRACCION_MESES*100)} %", predecir_con(m, d, tr, L, i_te, A, y_entrada=y_m), k)
        print(f"ventana {w} semilla {s} listo", flush=True)
    r = pd.DataFrame(filas)
    if a.rapido:
        print(r.groupby(["caso", "nivel"])[["MAE", "RMSE", "R2"]].mean().round(3))
        return
    r.to_csv(FICHAS / "casos_adversos.csv", index=False)
    base = r[r.caso == "limpio"].set_index(["ventana", "semilla"])[["MAE", "RMSE"]]
    r = r.join(base, on=["ventana", "semilla"], rsuffix="_limpio")
    r["dMAE_%"] = (r.MAE / r.MAE_limpio - 1) * 100
    res = r.groupby(["caso", "nivel"], sort=False).agg(
        MAE=("MAE", "mean"), MAE_sd=("MAE", "std"), RMSE=("RMSE", "mean"), R2=("R2", "mean"),
        cambio_MAE_pct=("dMAE_%", "mean"), corridas_peor=("dMAE_%", lambda x: int((x > 0).sum())), n=("MAE", "size"))
    md = ["# Evaluación: casos adversos\n",
          "Generado por `python -m src.adversos`. GE ya entrenado (4 ventanas × 5 semillas), sin reentrenar; "
          f"{SORTEOS} sorteos por nivel. Métricas en la prueba, en denuncias. Nota. Elaboración propia.\n",
          res.round(3).to_markdown(), "",
          "`cambio_MAE_pct`: cambio porcentual medio del MAE frente al mismo modelo con datos limpios. "
          "`corridas_peor`: casos en que el MAE subió.\n",
          detalle_grafo(r, cp),
          "### Cambio en los pesos del grafo vial por el ruido en coordenadas\n",
          "Los tramos que cruzan dependen de los límites y no del centroide, así que el ruido solo cambia la distancia por "
          "red y, con ella, el peso; el conjunto de aristas no cambia.\n",
          cp.groupby("sigma_m")[["cambio_abs_medio_peso", "cambio_abs_max_peso"]].mean().round(4).to_markdown(), ""]
    # ventana de pandemia, si ya se entrenó
    try:
        pp = cargar_predicciones(ventanas_ok=("P",))
        g = pp.groupby(["modelo", "semilla"]).apply(lambda t: pd.Series(metricas(t.real, t.predicho)), include_groups=False)
        g = g.groupby("modelo").agg(["mean", "std"]).round(3)
        g = g.loc[[m for m in ORDEN if m in g.index]].rename(index=NOMBRES)
        g.to_csv(FICHAS / "pandemia.csv")
        md += ["## Pandemia (ventana P)\n",
               "Entrenamiento 2018-01 – 2019-09, validación 2019-10 – 2020-03, prueba 2020-04 – 2021-03; todos los modelos "
               "reentrenados y ajustados con su propia validación. Media y desviación entre semillas.\n",
               g.to_markdown(), ""]
    except (ValueError, KeyError):
        md += ["## Pandemia (ventana P)\n", "Aún sin corridas de la ventana P.\n"]
    (FICHAS / "casos_adversos.md").write_text("\n".join(md), encoding="utf-8")
    print(res.round(3).to_string())


if __name__ == "__main__":
    main()
