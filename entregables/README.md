# Entregables · El miedo que no baja

**Bogotá DataJam Edición 5 (2026) · Equipo #16 The data squad**
Brandow Brusly León Rodríguez (análisis de políticas públicas), Samuel Esteban Riveros Cubides (experto temático) y Rafael Estiven Londoño Camacho (análisis de datos), estudiantes de Ciencia de Datos.

Todo lo que entregamos, en un solo lugar. Esta carpeta reúne los documentos; el código está en el resto del repositorio.

## Enlaces

| | Enlace |
|---|---|
| Visor interactivo desplegado | https://el-miedo-que-no-baja.vercel.app (la clave va en el correo de entrega) |
| Video de 4 minutos, con capítulos, explicación de cada parte y transcripción sincronizada | https://el-miedo-que-no-baja.vercel.app/video |
| Especificación de cada modelo, con incertidumbre y límites | https://el-miedo-que-no-baja.vercel.app/modelos |
| Reproducción completa en Google Colab | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rlondono1620-max/el-miedo-que-no-baja/blob/main/notebooks/colab_reproducir.ipynb) |

## Documentos frente a los términos de referencia

| Requisito | Entregable | Archivo |
|---|---|---|
| 11.1 Repositorio técnico | Estructura `data/`, `notebooks/`, `src/`, `outputs/`, `docs/`, README y `requirements.txt` | [README del proyecto](../README.md) |
| 11.2 Producto analítico reproducible | Notebook ejecutado de punta a punta y pipeline con semillas fijas | [`notebooks/el_miedo_que_no_baja.ipynb`](../notebooks/el_miedo_que_no_baja.ipynb) · [`notebooks/colab_reproducir.ipynb`](../notebooks/colab_reproducir.ipynb) · [`src/pipeline.py`](../src/pipeline.py) |
| 11.3 Visualización | Tablero de Power BI (`.pbix`, y su proyecto `.pbip` editable en [`powerbi/`](../powerbi)) y visor desplegado con descargas CSV y GeoJSON | [ElMiedoQueNoBaja.pbix](ElMiedoQueNoBaja.pbix) |
| 11.4 Formulario de caracterización | Formulario oficial diligenciado | [DOCX](Formulario_caracterizacion_The_data_squad.docx) · [PDF](Formulario_caracterizacion_The_data_squad.pdf) |
| 11.5 Nota técnica (máximo 1 página) | Disponibilidad, integración, limitaciones y recomendaciones | [PDF](Nota_tecnica_integracion_datos_The_data_squad.pdf) |
| Adicional | Informe técnico completo (15 páginas): hipótesis, validación del registro, métodos, resultados con intervalos, estrategias y trazabilidad de cada cifra | [PDF](Informe_tecnico_El_miedo_que_no_baja.pdf) · [Word](Informe_tecnico_El_miedo_que_no_baja.docx) |
| Adicional | Libro de datos en Excel con tablas nombradas, fórmulas vivas y simulador | [XLSX](Libro_de_datos_El_miedo_que_no_baja.xlsx) |
| Jornada final | Presentación del pitch (respaldo sin internet; la versión interactiva está en `/presentar` del visor) | [PDF](Pitch_El_miedo_que_no_baja_The_data_squad.pdf) · [PPTX](Pitch_El_miedo_que_no_baja_The_data_squad.pptx) |

## Cómo reproducirlo

```bash
git clone https://github.com/rlondono1620-max/el-miedo-que-no-baja.git && cd el-miedo-que-no-baja
pip install -r requirements.txt
python src/pipeline.py
```

O sin instalar nada, con el botón de Colab de arriba. Las semillas están fijas: dos corridas dan las mismas cifras.

*Proyecto académico presentado al Bogotá DataJam 2026 (Secretaría General de la Alcaldía Mayor de Bogotá y Universidad Compensar). No es un documento oficial de la Alcaldía de Bogotá ni de sus entidades.*
