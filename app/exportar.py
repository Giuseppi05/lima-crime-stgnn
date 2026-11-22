"""Exportación para el artículo: tablas (.docx estilo IEEE + .csv) y figuras (PNG a 300 dpi con pie y nota).

Todo se escribe en `app/exportes/` (en .gitignore). Nada se escribe en `results/`.
"""
from __future__ import annotations

import io
import re
import unicodedata
from pathlib import Path

import pandas as pd

from app.datos import EXPORTES

NOTA = "Nota. Elaboración propia."
DPI = 300
ANCHO_IN = 7.16  # ancho de dos columnas IEEE, en pulgadas
FUENTE = "Times New Roman"


def nombre_archivo(prefijo: str, numero: str, titulo: str) -> str:
    t = unicodedata.normalize("NFKD", f"{prefijo}_{numero}_{titulo}").encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_")[:80]


def guardar(nombre: str, datos: bytes, carpeta: Path = EXPORTES) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / nombre
    ruta.write_bytes(datos)
    return ruta


# ---------------------------------------------------------------- tablas
def tabla_csv(df: pd.DataFrame) -> bytes:
    """Los mismos datos que el .docx (cifras ya formateadas con coma decimal), separados por ';' para Excel."""
    return df.to_csv(index=False, sep=";").encode("utf-8-sig")


def tabla_docx(df: pd.DataFrame, numero: str, titulo: str, nota: str = NOTA) -> bytes:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt

    doc = Document()
    estilo = doc.styles["Normal"]
    estilo.font.name = FUENTE
    estilo.font.size = Pt(10)

    def parrafo(texto, tam=10, centrado=True, cursiva=False, despues=0):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centrado else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(despues)
        r = p.add_run(texto)
        r.font.size = Pt(tam)
        r.font.name = FUENTE
        r.italic = cursiva
        return p

    parrafo(f"TABLA {numero}.")
    parrafo(titulo.upper(), despues=4)

    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, nombre in zip(t.rows[0].cells, df.columns):
        c.text = ""
        r = c.paragraphs[0].add_run(str(nombre))
        r.bold = True
        r.font.size = Pt(8)
    for _, fila in df.iterrows():
        celdas = t.add_row().cells
        for c, val in zip(celdas, fila):
            c.text = ""
            r = c.paragraphs[0].add_run("" if pd.isna(val) else str(val))
            r.font.size = Pt(8)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    r = p.add_run("Nota. ")
    r.italic = True
    r.font.size = Pt(8)
    r2 = p.add_run(nota.removeprefix("Nota. ").removeprefix("Nota."))
    r2.font.size = Pt(8)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------- figuras
def imagen_de_plotly(fig, ancho_px: int = 1100, alto_px: int | None = None) -> bytes:
    """PNG del gráfico Plotly (requiere kaleido y Chrome). Se renderiza a ~2150 px de ancho (7,16 in a 300 dpi)."""
    alto_px = alto_px or int(fig.layout.height or 500)
    escala = ANCHO_IN * DPI / ancho_px
    import plotly.graph_objects as go
    g = go.Figure(fig.to_dict())
    g.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_family=FUENTE, font_color="#0b0b0b",
                    title=None)
    return g.to_image(format="png", width=ancho_px, height=alto_px, scale=escala)


def figura_png(imagen: bytes, numero: str, pie: str, nota: str = NOTA) -> bytes:
    """Compone la imagen con su pie 'Fig. N. …' y la nota debajo, y la guarda a 300 dpi."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image

    img = Image.open(io.BytesIO(imagen)).convert("RGB")
    ancho_img = ANCHO_IN
    alto_img = ancho_img * img.height / img.width
    alto_pie = 0.55
    fig = plt.figure(figsize=(ancho_img, alto_img + alto_pie), dpi=DPI)
    ax = fig.add_axes((0, alto_pie / (alto_img + alto_pie), 1, alto_img / (alto_img + alto_pie)))
    ax.imshow(img, interpolation="lanczos")
    ax.axis("off")
    familia = [FUENTE, "DejaVu Serif"]
    y1 = (alto_pie - 0.18) / (alto_img + alto_pie)
    y2 = (alto_pie - 0.40) / (alto_img + alto_pie)
    fig.text(0.02, y1, f"Fig. {numero}. {pie}", fontsize=9, family=familia, va="center", ha="left", wrap=True)
    fig.text(0.02, y2, nota, fontsize=8, family=familia, va="center", ha="left", style="italic")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, facecolor="white")
    plt.close(fig)
    return buf.getvalue()
