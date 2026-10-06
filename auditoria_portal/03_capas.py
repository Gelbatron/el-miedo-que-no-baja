"""
03 - Capas geográficas: atributos de los conjuntos que SOLO existen como mapa.

Unos 550 conjuntos del portal no traen CSV/Excel, solo servicios ArcGIS REST
(con indicadores por localidad/UPL dentro de la tabla de atributos). Aquí se
consulta cada capa con `query`, se trae la tabla completa por lotes de
objectIds y se guarda en `capas.duckdb`:
  - capas de puntos: atributos + lon/lat (EPSG:4326)
  - polígonos y líneas: solo atributos (la geometría pesada no hace falta
    para cruzar por código de localidad/UPL; los límites oficiales se bajan
    aparte en 04_limites.py)

Uso: python scripts/03_capas.py [--max-filas 300000]
Reanudable: salta capas ya registradas en `manifiesto_capas`.
"""
import argparse
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import duckdb
import pandas as pd
import requests
from unidecode import unidecode

STORE = Path(os.environ.get("DATOS_BOGOTA_STORE", "C:/Users/rafal/datos-bogota"))
DB = STORE / "capas.duckdb"
TABULARES = {"CSV", "XLSX", "XLS", "ODS", "JSON", "TXT"}
REST = {"ESRI REST", "ARCGIS GEOSERVICES REST API", "REST"}
UA = {"User-Agent": "DataJam5-TheDataSquad/1.0 (investigacion academica)"}
LOTE_IDS = 500


def pedir(url: str, post: bool = False, **params) -> dict:
    params.setdefault("f", "json")
    for intento in range(3):
        try:
            if post:  # listas largas de objectIds no caben en la URL (error 400 del servidor)
                r = requests.post(url, data=params, timeout=(20, 180), headers=UA)
            else:
                r = requests.get(url, params=params, timeout=(20, 120), headers=UA)
            r.raise_for_status()
            d = r.json()
            if "error" in d:
                raise RuntimeError(str(d["error"])[:200])
            return d
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(3 * (intento + 1))
    raise RuntimeError("sin respuesta del servidor")


def capas_de(url: str) -> list[str]:
    """Una URL puede ser la capa (…/MapServer/3) o el servicio (…/MapServer)."""
    url = url.split("?")[0].rstrip("/")
    if re.search(r"/(MapServer|FeatureServer)/\d+$", url):
        return [url]
    meta = pedir(url)
    return [f"{url}/{c['id']}" for c in meta.get("layers", []) if not c.get("subLayerIds")]


def bajar_capa(url: str, max_filas: int) -> tuple[pd.DataFrame, dict]:
    meta = pedir(url)
    geom = meta.get("geometryType") or ""
    info = {"capa": meta.get("name", ""), "geometria": geom}
    ids = pedir(f"{url}/query", where="1=1", returnIdsOnly="true").get("objectIds") or []
    ids = sorted(ids)[:max_filas]
    info["total_ids"] = len(ids)
    puntos = geom == "esriGeometryPoint"
    partes = []
    tope = int(meta.get("maxRecordCount") or 1000)
    if len(ids) <= min(tope, 1000):  # capa chica (p. ej. 20 localidades): una sola consulta
        d = pedir(f"{url}/query", where="1=1", outFields="*", returnGeometry="true" if puntos else "false", outSR="4326")
        filas = []
        for f in d.get("features", []):
            a = dict(f.get("attributes", {}))
            if puntos and f.get("geometry"):
                a["lon"], a["lat"] = f["geometry"].get("x"), f["geometry"].get("y")
            filas.append(a)
        return pd.DataFrame(filas), info
    for i in range(0, len(ids), LOTE_IDS):
        lote = ids[i:i + LOTE_IDS]
        d = pedir(f"{url}/query", post=True, objectIds=",".join(map(str, lote)), outFields="*",
                  returnGeometry="true" if puntos else "false", outSR="4326")
        filas = []
        for f in d.get("features", []):
            a = dict(f.get("attributes", {}))
            if puntos and f.get("geometry"):
                a["lon"], a["lat"] = f["geometry"].get("x"), f["geometry"].get("y")
            filas.append(a)
        partes.append(pd.DataFrame(filas))
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    return df, info


def nombre_tabla(dataset: str, url: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", unidecode(dataset).lower()).strip("_")[:50]
    capa = re.search(r"/(\d+)$", url).group(1)
    return f"g_{base}__{capa}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-filas", type=int, default=300_000)
    ap.add_argument("--hilos", type=int, default=8)
    ap.add_argument("--db", default="capas.duckdb")
    ap.add_argument("--reintentar-de", default="", help="base cuyas capas fallidas se reintentan")
    ap.add_argument("--patron", default="", help="regex sobre el nombre del conjunto (prioridades)")
    args = ap.parse_args()

    r = pd.read_csv(STORE / "catalogo" / "recursos.csv", dtype=str).fillna("")
    con_tabla = set(r[r["formato"].str.replace(".", "", regex=False).isin(TABULARES)]["dataset_id"])
    rest = r[r["formato"].isin(REST) & ~r["dataset_id"].isin(con_tabla)].drop_duplicates(["dataset_id", "url"])
    if args.patron:
        rest = rest[rest["dataset"].str.contains(args.patron, regex=True)]

    solo_urls = None
    if args.reintentar_de:
        previa = duckdb.connect(str(STORE / args.reintentar_de), read_only=True)
        fall = previa.execute("SELECT url FROM manifiesto_capas WHERE error <> ''").df()["url"]
        previa.close()
        solo_urls = set(fall)
        rest = rest[rest["url"].isin(solo_urls) | rest["url"].map(lambda u: any(f.startswith(u.split("?")[0].rstrip("/")) for f in solo_urls))]
        print(f"Reintentos: {len(solo_urls)} capas/servicios fallidos")
    con = duckdb.connect(str(STORE / args.db))
    con.execute("""CREATE TABLE IF NOT EXISTS manifiesto_capas (dataset VARCHAR, entidad VARCHAR, grupos VARCHAR,
        url VARCHAR, capa VARCHAR, geometria VARCHAR, tabla VARCHAR, filas BIGINT, total_ids BIGINT,
        lista_columnas VARCHAR, error VARCHAR, cargado_en TIMESTAMP DEFAULT now())""")
    hechas = {x[0] for x in con.execute("SELECT url FROM manifiesto_capas WHERE error = ''").fetchall()}
    con.execute("DELETE FROM manifiesto_capas WHERE error <> ''")

    # 1) expandir servicios a capas
    tareas = []
    for fila in rest.to_dict("records"):
        try:
            for capa in capas_de(fila["url"]):
                if capa not in hechas and (solo_urls is None or capa in solo_urls or fila["url"] in solo_urls):
                    tareas.append({**fila, "capa_url": capa})
        except Exception as e:
            con.execute("INSERT INTO manifiesto_capas (dataset,entidad,grupos,url,error) VALUES (?,?,?,?,?)",
                        [fila["dataset"], fila["entidad"], fila["grupos"], fila["url"], f"servicio: {e}"[:300]])
    print(f"Capas por bajar: {len(tareas)}", flush=True)

    # 2) bajar en paralelo, escribir en serie
    ok = err = 0
    t0 = time.time()
    with ThreadPoolExecutor(args.hilos) as pool:
        futuros = {pool.submit(bajar_capa, t["capa_url"], args.max_filas): t for t in tareas}
        for i, fut in enumerate(as_completed(futuros), 1):
            t = futuros[fut]
            try:
                df, info = fut.result()
                df.columns = [re.sub(r"[^a-z0-9]+", "_", unidecode(str(c)).lower()).strip("_") for c in df.columns]
                df = df.loc[:, ~df.columns.duplicated()]
                tabla = nombre_tabla(t["dataset"], t["capa_url"])
                con.register("_df", df.astype(str) if not df.empty else pd.DataFrame({"vacio": []}))
                con.execute(f"CREATE OR REPLACE TABLE {tabla} AS SELECT * FROM _df")
                con.unregister("_df")
                con.execute("""INSERT INTO manifiesto_capas (dataset,entidad,grupos,url,capa,geometria,tabla,filas,
                    total_ids,lista_columnas,error) VALUES (?,?,?,?,?,?,?,?,?,?,'')""",
                            [t["dataset"], t["entidad"], t["grupos"], t["capa_url"], info["capa"], info["geometria"],
                             tabla, len(df), info["total_ids"], "|".join(df.columns)])
                ok += 1
            except Exception as e:
                con.execute("INSERT INTO manifiesto_capas (dataset,entidad,grupos,url,error) VALUES (?,?,?,?,?)",
                            [t["dataset"], t["entidad"], t["grupos"], t["capa_url"], f"{type(e).__name__}: {e}"[:300]])
                err += 1
            if i % 25 == 0:
                print(f"  {i}/{len(tareas)} ok={ok} err={err} {time.time() - t0:.0f}s", flush=True)
    con.execute("CHECKPOINT")
    db = STORE / args.db
    print(f"Fin: ok={ok} err={err}. Base: {db} ({db.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
