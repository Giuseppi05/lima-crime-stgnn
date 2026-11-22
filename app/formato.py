"""Formato de cifras como en el artículo: coma decimal, espacio de miles y 3 decimales para MAE y RMSE."""
from __future__ import annotations

import math

import pandas as pd


def es_nulo(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x)) or (not isinstance(x, str) and pd.isna(x))


def num(x, dec: int = 3) -> str:
    """33.4689 → '33,469'; 957705 → '957 705'."""
    if es_nulo(x):
        return "—"
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", " ").replace(".", ",")


def entero(x) -> str:
    return "—" if es_nulo(x) else num(round(float(x)), 0)


def ms(m, sd, dec: int = 3) -> str:
    """Media ± desviación. Sin desviación (una sola corrida determinista) se muestra solo la media."""
    if es_nulo(m):
        return "—"
    if es_nulo(sd) or float(sd) == 0.0:
        return num(m, dec)
    return f"{num(m, dec)} ± {num(sd, dec)}"


def p_valor(p) -> str:
    if es_nulo(p):
        return "—"
    return "< 0,001" if float(p) < 0.001 else num(p, 3)


def romano(n: int) -> str:
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, r in vals:
        while n >= v:
            out += r
            n -= v
    return out


def mes(periodo: str) -> str:
    """'2022-10' → 'oct. 2022'."""
    meses = ["ene.", "feb.", "mar.", "abr.", "may.", "jun.", "jul.", "ago.", "sep.", "oct.", "nov.", "dic."]
    a, m = str(periodo).split("-")[:2]
    return f"{meses[int(m) - 1]} {a}"


def nombre_propio(texto: str) -> str:
    """'SAN JUAN DE LURIGANCHO' → 'San Juan de Lurigancho'."""
    menores = {"de", "del", "la", "las", "los", "y", "el"}
    palabras = str(texto).lower().split(" ")
    return " ".join(w if (i and w in menores) else w.capitalize() for i, w in enumerate(palabras))
