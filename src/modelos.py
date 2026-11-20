"""Modelado: ST-GNN (GAT → GRU con atención temporal aditiva → ŷ(t+1)) y GRU sin grafo (GC₁).

GE y GC₂ son la misma clase con distinta matriz de adyacencia. GC₁ es la misma clase sin GAT: la capa
espacial se reemplaza por una proyección lineal por nodo con las mismas dimensiones, que es lo que
calcula un GAT cuando cada nodo solo se atiende a sí mismo. Así lo único que cambia entre los tres es el grafo.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch_geometric.nn import GATConv

N_RASGOS = 4  # objetivo transformado, mes seno, mes coseno, pandemia


class STGNN(nn.Module):
    def __init__(self, oculto: int, dropout: float, usar_grafo: bool, residual: bool, heads: int = 2):
        super().__init__()
        self.usar_grafo = usar_grafo
        self.residual = residual
        if usar_grafo:
            # concat=False promedia las cabezas: la salida tiene 'oculto' dimensiones, igual que en GC₁
            self.espacial = GATConv(N_RASGOS, oculto, heads=heads, concat=False, edge_dim=1,
                                    add_self_loops=True, fill_value="mean")
        else:
            self.espacial = nn.Linear(N_RASGOS, oculto)
        self.drop = nn.Dropout(dropout)
        self.gru = nn.GRU(oculto, oculto, batch_first=True)
        # atención aditiva (Bahdanau): consulta = último estado oculto, claves = todos los estados
        self.att_w = nn.Linear(oculto, oculto, bias=False)
        self.att_u = nn.Linear(oculto, oculto)
        self.att_v = nn.Linear(oculto, 1, bias=False)
        self.salida = nn.Linear(oculto, 1)
        self._cache = {}

    def _lote_grafo(self, edge_index, edge_attr, n_grafos, n_nodos):
        clave = (n_grafos, n_nodos, edge_index.data_ptr())
        if clave not in self._cache:
            desp = (torch.arange(n_grafos) * n_nodos).view(1, -1, 1)
            ei = (edge_index.unsqueeze(1) + desp).reshape(2, -1)
            ea = edge_attr.repeat(n_grafos, 1)
            self._cache = {clave: (ei, ea)}
        return self._cache[clave]

    def forward(self, x, edge_index=None, edge_attr=None, atencion=False):
        """x: [B, L, N, F] → ŷ: [B, N] en escala transformada."""
        B, L, N, F = x.shape
        alfa = None
        if self.usar_grafo:
            ei, ea = self._lote_grafo(edge_index, edge_attr, B * L, N)
            h, (ei_out, alfa) = self.espacial(x.reshape(B * L * N, F), ei, ea, return_attention_weights=True)
        else:
            h = self.espacial(x)
        h = self.drop(torch.nn.functional.elu(h)).reshape(B, L, N, -1).permute(0, 2, 1, 3).reshape(B * N, L, -1)
        estados, _ = self.gru(h)
        q = estados[:, -1]
        e = self.att_v(torch.tanh(self.att_w(estados) + self.att_u(q).unsqueeze(1)))
        beta = torch.softmax(e, dim=1)               # [B·N, L, 1]
        contexto = (beta * estados).sum(1)
        y = self.salida(self.drop(contexto)).view(B, N)
        if self.residual:
            y = y + x[:, -1, :, 0]  # predice el cambio respecto del último mes observado
        if not atencion:
            return y
        extra = {"temporal": beta.view(B, N, L)}
        if alfa is not None:
            extra["espacial"] = (ei_out, alfa.mean(1), B, L, N)
        return y, extra


def atencion_a_tablas(extra, ubigeos, periodos_objetivo, L) -> pd.DataFrame:
    """Pesos de atención en formato largo: espacial por arista y mes de entrada; temporal por desfase."""
    filas = []
    ub = np.array(ubigeos)
    beta = extra["temporal"].detach().numpy()  # [B, N, L]
    B, N, _ = beta.shape
    b, n, l = np.meshgrid(np.arange(B), np.arange(N), np.arange(L), indexing="ij")
    filas.append(pd.DataFrame({
        "tipo": "temporal", "periodo": np.array(periodos_objetivo)[b.ravel()], "desfase": (L - l).ravel(),
        "origen": ub[n.ravel()], "destino": ub[n.ravel()], "peso": beta.ravel().round(6)}))
    if "espacial" in extra:
        ei, a, B, L_, N = extra["espacial"]
        ei = ei.numpy()
        g = ei[1] // N
        filas.append(pd.DataFrame({
            "tipo": "espacial", "periodo": np.array(periodos_objetivo)[g // L_], "desfase": L_ - g % L_,
            "origen": ub[ei[0] % N], "destino": ub[ei[1] % N], "peso": a.detach().numpy().round(6)}))
    return pd.concat(filas, ignore_index=True)
