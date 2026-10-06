"""
04 - Auditoría de usabilidad: qué se puede cruzar con qué.

Recorre todas las tablas del almacén (bogota.duckdb + capas.duckdb) y detecta:
  - unidad territorial: localidad / UPZ / UPL / coordenadas / ninguna
  - cobertura de localidades (cuántas de las 20 se reconocen)
  - rango de años
  - si trae sexo/género (enfoque diferencial)
Salida: tabla `inventario` en perfil.duckdb y outputs/inventario_tablas.csv.
Es el "paso 2: auditar lo que hay" de la metodología DataJam.
"""
import re
import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from bogota import (PAT_ANIO, PAT_COORD, PAT_FECHA, PAT_LOCALIDAD, PAT_SEXO, PAT_UPL, PAT_UPZ, STORE,
                    cod_localidad)

SALIDA = Path(__file__).parents[1] / "outputs"
RE_ANIO = r"((?:19|20)\d{2})"


def anios(con, tabla, col) -> tuple[int | None, int | None]:
    q = f"""SELECT min(a), max(a) FROM (SELECT TRY_CAST(regexp_extract(CAST("{col}" AS VARCHAR), '{RE_ANIO}', 1) AS INT) a
            FROM {tabla}) WHERE a BETWEEN 1990 AND 2027"""
    return con.execute(q).fetchone()


def perfilar(con, tabla: str, columnas: list[str]) -> dict:
    p = {"tabla": tabla, "n_columnas": len(columnas)}
    p["filas"] = con.execute(f"SELECT count(*) FROM {tabla}").fetchone()[0]
    loc = [c for c in columnas if PAT_LOCALIDAD.search(c)]
    p["col_localidad"] = ""
    p["localidades"] = 0
    for c in loc:  # la columna que más localidades reconoce
        vals = con.execute(f'SELECT DISTINCT CAST("{c}" AS VARCHAR) FROM {tabla} LIMIT 3000').fetchall()
        cods = {cod_localidad(v[0]) for v in vals} - {None}
        if len(cods) > p["localidades"]:
            p["col_localidad"], p["localidades"] = c, len(cods)
    p["col_upz"] = next((c for c in columnas if PAT_UPZ.search(c)), "")
    p["col_upl"] = next((c for c in columnas if PAT_UPL.search(c)), "")
    xs = [c for c in columnas if PAT_COORD.match(c)]
    p["coordenadas"] = len(xs) >= 2
    p["col_sexo"] = next((c for c in columnas if PAT_SEXO.search(c)), "")
    p["anio_min"] = p["anio_max"] = None
    for c in [c for c in columnas if PAT_ANIO.search(c)] + [c for c in columnas if PAT_FECHA.search(c)]:
        try:
            a, b = anios(con, tabla, c)
        except Exception:
            continue
        if a:
            p["anio_min"], p["anio_max"], p["col_tiempo"] = a, b, c
            break
    if p["localidades"] >= 15:
        p["unidad"] = "localidad"
    elif p["col_upz"]:
        p["unidad"] = "upz"
    elif p["col_upl"]:
        p["unidad"] = "upl"
    elif p["coordenadas"]:
        p["unidad"] = "punto"
    elif p["localidades"] > 0:
        p["unidad"] = "localidad_parcial"
    else:
        p["unidad"] = "ninguna"
    return p


def main():
    filas = []
    bases = [(r.name, "manifiesto") for r in sorted(STORE.glob("bogota*.duckdb"))]
    bases += [(r.name, "manifiesto_capas") for r in sorted(STORE.glob("capas*.duckdb"))]
    for archivo, manifiesto in bases:
        ruta = STORE / archivo
        try:
            con = duckdb.connect(str(ruta), read_only=True)
        except duckdb.IOException:
            print(f"{archivo}: en uso por otro proceso, se omite (vuelve a correr al terminar)")
            continue
        meta = con.execute(f"SELECT * FROM {manifiesto} WHERE tabla IS NOT NULL AND error = ''").df()
        print(f"{archivo}: {len(meta)} tablas")
        for i, m in enumerate(meta.to_dict("records"), 1):
            cols = [c[0] for c in con.execute(f"DESCRIBE {m['tabla']}").fetchall()]
            try:
                p = perfilar(con, m["tabla"], cols)
            except Exception as e:
                p = {"tabla": m["tabla"], "unidad": "error", "error": str(e)[:200]}
            p.update(base=archivo, dataset=m["dataset"], entidad=m["entidad"], grupos=m["grupos"],
                     recurso=m.get("nombre") or m.get("capa"), url=m["url"])
            filas.append(p)
            if i % 500 == 0:
                print(f"  {i}/{len(meta)}", flush=True)
        con.close()

    inv = pd.DataFrame(filas)
    SALIDA.mkdir(exist_ok=True)
    inv.to_csv(SALIDA / "inventario_tablas.csv", index=False, encoding="utf-8")
    out = duckdb.connect(str(STORE / "perfil.duckdb"))
    out.register("_inv", inv)
    out.execute("CREATE OR REPLACE TABLE inventario AS SELECT * FROM _inv")
    print(inv["unidad"].value_counts().to_string())
    print(f"Inventario: {SALIDA / 'inventario_tablas.csv'}")


if __name__ == "__main__":
    main()
