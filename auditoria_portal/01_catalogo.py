"""
01 - Catálogo completo del Portal de Datos Abiertos de Bogotá (CKAN).

Baja los metadatos de TODOS los conjuntos (no solo los de un grupo) por la API
oficial y los deja planos en dos tablas:
  - datasets.csv : un conjunto por fila (entidad, grupos, fechas, etiquetas)
  - recursos.csv : un archivo/servicio por fila (formato, url, tamaño, fecha)

Uso:  python scripts/01_catalogo.py
Salida: $DATOS_BOGOTA_STORE/catalogo/  (por defecto C:/Users/rafal/datos-bogota)
"""
import json
import os
import time
from pathlib import Path

import requests

API = "https://datosabiertos.bogota.gov.co/api/3/action"
STORE = Path(os.environ.get("DATOS_BOGOTA_STORE", "C:/Users/rafal/datos-bogota"))
SALIDA = STORE / "catalogo"
LOTE = 500


def pedir(accion: str, **params) -> dict:
    """GET a la API de CKAN con reintentos simples."""
    for intento in range(4):
        try:
            r = requests.get(f"{API}/{accion}", params=params, timeout=90)
            r.raise_for_status()
            return r.json()["result"]
        except Exception as e:  # red inestable del portal
            espera = 2 ** intento
            print(f"  reintento {intento + 1} ({e}); espero {espera}s")
            time.sleep(espera)
    raise RuntimeError(f"La API no respondió: {accion} {params}")


def bajar_paquetes() -> list[dict]:
    total = pedir("package_search", rows=0)["count"]
    print(f"Conjuntos en el portal: {total}")
    paquetes = []
    for inicio in range(0, total, LOTE):
        res = pedir("package_search", rows=LOTE, start=inicio)
        paquetes.extend(res["results"])
        print(f"  {len(paquetes)}/{total}")
    return paquetes


def aplanar(paquetes: list[dict]):
    import csv

    filas_d, filas_r = [], []
    for p in paquetes:
        org = (p.get("organization") or {}).get("title", "")
        grupos = "|".join(g["name"] for g in p.get("groups", []))
        filas_d.append({
            "dataset_id": p["id"],
            "nombre": p["name"],
            "titulo": p.get("title", ""),
            "entidad": org,
            "grupos": grupos,
            "etiquetas": "|".join(t["name"] for t in p.get("tags", [])),
            "creado": p.get("metadata_created", ""),
            "modificado": p.get("metadata_modified", ""),
            "frecuencia": next((e["value"] for e in p.get("extras", []) if "frecuencia" in e["key"].lower()), ""),
            "n_recursos": p.get("num_resources", 0),
            "licencia": p.get("license_title", ""),
            "descripcion": (p.get("notes") or "").replace("\n", " ")[:1000],
            "url": f"https://datosabiertos.bogota.gov.co/dataset/{p['name']}",
        })
        for r in p.get("resources", []):
            filas_r.append({
                "recurso_id": r["id"],
                "dataset_id": p["id"],
                "dataset": p["name"],
                "entidad": org,
                "grupos": grupos,
                "nombre": (r.get("name") or "").replace("\n", " "),
                "formato": (r.get("format") or "").upper().strip(),
                "url": r.get("url", ""),
                "tamano": r.get("size") or "",
                "modificado": r.get("last_modified") or r.get("created") or "",
                "datastore": r.get("datastore_active", False),
            })

    for nombre, filas in (("datasets.csv", filas_d), ("recursos.csv", filas_r)):
        with open(SALIDA / nombre, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
            w.writeheader()
            w.writerows(filas)
    return filas_d, filas_r


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    paquetes = bajar_paquetes()
    (SALIDA / "paquetes_raw.json").write_text(json.dumps(paquetes, ensure_ascii=False), encoding="utf-8")
    d, r = aplanar(paquetes)
    print(f"Listo: {len(d)} conjuntos, {len(r)} recursos -> {SALIDA}")


if __name__ == "__main__":
    main()
