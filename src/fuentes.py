"""
Fuentes públicas: descarga desde los servicios oficiales con caché local.

Cada fuente se baja una sola vez a data/crudos/ y queda registrada en
data/crudos/registro_descargas.csv (url, fecha, tamaño, sha1). Si el archivo ya
existe, se usa la copia local: el análisis se puede repetir sin red.

Todas las fuentes son del Distrito (Portal de Datos Abiertos de Bogotá y
servicios ArcGIS de las entidades) salvo la Encuesta Mundial de Valores, que la
Alcaldía publica en el portal Datos para la Transparencia.
"""
import csv
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
CRUDOS = RAIZ / "data" / "crudos"
UA = {"User-Agent": "DataJam5-TheDataSquad/1.0 (investigacion academica)"}
CKAN = "https://datosabiertos.bogota.gov.co/api/3/action"
SCJ = "https://oaiee.scj.gov.co/agc/rest/services/Tematicos_Pub/CifrasSCJ/MapServer"

FUENTES = {
    "scj_delitos_localidad": {
        "entidad": "Secretaría Distrital de Seguridad, Convivencia y Justicia (SCJ)",
        "conjunto": "Delito de Alto Impacto. Bogotá D.C.",
        "url": f"{SCJ}/0", "tipo": "arcgis", "archivo": "scj_delitos_alto_impacto_localidad.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/delito-de-alto-impacto-bogota-d-c",
    },
    "scj_incidentes_localidad": {
        "entidad": "SCJ (Línea 123, NUSE)", "conjunto": "Incidentes Reportados por localidad",
        "url": f"{SCJ}/2", "tipo": "arcgis", "archivo": "scj_incidentes_123_localidad.csv",
        "portal": "https://oaiee.scj.gov.co/agc/rest/services/Tematicos_Pub/CifrasSCJ/MapServer/2",
    },
    "scj_incidentes_upz": {
        "entidad": "SCJ (Línea 123, NUSE)", "conjunto": "Incidentes Reportados por UPZ",
        "url": f"{SCJ}/3", "tipo": "arcgis_geo", "archivo": "scj_incidentes_123_upz.geojson",
        "portal": "https://oaiee.scj.gov.co/agc/rest/services/Tematicos_Pub/CifrasSCJ/MapServer/3",
    },
    "ebcc_2025": {
        "entidad": "Secretaría de Cultura, Recreación y Deporte · Observatorio de Culturas",
        "conjunto": "Encuesta Bienal de Cultura Ciudadana 2025 (módulo cultura ciudadana)",
        "url": "https://drive.usercontent.google.com/download?id=1nCsuCpG7YJ-PQ7ilHtNdGahIDfNHcHDT&export=download&confirm=t",
        "tipo": "archivo", "archivo": "ebcc_2025_cultura_ciudadana.xlsx",
        "portal": "https://observatoriocultura.github.io/observatorio/#/ebc/encuesta-cultura-ciudadana-2025",
    },
    "emv_2024": {
        "entidad": "Alcaldía de Bogotá · Datos para la Transparencia (EMV Colombia, ola 8)",
        "conjunto": "Encuesta Mundial de Valores ola 8, 2024",
        "url": "https://gobiernoabiertobogota.gov.co/assets/docs/downloads/ENCUESTA_MUNDIAL_DE_VALORES_OLA_8_2024.xlsx",
        "tipo": "archivo", "archivo": "emv_ola8_2024.xlsx",
        "portal": "https://gobiernoabiertobogota.gov.co/transparencia",
    },
    "sdp_poblacion_localidad": {
        "entidad": "Secretaría Distrital de Planeación (SDP)",
        "conjunto": "Proyecciones y retroproyecciones de población por localidad 2005-2035",
        "url": "https://datosabiertos.bogota.gov.co/dataset/0f1fb76a-1595-43d5-9257-0abcc3db908a/resource/5669484f-dc1d-4457-b1d1-de0a3825b41c/download/202503_localidad_proyeccion_retroproyeccion_poblacion_2005_2035.ods",
        "tipo": "archivo", "archivo": "sdp_poblacion_localidad_2005_2035.ods",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035",
    },
    "sdp_poblacion_upz": {
        "entidad": "Secretaría Distrital de Planeación (SDP)",
        "conjunto": "Proyecciones y retroproyecciones de población por UPZ 2005-2035",
        "url": "https://datosabiertos.bogota.gov.co/dataset/0f1fb76a-1595-43d5-9257-0abcc3db908a/resource/96583ea9-9c0b-40c3-9797-156d173eb734/download/202503_upz_proyeccion_retroproyeccion_poblacion_2005_2035.ods",
        "tipo": "archivo", "archivo": "sdp_poblacion_upz_2005_2035.ods",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035",
    },
    "ideca_localidades": {
        "entidad": "UAECD · IDECA", "conjunto": "Localidad. Bogotá D.C.",
        "url": "https://datosabiertos.bogota.gov.co/dataset/856cb657-8ca3-4ee8-857f-37211173b1f8/resource/497b8756-0927-4aee-8da9-ca4e32ca3a8a/download/loca.json",
        "tipo": "archivo", "archivo": "ideca_localidades.geojson",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/localidad-bogota-d-c",
    },
    "uaesp_alumbrado": {
        "entidad": "Unidad Administrativa Especial de Servicios Públicos (UAESP)",
        "conjunto": "Alumbrado público: luminarias por localidad y tecnología (corte agosto 2019, el último publicado)",
        "url": "https://datosabiertos.bogota.gov.co/dataset/9bfb08ba-14d3-45e3-9ae8-2e96b59565c9/resource/cb3a42bd-72ec-4625-a004-55f7fc4dd7da/download/agosto-2019-sap-lt.csv",
        "tipo": "archivo", "archivo": "uaesp_alumbrado_2019_08.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/alumbrado_publico_lt",
    },
    "dadep_espacio_publico": {
        "entidad": "Departamento Administrativo de la Defensoría del Espacio Público (DADEP)",
        "conjunto": "Indicador de espacio público efectivo por localidad",
        "url": "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/espaciopublico/indicadorespaciopublico/MapServer",
        "tipo": "arcgis_capa_nombre", "capa": "Efectivo por Localidad", "archivo": "dadep_ep_efectivo_localidad.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/indicador-espacio-publico-localidad-bogota-d-c",
    },
}


def _registrar(clave: str, ruta: Path, url: str):
    """Anota cada descarga en data/crudos/registro_descargas.csv con su URL, fecha, tamaño y huella sha1."""
    reg = CRUDOS / "registro_descargas.csv"
    nuevo = not reg.exists()
    sha = hashlib.sha1(ruta.read_bytes()).hexdigest()
    with reg.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fuente", "archivo", "url", "descargado", "bytes", "sha1"])
        w.writerow([clave, ruta.name, url, datetime.now().isoformat(timespec="seconds"), ruta.stat().st_size, sha])


def _get(url: str, **kw) -> requests.Response:
    """Hace la petición HTTP con reintentos y espera creciente, para tolerar fallas de los servicios oficiales."""
    for intento in range(4):
        try:
            r = requests.get(url, timeout=(20, 300), headers=UA, **kw)
            r.raise_for_status()
            return r
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(3 * (intento + 1))
    raise RuntimeError(f"No respondió: {url}")


def _arcgis_atributos(url: str) -> pd.DataFrame:
    """Descarga todos los atributos de una capa ArcGIS (paginando) y devuelve una tabla con nombres legibles."""
    meta = _get(url, params={"f": "json"}).json()
    nombres = {f["name"]: f.get("alias") or f["name"] for f in meta.get("fields", [])}
    d = _get(f"{url}/query", params={"where": "1=1", "outFields": "*", "returnGeometry": "false", "f": "json"}).json()
    df = pd.DataFrame([f["attributes"] for f in d.get("features", [])])
    df.attrs["alias"] = nombres
    return df


def _arcgis_geojson(url: str) -> dict:
    """Polígonos simplificados (~20 m) en WGS84, por lotes para no exceder el límite del servicio."""
    ids = _get(f"{url}/query", params={"where": "1=1", "returnIdsOnly": "true", "f": "json"}).json()["objectIds"]
    feats = []
    for i in range(0, len(ids), 100):
        lote = ",".join(map(str, sorted(ids)[i:i + 100]))
        r = requests.post(f"{url}/query", data={"objectIds": lote, "outFields": "*", "returnGeometry": "true",
                                                "outSR": "4326", "maxAllowableOffset": "0.0002", "f": "geojson"},
                          timeout=(20, 300), headers=UA)
        r.raise_for_status()
        feats += r.json()["features"]
    return {"type": "FeatureCollection", "features": feats}


def obtener(clave: str, forzar: bool = False) -> Path:
    """Devuelve la ruta local de la fuente; la descarga si no está en caché."""
    f = FUENTES[clave]
    ruta = CRUDOS / f["archivo"]
    if ruta.exists() and not forzar:
        return ruta
    CRUDOS.mkdir(parents=True, exist_ok=True)
    tipo = f["tipo"]
    if tipo == "archivo":
        ruta.write_bytes(_get(f["url"]).content)
    elif tipo == "arcgis":
        _arcgis_atributos(f["url"]).to_csv(ruta, index=False, encoding="utf-8")
    elif tipo == "arcgis_geo":
        ruta.write_text(json.dumps(_arcgis_geojson(f["url"]), ensure_ascii=False), encoding="utf-8")
    elif tipo == "arcgis_capa_nombre":
        servicio = _get(f["url"], params={"f": "json"}).json()
        capa = next(c["id"] for c in servicio["layers"] if c["name"] == f["capa"])
        _arcgis_atributos(f"{f['url']}/{capa}").to_csv(ruta, index=False, encoding="utf-8")
    elif tipo == "ckan_ultimo":
        paquete = _get(f"{CKAN}/package_show", params={"id": f["url"].split(":", 1)[1]}).json()["result"]
        csvs = [r for r in paquete["resources"] if (r.get("format") or "").upper() == "CSV"
                and "metadata" not in (r.get("name") or "").lower()]
        ultimo = max(csvs, key=lambda r: r.get("created") or "")
        ruta.write_bytes(_get(ultimo["url"]).content)
        f["url"] = ultimo["url"]
    _registrar(clave, ruta, f["url"])
    return ruta


def obtener_todas(forzar: bool = False) -> pd.DataFrame:
    """Baja cada fuente que falte (o todas si forzar=True) y devuelve el inventario con entidad, archivo y tamaño."""
    filas = []
    for clave, f in FUENTES.items():
        t0 = time.time()
        ruta = obtener(clave, forzar)
        filas.append({"fuente": clave, "entidad": f["entidad"], "conjunto": f["conjunto"],
                      "archivo": ruta.name, "MB": round(ruta.stat().st_size / 1e6, 2),
                      "segundos": round(time.time() - t0, 1), "portal": f["portal"]})
    return pd.DataFrame(filas)
