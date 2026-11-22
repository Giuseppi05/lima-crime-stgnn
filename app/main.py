"""Interfaz local de resultados del artículo (solo lectura).

Uso: streamlit run app/main.py
Lee results/, data/processed/ y figuras/; las exportaciones van a app/exportes/.
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from app import datos as D  # noqa: E402
from app.componentes import AVISO_CACHE, NOTA_PREDICCIONES  # noqa: E402
from app.vistas import comparar, datos, desempeno, equidad, interpretabilidad  # noqa: E402

st.set_page_config(page_title="Resultados ST-GNN Lima", page_icon="📊", layout="wide")


def barra_lateral(versiones: list[D.Version]) -> D.Version:
    st.sidebar.title("Resultados del artículo")
    st.sidebar.caption("ST-GNN interpretable · denuncias de hurto y robo · Lima Metropolitana")
    etiquetas = [v.etiqueta for v in versiones]
    por_defecto = next((i for i, v in enumerate(versiones) if v.articulo), 0)
    elegida = st.sidebar.radio("Versión de resultados", etiquetas, index=por_defecto)
    v = versiones[etiquetas.index(elegida)]
    rel = lambda p: p.relative_to(RAIZ).as_posix() if p else "—"  # noqa: E731
    st.sidebar.markdown(f"- Fichas: `{rel(v.fichas)}`\n- Predicciones: `{rel(v.predicciones)}`\n"
                        f"- Figuras: `{rel(v.figuras)}`")
    st.sidebar.caption(f"`version.actual` en configs/ventanas.yaml: **{D.version_actual()}**")
    if D.aviso_cache_grafo(v):
        st.sidebar.caption("Corrección del caché del grafo: pendiente (rama fix/cache-grafo; la atención y los "
                           "casos adversos se recalcularán como el experimento h1_base). El aviso se apaga con "
                           "`correccion_cache_grafo: true` en el yaml de la versión.")
    else:
        st.sidebar.caption("Corrección del caché del grafo: declarada en el yaml de la versión.")
    if st.sidebar.button("Recargar archivos"):
        st.cache_data.clear()
        st.rerun()
    st.sidebar.divider()
    st.sidebar.caption(NOTA_PREDICCIONES + " No se usa para decisiones operativas de patrullaje.")
    return v


def en_construccion(titulo: str, contenido: str, aviso_cache: bool = False, v: D.Version | None = None) -> None:
    st.header(titulo)
    if aviso_cache and v is not None and D.aviso_cache_grafo(v):
        st.warning(AVISO_CACHE)
    st.info(f"Pestaña de la siguiente etapa. Mostrará: {contenido}")


def main() -> None:
    versiones = D.detectar_versiones()
    if not versiones:
        st.error("[PENDIENTE: no se encontró ninguna carpeta de resultados en results/]")
        return
    v = barra_lateral(versiones)
    pestañas = st.tabs(["1 · Datos (OE1)", "2 · Desempeño (OE2)", "3 · Interpretabilidad (OE3)", "4 · Equidad (OE4)",
                        "5 · Casos adversos", "6 · Mapa de riesgo", "7 · Pendientes", "Comparar versiones"])
    with pestañas[0]:
        datos.mostrar(v)
    with pestañas[1]:
        desempeno.mostrar(v)
    with pestañas[2]:
        interpretabilidad.mostrar(v)
    with pestañas[3]:
        equidad.mostrar(v)
    with pestañas[4]:
        en_construccion("Casos adversos", "pandemia (ventana P) y perturbaciones del grafo y de los datos.", True, v)
    with pestañas[5]:
        en_construccion("Mapa de riesgo (Despliegue)", "predicho, desviación entre semillas, real y error por "
                        "distrito.")
    with pestañas[6]:
        en_construccion("Pendientes del artículo", "lo que el AVC3 promete y falta o está parcial.")
    with pestañas[7]:
        comparar.mostrar(versiones, v)


main()
