# Correo de entrega

**Para:** comunigab@alcaldiabogota.gov.co
**Asunto:** DataJam – Entrega final – The data squad
**Plazo:** jueves 16 de octubre de 2026, 11:59 p. m. (hora Colombia). Un solo correo; después del plazo no se admiten cambios.

**Adjuntos:**
- `Formulario_caracterizacion_The_data_squad.docx` y su PDF (formulario oficial diligenciado)
- `Nota_tecnica_integracion_datos_The_data_squad.pdf` (1 página)
- `ElMiedoQueNoBaja.pbix` (archivo fuente del tablero de Power BI)
- `Libro_de_datos_El_miedo_que_no_baja.xlsx` (adicional: cifras con fórmulas vivas y simulador)

**Antes de enviar:** el repositorio debe estar público y el enlace debe abrir en una ventana privada.

---

Buen día, equipo DIPEA:

Enviamos la entrega final del equipo **The data squad** (#16) para el Bogotá DataJam Edición 5: «El miedo que no baja: inseguridad percibida y delito registrado en Bogotá».

**Integrantes:** Rafael Estiven Londoño Camacho, Brandow Brusly León Rodríguez y Samuel Esteban Riveros Cubides.

**1. Repositorio técnico:** https://github.com/rlondono1620-max/el-miedo-que-no-baja

Contiene el notebook reproducible ya ejecutado (`notebooks/el_miedo_que_no_baja.ipynb`), los scripts (`src/`), los datos (`data/`), los resultados (`outputs/`), el tablero de Power BI (`powerbi/`), la documentación (`docs/`), el archivo de dependencias (`requirements.txt`) y el README con el problema, las fuentes, la metodología y las instrucciones de ejecución y despliegue. Todo se reproduce con `python src/pipeline.py`.

**2. Visualización desplegada:** https://el-miedo-que-no-baja.vercel.app (clave de acceso: **[CLAVE]**)

Muestra la brecha por localidad, con mapas, tendencias validadas, índice, simulador y descargas en CSV y GeoJSON para visores institucionales. La página **Entregables** reúne todos los documentos y **Presentar** es la sustentación interactiva.

**3. Adjuntos:** formulario de caracterización (DOCX y PDF), nota técnica sobre integración de datos públicos (PDF), archivo fuente del tablero (`.pbix`) y libro de datos en Excel.

Un punto que quisimos documentar con cuidado: antes de modelar validamos cada serie contra una fuente independiente. La serie abierta de hurtos de 2018-2022 no es comparable con la de 2023 en adelante (vale entre 2,3 y 2,6 veces el registro de la Policía). Lo dejamos en la nota técnica como recomendación de documentación, no como evaluación de ninguna entidad.

Quedamos atentos a cualquier inquietud.

Cordialmente,
The data squad
