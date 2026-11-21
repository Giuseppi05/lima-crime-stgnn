# Evaluación: interpretabilidad mediante los pesos de atención (OE3)

Generado por `python -m src.atencion`. Pesos de la prueba de las 4 ventanas × 5 semillas. En el GAT, la atención de cada distrito destino suma 1 entre sus vecinos y él mismo. Se interpretan como indicio, no como causa. Nota. Elaboración propia.

## Atención temporal por desfase

Media sobre distritos, meses de prueba y semillas, por separado según los meses de entrada (L) que eligió la validación en cada ventana. Una atención uniforme valdría 1/L (0,167 con L = 6; 0,083 con L = 12).

|   desfase |   GE (L=6) |   GE (L=12) |   GC2 (L=6) |   GC2 (L=12) |   GC1 (L=6) |   GC1 (L=12) |
|----------:|-----------:|------------:|------------:|-------------:|------------:|-------------:|
|         1 |     0.1579 |      0.0879 |      0.1579 |       0.0879 |      0.4577 |       0.084  |
|         2 |     0.16   |      0.0861 |      0.16   |       0.0862 |      0.1801 |       0.0836 |
|         3 |     0.1629 |      0.0845 |      0.1629 |       0.0846 |      0.1018 |       0.0833 |
|         4 |     0.1672 |      0.0833 |      0.1672 |       0.0834 |      0.0781 |       0.0829 |
|         5 |     0.1722 |      0.0822 |      0.1722 |       0.0823 |      0.0796 |       0.0828 |
|         6 |     0.1798 |      0.0812 |      0.1797 |       0.0812 |      0.1026 |       0.0826 |
|         7 |   nan      |      0.0803 |    nan      |       0.0803 |    nan      |       0.0825 |
|         8 |   nan      |      0.0798 |    nan      |       0.0798 |    nan      |       0.0825 |
|         9 |   nan      |      0.0799 |    nan      |       0.08   |    nan      |       0.0828 |
|        10 |   nan      |      0.0809 |    nan      |       0.0809 |    nan      |       0.0832 |
|        11 |   nan      |      0.0835 |    nan      |       0.0834 |    nan      |       0.084  |
|        12 |   nan      |      0.0904 |    nan      |       0.0901 |    nan      |       0.0856 |

Figura: `results/figuras/atencion_temporal.png`

## Atención espacial frente a la conectividad vial y la contigüidad

Autoatención media (peso del propio distrito): GE 0.222; GC₂ 0.209.

Correlación de Spearman por arista. En el GE (89 aristas) 89 son contiguas, así que la contigüidad binaria es constante y la contigüidad se mide además como longitud del límite compartido (km). En el GC₂ (98 aristas) 9 pares contiguos no tienen tramo vial que cruce (peso vial 0). `peso_x_grado` multiplica la atención por el número medio de entradas del par (vecinos + 1) para quitar el efecto de la normalización por nodo.

| modelo   | atencion     | contra    |      rho |        p |   n_aristas | nota      |
|:---------|:-------------|:----------|---------:|---------:|------------:|:----------|
| GE       | peso         | peso_vial |  -0.1409 |   0.1877 |          89 |           |
| GE       | peso         | n_tramos  |   0.1243 |   0.2457 |          89 |           |
| GE       | peso         | limite_km |   0.403  |   0.0001 |          89 |           |
| GE       | peso         | contiguo  | nan      | nan      |          89 | constante |
| GE       | peso_x_grado | peso_vial |   0.1593 |   0.136  |          89 |           |
| GE       | peso_x_grado | n_tramos  |   0.1184 |   0.2693 |          89 |           |
| GE       | peso_x_grado | limite_km |  -0.0214 |   0.842  |          89 |           |
| GE       | peso_x_grado | contiguo  | nan      | nan      |          89 | constante |
| GC2      | peso         | peso_vial |   0.0436 |   0.6699 |          98 |           |
| GC2      | peso         | n_tramos  |   0.1338 |   0.1892 |          98 |           |
| GC2      | peso         | limite_km |   0.2212 |   0.0286 |          98 |           |
| GC2      | peso_x_grado | peso_vial |   0.02   |   0.845  |          98 |           |
| GC2      | peso_x_grado | n_tramos  |   0.0285 |   0.7803 |          98 |           |
| GC2      | peso_x_grado | limite_km |  -0.0192 |   0.8514 |          98 |           |

### Top 10 de pares por atención (GE)

| par                               |   peso |   peso_x_grado |   peso_vial |   n_tramos |   limite_km |
|:----------------------------------|-------:|---------------:|------------:|-----------:|------------:|
| PUCUSANA – SANTA MARIA DEL MAR    | 0.4133 |         1.0333 |      0.4063 |          2 |      4.5018 |
| ANCON – SANTA ROSA                | 0.3743 |         1.123  |      0.6908 |         37 |      8.5514 |
| SAN BARTOLO – SANTA MARIA DEL MAR | 0.3336 |         1.0009 |      0.6075 |         16 |      4.353  |
| PUNTA NEGRA – SAN BARTOLO         | 0.3325 |         0.9975 |      0.4917 |         15 |     14.2266 |
| PUNTA HERMOSA – PUNTA NEGRA       | 0.3303 |         0.991  |      0.3115 |          7 |     26.2118 |
| LURIN – PUNTA HERMOSA             | 0.2705 |         1.0819 |      0.6971 |         34 |     27.9633 |
| CHACLACAYO – CIENEGUILLA          | 0.2525 |         1.0099 |      0.2434 |          1 |      7.6583 |
| ANCON – CARABAYLLO                | 0.249  |         0.996  |      0.1486 |          3 |     10.6362 |
| EL AGUSTINO – SANTA ANITA         | 0.2346 |         1.1728 |      0.7523 |         16 |      8.4462 |
| BARRANCO – MIRAFLORES             | 0.2295 |         1.0327 |      0.8004 |         23 |      1.8819 |

### Top 10 de pares por atención corregida por grado (GE)

| par                           |   peso |   peso_x_grado |   peso_vial |   n_tramos |   limite_km |
|:------------------------------|-------:|---------------:|------------:|-----------:|------------:|
| ATE – SANTA ANITA             | 0.2185 |         1.4205 |      0.7689 |         43 |      7.6326 |
| LIMA – BREÑA                  | 0.1724 |         1.2933 |      0.8531 |         39 |      5.3652 |
| LIMA – SAN MIGUEL             | 0.1722 |         1.2913 |      0.6643 |         12 |      1.9542 |
| ATE – LA MOLINA               | 0.1769 |         1.2381 |      0.6969 |         31 |     11.7941 |
| ATE – CHACLACAYO              | 0.1752 |         1.2264 |      0.421  |          3 |      8.5835 |
| ATE – CIENEGUILLA             | 0.1746 |         1.2224 |      0.4576 |         13 |     13.4739 |
| LIMA – RIMAC                  | 0.1466 |         1.1731 |      0.744  |         16 |      3.995  |
| EL AGUSTINO – SANTA ANITA     | 0.2346 |         1.1728 |      0.7523 |         16 |      8.4462 |
| LA MOLINA – SANTIAGO DE SURCO | 0.18   |         1.1698 |      0.7221 |         27 |      8.7261 |
| LIMA – SAN MARTIN DE PORRES   | 0.1456 |         1.165  |      0.624  |         11 |      4.6735 |

## Prueba de fidelidad (complementaria)

En cada una de las 20 corridas del GE se quitó el 10 % de las aristas con más atención en esa corrida y, aparte, el mismo número de aristas al azar (10 sorteos, promedio). Sin reentrenar. Si la atención señala aristas útiles, quitar las de más atención debería subir más el MAE.

|   ventana |   MAE_base |   dMAE_top |   dMAE_azar |
|----------:|-----------:|-----------:|------------:|
|         1 |     37.11  |     -0.01  |       0.006 |
|         2 |     38.75  |      0     |       0.007 |
|         3 |     27.245 |      0.005 |      -0.008 |
|         4 |     25.611 |     -0.072 |      -0.003 |

Promedio de las 20 corridas: ΔMAE top -0.019; ΔMAE azar 0.001. Corridas donde quitar las de más atención dañó más que el azar: 10 de 20. Wilcoxon pareado: p = 0.2611.
