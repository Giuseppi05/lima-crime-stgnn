"""Evaluación (complementaria): diagnóstico de dependencia espacial en las denuncias a escala distrito-mes.

Uso: python -m src.diagnostico
Pregunta: ¿hay señal espacial que una GNN pueda aprovechar? Se mide sobre los datos, no sobre un modelo:
1. I de Moran mensual del nivel (log1p) y del cambio mensual (Δlog), con los dos grafos y prueba por permutación.
2. Parte del cambio mensual que es común a toda la ciudad.
3. Si el cambio de los vecinos en t−1 ayuda a predecir el cambio propio en t, fuera de muestra, en las 4 ventanas.
"""
from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.comun import FICHAS, FIGURAS, PROCESADOS
from src.protocolo import cargar_datos, indices, ventanas

PERMUTACIONES = 999
ALFA = 0.05
GRAFOS = {"geo": "geográfico (GC₂)", "vial": "vial (GE)"}


def pesos(nombre: str) -> np.ndarray:
    m = (pd.read_csv(PROCESADOS / f"matriz_{nombre}.csv", index_col=0).to_numpy(float) > 0).astype(float)
    return m / m.sum(1, keepdims=True)  # estandarizada por filas: promedio de los vecinos


def moran(z: np.ndarray, w: np.ndarray) -> float:
    z = z - z.mean()
    return len(z) / w.sum() * (z @ w @ z) / (z @ z)


def moran_perm(z: np.ndarray, w: np.ndarray, rng) -> tuple[float, float]:
    """I observado y p a dos colas por permutación de los distritos."""
    obs = moran(z, w)
    zc = z - z.mean()
    perm = np.array([rng.permutation(zc) for _ in range(PERMUTACIONES)])
    nul = len(z) / w.sum() * np.einsum("pi,ij,pj->p", perm, w, perm) / (zc @ zc)
    p = (np.sum(np.abs(nul - nul.mean()) >= abs(obs - nul.mean())) + 1) / (PERMUTACIONES + 1)
    return obs, p


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    rng = np.random.default_rng(0)
    d = cargar_datos()
    ly = np.log1p(d.y)
    dly = np.diff(ly, axis=0)
    per = np.array(d.periodos)
    N = ly.shape[1]
    md = ["# Evaluación (complementaria): diagnóstico de dependencia espacial\n",
          "Generado por `python -m src.diagnostico`. Se analizan los datos, no un modelo. Matrices de pesos estandarizadas "
          f"por filas; prueba de Moran por permutación ({PERMUTACIONES} permutaciones, dos colas, α = 0,05). "
          f"Valor esperado de I sin dependencia: −1/(n−1) = {-1/(N-1):.3f}. Nota. Elaboración propia.\n"]

    # ---------------- 1. Moran mensual
    filas, serie = [], {}
    for g in GRAFOS:
        w = pesos(g)
        for var, X, pp in [("nivel log1p", ly, per), ("cambio mensual Δlog", dly, per[1:])]:
            res = np.array([moran_perm(X[t], w, rng) for t in range(len(X))])
            serie[(g, var)] = pd.Series(res[:, 0], index=pp)
            for tramo, sel in [("2018-02 – 2026-09", np.ones(len(pp), bool)), ("2022-01 – 2026-09", pp >= "2022-01")]:
                filas.append({"grafo": GRAFOS[g], "variable": var, "periodo": tramo, "I_media": res[sel, 0].mean(),
                              "meses": int(sel.sum()), "meses_significativos": int((res[sel, 1] < ALFA).sum()),
                              "meses_sig_positivos": int(((res[sel, 1] < ALFA) & (res[sel, 0] > 0)).sum())})
    mo = pd.DataFrame(filas)
    mo.to_csv(FICHAS / "diagnostico_moran.csv", index=False)
    md += ["## 1. Autocorrelación espacial mensual (I de Moran)\n",
           "El nivel mide si los distritos con muchas denuncias están junto a otros con muchas. El cambio mensual mide si, "
           "cuando un distrito sube o baja respecto del mes anterior, sus vecinos se mueven igual: es la parte que el "
           "'mes anterior' no predice y la única que un grafo podría aportar.\n",
           mo.round(3).to_markdown(index=False), ""]

    fig, ax = plt.subplots(figsize=(10, 4))
    for g, col in [("geo", "#2e75b6"), ("vial", "#c55a11")]:
        s = serie[(g, "cambio mensual Δlog")]
        ax.plot(pd.PeriodIndex(s.index, freq="M").to_timestamp(), s.values, color=col, lw=1, label=f"Δlog, grafo {GRAFOS[g]}")
    ax.axhline(-1 / (N - 1), color="gray", ls="--", lw=.8, label="esperado sin dependencia")
    ax.set_ylabel("I de Moran")
    ax.set_title("Autocorrelación espacial del cambio mensual de hurto + robo")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURAS / "diagnostico_moran.png", dpi=150)
    plt.close(fig)

    # ---------------- 2. choque común
    ok = d.valido[1:] & d.valido[:-1]
    dl = np.where(ok, dly, np.nan)
    com = np.nanmean(dl, axis=1, keepdims=True)
    r2 = lambda sel: 1 - np.nansum((dl[sel] - com[sel]) ** 2) / np.nansum((dl[sel] - np.nanmean(dl[sel])) ** 2)
    sel_all, sel_22 = np.ones(len(dl), bool), per[1:] >= "2022-01"
    sel_np = ~((per[1:] >= "2020-03") & (per[1:] <= "2021-12"))
    md += ["## 2. Choque común a toda la ciudad\n",
           "Proporción de la varianza del cambio mensual (Δlog) explicada por el cambio medio de los 43 distritos ese mes. "
           "Un grafo entre distritos no aporta nada sobre ese componente común.\n",
           f"- Todo el periodo: {r2(sel_all):.3f}",
           f"- Sin pandemia (excluye 2020-03 – 2021-12): {r2(sel_np):.3f}",
           f"- Desde 2022: {r2(sel_22):.3f}\n"]

    # ---------------- 3. ¿predicen los vecinos?
    reg = []
    for wv, v in ventanas().items():
        itr, ite = indices(d, v["entrenamiento"]), indices(d, v["prueba"])
        for g in GRAFOS:
            w = pesos(g)

            def X(t):
                # sin el choque común del mes t (desconocido en t−1) se mide solo la parte propia de cada distrito
                e1 = dly[t - 2] - dly[t - 2].mean()
                return np.c_[e1, w @ e1]

            def Y(t):
                return dly[t - 1] - dly[t - 1].mean()

            tr = [t for t in itr if t >= 2]
            A, B = np.vstack([X(t) for t in tr]), np.concatenate([Y(t) for t in tr])
            mt = np.concatenate([d.valido[t] & d.valido[t - 1] & d.valido[t - 2] for t in tr])
            b_full = np.linalg.lstsq(A[mt], B[mt], rcond=None)[0]
            b_own = np.linalg.lstsq(A[mt][:, :1], B[mt], rcond=None)[0]
            res = B[mt] - A[mt] @ b_full
            cov = np.linalg.inv(A[mt].T @ A[mt]) * res.var(ddof=2)
            At, Bt = np.vstack([X(t) for t in ite]), np.concatenate([Y(t) for t in ite])
            mte = np.concatenate([d.valido[t] & d.valido[t - 1] & d.valido[t - 2] for t in ite])
            reg.append({"ventana": wv, "grafo": GRAFOS[g], "coef_propio": b_full[0], "coef_vecinos": b_full[1],
                        "t_vecinos": b_full[1] / np.sqrt(cov[1, 1]),
                        "MAE_cero": np.abs(Bt[mte]).mean(),
                        "MAE_propio": np.abs(Bt[mte] - At[mte][:, :1] @ b_own).mean(),
                        "MAE_propio_vecinos": np.abs(Bt[mte] - At[mte] @ b_full).mean()})
    reg = pd.DataFrame(reg)
    reg["mejora_por_vecinos_pct"] = (1 - reg.MAE_propio_vecinos / reg.MAE_propio) * 100
    reg.to_csv(FICHAS / "diagnostico_vecinos.csv", index=False)
    md += ["## 3. ¿El cambio de los vecinos ayuda a predecir el cambio propio?\n",
           "Regresión lineal por mínimos cuadrados del cambio propio del mes t (sin el choque común) sobre el cambio propio y "
           "el cambio medio de los vecinos del mes t−1. Se ajusta con el entrenamiento de cada ventana y se mide el MAE en "
           "Δlog en su prueba. Este análisis no ajusta ningún modelo del estudio.\n",
           reg.round(4).to_markdown(index=False), "",
           f"Mejora media del MAE al agregar los vecinos: {reg.groupby('grafo').mejora_por_vecinos_pct.mean().round(3).to_dict()} %.\n",
           "## Lectura\n",
           "El nivel tiene una autocorrelación espacial fuerte y estable: los distritos con muchas denuncias están juntos. "
           "Esa estructura es fija y ya está contenida en el historial de cada distrito. El cambio mensual, en cambio, tiene "
           "una I de Moran media cercana a cero: hay meses con dependencia significativa, pero su signo alterna (positiva en "
           "unos, negativa en otros), de modo que no deja un patrón estable que un modelo pueda aprender. El cambio de los "
           "vecinos en t−1 tiene un coeficiente pequeño y significativo dentro del entrenamiento, pero al predecir fuera de "
           "muestra su aporte al MAE es despreciable. Es una propiedad de los datos a escala distrito-mes, no de una "
           "arquitectura en particular. El Δlog de los distritos de muy bajo volumen es muy ruidoso y pesa en la I de Moran "
           "igual que el de los grandes, por lo que los meses significativos deben leerse con cautela.\n",
           "Figura: `results/figuras/diagnostico_moran.png`\n"]
    (FICHAS / "diagnostico_espacial.md").write_text("\n".join(md), encoding="utf-8")
    print(mo.round(3).to_string(index=False))
    print(f"choque común: todo {r2(sel_all):.3f}, sin pandemia {r2(sel_np):.3f}, desde 2022 {r2(sel_22):.3f}")
    print(reg[["ventana", "grafo", "coef_vecinos", "t_vecinos", "mejora_por_vecinos_pct"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
