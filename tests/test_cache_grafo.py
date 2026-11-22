"""El modelo debe usar el grafo que recibe en cada llamada, aunque antes haya visto otro.

Antes de la corrección, la caché de STGNN._lote_grafo usaba como clave edge_index.data_ptr(). Si llegaba un
grafo distinto (aristas eliminadas, ruido en coordenadas) y PyTorch reutilizaba esa memoria, el modelo
seguía usando el grafo anterior.

Uso: python -m tests.test_cache_grafo
"""
import numpy as np
import torch

from src.entrenar import cargar_grafo
from src.modelos import STGNN

N, L, F = 43, 6, 4


def _matrices(rng):
    A = np.triu((rng.random((N, N)) < 0.1) * rng.uniform(0.05, 1, (N, N)), 1)
    A = A + A.T
    W = np.where(A > 0, np.clip(A * rng.uniform(0.3, 1.7, A.shape), 0.01, 1), 0)  # mismas aristas, otros pesos
    Q = A.copy()
    i, j = np.nonzero(np.triu(Q, 1))
    Q[i[: len(i) // 3], j[: len(i) // 3]] = 0  # menos aristas
    Q[j[: len(i) // 3], i[: len(i) // 3]] = 0
    return A, W, Q


def _pred(modelo, x, matriz):
    ei, ea = cargar_grafo("x", [], matriz)
    with torch.no_grad():
        return modelo(x, ei, ea)


def test_cambiar_de_grafo():
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    A, W, Q = _matrices(rng)
    x = torch.randn(2, L, N, F)
    modelo = STGNN(16, 0.0, usar_grafo=True, residual=True).eval()
    for otra in (W, Q):
        for _ in range(20):  # muchas repeticiones: la reutilización de memoria es aleatoria
            p_a = _pred(modelo, x, A)
            p_otra = _pred(modelo, x, otra)
            modelo._cache = {}
            esperado = _pred(modelo, x, otra)
            assert torch.equal(p_otra, esperado), "el modelo usó un grafo anterior guardado en la caché"
            assert not torch.equal(p_a, p_otra), "dos grafos distintos dieron la misma predicción"


def test_mismo_grafo_reusa_cache():
    modelo = STGNN(16, 0.0, usar_grafo=True, residual=True).eval()
    ei, ea = cargar_grafo("x", [], _matrices(np.random.default_rng(1))[0])
    x = torch.randn(1, L, N, F)
    with torch.no_grad():
        modelo(x, ei, ea)
        lote = modelo._cache["lote"]
        modelo(x, ei, ea)
    assert modelo._cache["lote"] is lote


if __name__ == "__main__":
    test_cambiar_de_grafo()
    test_mismo_grafo_reusa_cache()
    print("ok: la caché del grafo respeta el grafo de cada llamada")
