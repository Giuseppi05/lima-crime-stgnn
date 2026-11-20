"""Despliegue: mapa de riesgo distrital con la predicción del GE para el último mes de prueba.

Uso: python -m src.mapa
Artefacto de investigación: no se usa para decisiones operativas de patrullaje.
"""
from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.comun import FICHAS, FIGURAS, PREDICCIONES
from src.grafos import cargar_limites


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rapido", action="store_true")
    ap.parse_args()
    vent = sorted({f.name.split("_")[1] for f in PREDICCIONES.glob("GE_[1-4]_[0-9].csv")})
    if not vent:
        raise SystemExit("Faltan las predicciones del GE")
    w = vent[-1]  # la última ventana disponible (la 4 en las corridas completas)
    archivos = sorted(PREDICCIONES.glob(f"GE_{w}_[0-9].csv"))
    p = pd.concat([pd.read_csv(f, dtype={"ubigeo": str}) for f in archivos])
    ultimo = p.periodo.max()
    u = p[p.periodo == ultimo].groupby("ubigeo").agg(predicho=("predicho", "mean"), sd=("predicho", "std"),
                                                     real=("real", "first"), valido=("valido", "first")).reset_index()
    u["error_abs"] = (u.predicho - u.real).abs()
    lim, _ = cargar_limites()
    g = lim.merge(u, on="ubigeo")
    fig, axs = plt.subplots(1, 3, figsize=(16, 7))
    vmax = max(g.predicho.max(), g.real.max())
    for ax, col, tit, cmap, vm in [(axs[0], "predicho", f"Predicción GE (media de {len(archivos)} semillas)", "OrRd", vmax),
                                   (axs[1], "real", "Denuncias registradas", "OrRd", vmax),
                                   (axs[2], "error_abs", "Error absoluto", "Purples", None)]:
        g.plot(column=col, ax=ax, cmap=cmap, vmin=0, vmax=vm, legend=True, edgecolor="white", lw=.4,
               legend_kwds={"shrink": .6})
        if col == "error_abs":
            g[~g.valido].plot(ax=ax, color="lightgray", hatch="//", edgecolor="white")
        ax.set_title(tit, fontsize=10)
        ax.set_axis_off()
    fig.suptitle(f"Mapa de riesgo distrital: hurto + robo, {ultimo} (ventana {w}). Artefacto de investigación, sin uso operativo.",
                 fontsize=11)
    fig.text(.01, .01, "Nota. Elaboración propia. Datos: SIDPOL-MININTER (ODC-BY); límites: INEI IDE 2023.", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURAS / "mapa_riesgo_distrital.png", dpi=170)
    plt.close(fig)
    u.assign(distrito=u.ubigeo.map(dict(zip(lim.ubigeo, lim.distrito)))).sort_values("predicho", ascending=False) \
        .round(2).to_csv(FICHAS / "mapa_riesgo_distrital.csv", index=False)
    print(f"mapa {ultimo}: {len(g)} distritos")


if __name__ == "__main__":
    main()
