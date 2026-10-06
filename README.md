# El miedo que no baja

**Inseguridad percibida y delito registrado en Bogotá.**
Bogotá DataJam Edición 5 (2026) · Equipo #16 **The data squad**: Rafael Estiven Londoño Camacho, Brandow Brusly León Rodríguez y Samuel Esteban Riveros Cubides.

| Entregable | Dónde |
|---|---|
| Notebook reproducible | [`notebooks/el_miedo_que_no_baja.ipynb`](notebooks/el_miedo_que_no_baja.ipynb) (ejecutado, con salidas) |
| Visor interpretativo (web) | https://el-miedo-que-no-baja.vercel.app (clave en el correo de entrega) · código en [`visor/`](visor/) |
| Tablero Power BI | [`powerbi/`](powerbi/) |
| Formulario de caracterización | [`docs/Formulario_caracterizacion_The_data_squad.docx`](docs/) |
| Nota técnica (1 página) | [`docs/Nota_tecnica_integracion_datos_The_data_squad.pdf`](docs/) |
| Datos exportables (CSV, GeoJSON) | [`visor/public/descargas/`](visor/public/descargas/) y [`outputs/`](outputs/) |

![Delitos registrados frente a percepción](outputs/figuras/fig1_serie_delitos.png)

## 1. Problema

Bogotá redujo de forma marcada los delitos contra el patrimonio que registra la Secretaría de Seguridad: el hurto a personas bajó 65 % entre enero-agosto de 2019 y de 2026. Pero el 74 % de los adultos califica la ciudad como insegura y el 48 % dice lo mismo de su propia zona (Encuesta Bienal de Cultura Ciudadana 2025). La política se planea y se evalúa con el delito registrado, que no capta el delito que no se denuncia ni lo que forma la sensación de inseguridad.

**Pregunta analítica.** ¿Por qué la inseguridad percibida no baja cuando el delito registrado sí, y en qué territorios debe intervenir primero el Distrito?

**Hipótesis.**
- **H1.** La percepción del barrio depende más del entorno inmediato que del delito registrado en la localidad.
- **H2.** Parte de la distancia entre miedo y registro es subregistro: donde hay más miedo que delito registrado, más delito queda fuera de las cifras.
- **H3.** A igual victimización, las mujeres restringen más su vida y temen más el acoso sexual.

## 2. Hallazgos

1. **La ciudad no ve buena parte de su delito.** Hay unas 5,6 víctimas (EMV 2024) por cada delito de alto impacto registrado (SCJ). La razón va de 10,6 en Bosa a 0,7 en Los Mártires. El Índice de Brecha de Seguridad crece donde más se subregistra: Spearman ρ = 0,72 (IC 95 % 0,41 a 0,88; p ajustado por pruebas múltiples = 0,004). Es la única relación territorial que sobrevive a la corrección.
2. **El barrio se siente por lo que pasa en él.** Ver atracos en el parque cercano suma +13,3 pp a la probabilidad de sentir insegura la zona (IC 6,2 a 17,5), y los conflictos vecinales hasta +14,7 pp. El hurto registrado de la localidad no tiene efecto (wild cluster bootstrap p = 0,92) y no mejora la predicción: AUC 0,609 → 0,611. El entorno sí: 0,655 con hechos y 0,782 con todo.
3. **Las mujeres pagan el miedo con autonomía.** A igual edad, estrato y victimización, las mujeres tienen +18,0 pp de temor al acoso sexual, +6,5 pp de evitar salir de noche y +9,3 pp de sentirse inseguras en su barrio, aunque reportan menos victimización (20,6 % frente a 28,4 %).
4. **Prioridad territorial.** Usme, Ciudad Bolívar, Bosa, Kennedy y San Cristóbal tienen el mayor Índice de Brecha y quedan en el top 5 en más del 90 % de las réplicas bootstrap.

**Recomendaciones.**
- Medir la seguridad con victimización (Encuesta Distrital de Percepción por UPL) y no solo con registros.
- Ejecutar un programa de entornos que se sienten seguros (parques sin atracos, mediación de conflictos vecinales, alumbrado), priorizado con el Índice de Brecha.
- Adoptar «% de mujeres que evita salir de noche» como indicador de resultado de la política de seguridad.
- Publicar el inventario georreferenciado de alumbrado y los delitos por UPZ.

## 3. Fuentes de datos

| Fuente | Entidad | Uso |
|---|---|---|
| [Delito de Alto Impacto. Bogotá D.C.](https://datosabiertos.bogota.gov.co/dataset/delito-de-alto-impacto-bogota-d-c) | Secretaría Distrital de Seguridad, Convivencia y Justicia | 11 delitos por localidad, enero-agosto 2018-2026 |
| [Incidentes reportados a la Línea 123](https://oaiee.scj.gov.co/agc/rest/services/Tematicos_Pub/CifrasSCJ/MapServer) | SCJ | Llamadas por narcóticos, riñas y maltrato a mujer, por localidad y UPZ |
| [Proyecciones de población 2005-2035](https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035) | Secretaría Distrital de Planeación | Denominadores por localidad, UPZ, sexo y edad |
| [Encuesta Bienal de Cultura Ciudadana 2025](https://observatoriocultura.github.io/observatorio/#/ebc/encuesta-cultura-ciudadana-2025) | Secretaría de Cultura, Recreación y Deporte | Microdatos: percepción y entorno (5.538 adultos) |
| [Encuesta Mundial de Valores ola 8, 2024](https://gobiernoabiertobogota.gov.co/transparencia) | Secretaría General · Datos para la Transparencia | Microdatos: victimización y género (1.824 en Bogotá) |
| [Alumbrado público por localidad](https://datosabiertos.bogota.gov.co/dataset/alumbrado_publico_lt) | UAESP | Validación (último corte publicado: agosto 2019) |
| [Indicador de espacio público](https://datosabiertos.bogota.gov.co/dataset/indicador-espacio-publico-localidad-bogota-d-c) | DADEP | Contexto |
| [Localidad. Bogotá D.C.](https://datosabiertos.bogota.gov.co/dataset/localidad-bogota-d-c) | UAECD · IDECA | Límites |

La localidad de cada registro de la EMV no viene en el archivo publicado. Se recuperó del tablero oficial de Datos para la Transparencia (`data/crudos/emv_localidad_por_registro.csv`) y se verificó: 96 encuestas por localidad, como dice la ficha técnica.

## 4. Metodología

1. **Auditoría de datos.** Variable ideal frente a variable disponible, con proxy y limitación (sección 1 del notebook).
2. **Limpieza** por fuente con bitácora (`outputs/tablas/bitacora_limpieza.csv`):
   - formato ancho a largo;
   - normalización de la localidad al código oficial 1-20;
   - recodificación de escalas;
   - controles de totales.
3. **Integración** por código de localidad, con tasas por 100.000 habitantes (población SDP). A cada persona de la Bienal se le asigna el delito y las llamadas 123 de su localidad.
4. **Diagnóstico.** Logit ponderado con el factor de expansión, efectos marginales promedio en puntos porcentuales e IC 95 % por bootstrap de localidades.
   - **Modelo principal:** solo hechos del entorno, para evitar el sesgo de método común.
   - **Robustez:** efectos fijos de localidad, modelo lineal con wild cluster bootstrap (pesos de Webb) y otros dos resultados.
5. **Predictivo.** AUC fuera de muestra por bloques de variables, con validación cruzada estratificada repetida.
6. **Género.** Efecto de ser mujer con controles de victimización (EMV).
7. **Territorio.**
   - Validaciones con Spearman y corrección de Benjamini-Hochberg.
   - Cifra oculta.
   - **Índice de Brecha de Seguridad** = z(% zona insegura) − z(ln delitos de alto impacto por 100.000), con intervalos bootstrap.
8. **Prescriptivo.** Escenarios del modelo (alumbrado y parques sin atracos) por localidad y sexo.

## 5. Cómo ejecutarlo

Requisitos: Python 3.11 o superior. El visor necesita además Node 20 o superior.

```bash
git clone <url-del-repositorio> && cd el-miedo-que-no-baja
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Opción A: todo el pipeline (≈ 6 min; los bootstraps son lo más lento)
python src/pipeline.py

# Opción B: el notebook paso a paso
jupyter notebook notebooks/el_miedo_que_no_baja.ipynb
```

- **Descarga de datos:** `src/fuentes.py` baja cada fuente desde su servicio oficial y la deja en `data/crudos/`, con registro de URL, fecha y sha1. Si el archivo ya existe, usa la copia local, así que el análisis corre sin red con los datos incluidos en el repositorio.
- **Resultados idénticos:** las semillas están fijas, así que dos corridas dan las mismas cifras.

## 6. Despliegue del visor

```bash
cd visor
npm install
VISOR_CLAVE=<clave> VISOR_SECRETO=<cadena-aleatoria> npm run dev   # local en http://localhost:3210
vercel deploy --prod                                                 # producción (Vercel)
```

- **Datos del visor:** el pipeline los regenera en `visor/data/visor.json` y `visor/public/descargas/`. Después de correr el pipeline basta con volver a desplegar.
- **Acceso con clave:** lo controla `visor/proxy.ts`. La sesión dura 30 días, va firmada con HMAC-SHA256 y la clave se configura en las variables de entorno de Vercel.

## 7. Estructura del repositorio

```
data/
  crudos/          fuentes oficiales descargadas + registro_descargas.csv
  procesados/      tablas limpias e integradas (panel por localidad, microdatos analíticos)
notebooks/         el_miedo_que_no_baja.ipynb (ejecutado)
src/
  fuentes.py       descarga con caché desde los servicios oficiales
  territorio.py    llave territorial (normalizador de localidades)
  limpieza.py      limpieza por fuente con bitácora
  indicadores.py   integración, tasas, cifra oculta, Índice de Brecha, validaciones
  modelos.py       logit ponderado con AME, wild bootstrap, AUC por bloques, escenarios
  figuras.py       figuras PNG
  exportar.py      JSON del visor, CSV/GeoJSON descargables, tablas Power BI
  pipeline.py      orquestación de punta a punta
outputs/
  figuras/         figuras del informe
  tablas/          resultados de cada modelo y validación (CSV)
  geo/             GeoJSON con indicadores (localidad y UPZ)
  resultados.json  cifras que citan el visor, el formulario y el pitch
visor/             visor web Next.js (desplegado en Vercel)
powerbi/           proyecto de Power BI y tablas que consume
docs/              formulario, nota técnica, ficha del indicador y material del pitch
auditoria_portal/  scripts de auditoría del catálogo completo del portal (cifras de la nota técnica)
```

## 8. Limitaciones

- **Asociación, no causalidad.** El simulador es una sensibilidad del modelo.
- **Sesgo de método común.** Las calificaciones de alumbrado y ventas informales comparten batería con la seguridad de la zona: se reportan aparte.
- **Inventario de alumbrado viejo:** es de 2019 y por localidad, así que no permite validar el efecto del alumbrado.
- **Muestra de la EMV:** 96 encuestas por localidad, con factor de ponderación nacional. La cifra oculta compara personas con hechos y se lee como orden de magnitud.
- **Delito solo por localidad.** La Encuesta Distrital de Percepción 2025 no se pudo descargar en forma automatizada; es la fuente propuesta para el seguimiento por UPL.

## Licencia

Código bajo licencia MIT. Los datos son de las entidades distritales citadas y se usan bajo sus condiciones de datos abiertos.
