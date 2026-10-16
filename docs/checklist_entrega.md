# Lista de verificación de la entrega

Cada requisito de los términos de referencia (TdR) y de la ficha metodológica, con el lugar donde se cumple.

## Entregables obligatorios

| Requisito | Dónde | Estado |
|---|---|---|
| Repositorio en GitHub/GitLab con /data, /notebooks o /scripts, /outputs, /docs y README | raíz del repositorio | ✔ |
| README: problema, fuentes, metodología, ejecución, despliegue, estructura | `README.md` (secciones 1 a 7) | ✔ |
| Notebook Python documentado y reproducible | `notebooks/el_miedo_que_no_baja.ipynb` (ejecutado) y `src/pipeline.py` | ✔ |
| Integración efectiva de mínimo 3 fuentes públicas | 18 fuentes con score de confiabilidad: 7 de núcleo (SCJ, SDP, SCRD, EMV, UAESP, DADEP, IDECA) y 11 de validación y frentes (Policía/SIEDCO, Medicina Legal, DANE, CCB, SIVIM, Secretaría de la Mujer, Veeduría, Secretaría General, Movilidad, IDU, serie de alumbrado UAESP); secciones 2 a 5 y 11.1 del notebook | ✔ |
| Evidencia de limpieza, transformación y cruce | sección 3 del notebook y `outputs/tablas/bitacora_limpieza.csv` | ✔ |
| Archivo de dependencias | `requirements.txt` y `visor/package.json` | ✔ |
| Visualización que muestre la brecha, con lectura territorial, exportable | visor web desplegado + `powerbi/` (.pbix adjunto al correo) + CSV/GeoJSON en `visor/public/descargas/` y `outputs/geo/` | ✔ (.pbix por actualizar) |
| Formulario de caracterización oficial diligenciado | `docs/Formulario_caracterizacion_The_data_squad.docx` (y PDF), adjunto al correo | ✔ (confirmar roles y correo) |
| Nota técnica de 1 página | `docs/Nota_tecnica_integracion_datos_The_data_squad.pdf` | ✔ |
| (Adicional) Libro de datos en Excel | `docs/Libro_de_datos_El_miedo_que_no_baja.xlsx` | ✔ |
| (Adicional) Presentación del pitch | `docs/pitch/` (PPTX con notas y PDF) y `/presentar` en el visor | ✔ |

## Lineamientos (TdR, numeral 10)

| Requisito | Cómo se cumple |
|---|---|
| Problema a escala de ciudad, con recomendaciones aplicables a todo el Distrito | 19 localidades urbanas; recomendaciones distritales; el índice escala a las 33 UPL con la EDP |
| Indicadores medibles, comparables y consistentes en el tiempo | Índice de Brecha de Seguridad con ficha técnica (`docs/ficha_indicador.md`); series 2018-2026 validadas contra la Policía y Medicina Legal, con la ventana comparable de cada delito |
| Enfoque de género (valorado) | sección 8 del notebook y página Género del visor |

## Criterios de evaluación

| Criterio (peso) | Evidencia principal |
|---|---|
| Pertinencia (20) | Problema distrital con cifra, pregunta e hipótesis explícitas; entidades responsables identificadas |
| Rigor e integración (20) | Validación cruzada del registro (quiebre de la serie de hurtos en 2023); score de confiabilidad de 18 fuentes; auditoría ideal frente a disponible; llave territorial; tasas con población SDP; bitácora |
| Calidad técnica (20) | Binomial negativa de panel; logit ponderado con efectos marginales e IC por bootstrap; wild cluster bootstrap; aprendizaje supervisado (bosque aleatorio, gradient boosting) y no supervisado (PCA y Ward); corrección Benjamini-Hochberg; IBS con incertidumbre |
| Solidez (20) | Marcador de 8 hipótesis (3 se sostienen y 5 no); resultados nulos reportados; limitaciones explícitas; respuestas preparadas (`docs/pitch/guion_pitch.md`) |
| Visualización (10) | Visor con mapas, simulador, modo presentación y descargas; Power BI; libro de Excel; pitch |
| Uso estratégico de datos (10) | Dos de las tres encuestas que la SDP llamó fundamentales, con factor de expansión; auditoría del portal completo en la nota técnica |

## Antes de enviar (16 de octubre, plazo 11:59 p. m.)

- [ ] Confirmar roles, programas y correo de contacto en el formulario.
- [ ] Repositorio público (o con acceso habilitado al jurado) y enlace probado en una ventana privada.
- [ ] Alguien que no escribió el código clona el repositorio, instala `requirements.txt` y corre `python src/pipeline.py` sin errores.
- [ ] Visor abre con la clave en un navegador limpio; la clave va en el cuerpo del correo.
- [ ] `.pbix` actualizado con la serie validada (abrir el `.pbip`, Actualizar, Guardar como `.pbix`) y adjunto al correo.
- [ ] Adjuntar también el informe técnico completo (`docs/Informe_tecnico_El_miedo_que_no_baja.pdf`, 15 páginas).
- [ ] Releer la corrección de H2 antes del pitch: la correlación de 0,72 entre el Índice de Brecha y la cifra oculta es mecánica (parcial −0,02); se presenta como hipótesis no sostenida.
- [ ] Correo con el asunto exacto «DataJam – Entrega final – The data squad», enviado el 16 antes de las 11:59 p. m. (mejor con margen).
