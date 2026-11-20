"""Modelado: ajuste de hiperparámetros (solo validación), elección de la salida y corridas finales de GE, GC₁ y GC₂.

Uso:
  python -m src.entrenar --rapido                 # prueba de humo: 1 ventana, 1 semilla, pocas épocas
  python -m src.entrenar --fase ajuste            # grilla × {directa, residual} × 3 modelos × ventanas, semilla 0
  python -m src.entrenar --fase congelar          # elige salida y configuración solo con validación (hito H4)
  python -m src.entrenar --fase final             # ventanas × 5 semillas × 3 modelos con la configuración congelada
  Añadir --pandemia para incluir la ventana adversa P.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import torch

from src.comun import ATENCION, FICHAS, PREDICCIONES, PROCESADOS, RESULTADOS, fijar_semilla, guardar_config, leer_config
from src.modelos import STGNN, atencion_a_tablas
from src.protocolo import Datos, Transformacion, cargar_datos, indices, metricas, tabla_predicciones, ventanas

MODELOS = {"GE": "vial", "GC1": None, "GC2": "geo"}
MODELOS_DIR = RESULTADOS / "modelos"
AJUSTE_CSV = FICHAS / "ajuste_hiperparametros.csv"


def cargar_grafo(tipo: str | None, ubigeos: list[str], matriz: np.ndarray | None = None):
    if tipo is None:
        return None, None
    if matriz is None:
        m = pd.read_csv(PROCESADOS / f"matriz_{tipo}.csv", index_col=0, dtype={0: str})
        m.index = m.index.astype(str).str.zfill(6)
        assert m.index.tolist() == ubigeos, "la matriz no está en el orden del panel"
        matriz = m.to_numpy(float)
    i, j = np.nonzero(matriz)
    return torch.tensor(np.vstack([i, j]), dtype=torch.long), torch.tensor(matriz[i, j], dtype=torch.float32).view(-1, 1)


def tensor_entrada(d: Datos, tr: Transformacion) -> torch.Tensor:
    """[meses, distritos, 4]: objetivo transformado, mes seno, mes coseno, pandemia."""
    z = tr.directa(d.y)
    T, N = z.shape
    s = np.repeat(np.sin(2 * np.pi * d.mes / 12)[:, None], N, 1)
    c = np.repeat(np.cos(2 * np.pi * d.mes / 12)[:, None], N, 1)
    p = np.repeat(d.pandemia[:, None], N, 1)
    return torch.tensor(np.stack([z, s, c, p], -1), dtype=torch.float32)


def ventanas_x(X: torch.Tensor, idx: np.ndarray, L: int) -> torch.Tensor:
    """Para cada mes objetivo t, los L meses anteriores: solo información previa a t."""
    return torch.stack([X[t - L:t] for t in idx])


def predecir(modelo, X, idx, L, ei, ea, tr, atencion=False):
    modelo.eval()
    with torch.no_grad():
        r = modelo(ventanas_x(X, idx, L), ei, ea, atencion=atencion)
    z, extra = (r if atencion else (r, None))
    return tr.inversa(z.numpy()), extra


def entrenar_una(d: Datos, v: dict, nombre: str, hp: dict, residual: bool, semilla: int,
                 epocas_max: int, paciencia: int, X: torch.Tensor | None = None, grafo=None):
    cfg = leer_config()["fijos_neuronales"]
    fijar_semilla(semilla)
    i_tr, i_va, i_te = (indices(d, v[k]) for k in ("entrenamiento", "validacion", "prueba"))
    tr = Transformacion(d, i_tr)
    if X is None:
        X = tensor_entrada(d, tr)
    L = int(hp["entrada_meses"])
    ei, ea = grafo if grafo is not None else cargar_grafo(MODELOS[nombre], d.ubigeos)
    i_fit = i_tr[i_tr >= L]
    Xtr, Ytr = ventanas_x(X, i_fit, L), X[i_fit, :, 0]
    Mtr = torch.tensor(d.valido[i_fit], dtype=torch.float32)  # los meses sin información no entran a la pérdida
    modelo = STGNN(int(hp["oculto"]), float(hp["dropout"]), MODELOS[nombre] is not None, residual, cfg["gat_heads"])
    opt = torch.optim.Adam(modelo.parameters(), lr=float(hp["lr"]), weight_decay=cfg["weight_decay"])
    huber = torch.nn.HuberLoss(reduction="none")
    gen = torch.Generator().manual_seed(semilla)
    va_real, va_ok = d.y[i_va], d.valido[i_va]
    mejor, estado, sin_mejora, ep = np.inf, None, 0, 0
    for ep in range(1, epocas_max + 1):
        modelo.train()
        for lote in torch.randperm(len(i_fit), generator=gen).split(cfg["tam_lote"]):
            opt.zero_grad()
            perd = (huber(modelo(Xtr[lote], ei, ea), Ytr[lote]) * Mtr[lote]).sum() / Mtr[lote].sum()
            perd.backward()
            opt.step()
        p_va, _ = predecir(modelo, X, i_va, L, ei, ea, tr)
        mae = np.abs(p_va - va_real)[va_ok].mean()
        if mae < mejor - 1e-9:
            mejor, estado, sin_mejora = mae, {k: t.clone() for k, t in modelo.state_dict().items()}, 0
        else:
            sin_mejora += 1
            if sin_mejora >= paciencia:
                break
    modelo.load_state_dict(estado)
    return modelo, float(mejor), ep, (X, tr, L, ei, ea, i_va, i_te)


def cargar_entrenado(d: Datos, nombre: str, w: str, semilla: int):
    """Modelo ya entrenado (sin reentrenar) y los insumos para predecir su ventana de prueba."""
    ck = torch.load(MODELOS_DIR / f"{nombre}_{w}_{semilla}.pt", weights_only=False)
    hp = ck["hp"]
    cfg = leer_config()
    m = STGNN(int(hp["oculto"]), float(hp["dropout"]), MODELOS[nombre] is not None, ck["residual"],
              cfg["fijos_neuronales"]["gat_heads"])
    m.load_state_dict(ck["estado"])
    m.eval()
    v = ventanas(incluir_pandemia=True)[w]
    tr = Transformacion(d, indices(d, v["entrenamiento"]))
    return m, tr, int(hp["entrada_meses"]), indices(d, v["prueba"])


def predecir_con(modelo, d: Datos, tr, L, i_te, matriz=None, y_entrada=None):
    """Predice la prueba con otro grafo (matriz 43×43) o con otra serie de entrada, sin tocar los pesos."""
    if y_entrada is not None:
        d = Datos(d.periodos, d.ubigeos, d.distritos, y_entrada, d.valido, d.pandemia, d.mes)
    X = tensor_entrada(d, tr)
    ei, ea = cargar_grafo("x", d.ubigeos, matriz) if modelo.usar_grafo else (None, None)
    p, _ = predecir(modelo, X, i_te, L, ei, ea, tr)
    return p


# ---------------------------------------------------------------- fases

def _tarea_ajuste(args):
    w, v, nombre, hp, residual, epocas, paciencia = args
    torch.set_num_threads(1)
    d = cargar_datos()
    t0 = time.time()
    _, mae, ep, _ = entrenar_una(d, v, nombre, hp, residual, 0, epocas, paciencia)
    return {"ventana": w, "modelo": nombre, "salida": "residual" if residual else "directa", **hp,
            "mae_validacion": round(mae, 4), "epocas": ep, "segundos": round(time.time() - t0, 1)}


def fase_ajuste(vs, rapido, trabajadores):
    cfg = leer_config()
    g = cfg["grilla_neuronal"]
    grilla = [dict(zip(g, c)) for c in itertools.product(*g.values())]
    fx = cfg["fijos_neuronales"]
    epocas, pac = (fx["epocas_max"], fx["paciencia"]) if not rapido else (3, 2)
    if rapido:
        grilla = grilla[:1]
    hechas = pd.read_csv(AJUSTE_CSV, dtype={"ventana": str}) if AJUSTE_CSV.exists() and not rapido else pd.DataFrame()
    clave = ["ventana", "modelo", "salida", "oculto", "lr", "dropout", "entrada_meses"]
    ya = set(map(tuple, hechas[clave].astype(str).values)) if len(hechas) else set()
    tareas = []
    for w, v in vs.items():
        for nombre in MODELOS:
            for residual in (False, True):
                for hp in grilla:
                    k = (w, nombre, "residual" if residual else "directa", *map(str, hp.values()))
                    if k not in ya:  # reanudable: no repite lo ya calculado
                        tareas.append((w, v, nombre, hp, residual, epocas, pac))
    print(f"ajuste: {len(tareas)} entrenamientos pendientes, {trabajadores} procesos")
    filas = []
    with ProcessPoolExecutor(trabajadores) as ex:
        for i, r in enumerate(ex.map(_tarea_ajuste, tareas), 1):
            filas.append(r)
            if i % 20 == 0 or i == len(tareas):
                print(f"  {i}/{len(tareas)}  último: {r}", flush=True)
                if not rapido:
                    pd.concat([hechas, pd.DataFrame(filas)]).to_csv(AJUSTE_CSV, index=False)
    return pd.concat([hechas, pd.DataFrame(filas)]) if filas else hechas


def fase_congelar(vs):
    """Elige la salida (directa o residual) y la configuración de cada modelo y ventana solo con validación."""
    a = pd.read_csv(AJUSTE_CSV, dtype={"ventana": str})
    a = a[a.ventana.isin(vs)]
    mejor = a.loc[a.groupby(["ventana", "modelo", "salida"]).mae_validacion.idxmin()]
    # la salida se elige una sola vez para los tres modelos: menor MAE de validación promedio de las mejores configuraciones
    cfg = leer_config()
    if "P" in vs:  # la ventana de pandemia hereda la salida elegida con las 4 ventanas principales
        salida = cfg["salida_neuronal"]["elegida"]
        por_salida = mejor.groupby("salida").mae_validacion.mean()
    else:
        por_salida = mejor.groupby("salida").mae_validacion.mean()
        salida = por_salida.idxmin()
        cfg["salida_neuronal"] = {"elegida": salida,
                                  "mae_validacion_promedio": {k: round(float(x), 4) for k, x in por_salida.items()}}
    hpn = cfg.setdefault("hiperparametros", {})
    for _, r in mejor[mejor.salida == salida].iterrows():
        hpn.setdefault(r.modelo, {})[r.ventana] = {
            "oculto": int(r.oculto), "lr": float(r.lr), "dropout": float(r.dropout),
            "entrada_meses": int(r.entrada_meses), "mae_validacion": float(r.mae_validacion)}
    guardar_config(cfg)
    t = mejor.pivot_table(index=["modelo", "ventana"], columns="salida", values="mae_validacion")
    (FICHAS / "eleccion_salida.md").write_text(
        "# Modelado: elección de la salida de los modelos neuronales\n\n"
        "Criterio: menor MAE de validación promedio (mejor configuración de la grilla por modelo y ventana, semilla 0). "
        "El conjunto de prueba no intervino.\n\n" + t.round(3).to_markdown() +
        f"\n\nPromedio por salida: {por_salida.round(3).to_dict()}. **Elegida: {salida}**, aplicada igual a GE, GC₁ y GC₂.\n"
        "\nNota. Elaboración propia.\n", encoding="utf-8")
    print(t.round(3).to_string(), f"\nsalida elegida: {salida}")


def _tarea_final(args):
    w, v, nombre, hp, residual, semilla, epocas, pac, sufijo = args
    torch.set_num_threads(1)
    d = cargar_datos()
    modelo, mae_va, ep, (X, tr, L, ei, ea, i_va, i_te) = entrenar_una(d, v, nombre, hp, residual, semilla, epocas, pac)
    p_te, extra = predecir(modelo, X, i_te, L, ei, ea, tr, atencion=True)
    base = f"{nombre}_{w}_{semilla}{sufijo}"
    tabla_predicciones(d, i_te, p_te).to_csv(PREDICCIONES / f"{base}.csv", index=False)
    atencion_a_tablas(extra, d.ubigeos, [d.periodos[t] for t in i_te], L).to_csv(ATENCION / f"{base}.csv", index=False)
    MODELOS_DIR.mkdir(exist_ok=True)
    torch.save({"estado": modelo.state_dict(), "hp": hp, "residual": residual}, MODELOS_DIR / f"{base}.pt")
    m = metricas(d.y[i_te][d.valido[i_te]], p_te[d.valido[i_te]])
    return {"modelo": nombre, "ventana": w, "semilla": semilla, "mae_validacion": round(mae_va, 4), "epocas": ep, **m}


def fase_final(vs, rapido, trabajadores):
    cfg = leer_config()
    fx = cfg["fijos_neuronales"]
    semillas = cfg["semillas"] if not rapido else [0]
    if rapido:
        g = cfg["grilla_neuronal"]
        hp_def = {"oculto": 16, "lr": 0.003, "dropout": 0.1, "entrada_meses": 12}
        residual, epocas, pac, sufijo = True, 3, 2, ""
    else:
        residual = cfg["salida_neuronal"]["elegida"] == "residual"
        epocas, pac, sufijo = fx["epocas_max"], fx["paciencia"], ""
    tareas = []
    for w, v in vs.items():
        for nombre in MODELOS:
            hp = hp_def if rapido else {k: cfg["hiperparametros"][nombre][w][k] for k in ("oculto", "lr", "dropout", "entrada_meses")}
            for s in semillas:
                tareas.append((w, v, nombre, hp, residual, s, epocas, pac, sufijo))
    print(f"final: {len(tareas)} corridas, {trabajadores} procesos")
    filas = []
    with ProcessPoolExecutor(trabajadores) as ex:
        for r in ex.map(_tarea_final, tareas):
            filas.append(r)
            print(f"  {r}", flush=True)
    r = pd.DataFrame(filas)
    if not rapido:
        nombre = "corridas_neuronales" + ("_pandemia" if "P" in vs else "") + ".csv"
        r.to_csv(FICHAS / nombre, index=False)
    print(r.groupby(["modelo", "ventana"])[["MAE", "RMSE", "R2"]].mean().round(3).to_string())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fase", choices=["ajuste", "congelar", "final"], default="final")
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--pandemia", action="store_true", help="solo la ventana adversa P")
    ap.add_argument("--trabajadores", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    a = ap.parse_args()
    vs = ventanas(incluir_pandemia=True)
    vs = {"P": vs["P"]} if a.pandemia else {k: x for k, x in vs.items() if k != "P"}
    if a.rapido:
        vs = {k: vs[k] for k in list(vs)[:1]}
        fase_ajuste(vs, True, a.trabajadores)
        fase_final(vs, True, a.trabajadores)
        return
    if a.fase == "ajuste":
        fase_ajuste(vs, False, a.trabajadores)
    elif a.fase == "congelar":
        fase_congelar(vs)
    else:
        fase_final(vs, False, a.trabajadores)


if __name__ == "__main__":
    main()
