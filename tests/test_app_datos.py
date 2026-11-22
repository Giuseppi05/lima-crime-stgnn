"""Pruebas mínimas de la interfaz de resultados: lectores de la v2 y cifras de la tabla global.

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
def v2() -> D.Version:
    vs = [v for v in D.detectar_versiones() if v.articulo]
    assert len(vs) == 1, "debe existir exactamente una versión del artículo (results/fichas)"
    return vs[0]


def test_detecta_v1_y_articulo():
    claves = [v.clave for v in D.detectar_versiones()]
    assert "v1" in claves
    assert D.version_actual() in claves


@pytest.mark.parametrize("lector, columnas, filas", [
    (D.metricas_global, ["modelo", "MAE", "RMSE", "R2", "MASE", "MAE_sd", "RMSE_sd"], 7),
    (D.metricas_por_ventana, ["modelo", "ventana", "MAE", "RMSE", "R2", "MAE_sd"], 28),
    (D.metricas_por_distrito, ["modelo", "ubigeo", "MAE", "RMSE", "distrito"], 7 * 43),
    (D.corridas_neuronales, ["modelo", "ventana", "semilla", "mae_validacion", "MAE", "RMSE", "R2"], 60),
    (D.pruebas_estadisticas, ["comparacion", "MAE_GE", "MAE_rival", "RMSE_GE", "RMSE_rival", "p", "GE_supera"], 4),
    (D.equidad_por_distrito, ["modelo", "ubigeo", "error_rel", "distrito", "sector", "volumen_entrenamiento"], 7 * 43),
    (D.equidad_resumen, ["modelo", "brecha", "brecha_sin_playa", "media_bajo", "media_medio", "media_alto"], 7),
    (D.equidad_sectores, ["modelo", "prueba", "estadistico", "p", "significativa"], 7),
])
def test_lectores_v2(v2, lector, columnas, filas):
    df = lector(v2)
    assert df is not None, f"{lector.__name__} no encontró su archivo"
    assert set(columnas) <= set(df.columns)
    assert len(df) >= filas if lector is D.metricas_por_ventana else len(df) == filas


def test_predicciones_v2(v2):
    p = D.predicciones(v2)
    assert p is not None
    assert {"ubigeo", "periodo", "real", "predicho", "valido", "modelo", "ventana", "semilla"} <= set(p.columns)
    assert p.ubigeo.str.len().eq(6).all()
    assert set(D.VENTANAS_PRUEBA) <= set(p.ventana)
    # 3 neuronales × 5 ventanas × 5 semillas + 4 deterministas × 5 ventanas, 516 filas cada uno
    assert len(p) == (3 * 5 * 5 + 4 * 5) * 516


def test_lector_ausente_devuelve_none(v2):
    v1 = next(v for v in D.detectar_versiones() if v.clave == "v1")
    assert D.equidad_resumen(v1) is None
    assert D.predicciones(v1) is None


def test_tabla_global_coincide_con_archivo(v2):
    """Las cifras que muestra la tabla global son las de metricas_global.csv, con coma decimal y 3 decimales."""
    from app.vistas import desempeno  # noqa: F401  (importa la vista: debe cargar sin Streamlit en ejecución)
    crudo = pd.read_csv(v2.archivo("metricas_global.csv")).set_index("modelo")
    g = D.metricas_global(v2).set_index("modelo")
    pd.testing.assert_frame_equal(g, crudo)
    assert F.ms(g.loc["GE", "MAE"], g.loc["GE", "MAE_sd"]) == "33,469 ± 1,368"
    assert F.ms(g.loc["GE", "RMSE"], g.loc["GE", "RMSE_sd"]) == "55,335 ± 2,559"
    assert F.ms(g.loc["xgboost", "MAE"], g.loc["xgboost", "MAE_sd"]) == "57,039"
    for m, fila in g.iterrows():
        assert F.num(fila.MAE) == f"{fila.MAE:.3f}".replace(".", ",")


def test_global_recalculada_desde_predicciones(v2):
    r = D.metricas_global_desde_predicciones(D.predicciones(v2))
    g = D.metricas_global(v2).set_index("modelo")
    for c in ["MAE", "RMSE", "R2", "MAE_sd", "RMSE_sd"]:
        assert (r[c] - g.loc[r.index, c]).abs().max() < 1e-9, c


def test_regla_avc3_coincide(v2):
    p = D.pruebas_estadisticas(v2)
    assert (p.apply(D.regla_avc3, axis=1) == p.GE_supera).all()


def test_mismo_conjunto_de_prueba(v2):
    r = D.verificar_mismo_conjunto(D.predicciones(v2))
    assert r.iguales.all()
    assert (r.celdas == 516).all()


def test_r2_por_distrito(v2):
    p = D.predicciones(v2)
    for modo in ["ventana", "48"]:
        r = D.r2_por_distrito(p, modo)
        assert r.groupby("modelo").size().eq(43).all()
        assert r.loc[r.modelo == "GE", "n_semillas"].eq(5).all()
        assert r.loc[r.modelo == "mes_anterior", "n_semillas"].eq(1).all()


def test_brecha_y_composicion(v2):
    r = D.equidad_resumen(v2)
    b = D.brecha_entre_sectores(r)
    assert (b >= 0).all()
    c = D.composicion_sectores(D.equidad_por_distrito(v2))
    assert c.n.sum() == 43 and list(c.sector) == D.SECTORES


def test_aviso_cache(v2, tmp_path):
    # sin la clave en el yaml, el aviso va en todas las versiones actuales
    assert all(D.aviso_cache_grafo(v) for v in D.detectar_versiones())
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


def test_validacion_grafos_coincide_con_ficha(v2):
    nod = D.nodos()
    ub = list(nod.ubigeo)
    rg, rv = D.resumen_grafo(D.aristas("geo"), ub), D.resumen_grafo(D.aristas("vial"), ub)
    assert (rg["aristas"], rv["aristas"]) == (98, 89) and rg["conectado"] and rv["conectado"]
    g = D.tabla_md(D.validacion_grafos_md(v2), "Grafos")
    assert list(g["Aristas"]) == ["98", "89"]
    assert list(g["Grado medio"]) == [f"{rg['grado_medio']:.2f}", f"{rv['grado_medio']:.2f}"]
    d = D.distancia_red_vs_recta(nod)
    assert d["pares"] == 903 and d["violaciones"] == 0
    assert f"{d['cociente_min']:.3f}" == "1.038" and f"{d['cociente_mediana']:.3f}" == "1.215"


def test_cobertura_coincide_con_calidad(v2):
    p = D.panel()
    c = D.cobertura(p).set_index("estado").celdas
    assert (c["observado"], c["cero"], c["sin_informacion"]) == (4446, 60, 9)
    assert "observado 4446, cero 60, sin_informacion 9" in D.calidad_md(v2)
    assert len(p) == 43 * 105 and not p.duplicated(["ubigeo", "periodo"]).any()
    assert F.entero(p.objetivo.sum()) == "957 705"


def test_configuracion_es_la_de_validacion(v2):
    cfg, aj = D.configuracion(v2), D.ajuste_hiperparametros(v2)
    ver = D.verificar_configuracion(cfg, aj, cfg["salida_neuronal"]["elegida"])
    assert len(ver) == 15 and ver.coincide.all()
    prom = D.eleccion_salida_desde_ajuste(aj)
    esperado = cfg["salida_neuronal"]["mae_validacion_promedio"]
    assert round(prom["residual"], 4) == esperado["residual"] and round(prom["directa"], 4) == esperado["directa"]
