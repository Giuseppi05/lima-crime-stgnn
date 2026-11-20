"""Protocolo de evaluación común a todos los modelos: ventanas, transformación y métricas."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.comun import leer_config, leer_panel

STD_MIN = 1e-3  # evita dividir por ~0 en distritos casi constantes


@dataclass
class Datos:
    """Panel en forma de matriz [meses, distritos], en el orden de ubigeo del panel."""
    periodos: list[str]
    ubigeos: list[str]
    distritos: list[str]
    y: np.ndarray            # denuncias (sin_informacion rellenado con 0)
    valido: np.ndarray       # False en las celdas sin_informacion: no entran a métricas ni a la pérdida
    pandemia: np.ndarray     # [meses]
    mes: np.ndarray          # 1..12


def cargar_datos() -> Datos:
    p = leer_panel()
    ub = p[["ubigeo", "distrito"]].drop_duplicates()
    per = sorted(p.periodo.unique())
    y = p.pivot(index="periodo", columns="ubigeo", values="objetivo").loc[per, ub.ubigeo].to_numpy(float)
    val = (p.pivot(index="periodo", columns="ubigeo", values="estado").loc[per, ub.ubigeo] != "sin_informacion").to_numpy()
    pan = p.groupby("periodo")["pandemia"].first().loc[per].to_numpy(float)
    mes = np.array([int(x[5:]) for x in per])
    return Datos(per, ub.ubigeo.tolist(), ub.distrito.tolist(), y, val, pan, mes)


def ventanas(incluir_pandemia: bool = False) -> dict[str, dict]:
    cfg = leer_config()
    v = dict(cfg["ventanas"])
    if incluir_pandemia:
        v.update(cfg["ventana_pandemia"])
    return v


def indices(d: Datos, rango: list[str]) -> np.ndarray:
    per = np.array(d.periodos)
    return np.nonzero((per >= rango[0]) & (per <= rango[1]))[0]


class Transformacion:
    """log1p y estandarización por distrito; media y desviación solo con los meses de entrenamiento."""

    def __init__(self, d: Datos, idx_entrenamiento: np.ndarray):
        z = np.log1p(d.y[idx_entrenamiento])
        m = d.valido[idx_entrenamiento]
        z = np.where(m, z, np.nan)  # los meses sin información no cuentan para la media ni la desviación
        self.media = np.nanmean(z, axis=0)
        self.desv = np.maximum(np.nanstd(z, axis=0), STD_MIN)

    def directa(self, y: np.ndarray) -> np.ndarray:
        return (np.log1p(y) - self.media) / self.desv

    def inversa(self, z: np.ndarray) -> np.ndarray:
        return np.clip(np.expm1(z * self.desv + self.media), 0, None)


def metricas(real: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    real = np.asarray(real, float)
    pred = np.asarray(pred, float)
    e = pred - real
    ss = ((real - real.mean()) ** 2).sum()
    return {"MAE": float(np.abs(e).mean()), "RMSE": float(np.sqrt((e ** 2).mean())),
            "R2": float(1 - (e ** 2).sum() / ss) if ss > 0 else float("nan")}


def tabla_predicciones(d: Datos, idx_meses: np.ndarray, pred: np.ndarray) -> pd.DataFrame:
    """Formato común de results/predicciones: ubigeo, periodo, real, predicho (+ valido para filtrar métricas)."""
    t, n = np.meshgrid(idx_meses, np.arange(len(d.ubigeos)), indexing="ij")
    return pd.DataFrame({
        "ubigeo": np.array(d.ubigeos)[n.ravel()],
        "periodo": np.array(d.periodos)[t.ravel()],
        "real": d.y[t.ravel(), n.ravel()].astype(int),
        "predicho": np.round(pred.ravel(), 4),
        "valido": d.valido[t.ravel(), n.ravel()],
    })
