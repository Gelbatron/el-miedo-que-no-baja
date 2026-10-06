"""
Pipeline completo: fuentes -> limpieza -> integración -> modelos -> salidas.

    python -m src.pipeline            (o: python src/pipeline.py)

Escribe:
  data/procesados/   tablas limpias e integradas (CSV)
  outputs/tablas/    resultados de cada modelo (CSV)
  outputs/resultados.json   todas las cifras que citan el informe, el visor y el pitch
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import fuentes  # noqa: E402
import indicadores as I  # noqa: E402
import limpieza as L  # noqa: E402
import modelos as M  # noqa: E402
from territorio import LOCALIDADES  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "procesados"
TAB = RAIZ / "outputs" / "tablas"

PERFIL = ["mujer", "edad", "estrato", "arrienda"]
DELITO = ["hurtos_100k_miles", "homicidios_100k", "narcoticos_100k_cientos"]
HECHOS = ["parque_atracos", "parque_spa", "sin_parque", "presencio_acoso", "conflictos_vecinos"]
CALIFICACIONES = ["alumbrado_malo", "ventas_informales_malo"]
ETIQUETAS = {
    "mujer": "Ser mujer", "edad": "Edad (por año)", "estrato": "Estrato (por nivel)", "arrienda": "Vive en arriendo",
    "hurtos_100k_miles": "Hurtos en la localidad (+1.000 por 100 mil)",
    "homicidios_100k": "Homicidios en la localidad (+1 por 100 mil)",
    "narcoticos_100k_cientos": "Llamadas 123 por narcóticos (+100 por 100 mil)",
    "parque_atracos": "Atracos en el parque más cercano", "parque_spa": "Venta o consumo de drogas en el parque",
    "sin_parque": "No tiene parque cerca", "presencio_acoso": "Presenció acoso a mujeres",
    "conflictos_vecinos": "Conflictos vecinales (de ninguno a todos)",
    "alumbrado_malo": "Alumbrado público malo en su zona", "ventas_informales_malo": "Ventas informales: situación mala",
    "victima": "Fue víctima de un delito (último año)",
}


def cargar():
    """Fuentes limpias y estandarizadas."""
    fuentes.obtener_todas()
    t = {"delitos": L.delitos(), "incidentes": L.incidentes(), "poblacion": L.poblacion_localidad(),
         "ebcc": L.ebcc(), "emv": L.emv(), "alumbrado": L.alumbrado(), "espacio_publico": L.espacio_publico(),
         "geo": L.localidades_geo()}
    t["incidentes_upz"], t["geo_upz"] = L.incidentes_upz()
    t["poblacion_upz"] = L.poblacion_upz()
    return t


def integrar(t: dict):
    P = I.panel_localidad(t["delitos"], t["incidentes"], t["poblacion"], t["ebcc"], t["emv"],
                          t["alumbrado"], t["espacio_publico"], t["geo"])
    ctx = P.set_index("localidad")[["hurtos_100k", "homicidios_100k", "incidentes_narcoticos_100k"]]
    eb = t["ebcc"].merge(ctx, left_on="localidad", right_index=True, how="left")
    eb["hurtos_100k_miles"] = eb["hurtos_100k"] / 1000
    eb["narcoticos_100k_cientos"] = eb["incidentes_narcoticos_100k"] / 100
    L.anotar("Integración", "cruce", f"{len(eb)} personas de la Bienal con el delito e incidentes 123 de su localidad (SCJ 2025)")
    # UPZ: incidentes 123 por 100.000 habitantes (ene-ago 2025)
    pu = t["poblacion_upz"][t["poblacion_upz"]["anio"] == I.ANIO].set_index("upz")["personas"]
    iu = t["incidentes_upz"][t["incidentes_upz"]["anio"] == I.ANIO].copy()
    iu["poblacion"] = iu["upz"].map(pu)
    sin = iu[iu["poblacion"].isna()]["upz"].nunique()
    iu = iu.dropna(subset=["poblacion"])
    iu = iu[iu["poblacion"] >= 1000]
    iu["tasa"] = iu["casos"] / iu["poblacion"] * 1e5
    L.anotar("Integración", "UPZ", f"incidentes 123 por UPZ con población SDP; {sin} UPZ sin población (rurales o nuevas) excluidas")
    return P, eb, iu


def modelar(P, eb, emv, n_boot: int = 300) -> dict:
    R = {}
    R["m_hechos"] = M.logit_ame(eb, "zona_insegura", PERFIL + DELITO + HECHOS, n_boot=n_boot)
    R["m_calif"] = M.logit_ame(eb, "zona_insegura", PERFIL + DELITO + HECHOS + CALIFICACIONES, n_boot=n_boot)
    R["m_ciudad"] = M.logit_ame(eb, "ciudad_insegura", PERFIL + DELITO + HECHOS, n_boot=n_boot // 2)
    R["m_miedo"] = M.logit_ame(eb, "miedo_espacio_publico", PERFIL + DELITO + HECHOS, n_boot=n_boot // 2)
    R["m_efectos_fijos"] = M.logit_ame(
        eb.join(pd.get_dummies(eb["localidad"], prefix="loc", drop_first=True, dtype=float)),
        "zona_insegura", PERFIL + HECHOS + [f"loc_{i}" for i in range(2, 20)], n_boot=n_boot // 3)
    R["lpm_wild"] = M.lpm_wild(eb, "zona_insegura", PERFIL + DELITO + HECHOS,
                               probar=DELITO + ["parque_atracos", "conflictos_vecinos"])
    R["auc"] = M.auc_por_bloques(eb, "zona_insegura", {
        "Perfil (sexo, edad, estrato, tenencia)": PERFIL,
        "Perfil + delito registrado": PERFIL + DELITO,
        "Perfil + hechos del entorno": PERFIL + HECHOS,
        "Perfil + hechos + delito": PERFIL + HECHOS + DELITO,
        "Perfil + calificación del entorno": PERFIL + CALIFICACIONES,
        "Todo": PERFIL + DELITO + HECHOS + CALIFICACIONES})
    emv_m = emv.dropna(subset=["edad", "estrato"])
    for y in ["no_sale_noche", "teme_acoso_sexual", "barrio_inseguro"]:
        R[f"emv_{y}"] = M.logit_ame(emv_m, y, ["mujer", "edad", "estrato", "victima"], n_boot=n_boot)
    R["escenarios"] = M.escenarios(eb, "zona_insegura", PERFIL + DELITO + HECHOS + ["alumbrado_malo"],
                                   palancas=("alumbrado_malo", "parque_atracos"))
    return R


def territorio(P, eb, t) -> dict:
    out = {"ibs": I.indice_brecha(P, eb), "cifra_oculta": I.cifra_oculta(P, t["delitos"], t["poblacion"])}
    pruebas = [
        ("Drogas en el parque (Bienal) vs incidentes por narcóticos 123", "parque_spa", "incidentes_narcoticos_100k"),
        ("Zona insegura (Bienal) vs riñas 123", "zona_insegura", "incidentes_rinas_100k"),
        ("Alumbrado malo (Bienal) vs luminarias por km² (UAESP 2019)", "alumbrado_malo", "luminarias_km2_2019"),
        ("Víctimas (EMV) vs delitos registrados (SCJ)", "emv_victima", "delitos_alto_impacto_100k"),
        ("Zona insegura (Bienal) vs delitos registrados (SCJ)", "zona_insegura", "delitos_alto_impacto_100k"),
        ("Barrio inseguro (EMV) vs zona insegura (Bienal)", "emv_barrio_inseguro", "zona_insegura"),
    ]
    val = []
    for nombre, a, b in pruebas:
        r = I.spearman(P[a], P[b])
        val.append({"prueba": nombre, **r})
    m = out["ibs"].merge(out["cifra_oculta"], on="localidad")
    val.append({"prueba": "Índice de Brecha vs cifra oculta (víctimas por delito registrado)", **I.spearman(m["ibs"], m["razon"])})
    V = pd.DataFrame(val)
    V["p_bh"] = I.bh(V["p"])
    out["validaciones"] = V
    return out


def guardar(t, P, eb, iu, R, T):
    for d in (PROC, TAB):
        d.mkdir(parents=True, exist_ok=True)
    t["delitos"].to_csv(PROC / "scj_delitos_localidad_largo.csv", index=False)
    t["incidentes"].to_csv(PROC / "scj_incidentes_123_localidad_largo.csv", index=False)
    iu.to_csv(PROC / "scj_incidentes_123_upz_2025.csv", index=False)
    t["poblacion"].to_csv(PROC / "sdp_poblacion_localidad_grupos.csv", index=False)
    eb.to_csv(PROC / "ebcc_2025_analitica.csv", index=False)
    t["emv"].to_csv(PROC / "emv_2024_bogota_analitica.csv", index=False)
    P.to_csv(PROC / "panel_localidad_2025.csv", index=False)
    for k, v in R.items():
        v.to_csv(TAB / f"{k}.csv", index=False)
    for k, v in T.items():
        v.to_csv(TAB / f"{k}.csv", index=False)
    L.bitacora().to_csv(TAB / "bitacora_limpieza.csv", index=False)


def resumen(t, P, eb, R, T) -> dict:
    """Las cifras que se citan en el informe, el visor y el pitch, en un solo lugar."""
    serie = I.serie_bogota(t["delitos"])
    s = serie.pivot(index="codigo", columns="anio", values="casos")
    w = lambda c: float(np.average(eb[c], weights=eb["peso"]) * 100)
    ame = lambda m, v: {k: round(float(R[m].set_index("variable").loc[v, k]), 2) for k in ("ame_pp", "ic_inf", "ic_sup", "p")}
    auc = R["auc"].set_index("bloque")["auc"].round(3).to_dict()
    co = T["cifra_oculta"]
    emv = t["emv"]
    pct = lambda col, sexo: float(np.average(emv[emv["mujer"] == sexo][col], weights=emv[emv["mujer"] == sexo]["peso"]) * 100)
    V = T["validaciones"].set_index("prueba")
    return {
        "hurto_personas": {"2019": int(s.loc["HP", 2019]), "2026": int(s.loc["HP", 2026]),
                           "cambio_pct": round((s.loc["HP", 2026] / s.loc["HP", 2019] - 1) * 100, 1)},
        "hurto_motos_cambio_pct": round((s.loc["HM", 2026] / s.loc["HM", 2019] - 1) * 100, 1),
        "vif_cambio_pct_2018_2026": round((s.loc["VI", 2026] / s.loc["VI", 2018] - 1) * 100, 1),
        "delitos_sexuales_cambio_pct_2018_2026": round((s.loc["DS", 2026] / s.loc["DS", 2018] - 1) * 100, 1),
        "ciudad_insegura_pct": round(w("ciudad_insegura"), 1), "zona_insegura_pct": round(w("zona_insegura"), 1),
        "ciudad_peor_que_antes_pct": round(w("ciudad_peor_que_antes"), 1),
        "miedo_espacio_publico_pct": round(w("miedo_espacio_publico"), 1),
        "n_bienal": int(len(eb)), "n_emv_bogota": int(len(emv)),
        "adultos_urbanos_bienal": int(eb["peso"].sum()),
        "ame_hechos": {v: ame("m_hechos", v) for v in PERFIL + DELITO + HECHOS},
        "ame_calificaciones": {v: ame("m_calif", v) for v in CALIFICACIONES},
        "auc": auc,
        "emv_mujer_ame": {y: ame(f"emv_{y}", "mujer") for y in ["no_sale_noche", "teme_acoso_sexual", "barrio_inseguro"]},
        "emv_victima_ame_barrio": ame("emv_barrio_inseguro", "victima"),
        "emv_por_sexo": {c: {"mujeres": round(pct(c, 1.0), 1), "hombres": round(pct(c, 0.0), 1)}
                         for c in ["victima", "no_sale_noche", "teme_acoso_sexual", "barrio_inseguro"]},
        "cifra_oculta_bogota": round(float(co["victimas_estimadas"].sum() / co["delitos_registrados"].sum()), 1),
        "cifra_oculta_max": [LOCALIDADES[int(co.loc[co["razon"].idxmax(), "localidad"])], round(float(co["razon"].max()), 1)],
        "cifra_oculta_min": [LOCALIDADES[int(co.loc[co["razon"].idxmin(), "localidad"])], round(float(co["razon"].min()), 1)],
        "ibs_vs_cifra_oculta": {k: round(float(v), 3) for k, v in V.loc["Índice de Brecha vs cifra oculta (víctimas por delito registrado)",
                                                                     ["rho", "p", "ic_inf", "ic_sup", "p_bh"]].items()},
        "ibs_top5": [LOCALIDADES[int(l)] for l in T["ibs"]["localidad"].head(5)],
        "poblacion_2025": int(t["poblacion"][(t["poblacion"]["anio"] == 2025) & (t["poblacion"]["grupo"] == "total")]["personas"].sum()),
    }


def figuras_y_exportes(res: dict):
    """Figuras PNG, JSON del visor, descargas CSV/GeoJSON y tablas de Power BI."""
    import exportar as EX
    import figuras as F

    t, P, R, T, S = res["t"], res["P"], res["R"], res["T"], res["S"]
    rutas = [F.serie(t["delitos"]), F.mapas(t["geo"], P), F.efectos(R["m_hechos"], ETIQUETAS), F.auc(R["auc"]),
             F.brecha_cifra(T["ibs"], T["cifra_oculta"], S["ibs_vs_cifra_oculta"]["rho"]), F.genero(S["emv_por_sexo"]),
             F.ranking_ibs(T["ibs"])]
    rutas.append(EX.visor(res, ETIQUETAS))
    return rutas


def correr(n_boot: int = 300, exportes: bool = True) -> dict:
    t0 = time.time()
    t = cargar()
    P, eb, iu = integrar(t)
    R = modelar(P, eb, t["emv"], n_boot)
    T = territorio(P, eb, t)
    guardar(t, P, eb, iu, R, T)
    S = resumen(t, P, eb, R, T)
    (RAIZ / "outputs" / "resultados.json").write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")
    res = {"t": t, "P": P, "eb": eb, "iu": iu, "R": R, "T": T, "S": S}
    if exportes:
        figuras_y_exportes(res)
    print(f"Pipeline completo en {time.time() - t0:.0f} s")
    return res


if __name__ == "__main__":
    correr()
