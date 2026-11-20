# ST-GNN interpretable para denuncias de hurto y robo en Lima Metropolitana

Código del artículo *Redes neuronales de grafos interpretables para el modelado y la auditoría predictiva de la delincuencia urbana, Lima 2026*. Predice las denuncias de hurto + robo de los 43 distritos de Lima Metropolitana para el mes siguiente con una ST-GNN (GAT → GRU con atención temporal) y compara el grafo vial (GE) con un grafo geográfico (GC₂), una GRU sin grafo (GC₁), XGBoost y referencias simples.

Artefacto de investigación: **no está pensado para decisiones operativas de patrullaje.** Se predicen denuncias registradas, no delitos ocurridos.

## Estado

| Rama | Contenido |
| --- | --- |
| `main` | Fases cerradas y validadas: Comprensión del problema, Comprensión de los datos y Preparación de los datos (panel y grafos). |
| `dev` | Modelado, Evaluación y Despliegue en desarrollo. |

## Entorno

Python 3.13, entrenamiento en CPU con algoritmos deterministas: con la misma semilla las corridas se repiten exactas.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

## Datos externos

- Denuncias: SIDPOL (PNP), publicadas por el MININTER en datosabiertos.gob.pe (licencia ODC-BY). El script lee `../Recursos/DATASET_Denuncias Policiales - Enero 2018 a Septiembre 2026.csv`.
- Límites distritales del INEI (IDE, capa 2023) y red vial de OpenStreetMap: ver `data/external/FUENTES.md`.

## Reproducción

| Fase de CRISP-DM | Comando | Salida principal |
| --- | --- | --- |
| Comprensión de los datos | `python -m src.datos` | `data/processed/panel.csv`, `results/fichas/calidad.md`, `results/figuras/` |
| Preparación de los datos | `python -m src.grafos` | `data/processed/nodos.csv`, `aristas_geo.csv`, `aristas_vial.csv`, `matriz_*.csv`, `results/fichas/validacion_grafos.md`, `results/figuras/mapa_grafos.png` |

Las matrices 43 × 43 siguen el mismo orden de ubigeo que el panel.

## Licencia

MIT (ver `LICENSE`). Los datos de terceros conservan sus licencias (ODC-BY para el SIDPOL; ODbL para OpenStreetMap).
