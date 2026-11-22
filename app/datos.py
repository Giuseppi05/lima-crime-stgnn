"""Lectura de resultados para la interfaz (solo lectura).

Lee `results/`, `data/processed/` y `configs/`. No escribe en ninguno de ellos: las exportaciones
van a `app/exportes/` (ver `app/exportar.py`). Si un archivo no existe, el lector devuelve None y la
vista muestra un aviso [PENDIENTE: ...]; nunca se rellenan cifras.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parents[1]
RESULTS = RAIZ / "results"
PROCESSED = RAIZ / "data" / "processed"
FIGURAS_METODO = RAIZ / "figuras"
CONFIG = RAIZ / "configs" / "ventanas.yaml"
EXPORTES = RAIZ / "app" / "exportes"

NEURONALES = ["GE", "GC2", "GC1"]
ORDEN = ["GE", "GC2", "GC1", "xgboost", "mes_anterior", "promedio_movil_3", "mismo_mes_anio_anterior"]
NOMBRES = {"GE": "GE (ST-GNN vial)", "GC2": "GC₂ (ST-GNN geográfica)", "GC1": "GC₁ (GRU sin grafo)",
           "xgboost": "XGBoost", "mes_anterior": "Mes anterior", "promedio_movil_3": "Promedio móvil 3 meses",
           "mismo_mes_anio_anterior": "Mismo mes del año anterior"}
CLAVE_DE_NOMBRE = {v: k for k, v in NOMBRES.items()}
# igual que src/evaluar.py
PLAYA = ["SANTA MARIA DEL MAR", "PUNTA NEGRA", "SAN BARTOLO", "PUCUSANA", "PUNTA HERMOSA"]
SECTORES = ["bajo", "medio", "alto"]
VENTANAS_PRUEBA = ["1", "2", "3", "4"]
ALFA = 0.05
_PATRON_PRED = re.compile(r"^(.+)_([0-9P]+)_(\d+)\.csv$")


# ---------------------------------------------------------------- caché (solo dentro de Streamlit)
def _cache(f):
    try:
        import streamlit as st
        from streamlit.runtime import exists
        return st.cache_data(show_spinner=False)(f) if exists() else f
    except Exception:  # sin streamlit (pruebas): sin caché
        return f


# ---------------------------------------------------------------- versiones
@dataclass(frozen=True)
class Version:
    clave: str
    etiqueta: str
    fichas: Path
    predicciones: Path | None = None
    figuras: Path | None = None
    atencion: Path | None = None
    yaml: Path | None = None
    articulo: bool = False

    def archivo(self, nombre: str) -> Path:
        return self.fichas / nombre

    def numero(self) -> tuple[int, ...] | None:
        """Número de versión (p. ej. (2, 1)) si se conoce."""
        texto = None
        if self.yaml is not None and self.yaml.exists():
            texto = str((leer_yaml(str(self.yaml)).get("version") or {}).get("actual", ""))
        elif re.fullmatch(r"v\d+(\.\d+)*", self.clave):
            texto = self.clave
        return numero_version(texto) if texto else None


def numero_version(texto: str) -> tuple[int, ...] | None:
    m = re.search(r"v?(\d+(?:\.\d+)*)", str(texto))
    return tuple(int(x) for x in m.group(1).split(".")) if m else None


def _si_existe(p: Path) -> Path | None:
    return p if p.exists() else None


@_cache
def leer_yaml(ruta: str) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def version_actual() -> str:
    if not CONFIG.exists():
        return "?"
    return str((leer_yaml(str(CONFIG)).get("version") or {}).get("actual", "?"))


def detectar_versiones(results: Path = RESULTS) -> list[Version]:
    """v1 (`results/v1/`), la del artículo (`results/fichas/`), cualquier `results/vN/` y cada
    `results/experimentos/<nombre>/fichas/`. Se detectan al iniciar: las nuevas aparecen solas."""
    vs: list[Version] = []
    actual = version_actual()
    for d in results.glob("v*"):
        if d.is_dir() and re.fullmatch(r"v\d+(\.\d+)*", d.name):
            fichas = d / "fichas" if (d / "fichas").is_dir() else d
            vs.append(Version(clave=d.name, etiqueta=f"{d.name} · results/{d.name}", fichas=fichas,
                              predicciones=_si_existe(d / "predicciones"), figuras=_si_existe(d / "figuras"),
                              atencion=_si_existe(d / "atencion")))
    if (results / "fichas").is_dir():
        vs.append(Version(clave=actual, etiqueta=f"{actual} · results/fichas (artículo)", fichas=results / "fichas",
                          predicciones=_si_existe(results / "predicciones"), figuras=_si_existe(results / "figuras"),
                          atencion=_si_existe(results / "atencion"), yaml=_si_existe(CONFIG), articulo=True))
    vs.sort(key=lambda v: (numero_version(v.clave) or (999,), not v.articulo))
    exp = results / "experimentos"
    if exp.is_dir():
        for d in sorted(exp.iterdir()):
            if (d / "fichas").is_dir():
                y = RAIZ / "configs" / "experimentos" / f"{d.name}.yaml"
                vs.append(Version(clave=f"exp:{d.name}", etiqueta=f"experimento {d.name}", fichas=d / "fichas",
                                  predicciones=_si_existe(d / "predicciones"), figuras=_si_existe(d / "figuras"),
                                  atencion=_si_existe(d / "atencion"), yaml=_si_existe(y)))
    return vs


def yamls_de(v: Version) -> list[Path]:
    """Yaml de la versión: el de configs (artículo o experimento) y cualquier *.yaml dentro de su carpeta."""
    out = [v.yaml] if v.yaml is not None and v.yaml.exists() else []
    carpetas = {v.fichas} | ({v.fichas.parent} if v.fichas.parent != RESULTS else set())
    for c in carpetas:
        out += sorted(c.glob("*.yaml"))
    return out


def correccion_cache_grafo(v: Version) -> bool:
    """True si el yaml de la versión declara `correccion_cache_grafo: true` (la clave la agrega el equipo cuando
    la atención y los casos adversos se recalculen con la corrección de fix/cache-grafo)."""
    return any(leer_yaml(str(y)).get("correccion_cache_grafo") is True for y in yamls_de(v))


def aviso_cache_grafo(v: Version) -> bool:
    """El aviso va en todas las versiones hasta que su yaml tenga `correccion_cache_grafo: true`."""
    return not correccion_cache_grafo(v)


# ---------------------------------------------------------------- lectores genéricos
@_cache
def _leer_csv(ruta: str, **kw) -> pd.DataFrame | None:
    p = Path(ruta)
    return pd.read_csv(p, **kw) if p.exists() else None


@_cache
def leer_texto(ruta: str) -> str | None:
    p = Path(ruta)
    return p.read_text(encoding="utf-8") if p.exists() else None


def metricas_global(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("metricas_global.csv")))


def metricas_por_ventana(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("metricas_por_ventana.csv")), dtype={"ventana": str})


def metricas_por_distrito(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("metricas_por_distrito.csv")), dtype={"ubigeo": str})


def corridas_neuronales(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("corridas_neuronales.csv")), dtype={"ventana": str})


def pruebas_estadisticas(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("pruebas_estadisticas.csv")))


def equidad_por_distrito(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("equidad_por_distrito.csv")), dtype={"ubigeo": str})


def equidad_resumen(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("equidad_resumen.csv")))


def equidad_sectores(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("equidad_sectores.csv")))


def nodos() -> pd.DataFrame | None:
    return _leer_csv(str(PROCESSED / "nodos.csv"), dtype={"ubigeo": str})


def comparaciones_md(*versiones: Version) -> dict[str, str]:
    """Archivos comparacion_*.md de las versiones dadas (y el de experimentos), por ruta relativa."""
    out = {}
    carpetas = {v.fichas for v in versiones} | {RESULTS / "experimentos"}
    for c in carpetas:
        if c.is_dir():
            for f in sorted(c.glob("comparacion*.md")):
                out[f.relative_to(RAIZ).as_posix()] = f.read_text(encoding="utf-8")
    return out


@_cache
def _leer_predicciones(carpeta: str) -> pd.DataFrame | None:
    filas = []
    for f in sorted(Path(carpeta).glob("*.csv")):
        m = _PATRON_PRED.match(f.name)
        if not m or "_rapido" in f.name:
            continue
        t = pd.read_csv(f, dtype={"ubigeo": str})
        filas.append(t.assign(modelo=m.group(1), ventana=m.group(2), semilla=int(m.group(3))))
    if not filas:
        return None
    p = pd.concat(filas, ignore_index=True)
    p["valido"] = p["valido"].astype(str).str.lower().eq("true")
    return p


def predicciones(v: Version) -> pd.DataFrame | None:
    """Todas las filas de `predicciones/` (incluidas las no válidas; filtrar con `valido`)."""
    return None if v.predicciones is None else _leer_predicciones(str(v.predicciones))


# ---------------------------------------------------------------- cálculos (sobre archivos existentes)
def _met(real: np.ndarray, pred: np.ndarray) -> dict:
    e = pred - real
    ss = ((real - real.mean()) ** 2).sum()
    return {"MAE": np.abs(e).mean(), "RMSE": np.sqrt((e ** 2).mean()),
            "R2": 1 - (e ** 2).sum() / ss if ss > 0 else np.nan}


def _metricas_grupo(p: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    filas = [{**dict(zip(por, k if isinstance(k, tuple) else (k,))), **_met(g.real.to_numpy(float), g.predicho.to_numpy(float))}
             for k, g in p.groupby(por, sort=False)]
    return pd.DataFrame(filas)


def metricas_global_desde_predicciones(pred: pd.DataFrame) -> pd.DataFrame:
    """Mismo cálculo que `src.evaluar`: 4 ventanas juntas por (modelo, semilla); media y sd entre semillas."""
    p = pred[pred.valido & pred.ventana.isin(VENTANAS_PRUEBA)]
    g = _metricas_grupo(p, ["modelo", "semilla"])
    m = g.groupby("modelo")[["MAE", "RMSE", "R2"]].mean()
    s = g.groupby("modelo")[["MAE", "RMSE", "R2"]].std(ddof=1).fillna(0.0)
    return m.join(s.add_suffix("_sd"))


def r2_por_distrito(pred: pd.DataFrame, modo: str = "ventana") -> pd.DataFrame:
    """R² por distrito calculado desde las predicciones válidas de las ventanas 1–4.

    modo="ventana": R² en los 12 meses de cada ventana y semilla; luego promedio entre ventanas (igual que
    el MAE por distrito de `src.evaluar`) y media ± sd entre semillas.
    modo="48": las 4 ventanas juntas (48 meses) por semilla; luego media ± sd entre semillas.
    Devuelve: modelo, ubigeo, R2, R2_sd, n_semillas.
    """
    p = pred[pred.valido & pred.ventana.isin(VENTANAS_PRUEBA)]
    if modo == "ventana":
        d = _metricas_grupo(p, ["modelo", "ventana", "semilla", "ubigeo"])
        d = d.groupby(["modelo", "semilla", "ubigeo"]).R2.mean().reset_index()
    elif modo == "48":
        d = _metricas_grupo(p, ["modelo", "semilla", "ubigeo"])
    else:
        raise ValueError(modo)
    g = d.groupby(["modelo", "ubigeo"]).R2
    return pd.DataFrame({"R2": g.mean(), "R2_sd": g.std(ddof=1), "n_semillas": g.size()}).reset_index()


def verificar_mismo_conjunto(pred: pd.DataFrame) -> pd.DataFrame:
    """Por ventana: ¿todos los archivos tienen las mismas celdas (ubigeo, periodo), el mismo `valido` y el mismo
    valor real? (verificación de la fase de Evaluación, Tabla II del AVC3)."""
    filas = []
    for w, gw in pred.groupby("ventana", sort=True):
        ref = None
        distintos = []
        archivos = 0
        for (m, s), g in gw.groupby(["modelo", "semilla"], sort=True):
            archivos += 1
            k = g.sort_values(["ubigeo", "periodo"])[["ubigeo", "periodo", "valido", "real"]].reset_index(drop=True)
            if ref is None:
                ref = k
            elif not k.equals(ref):
                distintos.append(f"{m}_{w}_{s}")
        filas.append({"ventana": w, "archivos": archivos, "celdas": len(ref), "validas": int(ref.valido.sum()),
                      "meses": ref.periodo.nunique(), "distritos": ref.ubigeo.nunique(),
                      "desde": ref.periodo.min(), "hasta": ref.periodo.max(),
                      "iguales": not distintos, "distintos": ", ".join(distintos)})
    return pd.DataFrame(filas)


def regla_avc3(fila: pd.Series) -> str:
    """Regla del estudio recalculada con las columnas del propio archivo de pruebas."""
    ok = fila.MAE_GE < fila.MAE_rival and fila.RMSE_GE < fila.RMSE_rival and fila.p < ALFA
    return "sí" if ok else "no"


def brecha_entre_sectores(resumen: pd.DataFrame) -> pd.Series:
    """Máximo − mínimo de las medias de error relativo por sector (columnas media_bajo/medio/alto del archivo)."""
    cols = [f"media_{s}" for s in SECTORES]
    return resumen[cols].max(axis=1) - resumen[cols].min(axis=1)


def composicion_sectores(epd: pd.DataFrame) -> pd.DataFrame:
    d = epd.drop_duplicates("ubigeo")[["ubigeo", "distrito", "sector", "volumen_entrenamiento"]]
    filas = []
    for s in SECTORES:
        g = d[d.sector == s].sort_values("distrito")
        filas.append({"sector": s, "n": len(g), "vol_min": g.volumen_entrenamiento.min(),
                      "vol_max": g.volumen_entrenamiento.max(), "distritos": ", ".join(g.distrito)})
    return pd.DataFrame(filas)


def periodos_prueba() -> dict[str, tuple[str, str]]:
    """Ventana → (inicio, fin) del conjunto de prueba según el yaml."""
    if not CONFIG.exists():
        return {}
    c = leer_yaml(str(CONFIG))
    out = {str(k): tuple(v["prueba"]) for k, v in (c.get("ventanas") or {}).items()}
    out.update({str(k): tuple(v["prueba"]) for k, v in (c.get("ventana_pandemia") or {}).items()})
    return out
