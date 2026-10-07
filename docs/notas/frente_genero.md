# Frente de género, noche y conectividad

Script: `src/fuentes_genero.py` (corre con `python src/fuentes_genero.py`; las cifras de esta nota salen de su salida y de las tablas que escribe; las tablas de esta nota se generaron desde esos CSV, no a mano).
Tablas: `data/procesados/genero_violencia_localidad_anio.csv`, `genero_violencia_perfil.csv`, `genero_violencia_crecimiento.csv`, `seguridad_nocturna_localidad.csv`, `acoso_callejero_bogota.csv`, `conectividad_localidad.csv`, `confiabilidad_genero.csv`, `genero_pruebas_spearman.csv`.
Corte de la consulta: 6 de octubre de 2026. Semilla de los remuestreos: 20261006.

## Respuesta corta

1. **La violencia contra mujeres que registra el sector salud subió, pero una parte grande del aumento es registro.** SIVIM: 591,7 casos por 100.000 mujeres en 2019, 738,1 en 2022 y 845,7 en 2025 (34.979 casos). Frente a 2019 el cambio es +42,9 % (IC 95 %: +24,4 a +64,3); frente a 2022 es +14,6 % (−0,4 a +31,8), que no se distingue de cero. El 64,8 % del aumento de casos en mujeres entre 2019 y 2025 está en niñas de 6 a 17 años, y la violencia sexual contra mujeres notificada en establecimientos educativos pasó de 411 a 2.835 casos. Las denuncias de violencia intrafamiliar ante la Policía (SCJ, enero-agosto) crecieron 27,1 % en el mismo lapso, contra 59,7 % de los casos SIVIM (ambos sexos).
2. **Las adultas también.** La tasa en mujeres de 18 años o más pasó de 337,4 a 473,1 por 100.000 (+40,2 %). La violencia de pareja o expareja pasó de 5.298 a 10.525 casos y hoy es el 30,1 % de los casos en mujeres (22,6 % en 2019).
3. **Picos por localidad, ninguno significativo por sí solo.** Los mayores crecimientos 2019-2025 están en localidades que partían de tasas bajas: Suba +119,9 % (2.086 → 4.742 casos), Barrios Unidos +107,6 % (239 → 502), Usaquén +96,3 % (782 → 1.593) y Engativá +93,1 % (1.586 → 3.160), frente a +42,9 % de Bogotá. Las de tasa alta del centro y el sur bajaron: Los Mártires −15,1 %, San Cristóbal −11,7 %, Rafael Uribe Uribe −6,4 %. Ninguna diferencia frente al resto de la ciudad sobrevive Benjamini-Hochberg: la más fuerte es Suba, razón 1,62 (1,00 a 2,64), p = 0,050, q = 0,32. En nivel, Ciudad Bolívar (1.247,5) y Usme (1.245,6) siguen con las tasas más altas; Chapinero (497,8) y Usaquén (517,1), con las más bajas.
4. **Las más vulnerables son las niñas y las mujeres jóvenes.** Por 100.000 personas de su grupo en 2025: niñas de 14 a 17 años 3.150,9 (2,3 veces la de los varones de esa edad) y de 6 a 13 años 2.721,1; mujeres de 18 a 26 años 948,0, 6,6 veces la de los hombres de esa edad (142,8); de 27 a 44 años 534,4, 6,7 veces (79,7).
5. **La casa, no la calle.** En 2025 el 79,3 % de los casos en mujeres ocurrió en la vivienda, el 8,9 % en establecimientos educativos y el 4,5 % en vía pública (1.571 casos). En violencia sexual: vivienda 55,5 %, establecimiento educativo 21,7 %, vía pública 6,3 % (819 casos).
6. **Noche (Secretaría de la Mujer, medición 2019).** Peor iluminación: Usme (86,3 de 100; el 5,2 % de sus puntos con poca o ninguna luz, frente a 1,1 % en Bogotá), Tunjuelito (90,6) y Bosa (91,0). Peor estado de sendero: Usme (84,6; 14,2 % de puntos con sendero pobre o inexistente, frente a 2,6 %), Ciudad Bolívar (93,4) y San Cristóbal (93,7). Con cautela: la medición tiene efecto techo (86,5 % de los puntos con luz «brillante», contra 11,8 % en 2016) y el orden de localidades por iluminación no se repite entre 2016 y 2019 (Spearman −0,19). Usme es la única que está entre las tres peores en sendero en las dos mediciones.
7. **Acoso callejero (Veeduría 2025, muestra no representativa).** De las mujeres que respondieron (n = 2.742), el 51,8 % dice haber sido acosada en el último año; entre las de 18 a 29, el 66,4 % (n = 889). En hombres, 16,1 % (n = 877). El 86,3 % de las mujeres califica las calles oscuras como muy inseguras y el 77,8 % busca siempre lugares alumbrados. Solo el 8,4 % de quienes vivieron acoso denunció.
8. **Pruebas: nada sobrevive, y eso también es un resultado.** Entre las 19 localidades, la tasa de violencia contra mujeres 2025 no se asocia con iluminación (ρ = +0,02; IC −0,49 a +0,52), estado de sendero (ρ = −0,29; −0,72 a +0,25) ni puntos de wifi por habitante (ρ = −0,28; −0,64 a +0,29). El menor p ajustado es 0,38. Con n = 19, una prueba al 5 % solo tiene 80 % de potencia para |ρ| ≥ 0,60 (aproximación de Fisher): «no hay evidencia» no es «no hay relación».

## 1. Fuentes

Todo se baja por script desde la URL oficial (la del inventario cuando existe), con caché en `data/crudos/` y registro en `data/crudos/registro_descargas.csv` (URL, fecha, bytes, sha1). No hizo falta usar el almacén DuckDB para ninguna tabla: solo sirvió para explorar.

| Fuente | Recurso | Archivo en `data/crudos/` | URL |
|---|---|---|---|
| SDS, SIVIM: Violencia intrafamiliar y de género en Bogotá D.C. | CSV, 492.837 casos 2013-2026 | `sds_sivim_violencia_2013_2026.csv` (110,6 MB) | https://datosabiertos.bogota.gov.co/dataset/a1e1ef90-10c0-436f-a290-d1f7c1cf2242/resource/bbe9e920-c564-40f2-a307-5ae1ff087168/download/osb_saludmental-vintrafamiliar.csv |
| SDS, metadato del mismo conjunto | XLSX (en el DuckDB quedó como texto binario ilegible) | `sds_sivim_metadato.xlsx` | https://datosabiertos.bogota.gov.co/dataset/a1e1ef90-10c0-436f-a290-d1f7c1cf2242/resource/c5235ec1-4b0b-4282-bdca-02658e8d1e6a/download/metadato-osb_v-intrafamiliar.xlsx |
| SDMujer, Evaluación de seguridad nocturna para las mujeres 2019 | GeoPackage «Versión 09.19»: 44.335 puntos de 2019 + 20.660 de 2015-2016 | `sdmujer_seguridad_nocturna_puntos_v0919.gpkg` | https://datosabiertos.bogota.gov.co/dataset/f714e477-8e2a-44a2-87c0-17b491a01bcc/resource/486903b6-42da-4b36-9bfd-6e17bd0b7c6e/download/puntosseguridadnocturna.gpkg |
| SDMujer, mismo conjunto | CSV «Versión 09.16»: índice por localidad (17.708 puntos de 2015) | `sdmujer_seguridad_nocturna_indice_v0916.csv` | https://datosabiertos.bogota.gov.co/dataset/f714e477-8e2a-44a2-87c0-17b491a01bcc/resource/ab81ce58-7f7f-4d47-80db-3a80d69a69ec/download/indice-seguridad-por-localidad.csv |
| SDMujer, mismo conjunto | CSV «Versión 09.16»: 19.970 puntos (solo trazabilidad; no entra en tablas) | `sdmujer_seguridad_nocturna_puntos_v0916.csv` | https://datosabiertos.bogota.gov.co/dataset/f714e477-8e2a-44a2-87c0-17b491a01bcc/resource/0328d2ae-75b9-4b0f-94cb-33402769afb7/download/puntos-evaluacion-seguridad-nocturna.csv |
| Veeduría Distrital, Encuesta de Acoso Callejero 2025 | CSV, 4.120 respuestas × 260 columnas | `veeduria_acoso_callejero_2025.csv` | https://datosabiertos.bogota.gov.co/dataset/307da72b-f2a4-4e5c-bcbe-238a67844b71/resource/36041e75-2f97-436c-beb9-30587c5e2705/download/base_acososexualcallejero_2025.csv |
| Veeduría, Encuesta Acoso Callejero Mujeres | CSV, 3.102 respuestas (solo ficha) | `veeduria_acoso_callejero_mujeres_2024.csv` | https://datosabiertos.bogota.gov.co/dataset/2c9f67ff-37d8-48ca-9eab-33c577160084/resource/ca622e73-3175-4e21-8312-ed2a68f258e2/download/acosocallejero_mujer_eficiencia1.csv |
| Veeduría, Encuesta Acoso Callejero Hombres | CSV, 986 respuestas (solo ficha) | `veeduria_acoso_callejero_hombres_2024.csv` | https://datosabiertos.bogota.gov.co/dataset/ab896cc5-a215-455c-9176-4149d2772426/resource/dcfa96e3-196b-4735-be49-c0ce7a23beb5/download/acosocallejero_hombre-eficiencia1.csv |
| SDMujer, Línea base Ciudades Seguras Kennedy | CSV, 1.374 respuestas (solo ficha) | `sdmujer_acoso_kennedy_2019.csv` | https://datosabiertos.bogota.gov.co/dataset/6f254a00-ed63-4a86-8f85-87d3fa106bb6/resource/1240872d-453b-4560-8fce-01149ddd661b/download/base-de-datos-se1.csv |
| Secretaría General, Conectividad pública gratuita a internet | Servicio ArcGIS REST, 531 puntos | `sg_conectividad_publica_gratuita.geojson` | https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/serviciospublicos/conectividad/MapServer/0 |
| SDP, proyecciones de población 2005-2035 (ya en el repo) | grupos por localidad y edad simple por sexo | `data/procesados/sdp_poblacion_localidad_grupos.csv`, `sdp_poblacion_localidad_2005_2035.ods` | https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035 |
| IDECA, localidades; SCJ, UPZ (ya en el repo) | áreas total y urbana | `ideca_localidades.geojson`, `scj_incidentes_123_upz.geojson` | https://datosabiertos.bogota.gov.co/dataset/localidad-bogota-d-c |
| SCJ, delitos de alto impacto (ya en el repo) | violencia intrafamiliar enero-agosto, para triangular | `data/procesados/scj_delitos_localidad_largo.csv` | https://oaiee.scj.gov.co/agc/rest/services/Tematicos_Pub/CifrasSCJ/MapServer/0 |

Por qué el GeoPackage y no el CSV que lista el inventario: el conjunto se titula «2019», pero sus CSV («Versión 09.16») son la medición de 2015-2016 y son idénticos, celda por celda, a los del conjunto «Año 2016». La medición de 2019 solo está en el servicio REST (`mujeres/seguridad/MapServer/1`, que hoy responde error 400 a cualquier consulta), en el GeoJSON (64.995 puntos sin un solo atributo) y en el GeoPackage, que sí trae las calificaciones, la fecha, el tipo de vía y el enlace a la foto de cada punto.

## 2. Limpieza

**SIVIM.** UTF-8 con BOM, separador `;`. Columnas a minúsculas. Localidad con `territorio.cod_localidad` sobre `NOMBRE_LOCALIDAD`: 491.323 casos en las 19 urbanas, 1.360 en Sumapaz y 154 sin localidad («Localidad Desconocida» o vacío); los dos últimos grupos solo entran en el total de Bogotá. Grupos de edad: «14 - 17 años» (1 caso) va a «De 14 - 17 años», «De 30 - 34 años» (2) a «De 27 - 44 años», y «De 80 - 99» con «De 100 - 105» se unen en «80 años o más» para cruzarlos con la población. Tipo de violencia = la columna de lugar de ese tipo distinta de «Sin dato» (regla del metadato). «Vía pública» = algún tipo de violencia del caso ocurrió en vía pública. La relación con el agresor se agrupa porque SIVIM partió categorías en 2022 (sección 3). Denominadores: población SDP del mismo sexo, localidad y año; para edad, la edad simple del `.ods` del repo, leída con `limpieza._poblacion`.

**Seguridad nocturna.** Localidad con `cod_localidad` sobre `LOCCODIGO`, que mezcla códigos («01») y nombres («Barrios Unidos»); los 44.335 puntos de 2019 caen en localidades urbanas. Medición según `Fecha`: 2019-09-10 (2019; las fotos son de abril y mayo de 2019 en el 99,95 % de los puntos), 2015-11-30 (17.708 puntos en vías: es la base del índice publicado de 2016) y 2016-02-29 (2.952 en ciclorrutas). Componentes = puntaje / (3 × puntos) × 100, con la escala 0-3 del dominio del servicio ArcGIS; la fórmula reproduce el índice publicado de 2016 con diferencias de 0,4 a 1,7 puntos en 17 localidades (3,0 en La Candelaria; Usme no cuadra, ver sección 3).

**Acoso 2025.** Codificación CP850 (DOS), separador `;`. Universo: aceptó el tratamiento de datos, es mayor de 18 y vive en Bogotá: 3.680 de 4.120. «Si» sin tilde (1 caso) se une con «Sí». Género: Femenino → Mujeres, Masculino → Hombres; No binario, Transmasculino y Transfemenino → Otras identidades (n = 35); «Prefiero no responder» solo entra en el total. Edad: «60 a 69 más» y «70 o más» → «60 o más». Celdas con n < 30 se omiten; los indicadores que se calculan solo entre quienes vivieron acoso (de noche, madrugada, denunció) se omiten si esa base es menor de 30.

**Conectividad.** Se usa el campo oficial `LOCALIDAD`. Coincide con el cruce espacial contra IDECA en el 97,2 % de los puntos; los 15 desacuerdos son puntos sobre avenidas limítrofes y estaciones de TransMilenio. La tabla trae también el conteo por cruce espacial. Área total = polígono IDECA; área urbana = intersección con las 113 UPZ (se excluyen las 4 UPR rurales); ambas en EPSG:3116.

## 3. Advertencias

### Cambios de registro en SIVIM (se ven en los datos)

- **2022, categorías nuevas de agresor.** «Amigo(a)» pasa de 0 casos en 2021 a 312 en 2022 y «Compañero(a) de trabajo» de 0 a 54, mientras «Conocido» cae de 2.841 (2022) a 1.555 (2023). Por eso el perfil trae la relación agrupada.
- **Notificación escolar desde 2022.** Agresor «Estudiantes» (todas las víctimas): 486 casos en 2019, 1.776 en 2022 y 4.398 en 2025. Violencia sexual en establecimiento educativo: mujeres 411 → 2.835 y hombres 210 → 2.315 entre 2019 y 2025. Es poco probable que una violencia se multiplique por 7 u 11 en seis años; lo verosímil es que empezaron a notificar más los colegios.
- **Gestación y primer año de vida.** La categoría «Mujer gestante» del campo relación con el agresor pasa de 2.333 casos en mujeres (2019) a 120 (2025), los casos de menores de un año (ambos sexos) de 3.296 a 972 y la negligencia contra mujeres cae 28,8 %. La caída de −71,5 % en la tasa de niñas menores de un año no se debe leer como mejora.
- **2018: lugares nuevos** (institución de salud, lugares con expendio de alcohol, virtual y otros). **2020: pandemia**, 17.294 casos en mujeres, −26 % frente a 2019. UPZ «Sin dato»: 13,3 % de los casos en 2018 y 2,6 % en 2025.

### Subregistro

SIVIM ve solo lo que llega al sector salud: no son personas (una víctima se puede notificar varias veces) ni denuncias. Entre 2019 y 2025 los casos SIVIM crecieron 59,7 % y las denuncias de violencia intrafamiliar a la Policía 27,1 % (SCJ, enero-agosto; el frente de victimización encontró que esta serie de la SCJ coincide con SIEDCO, razón 1,00 a 1,09). Las dos suben, pero no al mismo ritmo, y no hay cómo separar cuánto es violencia y cuánto es notificación.

### Años incompletos

2026 trae 25.660 casos, el 48,9 % de 2025, y el archivo no trae mes. Lo más probable es enero-junio (el metadato dice periodicidad semestral y el recurso se actualizó el 28 de julio de 2026), pero no es verificable. 2026 no tiene tasa en las tablas y no se compara con años completos. 2025 puede cambiar con notificaciones tardías; no hay cómo medirlo.

### Bases pequeñas y muestras

- La Candelaria tiene entre 86 y 128 casos de mujeres al año: su cambio 2019-2025 (−3,7 %) tiene un IC de −44,3 % a +66,4 %. Todas las localidades tienen al menos 86 casos de mujeres en cada año de corte (2019, 2022, 2025), así que ningún cambio porcentual por localidad sale de una base menor.
- En el perfil no se publica cambio porcentual si la base tiene menos de 20 casos.
- Acoso: hombres de 60 o más tienen 20 personas que vivieron acoso; esos indicadores están vacíos. «Otras identidades» tiene n = 35: léase como indicio.
- Seguridad nocturna: La Candelaria tiene 280 puntos y Antonio Nariño 612; el resto, más de 1.000.

### Errores de publicación de la Secretaría de la Mujer

- En el CSV del índice de 2016, «Total puntos transporte» da el porcentaje de sendero y «Total puntos estado de sendero» el de transporte (verificado en las 18 localidades sin Usme); los porcentajes sí están bien rotulados. Las columnas de distribución «alto» y «medio» también están cruzadas (la columna «alto» difiere del % medio recalculado en 0,2 puntos de mediana).
- La fila de Usme del índice 2016 no cuadra con sus propios totales: ¿qué veo? 42 publicado frente a 67 recalculado, ¿quién me ve? 24 frente a 36, sendero 47 frente a 73. Por eso los valores de 2016 se recalculan desde los puntos.
- Medición 2019: efecto techo (86,5 % de puntos con iluminación «brillante», 11,8 % en 2016) y Tunjuelito con sendero «bueno» en el 100 % de sus 1.089 puntos, que parece valor por defecto. El orden de las localidades no es estable entre mediciones: Spearman 2016-2019 de −0,19 en iluminación y 0,34 en sendero. En 2016, «¿qué veo?» vale «bastante visible» en el 98,5 % de los puntos: ese componente no discrimina.
- La auditoría de 2019 se hizo en recorridos nocturnos en vehículo por 16.145 km de malla vial y 537 km de ciclorrutas (metadato del conjunto), no a pie por las calles de barrio; y tiene siete años.

### Modelo de los intervalos

Los IC de los cambios suponen una binomial negativa NB2 con α = 0,0276, estimado en el panel de mujeres 19 × 2013-2025 con efectos fijos de localidad y año: una variación relativa entre años de ~17 % que no es azar de conteo. Se eligió NB2 y no quasi-Poisson porque el φ de cada localidad crece casi proporcional a su media (pendiente log-log 0,90; φ de Poisson global 39,1). Es conservador, porque α incluye los años de quiebre de registro. El IC de Bogotá solo incluye el ruido propio de cada localidad: el choque común de un año es justo lo que se quiere medir.

## 4. Hallazgos

### 4.1 Bogotá, casos y tasa por 100.000 personas del mismo sexo

| Año | Casos mujeres | Tasa mujeres | Casos hombres | Tasa hombres |
|---|---|---|---|---|
| 2013 | 20.163 | 535,9 | 9.930 | 286,5 |
| 2014 | 23.311 | 617,3 | 10.126 | 291,3 |
| 2015 | 25.042 | 661,0 | 10.416 | 298,9 |
| 2016 | 22.072 | 580,0 | 8.830 | 252,6 |
| 2017 | 20.280 | 530,1 | 8.671 | 246,9 |
| 2018 | 21.830 | 564,3 | 8.880 | 250,6 |
| 2019 | 23.429 | 591,7 | 9.448 | 260,0 |
| 2020 | 17.294 | 429,2 | 6.355 | 171,6 |
| 2021 | 22.199 | 544,6 | 8.141 | 217,3 |
| 2022 | 30.283 | 738,1 | 11.035 | 292,7 |
| 2023 | 32.155 | 780,3 | 13.724 | 362,4 |
| 2024 | 34.531 | 835,8 | 16.539 | 435,5 |
| 2025 | 34.979 | 845,7 | 17.514 | 460,6 |
| 2026 | 16.739 | – | 8.921 | – |

2026 es parcial (probable enero-junio) y no tiene tasa. La tasa en hombres creció más (+77,2 % entre 2019 y 2025), y ese crecimiento se concentra en niños de 6 a 17 años (+180,5 % y +187,9 %), los grupos donde más pesa la notificación escolar.

### 4.2 Crecimiento por localidad (mujeres, por 100.000 mujeres)

Ordenado por el cambio 2019-2025. «Frente al resto» es la razón entre el cambio de la tasa de la localidad y el de la suma de las otras 18; q es el p ajustado por Benjamini-Hochberg sobre las 19.

| Localidad | Casos 2019 → 2025 | Tasa 2019 | Tasa 2022 | Tasa 2025 | Rango 2025 | Cambio 2019-2025 [IC 95 %] | Cambio 2022-2025 [IC 95 %] | Frente al resto 2019-2025 [IC], q BH | Cambio tasa 18+ 2019-2025 |
|---|---|---|---|---|---|---|---|---|---|
| Suba | 2.086 → 4.742 | 330,7 | 561,8 | 727,2 | 12 | +119,9 % [+38,3; +249,7] | +29,4 % [-18,5; +105,6] | 1,62 [1,00; 2,64], q = 0,32 | +112,0 % |
| Barrios Unidos | 239 → 502 | 329,1 | 500,3 | 683,3 | 15 | +107,6 % [+27,7; +237,5] | +36,6 % [-15,5; +120,7] | 1,46 [0,88; 2,42], q = 0,36 | +97,4 % |
| Usaquén | 782 → 1.593 | 263,4 | 402,9 | 517,1 | 18 | +96,3 % [+22,9; +213,7] | +28,3 % [-19,5; +104,6] | 1,39 [0,85; 2,27], q = 0,36 | +102,8 % |
| Engativá | 1.586 → 3.160 | 374,8 | 619,8 | 723,7 | 13 | +93,1 % [+21,3; +207,3] | +16,8 % [-26,6; +85,6] | 1,39 [0,85; 2,26], q = 0,36 | +81,5 % |
| Teusaquillo | 302 → 533 | 363,4 | 473,8 | 624,3 | 16 | +71,8 % [+6,1; +178,2] | +31,8 % [-18,3; +112,6] | 1,21 [0,73; 1,99], q = 0,73 | +115,5 % |
| Fontibón | 721 → 1.245 | 362,4 | 539,9 | 600,9 | 17 | +65,8 % [+3,7; +165,3] | +11,3 % [-30,3; +77,7] | 1,17 [0,71; 1,91], q = 0,73 | +70,4 % |
| Puente Aranda | 667 → 1.095 | 526,9 | 583,2 | 851,0 | 10 | +61,5 % [+0,9; +158,6] | +45,9 % [-8,8; +133,5] | 1,13 [0,69; 1,85], q = 0,73 | +66,1 % |
| Kennedy | 3.027 → 4.987 | 567,1 | 743,6 | 888,3 | 7 | +56,6 % [-1,4; +148,9] | +19,4 % [-24,8; +89,7] | 1,11 [0,69; 1,81], q = 0,75 | +41,2 % |
| Chapinero | 272 → 430 | 319,4 | 444,8 | 497,8 | 19 | +55,9 % [-4,1; +153,2] | +11,9 % [-30,8; +81,0] | 1,09 [0,66; 1,81], q = 0,77 | +58,4 % |
| Usme | 1.723 → 2.569 | 900,7 | 1.075,4 | 1.245,6 | 2 | +38,3 % [-13,1; +120,1] | +15,8 % [-27,2; +84,3] | 0,97 [0,59; 1,57], q = 0,89 | +24,0 % |
| Ciudad Bolívar | 3.125 → 4.316 | 976,8 | 1.198,6 | 1.247,5 | 1 | +27,7 % [-19,6; +102,9] | +4,1 % [-34,5; +65,3] | 0,88 [0,54; 1,43], q = 0,73 | +9,7 % |
| Bosa | 3.117 → 4.171 | 848,9 | 917,3 | 1.050,2 | 4 | +23,7 % [-22,1; +96,6] | +14,5 % [-27,9; +81,9] | 0,85 [0,52; 1,38], q = 0,73 | -1,6 % |
| Tunjuelito | 645 → 795 | 719,3 | 798,2 | 869,8 | 8 | +20,9 % [-24,6; +93,9] | +9,0 % [-32,0; +74,6] | 0,84 [0,51; 1,38], q = 0,73 | +18,0 % |
| La Candelaria | 91 → 86 | 1.101,7 | 1.555,5 | 1.060,7 | 3 | -3,7 % [-44,3; +66,4] | -31,8 % [-60,1; +16,5] | 0,67 [0,38; 1,18], q = 0,36 | +2,9 % |
| Antonio Nariño | 307 → 296 | 731,0 | 758,2 | 697,8 | 14 | -4,5 % [-41,4; +55,5] | -8,0 % [-43,5; +49,8] | 0,67 [0,40; 1,10], q = 0,36 | +22,0 % |
| Santa Fe | 572 → 581 | 1.075,7 | 1.092,0 | 1.017,2 | 5 | -5,4 % [-41,2; +52,1] | -6,8 % [-42,0; +49,7] | 0,66 [0,40; 1,08], q = 0,36 | +16,8 % |
| Rafael Uribe Uribe | 1.702 → 1.634 | 902,8 | 869,2 | 845,3 | 11 | -6,4 % [-41,2; +49,2] | -2,7 % [-39,0; +54,9] | 0,64 [0,39; 1,04], q = 0,34 | +17,6 % |
| San Cristóbal | 1.957 → 1.774 | 966,8 | 906,9 | 853,5 | 9 | -11,7 % [-44,6; +40,6] | -5,9 % [-40,9; +49,9] | 0,60 [0,37; 0,97], q = 0,32 | +11,3 % |
| Los Mártires | 470 → 408 | 1.063,3 | 859,9 | 902,3 | 6 | -15,1 % [-47,5; +37,1] | +4,9 % [-35,1; +69,8] | 0,59 [0,36; 0,97], q = 0,32 | -10,0 % |
| Bogotá D.C. | 23.429 → 34.979 | 591,7 | 738,1 | 845,7 | – | +42,9 % [+24,4; +64,3] | +14,6 % [-0,4; +31,8] | – | +40,2 % |

Lectura:
- El crecimiento se concentra en el norte y el occidente, que partían de tasas bajas. Entre las 19 localidades, la tasa de 2019 y su cambio a 2025 tienen Spearman −0,84 (−0,90 en mujeres de 18+). Parte es regresión a la media y parte puede ser notificación desigual entre localidades; con estos datos no se separan.
- En Suba el aumento no es solo escolar: la tasa en mujeres de 18+ también creció 112,0 %.
- Bosa (−1,6 %) y Los Mártires (−10,0 %) son las únicas con caída en la tasa de adultas.
- Ninguna localidad se aparta del resto de forma significativa tras BH. Sin corregir, Suba (p = 0,050) crece más y San Cristóbal y Los Mártires (p = 0,038 cada una) crecen menos.

### 4.3 Quiénes son las víctimas

Tasa por 100.000 personas del mismo sexo y grupo de edad, Bogotá:

| Grupo de edad | Casos mujeres 2025 | Tasa mujeres 2019 | Tasa mujeres 2025 | Cambio 2019-2025 | Cambio 2022-2025 | Tasa hombres 2025 | Mujeres / hombres |
|---|---|---|---|---|---|---|---|
| Menor 1 año | 486 | 3.969,5 | 1.129,8 | -71,5 % | -14,6 % | 1.077,9 | 1,0 |
| De 1 - 5 años | 3.047 | 1.198,4 | 1.350,9 | +12,7 % | +18,6 % | 1.275,6 | 1,1 |
| De 6 - 13 años | 10.054 | 1.311,8 | 2.721,1 | +107,4 % | +26,3 % | 2.292,1 | 1,2 |
| De 14 - 17 años | 5.699 | 1.568,7 | 3.150,9 | +100,9 % | +2,4 % | 1.346,1 | 2,3 |
| De 18 - 26 años | 5.059 | 704,9 | 948,0 | +34,5 % | +12,1 % | 142,8 | 6,6 |
| De 27 - 44 años | 6.767 | 365,6 | 534,4 | +46,2 % | +29,5 % | 79,7 | 6,7 |
| De 45 - 59 años | 2.068 | 125,9 | 267,1 | +112,2 % | +37,9 % | 51,4 | 5,2 |
| De 60 - 69 años | 871 | 109,7 | 210,3 | +91,7 % | +24,8 % | 64,3 | 3,3 |
| De 70 - 79 años | 526 | 170,1 | 231,4 | +36,0 % | +3,8 % | 151,7 | 1,5 |
| De 80 años o más | 402 | 315,8 | 397,0 | +25,7 % | +5,2 % | 310,7 | 1,3 |

Mujeres según la relación con el agresor (porcentaje sobre los casos con dato):

| Relación con el agresor | Casos 2019 | Casos 2022 | Casos 2025 | % 2019 | % 2022 | % 2025 | Cambio 2019-2025 (pp) |
|---|---|---|---|---|---|---|---|
| Madre, padre o padrastros | 8.433 | 9.139 | 11.426 | 36,0 | 30,2 | 32,7 | -3,3 |
| Pareja o expareja | 5.298 | 7.878 | 10.525 | 22,6 | 26,0 | 30,1 | +7,5 |
| Otro familiar | 3.135 | 5.318 | 4.872 | 13,4 | 17,6 | 13,9 | +0,5 |
| Desconocido | 1.799 | 2.870 | 2.907 | 7,7 | 9,5 | 8,3 | +0,6 |
| Entorno escolar | 472 | 1.793 | 2.817 | 2,0 | 5,9 | 8,1 | +6,1 |
| Conocido, amigo, vecino o del trabajo | 1.942 | 2.990 | 2.293 | 8,3 | 9,9 | 6,6 | -1,7 |
| Mujer gestante (código de gestación) | 2.333 | 261 | 120 | 10,0 | 0,9 | 0,3 | -9,7 |
| Otro | 17 | 24 | 18 | 0,1 | 0,1 | 0,1 | +0,0 |

Tipo de violencia en los casos de mujeres (un caso puede tener varios tipos; la emocional está en todos):

| Tipo | Casos 2019 | Casos 2025 | % de casos 2019 | % de casos 2025 |
|---|---|---|---|---|
| Emocional | 23.429 | 34.979 | 100,0 | 100,0 |
| Física | 6.604 | 13.625 | 28,2 | 39,0 |
| Sexual | 6.934 | 13.039 | 29,6 | 37,3 |
| Negligencia | 10.143 | 7.218 | 43,3 | 20,6 |
| Económica | 623 | 1.734 | 2,7 | 5,0 |
| Abandono | 1.100 | 806 | 4,7 | 2,3 |

### 4.4 Lugar de ocurrencia, mujeres

Lugar del caso (columna de violencia emocional, que el metadato usa como total):

| Lugar | Casos 2019 | Casos 2025 | % 2019 | % 2022 | % 2025 |
|---|---|---|---|---|---|
| Vivienda | 21.137 | 27.743 | 90,2 | 83,4 | 79,3 |
| Establecimiento educativo | 523 | 3.097 | 2,2 | 6,1 | 8,9 |
| Vía Pública | 731 | 1.571 | 3,1 | 3,9 | 4,5 |
| Otro | 748 | 1.344 | 3,2 | 4,4 | 3,8 |
| Virtual | 10 | 406 | 0,0 | 0,6 | 1,2 |
| Lugar de trabajo | 45 | 201 | 0,2 | 0,3 | 0,6 |

Violencia sexual:

| Lugar | Casos 2019 | Casos 2025 | % 2019 | % 2022 | % 2025 |
|---|---|---|---|---|---|
| Vivienda | 5.239 | 7.241 | 75,6 | 69,2 | 55,5 |
| Establecimiento educativo | 411 | 2.835 | 5,9 | 12,1 | 21,7 |
| Otro | 657 | 1.226 | 9,5 | 8,9 | 9,4 |
| Vía Pública | 469 | 819 | 6,8 | 5,6 | 6,3 |
| Virtual | 11 | 378 | 0,2 | 1,3 | 2,9 |
| Lugares de esparcimiento con expendio de alcohol | 34 | 135 | 0,5 | 0,9 | 1,0 |

Violencia física:

| Lugar | Casos 2019 | Casos 2025 | % 2019 | % 2022 | % 2025 |
|---|---|---|---|---|---|
| Vivienda | 6.034 | 12.175 | 91,4 | 90,7 | 89,4 |
| Vía Pública | 299 | 783 | 4,5 | 4,8 | 5,7 |
| Otro | 129 | 237 | 2,0 | 2,2 | 1,7 |
| Establecimiento educativo | 68 | 199 | 1,0 | 1,1 | 1,5 |
| Lugares de esparcimiento con expendio de alcohol | 15 | 69 | 0,2 | 0,3 | 0,5 |
| Lugar de trabajo | 18 | 59 | 0,3 | 0,2 | 0,4 |

Si se cuenta cualquier tipo de violencia ocurrido en vía pública, en 2025 son 1.682 casos de mujeres: 40,7 por 100.000 mujeres.

### 4.5 Seguridad nocturna por localidad (Secretaría de la Mujer, 2019)

Componentes de 0 a 100; EE ingenuo entre paréntesis (subestima: los puntos de un mismo recorrido se parecen). Rango 1 = peor. Ordenado de peor a mejor iluminación. Las columnas de 2016 se recalcularon desde los puntos.

| Localidad | Puntos 2019 | Iluminación (EE) | % puntos con poca o ninguna luz | Rango peor iluminación | Sendero (EE) | % sendero pobre o ninguno | Rango peor sendero | % índice bajo o muy bajo | Iluminación 2016 | Sendero 2016 |
|---|---|---|---|---|---|---|---|---|---|---|
| Usme | 1.383 | 86,3 (0,6) | 5,2 | 1 | 84,6 (0,8) | 14,2 | 1 | 18,5 | 61,1 | 73,4 |
| Tunjuelito | 1.089 | 90,6 (0,5) | 2,4 | 2 | 100,0 (0,0) | 0,0 | 19 | 2,8 | 61,7 | 87,2 |
| Bosa | 2.379 | 91,0 (0,3) | 1,4 | 3 | 97,2 (0,2) | 1,3 | 8 | 3,0 | 50,2 | 89,2 |
| Chapinero | 2.245 | 92,7 (0,3) | 1,9 | 4 | 94,5 (0,4) | 4,1 | 5 | 11,1 | 64,8 | 87,4 |
| Teusaquillo | 2.374 | 92,7 (0,3) | 2,0 | 5 | 99,4 (0,2) | 0,6 | 17 | 4,1 | 68,8 | 87,7 |
| Fontibón | 2.596 | 93,7 (0,3) | 1,2 | 6 | 97,9 (0,2) | 1,6 | 9 | 7,4 | 58,0 | 86,8 |
| Usaquén | 4.019 | 94,7 (0,2) | 1,5 | 8 | 95,4 (0,3) | 4,4 | 7 | 6,8 | 65,1 | 87,7 |
| Ciudad Bolívar | 1.596 | 94,7 (0,3) | 0,2 | 7 | 93,4 (0,4) | 4,6 | 2 | 7,0 | 60,9 | 83,2 |
| San Cristóbal | 2.114 | 95,5 (0,3) | 0,4 | 9 | 93,7 (0,4) | 4,6 | 3 | 5,7 | 56,8 | 84,5 |
| Barrios Unidos | 2.092 | 95,8 (0,3) | 0,9 | 10 | 99,4 (0,2) | 0,6 | 16 | 2,5 | 69,0 | 82,1 |
| Suba | 4.893 | 96,2 (0,2) | 0,4 | 12 | 94,6 (0,3) | 5,6 | 6 | 9,4 | 62,5 | 81,4 |
| Santa Fe | 1.083 | 96,2 (0,3) | 0,6 | 11 | 94,5 (0,7) | 5,3 | 4 | 6,5 | 60,5 | 82,6 |
| Engativá | 5.193 | 96,9 (0,2) | 1,1 | 13 | 99,3 (0,1) | 0,2 | 15 | 5,1 | 61,2 | 85,2 |
| Los Mártires | 1.183 | 97,0 (0,3) | 0,6 | 14 | 99,2 (0,3) | 0,8 | 12 | 1,9 | 61,8 | 89,5 |
| Kennedy | 4.903 | 97,1 (0,1) | 0,6 | 15 | 99,1 (0,1) | 0,7 | 11 | 2,2 | 58,8 | 86,4 |
| Puente Aranda | 2.589 | 97,2 (0,2) | 0,5 | 16 | 98,8 (0,2) | 1,0 | 10 | 3,4 | 62,7 | 84,6 |
| La Candelaria | 280 | 97,5 (0,6) | 0,7 | 17 | 99,3 (0,5) | 0,7 | 14 | 3,2 | 59,5 | 72,0 |
| Antonio Nariño | 612 | 97,9 (0,4) | 0,5 | 18 | 99,4 (0,2) | 0,2 | 18 | 1,8 | 60,3 | 93,9 |
| Rafael Uribe Uribe | 1.712 | 98,3 (0,2) | 0,0 | 19 | 99,3 (0,2) | 0,4 | 13 | 1,5 | 53,7 | 84,1 |
| Bogotá D.C. | 44.335 | 95,1 (0,1) | 1,1 | – | 96,9 (0,1) | 2,6 | – | 5,7 | 61,2 | 85,3 |

En toda la ciudad los componentes de 2019 son: iluminación 95,1; sendero 96,9; ¿qué veo? 80,5; ¿quién me ve? 69,1; transporte 67,9; presencia de personas 25,9; presencia mixta 9,0; presencia de seguridad 4,8. Lo que sale mal en todas partes no es la luz ni el andén: son la falta de gente, de seguridad y de mezcla de hombres y mujeres en la calle de noche.

En 2016 el orden era otro. Peor iluminación: Bosa (50,2), Rafael Uribe Uribe (53,7) y San Cristóbal (56,8). Peor sendero: La Candelaria (72,0), Usme (73,4) y Suba (81,4).

### 4.6 Acoso callejero, Bogotá (Veeduría 2025)

Porcentajes sin ponderar sobre quienes respondieron (no hay factor de expansión). No es una estimación de Bogotá: es lo que dicen 3.680 personas que eligieron responder un formulario en línea, con 36 % de posgrados.

| Grupo | n | Acoso últimos 12 meses | Miedo al acoso (sí) | Calles oscuras muy inseguras | Siempre busca lugares alumbrados | n que vivió acoso | De noche (entre quienes lo vivieron) | Denunció |
|---|---|---|---|---|---|---|---|---|
| Todas las personas | 3.680 | 43,3 | 49,4 | 81,5 | 72,1 | 2.182 | 49,7 | 8,5 |
| Mujeres | 2.742 | 51,8 | 61,1 | 86,3 | 77,8 | 1.880 | 49,6 | 8,4 |
| Hombres | 877 | 16,1 | 12,2 | 66,6 | 54,0 | 254 | 49,6 | 7,9 |
| Otras identidades | 35 | 60,0 | 60,0 | 82,9 | 82,9 | 30 | 53,3 | 10,0 |
| Todas las personas, 18-29 | 1.110 | 58,7 | 66,8 | 83,1 | 76,2 | 853 | 53,7 | 7,5 |
| Todas las personas, 30-44 | 1.460 | 41,0 | 46,4 | 82,3 | 69,0 | 827 | 48,6 | 8,7 |
| Todas las personas, 45-59 | 891 | 33,2 | 38,5 | 79,8 | 71,8 | 424 | 45,0 | 9,2 |
| Todas las personas, 60 o más | 219 | 21,9 | 26,0 | 75,8 | 74,0 | 78 | 42,3 | 12,8 |
| Mujeres, 18-29 | 889 | 66,4 | 78,5 | 86,4 | 80,3 | 756 | 53,4 | 7,3 |
| Mujeres, 30-44 | 1.099 | 48,0 | 56,4 | 87,3 | 74,7 | 703 | 48,4 | 8,8 |
| Mujeres, 45-59 | 633 | 42,0 | 48,7 | 85,0 | 78,7 | 364 | 45,3 | 8,8 |
| Mujeres, 60 o más | 121 | 28,9 | 39,7 | 83,5 | 81,8 | 57 | 40,4 | 15,8 |
| Hombres, 18-29 | 187 | 23,5 | 11,2 | 67,4 | 56,1 | 68 | 60,3 | 7,4 |
| Hombres, 30-44 | 342 | 16,7 | 13,5 | 66,7 | 50,0 | 110 | 47,3 | 7,3 |
| Hombres, 45-59 | 251 | 11,2 | 12,4 | 66,1 | 54,2 | 56 | 42,9 | 10,7 |
| Hombres, 60 o más | 97 | 12,4 | 9,3 | 66,0 | 63,9 | 20 | – | – |

Por qué no hay tabla por localidad: la base trae la localidad de residencia, pero la muestra es de autoselección y el n va de 40 (La Candelaria) a 551 (Suba). Usaquén 313, Chapinero 127, Santa Fe 82, San Cristóbal 140, Usme 152, Tunjuelito 74, Bosa 305, Kennedy 400, Fontibón 223, Engativá 405, Suba 551, Barrios Unidos 91, Teusaquillo 190, Los Mártires 99, Antonio Nariño 51, Puente Aranda 146, La Candelaria 40, Rafael Uribe Uribe 109, Ciudad Bolívar 181. Un porcentaje por localidad mediría sobre todo quién llenó el formulario en cada una.

### 4.7 Conectividad pública gratuita

Población 2026 (el corte de los datos es octubre de 2026). Ordenado de menos a más puntos por habitante.

| Localidad | Puntos | Zonas wifi | CETIC | Por 100.000 hab. | Área total (km²) | Área urbana (km²) | Por km² total | Por km² urbano | Puntos por cruce espacial |
|---|---|---|---|---|---|---|---|---|---|
| Kennedy | 31 | 30 | 1 | 2,87 | 38,6 | 38,5 | 0,80 | 0,81 | 33 |
| Bosa | 25 | 23 | 2 | 3,24 | 23,9 | 23,9 | 1,04 | 1,05 | 25 |
| Usme | 14 | 14 | 0 | 3,45 | 214,9 | 30,2 | 0,07 | 0,46 | 14 |
| Suba | 61 | 56 | 5 | 4,90 | 100,5 | 62,6 | 0,61 | 0,97 | 59 |
| Ciudad Bolívar | 35 | 22 | 13 | 5,11 | 129,9 | 33,8 | 0,27 | 1,03 | 35 |
| Engativá | 50 | 48 | 2 | 6,06 | 35,9 | 35,8 | 1,40 | 1,40 | 52 |
| Usaquén | 35 | 35 | 0 | 6,14 | 65,2 | 38,1 | 0,54 | 0,92 | 36 |
| San Cristóbal | 28 | 27 | 1 | 6,99 | 49,1 | 16,4 | 0,57 | 1,70 | 26 |
| Fontibón | 29 | 29 | 0 | 7,43 | 33,2 | 33,1 | 0,87 | 0,88 | 27 |
| Rafael Uribe Uribe | 30 | 30 | 0 | 7,94 | 13,8 | 13,8 | 2,17 | 2,17 | 33 |
| Santa Fe | 11 | 10 | 1 | 9,69 | 45,1 | 6,9 | 0,24 | 1,59 | 12 |
| Puente Aranda | 27 | 25 | 2 | 10,76 | 17,3 | 17,2 | 1,56 | 1,56 | 25 |
| Chapinero | 19 | 19 | 0 | 11,71 | 38,0 | 13,0 | 0,50 | 1,46 | 18 |
| Tunjuelito | 25 | 24 | 1 | 14,15 | 9,9 | 9,9 | 2,52 | 2,53 | 23 |
| Los Mártires | 14 | 14 | 0 | 16,75 | 6,5 | 6,5 | 2,15 | 2,15 | 15 |
| Teusaquillo | 29 | 28 | 1 | 18,49 | 14,2 | 14,2 | 2,04 | 2,05 | 30 |
| Barrios Unidos | 28 | 27 | 1 | 20,13 | 11,9 | 11,9 | 2,35 | 2,36 | 29 |
| Antonio Nariño | 18 | 18 | 0 | 22,67 | 4,9 | 4,9 | 3,69 | 3,70 | 18 |
| La Candelaria | 7 | 4 | 3 | 42,00 | 2,1 | 2,0 | 3,40 | 3,41 | 6 |
| Bogotá D.C. (19 localidades urbanas) | 516 | 483 | 33 | 6,51 | 854,7 | 413,0 | 0,60 | 1,25 | 516 |

Kennedy, Bosa y Usme, que suman más de 2,2 millones de habitantes, tienen menos de 3,5 puntos por 100.000. Por km² urbano, Usme es la más baja (0,46). La densidad por km² total castiga a las localidades con mucho suelo rural (Usme 214,9 km² de los que 30,2 son urbanos).

## 5. Pruebas exploratorias

Spearman entre localidades (n = 19), IC 95 % bootstrap BCa con 10.000 remuestreos pareados, p por permutación (20.000), Benjamini-Hochberg dentro de cada bloque. El bloque pedido es «principal». «Sensibilidad» cambia la variable de violencia por la de vía pública, más cercana al mecanismo de la calle de noche. «Robustez» cambia la medición o la definición de la variable explicativa.

| Bloque | Y | X | ρ | IC 95 % (BCa) | p (permutación) | p ajustado (BH) | ¿Sobrevive BH al 5 %? |
|---|---|---|---|---|---|---|---|
| principal | Tasa de violencia contra mujeres 2025 (SIVIM, por 100.000 mujeres) | Iluminación (índice SDMujer 2019, 0-100) | +0,02 | [-0,49; +0,52] | 0,935 | 0,935 | no |
| principal | Tasa de violencia contra mujeres 2025 (SIVIM, por 100.000 mujeres) | Estado de sendero (índice SDMujer 2019, 0-100) | -0,29 | [-0,72; +0,25] | 0,223 | 0,378 | no |
| principal | Tasa de violencia contra mujeres 2025 (SIVIM, por 100.000 mujeres) | Puntos de conectividad pública gratuita por 100.000 hab. (2026) | -0,28 | [-0,64; +0,29] | 0,252 | 0,378 | no |
| sensibilidad | Tasa de casos en vía pública contra mujeres 2025 (por 100.000 mujeres) | Iluminación (índice SDMujer 2019, 0-100) | +0,29 | [-0,30; +0,68] | 0,218 | 0,327 | no |
| sensibilidad | Tasa de casos en vía pública contra mujeres 2025 (por 100.000 mujeres) | Estado de sendero (índice SDMujer 2019, 0-100) | -0,36 | [-0,74; +0,19] | 0,129 | 0,327 | no |
| sensibilidad | Tasa de casos en vía pública contra mujeres 2025 (por 100.000 mujeres) | Puntos de conectividad pública gratuita por 100.000 hab. (2026) | -0,18 | [-0,58; +0,32] | 0,458 | 0,458 | no |
| robustez | Tasa de violencia contra mujeres 2025 (SIVIM, por 100.000 mujeres) | Iluminación (medición 2016, recalculada desde puntos) | -0,45 | [-0,75; +0,04] | 0,052 | 0,195 | no |
| robustez | Tasa de violencia contra mujeres 2025 (SIVIM, por 100.000 mujeres) | Estado de sendero (medición 2016, recalculada desde puntos) | -0,39 | [-0,74; +0,14] | 0,097 | 0,195 | no |
| robustez | Tasa de violencia contra mujeres 2025 (SIVIM, por 100.000 mujeres) | Puntos de conectividad por 100.000 hab. (localidad por cruce espacial) | -0,27 | [-0,64; +0,30] | 0,270 | 0,270 | no |
| robustez | Tasa de violencia contra mujeres 2025 (SIVIM, por 100.000 mujeres) | Solo zonas wifi por 100.000 hab. (sin CETIC) | -0,30 | [-0,68; +0,29] | 0,217 | 0,270 | no |

Lectura:
- **Ninguna prueba sobrevive la corrección, ni en el bloque pedido ni en los otros dos.** Los IC son anchos: todos incluyen tanto asociaciones nulas como moderadas.
- **El resultado de iluminación depende de qué medición se use.** Con 2019 la asociación es nula (+0,02); con 2016 es negativa (−0,45, p sin ajustar 0,052): más luz, menos violencia. Como el orden de localidades no es estable entre las dos mediciones y 2019 tiene efecto techo, ninguna de las dos se puede presentar como evidencia.
- **El signo de la vía pública con iluminación es positivo (+0,29)**, lo contrario de lo esperable, y tampoco es significativo.
- Son correlaciones ecológicas entre 19 unidades grandes y heterogéneas: no dicen nada de personas ni de causas, y las variables de entorno se mueven juntas con el nivel socioeconómico, que no se controló.

## 6. Ficha de confiabilidad por fuente

También en `data/procesados/confiabilidad_genero.csv` (con la URL de cada fuente).

| Fuente | Entidad | Años | Periodicidad | Tipo | Tamaño | Nivel territorial más fino | Factor de expansión | Margen de error | Última actualización | Advertencia |
|---|---|---|---|---|---|---|---|---|---|---|
| SIVIM: violencia intrafamiliar y de género | Secretaría Distrital de Salud | 2013-2026 (2026 parcial) | Semestral según el metadato (el portal dice anual) | Registro administrativo (vigilancia en salud) | 492.837 casos notificados | UPZ de residencia de la víctima (2,6 % sin UPZ en 2025); en este frente se usa localidad | No aplica (registro) | No aplica; error no muestral por subregistro y cambios de notificación | 2026-07-28 | Cuenta casos notificados al sector salud, no personas ni denuncias. Categorías nuevas en 2018 (lugares) y 2022 (agresor amigo y compañero de trabajo) y auge de notificación escolar desde 2022: el crecimiento mezcla violencia y registro. |
| Seguridad nocturna para las mujeres 2019 | Secretaría Distrital de la Mujer (OMEG) | 2019 (fotos abr-may 2019) | Según necesidad (dos mediciones: 2015-2016 y 2019) | Auditoría en campo (app Safetipin, 6 a 11 p. m.) | 44.335 puntos | Punto georreferenciado en vía o ciclorruta | No aplica (no es muestra probabilística) | No publicado; error estándar ingenuo de los componentes por localidad ≤ 0,8 pts (subestima: puntos autocorrelacionados) | 2019-09-10 (dato); ficha del portal modificada 2025-03-15 | Tiene 7 años y solo cubre vías, arterias y ciclorrutas (no calles de barrio). Efecto techo: 86 % de los puntos con iluminación 'brillante' (12 % en 2016), así que discrimina poco entre localidades; el orden de localidades no se sostiene entre 2016 y 2019. Tunjuelito tiene sendero 'bueno' en el 100 % de sus puntos (posible valor por defecto). Es una auditoría del entorno, no la percepción de las mujeres. |
| Índice de seguridad nocturna por localidad 2016 (CSV 'Versión 09.16') | Secretaría Distrital de la Mujer (OMEG) | 2015-2016 | Según necesidad | Auditoría en campo (agregado por localidad) | 17.708 puntos (vías y arterias) | Localidad | No aplica | No publicado | Publicado 2024-05-07 (dato de nov-2015) | Errores de publicación: totales de transporte y sendero intercambiados, distribución alto/medio intercambiada, fila de Usme inconsistente. Usar solo recalculado desde los puntos. |
| Encuesta de acoso sexual callejero 2025 | Veeduría Distrital | 2025 (11-jun a 15-sep) | No planeada | Encuesta en línea autoadministrada (no probabilística) | 4.120 respuestas; 3.680 en el universo analítico (18+, vive en Bogotá) | Localidad de residencia autodeclarada (n de 40 a 551 por localidad) | No | No calculable (autoselección) | 2026-06-12 | Sesgo de autoselección (36 % con posgrado en el universo analítico). Sirve para describir a quienes respondieron, no para estimar prevalencias de Bogotá ni comparar localidades. |
| Encuesta de acoso callejero, mujeres | Veeduría Distrital | Publicada en 2024 (sin fecha de respuesta) | Anual según el portal (una sola base publicada) | Encuesta (diseño no documentado) | 3.102 mujeres de 14+ años | Localidad de residencia autodeclarada | No | No calculable | 2024-08-29 | Sin ficha técnica ni pesos; respuestas abiertas mezcladas en campos cerrados (calidad de captura baja). |
| Encuesta de acoso callejero, hombres | Veeduría Distrital | Publicada en 2024 (sin fecha de respuesta) | Anual según el portal (una sola base publicada) | Encuesta (diseño no documentado) | 986 hombres | Localidad de residencia autodeclarada | No | No calculable | 2024-08-28 | Mide percepción de los hombres sobre el acoso, no victimización. Sin pesos. |
| Línea base de acoso callejero, Ciudades Seguras Kennedy | Secretaría Distrital de la Mujer | 2019 | No planeada | Encuesta presencial con dispositivo (diseño no publicado) | 1.374 mujeres de 14+ años | UPZ (5 UPZ de Kennedy) | No | No calculable | 2019-12-13 | Solo Kennedy: no sirve para comparar localidades. |
| Conectividad pública gratuita a internet | Secretaría General de la Alcaldía Mayor | Corte 2026 | Según necesidad | Registro administrativo (inventario georreferenciado) | 531 puntos (488 zonas wifi y 43 centros CETIC) | Punto georreferenciado | No aplica | No aplica | 2026-10-01 | Inventario de puntos: no mide calidad, horario, ancho de banda ni uso. El 83 % son zonas wifi del DADEP en espacio público. |
| Proyecciones de población por localidad (denominador) | Secretaría Distrital de Planeación | 2005-2035 | Anual (proyección) | Proyección demográfica (base CNPV 2018) | 20 localidades × edad simple × sexo | Localidad (también UPZ) | No aplica | No publicado | Versión 2025-03 | Retroproyección para 2013-2017 y proyección después de 2018: los denominadores de años lejanos al censo tienen más error, sobre todo en localidades con migración reciente. |

## 7. Problemas encontrados

- **Archivo crudo de más de 50 MB:** `data/crudos/sds_sivim_violencia_2013_2026.csv`, 110,6 MB (110.636.231 bytes). Supera también el límite de 100 MB por archivo de GitHub; si `data/crudos/` se versiona, hay que excluirlo o pasarlo a LFS. No se tocó `.gitignore`.
- Servicio REST de seguridad nocturna (`mujeres/seguridad/MapServer`) roto: toda consulta responde error 400. GeoJSON «Versión 09.19» sin atributos. Se usó el GeoPackage del mismo conjunto.
- El conjunto «Evaluación de seguridad nocturna ... 2019» publica como CSV la medición de 2016; el índice CSV tiene columnas cruzadas y la fila de Usme mal (sección 3).
- Codificaciones distintas en cada fuente: SIVIM UTF-8 con BOM; SDMujer Latin-1; Veeduría 2025 CP850; Veeduría 2024 y Kennedy CP1252. Algunas tablas del almacén DuckDB quedaron con caracteres dañados por eso, y el metadato de SIVIM quedó como texto binario.
- Las encuestas de la Veeduría publicadas en 2024 no traen fecha de respuesta ni ficha técnica; la de mujeres tiene respuestas abiertas metidas en campos cerrados.
- El metadato de SIVIM dice periodicidad semestral y el portal dice anual; el archivo no trae mes.

## 8. Reproducir

```
python src/fuentes_genero.py
```

Con la caché llena tarda cerca de 2 minutos (la lectura del `.ods` de población toma unos 30 s). Imprime las descargas, los controles (sumas contra el total de Bogotá, conteos, errores de publicación detectados) y las pruebas. Las semillas están fijas, así que los IC bootstrap y los p de permutación salen iguales en cada corrida.
