"""Comprensión de los datos y Preparación de los datos: panel distrito × mes.

Uso: python -m src.datos
"""
from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.comun import CSV_CRUDO, FICHAS, FIGURAS, PROCESADOS

N_DISTRITOS = 43
N_MESES = 105
TOTAL_ESPERADO = 957_705
MODALIDADES = ["Hurto", "Robo"]


def leer_crudo() -> pd.DataFrame:
    # UBIGEO como texto: en otros departamentos pierde el cero inicial
    d = pd.read_csv(CSV_CRUDO, dtype={"UBIGEO_HECHO": str}, encoding="utf-8")
    d["UBIGEO_HECHO"] = d["UBIGEO_HECHO"].str.strip().str.zfill(6)
    return d


def construir_panel(crudo: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    lima = crudo[crudo["DPTO_HECHO_NEW"] == "LIMA METROPOLITANA"].copy()
    lima["periodo"] = lima["ANIO"].astype(str) + "-" + lima["MES"].astype(str).str.zfill(2)
    hr = lima[lima["P_MODALIDADES"].isin(MODALIDADES)]
    total_antes = int(hr["cantidad"].sum())

    distritos = (
        lima[["UBIGEO_HECHO", "DIST_HECHO"]].drop_duplicates().sort_values("UBIGEO_HECHO")
        .rename(columns={"UBIGEO_HECHO": "ubigeo", "DIST_HECHO": "distrito"})
    )
    periodos = pd.period_range("2018-01", "2026-09", freq="M").strftime("%Y-%m").tolist()
    rejilla = pd.MultiIndex.from_product([distritos["ubigeo"], periodos], names=["ubigeo", "periodo"])

    agg = (
        hr.pivot_table(index=["UBIGEO_HECHO", "periodo"], columns="P_MODALIDADES",
                       values="cantidad", aggfunc="sum")
        .rename(columns={"Hurto": "hurto", "Robo": "robo"})
    )
    agg.index.names = ["ubigeo", "periodo"]
    panel = agg.reindex(rejilla).reset_index()
    sin_hr = panel["hurto"].isna() & panel["robo"].isna()

    # Distrito-mes con alguna fila de cualquier modalidad: si la tiene, el cero es real
    con_alguna = set(map(tuple, lima[["UBIGEO_HECHO", "periodo"]].drop_duplicates().values))
    tiene_fila = np.array([(u, p) in con_alguna for u, p in zip(panel["ubigeo"], panel["periodo"])])

    panel["estado"] = "observado"
    panel.loc[sin_hr & tiene_fila, "estado"] = "cero"
    panel.loc[sin_hr & ~tiene_fila, "estado"] = "sin_informacion"
    panel[["hurto", "robo"]] = panel[["hurto", "robo"]].fillna(0).astype(int)
    panel["objetivo"] = panel["hurto"] + panel["robo"]
    panel = panel.merge(distritos, on="ubigeo")
    panel["pandemia"] = panel["periodo"].between("2020-03", "2021-12").astype(int)
    panel = panel[["ubigeo", "distrito", "periodo", "hurto", "robo", "objetivo", "estado", "pandemia"]]

    info = {
        "filas_lima": len(lima),
        "total_antes": total_antes,
        "hurto": int(hr.loc[hr.P_MODALIDADES == "Hurto", "cantidad"].sum()),
        "robo": int(hr.loc[hr.P_MODALIDADES == "Robo", "cantidad"].sum()),
        "dup_crudo": int(lima.duplicated(["ANIO", "MES", "UBIGEO_HECHO", "P_MODALIDADES"]).sum()),
        "nombres_por_ubigeo": int(lima.groupby("UBIGEO_HECHO")["DIST_HECHO"].nunique().max()),
        "ubigeos_por_nombre": int(lima.groupby("DIST_HECHO")["UBIGEO_HECHO"].nunique().max()),
        "nulos_crudo": int(lima.isna().sum().sum()),
        "negativos": int((lima["cantidad"] < 0).sum()),
    }
    return panel, info


def verificar(panel: pd.DataFrame, info: dict) -> dict:
    est = panel["estado"].value_counts().to_dict()
    chk = {
        "filas": len(panel) == N_DISTRITOS * N_MESES,
        "distritos": panel["ubigeo"].nunique() == N_DISTRITOS,
        "sin_duplicados": not panel.duplicated(["ubigeo", "periodo"]).any(),
        "total_957705": int(panel["objetivo"].sum()) == TOTAL_ESPERADO == info["total_antes"],
        "ceros_60": est.get("cero", 0) == 60,
        "sin_info_9": est.get("sin_informacion", 0) == 9,
        "sin_info_solo_SMM": set(panel.loc[panel.estado == "sin_informacion", "distrito"]) == {"SANTA MARIA DEL MAR"},
    }
    fallos = [k for k, v in chk.items() if not v]
    if fallos:
        raise SystemExit(f"Verificación fallida: {fallos} | estados={est} | total={panel['objetivo'].sum()}")
    return est


def atipicos(panel: pd.DataFrame) -> pd.DataFrame:
    # Atípico: |z robusto| > 3.5 sobre log1p por distrito (mediana y MAD), excluye pandemia del cálculo
    filas = []
    for u, g in panel[panel.estado == "observado"].groupby("ubigeo"):
        x = np.log1p(g["objetivo"])
        base = x[g["pandemia"] == 0]
        med = base.median()
        mad = (base - med).abs().median() * 1.4826
        if mad == 0:
            continue
        z = (x - med) / mad
        sel = g[z.abs() > 3.5].assign(z_robusto=z[z.abs() > 3.5].round(2))
        filas.append(sel)
    return pd.concat(filas) if filas else pd.DataFrame()


def graficos(panel: pd.DataFrame) -> list[str]:
    salidas = []
    tot = panel.groupby("periodo")[["hurto", "robo", "objetivo"]].sum()
    x = pd.PeriodIndex(tot.index, freq="M").to_timestamp()

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(x, tot["objetivo"], label="Hurto + robo", color="#1f4e79", lw=2)
    ax.plot(x, tot["hurto"], label="Hurto", color="#5b9bd5", lw=1)
    ax.plot(x, tot["robo"], label="Robo", color="#c55a11", lw=1)
    ax.plot(x, tot["objetivo"].rolling(12, center=True).mean(), "--", color="gray", label="Media móvil 12 m")
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2021-12-01"), color="#f4cccc", alpha=.4, label="Pandemia")
    ax.axvline(pd.Timestamp("2020-04-01"), color="red", lw=.8)
    ax.annotate("abr-2020", (pd.Timestamp("2020-04-01"), tot.loc["2020-04", "objetivo"]), xytext=(10, -5),
                textcoords="offset points", color="red", fontsize=8)
    ax.axvline(pd.Timestamp("2023-01-01"), color="purple", lw=.8, ls=":")
    ax.annotate("salto 2022→2023", (pd.Timestamp("2023-01-01"), tot["objetivo"].max() * .95), xytext=(5, 0),
                textcoords="offset points", color="purple", fontsize=8)
    ax.set_ylabel("Denuncias por mes")
    ax.set_title("Tendencia mensual de denuncias de hurto y robo, Lima Metropolitana")
    ax.legend(fontsize=8, ncol=3)
    fig.tight_layout()
    p = FIGURAS / "tendencia_mensual.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    salidas.append(p.name)

    # Estacionalidad: cada mes como proporción de la media de su año, solo años completos sin pandemia
    t = tot.reset_index()
    t["anio"] = t["periodo"].str[:4].astype(int)
    t["mes"] = t["periodo"].str[5:].astype(int)
    t = t[t["anio"].isin([2018, 2019, 2022, 2023, 2024, 2025])]
    t["indice"] = t["objetivo"] / t.groupby("anio")["objetivo"].transform("mean")
    fig, ax = plt.subplots(figsize=(8, 4))
    for a, g in t.groupby("anio"):
        ax.plot(g["mes"], g["indice"], marker="o", ms=3, lw=1, label=str(a))
    ax.plot(range(1, 13), t.groupby("mes")["indice"].mean(), color="black", lw=2.5, label="Promedio")
    ax.axhline(1, color="gray", lw=.5)
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("Mes")
    ax.set_ylabel("Índice estacional (mes / media del año)")
    ax.set_title("Estacionalidad de hurto + robo (años completos sin pandemia)")
    ax.legend(fontsize=7, ncol=4)
    fig.tight_layout()
    p = FIGURAS / "estacionalidad.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    salidas.append(p.name)

    anual = panel.assign(anio=panel.periodo.str[:4]).groupby("anio")["objetivo"].sum()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(anual.index, anual.values, color=["#c55a11" if a == "2026" else "#1f4e79" for a in anual.index])
    for i, v in enumerate(anual.values):
        ax.text(i, v, f"{v:,}".replace(",", " "), ha="center", va="bottom", fontsize=7)
    ax.set_title("Hurto + robo por año (2026: enero a septiembre)")
    fig.tight_layout()
    p = FIGURAS / "totales_anuales.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    salidas.append(p.name)
    return salidas


def informe(panel, info, est, atip, figs) -> None:
    tot = panel.groupby("periodo")["objetivo"].sum()
    anual = panel.assign(anio=panel.periodo.str[:4]).groupby("anio")["objetivo"].sum()
    faltas = (panel[panel.estado != "observado"].groupby(["distrito", "estado"]).size()
              .unstack(fill_value=0))
    obs = panel[panel.estado == "observado"]["objetivo"]
    desde22 = panel[panel.periodo >= "2022-01"].groupby("distrito")["objetivo"].sum()
    top4 = desde22.sort_values(ascending=False).head(4)
    m = []
    m.append("# Comprensión de los datos: informe de calidad\n")
    m.append("Generado por `python -m src.datos`. Nota. Elaboración propia.\n")
    m.append("## Diccionario de datos (archivo crudo)\n")
    m.append("| Campo | Descripción | Tratamiento |\n| --- | --- | --- |")
    m.append("| ANIO, MES | Año y mes del hecho | Se unen en `periodo` (YYYY-MM) |")
    m.append("| DPTO_HECHO_NEW | Departamento del hecho | Filtro `LIMA METROPOLITANA` |")
    m.append("| PROV_HECHO | Provincia del hecho | Solo `LIMA` tras el filtro |")
    m.append("| DIST_HECHO | Distrito del hecho | Nombre; se verifica relación 1:1 con el UBIGEO |")
    m.append("| UBIGEO_HECHO | Código INEI del distrito | Leído como texto, `zfill(6)` |")
    m.append("| P_MODALIDADES | Modalidad del delito | Se conservan Hurto y Robo |")
    m.append("| cantidad | Número de denuncias (ya agregado) | Se suma por distrito y mes |\n")
    m.append("## Verificaciones\n")
    m.append("| Comprobación | Resultado |\n| --- | --- |")
    m.append(f"| Filas de Lima Metropolitana en el crudo | {info['filas_lima']:,} |".replace(",", " "))
    m.append(f"| Duplicados en el crudo (año, mes, ubigeo, modalidad) | {info['dup_crudo']} |")
    m.append(f"| Valores nulos en el crudo (Lima) | {info['nulos_crudo']} |")
    m.append(f"| Cantidades negativas | {info['negativos']} |")
    m.append(f"| Nombres distintos por UBIGEO / UBIGEO distintos por nombre (máx.) | {info['nombres_por_ubigeo']} / {info['ubigeos_por_nombre']} |")
    m.append(f"| Filas del panel | {len(panel)} (43 × 105) |")
    m.append(f"| Duplicados distrito-mes en el panel | {int(panel.duplicated(['ubigeo','periodo']).sum())} |")
    m.append(f"| Total hurto + robo antes de agregar | {info['total_antes']:,} |".replace(",", " "))
    m.append(f"| Total hurto + robo en el panel | {int(panel['objetivo'].sum()):,} (hurto {info['hurto']:,}; robo {info['robo']:,}) |".replace(",", " "))
    m.append("")
    m.append("## Cobertura y meses sin hurto ni robo\n")
    m.append(f"Estados del panel: observado {est.get('observado',0)}, cero {est.get('cero',0)}, "
             f"sin_informacion {est.get('sin_informacion',0)}.\n")
    m.append("- `cero`: el distrito tiene denuncias de otras modalidades ese mes, pero ninguna de hurto ni robo. Se usa como 0 real.")
    m.append("- `sin_informacion`: el distrito no tiene ninguna fila de ninguna modalidad ese mes. Entra al modelo como 0, pero se excluye de todas las métricas.\n")
    m.append(faltas.to_markdown() if hasattr(faltas, "to_markdown") else faltas.to_string())
    m.append("\nMeses sin información: " + ", ".join(panel.loc[panel.estado == "sin_informacion", "periodo"]) + "\n")
    m.append("## Distribución por celda observada\n")
    m.append(f"Mínimo {obs.min()}, máximo {obs.max()}, media {obs.mean():.1f}, mediana {obs.median():.0f}.\n")
    m.append("## Totales anuales\n")
    m.append("| Año | Hurto + robo |\n| --- | --- |")
    for a, v in anual.items():
        m.append(f"| {a}{' (ene–sep)' if a == '2026' else ''} | {v:,} |".replace(",", " "))
    m.append("")
    m.append("## Quiebres\n")
    m.append(f"- Abril de 2020 (estado de emergencia): {tot['2020-04']:,} denuncias en Lima".replace(",", " ")
             + f", frente a {tot['2020-02']:,} en febrero de 2020.".replace(",", " ").replace("  ", ", "))
    m.append(f"- Salto de 2022 a 2023: {anual['2022']:,} → {anual['2023']:,} "
             f"({(anual['2023']/anual['2022']-1)*100:+.1f} %). Baja en 2025: {anual['2025']:,} "
             f"({(anual['2025']/anual['2024']-1)*100:+.1f} % frente a 2024).".replace(",", " "))
    m.append("- El salto de 2023 es un cambio de nivel que el modelo debe absorber; la ventana 1 lo tiene en prueba. "
             "No se corrige: se interpreta como cambio en el registro o en el fenómeno, sin poder separarlos con estos datos.\n")
    m.append("## Concentración desde 2022\n")
    m.append(f"Los cuatro distritos con más denuncias desde 2022 suman {top4.sum()/desde22.sum()*100:.1f} % del total: "
             + ", ".join(f"{d} ({v:,})".replace(",", " ") for d, v in top4.items()) + ".\n")
    m.append("## Atípicos\n")
    m.append("Criterio: |z robusto| > 3,5 sobre log1p(objetivo) por distrito (mediana y MAD de los meses sin pandemia). "
             "Decisión: se conservan; son registros reales y la pandemia se trata como caso adverso.\n")
    if len(atip):
        m.append(f"Celdas marcadas: {len(atip)} (de ellas en pandemia: {int(atip['pandemia'].sum())}).\n")
        m.append(atip[["distrito", "periodo", "objetivo", "z_robusto"]].sort_values("z_robusto")
                 .head(25).to_markdown(index=False))
    m.append("\n## Figuras\n")
    for f in figs:
        m.append(f"- `results/figuras/{f}`")
    (FICHAS / "calidad.md").write_text("\n".join(m) + "\n", encoding="utf-8")


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    crudo = leer_crudo()
    panel, info = construir_panel(crudo)
    est = verificar(panel, info)
    panel.to_csv(PROCESADOS / "panel.csv", index=False)
    figs = graficos(panel)
    informe(panel, info, est, atipicos(panel), figs)
    print(f"Panel: {len(panel)} filas, total {panel['objetivo'].sum()}, estados {est}")


if __name__ == "__main__":
    main()
