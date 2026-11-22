"""El choque común (v4) no debe filtrar información del mes objetivo ni de meses posteriores.

Para el mes objetivo t, la ventana de entrada son los meses t − H − L + 1 … t − H. Si se cambian las denuncias de t en
adelante, esa ventana tiene que quedar idéntica, y el rasgo tiene que ser el mismo en los 43 nodos.

Uso: GNN_EXPERIMENTO=h1_v4_choque python -m tests.test_choque_comun
"""
import os

import numpy as np

assert os.environ.get("GNN_EXPERIMENTO") == "h1_v4_choque", "correr con GNN_EXPERIMENTO=h1_v4_choque"

from src.entrenar import tensor_entrada, ventanas_x  # noqa: E402
from src.protocolo import CHOQUE_COMUN, Datos, Transformacion, cargar_datos, indices, ventanas  # noqa: E402


def test_sin_fuga():
    assert CHOQUE_COMUN
    d = cargar_datos()
    v = ventanas()["1"]
    tr = Transformacion(d, indices(d, v["entrenamiento"]))
    X = tensor_entrada(d, tr)
    assert X.shape[-1] == 5
    assert (X[..., 4] == X[:, :1, 4]).all(), "el choque común debe ser igual en todos los nodos"
    rng = np.random.default_rng(0)
    for t in indices(d, v["validacion"])[:3].tolist() + indices(d, v["prueba"])[:3].tolist():
        y2 = d.y.copy()
        y2[t:] = rng.integers(0, 5000, y2[t:].shape)  # futuro distinto
        d2 = Datos(d.periodos, d.ubigeos, d.distritos, y2, d.valido, d.pandemia, d.mes, d.extra)
        X2 = tensor_entrada(d2, tr)
        for L in (6, 12):
            assert (ventanas_x(X, np.array([t]), L) == ventanas_x(X2, np.array([t]), L)).all(), f"fuga en t={t}, L={L}"
        assert not (X[t:, 0, 4] == X2[t:, 0, 4]).all()  # el rasgo sí reacciona a los datos de su propio mes


if __name__ == "__main__":
    test_sin_fuga()
    print("ok: el choque común solo usa los meses de la ventana de entrada")
