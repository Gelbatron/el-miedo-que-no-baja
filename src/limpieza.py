"""
Limpieza y estandarización de cada fuente a una forma ordenada (tidy).

Cada función devuelve un DataFrame listo para integrar y anota en BITACORA lo
que hizo: filas leídas, descartadas, llaves que no cruzaron, recodificaciones.
El notebook imprime la bitácora como evidencia del proceso de limpieza.
"""
import json
import re

import numpy as np
import pandas as pd

from fuentes import CRUDOS
from territorio import URBANAS, cod_localidad

BITACORA: list[dict] = []


def anotar(fuente: str, paso: str, detalle: str):
    """Registra un paso de limpieza en la bitácora (fuente, paso y detalle) como evidencia del proceso."""
    BITACORA.append({"fuente": fuente, "paso": paso, "detalle": detalle})


def bitacora() -> pd.DataFrame:
    """Devuelve la bitácora de limpieza como tabla."""
    return pd.DataFrame(BITACORA)


def _num(s: pd.Series) -> pd.Series:
    """Números con coma decimal o separador de miles ('1.234,5', '74,49')."""
    t = s.astype(str).str.strip()
    t = t.where(~t.str.contains(r"\d\.\d{3},"), t.str.replace(".", "", regex=False))
    return pd.to_numeric(t.str.replace(",", ".", regex=False), errors="coerce")


# ------------------------------------------------------------------ SCJ: formato ancho cm{código}{aa}cont
def _ancho_a_largo(df: pd.DataFrame, col_loc: str, nombres: dict, fuente: str) -> pd.DataFrame:
    """Pasa las columnas anchas de la SCJ (una por delito y año) a formato largo: localidad, delito, año y casos."""
    cols = [c for c in df.columns if re.match(r"CM([A-Z]+?)(\d\d)CONT$", c)]
    largo = df.melt(id_vars=[col_loc], value_vars=cols, var_name="col", value_name="casos")
    largo["codigo"] = largo["col"].str.extract(r"CM([A-Z]+?)\d\dCONT")[0]
    largo["anio"] = 2000 + largo["col"].str.extract(r"(\d\d)CONT$")[0].astype(int)
    largo["casos"] = pd.to_numeric(largo["casos"], errors="coerce")
    nulos = int(largo["casos"].isna().sum())
    largo = largo.dropna(subset=["casos"])
    largo["tipo"] = largo["codigo"].map(nombres)
    anotar(fuente, "formato", f"{len(cols)} columnas año×tipo pasadas a formato largo; {nulos} celdas vacías descartadas")
    return largo.drop(columns="col")


DELITOS = {"H": "Homicidios", "LP": "Lesiones personales", "HP": "Hurto a personas", "HR": "Hurto a residencias",
           "HA": "Hurto de automotores", "HB": "Hurto de bicicletas", "HC": "Hurto a comercio",
           "HCE": "Hurto de celulares", "HM": "Hurto de motocicletas", "DS": "Delitos sexuales",
           "VI": "Violencia intrafamiliar"}
INCIDENTES = {"R": "Riñas", "N": "Narcóticos", "AOP": "Alteración del orden público", "MM": "Maltrato a mujer",
              "M": "Maltrato", "D": "Disparos", "PIA": "Porte ilegal de armas", "H": "Hurto",
              "HC": "Habitantes de calle"}
HURTOS = ["HP", "HR", "HA", "HB", "HC", "HCE", "HM"]


def delitos() -> pd.DataFrame:
    """Lee y limpia los delitos de alto impacto de la SCJ por localidad, año y tipo."""
    df = pd.read_csv(CRUDOS / "scj_delitos_alto_impacto_localidad.csv")
    corte = df["CMMES"].iloc[0]
    anotar("SCJ delitos", "lectura", f"{len(df)} filas (localidades + totales); corte '{corte}' para todos los años")
    d = _ancho_a_largo(df, "CMIULOCAL", DELITOS, "SCJ delitos")
    d["localidad"] = pd.to_numeric(d["CMIULOCAL"], errors="coerce")
    fuera = d[~d["localidad"].isin(range(1, 21))]["CMIULOCAL"].unique().tolist()
    d = d[d["localidad"].isin(range(1, 21))]
    d["localidad"] = d["localidad"].astype(int)
    anotar("SCJ delitos", "llave", f"códigos de localidad 01-20 normalizados a entero; descartados no territoriales: {fuera}")
    sin_2026 = d.groupby("codigo")["anio"].max()
    if (sin_2026 < 2026).any():
        anotar("SCJ delitos", "cobertura", f"tipos sin dato 2026: {sin_2026[sin_2026 < 2026].index.tolist()}")
    d["corte"] = "ene-ago"
    return d[["localidad", "anio", "codigo", "tipo", "casos", "corte"]]


def incidentes() -> pd.DataFrame:
    """Lee y limpia los incidentes de la Línea 123 por localidad, año y tipo."""
    df = pd.read_csv(CRUDOS / "scj_incidentes_123_localidad.csv")
    anotar("SCJ incidentes 123", "lectura", f"{len(df)} filas; corte '{df['CMMES'].iloc[0]}'")
    d = _ancho_a_largo(df, "CMIULOCAL", INCIDENTES, "SCJ incidentes 123")
    d["localidad"] = pd.to_numeric(d["CMIULOCAL"], errors="coerce")
    d = d[d["localidad"].isin(range(1, 21))].copy()
    d["localidad"] = d["localidad"].astype(int)
    return d[["localidad", "anio", "codigo", "tipo", "casos"]]


def incidentes_upz():
    """Lee los incidentes de la Línea 123 por UPZ con su geometría."""
    import geopandas as gpd

    g = gpd.read_file(CRUDOS / "scj_incidentes_123_upz.geojson")
    g["upz"] = g["CMIUUPLA"].astype(str).str.extract(r"(\d+)")[0].astype(int)
    largo = _ancho_a_largo(pd.DataFrame(g.drop(columns="geometry")), "CMIUUPLA", INCIDENTES, "SCJ incidentes UPZ")
    largo["upz"] = largo["CMIUUPLA"].astype(str).str.extract(r"(\d+)")[0].astype(int)
    geo = g[["upz", "CMNOMUPLA", "geometry"]].rename(columns={"CMNOMUPLA": "nombre_upz"})
    anotar("SCJ incidentes UPZ", "geometría", f"{len(geo)} UPZ con polígono simplificado (~20 m) en WGS84")
    return largo[["upz", "anio", "codigo", "tipo", "casos"]], geo


# ------------------------------------------------------------------ SDP población
def _poblacion(archivo: str, llaves: list[str], fuente: str) -> pd.DataFrame:
    """Lee una hoja de proyecciones de población de la SDP (formato .ods) y la deja en formato largo."""
    x = pd.read_excel(CRUDOS / archivo, header=None, engine="odf")
    fila = x.index[x.iloc[:, 0].astype(str).str.strip() == "Departamento"][0]
    x.columns = x.iloc[fila].astype(str).str.strip()
    x = x.iloc[fila + 1:].dropna(subset=[llaves[0]])
    edades = [c for c in x.columns if c.startswith(("Hombres_", "Mujeres_"))]
    largo = x.melt(id_vars=llaves + ["AÑO", "Área"], value_vars=edades, var_name="se", value_name="personas")
    largo["sexo"] = largo["se"].str.split("_").str[0]
    largo["edad"] = largo["se"].str.extract(r"_(\d+)")[0].astype(int)
    largo["personas"] = pd.to_numeric(largo["personas"], errors="coerce").fillna(0)
    largo["anio"] = pd.to_numeric(largo["AÑO"]).astype(int)
    anotar(fuente, "lectura", f"{len(x)} filas (unidad × año × área); {len(edades)} columnas sexo×edad simple")
    return largo


def poblacion_localidad() -> pd.DataFrame:
    """Proyecciones de población por localidad, año y grupo (total, mujeres, hombres, adultos)."""
    largo = _poblacion("sdp_poblacion_localidad_2005_2035.ods", ["Código Localidad"], "SDP población")
    largo["localidad"] = pd.to_numeric(largo["Código Localidad"]).astype(int)
    grupos = {"total": (None, 0, 200), "mujeres": ("Mujeres", 0, 200), "hombres": ("Hombres", 0, 200),
              "adultos": (None, 18, 200), "mujeres_adultas": ("Mujeres", 18, 200), "hombres_adultos": ("Hombres", 18, 200)}
    partes = []
    for g, (sexo, a, b) in grupos.items():
        sub = largo[largo["edad"].between(a, b)]
        if sexo:
            sub = sub[sub["sexo"] == sexo]
        t = sub.groupby(["localidad", "anio"], as_index=False)["personas"].sum()
        t["grupo"] = g
        partes.append(t)
    pob = pd.concat(partes, ignore_index=True)
    tot = pob[(pob["grupo"] == "total") & (pob["anio"] == 2025)]["personas"].sum()
    anotar("SDP población", "control", f"Bogotá 2025 = {tot:,.0f} habitantes (suma de localidades, cabecera + rural)")
    return pob


def poblacion_upz() -> pd.DataFrame:
    """Proyecciones de población por UPZ y año."""
    largo = _poblacion("sdp_poblacion_upz_2005_2035.ods", ["Código UPZ", "Código Localidad"], "SDP población UPZ")
    largo["upz"] = pd.to_numeric(largo["Código UPZ"], errors="coerce")
    largo = largo.dropna(subset=["upz"])
    t = largo.groupby(["upz", "anio"], as_index=False)["personas"].sum()
    t["upz"] = t["upz"].astype(int)
    return t


# ------------------------------------------------------------------ EBCC 2025 (microdatos)
def ebcc() -> pd.DataFrame:
    """Lee los microdatos de la Bienal de Cultura Ciudadana 2025 y construye las variables del análisis con su factor de expansión."""
    hojas = pd.ExcelFile(CRUDOS / "ebcc_2025_cultura_ciudadana.xlsx").sheet_names
    hoja = next(h for h in hojas if "dato" in h.lower()) if any("dato" in h.lower() for h in hojas) else hojas[0]
    d = pd.read_excel(CRUDOS / "ebcc_2025_cultura_ciudadana.xlsx", sheet_name=hoja)
    anotar("Bienal 2025", "lectura", f"hoja '{hoja}': {d.shape[0]} personas × {d.shape[1]} variables")
    n = lambda c: pd.to_numeric(d[c], errors="coerce") if c in d.columns else pd.Series(np.nan, index=d.index)
    si = lambda c, v: n(c).isin(v).astype(float).where(n(c).notna())
    x = pd.DataFrame({
        "id": d["encuestado_id"], "localidad": n("V1"), "estrato": n("V2"), "peso": n("FACTOR"),
        "mujer": (n("D1") == 2).astype(float), "edad": n("D3"),
        "arrienda": (n("V4") == 1).astype(float),
        # resultados
        "zona_insegura": si("P66.8", [1, 2]), "ciudad_insegura": si("P74", [1, 2]),
        "ciudad_peor_que_antes": si("P77", [3]), "miedo_espacio_publico": si("P63", [3]),
        # entorno percibido (zona)
        "alumbrado_malo": si("P66.1", [1, 2]), "aire_malo": si("P66.2", [1, 2]), "ruido_malo": si("P66.3", [1, 2]),
        "zonas_verdes_malas": si("P66.5", [1, 2]), "conexion_peatonal_mala": si("P66.7", [1, 2]),
        "ventas_informales_malo": si("P66.9", [1, 2]),
        # parque más cercano (solo a quien tiene parque cerca; sin parque = 0 y se controla aparte)
        "sin_parque": si("P67", [2]),
        "parque_spa": ((n("P72.10") == 1) | (n("P72.11") == 1)).astype(float),
        "parque_atracos": (n("P72.13") == 1).astype(float), "parque_acoso": (n("P72.12") == 1).astype(float),
        "parque_rinas": (n("P72.14") == 1).astype(float),
        # experiencia
        "presencio_acoso": ((n("P11.1") == 1) | (n("P11.4") == 1)).astype(float),
        # proporción de las 6 situaciones de conflicto vecinal que ocurren en su barrio (0 a 1)
        "conflictos_vecinos": d[[c for c in d.columns if c.startswith("P53.")]]
        .apply(pd.to_numeric, errors="coerce").eq(1).mean(axis=1),
        "razon_inseguridad": n("P75"),
    })
    antes = len(x)
    x = x[x["edad"] >= 18]
    anotar("Bienal 2025", "universo", f"se conservan adultos (18+): {len(x)} de {antes}; el modelo usa las 19 localidades urbanas")
    x = x[x["localidad"].isin(URBANAS)].copy()
    x["localidad"] = x["localidad"].astype(int)
    anotar("Bienal 2025", "recodificación", "escalas 1-4/1-5 → 1 si 'malo/muy malo' o 'insegura/muy insegura'; 'no sabe' queda vacío")
    anotar("Bienal 2025", "peso", f"factor de expansión FACTOR: suma {x['peso'].sum():,.0f} adultos urbanos representados")
    return x


# ------------------------------------------------------------------ EMV ola 8 (microdatos)
def emv() -> pd.DataFrame:
    """Lee la Encuesta Mundial de Valores 2024, le pega la localidad recuperada y construye victimización y miedo."""
    d = pd.read_excel(CRUDOS / "emv_ola8_2024.xlsx")
    cruce = pd.read_csv(CRUDOS / "emv_localidad_por_registro.csv")
    d["id_procesamiento"] = np.arange(1, len(d) + 1)
    d = d.merge(cruce[["id_procesamiento", "localidad"]], on="id_procesamiento", how="left")
    b = d[d["MUNICIPIO"].astype(str).str.contains("BOGOT", case=False)].copy()
    anotar("EMV 2024", "lectura", f"{len(d)} encuestas nacionales; {len(b)} en Bogotá")
    col = lambda pref: next(c for c in b.columns if str(c).startswith(pref))
    et = lambda pref: b[col(pref)].astype(str)
    x = pd.DataFrame({
        "localidad": b["localidad"].map(cod_localidad), "peso": pd.to_numeric(b["FACTOR_PONDERACION"], errors="coerce"),
        "mujer": et("CS1.").str.lower().str.contains("mujer").astype(float),
        "edad": pd.to_numeric(b[col("Q262.")], errors="coerce"),
        "estrato": pd.to_numeric(b["ESTRATO"].astype(str).str.extract(r"(\d)")[0], errors="coerce"),
        "victima": et("Q144.").str.strip().str.lower().eq("si").astype(float),
        "barrio_inseguro": et("Q131.").str.match(r"^[34]\.").astype(float),
        "no_sale_noche": et("Q140.").str.strip().str.lower().eq("si").astype(float),
        "no_lleva_dinero": et("Q139.").str.strip().str.lower().eq("si").astype(float),
        "lleva_arma": et("Q141.").str.strip().str.lower().eq("si").astype(float),
        "teme_acoso_sexual": et("Q146_3.").str.match(r"^[12]\.").astype(float),
        "teme_robo": et("Q146_1.").str.match(r"^[12]\.").astype(float),
        "desconfia_policia": et("Q69.").str.match(r"^[34]\.").astype(float),
    })
    sin = int(x["localidad"].isna().sum())
    anotar("EMV 2024", "llave", f"localidad recuperada del tablero oficial (cruce por id de registro); sin localidad: {sin}")
    return x.dropna(subset=["localidad"]).astype({"localidad": int})


# ------------------------------------------------------------------ contexto físico
def alumbrado() -> pd.DataFrame:
    """Lee el inventario de luminarias de la UAESP y lo agrega por localidad."""
    d = pd.read_csv(CRUDOS / "uaesp_alumbrado_2019_08.csv", sep=None, engine="python", encoding="utf-8")
    d.columns = [re.sub(r"\s+", " ", c).strip().lower() for c in d.columns]
    d["localidad"] = d["localidad"].map(cod_localidad)
    d = d.dropna(subset=["localidad"])
    out = pd.DataFrame({"localidad": d["localidad"].astype(int),
                        "luminarias": _num(d["cantidad de luminaria"]),
                        "luminarias_led": _num(d["luminarias tecnologia led"])})
    anotar("UAESP alumbrado", "vigencia", "último corte publicado en el portal: agosto de 2019, agregado por localidad")
    return out


def espacio_publico() -> pd.DataFrame:
    """Lee el espacio público efectivo por localidad (DADEP)."""
    d = pd.read_csv(CRUDOS / "dadep_ep_efectivo_localidad.csv")
    return pd.DataFrame({"localidad": pd.to_numeric(d["LOCCODIGO"]).astype(int), "ep_efectivo_m2_hab": d["EPE"].astype(float)})


def localidades_geo():
    """Lee los límites de las localidades de IDECA en coordenadas geográficas (EPSG:4326)."""
    import geopandas as gpd

    g = gpd.read_file(CRUDOS / "ideca_localidades.geojson").to_crs(4326)
    g["localidad"] = g["LocCodigo"].astype(int)
    g["area_km2"] = g["LocArea"].astype(float) / 1e6
    return g[["localidad", "area_km2", "geometry"]]
