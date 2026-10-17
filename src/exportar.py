"""
Exportes interoperables: JSON del visor web, CSV y GeoJSON descargables,
tablas para Power BI. Todo sale del mismo resultado del pipeline.
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from fuentes import FUENTES
from indicadores import ANIO
from territorio import LOCALIDADES

RAIZ = Path(__file__).resolve().parents[1]
VISOR = RAIZ / "visor"
DESC = VISOR / "public" / "descargas"
PBI = RAIZ / "powerbi" / "datos"
GEO_OUT = RAIZ / "outputs" / "geo"

INDICADORES = [
    # clave, nombre, grupo, unidad, color, fuente, sexo
    ("zona_insegura", "Califica mala la seguridad de su zona", "Percepción", "%", "percepcion", "Bienal 2025", True),
    ("ciudad_insegura", "Califica a Bogotá como insegura", "Percepción", "%", "percepcion", "Bienal 2025", True),
    ("miedo_espacio_publico", "Siente miedo en el espacio público", "Percepción", "%", "percepcion", "Bienal 2025", True),
    ("ciudad_peor_que_antes", "Cree que la ciudad está menos segura que el año pasado", "Percepción", "%", "percepcion", "Bienal 2025", True),
    ("alumbrado_malo", "Califica malo el alumbrado de su zona", "Entorno", "%", "percepcion", "Bienal 2025", True),
    ("parque_spa", "Reporta venta o consumo de drogas en su parque", "Entorno", "%", "percepcion", "Bienal 2025", True),
    ("parque_acoso", "Reporta acoso o abuso sexual en su parque", "Entorno", "%", "percepcion", "Bienal 2025", True),
    ("emv_victima", "Fue víctima de un delito en el último año", "Victimización", "%", "percepcion", "EMV 2024", False),
    ("emv_no_sale_noche", "Evita salir de noche por inseguridad", "Victimización", "%", "percepcion", "EMV 2024", False),
    ("emv_teme_acoso_sexual", "Teme mucho o bastante el acoso sexual", "Victimización", "%", "percepcion", "EMV 2024", False),
    ("delitos_alto_impacto_100k", "Delitos de alto impacto por 100.000 hab.", "Registro", "por 100.000", "registro", "SCJ ene-ago 2025", False),
    ("hurtos_100k", "Hurtos por 100.000 hab.", "Registro", "por 100.000", "registro", "SCJ ene-ago 2025", False),
    ("homicidios_100k", "Homicidios por 100.000 hab.", "Registro", "por 100.000", "registro", "SCJ ene-ago 2025", False),
    ("vif_ds_100k_mujeres", "Violencia intrafamiliar y delitos sexuales por 100.000 mujeres", "Registro", "por 100.000", "registro", "SCJ ene-ago 2025", False),
    ("incidentes_narcoticos_100k", "Llamadas 123 por narcóticos por 100.000 hab.", "Registro", "por 100.000", "registro", "SCJ Línea 123 ene-ago 2025", False),
    ("incidentes_rinas_100k", "Llamadas 123 por riñas por 100.000 hab.", "Registro", "por 100.000", "registro", "SCJ Línea 123 ene-ago 2025", False),
    ("incidentes_maltrato_mujer_100k", "Llamadas 123 por maltrato a mujer por 100.000 hab.", "Registro", "por 100.000", "registro", "SCJ Línea 123 ene-ago 2025", False),
    ("ibs", "Índice de Brecha de Seguridad", "Índices", "z", "div", "Cálculo propio", False),
    ("cifra_oculta", "Víctimas estimadas por cada delito registrado", "Índices", "veces", "percepcion", "EMV 2024 y SCJ 2024", False),
    ("ep_efectivo_m2_hab", "Espacio público efectivo por habitante", "Contexto", "m²", "registro", "DADEP", False),
]


def _proyeccion(gdf: gpd.GeoDataFrame, ancho: float = 600.0):
    """Proyección simple (equirectangular) de las geometrías al ancho del mapa del visor."""
    minx, miny, maxx, maxy = gdf.total_bounds
    lat0 = np.radians((miny + maxy) / 2)
    k = ancho / ((maxx - minx) * np.cos(lat0))
    alto = (maxy - miny) * k
    f = lambda x, y: ((x - minx) * np.cos(lat0) * k, (maxy - y) * k)
    return f, ancho, alto


def _path(geom, f) -> str:
    """Convierte un polígono en el atributo d de un path SVG."""
    partes = []
    polis = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    for p in polis:
        if p.area < 1e-7:
            continue
        for anillo in [p.exterior, *p.interiors]:
            pts = [f(x, y) for x, y in anillo.coords]
            partes.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(partes)


def geometrias(geo_loc: gpd.GeoDataFrame, geo_upz: gpd.GeoDataFrame, pob_upz: pd.DataFrame | None = None):
    """Localidades recortadas a su huella urbana (unión de UPZ urbanas) y UPZ, con la misma proyección."""
    upz = geo_upz.to_crs(4326).copy()
    if pob_upz is not None:  # UPZ urbanas: con población SDP de al menos 1.000 personas en 2025
        urbanas = set(pob_upz[(pob_upz["anio"] == ANIO) & (pob_upz["personas"] >= 1000)]["upz"])
        upz = upz[upz["upz"].isin(urbanas)].copy()
    upz["geometry"] = upz.geometry.buffer(0)
    urbano = upz.union_all()
    loc = geo_loc[geo_loc["localidad"] != 20].to_crs(4326).copy()
    loc["geometry"] = loc.geometry.buffer(0).intersection(urbano).simplify(0.00025, preserve_topology=True)
    upz["geometry"] = upz.geometry.simplify(0.00025, preserve_topology=True)
    cent = upz.copy()
    cent["geometry"] = upz.geometry.representative_point()
    upz["localidad"] = gpd.sjoin(cent, loc[["localidad", "geometry"]], how="left", predicate="within")["localidad"].values
    f, w, h = _proyeccion(loc)
    L = [{"id": int(r.localidad), "nombre": LOCALIDADES[int(r.localidad)], "d": _path(r.geometry, f),
          "cx": round(f(*r.geometry.representative_point().coords[0])[0], 1),
          "cy": round(f(*r.geometry.representative_point().coords[0])[1], 1)} for r in loc.itertuples()]
    U = [{"id": int(r.upz), "nombre": str(r.nombre_upz).title(), "localidad": None if pd.isna(r.localidad) else int(r.localidad),
          "d": _path(r.geometry, f)} for r in upz.itertuples()]
    return {"ancho": round(w, 1), "alto": round(h, 1), "localidades": L, "upz": U}, loc, upz


def _registros(df: pd.DataFrame) -> list[dict]:
    """Convierte una tabla en registros JSON válidos (sin infinitos)."""
    return json.loads(df.replace([np.inf, -np.inf], np.nan).to_json(orient="records", force_ascii=False))


def visor(res: dict, etiquetas: dict) -> Path:
    """Arma el JSON del visor web con indicadores, geometrías, modelos y textos."""
    t, P, R, T, S, iu = res["t"], res["P"], res["R"], res["T"], res["S"], res["iu"]
    geo, loc_urb, upz = geometrias(t["geo"], t["geo_upz"], t["poblacion_upz"])

    panel = P.copy()
    panel = panel.merge(T["ibs"][["localidad", "ibs", "ibs_p05", "ibs_p95", "puesto", "prob_top5"]], on="localidad", how="left")
    co = T["cifra_oculta"].set_index("localidad")
    panel["cifra_oculta"] = panel["localidad"].map(co["razon"])

    valores = {}
    for clave, *_ in INDICADORES:
        v = {"total": {str(int(r.localidad)): (None if pd.isna(getattr(r, clave)) else round(float(getattr(r, clave)), 3))
                       for r in panel.itertuples()}}
        for s in ("mujeres", "hombres"):
            col = f"{clave}_{s}"
            if col in panel:
                v[s] = {str(int(l)): (None if pd.isna(x) else round(float(x), 3)) for l, x in zip(panel["localidad"], panel[col])}
        valores[clave] = v

    upz_val = {}
    for cod, nom in (("N", "Narcóticos"), ("R", "Riñas"), ("MM", "Maltrato a mujer"), ("H", "Hurto")):
        sub = iu[iu["codigo"] == cod]
        upz_val[cod] = {"nombre": f"Llamadas 123 por {nom.lower()} por 100.000 hab. (ene-ago {ANIO})",
                        "valores": {str(int(u)): round(float(x), 1) for u, x in zip(sub["upz"], sub["tasa"])},
                        "casos": {str(int(u)): int(c) for u, c in zip(sub["upz"], sub["casos"])}}

    import validacion_registro as VR  # serie validada: SIEDCO donde la capa SCJ tiene quiebre
    serie_del = VR.serie_bogota_validada(t["delitos"])[["codigo", "tipo", "anio", "casos", "fuente", "estado", "casos_capa_scj"]]
    serie_inc = t["incidentes"].groupby(["codigo", "tipo", "anio"], as_index=False)["casos"].sum()

    def ame(df):
        d = df.copy()
        d["etiqueta"] = d["variable"].map(lambda v: etiquetas.get(v, v))
        return _registros(d)

    datos = {
        "generado": datetime.now().isoformat(timespec="minutes"),
        "resumen": S,
        "geo": geo,
        "indicadores": [{"clave": c, "nombre": n, "grupo": g, "unidad": u, "color": col, "fuente": fu, "sexo": sx}
                        for c, n, g, u, col, fu, sx in INDICADORES],
        "valores": valores,
        "upz": upz_val,
        "panel": _registros(panel),
        "serie_delitos": _registros(serie_del),
        "serie_incidentes": _registros(serie_inc),
        "ame": {k: ame(R[k]) for k in ("m_hechos", "m_calif", "m_ciudad", "m_miedo")},
        "ame_efectos_fijos": ame(R["m_efectos_fijos"][~R["m_efectos_fijos"]["variable"].str.startswith("loc_")]),
        "lpm_wild": ame(R["lpm_wild"]),
        "auc": _registros(R["auc"]),
        "emv_genero": {y: ame(R[f"emv_{y}"]) for y in ("no_sale_noche", "teme_acoso_sexual", "barrio_inseguro")},
        "ibs": _registros(T["ibs"].assign(nombre=T["ibs"]["localidad"].map(LOCALIDADES))),
        "cifra_oculta": _registros(T["cifra_oculta"]),
        "validaciones": _registros(T["validaciones"]),
        "escenarios": _registros(R["escenarios"]),
        "medias": {k: R[k].attrs.get("media") for k in ("m_hechos", "m_ciudad", "m_miedo")},
        "n": {k: R[k].attrs.get("n") for k in ("m_hechos", "m_ciudad", "m_miedo")},
        "fuentes": [{"clave": k, **{c: v for c, v in f.items() if c in ("entidad", "conjunto", "portal", "url")}}
                    for k, f in FUENTES.items()],
    }
    (VISOR / "data").mkdir(parents=True, exist_ok=True)
    (VISOR / "data" / "visor.json").write_text(json.dumps(datos, ensure_ascii=False, allow_nan=False, default=str), encoding="utf-8")

    # descargas interoperables (CSV + GeoJSON)
    DESC.mkdir(parents=True, exist_ok=True)
    GEO_OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(DESC / "panel_localidad_2025.csv", index=False, encoding="utf-8-sig")
    T["ibs"].assign(nombre=T["ibs"]["localidad"].map(LOCALIDADES)).to_csv(DESC / "indice_brecha_seguridad.csv", index=False, encoding="utf-8-sig")
    T["cifra_oculta"].to_csv(DESC / "cifra_oculta_localidad.csv", index=False, encoding="utf-8-sig")
    R["m_hechos"].assign(etiqueta=R["m_hechos"]["variable"].map(etiquetas)).to_csv(DESC / "efectos_marginales_modelo_principal.csv", index=False, encoding="utf-8-sig")
    serie_del.to_csv(DESC / "serie_delitos_bogota_ene_ago.csv", index=False, encoding="utf-8-sig")
    iu.to_csv(DESC / "incidentes_123_upz_2025.csv", index=False, encoding="utf-8-sig")
    gl = loc_urb.merge(panel, on="localidad")
    gl.to_file(GEO_OUT / "localidades_brecha_seguridad.geojson", driver="GeoJSON")
    gu = upz.merge(iu.pivot_table(index="upz", columns="codigo", values="tasa").add_prefix("tasa_123_").reset_index(), on="upz", how="left")
    gu.to_file(GEO_OUT / "upz_incidentes_123.geojson", driver="GeoJSON")
    for g in GEO_OUT.glob("*.geojson"):
        shutil.copy(g, DESC / g.name)

    # tablas para Power BI (modelo estrella simple)
    PBI.mkdir(parents=True, exist_ok=True)
    panel.to_csv(PBI / "dim_localidad_indicadores.csv", index=False, encoding="utf-8-sig")
    serie_del[["codigo", "tipo", "anio", "casos"]].to_csv(PBI / "fact_delitos_serie.csv", index=False, encoding="utf-8-sig")
    R["m_hechos"].assign(etiqueta=R["m_hechos"]["variable"].map(etiquetas), modelo="Hechos del entorno").pipe(
        lambda a: pd.concat([a, R["m_calif"].assign(etiqueta=R["m_calif"]["variable"].map(etiquetas), modelo="Con calificaciones")])
    ).to_csv(PBI / "fact_efectos_marginales.csv", index=False, encoding="utf-8-sig")
    R["auc"].to_csv(PBI / "fact_auc_bloques.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"indicador": k, "mujeres": v["mujeres"], "hombres": v["hombres"]} for k, v in S["emv_por_sexo"].items()]
                 ).to_csv(PBI / "fact_genero_emv.csv", index=False, encoding="utf-8-sig")
    return VISOR / "data" / "visor.json"
