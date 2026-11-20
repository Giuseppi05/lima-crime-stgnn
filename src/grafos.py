"""Preparación de los datos: coordenadas de los nodos, red vial y los dos grafos (GE vial, GC₂ geográfico).

Uso: python -m src.grafos
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
from shapely.geometry import Point

from src.comun import EXTERNOS, FICHAS, FIGURAS, PROCESADOS, leer_panel

CRS_UTM = "EPSG:32718"
GPKG_INEI = EXTERNOS / "inei_distrito_2023" / "DISTRITO.gpkg"
BUFFER_CONTIGUIDAD_M = 25  # 25 m por lado: tolera huecos de digitalización de hasta ~50 m
BUFFER_RED_M = 1000        # margen para no cortar tramos que salen y vuelven en el borde
PESO_MINIMO = 0.01         # si la fórmula da 0 en algún enlace, se sube para que la arista no desaparezca


def orden_nodos() -> pd.DataFrame:
    """Mismo orden de ubigeo que el panel: es el índice de fila/columna de todas las matrices."""
    p = leer_panel()
    return p[["ubigeo", "distrito"]].drop_duplicates().reset_index(drop=True)


def cargar_limites() -> tuple[gpd.GeoDataFrame, list[str]]:
    if not GPKG_INEI.exists():
        raise SystemExit(f"Falta {GPKG_INEI}: descargar Distrito.rar de https://ide.inei.gob.pe/ (ver FUENTES.md)")
    orden = orden_nodos()
    g = gpd.read_file(GPKG_INEI)
    g["ubigeo"] = g["ubigeo"].astype(str).str.zfill(6)
    sin_cruce = sorted(set(orden.ubigeo) - set(g.ubigeo))
    g = orden.merge(g[["ubigeo", "nombdist", "geometry"]], on="ubigeo", how="left")
    g = gpd.GeoDataFrame(g, geometry="geometry", crs="EPSG:4326").to_crs(CRS_UTM)
    return g, sin_cruce


def calcular_nodos(lim: gpd.GeoDataFrame) -> tuple[pd.DataFrame, list[str]]:
    cen = lim.geometry.centroid
    dentro = cen.within(lim.geometry)
    punto = cen.where(dentro, lim.geometry.representative_point())
    cambiados = lim.loc[~dentro, "distrito"].tolist()
    geo = gpd.GeoSeries(punto, crs=CRS_UTM).to_crs("EPSG:4326")
    nodos = pd.DataFrame({
        "ubigeo": lim.ubigeo, "distrito": lim.distrito,
        "lat": geo.y.round(6), "lon": geo.x.round(6),
        "x_utm": punto.x.round(2), "y_utm": punto.y.round(2),
        "area_km2": (lim.geometry.area / 1e6).round(3),
        "punto": np.where(dentro, "centroide", "representative_point"),
    })
    return nodos, cambiados


def grafo_geografico(lim: gpd.GeoDataFrame) -> np.ndarray:
    n = len(lim)
    a = np.zeros((n, n))
    geoms = lim.geometry.buffer(BUFFER_CONTIGUIDAD_M).values
    for i in range(n):
        for j in range(i + 1, n):
            if geoms[i].intersects(geoms[j]):
                a[i, j] = a[j, i] = 1.0
    return a


def descargar_red(lim: gpd.GeoDataFrame) -> tuple[nx.MultiDiGraph, Path]:
    existentes = sorted(EXTERNOS.glob("osm_lima_drive_*.graphml"))
    if existentes:  # idempotente: se reutiliza la descarga fechada
        ruta = existentes[-1]
        return ox.load_graphml(ruta), ruta
    zona = gpd.GeoSeries([lim.union_all().buffer(BUFFER_RED_M)], crs=CRS_UTM).to_crs("EPSG:4326").iloc[0]
    ox.settings.cache_folder = str(EXTERNOS / "osmnx_cache")
    G = ox.graph_from_polygon(zona, network_type="drive", retain_all=False, truncate_by_edge=True)
    ruta = EXTERNOS / f"osm_lima_drive_{dt.date.today().isoformat()}.graphml"
    ox.save_graphml(G, ruta)
    return G, ruta


def asignar_nodos_osm(Gu: nx.MultiGraph, lim: gpd.GeoDataFrame) -> pd.Series:
    """Distrito (índice 0..42) de cada nodo OSM; -1 si cae fuera de Lima (p. ej. Callao)."""
    nd = ox.graph_to_gdfs(Gu, edges=False)[["geometry"]].to_crs(CRS_UTM)
    poli = lim[["geometry"]].reset_index(names="idx")
    dentro = gpd.sjoin(nd, poli, how="left", predicate="within")
    dentro = dentro[~dentro.index.duplicated()]["idx"]
    faltan = dentro[dentro.isna()].index
    if len(faltan):
        # nodos en los huecos de digitalización entre polígonos: al distrito más cercano a ≤ 50 m
        cerca = gpd.sjoin_nearest(nd.loc[faltan], poli, how="left", max_distance=2 * BUFFER_CONTIGUIDAD_M)
        cerca = cerca[~cerca.index.duplicated()]["idx"]
        dentro.loc[faltan] = cerca
    return dentro.fillna(-1).astype(int)


def contar_cruces(Gu: nx.MultiGraph, asig: pd.Series, n: int) -> np.ndarray:
    cruces = np.zeros((n, n), dtype=int)
    a = asig.to_dict()
    for u, v, _ in Gu.edges(keys=True):
        du, dv = a[u], a[v]
        if du >= 0 and dv >= 0 and du != dv:
            cruces[du, dv] += 1
            cruces[dv, du] += 1
    return cruces


def distancias_red(Gu: nx.MultiGraph, xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Distancia por la red entre centroides: tramo recto al nodo vial más cercano + Dijkstra (length) + tramo recto.

    Los tramos de acceso se suman para que la distancia sea entre centroides y no entre nodos viales.
    """
    comp = max(nx.connected_components(Gu), key=len)
    Gc = Gu.subgraph(comp).copy()
    Gp = ox.project_graph(Gc, to_crs=CRS_UTM)
    ids = ox.distance.nearest_nodes(Gp, xy[:, 0], xy[:, 1])
    nx_ = np.array([Gp.nodes[i]["x"] for i in ids])
    ny_ = np.array([Gp.nodes[i]["y"] for i in ids])
    acceso = np.hypot(xy[:, 0] - nx_, xy[:, 1] - ny_)
    n = len(xy)
    d = np.zeros((n, n))
    G1 = nx.Graph()  # grafo simple con el tramo más corto entre cada par de nodos
    for u, v, data in Gc.edges(data=True):
        if not G1.has_edge(u, v) or data["length"] < G1[u][v]["length"]:
            G1.add_edge(u, v, length=data["length"])
    for i in range(n):
        lon = nx.single_source_dijkstra_path_length(G1, ids[i], weight="length")
        for j in range(n):
            if i != j:
                d[i, j] = acceso[i] + lon[ids[j]] + acceso[j]
    d = (d + d.T) / 2  # simetría numérica
    return d, acceso


def peso_vial(cruces: np.ndarray, d: np.ndarray) -> np.ndarray:
    """w = 0.5·log1p(n_AB)/max log1p(n) + 0.5·(1 − d_AB/max d), sobre las aristas con n_AB ≥ 1."""
    m = cruces >= 1
    lc = np.log1p(cruces)
    w = 0.5 * lc / lc[m].max() + 0.5 * (1 - d / d[m].max())
    w = np.where(m, np.maximum(w, PESO_MINIMO), 0.0)
    return w


def construir_vial(Gu, asig, nodos_xy, n, cruces=None):
    """Reutilizable en los casos adversos (ruido en coordenadas): recalcula distancias y pesos."""
    if cruces is None:
        cruces = contar_cruces(Gu, asig, n)
    d, acceso = distancias_red(Gu, nodos_xy)
    return peso_vial(cruces, d), cruces, d, acceso


def a_lista(w: np.ndarray, ubigeos: list[str]) -> pd.DataFrame:
    i, j = np.triu_indices_from(w, k=1)
    sel = w[i, j] > 0
    return pd.DataFrame({"origen": np.array(ubigeos)[i[sel]], "destino": np.array(ubigeos)[j[sel]],
                         "peso": w[i, j][sel].round(6)})


def mapa(lim, nodos, ageo, avial, ruta):
    fig, axs = plt.subplots(1, 2, figsize=(13, 8))
    for ax, a, tit, col in [(axs[0], ageo, "Grafo geográfico (GC₂): contigüidad", "#2e75b6"),
                            (axs[1], avial, "Grafo vial (GE): tramos que cruzan, ancho = peso", "#c55a11")]:
        lim.boundary.plot(ax=ax, color="lightgray", lw=.6)
        x, y = nodos.x_utm.values, nodos.y_utm.values
        i, j = np.nonzero(np.triu(a))
        for a_, b_ in zip(i, j):
            ax.plot([x[a_], x[b_]], [y[a_], y[b_]], color=col, lw=.5 + 2.5 * a[a_, b_], alpha=.8)
        ax.scatter(x, y, s=14, color="black", zorder=3)
        for k in range(len(nodos)):
            ax.annotate(nodos.distrito.iloc[k].title(), (x[k], y[k]), fontsize=5, xytext=(2, 2),
                        textcoords="offset points")
        ax.set_title(f"{tit}\n{len(i)} aristas", fontsize=10)
        ax.set_axis_off()
    fig.suptitle("Nodos (centroides) y aristas de los 43 distritos de Lima Metropolitana, UTM 18S")
    fig.tight_layout()
    fig.savefig(ruta, dpi=170)
    plt.close(fig)


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    lim, sin_cruce = cargar_limites()
    if sin_cruce or lim.geometry.isna().any():
        raise SystemExit(f"UBIGEO sin cruce con la capa INEI: {sin_cruce}")
    nodos, cambiados = calcular_nodos(lim)
    ubig = nodos.ubigeo.tolist()
    n = len(nodos)

    ageo = grafo_geografico(lim)

    G, ruta_osm = descargar_red(lim)
    Gu = ox.convert.to_undirected(G)  # cada tramo una sola vez aunque sea de doble sentido
    asig = asignar_nodos_osm(Gu, lim)
    xy = nodos[["x_utm", "y_utm"]].to_numpy()
    avial, cruces, dred, acceso = construir_vial(Gu, asig, xy, n)

    # Guardado: mismo orden que el panel
    nodos.to_csv(PROCESADOS / "nodos.csv", index=False)
    a_lista(ageo, ubig).to_csv(PROCESADOS / "aristas_geo.csv", index=False)
    a_lista(avial, ubig).to_csv(PROCESADOS / "aristas_vial.csv", index=False)
    pd.DataFrame(ageo, index=ubig, columns=ubig).to_csv(PROCESADOS / "matriz_geo.csv")
    pd.DataFrame(avial, index=ubig, columns=ubig).to_csv(PROCESADOS / "matriz_vial.csv")
    pd.DataFrame(cruces, index=ubig, columns=ubig).to_csv(PROCESADOS / "matriz_tramos_cruce.csv")
    pd.DataFrame(dred.round(1), index=ubig, columns=ubig).to_csv(PROCESADOS / "matriz_distancia_red_m.csv")
    asig.rename("distrito_idx").to_csv(PROCESADOS / "osm_nodo_distrito.csv")

    # Validaciones
    drecta = np.hypot(xy[:, None, 0] - xy[None, :, 0], xy[:, None, 1] - xy[None, :, 1])
    off = ~np.eye(n, dtype=bool)
    viol = int(((dred < drecta - 1e-6) & off).sum() // 2)
    dentro = gpd.GeoSeries([Point(p) for p in xy], crs=CRS_UTM).within(lim.geometry.reset_index(drop=True))
    con_geo = nx.is_connected(nx.from_numpy_array(ageo))
    con_vial = nx.is_connected(nx.from_numpy_array(avial))
    solo_geo = int((np.triu((ageo > 0) & (avial == 0))).sum())
    solo_vial = int((np.triu((avial > 0) & (ageo == 0))).sum())
    ruta_mapa = FIGURAS / "mapa_grafos.png"
    mapa(lim, nodos, ageo, avial, ruta_mapa)
    # longitud del límite compartido: medida continua de la contigüidad, para el contraste del OE3
    lk = np.zeros((n, n))
    for i_, j_ in zip(*np.nonzero(np.triu(ageo))):
        lk[i_, j_] = lk[j_, i_] = lim.geometry.iloc[i_].boundary.intersection(
            lim.geometry.iloc[j_].buffer(2 * BUFFER_CONTIGUIDAD_M)).length / 1000
    pd.DataFrame(lk.round(4), index=ubig, columns=ubig).to_csv(PROCESADOS / "matriz_limite_km.csv")

    ev = a_lista(avial, ubig).assign(
        n_tramos=[cruces[ubig.index(o), ubig.index(d)] for o, d in zip(*[a_lista(avial, ubig)[c] for c in ("origen", "destino")])],
        d_red_km=[dred[ubig.index(o), ubig.index(d)] / 1000 for o, d in zip(*[a_lista(avial, ubig)[c] for c in ("origen", "destino")])],
    )
    nom = dict(zip(nodos.ubigeo, nodos.distrito))
    ev["par"] = ev.origen.map(nom) + " – " + ev.destino.map(nom)
    m = ["# Preparación de los datos: validación de los grafos\n",
         "Generado por `python -m src.grafos`. Nota. Elaboración propia.\n",
         "## Fuentes\n",
         f"- Límites: INEI, IDE, capa distrital actualizada al 2023 (`{GPKG_INEI.relative_to(GPKG_INEI.parents[2])}`).",
         f"- Red vial: OpenStreetMap vía OSMnx {ox.__version__}, `network_type='drive'`, `{ruta_osm.name}`.\n",
         "## Cruce por UBIGEO\n",
         f"Ubigeos del panel que cruzan con la capa INEI: {n - len(sin_cruce)} de 43. Sin cruce: {sin_cruce or 'ninguno'}.\n",
         "## Nodos\n",
         f"- Centroides que cayeron fuera de su polígono y se reemplazaron con `representative_point()`: "
         f"{len(cambiados)} ({', '.join(cambiados) if cambiados else 'ninguno'}).",
         f"- Puntos finales dentro de su polígono: {int(dentro.sum())} de {n}.\n",
         "## Red vial\n",
         f"- Nodos OSM: {Gu.number_of_nodes():,}; tramos (no dirigidos): {Gu.number_of_edges():,}.".replace(",", " "),
         f"- Nodos OSM asignados a uno de los 43 distritos: {int((asig >= 0).sum()):,}; fuera (Callao; mar o margen): "
         f"{int((asig < 0).sum()):,}.".replace(",", " "),
         f"- Distancia de acceso centroide → nodo vial más cercano: mediana {np.median(acceso):.0f} m, máxima {acceso.max():.0f} m.\n",
         "## Grafos\n",
         "| Grafo | Aristas | Conectado | Grado medio | Grado mín. | Grado máx. |\n| --- | --- | --- | --- | --- | --- |",
         f"| Geográfico (GC₂) | {int(np.triu(ageo > 0).sum())} | {'sí' if con_geo else 'NO'} | {(ageo > 0).sum(1).mean():.2f} | {(ageo > 0).sum(1).min()} | {(ageo > 0).sum(1).max()} |",
         f"| Vial (GE) | {int(np.triu(avial > 0).sum())} | {'sí' if con_vial else 'NO'} | {(avial > 0).sum(1).mean():.2f} | {(avial > 0).sum(1).min()} | {(avial > 0).sum(1).max()} |\n",
         f"Aristas solo en el geográfico: {solo_geo}; solo en el vial: {solo_vial}.\n",
         f"Peso vial: mínimo {ev.peso.min():.3f}, mediana {ev.peso.median():.3f}, máximo {ev.peso.max():.3f}. "
         f"Tramos que cruzan por arista: mediana {ev.n_tramos.median():.0f}, máximo {ev.n_tramos.max()}.\n",
         "## Distancia por red frente a distancia recta\n",
         f"Pares (de {n*(n-1)//2}) con distancia por red menor que la recta: {viol}. "
         f"Cociente red/recta: mínimo {(dred[off]/drecta[off]).min():.3f}, mediana {np.median(dred[off]/drecta[off]):.3f}.\n",
         "## Aristas viales de mayor peso\n",
         ev.sort_values("peso", ascending=False).head(10)[["par", "n_tramos", "d_red_km", "peso"]].round(3).to_markdown(index=False),
         "\n## Aristas viales con un solo tramo\n",
         (ev[ev.n_tramos == 1][["par", "d_red_km", "peso"]].round(3).to_markdown(index=False) or "ninguna"),
         f"\n## Revisión visual\n\n`results/figuras/{ruta_mapa.name}`\n"]
    (FICHAS / "validacion_grafos.md").write_text("\n".join(m), encoding="utf-8")
    ok = con_geo and con_vial and viol == 0 and dentro.all()
    print(f"GC2 {int(np.triu(ageo>0).sum())} aristas, GE {int(np.triu(avial>0).sum())} aristas, "
          f"conectados {con_geo}/{con_vial}, violaciones red<recta {viol}, cambiados {cambiados}")
    if not ok:
        raise SystemExit("Alguna validación falló: ver results/fichas/validacion_grafos.md")


if __name__ == "__main__":
    main()
