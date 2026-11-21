# ST-GNN interpretable para denuncias de hurto y robo en Lima Metropolitana

Código del artículo *Redes neuronales de grafos interpretables para el modelado y la auditoría predictiva de la delincuencia urbana, Lima 2026*. Predice las denuncias de hurto + robo de los 43 distritos de Lima Metropolitana para el mes siguiente con una ST-GNN (GAT → GRU con atención temporal) y compara el grafo vial (GE) con un grafo geográfico (GC₂), una GRU sin grafo (GC₁), XGBoost y referencias simples.

Artefacto de investigación: **no está pensado para decisiones operativas de patrullaje.** Se predicen denuncias registradas, no delitos ocurridos.

## Estado

| Rama | Contenido |
| --- | --- |
| `main` | Versión estable v2: las seis fases de CRISP-DM con resultados completos (grilla ampliada, configuración elegida solo con validación). Resultados de la v1 en `results/v1/`. |
| `dev` | Desarrollo sobre la v2: diagnóstico de dependencia espacial y versión 3 (pérdida ponderada por volumen). Resultados de la v3 en `results/fichas/` y `results/v3/`; comparación en `results/fichas/comparacion_v1_v2_v3.md`. |

## Entorno

Python 3.13, entrenamiento en CPU con algoritmos deterministas (`torch.use_deterministic_algorithms(True)`): con la misma semilla las corridas se repiten exactas.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

## Datos externos

- Denuncias: `../Recursos/DATASET_Denuncias Policiales - Enero 2018 a Septiembre 2026.csv` (SIDPOL-MININTER, ODC-BY).
- Límites distritales del INEI y red vial de OpenStreetMap: ver `data/external/FUENTES.md`.

## Reproducción, por fases de CRISP-DM

| Fase | Comando | Salida principal |
| --- | --- | --- |
| Comprensión del problema | — | `configs/ventanas.yaml` (ventanas, semillas, grillas y criterio de parada) |
| Comprensión de los datos | `python -m src.datos` | `results/fichas/calidad.md`, `data/processed/panel.csv` |
| Preparación de los datos | `python -m src.grafos` | `data/processed/nodos.csv`, `aristas_*.csv`, `matriz_*.csv`, `results/fichas/validacion_grafos.md` |
| Modelado | `python -m src.baselines --pandemia` | referencias simples y XGBoost |
| Modelado | `python -m src.entrenar --fase ajuste`, luego `--fase congelar`, luego `--fase final` | grilla en validación, configuración congelada (H4), 4 ventanas × 5 semillas |
| Modelado (caso pandemia) | lo mismo con `--pandemia` | ventana P |
| Evaluación | `python -m src.evaluar`, `python -m src.atencion`, `python -m src.adversos` | OE2, OE3, OE4 y casos adversos en `results/fichas/` |
| Despliegue | `python -m src.mapa` | `results/figuras/mapa_riesgo_distrital.png` |

Cada script acepta `--rapido` (1 ventana, 1 semilla, pocas épocas) solo para comprobar que el código corre; sus salidas van a `results_rapido/` y no se usan en el artículo.

## Estructura

```
configs/ventanas.yaml   ventanas, semillas, grillas e hiperparámetros congelados
data/processed/         panel, nodos, aristas y matrices 43 × 43 (orden de ubigeo del panel)
src/                    datos, grafos, protocolo, baselines, modelos, entrenar, evaluar, atencion, adversos, mapa
results/predicciones/   {modelo}_{ventana}_{semilla}.csv: ubigeo, periodo, real, predicho, valido
results/atencion/       {modelo}_{ventana}_{semilla}.csv: pesos espaciales por arista y temporales por desfase
results/fichas/         tablas para el artículo
results/figuras/        figuras para el artículo
```

## Licencia

MIT (ver `LICENSE`). Los datos de terceros conservan sus licencias (ODC-BY para el SIDPOL; ODbL para OpenStreetMap).
