"""
Validación del registro antes de modelar: ¿la serie de cada delito es comparable en el tiempo?

La capa «Delitos Alto Impacto» de la SCJ (la que usa el proyecto) se contrasta, delito por delito y año
por año (enero-agosto, Bogotá), con dos fuentes independientes: el registro de la Policía Nacional
(SIEDCO, datos.gov.co) y los presuntos homicidios de Medicina Legal. La descarga y el cruce los hace
src/fuentes_victimizacion.py; este módulo convierte ese cruce en reglas que usa todo el proyecto.

Lo que sale (y por qué importa):
- Homicidios, lesiones personales, delitos sexuales y violencia intrafamiliar: razón SCJ/SIEDCO entre
  1,00 y 1,09 todos los años → serie validada; se usa la capa SCJ, que trae la localidad.
- Hurto a personas, residencias y automotores: razón de 2 a 3 en 2018-2022 y de 1,00 desde 2023 → quiebre
  de serie. Para Bogotá se usa el SIEDCO; por localidad, solo de 2023 en adelante.
- Hurto de bicicletas: no hay serie externa con qué validarlo.
- Hurto a comercio, celulares y motocicletas: desde 2023 la columna de un delito coincide caso por caso con
  OTRO delito del SIEDCO (por ejemplo, «motocicletas» de la capa = «comercio» de la Policía). No se usan
  por tipo; el total de delitos no cambia, porque las columnas se suman todas.

Escribe outputs/tablas/registro_razon_scj_siedco.csv, registro_etiquetas_cruzadas.csv,
registro_estado_series.csv y registro_hurto_personas.csv.
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "procesados"
TAB = RAIZ / "outputs" / "tablas"
SCJ, SIEDCO = "SCJ capa Delitos Alto Impacto", "SIEDCO (Policía Nacional, datos.gov.co)"
INMLCF = "INMLCF presuntos homicidios (definitivo)"
ANIOS_CRUCE = [2023, 2024, 2025]  # años cerrados en que las dos fuentes deberían coincidir
TOLERANCIA = (0.95, 1.10)         # una razón dentro de este rango cuenta como «la misma serie»
NOMBRES = {"HP": "Hurto a personas", "HR": "Hurto a residencias", "HA": "Hurto de automotores", "HB": "Hurto de bicicletas",
           "HC": "Hurto a comercio", "HCE": "Hurto de celulares", "HM": "Hurto de motocicletas", "H": "Homicidios",
           "LP": "Lesiones personales", "VI": "Violencia intrafamiliar", "DS": "Delitos sexuales"}


def contraste() -> pd.DataFrame:
    """Casos enero-agosto por delito, año y fuente (columnas scj, siedco, inmlcf)."""
    d = pd.read_csv(PROC / "registro_contraste_bogota.csv")
    d = d[d["periodo"] == "ene-ago"]
    w = d.pivot_table(index=["codigo", "anio"], columns="fuente", values="casos").reset_index()
    return w.rename(columns={SCJ: "scj", SIEDCO: "siedco", INMLCF: "inmlcf"})[["codigo", "anio", "scj", "siedco", "inmlcf"]]


def razones(C: pd.DataFrame | None = None) -> pd.DataFrame:
    C = contraste() if C is None else C
    C = C.copy()
    C["razon_scj_siedco"] = C["scj"] / C["siedco"]
    C["razon_scj_inmlcf"] = C["scj"] / C["inmlcf"]
    return C[C["anio"].between(2018, 2026)]


def etiquetas_cruzadas(C: pd.DataFrame | None = None) -> pd.DataFrame:
    """Columnas de la capa que, en los años cerrados desde 2023, repiten caso por caso otro delito del SIEDCO."""
    C = contraste() if C is None else C
    s = C[C["anio"].isin(ANIOS_CRUCE)].pivot(index="anio", columns="codigo", values="scj")
    p = C[C["anio"].isin(ANIOS_CRUCE)].pivot(index="anio", columns="codigo", values="siedco").dropna(axis=1, how="all")
    filas = []
    for a in s.columns:
        for b in p.columns:
            if a != b and (s[a] - p[b]).abs().max() <= 1:
                filas.append({"columna_capa": a, "dice": NOMBRES[a], "coincide_con_siedco": b, "que_es_en_siedco": NOMBRES[b],
                              **{f"capa_{y}": int(s.loc[y, a]) for y in ANIOS_CRUCE}, **{f"siedco_{y}": int(p.loc[y, b]) for y in ANIOS_CRUCE}})
    return pd.DataFrame(filas)


def estado_series(C: pd.DataFrame | None = None) -> pd.DataFrame:
    """Para cada delito: si la serie es comparable, desde qué año, y qué fuente usar para Bogotá."""
    R = razones(C)
    cruz = etiquetas_cruzadas(C)
    lo, hi = TOLERANCIA
    filas = []
    for cod, nombre in NOMBRES.items():
        r = R[R["codigo"] == cod].set_index("anio")["razon_scj_siedco"].dropna()
        r = r[r.index <= 2025]  # 2026 aún se actualiza en las dos fuentes
        dentro = r.between(lo, hi)
        if cod in set(cruz["columna_capa"]) or (len(r) and not dentro.loc[[a for a in ANIOS_CRUCE if a in r.index]].all()):
            e = dict(estado="no_coincide", desde=np.nan, fuente_bogota="ninguna",
                     detalle="La columna no coincide con su delito en el SIEDCO; desde 2023 repite otro delito." if cod in set(cruz["columna_capa"])
                     else "No coincide con el SIEDCO en ningún año: definición distinta.")
        elif r.empty:
            e = dict(estado="sin_validar", desde=2018, fuente_bogota="SCJ", detalle="Sin serie externa con qué contrastar.")
        elif dentro.all():
            e = dict(estado="validada", desde=2018, fuente_bogota="SCJ", detalle=f"Razón SCJ/SIEDCO entre {r.min():.2f} y {r.max():.2f} en 2018-2025.")
        else:
            pre = r[r.index < 2023]
            e = dict(estado="quiebre", desde=2023, fuente_bogota="SIEDCO",
                     detalle=f"La capa vale {pre.min():.2f} a {pre.max():.2f} veces el SIEDCO en 2018-2022 y lo mismo desde 2023.")
        filas.append({"codigo": cod, "tipo": nombre, **e,
                      "razon_min_2018_2022": r[r.index < 2023].min() if len(r) else np.nan,
                      "razon_max_2018_2022": r[r.index < 2023].max() if len(r) else np.nan})
    return pd.DataFrame(filas)


def serie_bogota_validada(delitos_scj: pd.DataFrame, E: pd.DataFrame | None = None) -> pd.DataFrame:
    """Serie de Bogotá (enero-agosto) que usan el informe, el visor, el Excel y Power BI.
    Validadas y sin validar: capa SCJ (suma de localidades). Con quiebre: SIEDCO. Las que no coinciden, fuera."""
    E = estado_series() if E is None else E
    C = contraste()
    scj = delitos_scj.groupby(["codigo", "anio"], as_index=False)["casos"].sum()
    filas = []
    for e in E.itertuples():
        if e.fuente_bogota == "ninguna":
            continue
        capa = scj[scj["codigo"] == e.codigo].set_index("anio")["casos"]
        if e.fuente_bogota == "SIEDCO":
            cc = C[(C["codigo"] == e.codigo) & C["anio"].between(2018, 2026)].set_index("anio")
            s = cc["siedco"]
            capa = cc["scj"]  # el contraste usa el total de la capa (con «Sin localización»), igual que el total de la Policía
            fuente = "Policía Nacional (SIEDCO)"
        else:
            s, fuente = capa, "SCJ" + (" (validada con SIEDCO)" if e.estado == "validada" else " (sin serie externa)")
        for a, v in s.items():
            filas.append({"codigo": e.codigo, "tipo": e.tipo, "anio": int(a), "casos": int(v), "fuente": fuente,
                          "estado": e.estado, "casos_capa_scj": int(capa.get(a)) if a in capa.index else None})
    S = pd.DataFrame(filas)
    base = S[S["anio"] == 2018].set_index("codigo")["casos"]
    S["indice_2018"] = S["casos"] / S["codigo"].map(base) * 100
    return S


def hurto_personas() -> pd.DataFrame:
    """Hurto a personas: capa SCJ (total de Bogotá, con «Sin localización», como el SIEDCO), SIEDCO y encuestas
    de victimización, con índices 2022 = 100."""
    C = contraste()
    hp = C[(C["codigo"] == "HP") & C["anio"].between(2018, 2026)].set_index("anio")
    d = pd.read_csv(PROC / "registro_contraste_bogota.csv")
    anual = d[(d["codigo"] == "HP") & (d["periodo"] == "anio") & (d["fuente"] == SIEDCO) & d["completo"]].set_index("anio")["casos"]
    v = pd.read_csv(PROC / "victimizacion_denuncia_bogota.csv")
    v = v[(v["delito"] == "hurto_personas") & v["indicador"].isin(["victimizacion", "tasa_denuncia"])]
    enc = lambda pref, ind: v[v["fuente"].str.startswith(pref) & (v["indicador"] == ind)].set_index("anio")["valor"]  # noqa: E731
    capa = hp["scj"]
    T = pd.DataFrame({"capa_scj": capa, "siedco": hp["siedco"], "siedco_anio_completo": anual,
                      "ecsc_victimizacion": enc("DANE", "victimizacion"), "ecsc_denuncia": enc("DANE", "tasa_denuncia"),
                      "ccb_victimizacion": enc("CCB", "victimizacion"), "ccb_denuncia": enc("CCB", "tasa_denuncia")})
    T = T[T.index >= 2018]
    for c in ["capa_scj", "siedco", "ccb_victimizacion"]:
        T[f"{c}_2022_100"] = T[c] / T.loc[2022, c] * 100
    T.index.name = "anio"
    return T.reset_index()


def correr(delitos_scj: pd.DataFrame | None = None) -> dict:
    if delitos_scj is None:
        delitos_scj = pd.read_csv(PROC / "scj_delitos_localidad_largo.csv")
    out = {"registro_razon_scj_siedco": razones(), "registro_etiquetas_cruzadas": etiquetas_cruzadas(),
           "registro_estado_series": estado_series(), "registro_hurto_personas": hurto_personas()}
    for k, v in out.items():
        v.to_csv(TAB / f"{k}.csv", index=False)
    return out


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    pd.set_option("display.width", 220)
    o = correr()
    print(o["registro_estado_series"][["codigo", "tipo", "estado", "desde", "fuente_bogota", "detalle"]].to_string(index=False))
    print(o["registro_etiquetas_cruzadas"].to_string(index=False))
    print(o["registro_hurto_personas"].round(1).to_string(index=False))
