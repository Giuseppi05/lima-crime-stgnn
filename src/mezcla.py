"""v4 (candidato 2): mezcla de cada modelo neuronal con la persistencia, sin reentrenar.

Uso: GNN_EXPERIMENTO=h1_v4_mezcla python -m src.mezcla

    ŷ_mix = α·ŷ_modelo + (1 − α)·y(t − H) = y(t − H) + α·(ŷ_modelo − y(t − H))

Con la salida residual, α solo encoge el cambio predicho. Hay un α por modelo y ventana, compartido por las 5 semillas,
y se elige solo con validación: P ∈ ℝ^{semillas×12×43} (predicciones de validación de los modelos ya entrenados de
`modelos_de`), Y_prev = y[i_va − H] y Y = y[i_va] ∈ ℝ^{12×43}, con la máscara de celdas válidas.

Como α = 1 está en la rejilla, el MAE de validación de la mezcla nunca es peor que el del modelo. Por eso decide una
validación cruzada que deja un mes fuera dentro de los 12 de validación: el α de cada mes se elige con los otros 11.
La prueba se calcula al final y solo se informa.
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd
import torch

from src.comun import FICHAS, RAIZ, leer_config
from src.entrenar import MODELOS, cargar_grafo, predecir, tensor_entrada
from src.evaluar import ALFA, comparar
from src.modelos import STGNN
from src.protocolo import H, Transformacion, cargar_datos, indices, ventanas

NEURONALES = ["GE", "GC2", "GC1"]


def _mae(pred: np.ndarray, real: np.ndarray, ok: np.ndarray) -> float:
    """pred [S, T, N] o [T, N]: MAE de cada semilla sobre las celdas válidas, promediado entre semillas."""
    pred = pred.reshape(-1, *real.shape)
    return float(np.mean([np.abs(p - real)[ok].mean() for p in pred]))


def _elegir(P, Yp, Y, ok, alfas) -> float:
    return float(alfas[int(np.argmin([_mae(a * P + (1 - a) * Yp, Y, ok) for a in alfas]))])


def predicciones_modelo(d, dir_modelos, nombre, w, v, semillas, heads):
    """Validación y prueba [S, T, N] de los modelos ya entrenados, sin tocar sus pesos."""
    tr = Transformacion(d, indices(d, v["entrenamiento"]))
    X = tensor_entrada(d, tr)
    ei, ea = cargar_grafo(MODELOS[nombre], d.ubigeos)
    va, te = [], []
    for s in semillas:
        ck = torch.load(dir_modelos / f"{nombre}_{w}_{s}.pt", weights_only=False)
        assert ck["rasgos"] == X.shape[-1], "el modelo y la entrada no tienen los mismos rasgos"
        hp = ck["hp"]
        m = STGNN(int(hp["oculto"]), float(hp["dropout"]), MODELOS[nombre] is not None, ck["residual"], heads,
                  rasgos=ck["rasgos"])
        m.load_state_dict(ck["estado"])
        L = int(hp["entrada_meses"])
        va.append(predecir(m, X, indices(d, v["validacion"]), L, ei, ea, tr)[0])
        te.append(predecir(m, X, indices(d, v["prueba"]), L, ei, ea, tr)[0])
    return np.stack(va), np.stack(te)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows (cp1252) no imprime α
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    cfg = leer_config()
    mz = cfg["mezcla_persistencia"]
    base = RAIZ / "results" / "experimentos" / mz["modelos_de"]
    alfas = np.round(np.arange(0, 1 + 1e-9, mz["paso_alfa"]), 4)
    d = cargar_datos()
    vs = ventanas(incluir_pandemia=True)
    semillas = cfg["semillas"]
    heads = cfg["fijos_neuronales"]["gat_heads"]
    corridas = pd.concat([pd.read_csv(base / "fichas" / f, dtype={"ventana": str})
                          for f in ("corridas_neuronales.csv", "corridas_neuronales_pandemia.csv")])

    filas, prueba, control = [], [], []
    for w, v in vs.items():
        i_va, i_te = indices(d, v["validacion"]), indices(d, v["prueba"])
        Y, Yp, ok = d.y[i_va], d.y[i_va - H], d.valido[i_va]
        Yt, Ytp, okt = d.y[i_te], d.y[i_te - H], d.valido[i_te]
        mae_pers = _mae(Yp, Y, ok)
        for nombre in NEURONALES:
            P, Pt = predicciones_modelo(d, base / "modelos", nombre, w, v, semillas, heads)
            # controles: la prueba repredicha coincide con la guardada y la validación con la del entrenamiento
            for k, s in enumerate(semillas):
                g = pd.read_csv(base / "predicciones" / f"{nombre}_{w}_{s}.csv", dtype={"ubigeo": str})
                control.append({"modelo": nombre, "ventana": w, "semilla": s,
                                "max_dif_prueba": float(np.abs(g.predicho.to_numpy() - Pt[k].ravel()).max())})
            mae_va_ck = corridas.query("modelo == @nombre and ventana == @w").mae_validacion.mean()
            mae_mod = _mae(P, Y, ok)
            assert abs(mae_mod - mae_va_ck) < 1e-3, (nombre, w, mae_mod, mae_va_ck)
            a_full = _elegir(P, Yp, Y, ok, alfas)
            # validación cruzada dejando un mes fuera: el α del mes k sale de los otros 11 meses
            err, a_k = [], []
            for k in range(len(i_va)):
                r = np.arange(len(i_va)) != k
                a = _elegir(P[:, r], Yp[r], Y[r], ok[r], alfas)
                a_k.append(a)
                mix = a * P[:, k] + (1 - a) * Yp[k]
                err.append(np.abs(mix - Y[k])[:, ok[k]])  # [S, celdas válidas del mes k]
            mae_cv = float(np.concatenate(err, axis=1).mean(1).mean())
            filas.append({"modelo": nombre, "ventana": w, "alfa": a_full, "alfa_cv_min": min(a_k),
                          "alfa_cv_max": max(a_k), "val_modelo": mae_mod, "val_mix": _mae(a_full * P + (1 - a_full) * Yp, Y, ok),
                          "cv_mix": mae_cv, "val_mes_anterior": mae_pers})
            Pmix = a_full * Pt + (1 - a_full) * Ytp
            for k, s in enumerate(semillas):
                for etiqueta, pr in ((nombre, Pt[k]), (f"{nombre}_mix", Pmix[k])):
                    t, n = np.nonzero(okt)
                    prueba.append(pd.DataFrame({"modelo": etiqueta, "ventana": w, "semilla": s,
                                                "ubigeo": np.array(d.ubigeos)[n], "real": Yt[t, n], "predicho": pr[t, n]}))
        t, n = np.nonzero(okt)
        prueba.append(pd.DataFrame({"modelo": "mes_anterior", "ventana": w, "semilla": 0,
                                    "ubigeo": np.array(d.ubigeos)[n], "real": Yt[t, n], "predicho": Ytp[t, n]}))
        print(f"ventana {w} lista", flush=True)

    ctl = pd.DataFrame(control)
    assert ctl.max_dif_prueba.max() < 1e-3, ctl.sort_values("max_dif_prueba").tail()
    r = pd.DataFrame(filas)
    r["mix_mejor_cv"] = r.cv_mix < r.val_modelo - 1e-6  # con α = 1 en todos los meses ambos son iguales salvo redondeo
    r.to_csv(FICHAS / "mezcla_validacion.csv", index=False)

    # ---------------- decisión, solo con validación (ventanas 1–4; P se informa aparte)
    ge = r[(r.modelo == "GE") & (r.ventana != "P")]
    n_mejor, n_alfa = int(ge.mix_mejor_cv.sum()), int((ge.alfa < 1).sum())
    adopta = n_mejor >= 2 and n_alfa >= 3
    decision = (f"GE_mix < GE en validación cruzada en {n_mejor} de 4 ventanas; α* < 1 en {n_alfa} de 4. "
                f"Regla fijada antes de calcular (≥ 2 de 4, y α* < 1 consistente = en ≥ 3 de 4): **{'se adopta' if adopta else 'no se adopta'}**.")

    # ---------------- prueba (solo se informa), con las convenciones de src.evaluar
    p = pd.concat(prueba, ignore_index=True)
    p4 = p[p.ventana != "P"]

    def met(g):
        e = g.predicho - g.real
        return pd.Series({"MAE": e.abs().mean(), "RMSE": np.sqrt((e ** 2).mean())})

    glob = p4.groupby(["modelo", "semilla"]).apply(met, include_groups=False).groupby("modelo").mean()
    glob_p = p[p.ventana == "P"].groupby(["modelo", "semilla"]).apply(met, include_groups=False).groupby("modelo").mean()
    dist = (p4.groupby(["modelo", "ventana", "semilla", "ubigeo"]).apply(met, include_groups=False)
            .groupby(["modelo", "ubigeo"]).mean())
    pm, pr_ = dist.MAE.unstack("modelo"), dist.RMSE.unstack("modelo")
    est = []
    for a_, b_ in [("GE_mix", "GC1_mix"), ("GE_mix", "GC2_mix"), ("GE_mix", "mes_anterior"), ("GE_mix", "GE")]:
        c = comparar(pm[a_].values, pm[b_].values)
        exito = glob.loc[a_, "MAE"] < glob.loc[b_, "MAE"] and glob.loc[a_, "RMSE"] < glob.loc[b_, "RMSE"] and c["p"] < ALFA
        est.append({"comparacion": f"{a_} vs {b_}", "MAE_a": glob.loc[a_, "MAE"], "MAE_b": glob.loc[b_, "MAE"],
                    "RMSE_a": glob.loc[a_, "RMSE"], "RMSE_b": glob.loc[b_, "RMSE"], "prueba": c["prueba"], "p": c["p"],
                    "p_RMSE_distrito": comparar(pr_[a_].values, pr_[b_].values)["p"],
                    "distritos_a_mejor": c["distritos_GE_mejor"], "a_supera": "sí" if exito else "no"})
    est = pd.DataFrame(est)
    glob.to_csv(FICHAS / "mezcla_prueba_global.csv")
    est.to_csv(FICHAS / "mezcla_pruebas_estadisticas.csv", index=False)
    ctl.to_csv(FICHAS / "mezcla_control.csv", index=False)

    orden = ["GE", "GE_mix", "GC2", "GC2_mix", "GC1", "GC1_mix", "mes_anterior"]
    tab = r.set_index(["modelo", "ventana"])[["alfa", "alfa_cv_min", "alfa_cv_max", "val_modelo", "val_mix", "cv_mix",
                                              "val_mes_anterior", "mix_mejor_cv"]]
    md = ["# v4 (candidato 2): mezcla con la persistencia — validación y decisión\n",
          "Generado por `GNN_EXPERIMENTO=h1_v4_mezcla python -m src.mezcla`. ŷ_mix = α·ŷ_modelo + (1 − α)·y(t − 1), "
          f"un α por modelo y ventana (rejilla 0–1, paso {mz['paso_alfa']}) compartido por las 5 semillas. Modelos de "
          f"`{mz['modelos_de']}` sin reentrenar. MAE en denuncias, media de 5 semillas. Nota. Elaboración propia.\n",
          "## Validación (decide)\n",
          "`val_modelo`: MAE de validación del modelo solo. `val_mix`: con el α* elegido en los 12 meses (optimista por "
          "construcción, nunca peor que `val_modelo`). `cv_mix`: validación cruzada dejando un mes fuera (el α de cada mes "
          "sale de los otros 11): **es la que decide**. `alfa_cv_min/max`: rango de los 12 α de la validación cruzada.\n",
          tab.round(3).to_markdown(), "",
          f"**Decisión.** {decision}\n",
          "Sesgo declarado: las predicciones de validación vienen de modelos cuya parada temprana y cuyos hiperparámetros se "
          "eligieron con esa misma validación, así que el modelo se ve en ella mejor de lo que es y α* se inclina hacia 1. "
          "El sesgo va en contra de adoptar la mezcla: si aun así α* < 1 ayuda, el resultado es más sólido.\n",
          f"Control: la prueba repredicha con los modelos cargados coincide con la guardada (máx. dif. "
          f"{ctl.max_dif_prueba.max():.1e}), y el MAE de validación coincide con `corridas_neuronales.csv`.\n",
          "## Prueba (solo se informa; calculada después de fijar la regla)\n",
          "### Ventanas 1–4 (MAE y RMSE globales, media de 5 semillas)\n",
          glob.loc[[m for m in orden if m in glob.index]].round(3).to_markdown(), "",
          "### Ventana P (pandemia)\n",
          glob_p.loc[[m for m in orden if m in glob_p.index]].round(3).to_markdown(), "",
          "### Pruebas estadísticas complementarias (n = 43, MAE por distrito promediado entre ventanas y semillas)\n",
          "No reemplazan la regla principal del AVC3 (GE frente a GC₂ y GC₁ sin mezcla).\n",
          est.round(4).to_markdown(index=False), ""]
    (FICHAS / "mezcla.md").write_text("\n".join(md), encoding="utf-8")
    print(tab.round(3).to_string())
    print(decision)


if __name__ == "__main__":
    main()
