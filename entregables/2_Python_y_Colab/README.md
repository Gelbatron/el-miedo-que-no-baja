# Python y Google Colab

Todo el análisis está en Python y corre en Google Colab sin instalar nada.

| Cuaderno | Para qué sirve | Abrir en Colab |
|---|---|---|
| `el_miedo_que_no_baja_colab.ipynb` | **El análisis completo**, paso a paso, con el código sin comentarios y la explicación en celdas de texto. Ya trae los resultados guardados. | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rlondono1620-max/el-miedo-que-no-baja/blob/main/notebooks/el_miedo_que_no_baja_colab.ipynb) |
| `colab_reproducir.ipynb` | Reproducción rápida: clona el repositorio, instala dependencias, corre `src/pipeline.py` y muestra las tablas y figuras clave. | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rlondono1620-max/el-miedo-que-no-baja/blob/main/notebooks/colab_reproducir.ipynb) |
| `el_miedo_que_no_baja.ipynb` | El notebook principal del repositorio, ejecutado de punta a punta (versión de trabajo local). | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rlondono1620-max/el-miedo-que-no-baja/blob/main/notebooks/el_miedo_que_no_baja.ipynb) |

## Cómo usamos Colab

1. Las primeras celdas clonan el repositorio público (que ya trae los datos) e instalan `requirements.txt`.
2. Cada celda reproduce un paso del método: inventario de las fuentes, limpieza y unión por código de localidad, validación del registro
   contra la Policía y Medicina Legal, tendencias, modelo explicativo, machine learning, tipología, cifra oculta, Índice de Brecha y enfoque de género.
3. Para reproducirlo: **Entorno de ejecución → Ejecutar todas**. Las semillas están fijas: dos corridas dan las mismas cifras.

El código fuente completo está en la carpeta [`src/`](https://github.com/rlondono1620-max/el-miedo-que-no-baja/tree/main/src) del repositorio; `python src/pipeline.py` corre todo de una vez.
