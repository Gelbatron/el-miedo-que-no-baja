"""
02 - Almacén: descarga los recursos tabulares del portal y los carga a DuckDB.

Capa "bronce": cada archivo queda como una tabla de texto (VARCHAR) sin tocar,
con trazabilidad completa en la tabla `manifiesto` (url, bytes, sha1, filas,
columnas, hoja, error). El archivo crudo se borra después de cargarlo para no
llenar el disco; se puede volver a bajar con la url del manifiesto.

Uso:
  python scripts/02_almacenar.py              # todo lo tabular <= 150 MB + especiales
  python scripts/02_almacenar.py --max-mb 50  # más liviano
Es reanudable: salta los recursos que ya están en el manifiesto.
"""
import argparse
import csv
import hashlib
import io
import os
import re
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import duckdb
import pandas as pd
import requests
from unidecode import unidecode

STORE = Path(os.environ.get("DATOS_BOGOTA_STORE", "C:/Users/rafal/datos-bogota"))
CRUDO = STORE / "crudo"
DB = STORE / "bogota.duckdb"
TABULARES = {"CSV", "XLSX", "XLS", "ODS", "JSON", "TXT"}
# Microdatos que valen la pena aunque pesen más que el tope.
ESPECIALES = {"encuesta-multiproposito-2021-sdp"}
# Conjuntos con decenas de cortes del mismo archivo: solo el más reciente.
SOLO_ULTIMO = {"predios-bogota"}
DISCO_MINIMO_GB = 5
UA = {"User-Agent": "DataJam5-TheDataSquad/1.0 (investigacion academica)"}

lock_db = threading.Lock()


def libre_gb() -> float:
    return shutil.disk_usage(STORE).free / 1e9


def nombre_tabla(dataset: str, recurso_id: str, hoja: str | None = None) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", unidecode(dataset).lower()).strip("_")[:50]
    t = f"t_{base}__{recurso_id[:8]}"
    if hoja:
        t += "__" + re.sub(r"[^a-z0-9]+", "_", unidecode(str(hoja)).lower()).strip("_")[:20]
    return t


def limpiar_columnas(cols) -> list[str]:
    vistos, salida = {}, []
    for i, c in enumerate(cols):
        c = re.sub(r"[^a-z0-9]+", "_", unidecode(str(c)).lower()).strip("_") or f"col_{i}"
        if c[0].isdigit():
            c = "c_" + c
        n = vistos.get(c, 0)
        vistos[c] = n + 1
        salida.append(c if n == 0 else f"{c}_{n}")
    return salida


# ---------------------------------------------------------------- lectura
def detectar_texto(ruta: Path) -> tuple[str, str]:
    """Devuelve (encoding, separador) mirando el primer MB."""
    muestra = ruta.open("rb").read(1_000_000)
    for enc in ("utf-8-sig", "latin-1"):
        try:
            txt = muestra.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    lineas = [l for l in txt.splitlines()[:50] if l.strip()]
    try:
        sep = csv.Sniffer().sniff("\n".join(lineas[:20]), delimiters=",;|\t").delimiter
    except csv.Error:
        sep = max([",", ";", "|", "\t"], key=lambda s: sum(l.count(s) for l in lineas[:20]))
    return enc, sep


def fila_encabezado(df: pd.DataFrame) -> int:
    """Hojas de Excel con títulos arriba: el encabezado es la primera fila 'llena'."""
    ancho = df.shape[1]
    for i in range(min(25, len(df))):
        llenos = df.iloc[i].notna().sum()
        if ancho and llenos / ancho >= 0.6:
            return i
    return 0


def leer_excel(ruta: Path) -> list[tuple[str, pd.DataFrame]]:
    # La extensión del portal no siempre dice la verdad (xlsx publicados como XLS y al revés)
    preferido = {".xls": "xlrd", ".ods": "odf"}.get(ruta.suffix.lower(), "openpyxl")
    ultimo_error = None
    for motor in dict.fromkeys([preferido, "openpyxl", "xlrd", "odf"]):
        try:
            hojas = pd.read_excel(ruta, sheet_name=None, header=None, dtype=str, engine=motor)
            break
        except Exception as e:
            ultimo_error = e
    else:
        raise ultimo_error
    salida = []
    for nombre, crudo in hojas.items():
        crudo = crudo.dropna(how="all").dropna(axis=1, how="all")
        if crudo.empty or crudo.shape[0] < 2:
            continue
        h = fila_encabezado(crudo)
        df = crudo.iloc[h + 1:].copy()
        df.columns = limpiar_columnas(crudo.iloc[h].fillna("").tolist())
        salida.append((nombre, df.reset_index(drop=True)))
    return salida


def cargar(con, ruta: Path, fila: dict) -> list[dict]:
    """Carga un archivo a una o varias tablas. Devuelve filas para el manifiesto."""
    fmt = fila["formato"]
    regs = []
    if fmt in ("CSV", "TXT"):
        enc, sep = detectar_texto(ruta)
        tabla = nombre_tabla(fila["dataset"], fila["recurso_id"])
        try:
            # Camino rápido: DuckDB lee directo (todo como texto)
            enc_duck = "utf-8" if enc.startswith("utf") else "latin-1"
            con.execute(
                f"""CREATE OR REPLACE TABLE {tabla} AS SELECT * FROM read_csv(?, delim=?, header=true,
                all_varchar=true, ignore_errors=true, null_padding=true, encoding=?, sample_size=-1)""",
                [str(ruta), sep, enc_duck],
            )
        except Exception:
            df = pd.read_csv(ruta, sep=sep, encoding=enc, dtype=str, on_bad_lines="skip", engine="python")
            df.columns = limpiar_columnas(df.columns)
            con.register("_df", df)
            con.execute(f"CREATE OR REPLACE TABLE {tabla} AS SELECT * FROM _df")
            con.unregister("_df")
        cols = [c[0] for c in con.execute(f"DESCRIBE {tabla}").fetchall()]
        limpias = limpiar_columnas(cols)
        for a, b in zip(cols, limpias):
            if a != b:
                con.execute(f'ALTER TABLE {tabla} RENAME COLUMN "{a}" TO "{b}"')
        n = con.execute(f"SELECT count(*) FROM {tabla}").fetchone()[0]
        regs.append({"tabla": tabla, "hoja": None, "filas": n, "columnas": len(cols), "lista_columnas": "|".join(limpias)})
    elif fmt in ("XLSX", "XLS", "ODS"):
        for hoja, df in leer_excel(ruta):
            tabla = nombre_tabla(fila["dataset"], fila["recurso_id"], hoja)
            con.register("_df", df)
            con.execute(f"CREATE OR REPLACE TABLE {tabla} AS SELECT * FROM _df")
            con.unregister("_df")
            regs.append({"tabla": tabla, "hoja": str(hoja), "filas": len(df), "columnas": df.shape[1],
                         "lista_columnas": "|".join(df.columns)})
    elif fmt == "JSON":
        import json
        obj = json.loads(ruta.read_text(encoding="utf-8", errors="replace"))
        if isinstance(obj, dict):
            obj = next((v for v in obj.values() if isinstance(v, list)), [obj])
        df = pd.json_normalize(obj).astype(str)
        df.columns = limpiar_columnas(df.columns)
        tabla = nombre_tabla(fila["dataset"], fila["recurso_id"])
        con.register("_df", df)
        con.execute(f"CREATE OR REPLACE TABLE {tabla} AS SELECT * FROM _df")
        con.unregister("_df")
        regs.append({"tabla": tabla, "hoja": None, "filas": len(df), "columnas": df.shape[1],
                     "lista_columnas": "|".join(df.columns)})
    return regs


# ---------------------------------------------------------------- descarga
def descargar(fila: dict, tope_bytes: int) -> tuple[dict, Path | None, str]:
    ext = {"XLSX": ".xlsx", "XLS": ".xls", "ODS": ".ods", "JSON": ".json"}.get(fila["formato"], ".csv")
    destino = CRUDO / f"{fila['recurso_id']}{ext}"
    ultimo = ""
    for intento in range(3):
        sha = hashlib.sha1()
        try:
            with requests.get(fila["url"], stream=True, timeout=(20, 180), headers=UA) as r:
                r.raise_for_status()
                total = 0
                with destino.open("wb") as f:
                    for trozo in r.iter_content(1 << 20):
                        total += len(trozo)
                        if total > tope_bytes:
                            raise ValueError(f"supera el tope ({total / 1e6:.0f} MB)")
                        sha.update(trozo)
                        f.write(trozo)
            fila["bytes"], fila["sha1"] = total, sha.hexdigest()
            return fila, destino, ""
        except (requests.ConnectionError, requests.Timeout) as e:  # red: se reintenta
            destino.unlink(missing_ok=True)
            ultimo = f"{type(e).__name__}: {e}"[:300]
            time.sleep(3 * (intento + 1))
        except Exception as e:  # 404, tope, etc.: no se reintenta
            destino.unlink(missing_ok=True)
            return fila, None, f"{type(e).__name__}: {e}"[:300]
    return fila, None, ultimo


def seleccionar(max_mb: float) -> pd.DataFrame:
    r = pd.read_csv(STORE / "catalogo" / "recursos.csv", dtype=str).fillna("")
    r["formato"] = r["formato"].str.replace(".", "", regex=False).str.upper()
    r["tam"] = pd.to_numeric(r["tamano"], errors="coerce")
    r = r[r["formato"].isin(TABULARES) & r["url"].str.startswith("http")]
    # Un solo corte para conjuntos con muchos cortes iguales
    ult = r[r["dataset"].isin(SOLO_ULTIMO)].sort_values("modificado").groupby("dataset").tail(1)
    r = pd.concat([r[~r["dataset"].isin(SOLO_ULTIMO)], ult])
    # Si un conjunto trae el mismo recurso en CSV y en Excel, basta el CSV
    r["clave"] = r["dataset_id"] + "|" + r["nombre"].str.lower().str.strip()
    r["pref"] = r["formato"].map({"CSV": 0, "JSON": 1, "XLSX": 2, "XLS": 3, "ODS": 4, "TXT": 5})
    r = r.sort_values("pref").drop_duplicates("clave")
    dentro = (r["tam"] <= max_mb * 1e6) | r["tam"].isna() | r["dataset"].isin(ESPECIALES | SOLO_ULTIMO)
    return r[dentro].sort_values("tam", na_position="last")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-mb", type=float, default=150)
    ap.add_argument("--hilos", type=int, default=6)
    ap.add_argument("--limite", type=int, default=0, help="solo los N primeros pendientes (prueba)")
    ap.add_argument("--db", default="bogota.duckdb", help="archivo de salida (otro archivo = no bloquea el principal)")
    ap.add_argument("--reintentar-de", default="", help="base cuyos fallos de red/lectura se reintentan")
    ap.add_argument("--patron", default="", help="regex sobre el nombre del conjunto (prioridades)")
    ap.add_argument("--excluir", default="", help="regex de conjuntos a dejar para después")
    args = ap.parse_args()

    CRUDO.mkdir(parents=True, exist_ok=True)
    solo = None
    if args.reintentar_de:
        previa = duckdb.connect(str(STORE / args.reintentar_de), read_only=True)
        solo = {x[0] for x in previa.execute("""SELECT DISTINCT recurso_id FROM manifiesto WHERE error LIKE 'ConnectionError%'
            OR error LIKE '%Timeout%' OR error LIKE 'ChunkedEncodingError%' OR error LIKE 'carga: XLRDError%'
            OR error LIKE 'carga: ValueError: Excel file format%' OR error LIKE 'carga: ValueError: Unable to read%'""").fetchall()}
        previa.close()
        print(f"Reintentos tomados de {args.reintentar_de}: {len(solo)}")
    con = duckdb.connect(str(STORE / args.db))
    con.execute("""CREATE TABLE IF NOT EXISTS manifiesto (
        recurso_id VARCHAR, dataset VARCHAR, entidad VARCHAR, grupos VARCHAR, nombre VARCHAR,
        formato VARCHAR, url VARCHAR, modificado VARCHAR, bytes BIGINT, sha1 VARCHAR,
        tabla VARCHAR, hoja VARCHAR, filas BIGINT, columnas INTEGER, lista_columnas VARCHAR,
        error VARCHAR, cargado_en TIMESTAMP DEFAULT now())""")
    # Las fallas de red se vuelven a intentar; las definitivas (404, tope) no.
    con.execute("""DELETE FROM manifiesto WHERE error LIKE 'ConnectionError%' OR error LIKE '%Timeout%'
                   OR error LIKE 'ChunkedEncodingError%' OR error LIKE 'carga: XLRDError%'
                   OR error LIKE 'carga: ValueError: Excel file format%'""")
    hechos = {x[0] for x in con.execute("SELECT DISTINCT recurso_id FROM manifiesto").fetchall()}
    sel = seleccionar(args.max_mb)
    pendientes = sel[~sel["recurso_id"].isin(hechos)]
    if solo is not None:
        pendientes = pendientes[pendientes["recurso_id"].isin(solo)]
    if args.patron:
        pendientes = pendientes[pendientes["dataset"].str.contains(args.patron, regex=True)]
    if args.excluir:
        pendientes = pendientes[~pendientes["dataset"].str.contains(args.excluir, regex=True)]
    print(f"Seleccionados {len(sel)} | ya procesados {len(sel) - len(pendientes)} | pendientes {len(pendientes)}")
    if args.limite:
        pendientes = pendientes.head(args.limite)

    def anotar(fila, regs, error=""):
        base = {k: fila.get(k, "") for k in ("recurso_id", "dataset", "entidad", "grupos", "nombre", "formato", "url", "modificado")}
        base.update(bytes=fila.get("bytes"), sha1=fila.get("sha1"))
        for reg in regs or [{"tabla": None, "hoja": None, "filas": None, "columnas": None, "lista_columnas": None}]:
            row = {**base, **reg, "error": error}
            con.execute("""INSERT INTO manifiesto (recurso_id,dataset,entidad,grupos,nombre,formato,url,modificado,
                bytes,sha1,tabla,hoja,filas,columnas,lista_columnas,error) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        [row[k] for k in ("recurso_id", "dataset", "entidad", "grupos", "nombre", "formato", "url",
                                          "modificado", "bytes", "sha1", "tabla", "hoja", "filas", "columnas",
                                          "lista_columnas", "error")])

    ok = err = 0
    t0 = time.time()
    with ThreadPoolExecutor(args.hilos) as pool:
        futuros = []
        for fila in pendientes.to_dict("records"):
            tope = 2_500e6 if fila["dataset"] in ESPECIALES else max(args.max_mb * 1.1e6, 200e6)
            futuros.append(pool.submit(descargar, fila, int(tope)))
        for i, fut in enumerate(as_completed(futuros), 1):
            fila, ruta, error = fut.result()
            if ruta is None:
                anotar(fila, None, error)
                err += 1
            else:
                try:
                    regs = cargar(con, ruta, fila)
                    anotar(fila, regs, "" if regs else "sin tablas legibles")
                    ok += 1
                except Exception as e:
                    anotar(fila, None, f"carga: {type(e).__name__}: {e}"[:300])
                    err += 1
                finally:
                    ruta.unlink(missing_ok=True)
            if i % 50 == 0:
                print(f"  {i}/{len(futuros)}  ok={ok} err={err}  {time.time() - t0:.0f}s  libre={libre_gb():.1f}GB", flush=True)
            if libre_gb() < DISCO_MINIMO_GB:
                print("Disco casi lleno: me detengo (vuelve a correr para reanudar).")
                pool.shutdown(cancel_futures=True)
                break
    con.execute("CHECKPOINT")
    db = STORE / args.db
    print(f"Fin: ok={ok} err={err} en {time.time() - t0:.0f}s. Base: {db} ({db.stat().st_size / 1e9:.2f} GB)")


if __name__ == "__main__":
    main()
