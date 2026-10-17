# Entregables · El miedo que no baja

**Bogotá DataJam Edición 5 (2026) · Equipo #16 The data squad**
Brandow Brusly León Rodríguez, Samuel Esteban Riveros Cubides y Rafael Estiven Londoño Camacho, estudiantes de Ciencia de Datos.

Todo lo que entregamos, en una sola carpeta: el tablero de Power BI, el análisis en Python y Colab, los documentos, el video y la presentación.
El código fuente está en el resto del repositorio.

| Carpeta | Qué hay | Requisito |
|---|---|---|
| [`1_Power_BI/`](1_Power_BI/) | `ElMiedoQueNoBaja.pbix` (abre con los datos cargados) y el proyecto editable `.pbip` con su modelo, informe, datos y tema | 11.3 Visualización |
| [`2_Python_y_Colab/`](2_Python_y_Colab/) | Análisis completo en Google Colab (código sin comentarios, explicación en texto, resultados guardados), cuaderno de reproducción rápida y notebook principal ejecutado | 11.2 Producto analítico reproducible |
| [`3_Informe_tecnico/`](3_Informe_tecnico/) | Informe técnico completo de 16 páginas en PDF y Word: hipótesis, validación del registro, métodos, resultados con intervalos, por qué solo dos de ocho hipótesis se sostienen, estrategias, propuesta final de sistema unificado y trazabilidad de cada cifra; además, un documento aparte con la propuesta final y el recorrido de las hipótesis | Adicional |
| [`4_Nota_tecnica/`](4_Nota_tecnica/) | Nota técnica de una página: disponibilidad, integración, limitaciones y recomendaciones | 11.5 Nota técnica |
| [`5_Formulario_caracterizacion/`](5_Formulario_caracterizacion/) | Formulario oficial diligenciado, en DOCX y PDF | 11.4 Formulario |
| [`6_Libro_de_datos_Excel/`](6_Libro_de_datos_Excel/) | Libro de Excel con tablas nombradas, fórmulas vivas y simulador | Adicional |
| [`7_Video/`](7_Video/) | Video explicativo de 4 minutos (MP4) y su transcripción | Adicional |
| [`8_Presentacion_pitch/`](8_Presentacion_pitch/) | Presentación del pitch en PDF y PPTX con notas del orador (respaldo sin internet de `/presentar`) | Jornada final |

El repositorio completo responde al requisito 11.1: `data/`, `notebooks/`, `src/`, `outputs/`, `docs/`, `powerbi/`, README y `requirements.txt` ([README del proyecto](../README.md)).

## Enlaces

| | Enlace |
|---|---|
| Visor interactivo desplegado | https://el-miedo-que-no-baja.vercel.app (la clave va en el correo de entrega) |
| Video con capítulos, explicación de cada parte y transcripción sincronizada | https://el-miedo-que-no-baja.vercel.app/video |
| Especificación de cada modelo, con incertidumbre y límites | https://el-miedo-que-no-baja.vercel.app/modelos |
| Análisis completo en Google Colab | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rlondono1620-max/el-miedo-que-no-baja/blob/main/notebooks/el_miedo_que_no_baja_colab.ipynb) |

## Cómo reproducirlo

```bash
git clone https://github.com/rlondono1620-max/el-miedo-que-no-baja.git && cd el-miedo-que-no-baja
pip install -r requirements.txt
python src/pipeline.py
```

O sin instalar nada, con el botón de Colab. Las semillas están fijas: dos corridas dan las mismas cifras.

*Proyecto académico presentado al Bogotá DataJam 2026 (Secretaría General de la Alcaldía Mayor de Bogotá y Universidad Compensar). No es un documento oficial de la Alcaldía de Bogotá ni de sus entidades.*
