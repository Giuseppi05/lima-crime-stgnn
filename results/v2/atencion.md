# Evaluación: interpretabilidad mediante los pesos de atención (OE3)

Generado por `python -m src.atencion`. Pesos de la prueba de las 4 ventanas × 5 semillas. En el GAT, la atención de cada distrito destino suma 1 entre sus vecinos y él mismo. Se interpretan como indicio, no como causa. Nota. Elaboración propia.

## Atención temporal por desfase

Media sobre distritos, meses de prueba y semillas, por separado según los meses de entrada (L) que eligió la validación en cada ventana. Una atención uniforme valdría 1/L (0,167 con L = 6; 0,083 con L = 12).

|   desfase |   GE (L=6) |   GE (L=12) |   GC2 (L=6) |   GC2 (L=12) |   GC1 (L=6) |   GC1 (L=12) |
|----------:|-----------:|------------:|------------:|-------------:|------------:|-------------:|
|         1 |     0.3011 |      0.0833 |      0.266  |       0.0833 |      0.1649 |       0.0901 |
|         2 |     0.161  |      0.0833 |      0.1579 |       0.0833 |      0.1657 |       0.0849 |
|         3 |     0.1314 |      0.0833 |      0.1376 |       0.0833 |      0.1665 |       0.0833 |
|         4 |     0.1273 |      0.0833 |      0.1345 |       0.0833 |      0.1672 |       0.0827 |
|         5 |     0.1315 |      0.0833 |      0.14   |       0.0833 |      0.1676 |       0.0821 |
|         6 |     0.1477 |      0.0832 |      0.1641 |       0.0832 |      0.1681 |       0.0821 |
|         7 |   nan      |      0.0832 |    nan      |       0.0832 |    nan      |       0.0822 |
|         8 |   nan      |      0.0832 |    nan      |       0.0832 |    nan      |       0.082  |
|         9 |   nan      |      0.0832 |    nan      |       0.0832 |    nan      |       0.0821 |
|        10 |   nan      |      0.0833 |    nan      |       0.0833 |    nan      |       0.0818 |
|        11 |   nan      |      0.0835 |    nan      |       0.0835 |    nan      |       0.0855 |
|        12 |   nan      |      0.084  |    nan      |       0.0839 |    nan      |       0.0811 |

Figura: `results/figuras/atencion_temporal.png`

## Atención espacial frente a la conectividad vial y la contigüidad

Autoatención media (peso del propio distrito): GE 0.224; GC₂ 0.210.

Correlación de Spearman por arista. En el GE (89 aristas) 89 son contiguas, así que la contigüidad binaria es constante y la contigüidad se mide además como longitud del límite compartido (km). En el GC₂ (98 aristas) 9 pares contiguos no tienen tramo vial que cruce (peso vial 0). `peso_x_grado` multiplica la atención por el número medio de entradas del par (vecinos + 1) para quitar el efecto de la normalización por nodo.

| modelo   | atencion     | contra    |      rho |        p |   n_aristas | nota      |
|:---------|:-------------|:----------|---------:|---------:|------------:|:----------|
| GE       | peso         | peso_vial |  -0.1369 |   0.2009 |          89 |           |
| GE       | peso         | n_tramos  |   0.1257 |   0.2405 |          89 |           |
| GE       | peso         | limite_km |   0.4047 |   0.0001 |          89 |           |
| GE       | peso         | contiguo  | nan      | nan      |          89 | constante |
| GE       | peso_x_grado | peso_vial |   0.1625 |   0.1281 |          89 |           |
| GE       | peso_x_grado | n_tramos  |   0.1035 |   0.3346 |          89 |           |
| GE       | peso_x_grado | limite_km |  -0.03   |   0.7801 |          89 |           |
| GE       | peso_x_grado | contiguo  | nan      | nan      |          89 | constante |
| GC2      | peso         | peso_vial |   0.0436 |   0.6702 |          98 |           |
| GC2      | peso         | n_tramos  |   0.1266 |   0.214  |          98 |           |
| GC2      | peso         | limite_km |   0.2138 |   0.0346 |          98 |           |
| GC2      | peso_x_grado | peso_vial |  -0.0049 |   0.9617 |          98 |           |
| GC2      | peso_x_grado | n_tramos  |  -0.0162 |   0.8742 |          98 |           |
| GC2      | peso_x_grado | limite_km |  -0.0523 |   0.6087 |          98 |           |

### Top 10 de pares por atención (GE)

| par                               |   peso |   peso_x_grado |   peso_vial |   n_tramos |   limite_km |
|:----------------------------------|-------:|---------------:|------------:|-----------:|------------:|
| PUCUSANA – SANTA MARIA DEL MAR    | 0.4077 |         1.0193 |      0.4063 |          2 |      4.5018 |
| ANCON – SANTA ROSA                | 0.3738 |         1.1215 |      0.6908 |         37 |      8.5514 |
| PUNTA NEGRA – SAN BARTOLO         | 0.3306 |         0.9917 |      0.4917 |         15 |     14.2266 |
| SAN BARTOLO – SANTA MARIA DEL MAR | 0.3294 |         0.9883 |      0.6075 |         16 |      4.353  |
| PUNTA HERMOSA – PUNTA NEGRA       | 0.3289 |         0.9866 |      0.3115 |          7 |     26.2118 |
| LURIN – PUNTA HERMOSA             | 0.2714 |         1.0857 |      0.6971 |         34 |     27.9633 |
| CHACLACAYO – CIENEGUILLA          | 0.2541 |         1.0165 |      0.2434 |          1 |      7.6583 |
| ANCON – CARABAYLLO                | 0.2463 |         0.9853 |      0.1486 |          3 |     10.6362 |
| EL AGUSTINO – SANTA ANITA         | 0.2369 |         1.1846 |      0.7523 |         16 |      8.4462 |
| BARRANCO – MIRAFLORES             | 0.2317 |         1.0426 |      0.8004 |         23 |      1.8819 |

### Top 10 de pares por atención corregida por grado (GE)

| par                           |   peso |   peso_x_grado |   peso_vial |   n_tramos |   limite_km |
|:------------------------------|-------:|---------------:|------------:|-----------:|------------:|
| ATE – SANTA ANITA             | 0.216  |         1.4039 |      0.7689 |         43 |      7.6326 |
| LIMA – BREÑA                  | 0.1736 |         1.3024 |      0.8531 |         39 |      5.3652 |
| LIMA – SAN MIGUEL             | 0.1715 |         1.2866 |      0.6643 |         12 |      1.9542 |
| ATE – LA MOLINA               | 0.1762 |         1.2337 |      0.6969 |         31 |     11.7941 |
| ATE – CHACLACAYO              | 0.1759 |         1.2311 |      0.421  |          3 |      8.5835 |
| ATE – CIENEGUILLA             | 0.1726 |         1.2079 |      0.4576 |         13 |     13.4739 |
| EL AGUSTINO – SANTA ANITA     | 0.2369 |         1.1846 |      0.7523 |         16 |      8.4462 |
| LIMA – RIMAC                  | 0.1475 |         1.1797 |      0.744  |         16 |      3.995  |
| LIMA – SAN MARTIN DE PORRES   | 0.1465 |         1.1718 |      0.624  |         11 |      4.6735 |
| LA MOLINA – SANTIAGO DE SURCO | 0.1797 |         1.168  |      0.7221 |         27 |      8.7261 |

## Prueba de fidelidad (complementaria)

En cada una de las 20 corridas del GE se quitó el 10 % de las aristas con más atención en esa corrida y, aparte, el mismo número de aristas al azar (10 sorteos, promedio). Sin reentrenar. Si la atención señala aristas útiles, quitar las de más atención debería subir más el MAE.

|   ventana |   MAE_base |   dMAE_top |   dMAE_azar |
|----------:|-----------:|-----------:|------------:|
|         1 |     37.229 |     -0.005 |       0.004 |
|         2 |     38.681 |      0.001 |       0.009 |
|         3 |     32.343 |     -0.113 |       0.042 |
|         4 |     25.593 |     -0.069 |      -0.005 |

Promedio de las 20 corridas: ΔMAE top -0.047; ΔMAE azar 0.013. Corridas donde quitar las de más atención dañó más que el azar: 5 de 20. Wilcoxon pareado: p = 0.0172.
