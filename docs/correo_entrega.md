# Correo de entrega

**Para:** comunigab@alcaldiabogota.gov.co
**Asunto:** DataJam – Entrega final – The data squad
**Plazo:** viernes 16 de octubre de 2026, 11:59 p. m. (hora Colombia). Un solo correo; después del plazo no se admiten cambios.

**Adjuntos:**
- `Formulario_caracterizacion_The_data_squad.docx` y su PDF (formulario oficial diligenciado)
- `Nota_tecnica_integracion_datos_The_data_squad.pdf` (1 página)
- `ElMiedoQueNoBaja.pbix` (archivo fuente del tablero de Power BI)
- `Libro_de_datos_El_miedo_que_no_baja.xlsx` (adicional: cifras con fórmulas vivas y simulador)
- `Informe_tecnico_El_miedo_que_no_baja.pdf` y `.docx` (adicional: informe técnico completo)

**Antes de enviar:** el repositorio debe estar público y el enlace debe abrir en una ventana privada.

---

Buen día, equipo DIPEA:

Enviamos la entrega final del equipo **The data squad** (#16) para el Bogotá DataJam Edición 5: «El miedo que no baja: inseguridad percibida y delito registrado en Bogotá».

**Integrantes:** Brandow Brusly León Rodríguez, Samuel Esteban Riveros Cubides y Rafael Estiven Londoño Camacho, estudiantes de Ciencia de Datos.

**1. Repositorio técnico:** https://github.com/rlondono1620-max/el-miedo-que-no-baja

Contiene el notebook reproducible ya ejecutado (`notebooks/el_miedo_que_no_baja.ipynb`), los scripts (`src/`), los datos (`data/`), los resultados (`outputs/`), el tablero de Power BI (`powerbi/`), la documentación (`docs/`), el archivo de dependencias (`requirements.txt`) y el README con el problema, las fuentes, la metodología y las instrucciones de ejecución y despliegue. Todo se reproduce con `python src/pipeline.py`, o sin instalar nada en [Google Colab](https://colab.research.google.com/github/rlondono1620-max/el-miedo-que-no-baja/blob/main/notebooks/el_miedo_que_no_baja_colab.ipynb).

La carpeta [`entregables/`](https://github.com/rlondono1620-max/el-miedo-que-no-baja/tree/main/entregables) reúne en carpetas numeradas todo lo entregado: Power BI (.pbix y proyecto editable), análisis en Python y Google Colab, informe técnico en Word y PDF, nota técnica, formulario, Excel, video y presentación, con una tabla que los relaciona con cada requisito de los términos de referencia.

**2. Visualización desplegada:** https://el-miedo-que-no-baja.vercel.app (clave de acceso: **[CLAVE]**)

Muestra la brecha por localidad, con mapas, tendencias validadas, índice, simulador y descargas en CSV y GeoJSON para visores institucionales. La página **Entregables** reúne todos los documentos y **Presentar** es la sustentación interactiva.

- Video de 4 minutos, con capítulos y transcripción sincronizada: https://el-miedo-que-no-baja.vercel.app/video
- Especificación de cada modelo, con incertidumbre y límites: https://el-miedo-que-no-baja.vercel.app/modelos

**3. Adjuntos:** formulario de caracterización (DOCX y PDF), nota técnica sobre integración de datos públicos (PDF), archivo fuente del tablero (`.pbix`), libro de datos en Excel e informe técnico completo (PDF y Word).

Un punto que quisimos documentar con cuidado: antes de modelar validamos cada serie contra una fuente independiente. La serie abierta de hurtos de 2018-2022 no es comparable con la de 2023 en adelante (vale entre 2,3 y 2,6 veces el registro de la Policía). Lo dejamos en la nota técnica como recomendación de documentación, no como evaluación de ninguna entidad. También reportamos las hipótesis que no se sostienen: de ocho, dos se sostienen y seis no, y cada veredicto trae su prueba; el informe explica cómo cada descarte cambió el paso siguiente (sección 6.9). Cerramos con una propuesta: un sistema unificado donde la ciudadanía registre hurtos, violencias y hechos del entorno, y que cruce de forma automática y mensual las fuentes que hoy están separadas, para que el Distrito tenga este análisis siempre al día (sección 7.2).

Quedamos atentos a cualquier inquietud.

Cordialmente,
The data squad
