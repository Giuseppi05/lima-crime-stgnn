"""Piezas comunes de las vistas: cita del AVC3, avisos, tablas y figuras con exportación."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app import avc3, exportar

NOTA_PREDICCIONES = "Se predicen denuncias registradas, no criminalidad real. Artefacto de investigación."
AVISO_CACHE = ("En revisión: un error de caché del grafo (`src/modelos.py`, `_lote_grafo`) puede haber hecho que "
               "las perturbaciones del grafo no se aplicaran. Estos valores se recalcularán.")

# Colores categóricos en orden fijo (paleta de referencia validada; el color sigue al modelo, nunca al rango)
COLOR_MODELO = {"GE": "#2a78d6", "GC2": "#eb6834", "GC1": "#1baf7a", "xgboost": "#eda100",
                "mes_anterior": "#e87ba4", "promedio_movil_3": "#008300", "mismo_mes_anio_anterior": "#6250d6"}
# Sectores: rampa ordinal de un solo tono (bajo → alto)
COLOR_SECTOR = {"bajo": "#86b6ef", "medio": "#2a78d6", "alto": "#104281"}
COLOR_REAL = "#0b0b0b"


def cita(*claves: str) -> None:
    lineas = [f"**AVC3, {avc3.CITAS[c][0]}:** «{avc3.CITAS[c][1]}»" for c in claves]
    st.info("  \n".join(lineas), icon="📄")


def nota_predicciones() -> None:
    st.caption(f"⚠️ {NOTA_PREDICCIONES}")


def pendiente(texto: str) -> None:
    st.warning(f"[PENDIENTE: {texto}]")


def calculado(texto: str) -> None:
    st.caption(f"🧮 Calculado en la interfaz: {texto}")


def _estado(clave: str) -> dict:
    return st.session_state.setdefault("_exportes", {}).setdefault(clave, {})


def _descargas(clave: str) -> None:
    e = _estado(clave)
    if not e:
        return
    cols = st.columns(len(e["archivos"]))
    for c, (nombre, (datos, mime)) in zip(cols, e["archivos"].items()):
        c.download_button(f"Descargar {nombre.rsplit('.', 1)[-1]}", datos, file_name=nombre, mime=mime,
                          key=f"dl_{clave}_{nombre}")
    st.caption("Guardado en: " + " · ".join(f"`{p}`" for p in e["rutas"]))


def tabla(df: pd.DataFrame, clave: str, titulo: str, nota: str = exportar.NOTA, altura: int | None = None) -> None:
    """Muestra una tabla ya formateada y ofrece exportarla como tabla del artículo (.docx + .csv)."""
    kw = {"height": altura} if altura else {}
    st.dataframe(df, hide_index=True, width="stretch", **kw)
    with st.expander("Exportar como tabla del artículo"):
        c1, c2 = st.columns([1, 4])
        numero = c1.text_input("TABLA N.", value=avc3.numero_tabla(clave), key=f"n_{clave}")
        tit = c2.text_input("Título", value=titulo, key=f"t_{clave}")
        nota_ = st.text_input("Nota", value=nota, key=f"nota_{clave}")
        if st.button("Exportar como tabla del artículo", key=f"b_{clave}"):
            base = exportar.nombre_archivo("TABLA", numero, tit)
            docx = exportar.tabla_docx(df, numero, tit, nota_)
            csv = exportar.tabla_csv(df)
            rutas = [exportar.guardar(f"{base}.docx", docx), exportar.guardar(f"{base}.csv", csv)]
            _estado(clave).update(archivos={
                f"{base}.docx": (docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                f"{base}.csv": (csv, "text/csv")}, rutas=[_rel(r) for r in rutas])
        _descargas(clave)


def figura(fig, clave: str, pie: str, nota: str = exportar.NOTA, alto_export: int | None = None) -> None:
    """Muestra un gráfico Plotly y ofrece exportarlo en PNG a 300 dpi con su pie."""
    st.plotly_chart(fig, width="stretch", key=f"g_{clave}")
    _exportar_figura(clave, pie, nota, lambda: exportar.imagen_de_plotly(fig, alto_px=alto_export))


def figura_archivo(ruta: Path, clave: str, pie: str, nota: str = exportar.NOTA) -> None:
    """Muestra una figura PNG ya generada por el repositorio y ofrece exportarla con su pie."""
    if not ruta.exists():
        pendiente(f"no existe `{_rel(ruta)}`")
        return
    st.image(str(ruta), width="stretch")
    st.caption(f"Archivo: `{_rel(ruta)}`")
    _exportar_figura(clave, pie, nota, ruta.read_bytes)


def _exportar_figura(clave: str, pie: str, nota: str, imagen) -> None:
    with st.expander("Exportar figura (PNG, 300 dpi)"):
        c1, c2 = st.columns([1, 4])
        numero = c1.text_input("Fig. N.", value=avc3.numero_figura(clave), key=f"fn_{clave}")
        pie_ = c2.text_input("Pie", value=pie, key=f"fp_{clave}")
        nota_ = st.text_input("Nota", value=nota, key=f"fnota_{clave}")
        if st.button("Exportar figura", key=f"fb_{clave}"):
            try:
                png = exportar.figura_png(imagen(), numero, pie_, nota_)
            except Exception as e:  # kaleido sin Chrome, etc.
                st.error(f"No se pudo generar la imagen: {e}")
            else:
                nombre = exportar.nombre_archivo("Fig", numero, pie_) + ".png"
                ruta = exportar.guardar(nombre, png)
                _estado(f"fig_{clave}").update(archivos={nombre: (png, "image/png")}, rutas=[_rel(ruta)])
        _descargas(f"fig_{clave}")


def _rel(p: Path) -> str:
    from app.datos import RAIZ
    try:
        return Path(p).resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return str(p)


def layout(fig, alto: int = 420, **kw):
    """Estilo común: fondo claro, rejilla tenue, leyenda arriba, tipografía del sistema."""
    fig.update_layout(height=alto, margin=dict(l=10, r=10, t=40, b=10), template="plotly_white",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None),
                      hoverlabel=dict(namelength=-1), separators=", ", **kw)
    fig.update_xaxes(showgrid=False, linecolor="#c3c2b7")
    fig.update_yaxes(gridcolor="#ecebe7", zerolinecolor="#c3c2b7")
    return fig
