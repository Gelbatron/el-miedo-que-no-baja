"""
Exporta al visor (visor/data/frentes.json) los resultados de los cuatro frentes y de los modelos:
validación del registro (capa SCJ frente a Policía y Medicina Legal), tendencias en ventana comparable,
aprendizaje supervisado, tipología de localidades, confianza en la Policía, score de confiabilidad,
victimización y denuncia (DANE y CCB) y el frente de género (SIVIM y acoso callejero).
Solo lo que el visor muestra: el detalle completo queda en outputs/tablas y data/procesados.

Solo lee tablas ya calculadas en outputs/tablas y data/procesados: no estima nada nuevo.
"""
import json
import math
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
TAB = RAIZ / "outputs" / "tablas"
PROC = RAIZ / "data" / "procesados"
SALIDA = RAIZ / "visor" / "data" / "frentes.json"


def _limpio(x):
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    return x


def _registros(df: pd.DataFrame) -> list[dict]:
    return [{k: _limpio(v) for k, v in r.items()} for r in df.to_dict("records")]


def _si_existe(ruta: Path):
    return pd.read_csv(ruta) if ruta.exists() else None


def _filas(df: pd.DataFrame, cols: list[str]) -> list[dict]:
    return _registros(df[[c for c in cols if c in df.columns]])


def construir() -> dict:
    out = {}
    out["tendencias"] = _registros(pd.read_csv(TAB / "tendencias_resumen.csv"))
    out["ml"] = {
        "completo": _registros(pd.read_csv(TAB / "ml_comparacion_modelos.csv")),
        "sin_calificaciones": _registros(pd.read_csv(TAB / "ml_comparacion_modelos_sin_calificaciones.csv")),
        "bloques_sin_calificaciones": _registros(pd.read_csv(TAB / "ml_importancia_bloques_sin_calificaciones.csv")),
        "contexto_localidad": _registros(pd.read_csv(TAB / "ml_contexto_localidad.csv")),
    }
    out["confianza_policia"] = {"bogota_desconfia_pct": float(pd.read_csv(TAB / "confianza_policia_bogota.csv")["valor"].iloc[0])}
    out["confiabilidad"] = _registros(pd.read_csv(TAB / "confiabilidad_fuentes.csv"))
    hom = _si_existe(TAB / "homicidios_localidad_periodos.csv")
    if hom is not None:
        out["homicidios_localidad"] = _registros(hom)
    tip = _si_existe(TAB / "tipologia_localidades.csv")
    if tip is not None:
        out["tipologia"] = {"localidades": _registros(tip), "perfiles_z": _registros(pd.read_csv(TAB / "tipologia_perfiles_z.csv"))}

    # validación del registro
    raz = pd.read_csv(TAB / "registro_razon_scj_siedco.csv")
    out["registro"] = {
        "hurto_personas": _registros(pd.read_csv(TAB / "registro_hurto_personas.csv")),
        "razones": _filas(raz[raz["codigo"].isin(["HP", "HR", "HA", "H", "LP", "DS", "VI"])],
                          ["codigo", "anio", "scj", "siedco", "inmlcf", "razon_scj_siedco", "razon_scj_inmlcf"]),
        "estado": _registros(pd.read_csv(TAB / "registro_estado_series.csv")),
        "etiquetas": _registros(pd.read_csv(TAB / "registro_etiquetas_cruzadas.csv")),
    }

    # victimización y denuncia (encuestas): solo las series del contraste
    v = _si_existe(PROC / "victimizacion_denuncia_bogota.csv")
    if v is not None:
        v = v[v["indicador"].isin(["victimizacion", "tasa_denuncia", "victimas_miles", "percepcion_inseguridad_ciudad"]) & (v["anio"] >= 2018)].copy()
        v["fuente"] = v["fuente"].str.split("|").str[0].str.strip()
        out["encuestas"] = _filas(v, ["anio", "fuente", "indicador", "delito", "valor"])

    # género: SIVIM y acoso callejero
    g = {}
    cre = _si_existe(PROC / "genero_violencia_crecimiento.csv")
    if cre is not None:
        g["localidades"] = _filas(cre, ["localidad", "nombre", "tasa_mujeres_2019", "tasa_mujeres_2022", "tasa_mujeres_2025", "cambio_pct_2019_2025",
                                        "cambio_pct_2019_2025_ic_inf", "cambio_pct_2019_2025_ic_sup", "cambio_pct_2022_2025", "q_bh_frente_resto_2019_2025",
                                        "casos_mujeres_2025", "casos_mujeres_via_publica_2025"])
    per = _si_existe(PROC / "genero_violencia_perfil.csv")
    if per is not None:
        per = per[per["dimension"].isin(["grupo_edad", "lugar_del_caso"])]
        g["perfil"] = _filas(per, ["dimension", "sexo_victima", "categoria", "casos_2019", "casos_2025", "pct_2025", "tasa_2019", "tasa_2025",
                                   "cambio_tasa_pct_2019_2025", "cambio_casos_pct_2019_2025"])
    aco = _si_existe(PROC / "acoso_callejero_bogota.csv")
    if aco is not None:
        g["acoso"] = _filas(aco[aco["nivel"].isin(["Total", "Género"])], ["nivel", "genero", "n", "pct_acoso_12_meses", "pct_miedo_acoso",
                                                                         "pct_calles_oscuras_muy_inseguras", "pct_siempre_busca_lugares_alumbrados",
                                                                         "pct_acoso_de_noche", "pct_denuncio"])
    pru = _si_existe(PROC / "genero_pruebas_spearman.csv")
    if pru is not None:
        g["pruebas"] = _registros(pru)
    out["genero"] = g
    mov = _si_existe(PROC / "movilidad_pruebas_hipotesis.csv")
    if mov is not None:
        mov = mov[mov["especificacion"].str.startswith("principal")]
        out["movilidad"] = {"pruebas": _filas(mov, ["bloque", "y", "x", "x_nombre", "n", "rho", "ic95_inf", "ic95_sup", "p_permutacion", "p_bh_bloque"])}
    return out


def guardar(datos: dict) -> Path:
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return SALIDA


if __name__ == "__main__":
    ruta = guardar(construir())
    print(ruta, round(ruta.stat().st_size / 1e3), "KB")
