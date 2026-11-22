"""Evaluación (opciones extra, fuera del AVC3): comparación de los experimentos de results/experimentos/.

Uso: python -m src.comparar_experimentos
Para cada experimento: MAE de validación (media de las corridas finales) y MAE de prueba de los modelos neuronales,
y la persistencia del mismo horizonte. La validación es la que decide; la prueba solo se informa.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import yaml

from src.comun import RAIZ
from src.protocolo import cargar_datos, indices, ventanas

EXP = RAIZ / "results" / "experimentos"
NOMBRES = ["h1_base", "h1_modalidades", "h3_base", "h3_modalidades"]


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    filas, pruebas = [], []
    d = cargar_datos()
    for e in NOMBRES:
        f = EXP / e / "fichas"
        cfg = yaml.safe_load(open(RAIZ / "configs" / "experimentos" / f"{e}.yaml", encoding="utf-8"))
        g = pd.read_csv(f / "metricas_global.csv", index_col=0)
        va = pd.read_csv(f / "corridas_neuronales.csv").groupby("modelo").mae_validacion.mean()
        fila = {"experimento": e, "horizonte": cfg["horizonte_meses"], "modalidades": cfg["entradas_modalidades"]}
        for m in ["GE", "GC2", "GC1"]:
            fila[f"val_{m}"] = va[m]
        h = cfg["horizonte_meses"]
        # persistencia en los mismos meses de validación, para ver si la ventaja de validación se sostiene en prueba
        fila["val_persistencia"] = np.mean([np.abs(d.y[i] - d.y[i - h])[d.valido[i]].mean()
                                            for i in (indices(d, v["validacion"]) for v in ventanas().values())])
        for m in ["GE", "GE_ens", "GC2", "GC1", "xgboost", "mes_anterior"]:
            fila[f"prueba_{m}"] = g.loc[m, "MAE"]
        filas.append(fila)
        p = pd.read_csv(f / "pruebas_estadisticas.csv")
        pruebas.append(p[["comparacion", "MAE_GE", "MAE_rival", "p", "distritos_GE_mejor", "GE_supera"]].assign(experimento=e))
    t = pd.DataFrame(filas).set_index("experimento")
    pr = pd.concat(pruebas).set_index(["experimento", "comparacion"])
    md = ["# Evaluación (opciones extra, fuera del AVC3): comparación de experimentos\n",
          "Generado por `python -m src.comparar_experimentos`. Todos parten de la v2 (sin pérdida ponderada). Horizonte H: "
          "se predice el mes t con datos hasta t − H; la persistencia es el último mes observado (t − H). Modalidades: "
          "hurto, robo y la suma de las otras cinco como entradas. `GE_ens`: promedio de las 5 semillas. Hiperparámetros "
          "elegidos solo con validación. MAE en denuncias por distrito y mes, 4 ventanas. Nota. Elaboración propia.\n",
          "## Validación (decide) — media de las 20 corridas finales\n",
          t[["horizonte", "modalidades", "val_GE", "val_GC2", "val_GC1", "val_persistencia"]].round(3).to_markdown(), "",
          "## Prueba (solo se informa)\n",
          t[[c for c in t if c.startswith("prueba_")]].round(3).to_markdown(), "",
          "## Pruebas estadísticas (n = 43 distritos)\n", pr.round(4).to_markdown(), "",
          "## Lectura\n",
          "- En validación los tres modelos neuronales quedan por debajo de la persistencia en los cuatro experimentos. En "
          "prueba ninguno la supera. La validación es optimista porque en ella se eligió la configuración y se hizo la "
          "parada temprana: esa ventaja no se sostiene fuera de muestra.",
          "- Las modalidades como entradas no mejoran ni en validación ni en prueba.",
          "- Con H = 3 el GE supera al GC₁ en prueba (p < 0,001), pero en validación el GC₁ es el mejor de los tres. La "
          "ventaja del grafo a 3 meses depende del periodo, no es estable. GE y GC₂ no se distinguen (p = 0,90).",
          "- El promedio de semillas baja el MAE de prueba entre 0,2 y 0,9 en todos los experimentos y no cambia ninguna "
          "conclusión.\n"]
    (EXP / "comparacion.md").write_text("\n".join(md), encoding="utf-8")
    t.to_csv(EXP / "comparacion.csv")
    print(t.round(3).T.to_string())
    print(pr.round(4).to_string())


if __name__ == "__main__":
    main()
