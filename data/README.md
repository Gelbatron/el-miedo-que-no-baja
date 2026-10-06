# Datos

## `crudos/`
Copias de las fuentes oficiales tal como se descargan (`src/fuentes.py`). `registro_descargas.csv` guarda la url, la fecha, el tamaño y el sha1 de cada descarga. Si borras esta carpeta, el pipeline vuelve a bajar todo desde los servicios oficiales.

| Archivo | Fuente |
|---|---|
| `scj_delitos_alto_impacto_localidad.csv` | SCJ, capa «Delitos Alto Impacto Localidad» (ArcGIS REST) |
| `scj_incidentes_123_localidad.csv`, `scj_incidentes_123_upz.geojson` | SCJ, incidentes reportados a la Línea 123 |
| `sdp_poblacion_localidad_2005_2035.ods`, `sdp_poblacion_upz_2005_2035.ods` | SDP, proyecciones de población |
| `ebcc_2025_cultura_ciudadana.xlsx` | SCRD, Encuesta Bienal de Cultura Ciudadana 2025 (microdatos y diccionario en el mismo archivo) |
| `emv_ola8_2024.xlsx` | Encuesta Mundial de Valores ola 8, Datos para la Transparencia |
| `emv_localidad_por_registro.csv` | Localidad de cada registro de la EMV, recuperada del tablero oficial de Datos para la Transparencia (cruce por número de registro) |
| `uaesp_alumbrado_2019_08.csv` | UAESP, alumbrado por localidad (último corte publicado) |
| `dadep_ep_efectivo_localidad.csv` | DADEP, espacio público efectivo por localidad |
| `ideca_localidades.geojson` | IDECA, límites de localidades |

## `procesados/`
Salidas limpias e integradas que produce `src/pipeline.py`: panel por localidad, series en formato largo, microdatos analíticos de la Bienal y la EMV, e incidentes 123 por UPZ con tasas.
