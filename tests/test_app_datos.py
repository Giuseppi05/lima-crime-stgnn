"""Pruebas mínimas de la interfaz de resultados: lectores de la versión del artículo y cifras de la tabla global.

Uso: python -m pytest tests/test_app_datos.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from app import datos as D  # noqa: E402
from app import exportar as X  # noqa: E402
from app import formato as F  # noqa: E402

AVC3 = RAIZ.parent / "AVC3.docx"  # fuera del repositorio: la prueba de citas se salta si no está


@pytest.fixture(scope="module")
def art() -> D.Version:
    vs = [v for v in D.detectar_versiones() if v.articulo]
    assert len(vs) == 1, "debe existir exactamente una versión del artículo (results/fichas)"
    return vs[0]


def test_detecta_v1_y_articulo():
    claves = [v.clave for v in D.detectar_versiones()]
    assert "v1" in claves
    assert D.version_actual() in claves


@pytest.mark.parametrize("lector, columnas, filas", [
    (D.metricas_global, ["modelo", "MAE", "RMSE", "R2", "MASE", "MAE_sd", "RMSE_sd"], 10),
    (D.metricas_por_ventana, ["modelo", "ventana", "MAE", "RMSE", "R2", "MAE_sd"], 40),
    (D.metricas_por_distrito, ["modelo", "ubigeo", "MAE", "RMSE", "distrito"], 10 * 43),
    (D.corridas_neuronales, ["modelo", "ventana", "semilla", "mae_validacion", "MAE", "RMSE", "R2"], 60),
    (D.pruebas_estadisticas, ["comparacion", "MAE_GE", "MAE_rival", "RMSE_GE", "RMSE_rival", "p", "GE_supera"], 7),
    (D.equidad_por_distrito, ["modelo", "ubigeo", "error_rel", "distrito", "sector", "volumen_entrenamiento"], 10 * 43),
    (D.equidad_resumen, ["modelo", "brecha", "brecha_sin_playa", "media_bajo", "media_medio", "media_alto"], 10),
    (D.equidad_sectores, ["modelo", "prueba", "estadistico", "p", "significativa"], 10),
])
def test_lectores_v2(art, lector, columnas, filas):
    df = lector(art)
    assert df is not None, f"{lector.__name__} no encontró su archivo"
    assert set(columnas) <= set(df.columns)
    assert len(df) >= filas if lector is D.metricas_por_ventana else len(df) == filas


def test_predicciones_v2(art):
    p = D.predicciones(art)
    assert p is not None
    assert {"ubigeo", "periodo", "real", "predicho", "valido", "modelo", "ventana", "semilla"} <= set(p.columns)
    assert p.ubigeo.str.len().eq(6).all()
    assert set(D.VENTANAS_PRUEBA) <= set(p.ventana)
    # 3 neuronales × 5 ventanas × 5 semillas + 4 deterministas × 5 ventanas, 516 filas cada uno
    assert len(p) == (3 * 5 * 5 + 4 * 5) * 516


def test_lector_ausente_devuelve_none(art):
    v1 = next(v for v in D.detectar_versiones() if v.clave == "v1")
    assert D.equidad_resumen(v1) is None
    assert D.predicciones(v1) is None


def test_tabla_global_coincide_con_archivo(art):
    """Las cifras que muestra la tabla global son las de metricas_global.csv, con coma decimal y 3 decimales."""
    from app.vistas import desempeno  # noqa: F401  (importa la vista: debe cargar sin Streamlit en ejecución)
    crudo = pd.read_csv(art.archivo("metricas_global.csv")).set_index("modelo")
    g = D.metricas_global(art).set_index("modelo")
    pd.testing.assert_frame_equal(g, crudo)
    assert D.version_actual() == "v4"
    assert F.ms(g.loc["GE", "MAE"], g.loc["GE", "MAE_sd"]) == "32,139 ± 0,213"
    assert F.ms(g.loc["GE", "RMSE"], g.loc["GE", "RMSE_sd"]) == "53,051 ± 0,385"
    assert F.ms(g.loc["xgboost", "MAE"], g.loc["xgboost", "MAE_sd"]) == "57,039"
    for m, fila in g.iterrows():
        assert F.num(fila.MAE) == f"{fila.MAE:.3f}".replace(".", ",")


def test_global_recalculada_desde_predicciones(art):
    r = D.metricas_global_desde_predicciones(D.predicciones(art))
    g = D.metricas_global(art).set_index("modelo")
    for c in ["MAE", "RMSE", "R2", "MAE_sd", "RMSE_sd"]:
        assert (r[c] - g.loc[r.index, c]).abs().max() < 1e-9, c


def test_regla_avc3_coincide(art):
    p = D.pruebas_estadisticas(art)
    assert (p.apply(D.regla_avc3, axis=1) == p.GE_supera).all()


def test_mismo_conjunto_de_prueba(art):
    r = D.verificar_mismo_conjunto(D.predicciones(art))
    assert r.iguales.all()
    assert (r.celdas == 516).all()


def test_r2_por_distrito(art):
    p = D.predicciones(art)
    for modo in ["ventana", "48"]:
        r = D.r2_por_distrito(p, modo)
        assert r.groupby("modelo").size().eq(43).all()
        assert r.loc[r.modelo == "GE", "n_semillas"].eq(5).all()
        assert r.loc[r.modelo == "mes_anterior", "n_semillas"].eq(1).all()


def test_brecha_y_composicion(art):
    r = D.equidad_resumen(art)
    b = D.brecha_entre_sectores(r)
    assert (b >= 0).all()
    c = D.composicion_sectores(D.equidad_por_distrito(art))
    assert c.n.sum() == 43 and list(c.sector) == D.SECTORES


def test_aviso_cache(art, tmp_path):
    # el aviso sale salvo que el yaml de la versión declare la corrección (la v4 la declara; la v1, no)
    assert not D.aviso_cache_grafo(art)
    assert D.aviso_cache_grafo(next(v for v in D.detectar_versiones() if v.clave == "v1"))
    (tmp_path / "fichas").mkdir()
    (tmp_path / "fichas" / "version.yaml").write_text("correccion_cache_grafo: true\n", encoding="utf-8")
    corregida = D.Version(clave="exp:h1_base", etiqueta="", fichas=tmp_path / "fichas")
    assert not D.aviso_cache_grafo(corregida)
    (tmp_path / "fichas" / "version.yaml").write_text("correccion_cache_grafo: false\n", encoding="utf-8")
    sin_correccion = D.Version(clave="exp:otra", etiqueta="", fichas=tmp_path / "fichas")
    assert D.aviso_cache_grafo(sin_correccion)


def test_formato():
    assert F.num(957705, 0) == "957 705"
    assert F.num(0.0004, 3) == "0,000"
    assert F.p_valor(4e-6) == "< 0,001"
    assert F.romano(3) == "III" and F.romano(14) == "XIV"


def test_exportar_tabla(tmp_path):
    from docx import Document
    df = pd.DataFrame({"Modelo": ["GE"], "MAE": ["33,469 ± 1,368"]})
    d = Document(io.BytesIO(X.tabla_docx(df, "III", "Métricas globales")))
    textos = [p.text for p in d.paragraphs]
    assert textos[0] == "TABLA III." and textos[1] == "MÉTRICAS GLOBALES"
    assert textos[-1] == "Nota. Elaboración propia."
    assert d.tables[0].cell(1, 1).text == "33,469 ± 1,368"
    csv = X.tabla_csv(df).decode("utf-8-sig")
    assert csv.splitlines() == ["Modelo;MAE", "GE;33,469 ± 1,368"]
    assert X.guardar("x.csv", b"a", tmp_path).read_bytes() == b"a"


def test_exportar_figura_300_dpi():
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (600, 300), "white").save(buf, format="PNG")
    png = X.figura_png(buf.getvalue(), "7", "Prueba.")
    im = Image.open(io.BytesIO(png))
    assert round(im.info["dpi"][0]) == 300
    assert im.width == round(X.ANCHO_IN * 300)


@pytest.mark.skipif(not AVC3.exists(), reason="AVC3.docx no está junto al repositorio")
def test_citas_literales_del_avc3():
    from docx import Document

    from app.avc3 import CITAS
    texto = " ".join(p.text for p in Document(str(AVC3)).paragraphs)
    for clave, (_, cita) in CITAS.items():
        assert cita in texto, clave


# ---------------------------------------------------------------- pestaña 1 (Datos, OE1)
def test_solapamiento_ge_gc2():
    """Dato verificado: 89 aristas comunes, 9 solo geográficas, 0 solo viales, Jaccard 0,908."""
    s = D.solapamiento(D.aristas("geo"), D.aristas("vial"))
    assert (s["comunes"], s["solo_geo"], s["solo_vial"], s["union"]) == (89, 9, 0, 98)
    assert F.num(s["jaccard"]) == "0,908"


def test_validacion_grafos_coincide_con_ficha(art):
    nod = D.nodos()
    ub = list(nod.ubigeo)
    rg, rv = D.resumen_grafo(D.aristas("geo"), ub), D.resumen_grafo(D.aristas("vial"), ub)
    assert (rg["aristas"], rv["aristas"]) == (98, 89) and rg["conectado"] and rv["conectado"]
    g = D.tabla_md(D.validacion_grafos_md(art), "Grafos")
    assert list(g["Aristas"]) == ["98", "89"]
    assert list(g["Grado medio"]) == [f"{rg['grado_medio']:.2f}", f"{rv['grado_medio']:.2f}"]
    d = D.distancia_red_vs_recta(nod)
    assert d["pares"] == 903 and d["violaciones"] == 0
    assert f"{d['cociente_min']:.3f}" == "1.038" and f"{d['cociente_mediana']:.3f}" == "1.215"


def test_cobertura_coincide_con_calidad(art):
    p = D.panel()
    c = D.cobertura(p).set_index("estado").celdas
    assert (c["observado"], c["cero"], c["sin_informacion"]) == (4446, 60, 9)
    assert "observado 4446, cero 60, sin_informacion 9" in D.calidad_md(art)
    assert len(p) == 43 * 105 and not p.duplicated(["ubigeo", "periodo"]).any()
    assert F.entero(p.objetivo.sum()) == "957 705"


def test_configuracion_es_la_de_validacion(art):
    cfg, aj = D.configuracion(art), D.ajuste_hiperparametros(art)
    assert D.multianual(cfg) and D.archivo_ajuste(art) == "ajuste_hiperparametros_v4.csv"
    ver = D.verificar_configuracion(cfg, aj, cfg["salida_neuronal"]["elegida"])
    assert len(ver) == 15 and ver.coincide.all()
    prom = D.eleccion_salida_desde_ajuste(aj, cfg)
    esperado = cfg["salida_neuronal"]["mae_validacion_promedio"]
    assert round(prom["residual"], 4) == esperado["residual"] and round(prom["directa"], 4) == esperado["directa"]


# ---------------------------------------------------------------- pestaña 3 (Interpretabilidad, OE3)
def test_lectores_atencion_v2(art):
    assert list(D.atencion_temporal(art).desfase) == list(range(1, 13))
    s = D.atencion_spearman(art)
    assert set(s.modelo) == {"GE", "GC2"}
    assert s.loc[(s.modelo == "GE") & (s.contra == "contiguo"), "nota"].eq("constante").all()
    assert len(D.atencion_pares(art, "GE")) == 89 and len(D.atencion_pares(art, "GC2")) == 98
    assert len(D.atencion_fidelidad(art)) == 20


def test_autoatencion_y_fidelidad_coinciden_con_ficha(art):
    import re
    md = D.atencion_md(art)
    a = D.autoatencion(art)
    ge, gc2 = re.search(r"GE (\d+\.\d+); GC₂ (\d+\.\d+)", md).groups()
    assert (f"{a['GE']:.3f}", f"{a['GC2']:.3f}") == (ge, gc2)
    f = D.atencion_fidelidad(art)
    assert f"ΔMAE top {f.dMAE_top.mean():.3f}; ΔMAE azar {f.dMAE_azar.mean():.3f}" in md
    assert f"{int((f.dMAE_top > f.dMAE_azar).sum())} de 20" in md


# ---------------------------------------------------------------- pestaña 5 (Casos adversos)
def test_pandemia_v2(art):
    pa = D.pandemia(art)
    assert len(pa) == 10 and {"MAE", "MAE_sd", "RMSE", "R2"} <= set(pa.columns)  # 7 + promedio de semillas
    c = D.corridas_pandemia(art)
    ge = pa.set_index("modelo").loc[D.NOMBRES["GE"]]
    assert round(c[c.modelo == "GE"].MAE.mean(), 3) == ge.MAE


def test_resumen_adversos_coincide_con_ficha(art):
    r = D.resumen_adversos(D.casos_adversos(art))
    tm = D.tablas_md(D.casos_adversos_md(art))[0][1]
    assert [f"{x:.3f}" for x in r.MAE] == [f"{float(x):.3f}" for x in tm["MAE"]]
    assert list(r.corridas_peor) == [int(x) for x in tm["corridas_peor"]]
    assert set(D.CASOS_GRAFO) <= set(r.caso)


# ---------------------------------------------------------------- pestaña 6 (Mapa de riesgo)
def test_mapa_riesgo_coincide_con_predicciones(art):
    if D.mapa_riesgo(art) is None:
        pytest.skip("falta el mapa de la v4: correr python -m src.mapa en la PC con los límites del INEI")
    m = D.mapa_riesgo(art).set_index("ubigeo")
    assert len(m) == 43
    p = D.predicciones(art)
    g = p[(p.modelo == "GE") & (p.ventana == "4")]
    u = g[g.periodo == g.periodo.max()].groupby("ubigeo").predicho.agg(["mean", "std"])
    assert (u["mean"].round(2) - m.predicho).abs().max() < 0.011
    assert (u["std"].round(2) - m.sd).abs().max() < 0.011


# ---------------------------------------------------------------- pestaña 7 (Pendientes)
def test_pendientes_v2(art):
    from app.vistas import pendientes
    filas = {f["Tema"]: f for f in pendientes.items(art)}
    assert "Jaccard 0,908" in filas["Solapamiento GE–GC₂ (Jaccard)"]["Detalle"]
    assert filas["Error de caché del grafo"]["Estado"] == "Corregido (declarado en el yaml)"
    assert filas["Reproducción en otra PC"]["Estado"] == "Cubierto"
    assert "60 de 60" in filas["Reproducción en otra PC"]["Detalle"]
    assert filas["Fig. 1 y Fig. 2"]["Estado"] == "Falta"
    assert filas["Selección multianual de hiperparámetros"]["Estado"] == "Redacción"
    assert "de 20 corridas" in filas["Fidelidad de la atención"]["Detalle"]
    assert "`metricas_referencias.csv` desactualizado" not in filas
    if D.mapa_riesgo(art) is None:
        assert filas["Mapa reproducible"]["Estado"] == "Falta"


def test_numeracion_cubre_todas_las_vistas():
    """Cada tabla y figura de las vistas tiene número sugerido (desde TABLA III y Fig. 7)."""
    import ast
    from app import avc3
    claves_t, claves_f = set(), set()
    for f in (RAIZ / "app" / "vistas").glob("*.py"):
        for n in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and len(n.args) >= 2                     and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
                if n.func.id == "tabla":
                    claves_t.add(n.args[1].value)
                elif n.func.id in ("figura", "figura_archivo"):
                    claves_f.add(n.args[1].value)
            # figuras del repositorio en listas de tuplas ("archivo.png", "clave", "pie")
            if isinstance(n, ast.Tuple) and len(n.elts) == 3 and all(isinstance(e, ast.Constant) for e in n.elts)                     and str(n.elts[0].value).endswith(".png"):
                claves_f.add(n.elts[1].value)
    assert len(claves_t) >= 25 and len(claves_f) >= 14
    assert not [c for c in claves_t if not avc3.numero_tabla(c)]
    assert not [c for c in claves_f if not avc3.numero_figura(c)]
    assert avc3.numero_tabla(avc3.TABLAS[0]) == "III" and avc3.numero_figura(avc3.FIGURAS[0]) == "7"
