# Lista de verificación de la entrega

Cada requisito de los términos de referencia (TdR) y de la ficha metodológica, con el lugar donde se cumple.

## Entregables obligatorios

| Requisito | Dónde | Estado |
|---|---|---|
| Repositorio en GitHub/GitLab con /data, /notebooks o /scripts, /outputs, /docs y README | raíz del repositorio | ✔ |
| README: problema, fuentes, metodología, ejecución, despliegue, estructura | `README.md` (secciones 1 a 7) | ✔ |
| Notebook Python documentado y reproducible | `notebooks/el_miedo_que_no_baja.ipynb` (ejecutado) y `src/pipeline.py` | ✔ |
| Integración efectiva de mínimo 3 fuentes públicas | 7 fuentes (SCJ, SDP, SCRD, EMV, UAESP, DADEP, IDECA), secciones 2 a 4 del notebook | ✔ |
| Evidencia de limpieza, transformación y cruce | sección 3 del notebook y `outputs/tablas/bitacora_limpieza.csv` | ✔ |
| Archivo de dependencias | `requirements.txt` y `visor/package.json` | ✔ |
| Visualización que muestre la brecha, con lectura territorial, exportable | visor web desplegado + `powerbi/` + CSV/GeoJSON en `visor/public/descargas/` y `outputs/geo/` | ✔ |
| Formulario de caracterización oficial diligenciado | `docs/Formulario_caracterizacion_The_data_squad.docx` (y PDF) | ✔ (confirmar roles y correo) |
| Nota técnica de 1 página | `docs/Nota_tecnica_integracion_datos_The_data_squad.pdf` | ✔ |

## Lineamientos (TdR, numeral 10)

| Requisito | Cómo se cumple |
|---|---|
| Problema a escala de ciudad, con recomendaciones aplicables a todo el Distrito | 19 localidades urbanas; recomendaciones distritales; el índice escala a las 33 UPL con la EDP |
| Indicadores medibles, comparables y consistentes en el tiempo | Índice de Brecha de Seguridad con ficha técnica (`docs/ficha_indicador.md`); series de la SCJ 2018-2026 con el mismo corte |
| Enfoque de género (valorado) | sección 8 del notebook y página Género del visor |

## Criterios de evaluación

| Criterio (peso) | Evidencia principal |
|---|---|
| Pertinencia (20) | Problema distrital con cifra, pregunta e hipótesis explícitas; entidades responsables identificadas |
| Rigor e integración (20) | Auditoría ideal frente a disponible; llave territorial; tasas con población SDP; bitácora; validación del cruce de la EMV |
| Calidad técnica (20) | Logit ponderado con efectos marginales e IC por bootstrap; efectos fijos; wild cluster bootstrap; AUC fuera de muestra; corrección Benjamini-Hochberg; IBS con incertidumbre |
| Solidez (20) | Resultados nulos reportados; limitaciones explícitas; respuestas preparadas (`docs/pitch/guion_pitch.md`) |
| Visualización (10) | Visor con mapas, simulador y descargas; Power BI; pitch |
| Uso estratégico de datos (10) | Dos de las tres encuestas que la SDP llamó fundamentales, con factor de expansión; auditoría del portal completo en la nota técnica |

## Antes de enviar (15 de octubre)

- [ ] Confirmar roles, programas y correo de contacto en el formulario.
- [ ] Repositorio público (o con acceso habilitado al jurado) y enlace probado en una ventana privada.
- [ ] Alguien que no escribió el código clona el repositorio, instala `requirements.txt` y corre `python src/pipeline.py` sin errores.
- [ ] Visor abre con la clave en un navegador limpio; la clave va en el cuerpo del correo.
- [ ] Power BI abre con la ruta de datos correcta (o .pbix adjunto).
- [ ] Correo con el asunto exacto, enviado el 16 antes de las 6 p. m.
