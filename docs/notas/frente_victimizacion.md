# Frente de victimización y denuncia: ¿cayó el delito o cayó la denuncia?

Script: `src/fuentes_victimizacion.py` (corre con `python src/fuentes_victimizacion.py`; todas las cifras de esta nota salen de su salida).
Tablas: `data/procesados/victimizacion_denuncia_bogota.csv`, `data/procesados/registro_contraste_bogota.csv`, `data/procesados/confiabilidad_victimizacion.csv`.
Cifras transcritas a mano: `data/crudos/victimizacion_transcritos.csv`.
Corte de la consulta: 6 de octubre de 2026.

## Respuesta corta

1. **La caída del 59 % no mide delito ni denuncia: es un quiebre de la serie de la SCJ.** En la capa de la Secretaría de Seguridad que usa el proyecto, el hurto a personas de enero a agosto de 2018 a 2022 vale entre 2,28 y 2,55 veces lo que publica la Policía Nacional (SIEDCO) para los mismos meses. Desde 2023 las dos series son idénticas (razón 1,00). Pasa lo mismo con hurto a residencias (2,29 a 3,00 veces) y hurto de automotores (2,00 a 2,01 veces de 2018 a 2021). En homicidios, lesiones personales, delitos sexuales y violencia intrafamiliar la razón está entre 1,00 y 1,09 en todos los años. El «−40 % en un solo año» de 2023 es el paso de una escala a la otra.
2. **Con la serie de la Policía no hay caída grande.** El hurto a personas registrado en Bogotá de enero a agosto pasó de 78.419 casos en 2022 a 75.124 en 2026 (−4,2 %). Entre 2022 y 2023 subió 36,2 %, como informó la Alcaldía en su momento (+23 % al 31 de agosto de 2023).
3. **Las encuestas no muestran que la denuncia haya caído.** ECSC (DANE), Bogotá, 2021 frente a 2023: la victimización por hurto a personas pasó de 7,3 % a 6,9 % (−0,5 pp; p = 0,50) y la denuncia del hurto de 36,0 % a 42,9 % (+6,9 pp; p = 0,15). Para que la caída de la SCJ entre 2021 y 2023 se explicara por menos denuncia, la tasa de 2023 tendría que haber sido 25,2 %, 4,6 errores estándar por debajo de lo que midió el DANE. La encuesta de la Cámara de Comercio (CCB) da lo mismo para 2022 frente a 2023: la denuncia del hurto pasó de 38,6 % a 38,8 %.
4. **Desde 2023 sí hay una baja moderada, y apunta a menos delito.** El registro baja 17,5 % entre enero-agosto de 2023 y de 2025, con las dos series ya iguales. En ese lapso, la CCB mide menos victimización por hurto a personas (14,7 % a 11,1 %, −24 %, calculada) y más denuncia (38,8 % a 43,2 %). Víctimas por denuncia bajan 15,5 %, casi lo mismo que el registro. La evidencia es más débil: una sola encuesta, sin errores por indicador, con campo en meses distintos cada año.
5. **Lo que la encuesta oficial no alcanza.** El DANE no hizo la ECSC en 2023 «por motivos presupuestales», así que no hay victimización de 2022. La última edición publicada (noviembre de 2025) mide 2023. No hay ECSC para 2024, 2025 ni 2026.

## 1. Fuentes

| Fuente | Qué se usó | URL |
|---|---|---|
| DANE, Encuesta de Convivencia y Seguridad Ciudadana (ECSC), página vigente | edición 2024 (victimización 2023) | https://www.dane.gov.co/index.php/estadisticas-por-tema/seguridad-y-defensa/encuesta-de-convivencia-y-seguridad-ciudadana-ecsc |
| DANE, ECSC históricos | ediciones 2014 a 2022 | https://www.dane.gov.co/index.php/estadisticas-por-tema/seguridad-y-defensa/encuesta-de-convivencia-y-seguridad-ciudadana-ecsc/encuesta-de-convivencia-y-seguridad-ciudadana-ecsc-historicos |
| Anexos ECSC (Excel) | cuadros por ciudad | `https://www.dane.gov.co/files/investigaciones/poblacion/convivencia/{2014/anexos_ecsc_2013_2014.xls, 2015/anexos_ecsc_2015.xls, 2016/anexos_ecsc_2016.xls, 2017/anexos_ecsc_2017.xls, 2018/anexos_ecsc_2018.xls, 2019/anexos_ecsc_2019.xlsx, 2020/anexos_ecsc_2020.xlsx, 2021/anexos_ecsc_2021.xlsx}` y https://www.dane.gov.co/files/operaciones/ECSC/anex-ECSC-2024.xlsx |
| Boletín técnico ECSC 2024 | pruebas de significancia por ciudad (gráficos 2, 4, 11 y 12, pp. 12, 14, 24 y 28) | https://www.dane.gov.co/files/operaciones/ECSC/bol-ECSC-2024.pdf |
| Metodología general ECSC, versión 9 | historia de la operación y quiebres (p. 7), período de referencia y campo (p. 35), muestra por sede (p. 39) | https://www.dane.gov.co/files/operaciones/ECSC/met-ECSC.pdf |
| Microdatos ECSC «2023» (año de referencia; campo 2024-2025) | confirma que no hay edición posterior | https://microdatos.dane.gov.co/index.php/catalog/894 |
| CCB, Encuesta de Percepción y Victimización 2025 (informe) | victimización 2015-2025 (p. 6), delitos sufridos (p. 8), denuncia 2015-2025 (p. 9), denuncia por delito 2022-2025 (p. 10), razones de no denuncia (p. 12), ficha técnica (p. 3) | https://assets.ctfassets.net/n1ptkpqt763u/4K3x5p5DuldDQiWajUfAHu/61a2b7a5a0392c06953d6dc6124baa03/2026.02.16_EPV_2025_WEB.pdf |
| CCB, EPV 2024 (informe) | ficha técnica (p. 3): campo 4 jun-5 jul 2024, n = 19.354 | https://www.valoraanalitik.com/wp-content/uploads/2025/06/Encuesta-de-Percepcion-y-Victimizacion-2024-VF-Bogota_.pdf |
| CCB, comunicados | 17 feb 2026 (EPV 2025) y 26 jun 2025 (EPV 2024) | https://www.ccb.org.co/de-interes/comunicados/bogota-mejoro-en-indicadores-de-victimizacion-y-percepcion-de-seguridad-en-2025 · https://www.ccb.org.co/de-interes/comunicados/en-descenso-percepcion-de-inseguridad-y-victimizacion-en-bogota |
| SCJ, capa «Delitos Alto Impacto Localidad» (la del proyecto) | enero-agosto 2018-2026; «Cálculos propios de la OAIEE. Fecha de corte 31 agosto 2026» | https://oaiee.scj.gov.co/agc/rest/services/Tematicos_Pub/CifrasSCJ/MapServer/0 |
| Policía Nacional (SIEDCO), publicado por MinDefensa en datos.gov.co | Bogotá (11001), mes a mes: hurto a personas, residencias, comercio, vehículos, homicidio, lesiones, delitos sexuales, VIF (actualizado 16 sep 2026) | https://www.datos.gov.co/d/4rxi-8m8d · 7mn7-vzqp · 7i2x-h5vp · csb4-y6v2 · m8fd-ahd9 · jr6v-i33g · bz43-8ahq · gepp-dxcs |
| Medicina Legal (INMLCF), presuntos homicidios | 2015-2024 definitivo; 2025-julio 2026 preliminar | https://www.datos.gov.co/d/vtub-3de2 · https://www.datos.gov.co/d/2kpj-cktv |
| Alcaldía de Bogotá, 5 sep 2023 | el hurto a personas iba 23 % por encima de 2022 al 31 de agosto de 2023 | https://bogota.gov.co/mi-ciudad/seguridad/8-de-12-delitos-de-alto-impacto-han-disminuido-en-bogota-durante-2023 |
| ProBogotá, Informe Anual de Seguridad 2024 (SIEDCO al 28 ene 2025) | 2024: −18,2 % frente a 2023, «rompe con el patrón histórico del delito que sólo se había modificado durante el año de la pandemia» (p. 32 del PDF) | https://www.probogota.org/wp-content/uploads/2025/04/Informe-Anual-de-Seguridad-2024.pdf |

Todos los datos se bajan por script; las filas de la Alcaldía y de ProBogotá son citas de contexto, no entran en las tablas. Lo único transcrito a mano son las cifras de la CCB, que el informe publica como etiquetas de gráficos: cada una lleva documento, página y gráfico en `data/crudos/victimizacion_transcritos.csv`, y el PDF queda en `data/crudos/ccb/`.

## 2. Quiebres metodológicos

### ECSC (DANE)

- **Edición frente a año.** La edición N pregunta por la victimización de enero a diciembre del año N-1 (met-ECSC.pdf, p. 35) y por la percepción del momento de la encuesta. En las tablas, `anio` es el año de referencia para victimización y denuncia, y el año de la encuesta para percepción.
- **Huecos.** No hubo productos de la edición 2018 (página de históricos: «durante la vigencia no se generaron productos de difusión»), así que falta 2017. La edición 2023 no se hizo: «Por motivos presupuestales no fue posible realizar la recolección de información para la ronda 2023» (met-ECSC.pdf, p. 7; también bol-ECSC-2024.pdf, p. 2). Falta 2022.
- **Diseño.** De 2014 a 2017, 28 ciudades (área urbana). Desde 2019, muestra nacional con 13 ciudades representativas (cabecera). Las ediciones 2012 y 2013 preguntaban por «los últimos doce meses» y en 2012 Bogotá iba con Soacha: quedan fuera.
- **Momento de campo (el quiebre más serio).** Hasta 2019 el campo se hacía entre febrero y junio del año siguiente al de referencia. Por la pandemia, la edición 2020 se aplazó a agosto-octubre de 2020 (met-ECSC.pdf, p. 7), y desde entonces el campo quedó en el segundo semestre: junio-agosto de 2021, septiembre-noviembre de 2022, octubre-diciembre de 2024, con extensión en Bogotá del 1 de marzo al 29 de abril de 2025 «para fortalecer la cobertura» (p. 35). Más meses entre el hecho y la pregunta suele bajar lo que la gente recuerda. Justo en esa edición la victimización por hurto a personas cae de 17,6 % (2018) a 10,6 % (2019), −7,0 pp (z = −9,1), mientras el registro de la Policía sube 21,8 % ese año. **La serie no es comparable antes y después de 2019.** La subserie comparable es 2019, 2020, 2021 y 2023. En 2023 la pregunta se hizo entre 10 y 28 meses después del hecho, el desfase más largo de la serie.
- **Delitos incluidos.** Desde el año de referencia 2020, la victimización y la denuncia «por cualquier delito» incluyen incidentes de seguridad digital (página vigente de la ECSC). Por eso se publican dos series: `cualquier_delito_sin_isd` (2013-2020) y `cualquier_delito_con_isd` (2020-2023); 2020 sale en ambas. En 2018 la lista trae lesiones personales en vez de riñas. Desde la edición 2022 el hurto de vehículos excluye bicicletas. **El hurto a personas se define igual en todas las ediciones**: por eso es el indicador del contraste.
- **Error.** Los anexos traen el cve de cada porcentaje. El EE se calcula como valor × cve / 100. Para hurto a personas en Bogotá el cve va de 3,3 % a 7,7 % en la victimización y de 4,3 % a 9,0 % en la denuncia: precisión buena para el DANE (5 %-10 %). El total expandido (miles de personas) no trae cve.
- **Qué es «denuncia».** Porcentaje de víctimas de 15 años y más que dicen haber denunciado al menos uno de los hechos ante una autoridad (met-ECSC.pdf, indicador TD). Es lo que la víctima declara, no un registro: incluye denuncias que tal vez nunca quedaron en el SIEDCO.

### Encuesta de Percepción y Victimización (CCB)

- Universo de 18 años y más. Pregunta «En este año, ¿usted ha sido víctima de algún delito?», así que la ventana depende del mes de campo: 4 de junio a 5 de julio en 2024, 2 de septiembre a 10 de noviembre en 2025.
- Cobertura: 19 localidades urbanas en 2024; 20 en 2025, con Sumapaz por primera vez. Muestra: 19.354 (2024) y 20.038 (2025). En 2021 fueron «más 6.500 hogares», según el comunicado del 15 de febrero de 2022.
- Denuncia: hasta 2018, pregunta binaria; desde 2019, por cada delito; desde 2020, promedio de la tasa de cada delito ponderado por su ocurrencia (notas del gráfico, p. 9).
- Error: solo un margen global (1,0 % en 2025; 0,7 % promedio en 2024, al 95 %). No hay EE por indicador ni por año.
- «Denuncia» incluye cualquier autoridad o canal: en 2025, Policía (estación o CAI) 59,3 %, Fiscalía 36,3 %, página web «A denunciar» 8,6 % (p. 11).

### Registro: la capa de la SCJ frente al SIEDCO

Razón SCJ / SIEDCO, enero-agosto, Bogotá. SCJ incluye la fila «Sin localización»; el procesado del proyecto la deja fuera.

| Año | Hurto a personas | Hurto a residencias | Hurto de automotores | Homicidios | Lesiones personales | Delitos sexuales | VIF |
|---|---|---|---|---|---|---|---|
| 2018 | 2,52 | 2,78 | 2,00 | 1,00 | 1,09 | 1,00 | 1,00 |
| 2019 | 2,55 | 2,79 | 2,00 | 1,00 | 1,00 | 1,00 | 1,00 |
| 2020 | 2,41 | 3,00 | 2,00 | 1,02 | 1,00 | 1,00 | 1,00 |
| 2021 | 2,34 | 2,90 | 2,01 | 1,01 | 1,00 | 1,00 | 1,00 |
| 2022 | 2,28 | 2,29 | 1,92 | 1,00 | 1,00 | 1,00 | 1,00 |
| 2023 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 |
| 2024 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 |
| 2025 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 |

- El cambio es solo en algunos hurtos y empieza justo en 2023. La razón exacta de 2,00 en automotores hace pensar en hechos contados dos veces, por ejemplo al sumar dos bases (Policía y Fiscalía) sin deduplicar. Es una hipótesis: la capa no documenta su método, y habría que pedírselo a la OAIEE de la SCJ.
- Lo que la Alcaldía informó en su momento va en la dirección del SIEDCO, no en la de la capa: el 5 de septiembre de 2023 dijo que el hurto a personas iba 23 % por encima de 2022 (la capa hoy dice −40 %). ProBogotá, con el SIEDCO del 28 de enero de 2025, describe la baja de 2024 (−18,2 %) como la primera fuera de la pandemia.
- Hurto a comercio y hurto de motocicletas tampoco coinciden con el SIEDCO en ningún año (razones de 3 a 5 y de 2 a 10): definen distinto y no se usan aquí.
- Precisión sobre la premisa: en la capa de la SCJ no «todos» los hurtos cayeron 40 %-44 % en 2023. Cayeron personas (−40,2 %), residencias (−44,1 %), automotores (−40,1 %), motocicletas (−41,5 %) y celulares (−43,4 %). Comercio (−2,9 %) y bicicletas (−2,4 %) casi no cambiaron.
- El SIEDCO también tiene su propio salto: hurto a personas en Bogotá pasó de 37.954 casos en 2016 a 76.906 en 2017 (año completo). Queda fuera de la ventana de este análisis.

## 3. La serie

### ECSC, Bogotá (cabecera, 15 años y más). Porcentaje y, entre paréntesis, EE en puntos porcentuales

| Año ref. | Edición | Victimización, cualquier delito (sin ISD) | Victimización, cualquier delito (con ISD) | Hurto a personas: victimización | Hurto a personas: denuncia | Víctimas de hurto (miles) | Denunciantes de hurto (miles) | Denuncia, cualquier delito |
|---|---|---|---|---|---|---|---|---|
| 2013 | 2014 | 25,1 (0,79) | sin dato | 16,5 (0,62) | 27,4 (1,58) | 976,2 | 267,1 | 25,5 (1,38) |
| 2014 | 2015 | 23,1 (0,79) | sin dato | 15,3 (0,58) | 22,7 (1,48) | 924,8 | 210,4 | 23,0 (1,36) |
| 2015 | 2016 | 25,0 (0,75) | sin dato | 16,2 (0,57) | 27,1 (1,44) | 993,8 | 269,4 | 25,7 (1,34) |
| 2016 | 2017 | 25,3 (0,79) | sin dato | 16,9 (0,66) | 32,1 (1,64) | 1.057,3 | 339,4 | 32,2 (1,58) |
| 2017 | no hubo | | | | | | | |
| 2018 | 2019 | 26,5 (0,74) | sin dato | 17,6 (0,58) | 37,0 (1,59) | 1.131,2 | 418,0 | 35,2 (1,51) |
| 2019* | 2020 | 15,6 (0,72) | sin dato | 10,6 (0,51) | 37,5 (2,13) | 662,8 | 248,9 | 36,1 (2,13) |
| 2020 | 2021 | 12,2 (0,67) | 14,6 (0,73) | 7,0 (0,47) | 34,3 (3,10) | 448,3 | 153,7 | 32,4 (2,17) con ISD |
| 2021 | 2022 | sin dato | 13,6 (0,61) | 7,3 (0,46) | 36,0 (2,84) | 473,1 | 170,3 | 35,4 (2,14) con ISD |
| 2022 | no hubo | | | | | | | |
| 2023 | 2024 | sin dato | 14,7 (0,87) | 6,9 (0,53) | 42,9 (3,81) | 453,6 | 194,4 | 43,1 (2,80) con ISD |

\* Desde 2019 el campo pasa al segundo semestre del año siguiente: no comparar con 2018 y antes.

Percepción de inseguridad (año de la encuesta): ciudad 69,2 % (2014), 81,6 % (2015), 83,2 % (2016), 81,7 % (2017), 84,0 % (2019), 69,0 % (2020, campo en pandemia), 77,8 % (2021), 83,8 % (2022), 78,7 % (2024). Barrio: 40,4 %, 44,3 %, 44,1 %, 41,5 %, 44,1 %, 32,3 %, 43,0 %, 41,3 %, 39,0 %. EE entre 0,7 y 2,0 pp.

Razones para no denunciar: **la ECSC no las publica para Bogotá**; el cuadro 8 es solo nacional. A nivel nacional, entre las víctimas de hurto a personas que no denunciaron en 2023: «las autoridades no hacen nada» 46,1 % (cve 5,2; anex-ECSC-2024.xlsx, Cuadro 8, M13), «consideró que era innecesario» 18,3 % (M16), «no confía en la administración de justicia» 11,5 % (M14), «faltaban pruebas» 7,0 % (M19).

### CCB, Bogotá (18 años y más)

| Año | Victimización, cualquier delito | % de víctimas que sufrió hurto a personas | Victimización por hurto (calculada) | Denuncia, cualquier delito | Denuncia del hurto a personas |
|---|---|---|---|---|---|
| 2015 | 13,0 | | | 29,1 | |
| 2016 | 18,0 | | | 40,2 | |
| 2017 | 13,5 | | | 35,4 | |
| 2018 | 17,5 | | | 41,1 | |
| 2019 | 14,7 | | | 45,1 | |
| 2020 | 17,0 | | | 35,8 | |
| 2021 | 19,6 | 81,1 | 15,9 | 47,6 | |
| 2022 | 16,7 | 76,8 | 12,8 | 41,1 | 38,6 |
| 2023 | 17,7 | 82,8 | 14,7 | 44,6 | 38,8 |
| 2024 | 15,3 | 76,8 | 11,8 | 52,0 | 51,1 |
| 2025 | 14,9 | 74,7 | 11,1 | 45,6 | 43,2 |

Victimización por hurto calculada = victimización × % de víctimas que sufrió hurto (respuesta múltiple). Razones de no denuncia en 2025 (p. 12): «tras denunciar, las autoridades no hacen nada» 59,9 %, «es difícil denunciar» 16,6 %, «no tengo tiempo» 13,0 %, «no confío en las autoridades» 10,5 %, «no sé cómo se denuncia» 5,9 %.

### Registro de hurto a personas, Bogotá

| Año | SCJ, enero-agosto | SIEDCO, enero-agosto | SIEDCO, año completo |
|---|---|---|---|
| 2018 | 170.219 | 67.633 | 105.964 |
| 2019 | 210.220 | 82.390 | 127.842 |
| 2020 | 128.265 | 53.135 | 83.136 |
| 2021 | 159.153 | 68.077 | 109.428 |
| 2022 | 178.534 | 78.419 | 137.157 |
| 2023 | 106.824 | 106.823 | 158.745 |
| 2024 | 86.196 | 86.196 | 130.504 |
| 2025 | 88.114 | 88.116 | 123.017 |
| 2026 | 75.863 | 75.124 | parcial |

La capa SCJ aquí suma las 21 filas. Con las 20 localidades del procesado del proyecto, 2022 = 178.532 y 2026 = 73.563 (−58,8 %, el 59 % de la pregunta). Con la fila «Sin localización» es −57,5 %.

### Validación externa de homicidios

Homicidios de enero a agosto: SCJ 684, 656, 654, 763, 658, 712, 747, 799 (2018-2025); Medicina Legal 703, 690, 655, 769, 672, 748, 774 y 826 (este último preliminar). La SCJ registra entre 95 % y 100 % de lo que registra Medicina Legal, y las dos series se mueven en la misma dirección todos los años. Tasa anual por 100.000 habitantes (población SDP): Medicina Legal 14,7 (2018), 14,4, 13,5, 14,5, 14,0, 14,3, 15,8 (2024) y 15,2 (2025, preliminar). SIEDCO: 14,4, 13,9, 13,2, 14,4, 12,9, 13,7, 15,3 y 14,9. ProBogotá reporta 15,2 para 2024 con datos SIEDCO. **La serie de homicidios de la SCJ es confiable. La de hurtos antes de 2023, no.**

## 4. Respuesta a la pregunta clave

**Índices con 2022 = 100**

| Serie | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| Registro SCJ, hurto a personas (enero-agosto) | 89,1 | 100 | 59,8 | 48,3 | 49,4 | 42,5 |
| Registro SIEDCO, hurto a personas (enero-agosto) | 86,8 | 100 | 136,2 | 109,9 | 112,4 | 95,8 |
| Registro SIEDCO, hurto a personas (año) | 79,8 | 100 | 115,7 | 95,1 | 89,7 | parcial |
| CCB, victimización por hurto (calculada) | 123,9 | 100 | 114,3 | 91,6 | 86,7 | sin dato |
| CCB, víctimas × tasa de denuncia del hurto | sin dato | 100 | 114,9 | 121,3 | 97,1 | sin dato |
| ECSC, victimización por hurto (%) | 7,3 | sin encuesta | 6,9 | sin dato | sin dato | sin dato |
| ECSC, denuncia del hurto (%) | 36,0 | sin encuesta | 42,9 | sin dato | sin dato | sin dato |

**a) El 59 % es en su mayor parte un artefacto de la serie.** De 2022 a 2026 la capa SCJ cae 57,5 % (58,8 % en el procesado). Toda la diferencia con el SIEDCO aparece en 2023, el año en que la capa cambia de escala. En la serie de la Policía, 2022-2026 es −4,2 %. Cualquier comparación de hurtos de la capa SCJ entre antes y después de 2023 está contaminada.

**b) 2021 frente a 2023 (ECSC, la única encuesta oficial con errores publicados):**
- Victimización por hurto a personas: 7,33 % → 6,86 %, diferencia −0,47 pp (IC 95 % −1,83 a 0,89; z = −0,67; p = 0,50). El boletín del DANE también la marca como no significativa (−0,4 pp; bol-ECSC-2024.pdf, gráfico 4, p. 14).
- Denuncia del hurto a personas: 35,99 % → 42,86 %, +6,87 pp (IC 95 % −2,44 a 16,19; z = 1,45; p = 0,15).
- Denuncia de cualquier delito: 35,4 % → 43,1 %, +7,7 pp (z = 2,19; p = 0,028). El DANE la reporta como significativa (gráfico 11, p. 24).
- En personas: las víctimas de hurto bajan de 473 mil a 454 mil (razón 0,96; IC 95 % aproximado 0,79 a 1,16) y quienes dicen haber denunciado suben de 170 mil a 194 mil (razón 1,14; IC 95 % aproximado 0,84 a 1,55). En el registro, la razón 2023/2021 es 0,67 en la SCJ, fuera del intervalo, y 1,45 en el SIEDCO año completo, dentro (1,57 en enero-agosto, apenas por encima).
- Contrafactual: con la victimización que midió la encuesta, la caída de la SCJ entre 2021 y 2023 exigiría que la denuncia del hurto bajara a 25,2 % en 2023. La ECSC midió 42,9 % (EE 3,81). La hipótesis «cayó la denuncia» queda descartada para ese intervalo.

**c) 2022 frente a 2023 (sin ECSC; solo CCB).** Victimización por cualquier delito 16,7 % → 17,7 %; por hurto, calculada, 12,8 % → 14,7 %; denuncia del hurto 38,6 % → 38,8 %. No hubo ni menos delito ni menos denuncia. Víctimas × denuncia sube 14,9 %, lo mismo que el SIEDCO año completo (+15,7 %). La capa SCJ dice −40 %.

**d) 2023 a 2025: baja real y moderada.** Registro −17,5 % (enero-agosto; las dos series ya coinciden). CCB: victimización por hurto −24 %, denuncia del hurto +4,4 pp, víctimas × denuncia −15,5 %. El delito registrado baja más o menos lo que baja el delito vivido, y la denuncia no cae. Con la cautela de que es una sola encuesta sin EE por indicador, lo que cae desde 2023 es el delito, no la denuncia. Para 2026 solo hay registro: −14,7 % frente a enero-agosto de 2025 en el SIEDCO.

**Conclusión.** La pregunta «¿cayó el delito o cayó la denuncia?» tiene una tercera respuesta: cambió el registro. La caída de 2023 en la capa de la SCJ no aparece en el registro de la Policía ni en las dos encuestas. Desde 2023 el registro baja 17,5 % hasta 2025 y 29,7 % hasta enero-agosto de 2026, y la encuesta de la CCB acompaña esa baja con menos victimización y una denuncia estable o mayor. Frente a 2022, el registro de la Policía de 2026 está 4 % abajo y la victimización por hurto de la CCB en 2025, 13 % abajo: nada parecido a −59 %.

## 5. Problemas y límites

- La ECSC no tiene 2022 (no se hizo) ni 2024-2026 (no publicada al 6 de octubre de 2026). El contraste formal es 2021 frente a 2023, no 2022 frente a 2023.
- El quiebre de 2019 en la ECSC impide usar su serie larga: la caída de 17,6 % a 10,6 % coincide con el cambio de calendario de campo en pandemia, no con el registro, que sube ese año.
- En 2023 la recordación es de 10 a 28 meses y Bogotá necesitó extender el campo. Si eso sesga, sesga hacia menos victimización declarada, lo que refuerza que el delito no cayó entre 2021 y 2023.
- La ECSC mide personas víctimas (prevalencia, cabecera, 15 años y más). El registro mide hechos (incidencia, toda la ciudad). Revictimización, varios objetos por hecho y denuncias de no residentes separan las dos medidas. Por eso se comparan razones entre años, no niveles.
- La «denuncia» de las encuestas es declarada y ante cualquier autoridad. No equivale a una noticia criminal registrada.
- Los IC de los totales en personas son aproximados: método delta con el cv de cada porcentaje, sin covarianza y sin error de la proyección de población. El DANE no publica el cve del total.
- Las cifras de la CCB vienen de etiquetas de gráficos. Se verificaron contra los comunicados donde coinciden (2023, 2024, 2025), y el comunicado de 2022 redondeaba la denuncia de 2021 a 49 % frente a 47,6 % del informe de 2025: se usó el informe más reciente.
- El tamaño de muestra de la ECSC en Bogotá no está en los anexos. La metodología da 311 segmentos de unas 10 viviendas para la ronda 2024 (p. 39). El n exacto exige los microdatos (catálogo 894), que no se bajaron.
- El método de la capa SCJ para 2018-2022 no está documentado. La lectura de «suma sin deduplicar» es una hipótesis.

## 6. Implicaciones para el resto del proyecto (no se cambió ningún archivo ajeno)

- El README dice que «el hurto a personas bajó 65 % entre enero-agosto de 2019 y de 2026». Con el SIEDCO, el cambio es de 82.390 a 75.124 casos (−8,8 %). Cualquier gráfica o cifra de tendencia de hurtos que use la capa SCJ antes de 2023 (por ejemplo `outputs/figuras/fig1_serie_delitos.png`) hereda el quiebre.
- Los cortes transversales de 2025 por localidad no se afectan: desde 2023 la capa SCJ coincide con el SIEDCO a nivel de ciudad.
- Recomendación: para series de tiempo de hurtos usar el SIEDCO de datos.gov.co, o la capa SCJ solo desde 2023. Pedir a la OAIEE de la SCJ la nota metodológica de las columnas 2018-2022.

## 7. Reproducir

```
python src/fuentes_victimizacion.py            # usa la caché de data/crudos/
python src/fuentes_victimizacion.py --forzar   # vuelve a bajar todo
```

El script verifica la extracción contra el boletín ECSC 2024 (victimización 14,7 %, hurto a personas 6,9 %, denuncia 43,1 % y percepción en la ciudad 78,7 % para Bogotá) e imprime el título de cada cuadro leído.
