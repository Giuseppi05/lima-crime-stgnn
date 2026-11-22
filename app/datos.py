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
        if d.name == actual and (results / "fichas").is_dir():
            continue  # resumen de la versión actual: ya aparece como la del artículo (results/fichas)
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


# ---------------------------------------------------------------- fichas en Markdown
def tablas_md(texto: str) -> list[tuple[str, pd.DataFrame]]:
    """Tablas de un .md del repositorio, con el encabezado (##/###) bajo el que aparecen. Celdas como texto."""
    out, titulo, bloque = [], "", []

    def cerrar():
        if len(bloque) >= 2:
            filas = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in bloque]
            cuerpo = [f for f in filas[1:] if not all(re.fullmatch(r":?-{3,}:?", c) for c in f)]
            out.append((titulo, pd.DataFrame(cuerpo, columns=filas[0])))
        bloque.clear()

    for ln in texto.splitlines():
        if ln.lstrip().startswith("|"):
            bloque.append(ln)
            continue
        cerrar()
        if ln.startswith("#"):
            titulo = ln.lstrip("#").strip()
    cerrar()
    return out


def tabla_md(texto: str, titulo: str, n: int = 0) -> pd.DataFrame | None:
    t = [df for tit, df in tablas_md(texto) if tit == titulo]
    return t[n] if len(t) > n else None


def seccion_md(texto: str, titulo: str) -> str | None:
    """Texto de la sección `## titulo` (o ###) hasta el siguiente encabezado de igual o mayor nivel."""
    lineas = texto.splitlines()
    for i, ln in enumerate(lineas):
        m = re.match(r"^(#+)\s+(.*)$", ln)
        if m and m.group(2).strip() == titulo:
            nivel, fin = len(m.group(1)), len(lineas)
            for j in range(i + 1, len(lineas)):
                m2 = re.match(r"^(#+)\s", lineas[j])
                if m2 and len(m2.group(1)) <= nivel:
                    fin = j
                    break
            return "\n".join(lineas[i + 1:fin]).strip()
    return None


def decimal_es(texto: str) -> str:
    """Coma decimal en números sueltos de un texto ('65.7 %' → '65,7 %'); no toca versiones como 2.2.0."""
    return re.sub(r"(?<![\w.])(-?\d+)\.(\d+)(?![\w.])", r"\1,\2", texto)


def calidad_md(v: Version) -> str | None:
    return leer_texto(str(v.archivo("calidad.md")))


def validacion_grafos_md(v: Version) -> str | None:
    return leer_texto(str(v.archivo("validacion_grafos.md")))


# ---------------------------------------------------------------- panel y grafos (data/processed)
def panel() -> pd.DataFrame | None:
    return _leer_csv(str(PROCESSED / "panel.csv"), dtype={"ubigeo": str})


def cobertura(p: pd.DataFrame) -> pd.DataFrame:
    n = p.estado.value_counts()
    estados = ["observado", "cero", "sin_informacion"]
    return pd.DataFrame({"estado": estados, "celdas": [int(n.get(e, 0)) for e in estados],
                         "pct": [100 * n.get(e, 0) / len(p) for e in estados]})


def cobertura_por_distrito(p: pd.DataFrame) -> pd.DataFrame:
    t = p[p.estado != "observado"].pivot_table(index="distrito", columns="estado", values="periodo",
                                                aggfunc="count", fill_value=0)
    for c in ["cero", "sin_informacion"]:
        if c not in t:
            t[c] = 0
    return t[["cero", "sin_informacion"]].reset_index()


def aristas(nombre: str) -> pd.DataFrame | None:
    """nombre: 'geo' o 'vial'. Columnas origen, destino, peso (ubigeo como texto)."""
    return _leer_csv(str(PROCESSED / f"aristas_{nombre}.csv"), dtype={"origen": str, "destino": str})


def _pares(a: pd.DataFrame) -> set[tuple[str, str]]:
    return {tuple(sorted(x)) for x in zip(a.origen, a.destino)}


def solapamiento(geo: pd.DataFrame, vial: pd.DataFrame) -> dict:
    """Aristas no dirigidas comunes, exclusivas y Jaccard = |común| / |unión|."""
    g, v = _pares(geo), _pares(vial)
    return {"geo": len(g), "vial": len(v), "comunes": len(g & v), "solo_geo": len(g - v), "solo_vial": len(v - g),
            "union": len(g | v), "jaccard": len(g & v) / len(g | v) if g | v else float("nan"),
            "pares_solo_geo": sorted(g - v), "pares_solo_vial": sorted(v - g)}


def resumen_grafo(a: pd.DataFrame, ubigeos: list[str]) -> dict:
    """Aristas, conexión (búsqueda en anchura) y grados, desde la lista de aristas."""
    vecinos = {u: set() for u in ubigeos}
    for o, d in _pares(a):
        vecinos[o].add(d)
        vecinos[d].add(o)
    visto, pila = {ubigeos[0]}, [ubigeos[0]]
    while pila:
        for w in vecinos[pila.pop()] - visto:
            visto.add(w)
            pila.append(w)
    grados = np.array([len(vecinos[u]) for u in ubigeos])
    return {"aristas": len(_pares(a)), "conectado": len(visto) == len(ubigeos), "grado_medio": grados.mean(),
            "grado_min": int(grados.min()), "grado_max": int(grados.max())}


def distancia_red_vs_recta(nod: pd.DataFrame) -> dict | None:
    """Pares con distancia por red menor que la recta entre los puntos UTM de nodos.csv (la matriz de red viene
    redondeada a 0,1 m, por eso la tolerancia de 0,1 m)."""
    m = _leer_csv(str(PROCESSED / "matriz_distancia_red_m.csv"), index_col=0)
    if m is None:
        return None
    m.index, m.columns = m.index.astype(str), m.columns.astype(str)
    n = nod.set_index("ubigeo").loc[m.index]
    xy = n[["x_utm", "y_utm"]].to_numpy(float)
    recta = np.hypot(xy[:, None, 0] - xy[None, :, 0], xy[:, None, 1] - xy[None, :, 1])
    red = m.to_numpy(float)
    off = ~np.eye(len(xy), dtype=bool)
    cociente = red[off] / recta[off]
    return {"pares": int(off.sum() // 2), "violaciones": int(((red < recta - 0.1) & off).sum() // 2),
            "cociente_min": float(cociente.min()), "cociente_mediana": float(np.median(cociente))}


# ---------------------------------------------------------------- configuración elegida (Modelado)
def configuracion(v: Version) -> dict | None:
    if v.yaml is None or not v.yaml.exists():
        return None
    return leer_yaml(str(v.yaml))


def archivo_ajuste(v: Version) -> str:
    """Mismo nombre que usa `src/entrenar.py` (AJUSTE_CSV): sin sufijo en v1 y v2; si no, con el nombre de la versión."""
    clave = version_actual() if v.articulo else v.clave.removeprefix("exp:")
    return "ajuste_hiperparametros.csv" if clave in ("v1", "v2") else f"ajuste_hiperparametros_{clave}.csv"


def ajuste_hiperparametros(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo(archivo_ajuste(v))), dtype={"ventana": str})


def multianual(cfg: dict | None) -> bool:
    return (cfg or {}).get("seleccion") == "multianual"


def criterio_seleccion(ajuste: pd.DataFrame, cfg: dict | None) -> pd.DataFrame:
    """Agrega `criterio`: el MAE con que se eligió cada configuración. Es el de su ventana o, con
    `seleccion: multianual`, el promedio de los años de validación de las ventanas 1…w (como `fase_congelar`)."""
    a = ajuste.copy()
    a["criterio"] = a.mae_validacion
    if multianual(cfg):
        clave = ["modelo", "salida", "oculto", "lr", "dropout", "entrada_meses"]
        piv = a[a.ventana.isin(VENTANAS_PRUEBA)].pivot_table(index=clave, columns="ventana", values="mae_validacion")
        orden = sorted(piv.columns)
        for k, w in enumerate(orden):
            prom = piv[orden[:k + 1]].mean(axis=1).rename("prom").reset_index()
            fila = a.ventana == w
            a.loc[fila, "criterio"] = a.loc[fila, clave].merge(prom, on=clave, how="left")["prom"].to_numpy()
    return a


def verificar_configuracion(cfg: dict, ajuste: pd.DataFrame, salida: str) -> pd.DataFrame:
    """¿La configuración del yaml es la de menor criterio de validación en la grilla (con la salida elegida)?"""
    a = criterio_seleccion(ajuste, cfg)
    filas = []
    for m in NEURONALES:
        for w, h in (cfg.get("hiperparametros", {}).get(m) or {}).items():
            s = a[(a.modelo == m) & (a.ventana == str(w)) & (a.salida == salida)]
            if s.empty:
                continue
            b = s.loc[s.criterio.idxmin()]
            igual = (b.oculto, b.lr, b.dropout, b.entrada_meses) == (h["oculto"], h["lr"], h["dropout"],
                                                                     h["entrada_meses"])
            filas.append({"modelo": m, "ventana": str(w), "combinaciones": len(s),
                          "mae_yaml": h.get("mae_validacion_multianual", h["mae_validacion"]),
                          "mae_min_grilla": b.criterio, "coincide": bool(igual)})
    return pd.DataFrame(filas)


def eleccion_salida_desde_ajuste(ajuste: pd.DataFrame, cfg: dict | None = None) -> pd.Series:
    """MAE de validación promedio por salida: mejor configuración por modelo y ventana (1–4) según el criterio de
    selección, luego el promedio de su MAE de validación (como `fase_congelar`)."""
    a = criterio_seleccion(ajuste, cfg)
    a = a[a.ventana.isin(VENTANAS_PRUEBA)]
    mejor = a.loc[a.groupby(["modelo", "ventana", "salida"]).criterio.idxmin()]
    return mejor.groupby("salida").mae_validacion.mean()


# ---------------------------------------------------------------- atención (OE3)
def atencion_temporal(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("atencion_temporal.csv")))


def atencion_spearman(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("atencion_spearman.csv")))


def atencion_pares(v: Version, modelo: str) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo(f"atencion_espacial_pares_{modelo}.csv")), dtype={"a": str, "b": str})


def atencion_fidelidad(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("atencion_fidelidad.csv")), dtype={"ventana": str})


def atencion_md(v: Version) -> str | None:
    return leer_texto(str(v.archivo("atencion.md")))


@_cache
def _autoatencion(carpeta: str) -> dict[str, float]:
    """Peso medio del propio distrito en el GAT (origen = destino), ventanas 1–4 y todas las semillas."""
    out = {}
    for modelo in ["GE", "GC2"]:
        suma, n = 0.0, 0
        for f in sorted(Path(carpeta).glob(f"{modelo}_*_*.csv")):
            if not re.match(rf"^{modelo}_[1-4]_\d+\.csv$", f.name):
                continue
            t = pd.read_csv(f, dtype={"origen": str, "destino": str})
            e = t[(t.tipo == "espacial") & (t.origen == t.destino)].peso
            suma, n = suma + e.sum(), n + len(e)
        if n:
            out[modelo] = suma / n
    return out


def autoatencion(v: Version) -> dict[str, float] | None:
    return None if v.atencion is None else _autoatencion(str(v.atencion))


def entrada_elegida(cfg: dict) -> pd.DataFrame:
    """Meses de entrada (L) que eligió la validación por modelo y ventana (1–4)."""
    filas = [{"modelo": m, "ventana": str(w), "L": h["entrada_meses"]}
             for m in NEURONALES for w, h in ((cfg.get("hiperparametros") or {}).get(m) or {}).items()
             if str(w) in VENTANAS_PRUEBA]
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- casos adversos
CASOS_GRAFO = ["aristas eliminadas", "ruido en coordenadas"]  # dependen del grafo: en revisión por el caché


def casos_adversos(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("casos_adversos.csv")), dtype={"ventana": str})


def casos_adversos_md(v: Version) -> str | None:
    return leer_texto(str(v.archivo("casos_adversos.md")))


def resumen_adversos(c: pd.DataFrame) -> pd.DataFrame:
    """Misma agregación que `src.adversos`: cambio % del MAE frente al caso limpio de la misma ventana y semilla."""
    base = c[c.caso == "limpio"].set_index(["ventana", "semilla"])[["MAE"]].rename(columns={"MAE": "MAE_limpio"})
    r = c.join(base, on=["ventana", "semilla"])
    r["dMAE_pct"] = (r.MAE / r.MAE_limpio - 1) * 100
    return r.groupby(["caso", "nivel"], sort=False).agg(
        MAE=("MAE", "mean"), MAE_sd=("MAE", "std"), RMSE=("RMSE", "mean"), R2=("R2", "mean"),
        cambio_MAE_pct=("dMAE_pct", "mean"), corridas_peor=("dMAE_pct", lambda x: int((x > 0).sum())),
        n=("MAE", "size")).reset_index()


def pandemia(v: Version) -> pd.DataFrame | None:
    """`pandemia.csv` (cabecera de dos niveles) → modelo, MAE, MAE_sd, RMSE, RMSE_sd, R2, R2_sd."""
    ruta = v.archivo("pandemia.csv")
    if not ruta.exists():
        return None
    t = pd.read_csv(ruta, header=[0, 1], index_col=0)
    t.columns = [f"{a}_sd" if b == "std" else a for a, b in t.columns]
    return t.rename_axis("modelo").reset_index()


def metricas_referencias_pandemia(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("metricas_referencias_pandemia.csv")), dtype={"ventana": str})


def corridas_pandemia(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("corridas_neuronales_pandemia.csv")), dtype={"ventana": str})


# ---------------------------------------------------------------- mapa de riesgo (despliegue)
def mapa_riesgo(v: Version) -> pd.DataFrame | None:
    return _leer_csv(str(v.archivo("mapa_riesgo_distrital.csv")), dtype={"ubigeo": str})


GPKG_INEI = RAIZ / "data" / "external" / "inei_distrito_2023" / "DISTRITO.gpkg"
