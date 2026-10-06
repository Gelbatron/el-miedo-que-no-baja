# Auditoría del Portal de Datos Abiertos de Bogotá

Scripts que respaldan las cifras de la nota técnica (catálogo completo, 5 de octubre de 2026).

| Script | Qué hace |
|---|---|
| `01_catalogo.py` | Baja por la API CKAN los metadatos de todos los conjuntos (1.835) y recursos (11.707) |
| `02_almacenar.py` | Descarga los recursos tabulares (≤ 150 MB) y los carga a DuckDB con manifiesto (url, sha1, filas, error) |
| `03_capas.py` | Atributos de los conjuntos que solo existen como capa ArcGIS REST |
| `04_perfil.py` | Detecta en cada tabla la llave territorial (localidad, UPZ, UPL, coordenadas), el rango de años y la variable de sexo |

Resultado: `inventario_tablas.csv` (4.598 tablas). De ellas, 310 (6,7 %) traen una llave de localidad que se puede cruzar, 23 UPZ, 14 UPL y 64 coordenadas. El 23,9 % trae año o fecha y el 3,4 % trae sexo.

El almacén completo (≈ 2 GB en DuckDB) no se versiona; se reconstruye con los scripts en orden (variable `DATOS_BOGOTA_STORE` para la ruta).
