"""
Frente de vías, movilidad y alumbrado por localidad (DataJam 5 · The data squad).

Uso:  python src/fuentes_movilidad.py            (usa la caché de data/crudos/)
      python src/fuentes_movilidad.py --forzar   (vuelve a bajar todo)

Descarga desde las fuentes oficiales con caché en data/crudos/ (registro en
data/crudos/registro_descargas.csv, misma convención que src/fuentes.py), limpia,
normaliza la localidad con territorio.cod_localidad() y escribe en data/procesados/:

  movilidad_siniestros_localidad_anio.csv   muertes, heridos y siniestros por localidad y año
  alumbrado_localidad_anio.csv              luminarias por localidad y corte (2017-2024)
  ciclo_localidad.csv                       km de cicloinfraestructura y hurto de bicicletas
  vias_localidad.csv                        densidad vial y estado (PCI) de la malla
  hurtos_vehiculos_localidad.csv            HA, HM, HB (y HP) en tasa por 100.000
  movilidad_panel_localidad.csv             una fila por localidad urbana: insumo de las pruebas
  movilidad_pruebas_hipotesis.csv           Spearman, IC bootstrap, p por permutación y BH
  confiabilidad_movilidad.csv               ficha de confiabilidad por fuente

DECISIONES DE MÉTODO
1. Territorio. Llave = código oficial 1-20 de la SDP (territorio.cod_localidad). Las tablas
   traen las 20 localidades y una fila Bogotá (código 0) que incluye los registros sin
   localidad. Las pruebas usan las 19 urbanas (sin Sumapaz).
2. Muertes en vía. Fuente principal: INMLCF publicado por la SDS (localidad del hecho; es la
   cifra oficial de la tasa de mortalidad vial). El archivo trae cada muerte dos veces: una
   con código 0 («Bogotá») y otra con su localidad (1-20) o 21 («Sin dato»). Se usa el
   código 0 como total y se verifica que 1-21 sume lo mismo. 2026 llega hasta junio.
3. Heridos y siniestros. SDM, base SIGAT (servicio ArcGIS AccidentalidadAnalisis), conteos
   calculados por el propio servidor (outStatistics). En 2007-2020 cada formulario aparece
   dos veces (prefijo «A» y «AA», el mismo número): se excluyen los «AA%». Contra el
   histórico publicado en el portal (2015-2020) los siniestros con víctimas quedan 0,2-1,7 %
   por debajo (suma de control en la bitácora); los heridos, 8-10 % (verificación aparte). Se cuentan solo siniestros con heridos o con
   muertos: los de «solo daños» casi desaparecen del registro desde 2023 (12.557 en 2022,
   1.115 en 2023), así que no son comparables. 2026 llega hasta septiembre.
4. Tasas por 100.000 con la proyección de población SDP del mismo año. En años
   incompletos se dejan los conteos y la tasa vacía.
5. Alumbrado. UAESP publica inventarios mensuales por localidad en ~15 conjuntos con
   formatos distintos (CSV 2017-2021, Excel 2021-2024). Un lector genérico ubica cada tabla
   «localidad × tecnología» y separa el bloque del operador (CODENSA/ENEL, ~355.000
   luminarias) del bloque de propiedad del Distrito (~5.000-7.000, solo desagregado por
   localidad en jul-2021 a abr-2022 y en 2024). La serie comparable es la del operador; el
   total suma el Distrito cuando viene por localidad. Se marcan los cortes duplicados
   (mismo vector que un corte anterior). Último corte publicado: mayo de 2024.
6. Densidades. Las áreas oficiales de localidad incluyen suelo rural y cerros (Usme 215
   km², Ciudad Bolívar 130 km²); por eso se usa también el área urbana (cruce con la capa
   de clasificación del suelo, IDECA) y la longitud de vía. Todo en EPSG:3116.
7. Malla vial. Estado: IDU, PCI por calzada (ASTM D6433, 0-100) en km-carril, cortes
   dic-2024 (POT 190) y jun-2026 (POT 555). Indicador principal: % de km-carril con PCI < 56
   (pobre, muy pobre, grave o fallado; es el «malo» de la escala de 3 rangos que el IDU usó
   hasta 2021). Densidad vial: km de eje vial (IDECA, malla vial) dentro del suelo urbano por
   km² urbano; las luminarias por km de vía usan esa misma longitud urbana.
8. Cicloinfraestructura. Red de biciusuarios IDU (líneas). Un segmento cuenta como
   ciclorruta/bicicarril exclusivo si ≥ 50 % de su longitud cae dentro del polígono de
   ciclorruta del IDU (con 1,5 m de tolerancia). Se cruza con la cifra oficial del IDU a
   dic-2024 (infografía 2024-II).
9. Hurtos. SCJ, ventana ene-ago de cada año (ya en el repo). Según el contraste con el
   SIEDCO (src/validacion_registro.py), hurto a personas y automotores valen 2 a 2,6 veces
   el SIEDCO en 2018-2022 y lo mismo desde 2023 (de ahí la caída de -40 % en 2023): solo se
   comparan desde 2023. Las columnas HM, HCE y HC no se usan: desde 2023 «motocicletas»
   repite el hurto a comercio del SIEDCO y «celulares» repite motos. No hay, entonces, una
   serie confiable de hurto de motos por localidad. HB no tiene serie externa para validar
   y no muestra salto en 2023.
10. Calidad del alumbrado (sensibilidad). Bienal de Cultura 2025 (% que califica malo el
   alumbrado, del panel del proyecto) y auditoría nocturna de la SDMujer de sep-2019
   (% de puntos con iluminación «ninguna» o «poca»; GeoPackage 09.19, el único que trae la
   ola 2019 con atributos).
11. Pruebas. Spearman entre las 19 localidades urbanas; IC 95 % por bootstrap percentil
   (10.000 remuestreos de localidades); p bilateral por permutación (10.000); Benjamini-
   Hochberg dentro de cada bloque. Especificación principal: hurtos ene-ago 2025;
   sensibilidades: promedio 2023-2025 (el tramo sin quiebre) y lo mismo sin las 4
   localidades del centro (Chapinero, Santa Fe, Los Mártires, La Candelaria), donde las
   tasas por residente de hurto y de muertes en vía se inflan juntas por población flotante.
"""
from __future__ import annotations

import csv
import io
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fuentes import CKAN, CRUDOS, RAIZ, UA, _get, _registrar  # noqa: E402
from territorio import LOCALIDADES, URBANAS, cod_localidad, normalizar  # noqa: E402

PROC = RAIZ / "data" / "procesados"
ALUMBRADO_DIR = CRUDOS / "uaesp_alumbrado"
EPSG_PLANO = 3116  # MAGNA-SIRGAS / Colombia Bogotá
ANIO_REF = 2025
# Centro: localidades donde los residentes son una fracción pequeña de quienes circulan; las tasas por
# residente de hurto y de muertes en vía se inflan juntas (mismo denominador) y pueden fabricar correlación.
CENTRO = [2, 3, 14, 17]  # Chapinero, Santa Fe, Los Mártires, La Candelaria
SEMILLA = 20261006
B_BOOT = 10_000
B_PERM = 10_000

SDM = "https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer"
IDU_HUB = "https://services2.arcgis.com/qAnmJmgmnVso8Fzo/arcgis/rest/services"
MR = "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/Mapa_Referencia/Mapa_Referencia/MapServer"
PORTAL = "https://datosabiertos.bogota.gov.co/dataset"

BITACORA: list[dict] = []


def anotar(fuente: str, paso: str, detalle: str):
    BITACORA.append({"fuente": fuente, "paso": paso, "detalle": detalle})
    print(f"  · [{fuente}] {paso}: {detalle}")


# =================================================================== fuentes oficiales
FUENTES_MOV = {
    "sds_mortalidad_transito": {
        "entidad": "SDS · Observatorio de Salud (datos del INMLCF)",
        "conjunto": "Mortalidad por accidentes de tránsito (localidad del hecho)",
        "tipo": "archivo", "archivo": "sds_mortalidad_transito_inmlcf.csv",
        "url": f"{PORTAL}/bded0839-a912-467d-94c5-8561dbefcb22/resource/a956ec09-e22b-4b84-aeb9-25702cf610a0/download/osb_evento_transporte.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/mortalidad-por-accidentes-de-transito",
    },
    "sdm_sigat_conteos": {
        "entidad": "Secretaría Distrital de Movilidad (SDM) · SIGAT",
        "conjunto": "Siniestralidad_BD: muertos, lesionados y siniestros (conteos por año y localidad)",
        "tipo": "arcgis_conteo", "archivo": "sdm_sigat_conteos_localidad_anio.csv",
        "url": SDM,
        "portal": "https://datos.movilidadbogota.gov.co (Siniestralidad_BD)",
    },
    "sdm_historico_siniestros": {
        "entidad": "SDM", "conjunto": "Histórico siniestros Bogotá D.C. (2015-2021, control)",
        "tipo": "archivo", "archivo": "sdm_historico_siniestros_2015_2021.csv",
        "url": f"{PORTAL}/8624f916-1db2-4c17-b669-19a19b35d1ca/resource/f5862aaa-4e1c-463e-94d5-f04db8164360/download/historico_siniestros_bogota_d.c_-.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/historico-siniestros-bogota-d-c",
    },
    "idu_estado_malla_2026_06": {
        "entidad": "Instituto de Desarrollo Urbano (IDU)",
        "conjunto": "Estado MallaVial urbana POT-555 (junio 2026), capa EstadoMallaVialUrbanaConsolidado",
        "tipo": "arcgis_tabla", "archivo": "idu_estado_malla_vial_2026_06.csv",
        "url": f"{IDU_HUB}/EstadoMallaVialOD555/FeatureServer/2",
        "campos": "PK_ID_CALZADA,CIV,LOCEST,KMCAINDEST,TIPOMALLAEST,INDEST,ESTAASHTO", "lote": 2000,
        "portal": "https://geoportal-idu.hub.arcgis.com/",
    },
    "idu_estado_malla_2024_12": {
        "entidad": "Instituto de Desarrollo Urbano (IDU)",
        "conjunto": "Estado MallaVial urbana POT-190 (diciembre 2024), capa EstadoMallaVialUrbanaConsolidado",
        "tipo": "arcgis_tabla", "archivo": "idu_estado_malla_vial_2024_12.csv",
        "url": f"{IDU_HUB}/EstadoMallaVialOD/FeatureServer/0",
        "campos": "PK_ID_CALZADA,CIV,LOCEST,KMCAINDEST,TIPOMALLAEST,INDEST,ESTAASHTO,SUPERFEST", "lote": 2000,
        "portal": "https://geoportal-idu.hub.arcgis.com/",
    },
    "idu_estado_superficial_portal": {
        "entidad": "IDU", "conjunto": "Estado superficial Bogotá D.C. (portal; diagnóstico de calidad)",
        "tipo": "archivo", "archivo": "idu_estado_superficial_portal.7z",
        "url": f"{PORTAL}/a7b9d2f1-c68d-4c58-a225-e2b1450f95fb/resource/da423fdb-350f-4230-8367-53b71c4204e2/download/estado.7z",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/estado-superficial-bogota-d-c",
    },
    "idu_calzada_superficie": {
        "entidad": "IDU (Mapa de Referencia IDECA, capa Calzada)",
        "conjunto": "Calzada: tipo de superficie (para el diagnóstico del archivo de estado superficial)",
        "tipo": "arcgis_tabla", "archivo": "idu_calzada_tipo_superficie.csv",
        "url": f"{MR}/15", "campos": "CALCODIGO,CALTSUPERF,CALFUNCION", "lote": 1000,
        "portal": "https://datosabiertos.bogota.gov.co/dataset/calzada-bogota-d-c",
    },
    "ideca_malla_vial": {
        "entidad": "UAECD · IDECA (Mapa de Referencia)", "conjunto": "Malla vial (ejes viales)",
        "tipo": "arcgis_geo", "archivo": "ideca_malla_vial_ejes.geojson",
        "url": f"{MR}/13", "campos": "MVICODIGO,MVITCLA,MVITIPO", "lote": 1000, "simplificar": "0.00001",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/mapa-de-referencia",
    },
    "ideca_suelo": {
        "entidad": "UAECD · IDECA (Mapa de Referencia)", "conjunto": "Clasificación del suelo (urbano, expansión, rural)",
        "tipo": "arcgis_geo", "archivo": "ideca_clasificacion_suelo.geojson",
        "url": f"{MR}/45", "campos": "SUECODIGO,SUECSUELO,SUEAREA", "lote": 10,
        "portal": "https://datosabiertos.bogota.gov.co/dataset/mapa-de-referencia",
    },
    "idu_red_biciusuarios": {
        "entidad": "IDU (Mapa de Referencia IDECA)", "conjunto": "Red de biciusuarios (líneas)",
        "tipo": "arcgis_geo", "archivo": "idu_red_biciusuarios.geojson",
        "url": f"{MR}/19", "campos": "RBICODIGO,RBICLASE,RBILOCALIZ,RBITSUPERF", "lote": 1000,
        "portal": "https://datosabiertos.bogota.gov.co/dataset/red-biciusuarios-bogota-d-c",
    },
    "idu_cicloruta": {
        "entidad": "IDU (Mapa de Referencia IDECA)", "conjunto": "Cicloruta (polígonos)",
        "tipo": "arcgis_geo", "archivo": "idu_cicloruta_poligonos.geojson",
        "url": f"{MR}/18", "campos": "CICCODIGO,CICTSUPERF", "lote": 500,
        "portal": "https://datosabiertos.bogota.gov.co/dataset/cicloruta-bogota-d-c",
    },
    "idu_infografia_ciclorrutas_2024": {
        "entidad": "IDU · DTINI", "conjunto": "Estadísticas de extensión y estado de ciclorrutas 2024-II (corte 31-dic-2024)",
        "tipo": "archivo", "archivo": "idu_infografia_ciclorrutas_2024_II.pdf",
        "url": "https://idu.gov.co/Archivos_Portal/Transparencia/Informacion%20de%20interes/SIIPVIALES/Innovaci%C3%B3n/ciclorrutas-2025/Infografia%20Ciclorrutas%202024-II.pdf",
        "portal": "https://www.idu.gov.co",
    },
    "sdmujer_seguridad_nocturna": {
        "entidad": "Secretaría Distrital de la Mujer",
        "conjunto": "Puntos de evaluación de seguridad nocturna para las mujeres (olas nov-2015, feb-2016 y sep-2019), versión 09.19",
        "tipo": "archivo", "archivo": "sdmujer_puntos_seguridad_nocturna_v0919.gpkg",
        "url": f"{PORTAL}/f714e477-8e2a-44a2-87c0-17b491a01bcc/resource/486903b6-42da-4b36-9bfd-6e17bd0b7c6e/download/puntosseguridadnocturna.gpkg",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/evaluacion-de-seguridad-nocturna-para-las-mujeres-de-bogota-d-c",
    },
}

# Cortes de alumbrado (UAESP). periodo = mes del corte; la hoja aplica a los libros de Excel.
_A = f"{PORTAL}/9bfb08ba-14d3-45e3-9ae8-2e96b59565c9/resource"
_M21 = f"{PORTAL}/32ea873e-b78d-4689-8a52-fc7267fced6e/resource"
_M22 = f"{PORTAL}/9c5bc0ef-25f7-45d4-be54-81c9c4c8cc70/resource"
_XL22 = f"{PORTAL}/486421e6-1c6a-4870-802f-32ca39944e91/resource/137b5369-ee1c-46ac-94ef-e2a37b27018a/download/modelo-de-prestacion-de-servicios-alumbrado-publico-mayo-septiembre-2022.xlsx"
_XL23 = f"{PORTAL}/ad6b5fae-9195-4ccf-90cb-00ae05c42b8a/resource/49073170-d850-4474-bda0-394e342d5785/download/consolidado-mensual-lum-ap-2023.xlsx"
_XL24 = f"{PORTAL}/02d93186-1c9c-4bd6-89fa-747d829268c8/resource/99d78184-c7d1-4f37-be4c-c2c02cf1023d/download/consolidado-mensual-enero-a-mayo-2024-alumbrado-publico.xlsx"
_C21 = f"{PORTAL}/fd7d0aae-c169-4ace-a843-1622e0cced20/resource"
ALUMBRADO_CORTES = [
    ("2017-05", f"{_A}/b410e7ef-9877-4c7d-85e4-4777014e1357/download/mayo-2017-sap-lt.csv", None,
     "el archivo dice 'fecha corte mayo 15 de 2019' pero el portal lo publica como mayo 2017; solo trae el total"),
    ("2017-07", f"{_A}/f745d42a-99a0-416d-9620-f865e35694a8/download/julio-2017-ssfap-lt.csv", None, ""),
    ("2017-09", f"{_A}/3797f794-8052-4cb9-8cd0-39f44c5a060e/download/septiembre-2017-sap-lt.csv", None, ""),
    ("2017-10", f"{_A}/e5360c91-d533-4c04-83a0-8d2a39cb2c04/download/octubre-2017-ssfap-lt.csv", None,
     "el archivo de octubre trae fecha interna 22/09/2017"),
    ("2017-11", f"{_A}/11c5cb9e-9e2d-42f8-997c-922a5bb2c25c/download/noviembre-2017-ssfap-lt.csv", None,
     "fecha interna 20/09/2017"),
    ("2017-12", f"{_A}/81bba444-79d9-4bb8-9df9-192ddb224194/download/diciembre-2017-ssfap-lt.csv", None, ""),
    ("2018-02", f"{_A}/eeda80e9-97ae-4ed0-90f4-f976eb78937a/download/febrero-2018-sap-lt.csv", None, ""),
    ("2018-03", f"{_A}/b6e3c087-a1af-4302-8c2a-249ad8674e86/download/marzo-2018-sap-lt.csv", None, ""),
    ("2018-05", f"{_A}/8d9f3bcf-5130-4da8-aac1-85f8f9ae0fc3/download/mayo-2018-ssfap-lt.csv", None, ""),
    ("2018-06", f"{PORTAL}/09469f62-7a12-485f-b258-fb7f82d4b3dd/resource/5829f6aa-1cda-4b19-b6f7-9873f06bd7bc/download/data-set-alumbrado-publico.csv", None,
     "conjunto 'data set subdirección alumbrado público junio 2018'"),
    ("2018-09", f"{_A}/fdd56330-c8ab-47ab-bfe1-f1a1c967e1d5/download/septiembre-2018-sap-lt.csv", None, ""),
    ("2019-02", f"{_A}/60e456c8-bbec-4a0a-b155-8c23f4ff00e7/download/febrero-2019-sap-lt.csv", None, ""),
    ("2019-05", f"{_A}/7906b9af-f5ae-44a5-b93d-23cf6a9fefab/download/mayo-2019-sap-lt.csv", None, ""),
    ("2019-08", f"{_A}/cb3a42bd-72ec-4625-a004-55f7fc4dd7da/download/agosto-2019-sap-lt.csv", None, ""),
    ("2020-04", f"{_A}/3d69b39e-a2d7-49f1-bc1f-f86de49436e1/download/inf.-datasets-alumbrado-publico-29_05_2020.csv", None,
     "el portal lo llama 'Marzo 2020'; el archivo dice 'fecha de corte: 24 abril 2020'"),
    ("2021-01", f"{_C21}/3c723763-6d4d-4e10-ab82-b4c3c8d810a1/download/luminarias-ene.csv", None, ""),
    ("2021-02", f"{_C21}/a403c7d9-0caf-45dc-b25f-80b1025832b1/download/luminarias-feb.csv", None, ""),
    ("2021-03", f"{_C21}/40591717-5306-4d4e-812a-a80f8a648b6c/download/luminarias-mar.csv", None, ""),
    ("2021-04", f"{_C21}/5f78785e-feeb-472d-a840-6836afd18c43/download/luminarias-abr.csv", None, ""),
    ("2021-05", f"{_C21}/fe343c5e-709e-4eac-9bcb-1f7d37cd5148/download/luminarias-may.csv", None, ""),
    ("2021-06", f"{_M21}/acd32009-07d6-4376-afc0-6db8fe964d1c/download/modelo-prestacion-servicio-junio.xlsx", None, ""),
    ("2021-07", f"{_M21}/3519a93e-2c6d-432d-9916-59c7c14dfbf9/download/modelo-prestacion-servicio-julio.xlsx", None, ""),
    ("2021-08", f"{_M21}/a4e4d27a-04dd-4fae-8331-0942f62e43d9/download/modelo-prestacion-servicio-agosto.xlsx", None, ""),
    ("2021-09", f"{_M21}/6ff66c14-ccac-4a2e-bee8-00cb8a2d99dc/download/modelo-prestacion-servicio-septiembre.xlsx", None, ""),
    ("2021-10", f"{_M21}/f8bbbabc-aac9-4949-87fc-4838ff4e10e7/download/modelo-prestacion-servicio-octubre.xlsx", None, ""),
    ("2021-11", f"{_M21}/4916287b-a634-411f-9a9d-ae6b1c3ec0bb/download/modelo-prestacion-servicio-noviembre.xlsx", None, ""),
    ("2021-12", f"{_M21}/a684f513-9210-43bb-a229-f07a620a2508/download/modelo-prestacion-servicio-diciembre.xlsx", None, ""),
    ("2022-01", f"{_M22}/314e0844-34d6-4e57-a813-ee09cab5f06a/download/modelo-prestacion-servicio-enero.xlsx", None, ""),
    ("2022-02", f"{_M22}/e0bf81fc-5e92-4652-b977-744f6ff08bea/download/modelo-prestacion-servicio-febrero.xlsx", None, ""),
    ("2022-03", f"{_M22}/bf5efdae-ac27-4e03-a629-a22e975c05f9/download/modelo-prestacion-servicio-marzo.xlsx", None, ""),
    ("2022-04", f"{_M22}/37ec9a35-8776-473e-a2c4-76f503889aa6/download/modelo-prestacion-servicio-abril.xlsx", None, ""),
    ("2022-05", _XL22, "MAY", ""),
    ("2022-06", _XL22, "JUN v.2", "el libro trae dos versiones de junio; se usa 'JUN v.2'"),
    ("2022-07", _XL22, "JUL", ""), ("2022-08", _XL22, "AGO", ""), ("2022-09", _XL22, "SEP", ""),
] + [(f"2023-{i:02d}", _XL23, h, "") for i, h in enumerate(
    ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV"], start=1)
] + [(f"2024-{i:02d}", _XL24, h, "") for i, h in enumerate(["ENE", "FEB", "MAR", "ABR", "MAY"], start=1)]

ALUMBRADO_DUPLICADOS_EXCLUIDOS = [
    "data_set_alumbrado_publico_febrero_2019 (= feb-2019 de alumbrado_publico_lt)",
    "data-set-alumbrado-publico-abril-de-2018 y alumbrado-publico (= mar-2018, archivo 23_03_2018)",
    "data-set-alumbrado-publico-septiembre-2018 (= sep-2018)",
    "data-set-alumbrado-publico-2017 (archivo 20_11_2017 = sep-2017)",
    "inventario-alumbrado-publico-modelo-de-prestacion-de-servicios-ap (jun-nov 2021 = modelo jun-dic 2021)",
    "modelo-de-prestacion...-enero-a-abril-del-2023 (= hojas ENE-ABR del libro año 2023)",
]

# IDU, infografía «Estadísticas de extensión y estado ciclorrutas 2024-II», tabla «Desagregación de
# estado por localidad»: km de ciclorruta y bicicarril con diagnóstico y % en estado bueno o satisfactorio.
# Transcrita del PDF oficial (FUENTES_MOV['idu_infografia_ciclorrutas_2024']); total publicado 470,8 km.
IDU_CICLORRUTAS_2024 = {  # localidad: (km con diagnóstico, % bueno, % satisfactorio)
    1: (44.2, 78.8, 11.2), 2: (18.1, 77.2, 16.1), 3: (9.5, 77.9, 22.0), 4: (7.0, 60.6, 29.3),
    5: (7.3, 63.1, 22.9), 6: (15.6, 69.6, 22.4), 7: (29.3, 90.9, 6.9), 8: (73.6, 76.0, 15.3),
    9: (24.3, 83.0, 14.6), 10: (58.1, 73.1, 20.6), 11: (73.1, 75.7, 17.2), 12: (26.4, 63.4, 29.4),
    13: (37.0, 73.6, 21.5), 14: (6.6, 91.2, 8.8), 15: (3.9, 82.0, 14.0), 16: (16.0, 59.1, 31.8),
    17: (3.4, 68.8, 27.8), 18: (4.9, 45.2, 11.5), 19: (12.6, 55.8, 28.9),
}


# =================================================================== descarga con caché
def _post_json(url: str, data: dict) -> dict:
    for intento in range(5):
        try:
            r = requests.post(url, data=data, timeout=(20, 300), headers=UA)
            r.raise_for_status()
            j = r.json()
            if "error" in j:
                raise RuntimeError(f"{url}: {j['error']}")
            return j
        except (requests.ConnectionError, requests.Timeout, json.JSONDecodeError):
            time.sleep(3 * (intento + 1))
    raise RuntimeError(f"No respondió: {url}")


def _arcgis_ids(url: str, where: str = "1=1") -> list[int]:
    j = _get(f"{url}/query", params={"where": where, "returnIdsOnly": "true", "f": "json"}).json()
    ids = sorted(j.get("objectIds") or [])
    n = _get(f"{url}/query", params={"where": where, "returnCountOnly": "true", "f": "json"}).json()["count"]
    if len(ids) != n:
        raise RuntimeError(f"{url}: {len(ids)} ids frente a {n} registros")
    return ids


def _arcgis_tabla(url: str, campos: str, lote: int) -> pd.DataFrame:
    """Atributos completos de una capa, por lotes de objectIds (sin geometría)."""
    ids, filas = _arcgis_ids(url), []
    for i in range(0, len(ids), lote):
        j = _post_json(f"{url}/query", {"objectIds": ",".join(map(str, ids[i:i + lote])), "outFields": campos,
                                        "returnGeometry": "false", "f": "json"})
        filas += [f["attributes"] for f in j["features"]]
    if len(filas) != len(ids):
        raise RuntimeError(f"{url}: bajaron {len(filas)} de {len(ids)}")
    return pd.DataFrame(filas)


def _arcgis_geo(url: str, campos: str, lote: int, simplificar: str | None = None) -> dict:
    """GeoJSON en WGS84 por lotes. 'simplificar' = maxAllowableOffset en grados (1e-5 ≈ 1 m)."""
    ids, feats = _arcgis_ids(url), []
    for i in range(0, len(ids), lote):
        datos = {"objectIds": ",".join(map(str, ids[i:i + lote])), "outFields": campos, "returnGeometry": "true",
                 "outSR": "4326", "f": "geojson"}
        if simplificar:
            datos.update({"maxAllowableOffset": simplificar, "geometryPrecision": "7"})
        feats += _post_json(f"{url}/query", datos)["features"]
    if len(feats) != len(ids):
        raise RuntimeError(f"{url}: bajaron {len(feats)} de {len(ids)}")
    return {"type": "FeatureCollection", "features": feats}


def _arcgis_conteo(url: str, grupo: str, where: str) -> pd.DataFrame:
    """Conteo calculado por el servidor (outStatistics), agrupado."""
    st = json.dumps([{"statisticType": "count", "onStatisticField": "OBJECTID", "outStatisticFieldName": "n"}])
    j = _post_json(f"{url}/query", {"where": where, "outStatistics": st, "groupByFieldsForStatistics": grupo,
                                     "f": "json"})
    if j.get("exceededTransferLimit"):
        raise RuntimeError(f"{url}: el conteo agrupado excedió el límite del servicio")
    d = pd.DataFrame([f["attributes"] for f in j["features"]])
    d.columns = [c.lower() for c in d.columns]
    return d


def _sdm_conteos() -> pd.DataFrame:
    """Muertos (0), lesionados (1) y siniestros (2) por año y localidad, con y sin los formularios 'AA'."""
    partes = []
    for capa, nombre, grupo in ((0, "muertos", "ANO_OCURRENCIA_ACC,LOCALIDAD"),
                                (1, "lesionados", "ANO_OCURRENCIA_ACC,LOCALIDAD"),
                                (2, "siniestros", "ANO_OCURRENCIA_ACC,LOCALIDAD,GRAVEDAD")):
        url = f"{SDM}/{capa}"
        todos = _arcgis_conteo(url, grupo, "1=1").rename(columns={"n": "n_todos"})
        sin_aa = _arcgis_conteo(url, grupo, "FORMULARIO NOT LIKE 'AA%'").rename(columns={"n": "n_sin_aa"})
        llaves = [c.lower() for c in grupo.split(",")]
        d = todos.merge(sin_aa, on=llaves, how="outer")
        d["capa"] = nombre
        if "gravedad" not in d:
            d["gravedad"] = ""
        partes.append(d)
    d = pd.concat(partes, ignore_index=True).rename(columns={"ano_ocurrencia_acc": "anio"})
    return d[["capa", "anio", "localidad", "gravedad", "n_todos", "n_sin_aa"]]


def obtener_mov(clave: str, forzar: bool = False) -> Path:
    f = FUENTES_MOV[clave]
    ruta = CRUDOS / f["archivo"]
    if ruta.exists() and not forzar:
        return ruta
    CRUDOS.mkdir(parents=True, exist_ok=True)
    print(f"  ↓ {clave}")
    tipo = f["tipo"]
    if tipo == "archivo":
        ruta.write_bytes(_get(f["url"]).content)
    elif tipo == "arcgis_tabla":
        _arcgis_tabla(f["url"], f["campos"], f["lote"]).to_csv(ruta, index=False, encoding="utf-8")
    elif tipo == "arcgis_geo":
        ruta.write_text(json.dumps(_arcgis_geo(f["url"], f["campos"], f["lote"], f.get("simplificar")),
                                   ensure_ascii=False), encoding="utf-8")
    elif tipo == "arcgis_conteo":
        _sdm_conteos().to_csv(ruta, index=False, encoding="utf-8")
    _registrar(clave, ruta, f["url"])
    return ruta


def _archivo_alumbrado(url: str) -> Path:
    rid = re.search(r"resource/([0-9a-f]{8})", url).group(1)
    return ALUMBRADO_DIR / f"uaesp_{rid}{Path(url).suffix.lower()}"


def obtener_alumbrado(forzar: bool = False) -> list[Path]:
    ALUMBRADO_DIR.mkdir(parents=True, exist_ok=True)
    rutas = []
    for url in dict.fromkeys(u for _, u, _, _ in ALUMBRADO_CORTES):
        ruta = _archivo_alumbrado(url)
        if forzar or not ruta.exists():
            ruta.write_bytes(_get(url).content)
            _registrar("uaesp_alumbrado_serie", ruta, url)
        rutas.append(ruta)
    return rutas


def sdm_fecha_max() -> str | None:
    """Fecha del siniestro más reciente en el servicio de la SDM (define los meses cubiertos del último año)."""
    st = json.dumps([{"statisticType": "max", "onStatisticField": "FECHA_OCURRENCIA_ACC", "outStatisticFieldName": "mx"}])
    try:
        j = _post_json(f"{SDM}/2/query", {"where": "1=1", "outStatistics": st, "f": "json"})
        ms = j["features"][0]["attributes"]["MX"]
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date().isoformat()
    except Exception:  # noqa: BLE001
        return None


def metadatos(forzar: bool = False) -> dict:
    """Fecha de última actualización declarada por cada servicio (se guarda la primera consulta)."""
    ruta = CRUDOS / "metadatos_movilidad.json"
    if ruta.exists() and not forzar:
        return json.loads(ruta.read_text(encoding="utf-8"))
    meta = {"consultado": datetime.now().isoformat(timespec="seconds")}

    def ckan(paquete):
        try:
            p = _get(f"{CKAN}/package_show", params={"id": paquete}).json()["result"]
            return max((r.get("last_modified") or r.get("created") or "")[:10] for r in p["resources"])
        except Exception:  # noqa: BLE001
            return None

    def arcgis(url):
        try:
            j = _get(url, params={"f": "json"}).json()
            ms = (j.get("editingInfo") or {}).get("lastEditDate") or (j.get("editingInfo") or {}).get("dataLastEditDate")
            return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date().isoformat() if ms else None
        except Exception:  # noqa: BLE001
            return None

    meta.update({
        "sds_mortalidad_transito": ckan("mortalidad-por-accidentes-de-transito"),
        "sdm_historico_siniestros": ckan("historico-siniestros-bogota-d-c"),
        "idu_estado_malla_2026_06": arcgis(FUENTES_MOV["idu_estado_malla_2026_06"]["url"]),
        "idu_estado_malla_2024_12": arcgis(FUENTES_MOV["idu_estado_malla_2024_12"]["url"]),
        "idu_estado_superficial_portal": ckan("estado-superficial-bogota-d-c"),
        "ideca_mapa_referencia": ckan("mapa-de-referencia"),
        "idu_red_biciusuarios": ckan("red-biciusuarios-bogota-d-c"),
        "idu_cicloruta": ckan("cicloruta-bogota-d-c"),
        "uaesp_alumbrado": ckan("modelo-de-prestacion-de-servicios-alumbrado-publico-ano-2024"),
        "sdmujer_seguridad_nocturna": ckan("evaluacion-de-seguridad-nocturna-para-las-mujeres-de-bogota-d-c"),
        "scj_delitos": ckan("delito-de-alto-impacto-bogota-d-c"),
        "sdm_fecha_max": sdm_fecha_max(),
    })
    ruta.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


# =================================================================== insumos del repo
def poblacion() -> pd.DataFrame:
    p = pd.read_csv(PROC / "sdp_poblacion_localidad_grupos.csv")
    p = p[p["grupo"] == "total"][["localidad", "anio", "personas"]]
    bog = p.groupby("anio", as_index=False)["personas"].sum().assign(localidad=0)
    return pd.concat([p, bog], ignore_index=True)


def _pob(pob: pd.DataFrame, anio) -> pd.Series:
    return pob[pob["anio"] == anio].set_index("localidad")["personas"]


def localidades_geo():
    import geopandas as gpd

    g = gpd.read_file(CRUDOS / "ideca_localidades.geojson")
    g["localidad"] = g["LocCodigo"].astype(int)
    return g[["localidad", "LocArea", "geometry"]].to_crs(EPSG_PLANO)


def scj_delitos() -> pd.DataFrame:
    """Serie SCJ del repo (localidad 1-20) + fila Bogotá que incluye 'Sin localización' (código 99, del crudo)."""
    d = pd.read_csv(PROC / "scj_delitos_localidad_largo.csv")
    crudo = pd.read_csv(CRUDOS / "scj_delitos_alto_impacto_localidad.csv", encoding="latin-1")
    sin = crudo[pd.to_numeric(crudo["CMIULOCAL"], errors="coerce") == 99]
    filas = []
    for col in sin.columns:
        m = re.match(r"CM([A-Z]+?)(\d\d)CONT$", col)
        if m:
            filas.append({"codigo": m.group(1), "anio": 2000 + int(m.group(2)),
                          "sin_loc": pd.to_numeric(sin[col], errors="coerce").sum()})
    sin = pd.DataFrame(filas)
    bog = d.groupby(["anio", "codigo", "tipo"], as_index=False)["casos"].sum()
    bog = bog.merge(sin, on=["codigo", "anio"], how="left").fillna({"sin_loc": 0})
    bog["casos"] = bog["casos"] + bog["sin_loc"]
    bog["localidad"] = 0
    return pd.concat([d, bog.drop(columns="sin_loc")], ignore_index=True)


# =================================================================== siniestralidad
def mortalidad_inmlcf() -> pd.DataFrame:
    d = pd.read_csv(obtener_mov("sds_mortalidad_transito"), sep=";", encoding="utf-8-sig")
    d.columns = [c.strip().lower() for c in d.columns]
    d["cod"] = pd.to_numeric(d["codigo_localidad"], errors="coerce").astype(int)
    d["casos"] = pd.to_numeric(d["casos"], errors="coerce")
    t = d.groupby(["ano", "cod"])["casos"].sum().unstack(fill_value=0)
    control = t[0] - t.drop(columns=0).sum(axis=1)
    anotar("INMLCF (SDS)", "duplicación", f"{len(d)} filas; cada muerte aparece con código 0 (Bogotá) y con su localidad; "
           f"diferencia 0 vs suma 1-21 por año: {control.abs().max():.0f}")
    sin = t.get(21, pd.Series(0, index=t.index))
    anotar("INMLCF (SDS)", "sin localidad", "muertes con localidad 'Sin dato' (código 21) por año: "
           + ", ".join(f"{a}: {int(v)} ({v / t.loc[a, 0]:.0%})" for a, v in sin.items()))
    meses = d.groupby("ano")["mes_del_hecho"].apply(lambda s: s.str.lower().str.strip().nunique())
    largo = t.drop(columns=21, errors="ignore").stack().rename("muertes_inmlcf").reset_index()
    largo.columns = ["anio", "localidad", "muertes_inmlcf"]
    largo["meses_inmlcf"] = largo["anio"].map(meses.clip(upper=12))
    return largo


def siniestralidad_sdm() -> pd.DataFrame:
    d = pd.read_csv(obtener_mov("sdm_sigat_conteos"))
    d = d[d["anio"].between(2015, 2026)].copy()
    tot = d.groupby(["capa", "anio"])[["n_todos", "n_sin_aa"]].sum()
    dup = tot.assign(pct=lambda x: 1 - x["n_sin_aa"] / x["n_todos"])["pct"].unstack(0)
    anotar("SDM SIGAT", "duplicación", "share de registros con formulario 'AA' excluidos (muertos) por año: "
           + ", ".join(f"{int(a)}: {v:.0%}" for a, v in dup["muertos"].items() if v > 0))
    d["cod"] = d["localidad"].map(cod_localidad)
    sin = d[d["cod"].isna()].groupby("capa")["n_sin_aa"].sum()
    anotar("SDM SIGAT", "llave", f"registros sin localidad reconocible (solo cuentan en Bogotá): {sin.to_dict()}")
    d["cod"] = d["cod"].fillna(-1).astype(int)
    d["gravedad"] = d["gravedad"].fillna("")

    def pivote(mask, nombre):
        x = d[mask].groupby(["anio", "cod"])["n_sin_aa"].sum().rename(nombre).reset_index()
        bog = x.groupby("anio", as_index=False)[nombre].sum().assign(cod=0)
        return pd.concat([x[x["cod"] > 0], bog]).rename(columns={"cod": "localidad"})

    partes = [pivote(d["capa"] == "muertos", "muertes_sdm"),
              pivote(d["capa"] == "lesionados", "lesionados_sdm"),
              pivote((d["capa"] == "siniestros") & d["gravedad"].isin(["CON HERIDOS", "CON MUERTOS"]),
                     "siniestros_con_victimas_sdm"),
              pivote((d["capa"] == "siniestros") & (d["gravedad"] == "CON MUERTOS"), "siniestros_con_muertos_sdm"),
              pivote((d["capa"] == "siniestros") & (d["gravedad"] == "SOLO DANOS"), "siniestros_solo_danos_sdm")]
    out = partes[0]
    for p in partes[1:]:
        out = out.merge(p, on=["anio", "localidad"], how="outer")
    out["anio"] = out["anio"].astype(int)
    return out


def control_historico_portal(sdm: pd.DataFrame):
    """Suma de control: SDM SIGAT (sin 'AA') frente al histórico publicado en el portal (2015-2020)."""
    h = pd.read_csv(obtener_mov("sdm_historico_siniestros"), low_memory=False, encoding_errors="replace")
    h.columns = [c.strip().lower() for c in h.columns]
    h = h.groupby(["ano_ocurrencia_acc", "gravedad"]).size().unstack(fill_value=0)
    bog = sdm[sdm["localidad"] == 0].set_index("anio")
    filas = []
    for a in range(2015, 2021):
        portal = h.loc[a, "CON HERIDOS"] + h.loc[a, "CON MUERTOS"]
        filas.append(f"{a}: SIGAT {int(bog.loc[a, 'siniestros_con_victimas_sdm'])} vs portal {portal}")
    anotar("SDM SIGAT", "control", "siniestros con víctimas, SIGAT sin 'AA' vs histórico del portal: " + "; ".join(filas))
    return h


def tabla_siniestros(pob: pd.DataFrame, meta: dict) -> pd.DataFrame:
    inm = mortalidad_inmlcf()
    sdm = siniestralidad_sdm()
    control_historico_portal(sdm)
    base = pd.MultiIndex.from_product([range(2015, 2027), [0] + list(range(1, 21))], names=["anio", "localidad"])
    t = pd.DataFrame(index=base).reset_index()
    t = t.merge(inm, on=["anio", "localidad"], how="left").merge(sdm, on=["anio", "localidad"], how="left")
    cuentas = ["muertes_inmlcf", "muertes_sdm", "lesionados_sdm", "siniestros_con_victimas_sdm",
               "siniestros_con_muertos_sdm", "siniestros_solo_danos_sdm"]
    t[cuentas] = t[cuentas].fillna(0).astype(int)
    t["meses_inmlcf"] = t["anio"].map(t.groupby("anio")["meses_inmlcf"].max())
    fmax = pd.Timestamp(meta["sdm_fecha_max"])  # último día con siniestros en el servicio de la SDM
    t["meses_sdm"] = np.where(t["anio"] < fmax.year, 12, np.where(t["anio"] == fmax.year, fmax.month, 0))
    t["poblacion"] = [_pob(pob, a).get(l, np.nan) for a, l in zip(t["anio"], t["localidad"])]
    for c, meses in (("muertes_inmlcf", "meses_inmlcf"), ("muertes_sdm", "meses_sdm"),
                     ("lesionados_sdm", "meses_sdm"), ("siniestros_con_victimas_sdm", "meses_sdm")):
        t[f"tasa_{c}_100k"] = (t[c] / t["poblacion"] * 1e5).where(t[meses] == 12)
    t["anio_completo_inmlcf"] = t["meses_inmlcf"] == 12
    t["anio_completo_sdm"] = t["meses_sdm"] == 12
    t["nombre"] = t["localidad"].map({0: "Bogotá D.C.", **LOCALIDADES})
    sin_loc = inm[inm["localidad"] == 0].set_index("anio")["muertes_inmlcf"] - \
        inm[inm["localidad"] > 0].groupby("anio")["muertes_inmlcf"].sum()

    def nota(r):
        n = []
        if r["meses_inmlcf"] < 12 or r["meses_sdm"] < 12:
            n.append(f"{r['anio']} incompleto: INMLCF {int(r['meses_inmlcf'])} meses (preliminar), SDM "
                     f"{int(r['meses_sdm'])} meses; sin tasa en la fuente incompleta")
        if r["localidad"] == 0 and sin_loc.get(r["anio"], 0) > 0:
            n.append(f"incluye {int(sin_loc[r['anio']])} muertes INMLCF sin localidad")
        if r["anio"] >= 2023:
            n.append("siniestros 'solo daños' casi no se registran desde 2023")
        return "; ".join(n)

    t["nota"] = t.apply(nota, axis=1)
    cols = ["localidad", "nombre", "anio", "muertes_inmlcf", "muertes_sdm", "lesionados_sdm",
            "siniestros_con_victimas_sdm", "siniestros_con_muertos_sdm", "siniestros_solo_danos_sdm", "poblacion",
            "tasa_muertes_inmlcf_100k", "tasa_muertes_sdm_100k", "tasa_lesionados_sdm_100k",
            "tasa_siniestros_con_victimas_sdm_100k", "meses_inmlcf", "meses_sdm", "anio_completo_inmlcf",
            "anio_completo_sdm", "nota"]
    return t[cols].sort_values(["anio", "localidad"]).reset_index(drop=True)


# =================================================================== alumbrado (lector genérico)
_TEC = {"fluor": r"fluorescent|mercurio|\bfi\b", "led": r"led\b|diodo", "mh": r"halogenur|\bmh\b|\bcmh\b",
        "na": r"sodio|\bna\b"}


def _numero(v):
    if v is None:
        return None
    if isinstance(v, (int, float, np.integer, np.floating)):
        return None if pd.isna(v) else float(v)
    s = str(v).strip().replace("\xa0", "").replace(" ", "")
    if s == "-":
        return 0.0
    if s in ("", "nan"):
        return None
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", s):
        return float(re.sub(r"[.,]", "", s))
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def _leer_grilla(ruta: Path, hoja: str | None) -> list[list]:
    if ruta.suffix == ".csv":
        crudo = ruta.read_bytes()
        for enc in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                txt = crudo.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        return [list(f) for f in csv.reader(io.StringIO(txt), delimiter=";")]
    d = pd.read_excel(ruta, sheet_name=hoja or 0, header=None, dtype=object)
    return d.where(d.notna(), "").values.tolist()


def _rotulo(texto: str) -> str | None:
    t = normalizar(texto)
    if re.search(r"potencia|\bkw\b|porcent|%", t):
        return None
    if re.search(r"total|cantidad de luminaria|n\w* mero de luminaria|numero de luminaria", t):
        return "total"
    for k, pat in _TEC.items():
        if re.search(pat, t):
            return k
    return None


def _es_cabecera_localidad(c) -> bool:
    t = normalizar(c) if isinstance(c, str) else ""
    return (t.endswith("localidad") and len(t) <= 20) or t == "nombre"


def _es_codigo(v) -> bool:
    return v is not None and float(v).is_integer() and 1 <= v <= 20


def _cod_fila(fila: list, j: int) -> int | None:
    """Código de localidad de una fila de datos: número 1-20 o nombre reconocible en la columna j."""
    celda = fila[j] if j < len(fila) else ""
    v = _numero(celda)
    if v is not None:
        return int(v) if _es_codigo(v) else None
    if isinstance(celda, str) and celda.strip():
        c = cod_localidad(celda)
        if c:
            return c
        # nombre ilegible por la codificación ('Los M rtires', 'San Crist¢bal'): código de la columna anterior
        if j > 0 and _es_codigo(_numero(fila[j - 1])):
            return int(_numero(fila[j - 1]))
    return None


def _bloques_alumbrado(g: list[list]) -> list[pd.DataFrame]:
    out = []
    for i, fila in enumerate(g):
        cols = [j for j, c in enumerate(fila) if _es_cabecera_localidad(c)]
        for n, jloc in enumerate(cols):
            jfin = cols[n + 1] if n + 1 < len(cols) else max(len(f) for f in g[max(0, i - 2): i + 3])
            # rótulo de cada columna = texto de las celdas no numéricas de la fila cabecera y sus vecinas
            rotulos = {}
            for j in range(jloc + 1, jfin):
                partes = [g[k][j] for k in range(max(0, i - 2), min(len(g), i + 3))
                          if j < len(g[k]) and isinstance(g[k][j], str) and g[k][j].strip() and _numero(g[k][j]) is None]
                rotulos[j] = _rotulo(" ".join(partes))
            filas, vacias = [], 0
            for k in range(i + 1, len(g)):
                cod = _cod_fila(g[k], jloc)
                if cod is None:
                    vacias += 1
                    if filas and vacias > 1:
                        break
                    continue
                vacias = 0
                reg = {"localidad": cod}
                for j, r in rotulos.items():
                    if r and j < len(g[k]):
                        v = _numero(g[k][j])
                        if v is not None and not (r == "total" and "total" in reg):
                            reg[r] = reg.get(r, 0) + v
                filas.append(reg)
            if len(filas) >= 10:
                d = pd.DataFrame(filas).groupby("localidad").sum()
                tecs = [c for c in _TEC if c in d]
                if "total" not in d and tecs:
                    d["total"] = d[tecs].sum(axis=1)
                if "total" in d and d["total"].sum() > 0:
                    d.attrs.update({"fila": i, "tecs": tecs})
                    out.append(d)
    return out


def _total_distrito(g: list[list]) -> float | None:
    """Total de luminarias del Distrito cuando el libro solo lo trae como resumen ('Totales Propiedad Distrito')."""
    for i, fila in enumerate(g):
        if any(isinstance(c, str) and "propiedad distrito" in normalizar(c) for c in fila) and i + 1 < len(g):
            nums = [_numero(c) for c in g[i + 1]]
            nums = [v for v in nums if v is not None and v >= 1000]
            if nums:
                return max(nums)
    return None


def _corte_texto(g: list[list]) -> str:
    texto = " ".join(str(c) for f in g for c in f if isinstance(c, str) and "corte" in c.lower())
    m = re.search(r"corte\D{0,25}?(\d{1,2})\s*(?:de\s*)?([A-Za-zé]{3,})\.?\s*(?:de\s*)?(\d{4})", texto, re.I)
    return " ".join(m.groups()) if m else ""


def leer_alumbrado() -> pd.DataFrame:
    obtener_alumbrado()
    filas = []
    for periodo, url, hoja, nota in ALUMBRADO_CORTES:
        ruta = _archivo_alumbrado(url)
        g = _leer_grilla(ruta, hoja)
        unicos = []
        for b in _bloques_alumbrado(g):  # la misma tabla puede salir dos veces (columna código y columna nombre)
            if not any(b["total"].reindex(range(1, 21)).fillna(-1).equals(u["total"].reindex(range(1, 21)).fillna(-1))
                       for u in unicos):
                unicos.append(b)
        op = [b for b in unicos if b["total"].sum() > 100_000]
        dis = [b for b in unicos if b["total"].sum() < 20_000]
        if not op:
            raise RuntimeError(f"alumbrado {periodo}: no se encontró la tabla del operador")
        o = op[0]
        d = pd.DataFrame(index=pd.Index(range(1, 21), name="localidad"))
        d["luminarias_operador"] = o["total"]
        d["led_operador"] = o["led"] if "led" in o else np.nan
        if dis:
            d["luminarias_distrito"] = dis[0]["total"].reindex(d.index).fillna(0)
            d["led_distrito"] = dis[0]["led"].reindex(d.index).fillna(0) if "led" in dis[0] else 0.0
        else:
            d["luminarias_distrito"] = np.nan
            d["led_distrito"] = np.nan
            td = _total_distrito(g)
            if td:
                nota = (nota + "; " if nota else "") + (f"el libro solo trae el total de luminarias del Distrito "
                                                        f"({td:,.0f}), no por localidad")
        if len(op) > 1:  # tabla 'TOTAL BOGOTÁ' por localidad (operador + distrito), solo como control
            dif = (op[1]["total"].reindex(d.index).fillna(0) - d["luminarias_operador"]
                   - d["luminarias_distrito"].fillna(0)).abs().sum()
            nota = (nota + "; " if nota else "") + f"tabla combinada del archivo = operador + distrito (diferencia {dif:.0f})"
        d["periodo"] = periodo
        d["fecha_corte_texto"] = _corte_texto(g)
        d["archivo"] = ruta.name
        d["hoja"] = hoja or ""
        d["url"] = url
        d["nota"] = nota
        d["n_localidades_leidas"] = int(o["total"].notna().sum())
        filas.append(d.reset_index())
    a = pd.concat(filas, ignore_index=True)
    # cortes duplicados: mismo vector del operador que un corte anterior
    vec = a.pivot(index="periodo", columns="localidad", values="luminarias_operador")
    dup = {}
    for i, p in enumerate(vec.index):
        for q in vec.index[:i]:
            if vec.loc[p].fillna(-1).equals(vec.loc[q].fillna(-1)):
                dup[p] = q
                break
    a["duplicado_de"] = a["periodo"].map(dup).fillna("")
    resumen = a.groupby("periodo").agg(op=("luminarias_operador", "sum"), n=("luminarias_operador", "count"))
    anotar("UAESP alumbrado", "lectura", f"{len(resumen)} cortes ({resumen.index.min()} a {resumen.index.max()}); "
           f"luminarias del operador entre {resumen['op'].min():,.0f} y {resumen['op'].max():,.0f}; "
           f"cortes con <20 localidades: {resumen[resumen['n'] < 20].index.tolist()}")
    anotar("UAESP alumbrado", "duplicados", f"cortes idénticos a uno anterior: {dup}")
    return a


# =================================================================== geometría: áreas, vías, ciclo
def suelo_urbano(locs):
    """Parte urbana de cada localidad (capa de clasificación del suelo, SUECSUELO = 1)."""
    import geopandas as gpd

    s = gpd.read_file(obtener_mov("ideca_suelo")).to_crs(EPSG_PLANO)
    urbano = s[s["SUECSUELO"] == 1].union_all()
    u = locs.copy()
    u["geometry"] = u.geometry.intersection(urbano)
    a = u.set_index("localidad").area / 1e6
    anotar("IDECA suelo", "área urbana", f"suelo urbano total {urbano.area / 1e6:.1f} km² (SUECSUELO=1); "
           f"suma por localidad {a.sum():.1f} km²; sin suelo urbano: {a[a < 0.5].index.tolist()}")
    return u[~u.geometry.is_empty], a


def km_via(locs, urb) -> pd.DataFrame:
    """km de eje vial por localidad: total y dentro del suelo urbano."""
    import geopandas as gpd

    v = gpd.read_file(obtener_mov("ideca_malla_vial")).to_crs(EPSG_PLANO)
    v = v[v.geometry.notna() & ~v.geometry.is_empty]
    tot = v.length.sum() / 1000
    out = {}
    for nombre, poligonos in (("km_via_ejes", locs), ("km_via_urbana", urb)):
        x = gpd.overlay(v[["MVICODIGO", "geometry"]], poligonos[["localidad", "geometry"]], how="intersection",
                        keep_geom_type=True)
        out[nombre] = x.assign(km=x.length / 1000).groupby("localidad")["km"].sum()
    km = pd.DataFrame(out).reindex(range(1, 21)).fillna(0)
    anotar("IDECA malla vial", "longitud", f"{len(v):,} ejes; {tot:,.0f} km totales; {km['km_via_ejes'].sum():,.0f} km "
           f"dentro de las 20 localidades y {km['km_via_urbana'].sum():,.0f} km en suelo urbano "
           f"(geometría simplificada a 1 m en la descarga)")
    return km


def ciclo_km(locs) -> pd.DataFrame:
    import geopandas as gpd

    r = gpd.read_file(obtener_mov("idu_red_biciusuarios")).to_crs(EPSG_PLANO)
    c = gpd.read_file(obtener_mov("idu_cicloruta")).to_crs(EPSG_PLANO)
    r["rid"] = range(len(r))
    r["km_seg"] = r.length / 1000
    cb = c[["geometry"]].copy()
    cb["geometry"] = cb.buffer(1.5)
    dentro = gpd.overlay(r[["rid", "geometry"]], cb, how="intersection", keep_geom_type=True).dissolve(by="rid")
    r["km_dentro"] = r["rid"].map(dentro.length / 1000).fillna(0).clip(upper=r["km_seg"])
    r["exclusiva"] = r["km_dentro"] >= 0.5 * r["km_seg"]
    x = gpd.overlay(r[["rid", "exclusiva", "geometry"]], locs[["localidad", "geometry"]], how="intersection",
                    keep_geom_type=True)
    x["km"] = x.length / 1000
    out = pd.DataFrame({"km_red_biciusuarios": x.groupby("localidad")["km"].sum(),
                        "km_ciclorruta_exclusiva": x[x["exclusiva"]].groupby("localidad")["km"].sum()}).fillna(0)
    anotar("IDU cicloinfraestructura", "longitud", f"red de biciusuarios {r['km_seg'].sum():.1f} km; exclusiva "
           f"(≥50 % dentro de polígono de ciclorruta) {r.loc[r['exclusiva'], 'km_seg'].sum():.1f} km; IDU dic-2024 "
           f"publica 677,5 km de red y 470,8 km de ciclorruta+bicicarril con diagnóstico")
    return out


def estado_malla(clave: str) -> pd.DataFrame:
    e = pd.read_csv(obtener_mov(clave))
    e = e[e["LOCEST"].between(1, 20)]
    con = e[e["INDEST"] >= 0]

    def agrega(df, sub):
        g = df.groupby("LOCEST")
        km = g["KMCAINDEST"].sum()
        kme = sub.groupby("LOCEST")["KMCAINDEST"].sum()
        pci = sub.assign(p=sub["INDEST"] * sub["KMCAINDEST"]).groupby("LOCEST")["p"].sum() / kme
        malo = sub[sub["INDEST"] < 56].groupby("LOCEST")["KMCAINDEST"].sum() / kme
        grave = sub[sub["INDEST"] <= 25].groupby("LOCEST")["KMCAINDEST"].sum() / kme
        bueno = sub[sub["INDEST"] >= 71].groupby("LOCEST")["KMCAINDEST"].sum() / kme
        return pd.DataFrame({"km_carril": km, "km_carril_con_estado": kme, "pci_medio": pci,
                             "pct_pci_menor_56": malo * 100, "pct_grave_fallado": grave * 100,
                             "pct_bueno_satisfactorio": bueno * 100}).fillna(0)

    t = agrega(e, con)
    loc = agrega(e[e["TIPOMALLAEST"] == "Local"], con[con["TIPOMALLAEST"] == "Local"])
    t["pct_pci_menor_56_local"] = loc["pct_pci_menor_56"]
    # Bogotá
    kme = con["KMCAINDEST"].sum()
    t.loc[0] = [e["KMCAINDEST"].sum(), kme, (con["INDEST"] * con["KMCAINDEST"]).sum() / kme,
                con.loc[con["INDEST"] < 56, "KMCAINDEST"].sum() / kme * 100,
                con.loc[con["INDEST"] <= 25, "KMCAINDEST"].sum() / kme * 100,
                con.loc[con["INDEST"] >= 71, "KMCAINDEST"].sum() / kme * 100,
                con.loc[(con["INDEST"] < 56) & (con["TIPOMALLAEST"] == "Local"), "KMCAINDEST"].sum()
                / con.loc[con["TIPOMALLAEST"] == "Local", "KMCAINDEST"].sum() * 100]
    t.index.name = "localidad"
    anotar("IDU estado malla", clave, f"{len(e):,} calzadas urbanas; {e['KMCAINDEST'].sum():,.1f} km-carril, "
           f"{kme:,.1f} con estado; PCI medio {t.loc[0, 'pci_medio']:.1f}; PCI<56: {t.loc[0, 'pct_pci_menor_56']:.1f} %")
    return t


def diagnostico_estado_superficial() -> dict:
    """El archivo 'estado superficial' del portal (estado.7z): ¿trae estado o tipo de superficie?"""
    ruta = obtener_mov("idu_estado_superficial_portal")
    destino = CRUDOS / "idu_estado_superficial_portal"
    csvs = list(destino.glob("*.csv"))
    if not csvs:
        # bsdtar de Windows lee .7z; el tar GNU de Git Bash no
        bsdtar = Path(r"C:\Windows\System32\tar.exe")
        tar = str(bsdtar) if bsdtar.exists() else (shutil.which("bsdtar") or shutil.which("tar"))
        if not tar:
            anotar("IDU estado superficial (portal)", "diagnóstico", "no se pudo abrir el .7z (falta bsdtar)")
            return {"resultado": "no se pudo abrir el .7z (falta tar/bsdtar)"}
        destino.mkdir(exist_ok=True)
        r = subprocess.run([tar, "-xf", str(ruta), "-C", str(destino)], capture_output=True, text=True)
        csvs = list(destino.glob("*.csv"))
        if r.returncode != 0 or not csvs:
            anotar("IDU estado superficial (portal)", "diagnóstico", f"no se pudo abrir el .7z: {r.stderr.strip()[:200]}")
            return {"resultado": f"no se pudo abrir el .7z: {r.stderr.strip()[:200]}"}
    e = pd.read_csv(csvs[0])
    s = pd.read_csv(obtener_mov("idu_calzada_superficie"))
    m = e.merge(s, left_on="CalCodigo", right_on="CALCODIGO")
    coincide = (m["ESTADO_SUPERFICIAL"] == m["CALTSUPERF"]).mean()
    res = {"registros": len(e), "fecha_estado": str(e["FECHA_ESTADO"].mode().iat[0]),
           "codigos": sorted(e["ESTADO_SUPERFICIAL"].dropna().astype(int).unique().tolist()),
           "cruzan_con_calzada": len(m), "coincide_con_tipo_superficie": round(float(coincide), 3)}
    anotar("IDU estado superficial (portal)", "diagnóstico",
           f"{len(e):,} calzadas, códigos {res['codigos']}; el código coincide con el TIPO de superficie de la "
           f"calzada (CALTSUPERF) en {coincide:.1%} de {len(m):,} cruces: el archivo no trae el estado (PCI)")
    return res


def iluminacion_auditoria() -> pd.DataFrame:
    """% de puntos auditados de noche (6-11 p.m.) con iluminación 'ninguna' (0) o 'poca' (1), por ola."""
    import geopandas as gpd

    d = gpd.read_file(obtener_mov("sdmujer_seguridad_nocturna"), ignore_geometry=True)
    # olas: nov-2015 y feb-2016 (publicada como versión 09.16, «2016») y sep-2019
    d["ola"] = pd.to_datetime(d["Fecha"]).dt.year.map({2015: "2016", 2016: "2016", 2019: "2019"})
    d["loc"] = pd.to_numeric(d["LOCCODIGO"], errors="coerce")
    d["deficiente"] = d["ILUMINACIO"].isin([0, 1])
    s = d[d["loc"].between(1, 20)].pivot_table(index="loc", columns="ola", values="deficiente", aggfunc="mean") * 100
    n = d[d["loc"].between(1, 20)].pivot_table(index="loc", columns="ola", values="deficiente", aggfunc="size")
    s.index = s.index.astype(int)
    anotar("SDMujer seguridad nocturna", "iluminación",
           f"{len(d):,} puntos (ola 2019: {int((d['ola'] == '2019').sum()):,}); % ninguna o poca: "
           + ", ".join(f"{o}: {d.loc[d['ola'] == o, 'deficiente'].mean():.1%}" for o in ("2016", "2019"))
           + f"; puntos por localidad en 2019 entre {int(n['2019'].min())} y {int(n['2019'].max())}")
    otro = PROC / "seguridad_nocturna_localidad.csv"  # el mismo GPKG procesado por el frente de género
    if otro.exists():
        g = pd.read_csv(otro).set_index("localidad")["pct_iluminacion_poca_o_ninguna"]
        dif = (s["2019"] - g).abs().max()
        anotar("SDMujer seguridad nocturna", "control", f"diferencia máxima con seguridad_nocturna_localidad.csv "
               f"(frente de género, 2019): {dif:.2f} pp")
    return s.rename(columns=lambda o: f"iluminacion_deficiente_{o}")


# =================================================================== tablas de salida
def _con_bogota(serie: pd.Series) -> pd.Series:
    """Agrega el índice 0 (Bogotá) con la suma de las localidades."""
    serie = serie.copy()
    serie.loc[0] = serie.drop(index=0, errors="ignore").sum()
    return serie


def tabla_alumbrado(alum: pd.DataFrame, pob, area_km2, area_urb, kmv, kmc) -> pd.DataFrame:
    a = alum.copy()
    a["anio"] = a["periodo"].str[:4].astype(int)
    a["luminarias_total"] = a["luminarias_operador"] + a["luminarias_distrito"].fillna(0)
    a["alcance_total"] = np.where(a["luminarias_distrito"].notna(), "operador + distrito", "solo operador")
    a["luminarias_led"] = a["led_operador"] + a["led_distrito"].fillna(0)
    sumas = ["luminarias_operador", "luminarias_distrito", "luminarias_total", "luminarias_led", "led_operador"]
    fijos = ["anio", "fecha_corte_texto", "archivo", "hoja", "url", "nota", "duplicado_de", "alcance_total",
             "n_localidades_leidas"]
    g = a.groupby("periodo")
    bog = pd.concat([g[sumas].sum(min_count=1), g[fijos].first()], axis=1).reset_index()
    bog["localidad"] = 0
    a = pd.concat([a, bog], ignore_index=True)
    a["pct_led"] = a["luminarias_led"] / a["luminarias_total"] * 100
    a["area_km2"] = a["localidad"].map(_con_bogota(area_km2))
    a["area_urbana_km2"] = a["localidad"].map(_con_bogota(area_urb))
    a["km_via_urbana"] = a["localidad"].map(_con_bogota(kmv["km_via_urbana"]))
    a["km_carril_2024_12"] = a["localidad"].map(kmc)
    a["luminarias_km2"] = a["luminarias_total"] / a["area_km2"]
    a["luminarias_km2_urbano"] = a["luminarias_total"] / a["area_urbana_km2"].where(a["area_urbana_km2"] > 0.5)
    a["luminarias_km_via"] = a["luminarias_total"] / a["km_via_urbana"].where(a["km_via_urbana"] > 0)
    a["luminarias_km_carril"] = a["luminarias_total"] / a["km_carril_2024_12"]
    a["poblacion"] = [_pob(pob, y).get(l, np.nan) for y, l in zip(a["anio"], a["localidad"])]
    a["luminarias_1000_hab"] = a["luminarias_total"] / a["poblacion"] * 1000
    a["nombre"] = a["localidad"].map({0: "Bogotá D.C.", **LOCALIDADES})
    cols = ["localidad", "nombre", "periodo", "anio", "fecha_corte_texto", "luminarias_operador", "luminarias_distrito",
            "luminarias_total", "alcance_total", "luminarias_led", "pct_led", "area_km2", "area_urbana_km2",
            "km_via_urbana", "km_carril_2024_12", "luminarias_km2", "luminarias_km2_urbano", "luminarias_km_via",
            "luminarias_km_carril", "poblacion", "luminarias_1000_hab", "duplicado_de", "n_localidades_leidas", "nota",
            "archivo", "hoja", "url"]
    return a[cols].sort_values(["periodo", "localidad"]).reset_index(drop=True)


def tabla_vias(area_km2, area_urb, kmv, e24, e26) -> pd.DataFrame:
    t = pd.DataFrame(index=pd.Index([0] + list(range(1, 21)), name="localidad"))
    t["nombre"] = t.index.map({0: "Bogotá D.C.", **LOCALIDADES})
    t["area_km2"] = _con_bogota(area_km2)
    t["area_urbana_km2"] = _con_bogota(area_urb)
    t["km_via_ejes"] = _con_bogota(kmv["km_via_ejes"])
    t["km_via_urbana"] = _con_bogota(kmv["km_via_urbana"])
    t["densidad_via_km_km2"] = t["km_via_ejes"] / t["area_km2"]
    t["densidad_via_km_km2_urbano"] = t["km_via_urbana"] / t["area_urbana_km2"].where(t["area_urbana_km2"] > 0.5)
    for sufijo, e in (("2024_12", e24), ("2026_06", e26)):
        for c in e.columns:
            t[f"{c}_{sufijo}"] = e[c]
    t["densidad_km_carril_km2_urbano_2024_12"] = t["km_carril_2024_12"] / t["area_urbana_km2"].where(
        t["area_urbana_km2"] > 0.5)
    t["cambio_pp_pci_menor_56"] = t["pct_pci_menor_56_2026_06"] - t["pct_pci_menor_56_2024_12"]
    t["nota"] = ""
    t.loc[20, "nota"] = "Sumapaz: rural; el estado urbano del IDU no la cubre y no tiene suelo urbano"
    t.loc[0, "nota"] = ("PCI = Índice de Condición del Pavimento (ASTM D6433), ponderado por km-carril; "
                        "2024-12 clasifica la malla con el POT 190 y 2026-06 con el POT 555")
    return t.reset_index()


def _var(a, b):
    return (b / a - 1) * 100 if a and a > 0 else np.nan


# Columnas de la capa SCJ que no se usan (src/validacion_registro.py, contraste con el SIEDCO 2023-2025):
SCJ_NO_USAR = {"HM": "la columna 'motocicletas' repite caso por caso el hurto a comercio del SIEDCO desde 2023",
               "HCE": "la columna 'celulares' repite el hurto de motocicletas del SIEDCO desde 2023",
               "HC": "hurto a comercio no coincide con el SIEDCO en ningún año"}
ESTADO_SCJ = {"HA": "quiebre: 1,9-2,0 veces el SIEDCO en 2018-2022, igual desde 2023; solo comparable desde 2023",
              "HP": "quiebre: 2,3-2,6 veces el SIEDCO en 2018-2022, igual desde 2023; solo comparable desde 2023",
              "HB": "sin serie externa para validar; sin salto de nivel en 2023 (-2 %); tendencias, preferir desde 2023"}


def tabla_hurtos(scj: pd.DataFrame, pob) -> pd.DataFrame:
    anios = [2019, 2022, 2023, 2024, 2025, 2026]
    bog = scj[scj["localidad"] == 0].pivot_table(index="codigo", columns="anio", values="casos")
    quiebre = (bog[2023] / bog[2022] - 1)
    filas = []
    for cod in ["HA", "HB", "HP"]:
        roto = bool(quiebre[cod] < -0.30)
        for loc in [0] + list(range(1, 21)):
            s = scj[(scj["codigo"] == cod) & (scj["localidad"] == loc)].set_index("anio")["casos"]
            f = {"localidad": loc, "nombre": "Bogotá D.C." if loc == 0 else LOCALIDADES[loc], "codigo": cod,
                 "tipo": scj.loc[scj["codigo"] == cod, "tipo"].iat[0]}
            for a in anios:
                f[f"casos_{a}"] = s.get(a, np.nan)
                f[f"tasa_100k_{a}"] = s.get(a, np.nan) / _pob(pob, a).get(loc, np.nan) * 1e5
            for a0, a1 in ((2019, 2025), (2022, 2025), (2023, 2025), (2025, 2026)):
                f[f"var_pct_tasa_{a0}_{a1}"] = np.nan if (roto and a0 < 2023) else _var(f[f"tasa_100k_{a0}"],
                                                                                       f[f"tasa_100k_{a1}"])
            f["quiebre_serie_2023"] = roto
            f["comparable_desde"] = 2023 if roto else 2018
            f["estado_serie"] = ESTADO_SCJ[cod]
            f["nota"] = ("ventana ene-ago de cada año; tasas no anualizadas; " +
                         ("casos 2019 y 2022 en la escala vieja de la capa (no comparables): cambios desde 2019 y "
                          "2022 en blanco" if roto else "2025 = último año calendario cerrado; 2026 = último disponible"))
            filas.append(f)
    anotar("SCJ hurtos", "quiebre 2023", "variación Bogotá 2022→2023 (ene-ago): " +
           ", ".join(f"{c}: {v:+.0%}" for c, v in quiebre[["HP", "HA", "HM", "HB", "H"]].items()) +
           "; no se usan: " + ", ".join(f"{k} ({v})" for k, v in SCJ_NO_USAR.items()))
    return pd.DataFrame(filas)


def tabla_ciclo(ck: pd.DataFrame, scj: pd.DataFrame, pob) -> pd.DataFrame:
    t = pd.DataFrame(index=pd.Index([0] + list(range(1, 21)), name="localidad"))
    t["nombre"] = t.index.map({0: "Bogotá D.C.", **LOCALIDADES})
    for c in ("km_red_biciusuarios", "km_ciclorruta_exclusiva"):
        t[c] = _con_bogota(ck[c].reindex(range(1, 21)).fillna(0))
    t["km_ciclorruta_idu_2024"] = t.index.map(lambda l: IDU_CICLORRUTAS_2024.get(l, (np.nan,))[0])
    t.loc[0, "km_ciclorruta_idu_2024"] = 470.8
    t["pct_buen_estado_idu_2024"] = t.index.map(
        lambda l: sum(IDU_CICLORRUTAS_2024[l][1:]) if l in IDU_CICLORRUTAS_2024 else np.nan)
    hb = scj[scj["codigo"] == "HB"].pivot_table(index="localidad", columns="anio", values="casos")
    for a in (2022, 2023, 2025, 2026):
        t[f"hb_{a}"] = hb[a]
        t[f"hb_100k_{a}"] = hb[a] / _pob(pob, a) * 1e5
        t[f"hb_por_km_red_{a}"] = hb[a] / t["km_red_biciusuarios"].where(t["km_red_biciusuarios"] > 0)
        t[f"hb_por_km_exclusiva_{a}"] = hb[a] / t["km_ciclorruta_exclusiva"].where(t["km_ciclorruta_exclusiva"] > 0)
    for a0, a1 in ((2022, 2025), (2023, 2025), (2022, 2026)):
        t[f"var_pct_hb_100k_{a0}_{a1}"] = (t[f"hb_100k_{a1}"] / t[f"hb_100k_{a0}"] - 1) * 100
    t["var_pct_hb_casos_2022_2025"] = (t["hb_2025"] / t["hb_2022"] - 1) * 100
    t["nota"] = ("hurtos ene-ago (SCJ; HB sin serie externa para validar); km de la red a ago-2026 aplicados a todos "
                 "los años (la red de 2022 era más corta: el hurto por km de 2022 queda subestimado); "
                 "2025 = último año calendario cerrado")
    return t.reset_index()


def panel(sin, alum_t, vias, hurtos_scj, pob, bienal, ilum) -> pd.DataFrame:
    P = pd.DataFrame({"localidad": URBANAS})
    P["nombre"] = P["localidad"].map(LOCALIDADES)
    p25 = _pob(pob, ANIO_REF)
    P["poblacion_2025"] = P["localidad"].map(p25)
    for cod, nom in (("HP", "hp"), ("HA", "ha"), ("HB", "hb"), ("H", "homicidios")):
        s = hurtos_scj[hurtos_scj["codigo"] == cod].pivot_table(index="localidad", columns="anio", values="casos")
        t = {a: s[a] / _pob(pob, a) * 1e5 for a in (2023, 2024, 2025)}
        P[f"{nom}_100k_2025"] = P["localidad"].map(t[2025])
        P[f"{nom}_100k_2023_2025"] = P["localidad"].map((t[2023] + t[2024] + t[2025]) / 3)
    ult = alum_t[(alum_t["periodo"] == alum_t["periodo"].max()) & (alum_t["localidad"] > 0)].set_index("localidad")
    for c in ("luminarias_km2_urbano", "luminarias_km_via", "luminarias_km_carril", "luminarias_1000_hab", "pct_led"):
        P[f"{c}_2024_05"] = P["localidad"].map(ult[c])
    v = vias.set_index("localidad")
    for c in ("pct_pci_menor_56_2024_12", "pci_medio_2024_12", "densidad_via_km_km2_urbano",
              "pct_pci_menor_56_2026_06"):
        P[c] = P["localidad"].map(v[c])
    s = sin[sin["localidad"] > 0]
    piv = lambda c: s.pivot_table(index="localidad", columns="anio", values=c)  # noqa: E731
    m = piv("tasa_muertes_inmlcf_100k")
    P["muertes_via_100k_2025"] = P["localidad"].map(m[2025])
    P["muertes_via_100k_2023_2025"] = P["localidad"].map(m[[2023, 2024, 2025]].mean(axis=1))
    P["lesionados_via_100k_2025"] = P["localidad"].map(piv("tasa_lesionados_sdm_100k")[2025])
    P["lesionados_via_100k_2023_2025"] = P["localidad"].map(piv("tasa_lesionados_sdm_100k")[[2023, 2024, 2025]].mean(axis=1))
    P["alumbrado_malo_bienal_2025"] = P["localidad"].map(bienal)
    for c in ilum.columns:
        P[c] = P["localidad"].map(ilum[c])
    return P


# =================================================================== pruebas de hipótesis
def _corr_filas(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Correlación de Pearson fila por fila (sobre rangos = Spearman)."""
    a = a - a.mean(axis=1, keepdims=True)
    b = b - b.mean(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (a * b).sum(axis=1) / np.sqrt((a ** 2).sum(axis=1) * (b ** 2).sum(axis=1))


def _spearman(x, y) -> float:
    from scipy.stats import rankdata

    return float(_corr_filas(rankdata(x)[None, :], rankdata(y)[None, :])[0])


def _bh(p: pd.Series) -> pd.Series:
    p = p.astype(float)
    n = p.notna().sum()
    orden = p.sort_values()
    adj = (orden * n / np.arange(1, len(orden) + 1)).iloc[::-1].cummin().iloc[::-1].clip(upper=1)
    return adj.reindex(p.index)


BLOQUES = {
    "1 alumbrado (inventario UAESP may-2024)": {
        "x": [("luminarias_km2_urbano_2024_05", "luminarias por km² urbano", "-"),
              ("luminarias_km_via_2024_05", "luminarias por km de vía", "-")],
        "y": ["hp", "ha", "hb"]},
    "2 malla vial (IDU dic-2024 e IDECA)": {
        "x": [("pct_pci_menor_56_2024_12", "% km-carril con PCI < 56", "+"),
              ("densidad_via_km_km2_urbano", "km de vía por km² urbano", "sin signo previo")],
        "y": ["hp", "ha", "hb"]},
    "3 siniestralidad vial": {
        "x": [("muertes_via_100k", "muertes en vía por 100.000 (INMLCF)", "+")],
        "y": ["hp", "ha", "hb", "homicidios"],
        "extra": [("homicidios", "lesionados_via_100k", "heridos en vía por 100.000 (SDM)", "+")]},
    "4 sensibilidad: calidad del alumbrado (percepción y auditoría)": {
        "x": [("alumbrado_malo_bienal_2025", "% que califica malo el alumbrado (Bienal 2025)", "+"),
              ("iluminacion_deficiente_2019", "% de puntos con iluminación ninguna o poca (SDMujer 2019)", "+")],
        "y": ["hp", "ha", "hb"]},
}
NOMBRE_Y = {"hp": "hurto a personas", "ha": "hurto de automotores", "hb": "hurto de bicicletas",
            "homicidios": "homicidios"}


def _pares(b: dict) -> list[tuple]:
    pares = [(y, xcol, xnom, signo) for xcol, xnom, signo in b["x"] for y in b["y"]]
    return pares + list(b.get("extra", []))


def pruebas(P: pd.DataFrame) -> pd.DataFrame:
    """Spearman entre localidades; IC 95 % bootstrap percentil; p bilateral por permutación; BH por bloque."""
    from scipy.stats import rankdata

    rng = np.random.default_rng(SEMILLA)
    filas = []
    especs = (("principal: hurtos 2025", "2025", P),
              ("sensibilidad: promedio 2023-2025", "2023_2025", P),
              ("sensibilidad: promedio 2023-2025 sin el centro (n = 15)", "2023_2025", P[~P["localidad"].isin(CENTRO)]))
    for espec, suf_y, datos in especs:
        for bloque, b in BLOQUES.items():
            for y, xcol, xnom, signo in _pares(b):
                yc = f"{y}_100k_{suf_y}"
                xc = xcol if xcol in P else f"{xcol}_{suf_y}"
                d = datos[[yc, xc]].dropna()
                x, yv = d[xc].to_numpy(float), d[yc].to_numpy(float)
                m = len(d)
                rho = _spearman(x, yv)
                idx = rng.integers(0, m, size=(B_BOOT, m))
                boot = _corr_filas(rankdata(x[idx], axis=1), rankdata(yv[idx], axis=1))
                rx, ry = rankdata(x), rankdata(yv)
                perm = np.argsort(rng.random((B_PERM, m)), axis=1)
                rperm = _corr_filas(np.broadcast_to(rx, (B_PERM, m)), ry[perm])
                p = (1 + np.sum(np.abs(rperm) >= abs(rho) - 1e-12)) / (1 + B_PERM)
                filas.append({"especificacion": espec, "bloque": bloque, "y": yc, "y_nombre": NOMBRE_Y[y] + " por 100.000",
                              "x": xc, "x_nombre": xnom, "signo_esperado": signo, "n": m, "rho": rho,
                              "ic95_inf": np.nanpercentile(boot, 2.5), "ic95_sup": np.nanpercentile(boot, 97.5),
                              "p_permutacion": p})
    t = pd.DataFrame(filas)
    t["p_bh_bloque"] = t.groupby(["especificacion", "bloque"])["p_permutacion"].transform(_bh)

    def lectura(r):
        sig = r["p_bh_bloque"] < 0.05
        if r["signo_esperado"] in ("+", "-"):
            a_favor = (r["rho"] > 0) == (r["signo_esperado"] == "+")
            sentido = "en el sentido de la hipótesis" if a_favor else "en sentido contrario a la hipótesis"
        else:
            sentido = "positiva" if r["rho"] > 0 else "negativa"
        if sig:
            return f"significativa tras BH ({sentido})"
        if r["p_permutacion"] < 0.05:
            return f"p < 0,05 sin ajustar, no sobrevive a BH ({sentido})"
        return f"no significativa ({sentido})"

    t["lectura"] = t.apply(lectura, axis=1)
    return t


# =================================================================== ficha de confiabilidad
def ficha_confiabilidad(meta, sin, alum, e24, e26, kmv_n, ck, diag, ilum_n, scj) -> pd.DataFrame:
    c = lambda clave: FUENTES_MOV[clave]  # noqa: E731
    sdm = pd.read_csv(CRUDOS / FUENTES_MOV["sdm_sigat_conteos"]["archivo"])
    sdm = sdm[sdm["anio"].between(2015, 2026)]
    nsdm = sdm.groupby("capa")["n_sin_aa"].sum()
    filas = [
        {"fuente": "Mortalidad por accidentes de tránsito", "entidad": c("sds_mortalidad_transito")["entidad"],
         "anios_disponibles": "2015-2026 (2026 ene-jun)", "periodicidad": "semestral", "tipo": "registro administrativo",
         "n_registros": int(sin.loc[sin["localidad"] == 0, "muertes_inmlcf"].sum()),
         "nivel_territorial_mas_fino": "localidad del hecho", "ultima_actualizacion": meta.get("sds_mortalidad_transito"),
         "anios_faltantes": "2026 jul-dic; antes de 2015 no publicado",
         "advertencia": "cada muerte viene dos veces (código 0 y localidad); 8 % 'sin dato' de localidad en 2022-2024; cifras preliminares recientes"},
        {"fuente": "Siniestralidad_BD (muertos)", "entidad": c("sdm_sigat_conteos")["entidad"],
         "anios_disponibles": "2007-2026 (2026 ene-sep)", "periodicidad": "continua (servicio ArcGIS)",
         "tipo": "registro administrativo (IPAT)", "n_registros": int(nsdm.get("muertos", 0)),
         "nivel_territorial_mas_fino": "punto (lat/lon)", "ultima_actualizacion": "consulta " + meta.get("consultado", "")[:10],
         "anios_faltantes": "ninguno 2015-2025",
         "advertencia": "2007-2020 duplicado (formularios 'A' y 'AA'); cuenta muertes en el sitio y posteriores registradas por la SDM, menos que el INMLCF"},
        {"fuente": "Siniestralidad_BD (lesionados)", "entidad": c("sdm_sigat_conteos")["entidad"],
         "anios_disponibles": "2007-2026 (2026 ene-sep)", "periodicidad": "continua (servicio ArcGIS)",
         "tipo": "registro administrativo (IPAT)", "n_registros": int(nsdm.get("lesionados", 0)),
         "nivel_territorial_mas_fino": "punto (lat/lon)", "ultima_actualizacion": "consulta " + meta.get("consultado", "")[:10],
         "anios_faltantes": "ninguno 2015-2025",
         "advertencia": "duplicado 'AA' hasta 2020; 8-10 % menos heridos que el consolidado del portal 2015-2019; solo lo que registra la policía de tránsito"},
        {"fuente": "Siniestralidad_BD (siniestros)", "entidad": c("sdm_sigat_conteos")["entidad"],
         "anios_disponibles": "2007-2026 (2026 ene-sep)", "periodicidad": "continua (servicio ArcGIS)",
         "tipo": "registro administrativo (IPAT)", "n_registros": int(nsdm.get("siniestros", 0)),
         "nivel_territorial_mas_fino": "punto (lat/lon) y calzada", "ultima_actualizacion": "consulta " + meta.get("consultado", "")[:10],
         "anios_faltantes": "ninguno 2015-2025",
         "advertencia": "'solo daños' deja de registrarse en 2023 (-91 %); usar solo con heridos o muertos"},
        {"fuente": "Histórico siniestros Bogotá D.C. (control)", "entidad": "SDM",
         "anios_disponibles": "2015-2021 (2021 parcial)", "periodicidad": "única (publicado oct-2021)",
         "tipo": "registro administrativo", "n_registros": 199146, "nivel_territorial_mas_fino": "punto",
         "ultima_actualizacion": meta.get("sdm_historico_siniestros"), "anios_faltantes": "2022 en adelante",
         "advertencia": "solo se usa como suma de control del SIGAT"},
        {"fuente": "Inventario de luminarias (modelo de prestación AP)", "entidad": "UAESP (datos del operador ENEL-CODENSA)",
         "anios_disponibles": f"{alum['periodo'].min()} a {alum['periodo'].max()}", "periodicidad": "mensual (con huecos)",
         "tipo": "inventario", "n_registros": int(alum["periodo"].nunique()),
         "nivel_territorial_mas_fino": "localidad (UPZ solo en 2022)", "ultima_actualizacion": meta.get("uaesp_alumbrado"),
         "anios_faltantes": "jun-2024 en adelante; 2020 solo abril; 2018-2019 con huecos",
         "advertencia": "15 conjuntos con formatos distintos y fechas internas inconsistentes; las luminarias del Distrito (~2 %) solo vienen por localidad en algunos cortes; mide cantidad, no si encienden"},
        {"fuente": "Estado de la malla vial urbana (PCI) jun-2026", "entidad": "IDU",
         "anios_disponibles": "corte jun-2026 (POT 555)", "periodicidad": "semestral",
         "tipo": "inventario técnico (capa geográfica)", "n_registros": int(e26.attrs.get("n", 0)),
         "nivel_territorial_mas_fino": "calzada", "ultima_actualizacion": meta.get("idu_estado_malla_2026_06"),
         "anios_faltantes": "cortes anteriores no publicados como datos abiertos salvo dic-2024",
         "advertencia": "el PCI de cada calzada puede tener años de antigüedad (la inspección no es anual); clasificación de malla del POT 555"},
        {"fuente": "Estado de la malla vial urbana (PCI) dic-2024", "entidad": "IDU",
         "anios_disponibles": "corte dic-2024 (POT 190)", "periodicidad": "semestral",
         "tipo": "inventario técnico (capa geográfica)", "n_registros": int(e24.attrs.get("n", 0)),
         "nivel_territorial_mas_fino": "calzada", "ultima_actualizacion": meta.get("idu_estado_malla_2024_12"),
         "anios_faltantes": "-", "advertencia": "clasificación de malla del POT 190: no comparable por tipo de malla con jun-2026"},
        {"fuente": "Estado superficial Bogotá D.C. (portal)", "entidad": "IDU",
         "anios_disponibles": str(diag.get("fecha_estado", "")), "periodicidad": "irregular", "tipo": "tabla sin geometría",
         "n_registros": diag.get("registros"), "nivel_territorial_mas_fino": "calzada (sin localidad)",
         "ultima_actualizacion": meta.get("idu_estado_superficial_portal"), "anios_faltantes": "-",
         "advertencia": f"no usable: el código coincide con el tipo de superficie en {diag.get('coincide_con_tipo_superficie', 'n.d.')} de los casos"},
        {"fuente": "Malla vial (ejes)", "entidad": c("ideca_malla_vial")["entidad"], "anios_disponibles": "versión vigente",
         "periodicidad": "trimestral", "tipo": "capa geográfica", "n_registros": kmv_n,
         "nivel_territorial_mas_fino": "segmento vial", "ultima_actualizacion": meta.get("ideca_mapa_referencia"),
         "anios_faltantes": "sin serie histórica en el servicio", "advertencia": "no trae estado; geometría simplificada a 1 m en la descarga"},
        {"fuente": "Red de biciusuarios y ciclorrutas", "entidad": "IDU", "anios_disponibles": "versión vigente (ago-2026)",
         "periodicidad": "trimestral", "tipo": "capa geográfica", "n_registros": int(ck.attrs.get("n", 0)),
         "nivel_territorial_mas_fino": "segmento", "ultima_actualizacion": meta.get("idu_red_biciusuarios"),
         "anios_faltantes": "versiones previas solo como SHP 7z", "advertencia": "el dominio de RBICLASE no está publicado; la clasificación exclusiva sale del cruce con el polígono de ciclorruta"},
        {"fuente": "Infografía extensión y estado ciclorrutas 2024-II", "entidad": "IDU · DTINI",
         "anios_disponibles": "dic-2024", "periodicidad": "semestral", "tipo": "reporte (PDF)", "n_registros": 19,
         "nivel_territorial_mas_fino": "localidad", "ultima_actualizacion": "2024-12-31",
         "anios_faltantes": "-", "advertencia": "transcrito a mano del PDF; sirve de contraste de los km calculados"},
        {"fuente": "Delitos de alto impacto (HA, HB, HP, H)", "entidad": "SCJ", "anios_disponibles": "2018-2026 (ene-ago)",
         "periodicidad": "mensual (ventana ene-ago publicada)", "tipo": "registro administrativo (SIEDCO)",
         "n_registros": int(scj[(scj["localidad"] == 0) & scj["codigo"].isin(["HA", "HM", "HB", "HP", "H"])]["casos"].sum()),
         "nivel_territorial_mas_fino": "localidad", "ultima_actualizacion": meta.get("scj_delitos"),
         "anios_faltantes": "sep-dic de cada año; antes de 2018",
         "advertencia": "HP y HA en escala 2-2,6 veces el SIEDCO hasta 2022 (comparables solo desde 2023); HM, HCE y HC con etiquetas cruzadas, no se usan; HB sin validar; tasas por residente inflan el centro (población flotante)"},
        {"fuente": "Auditoría de seguridad nocturna para las mujeres", "entidad": "Secretaría Distrital de la Mujer",
         "anios_disponibles": "olas nov-2015/feb-2016 y sep-2019", "periodicidad": "irregular (2 olas)",
         "tipo": "observación en campo", "n_registros": ilum_n, "nivel_territorial_mas_fino": "punto",
         "ultima_actualizacion": meta.get("sdmujer_seguridad_nocturna"), "anios_faltantes": "2020 en adelante",
         "advertencia": "la ola 2019 es anterior a casi toda la modernización LED (2020-2024); recorridos por vías elegidas, no muestra aleatoria; el GeoJSON publicado viene sin atributos (usar el GPKG)"},
    ]
    return pd.DataFrame(filas)


# =================================================================== orquestación
def main(forzar: bool = False):
    import geopandas as gpd  # noqa: F401  (falla temprano si no está)
    import pyogrio

    t0 = time.time()
    print("Frente de vías, movilidad y alumbrado")
    for clave in FUENTES_MOV:
        obtener_mov(clave, forzar)
    obtener_alumbrado(forzar)
    meta = metadatos(forzar)
    pob = poblacion()

    print("· Siniestralidad")
    sin = tabla_siniestros(pob, meta)

    print("· Geometría")
    locs = localidades_geo()
    area_km2 = locs.set_index("localidad")["LocArea"] / 1e6
    urb, area_urb = suelo_urbano(locs)
    kmv = km_via(locs, urb)
    ck = ciclo_km(locs)

    print("· Malla vial")
    e24, e26 = estado_malla("idu_estado_malla_2024_12"), estado_malla("idu_estado_malla_2026_06")
    e24.attrs["n"] = len(pd.read_csv(CRUDOS / FUENTES_MOV["idu_estado_malla_2024_12"]["archivo"]))
    e26.attrs["n"] = len(pd.read_csv(CRUDOS / FUENTES_MOV["idu_estado_malla_2026_06"]["archivo"]))
    diag = diagnostico_estado_superficial()
    vias = tabla_vias(area_km2, area_urb, kmv, e24, e26)

    print("· Alumbrado")
    alum = leer_alumbrado()
    alum_t = tabla_alumbrado(alum, pob, area_km2, area_urb, kmv, e24["km_carril"])

    print("· Hurtos y ciclo")
    scj = scj_delitos()
    hurtos = tabla_hurtos(scj, pob)
    ciclo = tabla_ciclo(ck, scj, pob)
    ck.attrs["n"] = len(json.loads((CRUDOS / FUENTES_MOV["idu_red_biciusuarios"]["archivo"]).read_text(encoding="utf-8"))["features"])

    print("· Pruebas")
    bienal = pd.read_csv(PROC / "panel_localidad_2025.csv").set_index("localidad")["alumbrado_malo"]
    ilum = iluminacion_auditoria()
    P = panel(sin, alum_t, vias, scj, pob, bienal, ilum)
    res = pruebas(P)

    kmv_n = len(json.loads((CRUDOS / FUENTES_MOV["ideca_malla_vial"]["archivo"]).read_text(encoding="utf-8"))["features"])
    ilum_n = int(pyogrio.read_info(CRUDOS / FUENTES_MOV["sdmujer_seguridad_nocturna"]["archivo"])["features"])
    conf = ficha_confiabilidad(meta, sin, alum, e24, e26, kmv_n, ck, diag, ilum_n, scj)

    salidas = {"movilidad_siniestros_localidad_anio.csv": sin, "alumbrado_localidad_anio.csv": alum_t,
               "ciclo_localidad.csv": ciclo, "vias_localidad.csv": vias, "hurtos_vehiculos_localidad.csv": hurtos,
               "movilidad_panel_localidad.csv": P, "movilidad_pruebas_hipotesis.csv": res,
               "confiabilidad_movilidad.csv": conf}
    for nombre, df in salidas.items():
        df.to_csv(PROC / nombre, index=False, encoding="utf-8")
        print(f"  ✓ {nombre}: {len(df)} filas")
    pd.DataFrame(BITACORA).to_csv(PROC / "movilidad_bitacora.csv", index=False, encoding="utf-8")

    propios = [CRUDOS / f["archivo"] for f in FUENTES_MOV.values()] + list(ALUMBRADO_DIR.glob("*"))
    grandes = [(p.name, round(p.stat().st_size / 1e6, 1)) for p in propios if p.exists() and p.stat().st_size > 50e6]
    if grandes:
        print(f"  ! crudos de más de 50 MB: {grandes}")
    print(f"Listo en {time.time() - t0:.0f} s")
    return salidas


if __name__ == "__main__":
    main(forzar="--forzar" in sys.argv)
