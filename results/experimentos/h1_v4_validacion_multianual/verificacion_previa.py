import pandas as pd, numpy as np
from scipy.stats import spearmanr
from src.protocolo import cargar_datos, indices, ventanas
a = pd.read_csv("results/fichas/ajuste_hiperparametros.csv", dtype={"ventana": str})
r = a[a.salida == "residual"].copy()
K = ["oculto", "lr", "dropout", "entrada_meses"]
r["cfg"] = r[K].astype(str).agg("/".join, axis=1)
M = r.pivot_table(index=["modelo", "cfg"], columns="ventana", values="mae_validacion")  # [modelo×48, ventana]
d = cargar_datos(); vs = ventanas()
pers = {w: np.abs(d.y[i] - d.y[i - 1])[d.valido[i]].mean() for w, v in vs.items() for i in [indices(d, v["validacion"])]}
print("persistencia en cada año de validación:", {w: round(x, 3) for w, x in pers.items()})
filas = []
for m in ["GE", "GC2", "GC1"]:
    X = M.loc[m]
    for w in ["2", "3", "4"]:
        prev = [str(k) for k in range(1, int(w))]
        cA = X[str(int(w) - 1)].idxmin()                 # A: un año (ventana w−1)
        cB = X[prev].mean(1).idxmin()                    # B: promedio de los años previos
        cBr = (X[prev] / pd.Series(pers)[prev]).mean(1).idxmin()  # B': promedio relativo a la persistencia (sensibilidad)
        cC = X[w].idxmin()                               # C: elige con el mismo año (optimista, como hoy)
        filas.append({"modelo": m, "ventana": w, "A_cfg": cA, "A": X.loc[cA, w], "B_cfg": cB, "B": X.loc[cB, w],
                      "Brel": X.loc[cBr, w], "C_mismo_anio": X.loc[cC, w], "mediana_48": X[w].median(),
                      "rango_A_en_w": int(X[w].rank().loc[cA]), "rango_B_en_w": int(X[w].rank().loc[cB]),
                      "spearman_w-1_w": spearmanr(X[str(int(w) - 1)], X[w])[0], "persistencia": pers[w]})
t = pd.DataFrame(filas)
pd.set_option("display.width", 250)
print(t.round(3).to_string(index=False))
t.to_csv(__import__("sys").argv[1], index=False)
# ¿y la configuración de 'h1_base' para la ventana w (elegida con su propio año) en el año siguiente?
print("\nconfig elegida hoy con el año w, medida en el año w+1 (ventana w+1):")
for m in ["GE", "GC2", "GC1"]:
    X = M.loc[m]
    print(m, [(w, round(X.loc[X[w].idxmin(), str(int(w)+1)], 3), round(X[str(int(w)+1)].min(), 3)) for w in ["1", "2", "3"]])
