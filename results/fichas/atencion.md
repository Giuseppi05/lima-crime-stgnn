# Evaluación: interpretabilidad mediante los pesos de atención (OE3)

Generado por `python -m src.atencion`. Pesos de la prueba de las 4 ventanas × 5 semillas. En el GAT, la atención de cada distrito destino suma 1 entre sus vecinos y él mismo. Se interpretan como indicio, no como causa. Nota. Elaboración propia.

## Atención temporal por desfase

Media sobre distritos, meses de prueba y semillas, por separado según los meses de entrada (L) que eligió la validación en cada ventana. Una atención uniforme valdría 1/L (0,167 con L = 6; 0,083 con L = 12).

|   desfase |   GE (L=6) |   GE (L=12) |   GC2 (L=6) |   GC2 (L=12) |   GC1 (L=6) |   GC1 (L=12) |
|----------:|-----------:|------------:|------------:|-------------:|------------:|-------------:|
|         1 |     0.3011 |      0.0834 |      0.266  |       0.0834 |      0.1649 |       0.0901 |
|         2 |     0.161  |      0.0834 |      0.1579 |       0.0833 |      0.1657 |       0.0849 |
|         3 |     0.1314 |      0.0833 |      0.1376 |       0.0833 |      0.1665 |       0.0833 |
|         4 |     0.1273 |      0.0832 |      0.1345 |       0.0832 |      0.1672 |       0.0827 |
|         5 |     0.1315 |      0.0832 |      0.14   |       0.0832 |      0.1676 |       0.082  |
|         6 |     0.1477 |      0.0832 |      0.1641 |       0.0832 |      0.1681 |       0.0821 |
|         7 |   nan      |      0.0831 |    nan      |       0.0831 |    nan      |       0.0822 |
|         8 |   nan      |      0.0831 |    nan      |       0.0831 |    nan      |       0.082  |
|         9 |   nan      |      0.0831 |    nan      |       0.0831 |    nan      |       0.0821 |
|        10 |   nan      |      0.0832 |    nan      |       0.0832 |    nan      |       0.0819 |
|        11 |   nan      |      0.0835 |    nan      |       0.0835 |    nan      |       0.0855 |
|        12 |   nan      |      0.0842 |    nan      |       0.0842 |    nan      |       0.0811 |

Figura: `results/figuras/atencion_temporal.png`

## Atención espacial frente a la conectividad vial y la contigüidad

Autoatención media (peso del propio distrito): GE 0.224; GC₂ 0.210.

Correlación de Spearman por arista. En el GE (89 aristas) 89 son contiguas, así que la contigüidad binaria es constante y la contigüidad se mide además como longitud del límite compartido (km). En el GC₂ (98 aristas) 9 pares contiguos no tienen tramo vial que cruce (peso vial 0). `peso_x_grado` multiplica la atención por el número medio de entradas del par (vecinos + 1) para quitar el efecto de la normalización por nodo.

| modelo   | atencion     | contra    |      rho |        p |   n_aristas | nota      |
|:---------|:-------------|:----------|---------:|---------:|------------:|:----------|
| GE       | peso         | peso_vial |  -0.1379 |   0.1974 |          89 |           |
| GE       | peso         | n_tramos  |   0.1246 |   0.2447 |          89 |           |
| GE       | peso         | limite_km |   0.4046 |   0.0001 |          89 |           |
| GE       | peso         | contiguo  | nan      | nan      |          89 | constante |
| GE       | peso_x_grado | peso_vial |   0.1689 |   0.1137 |          89 |           |
| GE       | peso_x_grado | n_tramos  |   0.1137 |   0.2885 |          89 |           |
| GE       | peso_x_grado | limite_km |  -0.0213 |   0.8428 |          89 |           |
| GE       | peso_x_grado | contiguo  | nan      | nan      |          89 | constante |
| GC2      | peso         | peso_vial |   0.0415 |   0.6848 |          98 |           |
| GC2      | peso         | n_tramos  |   0.1269 |   0.213  |          98 |           |
| GC2      | peso         | limite_km |   0.2161 |   0.0326 |          98 |           |
| GC2      | peso_x_grado | peso_vial |  -0.0071 |   0.9446 |          98 |           |
| GC2      | peso_x_grado | n_tramos  |  -0.0106 |   0.9178 |          98 |           |
| GC2      | peso_x_grado | limite_km |  -0.0459 |   0.6532 |          98 |           |

### Top 10 de pares por atención (GE)

| par                               |   peso |   peso_x_grado |   peso_vial |   n_tramos |   limite_km |
|:----------------------------------|-------:|---------------:|------------:|-----------:|------------:|
| PUCUSANA – SANTA MARIA DEL MAR    | 0.4083 |         1.0206 |      0.4063 |          2 |      4.5018 |
| ANCON – SANTA ROSA                | 0.3747 |         1.1242 |      0.6908 |         37 |      8.5514 |
| PUNTA NEGRA – SAN BARTOLO         | 0.3307 |         0.992  |      0.4917 |         15 |     14.2266 |
| SAN BARTOLO – SANTA MARIA DEL MAR | 0.3298 |         0.9895 |      0.6075 |         16 |      4.353  |
| PUNTA HERMOSA – PUNTA NEGRA       | 0.3287 |         0.9862 |      0.3115 |          7 |     26.2118 |
| LURIN – PUNTA HERMOSA             | 0.2717 |         1.0869 |      0.6971 |         34 |     27.9633 |
| CHACLACAYO – CIENEGUILLA          | 0.2537 |         1.0149 |      0.2434 |          1 |      7.6583 |
| ANCON – CARABAYLLO                | 0.2458 |         0.9831 |      0.1486 |          3 |     10.6362 |
| EL AGUSTINO – SANTA ANITA         | 0.2378 |         1.1888 |      0.7523 |         16 |      8.4462 |
| BARRANCO – MIRAFLORES             | 0.2314 |         1.0413 |      0.8004 |         23 |      1.8819 |

### Top 10 de pares por atención corregida por grado (GE)

| par                           |   peso |   peso_x_grado |   peso_vial |   n_tramos |   limite_km |
|:------------------------------|-------:|---------------:|------------:|-----------:|------------:|
| ATE – SANTA ANITA             | 0.2162 |         1.405  |      0.7689 |         43 |      7.6326 |
| LIMA – BREÑA                  | 0.1734 |         1.3005 |      0.8531 |         39 |      5.3652 |
| LIMA – SAN MIGUEL             | 0.1713 |         1.285  |      0.6643 |         12 |      1.9542 |
| ATE – LA MOLINA               | 0.1763 |         1.2343 |      0.6969 |         31 |     11.7941 |
| ATE – CHACLACAYO              | 0.1761 |         1.2328 |      0.421  |          3 |      8.5835 |
| ATE – CIENEGUILLA             | 0.1728 |         1.2096 |      0.4576 |         13 |     13.4739 |
| EL AGUSTINO – SANTA ANITA     | 0.2378 |         1.1888 |      0.7523 |         16 |      8.4462 |
| LIMA – RIMAC                  | 0.1471 |         1.1769 |      0.744  |         16 |      3.995  |
| LIMA – SAN MARTIN DE PORRES   | 0.1462 |         1.17   |      0.624  |         11 |      4.6735 |
| LA MOLINA – SANTIAGO DE SURCO | 0.1797 |         1.1678 |      0.7221 |         27 |      8.7261 |

## Prueba de fidelidad (complementaria)

En cada una de las 20 corridas del GE se quitó el 10 % de las aristas con más atención en esa corrida y, aparte, el mismo número de aristas al azar (10 sorteos, promedio). Sin reentrenar. Si la atención señala aristas útiles, quitar las de más atención debería subir más el MAE.

|   ventana |   MAE_base |   dMAE_top |   dMAE_azar |
|----------:|-----------:|-----------:|------------:|
|         1 |     37.229 |     -0.005 |       0.004 |
|         2 |     38.681 |      0.001 |       0.009 |
|         3 |     32.343 |     -0.113 |       0.042 |
|         4 |     25.372 |     -0.091 |      -0.003 |

Promedio de las 20 corridas: ΔMAE top -0.052; ΔMAE azar 0.013. Corridas donde quitar las de más atención dañó más que el azar: 4 de 20. Wilcoxon pareado: p = 0.0064.
