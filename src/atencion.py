"""Evaluación (OE3): agregación de los pesos de atención, contraste con contigüidad y conectividad vial y prueba de fidelidad.

Uso: python -m src.atencion
Los pesos se interpretan como indicio de las relaciones que usa el modelo, no como explicación causal.
"""
from __future__ import annotations

import argparse
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src.comun import ATENCION, FICHAS, FIGURAS, PROCESADOS, leer_config
from src.entrenar import cargar_entrenado, predecir_con
from src.protocolo import H, cargar_datos

FRACCION_FIDELIDAD = 0.10
SORTEOS_AZAR = 10


def matriz(nombre: str) -> pd.DataFrame:
    m = pd.read_csv(PROCESADOS / f"matriz_{nombre}.csv", index_col=0)
    m.index = m.index.astype(str).str.zfill(6)
    m.columns = m.index
    return m


def leer_atencion(modelo: str) -> pd.DataFrame:
    filas = []
    for f in sorted(ATENCION.glob(f"{modelo}_*_*.csv")):
        mt = re.match(rf"^{modelo}_([1-4])_(\d+)\.csv$", f.name)
        if mt:
            filas.append(pd.read_csv(f, dtype={"origen": str, "destino": str}).assign(ventana=mt.group(1), semilla=int(mt.group(2))))
    return pd.concat(filas, ignore_index=True) if filas else pd.DataFrame()


def por_par(a: pd.DataFrame) -> pd.DataFrame:
    """Atención espacial media por par no dirigido (promedio de ambos sentidos, meses, desfases, ventanas y semillas)."""
    e = a[(a.tipo == "espacial") & (a.origen != a.destino)]
    g = e.groupby(["origen", "destino"]).peso.mean().reset_index()
    g["a"], g["b"] = np.minimum(g.origen, g.destino), np.maximum(g.origen, g.destino)
    return g.groupby(["a", "b"]).peso.mean().reset_index()


def fidelidad(d, pares_run: pd.DataFrame, w: str, s: int, rng) -> dict:
    """Quita el 10 % de aristas con más atención y, aparte, el mismo número al azar; ΔMAE en la prueba, sin reentrenar."""
    m, tr, L, i_te = cargar_entrenado(d, "GE", w, s)
    A = matriz("vial")
    ub = A.index.tolist()
    ok = d.valido[i_te]
    base = np.abs(predecir_con(m, d, tr, L, i_te, A.values) - d.y[i_te])[ok].mean()
    k = max(1, int(round(FRACCION_FIDELIDAD * len(pares_run))))

    def sin(pares):
        B = A.values.copy()
        for a_, b_ in pares:
            i, j = ub.index(a_), ub.index(b_)
            B[i, j] = B[j, i] = 0
        return np.abs(predecir_con(m, d, tr, L, i_te, B) - d.y[i_te])[ok].mean()

    top = pares_run.nlargest(k, "peso")[["a", "b"]].values
    mae_top = sin(top)
    azar = [sin(pares_run.iloc[rng.choice(len(pares_run), k, replace=False)][["a", "b"]].values) for _ in range(SORTEOS_AZAR)]
    return {"ventana": w, "semilla": s, "aristas_quitadas": k, "MAE_base": base, "MAE_sin_top": mae_top,
            "MAE_sin_azar": float(np.mean(azar)), "dMAE_top": mae_top - base, "dMAE_azar": float(np.mean(azar)) - base}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rapido", action="store_true", help="lee y escribe en results_rapido/")
    ap.parse_args()
    d = cargar_datos()
    nom = dict(zip(d.ubigeos, d.distritos))
    vial, geo = matriz("vial"), matriz("geo")
    md = ["# Evaluación: interpretabilidad mediante los pesos de atención (OE3)\n",
          "Generado por `python -m src.atencion`. Pesos de la prueba de las 4 ventanas × 5 semillas. "
          "En el GAT, la atención de cada distrito destino suma 1 entre sus vecinos y él mismo. "
          "Se interpretan como indicio, no como causa. Nota. Elaboración propia.\n"]

    # ---------------- temporal
    temp = []
    for mod in ["GE", "GC2", "GC1"]:
        a = leer_atencion(mod)
        if len(a):
            t = a[a.tipo == "temporal"].copy()
            # cada corrida usa 6 o 12 meses de entrada: se promedia por separado (uniforme sería 1/6 o 1/12)
            t["entrada"] = t.groupby(["ventana", "semilla"]).desfase.transform("max") - H + 1
            for L_, g in t.groupby("entrada"):
                temp.append(g.groupby("desfase").peso.mean().rename(f"{mod} (L={L_})"))
    temp = pd.concat(temp, axis=1)
    temp.to_csv(FICHAS / "atencion_temporal.csv")
    fig, ax = plt.subplots(figsize=(7, 3.5))
    for c in temp:
        ax.plot(temp.index, temp[c], marker="o", label=c)
    ax.set_xlabel("Desfase (meses antes del mes predicho)")
    ax.set_ylabel("Atención temporal media")
    ax.set_xticks(temp.index)
    ax.legend()
    ax.set_title("Atención temporal por desfase")
    fig.tight_layout()
    fig.savefig(FIGURAS / "atencion_temporal.png", dpi=150)
    plt.close(fig)
    md += ["## Atención temporal por desfase\n",
           "Media sobre distritos, meses de prueba y semillas, por separado según los meses de entrada (L) que eligió la "
           "validación en cada ventana. Una atención uniforme valdría 1/L (0,167 con L = 6; 0,083 con L = 12).\n",
           temp.round(4).to_markdown(), "", "Figura: `results/figuras/atencion_temporal.png`\n"]

    # ---------------- espacial
    ge = leer_atencion("GE")
    autoat = {}
    for mod, a in [("GE", ge), ("GC2", leer_atencion("GC2"))]:
        e = a[a.tipo == "espacial"]
        autoat[mod] = e[e.origen == e.destino].peso.mean()
    limite = matriz("limite_km")
    tramos = matriz("tramos_cruce")

    def preparar(a, adj):
        pp = por_par(a)
        pp["peso_vial"] = [vial.loc[x, y] for x, y in zip(pp.a, pp.b)]
        pp["n_tramos"] = [tramos.loc[x, y] for x, y in zip(pp.a, pp.b)]
        pp["contiguo"] = [int(geo.loc[x, y] > 0) for x, y in zip(pp.a, pp.b)]
        pp["limite_km"] = [limite.loc[x, y] for x, y in zip(pp.a, pp.b)]
        # el GAT normaliza por nodo destino: un distrito con muchos vecinos reparte más; se corrige por el grado medio del par
        grado = (adj > 0).sum(1)
        pp["peso_x_grado"] = pp.peso * [(grado[x] + grado[y] + 2) / 2 for x, y in zip(pp.a, pp.b)]
        pp["par"] = pp.a.map(nom) + " – " + pp.b.map(nom)
        return pp

    pp = preparar(ge, vial)
    pp.to_csv(FICHAS / "atencion_espacial_pares_GE.csv", index=False)
    pg = preparar(leer_atencion("GC2"), geo)
    pg.to_csv(FICHAS / "atencion_espacial_pares_GC2.csv", index=False)

    rho = []
    for mod, t, refs in [("GE", pp, ["peso_vial", "n_tramos", "limite_km", "contiguo"]),
                         ("GC2", pg, ["peso_vial", "n_tramos", "limite_km"])]:
        for col in ["peso", "peso_x_grado"]:
            for ref in refs:
                if t[ref].nunique() < 2:  # constante en esas aristas: la correlación no está definida
                    rho.append({"modelo": mod, "atencion": col, "contra": ref, "rho": np.nan, "p": np.nan,
                                "n_aristas": len(t), "nota": "constante"})
                    continue
                r = stats.spearmanr(t[col], t[ref])
                rho.append({"modelo": mod, "atencion": col, "contra": ref, "rho": r.statistic, "p": r.pvalue,
                            "n_aristas": len(t), "nota": ""})
    rho = pd.DataFrame(rho)
    rho.to_csv(FICHAS / "atencion_spearman.csv", index=False)
    md += ["## Atención espacial frente a la conectividad vial y la contigüidad\n",
           f"Autoatención media (peso del propio distrito): GE {autoat['GE']:.3f}; GC₂ {autoat['GC2']:.3f}.\n",
           f"Correlación de Spearman por arista. En el GE ({len(pp)} aristas) {int(pp.contiguo.sum())} son contiguas, "
           "así que la contigüidad binaria es constante y la contigüidad se mide además como longitud del límite compartido "
           f"(km). En el GC₂ ({len(pg)} aristas) {int((pg.peso_vial == 0).sum())} pares contiguos no tienen tramo vial que "
           "cruce (peso vial 0). `peso_x_grado` multiplica la atención por el número medio de entradas del par (vecinos + 1) "
           "para quitar el efecto de la normalización por nodo.\n",
           rho.round(4).to_markdown(index=False), "",
           "### Top 10 de pares por atención (GE)\n",
           pp.nlargest(10, "peso")[["par", "peso", "peso_x_grado", "peso_vial", "n_tramos", "limite_km"]].round(4).to_markdown(index=False), "",
           "### Top 10 de pares por atención corregida por grado (GE)\n",
           pp.nlargest(10, "peso_x_grado")[["par", "peso", "peso_x_grado", "peso_vial", "n_tramos", "limite_km"]].round(4).to_markdown(index=False), ""]

    # ---------------- fidelidad (complementaria)
    rng = np.random.default_rng(0)
    fid = []
    for (w, s), a in ge.groupby(["ventana", "semilla"]):
        fid.append(fidelidad(d, por_par(a), w, int(s), rng))
    fid = pd.DataFrame(fid)
    fid.to_csv(FICHAS / "atencion_fidelidad.csv", index=False)
    dif = fid.dMAE_top - fid.dMAE_azar
    w_ = stats.wilcoxon(fid.dMAE_top, fid.dMAE_azar)
    md += ["## Prueba de fidelidad (complementaria)\n",
           f"En cada una de las {len(fid)} corridas del GE se quitó el {int(FRACCION_FIDELIDAD*100)} % de las aristas "
           f"con más atención en esa corrida y, aparte, el mismo número de aristas al azar ({SORTEOS_AZAR} sorteos, promedio). "
           "Sin reentrenar. Si la atención señala aristas útiles, quitar las de más atención debería subir más el MAE.\n",
           fid.groupby("ventana")[["MAE_base", "dMAE_top", "dMAE_azar"]].mean().round(3).to_markdown(), "",
           f"Promedio de las {len(fid)} corridas: ΔMAE top {fid.dMAE_top.mean():.3f}; ΔMAE azar {fid.dMAE_azar.mean():.3f}. "
           f"Corridas donde quitar las de más atención dañó más que el azar: {int((dif > 0).sum())} de {len(fid)}. "
           f"Wilcoxon pareado: p = {w_.pvalue:.4f}.\n"]
    (FICHAS / "atencion.md").write_text("\n".join(md), encoding="utf-8")
    print(temp.round(3).to_string())
    print(rho.round(3).to_string(index=False))
    print(fid[["dMAE_top", "dMAE_azar"]].mean().round(3).to_dict())


if __name__ == "__main__":
    main()
