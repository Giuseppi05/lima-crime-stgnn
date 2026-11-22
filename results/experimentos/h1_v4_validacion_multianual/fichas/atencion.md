# Evaluación: interpretabilidad mediante los pesos de atención (OE3)

Generado por `python -m src.atencion`. Pesos de la prueba de las 4 ventanas × 5 semillas. En el GAT, la atención de cada distrito destino suma 1 entre sus vecinos y él mismo. Se interpretan como indicio, no como causa. Nota. Elaboración propia.

## Atención temporal por desfase

Media sobre distritos, meses de prueba y semillas, por separado según los meses de entrada (L) que eligió la validación en cada ventana. Una atención uniforme valdría 1/L (0,167 con L = 6; 0,083 con L = 12).

|   desfase |   GE (L=6) |   GE (L=12) |   GC2 (L=6) |   GC2 (L=12) |   GC1 (L=6) |   GC1 (L=12) |
|----------:|-----------:|------------:|------------:|-------------:|------------:|-------------:|
|         1 |     0.1602 |      0.0867 |      0.16   |       0.086  |      0.1665 |       0.0838 |
|         2 |     0.1616 |      0.0855 |      0.1615 |       0.0849 |      0.1666 |       0.0838 |
|         3 |     0.1637 |      0.0844 |      0.1637 |       0.084  |      0.1668 |       0.0838 |
|         4 |     0.1669 |      0.0836 |      0.1669 |       0.0833 |      0.1668 |       0.0837 |
|         5 |     0.1707 |      0.0829 |      0.1708 |       0.0827 |      0.1667 |       0.0837 |
|         6 |     0.1768 |      0.0821 |      0.177  |       0.0821 |      0.1666 |       0.0836 |
|         7 |   nan      |      0.0813 |    nan      |       0.0815 |    nan      |       0.0835 |
|         8 |   nan      |      0.0808 |    nan      |       0.0812 |    nan      |       0.0833 |
|         9 |   nan      |      0.0808 |    nan      |       0.0812 |    nan      |       0.0831 |
|        10 |   nan      |      0.0813 |    nan      |       0.0818 |    nan      |       0.0828 |
|        11 |   nan      |      0.0831 |    nan      |       0.0835 |    nan      |       0.0825 |
|        12 |   nan      |      0.0876 |    nan      |       0.0879 |    nan      |       0.0823 |

Figura: `results/figuras/atencion_temporal.png`

## Atención espacial frente a la conectividad vial y la contigüidad

Autoatención media (peso del propio distrito): GE 0.223; GC₂ 0.209.

Correlación de Spearman por arista. En el GE (89 aristas) 89 son contiguas, así que la contigüidad binaria es constante y la contigüidad se mide además como longitud del límite compartido (km). En el GC₂ (98 aristas) 9 pares contiguos no tienen tramo vial que cruce (peso vial 0). `peso_x_grado` multiplica la atención por el número medio de entradas del par (vecinos + 1) para quitar el efecto de la normalización por nodo.

| modelo   | atencion     | contra    |      rho |        p |   n_aristas | nota      |
|:---------|:-------------|:----------|---------:|---------:|------------:|:----------|
| GE       | peso         | peso_vial |  -0.1255 |   0.2414 |          89 |           |
| GE       | peso         | n_tramos  |   0.1347 |   0.2081 |          89 |           |
| GE       | peso         | limite_km |   0.4081 |   0.0001 |          89 |           |
| GE       | peso         | contiguo  | nan      | nan      |          89 | constante |
| GE       | peso_x_grado | peso_vial |   0.2064 |   0.0523 |          89 |           |
| GE       | peso_x_grado | n_tramos  |   0.161  |   0.1318 |          89 |           |
| GE       | peso_x_grado | limite_km |   0.0172 |   0.8731 |          89 |           |
| GE       | peso_x_grado | contiguo  | nan      | nan      |          89 | constante |
| GC2      | peso         | peso_vial |   0.0481 |   0.6378 |          98 |           |
| GC2      | peso         | n_tramos  |   0.1371 |   0.1784 |          98 |           |
| GC2      | peso         | limite_km |   0.2228 |   0.0274 |          98 |           |
| GC2      | peso_x_grado | peso_vial |   0.0225 |   0.8262 |          98 |           |
| GC2      | peso_x_grado | n_tramos  |   0.0325 |   0.7506 |          98 |           |
| GC2      | peso_x_grado | limite_km |  -0.0133 |   0.8962 |          98 |           |

### Top 10 de pares por atención (GE)

| par                               |   peso |   peso_x_grado |   peso_vial |   n_tramos |   limite_km |
|:----------------------------------|-------:|---------------:|------------:|-----------:|------------:|
| PUCUSANA – SANTA MARIA DEL MAR    | 0.4109 |         1.0272 |      0.4063 |          2 |      4.5018 |
| ANCON – SANTA ROSA                | 0.3734 |         1.1203 |      0.6908 |         37 |      8.5514 |
| PUNTA NEGRA – SAN BARTOLO         | 0.3344 |         1.0032 |      0.4917 |         15 |     14.2266 |
| SAN BARTOLO – SANTA MARIA DEL MAR | 0.3324 |         0.9973 |      0.6075 |         16 |      4.353  |
| PUNTA HERMOSA – PUNTA NEGRA       | 0.328  |         0.984  |      0.3115 |          7 |     26.2118 |
| LURIN – PUNTA HERMOSA             | 0.2711 |         1.0844 |      0.6971 |         34 |     27.9633 |
| CHACLACAYO – CIENEGUILLA          | 0.2547 |         1.0186 |      0.2434 |          1 |      7.6583 |
| ANCON – CARABAYLLO                | 0.2477 |         0.9907 |      0.1486 |          3 |     10.6362 |
| CHACLACAYO – LURIGANCHO - CHOSICA | 0.2333 |         1.0497 |      0.6659 |         10 |     16.6321 |
| EL AGUSTINO – SANTA ANITA         | 0.2326 |         1.163  |      0.7523 |         16 |      8.4462 |

### Top 10 de pares por atención corregida por grado (GE)

| par                           |   peso |   peso_x_grado |   peso_vial |   n_tramos |   limite_km |
|:------------------------------|-------:|---------------:|------------:|-----------:|------------:|
| ATE – SANTA ANITA             | 0.2196 |         1.4274 |      0.7689 |         43 |      7.6326 |
| LIMA – BREÑA                  | 0.1741 |         1.306  |      0.8531 |         39 |      5.3652 |
| LIMA – SAN MIGUEL             | 0.1741 |         1.3059 |      0.6643 |         12 |      1.9542 |
| ATE – LA MOLINA               | 0.1773 |         1.2413 |      0.6969 |         31 |     11.7941 |
| ATE – CHACLACAYO              | 0.1745 |         1.2218 |      0.421  |          3 |      8.5835 |
| ATE – CIENEGUILLA             | 0.1728 |         1.2096 |      0.4576 |         13 |     13.4739 |
| LIMA – RIMAC                  | 0.1485 |         1.1877 |      0.744  |         16 |      3.995  |
| LA MOLINA – SANTIAGO DE SURCO | 0.1805 |         1.1731 |      0.7221 |         27 |      8.7261 |
| LIMA – SAN MARTIN DE PORRES   | 0.1466 |         1.1727 |      0.624  |         11 |      4.6735 |
| LIMA – LINCE                  | 0.1457 |         1.1655 |      0.7321 |         14 |      1.0089 |

## Prueba de fidelidad (complementaria)

En cada una de las 20 corridas del GE se quitó el 10 % de las aristas con más atención en esa corrida y, aparte, el mismo número de aristas al azar (10 sorteos, promedio). Sin reentrenar. Si la atención señala aristas útiles, quitar las de más atención debería subir más el MAE.

|   ventana |   MAE_base |   dMAE_top |   dMAE_azar |
|----------:|-----------:|-----------:|------------:|
|         1 |     37.229 |     -0.005 |       0.004 |
|         2 |     38.638 |      0.002 |       0.009 |
|         3 |     27.25  |     -0.011 |      -0.006 |
|         4 |     25.413 |      0.002 |      -0.001 |

Promedio de las 20 corridas: ΔMAE top -0.003; ΔMAE azar 0.001. Corridas donde quitar las de más atención dañó más que el azar: 10 de 20. Wilcoxon pareado: p = 0.7841.
