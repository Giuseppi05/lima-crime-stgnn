"""Rutas, semillas y utilidades compartidas por todos los scripts."""
from __future__ import annotations

import os
import random
import sys
from pathlib import Path

import numpy as np
import yaml

RAIZ = Path(__file__).resolve().parents[1]
CSV_CRUDO = RAIZ.parent / "Recursos" / "DATASET_Denuncias Policiales - Enero 2018 a Septiembre 2026.csv"
DATA = RAIZ / "data"
EXTERNOS = DATA / "external"
PROCESADOS = DATA / "processed"
# --rapido solo comprueba que el código corre: sus salidas van a otra carpeta y nunca al artículo
MODO_RAPIDO = "--rapido" in sys.argv
RESULTADOS = RAIZ / ("results_rapido" if MODO_RAPIDO else "results")
# opciones extra (fuera del AVC3): cada experimento tiene su configuración y su carpeta, sin tocar los resultados del artículo
EXPERIMENTO = os.environ.get("GNN_EXPERIMENTO", "")
if EXPERIMENTO:
    RESULTADOS = RESULTADOS / "experimentos" / EXPERIMENTO
FICHAS = RESULTADOS / "fichas"
FIGURAS = RESULTADOS / "figuras"
PREDICCIONES = RESULTADOS / "predicciones"
ATENCION = RESULTADOS / "atencion"
CONFIG_VENTANAS = RAIZ / "configs" / (f"experimentos/{EXPERIMENTO}.yaml" if EXPERIMENTO else "ventanas.yaml")

for _d in (EXTERNOS, PROCESADOS, FICHAS, FIGURAS, PREDICCIONES, ATENCION):
    _d.mkdir(parents=True, exist_ok=True)


def fijar_semilla(semilla: int) -> None:
    """Fija todas las fuentes de azar; en CPU con algoritmos deterministas las corridas se repiten exactas."""
    os.environ["PYTHONHASHSEED"] = str(semilla)
    random.seed(semilla)
    np.random.seed(semilla)
    try:
        import torch

        torch.manual_seed(semilla)
        torch.use_deterministic_algorithms(True)
        torch.set_num_threads(1)  # un solo hilo: evita sumas en distinto orden entre corridas
    except ImportError:
        pass


def leer_config() -> dict:
    with open(CONFIG_VENTANAS, encoding="utf-8") as f:
        return yaml.safe_load(f)


def guardar_config(cfg: dict) -> None:
    with open(CONFIG_VENTANAS, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)


def leer_panel():
    import pandas as pd

    return pd.read_csv(PROCESADOS / "panel.csv", dtype={"ubigeo": str})
