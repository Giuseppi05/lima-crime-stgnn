"""v4 (candidato 3b): confirmación con 5 semillas de la selección multianual, fuera de muestra y solo con validación.

Uso: GNN_EXPERIMENTO=h1_v4_validacion_multianual python -m src.confirmar_seleccion [--rapido]

Para w = 3 y 4 y los tres modelos neuronales, con la grilla de la v2 (salida residual, semilla 0):
  A = configuración con menor MAE en el año de validación de la ventana w − 1 (un año)
  B = configuración con menor MAE promedio en los años de validación de las ventanas 1 … w − 1 (varios años)
Ninguna usa el año de validación de w. Ambas se entrenan en la ventana w con las semillas 0–4 y se mide su MAE en ese
año (con la parada temprana en él, igual para las dos). La prueba no interviene.

Regla fijada antes de correr. Se adopta si, en el GE:
  - con las 5 semillas, B < A en la media en w = 3 y en w = 4, y al menos 6 de 10 pares (ventana × semilla) favorecen
    a B;
  - y también sin la semilla 0 (ya vista en la verificación previa): B < A en la media de las semillas 1–4 en las dos
    ventanas, y al menos 5 de 8 pares favorecen a B.
"""
from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
import torch

from src.comun import FICHAS, RAIZ, leer_config
from src.entrenar import entrenar_una
from src.protocolo import cargar_datos, ventanas

K = ["oculto", "lr", "dropout", "entrada_meses"]
GRILLA_V2 = RAIZ / "results" / "fichas" / "ajuste_hiperparametros.csv"  # v2, commit ca03da1


def configuraciones() -> pd.DataFrame:
    a = pd.read_csv(GRILLA_V2, dtype={"ventana": str})
    a = a[a.salida == "residual"]
    M = a.pivot_table(index=["modelo", *K], columns="ventana", values="mae_validacion")
    filas = []
    for m in ["GE", "GC2", "GC1"]:
        X = M.loc[m]
        for w in ["3", "4"]:
            previas = [str(k) for k in range(1, int(w))]
            for proc, cfg in (("A", X[str(int(w) - 1)].idxmin()), ("B", X[previas].mean(1).idxmin())):
                filas.append({"modelo": m, "ventana": w, "procedimiento": proc, **dict(zip(K, cfg)),
                              "mae_semilla0_grilla": X.loc[cfg, w]})
    return pd.DataFrame(filas)


def _tarea(args):
    fila, semilla, epocas, pac = args
    torch.set_num_threads(1)
    d = cargar_datos()
    v = ventanas()[fila["ventana"]]
    hp = {"oculto": int(fila["oculto"]), "lr": float(fila["lr"]), "dropout": float(fila["dropout"]),
          "entrada_meses": int(fila["entrada_meses"])}
    _, mae, ep, _ = entrenar_una(d, v, fila["modelo"], hp, True, semilla, epocas, pac)
    return {**fila, "semilla": semilla, "mae_validacion": round(mae, 4), "epocas": ep}


def decidir(r: pd.DataFrame) -> tuple[bool, list[str]]:
    ge = r[r.modelo == "GE"].pivot_table(index=["ventana", "semilla"], columns="procedimiento", values="mae_validacion")
    ge["dif"] = ge.B - ge.A
    lineas, ok = [], True
    for etiqueta, sel, minimo in (("5 semillas", ge, 6), ("sin la semilla 0", ge.drop(index=0, level="semilla"), 5)):
        media = sel.groupby("ventana").dif.mean()
        pares = int((sel.dif < 0).sum())
        cumple = bool((media < 0).all() and pares >= minimo)
        ok &= cumple
        lineas.append(f"- {etiqueta}: B − A medio en w = 3 {media['3']:+.3f}, en w = 4 {media['4']:+.3f}; "
                      f"{pares} de {len(sel)} pares a favor de B (mínimo {minimo}) → {'cumple' if cumple else 'no cumple'}.")
    return ok, lineas


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--trabajadores", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    a = ap.parse_args()
    fx = leer_config()["fijos_neuronales"]
    c = configuraciones()
    semillas = [0] if a.rapido else leer_config()["semillas"]
    epocas, pac = (2, 1) if a.rapido else (fx["epocas_max"], fx["paciencia"])
    filas = c.to_dict("records")[:2] if a.rapido else c.to_dict("records")
    tareas = [(f, s, epocas, pac) for f in filas for s in semillas]
    print(f"confirmación: {len(tareas)} corridas, {a.trabajadores} procesos", flush=True)
    with ProcessPoolExecutor(a.trabajadores) as ex:
        r = pd.DataFrame(list(ex.map(_tarea, tareas)))
    r.to_csv(FICHAS / "confirmacion_seleccion.csv", index=False)
    if a.rapido:
        print(r.to_string())
        return
    ok, lineas = decidir(r)
    t = r.pivot_table(index=["modelo", "ventana"], columns="procedimiento", values="mae_validacion", aggfunc="mean")
    t1 = r[r.semilla != 0].pivot_table(index=["modelo", "ventana"], columns="procedimiento", values="mae_validacion",
                                       aggfunc="mean")
    sd = r.pivot_table(index=["modelo", "ventana"], columns="procedimiento", values="mae_validacion", aggfunc="std")
    tab = pd.DataFrame({"A (5 sem.)": t.A, "B (5 sem.)": t.B, "B − A": t.B - t.A, "sd A": sd.A, "sd B": sd.B,
                        "A (sem. 1–4)": t1.A, "B (sem. 1–4)": t1.B, "B − A (sem. 1–4)": t1.B - t1.A})
    cfg = c.assign(cfg=c[K].astype(str).agg("/".join, axis=1)).pivot_table(
        index=["modelo", "ventana"], columns="procedimiento", values="cfg", aggfunc="first")
    s0 = r[r.semilla == 0].merge(c, on=["modelo", "ventana", "procedimiento", *K, "mae_semilla0_grilla"])
    s0_dif = (s0.mae_validacion - s0.mae_semilla0_grilla).abs()
    md = ["# v4 (candidato 3b): confirmación de la selección multianual con 5 semillas\n",
          "Generado por `GNN_EXPERIMENTO=h1_v4_validacion_multianual python -m src.confirmar_seleccion`. MAE en denuncias "
          "en el año de validación de la ventana w, que ni A ni B usaron para elegir. A: elegida con el año de "
          "validación de w − 1. B: elegida con el promedio de los años de validación de las ventanas 1 … w − 1. Grilla de "
          "la v2 (`results/fichas/ajuste_hiperparametros.csv`, salida residual). La prueba no intervino. "
          "Nota. Elaboración propia.\n",
          "## Configuraciones (oculto/lr/dropout/L)\n", cfg.to_markdown(), "",
          "## MAE fuera de muestra (media entre semillas)\n", tab.round(3).to_markdown(), "",
          "## Decisión (regla fijada antes de correr, sobre el GE)\n", *lineas, "",
          f"**{'Se adopta' if ok else 'No se adopta'} la selección multianual.**\n",
          f"Control: la semilla 0 reproduce el MAE de la grilla de la v2 con una diferencia máxima de {s0_dif.max():.4f} "
          "(la grilla se corrió en otra PC).\n"]
    (FICHAS / "confirmacion_seleccion.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
