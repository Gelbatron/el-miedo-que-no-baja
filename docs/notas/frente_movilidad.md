# Frente de vías, movilidad y alumbrado: ¿las zonas con peor alumbrado y peores vías tienen más hurtos?

Script: `src/fuentes_movilidad.py` (corre con `python src/fuentes_movilidad.py`; `--forzar` vuelve a bajar todo). Todas las cifras de esta nota salen de su salida.
Tablas: `data/procesados/movilidad_siniestros_localidad_anio.csv`, `alumbrado_localidad_anio.csv`, `ciclo_localidad.csv`, `vias_localidad.csv`, `hurtos_vehiculos_localidad.csv`, `movilidad_panel_localidad.csv` (insumo de las pruebas), `movilidad_pruebas_hipotesis.csv`, `confiabilidad_movilidad.csv` y `movilidad_bitacora.csv` (cada paso de limpieza con sus conteos).
Corte de la consulta: 6 de octubre de 2026.

## Respuesta corta

1. **La hipótesis no se sostiene por localidad.** En la especificación principal (hurtos de enero a agosto de 2025 por 100.000 habitantes, 19 localidades urbanas) ninguna de las 23 pruebas es significativa después de Benjamini-Hochberg. Las dos que tienen p < 0,05 sin ajustar van **en contra** de la hipótesis: donde hay más luminarias por km de vía hay más hurto a personas (rho = 0,48; p = 0,040) y de bicicletas (rho = 0,52; p = 0,027). Es el centro: más luz y más hurto por residente.
2. **El inventario de luminarias no sirve para medir «peor alumbrado».** Las luminarias siguen a la vía: hay entre 39,6 (Ciudad Bolívar) y 56,8 (La Candelaria) por km de vía urbana, con Bogotá en 44,4 y una variación de apenas 10 % entre localidades. Las diferencias en luminarias por km² (variación de 19 %) son, sobre todo, diferencias de densidad vial: las dos medidas se correlacionan 0,67. No hay datos abiertos de luminarias apagadas, de reclamos (PQR) ni de niveles de iluminación medidos.
3. **Lo que cambió fue la tecnología, no la cantidad.** Las luminarias del operador pasaron de 352.277 (agosto de 2019) a 354.660 (mayo de 2024), +0,7 %; con las 7.197 del Distrito, el último corte suma 361.857. La participación LED subió de 3,2 % (julio de 2017) a 70,5 %. La modernización fue sobre todo en el sur: Rafael Uribe Uribe 95 %, San Cristóbal 93 %, Ciudad Bolívar 92 %, frente a Suba 21 %, Tunjuelito 26 % y Barrios Unidos 28 %.
4. **La malla vial urbana tiene 22,4 % de km-carril en mal estado** (PCI < 56, diciembre de 2024; 21,4 % en junio de 2026). Las peores: Usme (32,3 %, con 26,4 % grave o fallado), Los Mártires (31,1 %), Ciudad Bolívar (28,7 %) y Rafael Uribe Uribe (26,7 %). El estado de la malla no se asocia con el hurto: rho entre −0,35 y 0,28, ninguna significativa.
5. **La única asociación que pasa la corrección es hurto con muertes en vía, y no habla de alumbrado.** Con el promedio 2023-2025, el hurto a personas, de automotores y de bicicletas sube con las muertes en vía por 100.000 (rho de 0,53 a 0,57; p ajustado 0,029), y sigue sin las cuatro localidades del centro (0,68 y 0,69 para personas y automotores). Las dos tasas comparten el denominador (residentes): al controlar por habitantes por km de vía, el rho parcial baja a 0,30-0,38. Lo más probable es que ambas midan actividad y tránsito que no viven en la localidad.
6. **Siniestralidad.** En 2025 murieron 612 personas en vías de Bogotá según Medicina Legal (7,7 por 100.000) y 597 según la SDM. Hubo 19.602 heridos y 11.598 siniestros con víctimas. Las tasas de muerte más altas (promedio 2023-2025) son de Los Mártires (26,9), Santa Fe (22,1) y Antonio Nariño (19,2); la más baja, Suba (3,8).
7. **Hurto de vehículos y bicicletas, solo comparable desde 2023.** Enero-agosto de 2025: 2.176 automotores (−22,6 % en tasa frente a 2023), 4.699 bicicletas (−13,8 %) y 88.114 hurtos a personas (−17,8 %). Los cambios desde 2019 y 2022 no se pueden calcular para automotores ni personas, porque la capa de la SCJ valía el doble que el SIEDCO hasta 2022. El hurto de motos por localidad no existe en una serie confiable.
8. **Cicloinfraestructura.** La red de biciusuarios mide 697 km, de los cuales 490 km son ciclorruta o bicicarril exclusivo. La cifra oficial del IDU a diciembre de 2024 es 470,8 km; por localidad la razón está entre 0,97 y 1,09 (rho = 0,998). Hurtos de bicicletas por km exclusivo en 2025: Bogotá 9,6, Los Mártires 20,4, Rafael Uribe Uribe 17,8, Fontibón 14,9.

## 1. Fuentes y pasos

| Fuente | Entidad | Qué se tomó | URL oficial |
|---|---|---|---|
| Mortalidad por accidentes de tránsito | SDS con datos del INMLCF | muertes por localidad del hecho, 2015 a junio de 2026 | https://datosabiertos.bogota.gov.co/dataset/bded0839-a912-467d-94c5-8561dbefcb22/resource/a956ec09-e22b-4b84-aeb9-25702cf610a0/download/osb_evento_transporte.csv |
| Siniestralidad_BD (SIGAT) | SDM | conteos del servidor por año, localidad y gravedad: muertos (capa 0), lesionados (1), siniestros (2), 2015 a septiembre de 2026 | https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer (catálogo: https://datos.movilidadbogota.gov.co) |
| Histórico siniestros Bogotá D.C. | SDM | 2015-2021, solo como suma de control | https://datosabiertos.bogota.gov.co/dataset/historico-siniestros-bogota-d-c |
| Modelo de prestación de servicios de alumbrado público (15 conjuntos) | UAESP, con el inventario de ENEL-CODENSA | luminarias por localidad y tecnología, 52 cortes mensuales de mayo de 2017 a mayo de 2024 | conjuntos `alumbrado_publico_lt`, `data-set-subdireccion-alumbrado-publico-junio-2018`, `modelo-de-prestacion-de-servicios-alumbrado-publico-2021`, `-junio-diciembre-2021`, `-enero-abril-2022`, `-mayo-septiembre-2022`, `-ano-2023`, `-ano-2024` en https://datosabiertos.bogota.gov.co (cada URL de recurso está en `ALUMBRADO_CORTES` del script y en la columna `url` de la tabla) |
| Estado MallaVial urbana POT-555 (junio 2026) y POT-190 (diciembre 2024) | IDU | PCI y km-carril de cada calzada, con localidad | https://services2.arcgis.com/qAnmJmgmnVso8Fzo/arcgis/rest/services/EstadoMallaVialOD555/FeatureServer/2 y .../EstadoMallaVialOD/FeatureServer/0 (catálogo: https://geoportal-idu.hub.arcgis.com) |
| Estado superficial Bogotá D.C. | IDU | diagnóstico de calidad; no se usa | https://datosabiertos.bogota.gov.co/dataset/estado-superficial-bogota-d-c |
| Calzada (tipo de superficie) | IDU en el Mapa de Referencia | para el diagnóstico anterior | https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/Mapa_Referencia/Mapa_Referencia/MapServer/15 |
| Malla vial (ejes) | IDECA | longitud de vía | .../Mapa_Referencia/MapServer/13 |
| Clasificación del suelo | IDECA | suelo urbano (SUECSUELO = 1), para el área urbana | .../Mapa_Referencia/MapServer/45 |
| Red de biciusuarios y Cicloruta | IDU en el Mapa de Referencia | líneas de la red y polígonos de ciclorruta | .../Mapa_Referencia/MapServer/19 y /18 |
| Estadísticas de extensión y estado de ciclorrutas 2024-II | IDU | km y estado por localidad (contraste) | https://idu.gov.co/Archivos_Portal/Transparencia/Informacion%20de%20interes/SIIPVIALES/Innovaci%C3%B3n/ciclorrutas-2025/Infografia%20Ciclorrutas%202024-II.pdf |
| Puntos de evaluación de seguridad nocturna (GeoPackage 09.19) | Secretaría de la Mujer | iluminación de 44.335 puntos auditados en 2019 | https://datosabiertos.bogota.gov.co/dataset/f714e477-8e2a-44a2-87c0-17b491a01bcc/resource/486903b6-42da-4b36-9bfd-6e17bd0b7c6e/download/puntosseguridadnocturna.gpkg |
| Delitos de alto impacto | SCJ | HA, HB, HP y homicidios, enero-agosto 2018-2026 (ya en el repo: `scj_delitos_localidad_largo.csv`; la fila «Sin localización» se toma del crudo) | https://oaiee.scj.gov.co/agc/rest/services/Tematicos_Pub/CifrasSCJ/MapServer/0 |
| Población, límites y Bienal 2025 | SDP, IDECA, SCRD | del repo: `sdp_poblacion_localidad_grupos.csv`, `ideca_localidades.geojson`, `panel_localidad_2025.csv` (alumbrado malo) | ver `src/fuentes.py` |

Pasos:

1. Cada fuente se baja una sola vez a `data/crudos/` y queda en `registro_descargas.csv` (URL, fecha, bytes, sha1). Los alumbrados van en `data/crudos/uaesp_alumbrado/` (34 archivos). Ningún crudo pasa de 50 MB; el más grande es el histórico de siniestros (38,4 MB).
2. Los servicios ArcGIS se consultan por lotes de `objectIds`, y se verifica que bajen tantos registros como reporta `returnCountOnly`. Los conteos de la SDM los calcula el servidor (`outStatistics`), con y sin los formularios «AA».
3. La localidad se normaliza con `territorio.cod_localidad()`. Los registros sin localidad cuentan solo en la fila Bogotá (código 0).
4. Las geometrías se proyectan a EPSG:3116. Áreas, longitudes de vía y de ciclorruta salen de `geopandas.overlay` contra los límites de localidad de IDECA y su parte urbana.
5. El lector de alumbrado encuentra en cada hoja la tabla «localidad × tecnología» por sus rótulos. La que suma cerca de 355.000 luminarias es la del operador; la que suma menos de 20.000, la del Distrito. Los 38 cortes que traen un total impreso coinciden exactamente con lo leído. En los CSV de 2017-2019 que traen a la vez el total y las tecnologías, el total por localidad es igual a la suma de las cuatro tecnologías (mayo de 2017 solo trae el total).

## 2. Advertencias

**Cortes y años incompletos**

- Medicina Legal (SDS) llega hasta junio de 2026 (cifras preliminares); la SDM, hasta el 30 de septiembre de 2026. En 2026 se dejan los conteos y la tasa en blanco (`anio_completo_* = False`).
- Los hurtos de la SCJ son enero-agosto de cada año: las tasas «por 100.000» son de ocho meses, no anuales. «Último año completo» = 2025 (ventana cerrada y año calendario cerrado); 2026 es el último disponible.
- El último inventario de alumbrado publicado es de **mayo de 2024**. No hay cortes de junio de 2024 en adelante. Entre 2017 y 2020 hay huecos: 2020 solo trae abril.
- El estado de la malla del IDU tiene dos cortes en datos abiertos (diciembre de 2024 y junio de 2026); no hay serie anterior por calzada.

**Duplicados y cambios de registro**

- Medicina Legal (SDS): cada muerte aparece dos veces, una con código 0 («Bogotá») y otra con su localidad o con 21 («Sin dato»). El código 0 cuadra con la suma de 1 a 21 en todos los años (diferencia 0). Entre 2022 y 2024, 8 % de las muertes no tiene localidad (49, 53 y 51); en los demás años, de 1 % a 3 %.
- SDM (SIGAT): de 2007 a 2020 cada formulario está dos veces, con prefijo «A» y «AA» y el mismo número: 50 % de los registros de muertos de 2015-2019 y 45 % de 2020 son «AA». Sin ellos, los siniestros con víctimas quedan entre 0,2 % y 1,7 % por debajo del histórico publicado en el portal (2015: 10.164 frente a 10.210; 2019: 11.944 frente a 12.145). En una prueba con 2019, los «AA» que no tienen par aportan 86 heridos (0,5 %). Frente al consolidado de víctimas del portal, las muertes difieren en 0 a 3 por año (2015: 542 frente a 544; 2019: 502 frente a 505) y los heridos quedan 8 a 10 % por debajo (2019: 17.057 frente a 18.477); esa diferencia no se pudo explicar.
- Los siniestros de «solo daños» casi dejan de registrarse en 2023 (12.557 en 2022, 1.115 en 2023, 802 en 2025). Solo se usan siniestros con heridos o muertos.
- La SDM cuenta menos muertes que Medicina Legal (597 frente a 612 en 2025; 560 frente a 630 en 2022). La tasa principal usa Medicina Legal.
- SCJ: según el contraste con el SIEDCO (`src/validacion_registro.py`, `docs/notas/frente_victimizacion.md`), hurto a personas y automotores valen 1,9 a 2,6 veces el SIEDCO en 2018-2022 e igual desde 2023. Por eso caen 40 % en 2023. Solo se comparan desde 2023 y la tabla deja en blanco los cambios desde 2019 y 2022. Las columnas «motocicletas» (HM), «celulares» (HCE) y «comercio» (HC) no se usan: desde 2023 HM repite el hurto a comercio del SIEDCO y HCE repite motos. El hurto de bicicletas no tiene serie externa para validarlo y no muestra salto en 2023 (−2 %).

**Cambios de inventario en el alumbrado**

- Hasta junio de 2021 solo se publica el inventario del operador. Desde julio de 2021 se agregan las luminarias de propiedad del Distrito (4.251 a 7.197), pero por localidad solo vienen de julio de 2021 a abril de 2022 y de enero a mayo de 2024. De mayo de 2022 a noviembre de 2023 el libro trae solo el total del Distrito, y la tabla lo anota. La serie comparable en el tiempo es `luminarias_operador`.
- Fechas internas inconsistentes: el archivo de mayo de 2017 dice «fecha corte mayo 15 de 2019»; el de octubre de 2017 trae fecha 22/09/2017; el de noviembre de 2017 es idéntico al de septiembre de 2017 (`duplicado_de = 2017-09`); el que el portal llama «Marzo 2020» es del 24 de abril de 2020. El libro de mayo-septiembre de 2022 trae dos versiones de junio; se usa «JUN v.2».
- Seis conjuntos del portal repiten cortes ya incluidos y se excluyen (lista en `ALUMBRADO_DUPLICADOS_EXCLUIDOS`).
- El inventario cuenta luminarias instaladas, no si encienden ni cuánta luz dan.

**Denominadores**

- El área oficial de varias localidades incluye suelo rural y cerros: Usme 215 km² (19,3 urbanos), Ciudad Bolívar 130 (26,2), Suba 101 (58,1). Las luminarias por km² total castigan a esas localidades: Usme tiene 82 por km² total y 916 por km² urbano. Por eso las pruebas usan el área urbana (IDECA, 370,5 km²) y los km de vía dentro del suelo urbano (8.145 de 9.390 km).
- Sumapaz no tiene suelo urbano ni estado urbano de la malla; queda fuera de las densidades y de las pruebas.
- Las tasas por residente inflan el centro, adonde llega mucha más gente de la que vive allí. La Candelaria tiene 16.801 habitantes y 6.720 hurtos a personas por 100.000 en ocho meses.
- La malla vial de IDECA se bajó simplificada a 1 m (`maxAllowableOffset`); el efecto sobre longitudes es despreciable a esta escala.

## 3. Hallazgos

### Siniestralidad (`movilidad_siniestros_localidad_anio.csv`)

| Año | Muertes INMLCF | por 100.000 | Muertes SDM | Heridos SDM | Siniestros con víctimas |
|---|---|---|---|---|---|
| 2015 | 556 | 7,6 | 542 | 13.183 | 10.164 |
| 2019 | 523 | 6,9 | 502 | 17.057 | 11.944 |
| 2020 | 406 | 5,3 | 376 | 12.482 | 8.667 |
| 2022 | 630 | 8,0 | 560 | 21.500 | 12.896 |
| 2023 | 629 | 8,0 | 564 | 22.971 | 13.001 |
| 2024 | 665 | 8,4 | 600 | 22.667 | 12.977 |
| 2025 | 612 | 7,7 | 597 | 19.602 | 11.598 |
| 2026 (ene-jun / ene-sep) | 369 | — | 480 | 12.230 | 7.340 |

Muertes en vía por 100.000, promedio 2023-2025 (Medicina Legal): Los Mártires 26,9; Santa Fe 22,1; Antonio Nariño 19,2; Puente Aranda 14,4; Tunjuelito 13,5; Teusaquillo 13,3. Las más bajas: Suba 3,8, Bosa 5,7, La Candelaria 5,9. Sumapaz da 27,6 con solo 3 muertes en tres años, y La Candelaria 5,9 con 3. En las localidades pequeñas una muerte mueve mucho la tasa.

### Alumbrado (`alumbrado_localidad_anio.csv`)

- 52 cortes, de mayo de 2017 a mayo de 2024. Las luminarias del operador van de 344.910 a 356.543. El total casi no se mueve; lo que cambia es la tecnología: LED de 3,2 % (julio de 2017) a 22,8 % (agosto de 2019), 41,8 % (abril de 2020), 63,1 % (junio de 2022) y 70,5 % (mayo de 2024).
- Mayo de 2024, luminarias por km² urbano: de 604,7 (Fontibón) a 1.378,8 (Santa Fe). Por km de vía urbana: de 39,6 (Ciudad Bolívar) a 56,8 (La Candelaria). Por 1.000 habitantes: de 30,7 (Bosa) a 153,0 (La Candelaria).
- De agosto de 2019 a mayo de 2024 crece Bosa (+10,6 %) y Usme (+8,0 %). Bajan La Candelaria (−13,0 %), Santa Fe (−2,2 %) y Los Mártires (−1,8 %). La comparación mezcla operador (2019) y operador más Distrito (2024): el Distrito pesa 2 %.

### Malla vial (`vias_localidad.csv`)

- Diciembre de 2024: 13.373 km-carril urbanos, 13.291 con estado, PCI medio 71,0, 22,4 % con PCI < 56 y 9,8 % grave o fallado (PCI ≤ 25). En la malla local sube a 31,9 %. Junio de 2026: 13.860 km-carril, PCI medio 71,4, 21,4 % con PCI < 56.
- Peor estado (PCI < 56, dic-2024): Usme 32,3 %, Los Mártires 31,1 %, Ciudad Bolívar 28,7 %, Rafael Uribe Uribe 26,7 %. Mejor: Santa Fe 13,9 %, Barrios Unidos 17,4 %, Chapinero 17,9 %.
- Densidad vial urbana: de 15,0 km de vía por km² (Fontibón) a 29,7 (Rafael Uribe Uribe); Bogotá 22,0 (8.145 km en 370,5 km²). Las luminarias por km² urbano se correlacionan 0,67 con esta densidad.
- **El archivo «Estado superficial» del portal no trae el estado.** Sus 104.550 calzadas tienen códigos 1, 2, 3, 4, 5, 6, 8, 12 y 13, y el código coincide con el tipo de superficie de la calzada (rígido, flexible, mixto, adoquín, afirmado, tierra, piedra laja, placa huella) en 93,4 % de 104.104 cruces. El estado (PCI) solo está en el servicio del IDU.

### Cicloinfraestructura y hurto de bicicletas (`ciclo_localidad.csv`)

- Red de biciusuarios (agosto de 2026): 697,1 km. Exclusiva (ciclorruta o bicicarril, ≥ 50 % dentro del polígono de ciclorruta): 489,8 km. Contraste con el IDU a diciembre de 2024: 677,5 km de red y 470,8 km con diagnóstico; por localidad la razón calculado/IDU va de 0,97 a 1,09.
- Hurto de bicicletas, enero-agosto 2025: 4.699 en Bogotá (59,2 por 100.000; 9,6 por km exclusivo), −13,8 % en tasa frente a 2023 y −16,2 % frente a 2022. Por residente, el más alto es Los Mártires (164,3), Teusaquillo (147,2), La Candelaria (142,8) y Barrios Unidos (136,7); el más bajo, Usme (11,7). Por km exclusivo, Los Mártires (20,4), Rafael Uribe Uribe (17,8), Fontibón (14,9) y Antonio Nariño (14,8).
- Los km son de la red de 2026, aplicados a todos los años: el hurto por km de 2022 queda subestimado.

### Hurto de vehículos (`hurtos_vehiculos_localidad.csv`)

- Automotores, enero-agosto 2025: 2.176 (27,4 por 100.000), −22,6 % en tasa frente a 2023 y −6,3 % en 2026. Más altos: Puente Aranda (100,5), Antonio Nariño (61,4), Los Mártires (57,2). Más bajos: Usaquén (7,5), Suba (12,1).
- Bicicletas: ver arriba. Hurto a personas, como referencia: 88.114 con «Sin localización» (3.889 sin localidad), −17,8 % en tasa frente a 2023.
- Las columnas de 2019 y 2022 quedan en la tabla con la escala vieja de la capa y `quiebre_serie_2023 = True`; sus cambios están en blanco.

## 4. ¿Se sostiene la hipótesis?

**Método.** Spearman entre las 19 localidades urbanas. IC 95 % por bootstrap percentil (10.000 remuestreos de localidades, semilla fija). p bilateral por permutación (10.000). Benjamini-Hochberg dentro de cada bloque: 1 alumbrado, 2 malla vial, 3 siniestralidad, 4 calidad del alumbrado. Hurtos: personas, automotores y bicicletas por 100.000; las motos quedan fuera (ver advertencias). Alumbrado: inventario de mayo de 2024. Malla: diciembre de 2024. Muertes: Medicina Legal 2025.

**Especificación principal: hurtos enero-agosto 2025**

| Bloque | Hurto (y) | Variable (x) | Signo esperado | n | rho | IC 95 % | p perm. | p BH |
|---|---|---|---|---|---|---|---|---|
| 1 | hurto a personas | luminarias por km² urbano | − | 19 | 0,30 | [−0,22; 0,69] | 0,213 | 0,426 |
| 1 | hurto de automotores | luminarias por km² urbano | − | 19 | 0,13 | [−0,37; 0,58] | 0,587 | 0,704 |
| 1 | hurto de bicicletas | luminarias por km² urbano | − | 19 | 0,17 | [−0,28; 0,57] | 0,471 | 0,704 |
| 1 | hurto a personas | luminarias por km de vía | − | 19 | 0,48 | [−0,04; 0,82] | 0,040 | 0,119 |
| 1 | hurto de automotores | luminarias por km de vía | − | 19 | −0,08 | [−0,43; 0,36] | 0,734 | 0,734 |
| 1 | hurto de bicicletas | luminarias por km de vía | − | 19 | 0,52 | [0,02; 0,82] | 0,027 | 0,119 |
| 2 | hurto a personas | % km-carril con PCI < 56 | + | 19 | −0,35 | [−0,76; 0,21] | 0,140 | 0,336 |
| 2 | hurto de automotores | % km-carril con PCI < 56 | + | 19 | 0,28 | [−0,22; 0,69] | 0,244 | 0,366 |
| 2 | hurto de bicicletas | % km-carril con PCI < 56 | + | 19 | −0,33 | [−0,80; 0,23] | 0,168 | 0,336 |
| 2 | hurto a personas | km de vía por km² urbano | sin signo previo | 19 | −0,06 | [−0,48; 0,41] | 0,818 | 0,818 |
| 2 | hurto de automotores | km de vía por km² urbano | sin signo previo | 19 | 0,34 | [−0,12; 0,67] | 0,155 | 0,336 |
| 2 | hurto de bicicletas | km de vía por km² urbano | sin signo previo | 19 | −0,19 | [−0,63; 0,30] | 0,448 | 0,538 |
| 3 | hurto a personas | muertes en vía por 100.000 | + | 19 | 0,45 | [−0,08; 0,85] | 0,051 | 0,228 |
| 3 | hurto de automotores | muertes en vía por 100.000 | + | 19 | 0,36 | [−0,16; 0,72] | 0,123 | 0,228 |
| 3 | hurto de bicicletas | muertes en vía por 100.000 | + | 19 | 0,36 | [−0,15; 0,72] | 0,137 | 0,228 |
| 3 | homicidios | muertes en vía por 100.000 | + | 19 | 0,26 | [−0,27; 0,67] | 0,291 | 0,337 |
| 3 | homicidios | heridos en vía por 100.000 (SDM) | + | 19 | 0,24 | [−0,34; 0,67] | 0,337 | 0,337 |
| 4 | hurto a personas | % que califica malo el alumbrado (Bienal 2025) | + | 19 | −0,02 | [−0,57; 0,49] | 0,953 | 0,953 |
| 4 | hurto de automotores | % que califica malo el alumbrado (Bienal 2025) | + | 19 | −0,06 | [−0,52; 0,43] | 0,821 | 0,953 |
| 4 | hurto de bicicletas | % que califica malo el alumbrado (Bienal 2025) | + | 19 | −0,20 | [−0,67; 0,31] | 0,408 | 0,897 |
| 4 | hurto a personas | % de puntos con iluminación ninguna o poca (SDMujer 2019) | + | 19 | 0,13 | [−0,39; 0,62] | 0,599 | 0,898 |
| 4 | hurto de automotores | % de puntos con iluminación ninguna o poca (SDMujer 2019) | + | 19 | −0,21 | [−0,66; 0,29] | 0,396 | 0,897 |
| 4 | hurto de bicicletas | % de puntos con iluminación ninguna o poca (SDMujer 2019) | + | 19 | 0,18 | [−0,37; 0,69] | 0,449 | 0,897 |

**Sensibilidades** (todas en `movilidad_pruebas_hipotesis.csv`):

- *Promedio 2023-2025* (el tramo sin quiebre de la SCJ, con muertes y heridos también promediados). Alumbrado, malla y calidad del alumbrado siguen sin ninguna prueba significativa tras BH. Lo único que pasa la corrección es el bloque 3: hurto a personas (rho = 0,57; IC [0,09; 0,86]), automotores (0,56; [0,11; 0,83]) y bicicletas (0,53; [0,15; 0,79]) frente a muertes en vía, los tres con p BH = 0,029. Homicidios frente a muertes (0,20) y heridos (0,30) no.
- *Promedio 2023-2025 sin el centro* (n = 15, sin Chapinero, Santa Fe, Los Mártires ni La Candelaria). Muertes en vía siguen asociadas con hurto a personas (0,68; IC [0,26; 0,88]; p BH = 0,016) y automotores (0,69; [0,21; 0,92]; p BH = 0,016); bicicletas queda en p = 0,042 sin ajustar. El «% que califica malo el alumbrado» va **en contra** de la hipótesis: menos hurto donde peor se califica la luz (personas −0,51, p = 0,055; bicicletas −0,57, p = 0,030), sin sobrevivir a BH.
- *Control exploratorio, sin p:* al quitar por rangos el efecto de los habitantes por km de vía urbana (un indicador de cuánta gente vive frente a cuánta vía hay), el rho parcial entre muertes en vía y hurto baja de 0,57 a 0,30 (personas), de 0,56 a 0,38 (automotores) y de 0,53 a 0,30 (bicicletas). Los habitantes por km de vía se correlacionan −0,53 con las muertes y −0,76 con el hurto a personas.

**Lectura.**

- *Alumbrado:* no hay señal de que menos luminarias o peor luz acompañen más hurto. Lo poco que aparece va al revés, y se explica porque el centro concentra luz, vías, comercio y población flotante. El inventario no distingue una luminaria que alumbra de una apagada, y la variación de luminarias por km de vía es de 10 %. Los dos indicadores de calidad tampoco ayudan: la auditoría de 2019 encontró iluminación «ninguna» o «poca» en solo 1,1 % de los puntos (piso casi sin variación) y la percepción de la Bienal no se asocia o va en contra.
- *Malla vial:* las localidades con peor pavimento (Usme, Ciudad Bolívar, Rafael Uribe Uribe) tienen tasas bajas de hurto por residente, y los IC cubren el cero. Con n = 19 no podemos descartar efectos de tamaño moderado (los IC llegan a ±0,7), pero tampoco hay evidencia a favor.
- *Siniestralidad:* es la única relación robusta, y no sale de la hipótesis de alumbrado. Hurto y muertes en vía son altos donde hay mucha circulación y pocos residentes; el control por habitantes por km de vía le quita cerca de la mitad. Homicidios y siniestralidad vial no se asocian.
- *Escala:* esto es ecológico, entre 19 unidades grandes y heterogéneas. Que no aparezca a nivel de localidad no descarta un efecto de calle o de cuadra. Para probarlo haría falta cruzar hurtos georreferenciados (no públicos con coordenadas) con luminarias por punto o con luminarias reportadas apagadas, que no se publican.

**Conclusión.** Con los datos abiertos disponibles, la hipótesis no se sostiene a nivel de localidad: no hay asociación entre alumbrado, estado de la malla y hurto (de personas, automotores o bicicletas) que sobreviva a la corrección por comparaciones múltiples, y los signos que aparecen van en contra. Con n = 19, la potencia es baja; un efecto moderado podría existir y no verse.

## 5. Ficha de confiabilidad (`confiabilidad_movilidad.csv`)

| Fuente | Entidad | Años | Periodicidad | Tipo | Registros | Nivel más fino | Última actualización | Faltantes | Advertencia |
|---|---|---|---|---|---|---|---|---|---|
| Mortalidad por accidentes de tránsito | SDS (INMLCF) | 2015-2026 (2026 ene-jun) | semestral | registro administrativo | 6.569 muertes | localidad del hecho | 2026-09-02 | 2026 jul-dic; antes de 2015 | cada muerte dos veces en el archivo; 8 % sin localidad en 2022-2024; recientes preliminares |
| Siniestralidad_BD, muertos | SDM (SIGAT) | 2007-2026 (2026 ene-sep) | continua | registro administrativo (IPAT) | 6.333 (2015-2026, sin «AA») | punto | consulta 2026-10-06 | ninguno 2015-2025 | duplicado «A»/«AA» hasta 2020; cuenta menos que Medicina Legal |
| Siniestralidad_BD, lesionados | SDM (SIGAT) | 2007-2026 | continua | registro administrativo (IPAT) | 204.090 | punto | consulta 2026-10-06 | ninguno 2015-2025 | duplicado hasta 2020; 8-10 % menos heridos que el consolidado del portal 2015-2019; solo lo que registra la policía de tránsito |
| Siniestralidad_BD, siniestros | SDM (SIGAT) | 2007-2026 | continua | registro administrativo (IPAT) | 281.786 | punto y calzada | consulta 2026-10-06 | ninguno 2015-2025 | «solo daños» deja de registrarse en 2023 |
| Histórico siniestros (control) | SDM | 2015-2021 (2021 parcial) | única | registro administrativo | 199.146 | punto | 2021-10-22 | 2022 en adelante | solo suma de control |
| Inventario de luminarias | UAESP (ENEL-CODENSA) | may-2017 a may-2024 | mensual con huecos | inventario | 52 cortes | localidad | 2024-08-07 | jun-2024 en adelante | 15 conjuntos con formatos distintos y fechas internas inconsistentes; Distrito por localidad solo en algunos cortes; no mide si encienden |
| Estado de la malla vial (PCI) jun-2026 | IDU | jun-2026 | semestral | inventario técnico (capa geográfica) | 102.238 calzadas | calzada | 2026-09-03 | cortes anteriores salvo dic-2024 | el PCI de cada calzada puede tener años; malla del POT 555 |
| Estado de la malla vial (PCI) dic-2024 | IDU | dic-2024 | semestral | inventario técnico (capa geográfica) | 100.508 calzadas | calzada | 2025-04-29 | — | malla del POT 190: no comparable por tipo de malla con 2026 |
| Estado superficial (portal) | IDU | 2025-12-31 | irregular | tabla sin geometría | 104.550 | calzada | 2026-05-25 | — | no usable: el código es el tipo de superficie en 93,4 % de los casos |
| Malla vial (ejes) | IDECA | vigente | trimestral | capa geográfica | 139.106 ejes | segmento | 2026-08-28 | sin serie histórica | no trae estado; simplificada a 1 m |
| Red de biciusuarios y ciclorrutas | IDU | vigente (ago-2026) | trimestral | capa geográfica | 15.985 segmentos | segmento | 2026-08-25 | versiones previas solo en SHP 7z | dominio de clase no publicado; exclusividad por cruce con el polígono |
| Infografía ciclorrutas 2024-II | IDU | dic-2024 | semestral | reporte (PDF) | 19 localidades | localidad | 2024-12-31 | — | transcrito a mano; solo contraste |
| Delitos de alto impacto (HA, HB, HP, H) | SCJ | 2018-2026 (ene-ago) | mensual | registro administrativo (SIEDCO) | 1.428.437 hechos | localidad | 2026-09-21 | sep-dic de cada año; antes de 2018 | HP y HA comparables solo desde 2023; HM, HCE y HC no se usan; HB sin validar; el centro se infla por población flotante |
| Auditoría de seguridad nocturna | Secretaría de la Mujer | nov-2015/feb-2016 y sep-2019 | 2 olas | observación en campo | 64.995 puntos | punto | 2024-05-07 | 2020 en adelante | 2019 es anterior a casi toda la modernización LED; recorridos no aleatorios; el GeoJSON viene sin atributos |

## 6. Datos que no existen o no se pudieron usar

- **Luminarias apagadas, fallas o reclamos de alumbrado por localidad:** no hay ningún conjunto en el portal (búsquedas «luminarias apagadas», «PQR alumbrado»: 0 resultados). Tampoco niveles de iluminación medidos (lux).
- **Inventario de alumbrado después de mayo de 2024.** Por UPZ solo hay una capa de 2022 (`luminarias_upz-bogota-d-c`), que no se usó.
- **Siniestros 2022-2025 por localidad en el portal de datos abiertos:** el portal se quedó en 2021. Existen en el servicio ArcGIS de la SDM, que es lo que se usó.
- **Hurto de motocicletas por localidad confiable:** la columna HM de la SCJ es otro delito desde 2023, y la HCE (que coincide con motos del SIEDCO en Bogotá) no está validada por localidad.
- **Hurtos de vehículos de 2019 y 2022 comparables con 2025:** solo con el SIEDCO, que no viene por localidad.
- **Estado de la malla vial antes de diciembre de 2024 por calzada.** El archivo «estado superficial» del portal trae el tipo de superficie, no el estado.
- El IPAT (tabla `VM_ACC_VIA` de la SDM) registra iluminación artificial y su estado en cada siniestro desde 2019. Existe, pero cruzarlo por localidad exige bajar ~970.000 filas y unirlas con los siniestros; no se hizo en esta entrega.

## 7. Columnas de las tablas por localidad

- `movilidad_siniestros_localidad_anio.csv`: localidad, nombre, anio, muertes_inmlcf, muertes_sdm, lesionados_sdm, siniestros_con_victimas_sdm, siniestros_con_muertos_sdm, siniestros_solo_danos_sdm, poblacion, tasa_muertes_inmlcf_100k, tasa_muertes_sdm_100k, tasa_lesionados_sdm_100k, tasa_siniestros_con_victimas_sdm_100k, meses_inmlcf, meses_sdm, anio_completo_inmlcf, anio_completo_sdm, nota.
- `alumbrado_localidad_anio.csv`: localidad, nombre, periodo, anio, fecha_corte_texto, luminarias_operador, luminarias_distrito, luminarias_total, alcance_total, luminarias_led, pct_led, area_km2, area_urbana_km2, km_via_urbana, km_carril_2024_12, luminarias_km2, luminarias_km2_urbano, luminarias_km_via, luminarias_km_carril, poblacion, luminarias_1000_hab, duplicado_de, n_localidades_leidas, nota, archivo, hoja, url.
- `ciclo_localidad.csv`: localidad, nombre, km_red_biciusuarios, km_ciclorruta_exclusiva, km_ciclorruta_idu_2024, pct_buen_estado_idu_2024, hb_{2022,2023,2025,2026}, hb_100k_{año}, hb_por_km_red_{año}, hb_por_km_exclusiva_{año}, var_pct_hb_100k_2022_2025, var_pct_hb_100k_2023_2025, var_pct_hb_100k_2022_2026, var_pct_hb_casos_2022_2025, nota.
- `vias_localidad.csv`: localidad, nombre, area_km2, area_urbana_km2, km_via_ejes, km_via_urbana, densidad_via_km_km2, densidad_via_km_km2_urbano; para 2024_12 y 2026_06: km_carril, km_carril_con_estado, pci_medio, pct_pci_menor_56, pct_grave_fallado, pct_bueno_satisfactorio, pct_pci_menor_56_local; densidad_km_carril_km2_urbano_2024_12, cambio_pp_pci_menor_56, nota.
- `hurtos_vehiculos_localidad.csv` (una fila por localidad y código HA, HB, HP): localidad, nombre, codigo, tipo, casos_{2019,2022,2023,2024,2025,2026}, tasa_100k_{año}, var_pct_tasa_2019_2025, var_pct_tasa_2022_2025, var_pct_tasa_2023_2025, var_pct_tasa_2025_2026, quiebre_serie_2023, comparable_desde, estado_serie, nota.
- `movilidad_panel_localidad.csv` (19 urbanas): localidad, nombre, poblacion_2025, {hp, ha, hb, homicidios}_100k_{2025, 2023_2025}, luminarias_km2_urbano_2024_05, luminarias_km_via_2024_05, luminarias_km_carril_2024_05, luminarias_1000_hab_2024_05, pct_led_2024_05, pct_pci_menor_56_2024_12, pci_medio_2024_12, densidad_via_km_km2_urbano, pct_pci_menor_56_2026_06, muertes_via_100k_{2025, 2023_2025}, lesionados_via_100k_{2025, 2023_2025}, alumbrado_malo_bienal_2025, iluminacion_deficiente_2016, iluminacion_deficiente_2019.
