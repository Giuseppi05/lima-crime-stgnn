# Fuentes externas

## Límites distritales (INEI)
- **Fuente:** Instituto Nacional de Estadística e Informática (INEI), Infraestructura de Datos Espaciales, geoportal https://ide.inei.gob.pe/, capa "Distrital (Actualizado al 2023)".
- **Archivo:** https://ide.inei.gob.pe/files/Distrito.rar (13 053 124 bytes; `Last-Modified` del servidor: 06/03/2026). Contiene `DISTRITO.gpkg` (EPSG:4326, 1 890 distritos; campos `ubigeo`, `nombdist`, `nombdep`, `nombprov`, `fuente`).
- **SHA-256 de Distrito.rar:** ae22428029000d801b3d68afd0914ba94ca40a789a9b56231f6131a75abb9654
- **Fecha de descarga:** 2026-11-20 (descarga automática con `curl`).
- **Licencia:** la página del geoportal no declara una licencia explícita. Indica que ofrece "utilizar de manera gratuita" la información y advierte que las capas pueden contener diferencias o inconsistencias. Se cita al INEI como fuente. Si se publica el repositorio, el archivo no se redistribuye: se descarga con el enlace anterior.
- **Ubicación local:** `data/external/inei_distrito_2023/DISTRITO.gpkg`.

## Red vial (OpenStreetMap)
- **Fuente:** OpenStreetMap, descargado con OSMnx (`network_type="drive"`) sobre la unión de los 43 polígonos con un margen de 1 km.
- **Licencia:** Open Database License (ODbL) 1.0, © colaboradores de OpenStreetMap.
- **Archivo y fecha:** `data/external/osm_lima_drive_<fecha de descarga>.graphml` (la fecha va en el nombre).
