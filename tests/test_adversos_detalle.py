"""El párrafo de casos de grafo de `casos_adversos.md` informa con 4 decimales y detecta sorteos repetidos.

Uso: python -m tests.test_adversos_detalle
"""
import pandas as pd

from src.adversos import detalle_grafo


def _corridas(repetir_sorteo: bool) -> pd.DataFrame:
    filas = []
    for w in ("1", "2"):
        base = 30.0 + int(w)
        filas.append({"ventana": w, "semilla": 0, "caso": "limpio", "nivel": "-", "MAE": base})
        for k in range(3):
            filas.append({"ventana": w, "semilla": 0, "caso": "ruido en coordenadas", "nivel": "σ = 500 m",
                          "MAE": base + 0.0001 * (k + 1)})
            mae = base + (0.5 if repetir_sorteo and k > 0 else 0.1 * k)
            filas.append({"ventana": w, "semilla": 0, "caso": "aristas eliminadas", "nivel": "30 %", "MAE": mae})
    r = pd.DataFrame(filas)
    r["MAE_limpio"] = r.ventana.map(r[r.caso == "limpio"].set_index("ventana").MAE)
    r["dMAE_%"] = (r.MAE / r.MAE_limpio - 1) * 100
    return r


CP = pd.DataFrame({"sigma_m": [500, 500], "sorteo": [0, 1], "cambio_abs_medio_peso": [0.0170, 0.0186]})


def test_cuatro_decimales_y_pesos():
    t = detalle_grafo(_corridas(False), CP)
    assert "MAE limpio 31,5000" in t and "con σ = 500 m, 31,5002" in t
    assert "< 0,01 % en 6 de 6 corridas" in t and "0 dieron un MAE idéntico" in t
    assert "0,0178 con σ = 500 m" in t
    assert "30 %: 0 de 2" in t


def test_detecta_sorteos_repetidos():
    assert "30 %: 2 de 2" in detalle_grafo(_corridas(True), CP)


if __name__ == "__main__":
    test_cuatro_decimales_y_pesos()
    test_detecta_sorteos_repetidos()
    print("ok: el detalle de casos de grafo usa 4 decimales y detecta sorteos repetidos")
