"""
Tendencias del registro de delitos con el efecto pandemia separado.

Por qué un modelo y no solo porcentajes: el cambio de un año a otro mezcla la tendencia real, el
encierro de 2020-2021 y el tamaño de cada localidad. Un modelo de conteo de panel separa esas cosas
y da un intervalo de confianza para cada cambio.

Especificación (para cada tipo de delito, 19 localidades urbanas × 2018-2026, siempre enero-agosto):
    casos_lt ~ BinomialNegativa(μ_lt, α)
    log μ_lt = log(población_lt) + efecto fijo de localidad + término de tiempo
- Binomial negativa porque los conteos tienen sobredispersión (la varianza supera a la media).
- Offset de población: se modela la TASA, no el conteo.
- Errores agrupados por localidad: las 9 observaciones de una misma localidad no son independientes.

Antes de modelar se valida cada serie contra el registro de la Policía (src/validacion_registro.py):
- Validadas (homicidios, lesiones, delitos sexuales, violencia intrafamiliar): ventana 2022-2026.
- Con quiebre en 2023 (hurto a personas, residencias, automotores): solo 2023-2026, la parte comparable.
  Para Bogotá, el cambio 2022 → último año sale del SIEDCO.
- Bicicletas: sin serie externa; se reporta marcada como no validada.
- Comercio, celulares y motocicletas: la columna no coincide con su delito; no se modelan.

Tres preguntas:
1. Tendencia reciente (ventana comparable): cambio anual promedio en %, con IC 95 %.
2. ¿Hubo un salto en 2023? Razón de tasas 2023/2022 con dummies de año (solo series validadas).
3. ¿Dónde estamos frente a antes de la pandemia? Razón de tasas 2026/2019 (solo series validadas).
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from territorio import URBANAS  # noqa: E402
import validacion_registro as VR  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
TIPOS = {"HP": "Hurto a personas", "HCE": "Hurto de celulares", "HR": "Hurto a residencias", "HC": "Hurto a comercio",
         "HA": "Hurto de automotores", "HM": "Hurto de motocicletas", "HB": "Hurto de bicicletas",
         "H": "Homicidios", "LP": "Lesiones personales", "VI": "Violencia intrafamiliar", "DS": "Delitos sexuales"}


def panel(delitos: pd.DataFrame, poblacion: pd.DataFrame) -> pd.DataFrame:
    """Arma el panel localidad-año de las 19 localidades urbanas con casos y población."""
    pob = poblacion[poblacion["grupo"] == "total"][["localidad", "anio", "personas"]]
    d = delitos[delitos["localidad"].isin(URBANAS)].merge(pob, on=["localidad", "anio"], how="left")
    return d.dropna(subset=["casos", "personas"])


def _nb(d: pd.DataFrame, X: pd.DataFrame):
    """Ajusta una binomial negativa con exposición poblacional y errores agrupados por localidad."""
    m = sm.NegativeBinomial(d["casos"].astype(float), X.astype(float), exposure=d["personas"].astype(float))
    return m.fit(disp=0, maxiter=300, cov_type="cluster", cov_kwds={"groups": d["localidad"].values})


def _efectos_fijos(d: pd.DataFrame) -> pd.DataFrame:
    """Variables indicadoras de localidad (efectos fijos), omitiendo una como base."""
    return pd.get_dummies(d["localidad"], prefix="loc", drop_first=True, dtype=float)


def tendencia_post(d: pd.DataFrame, desde: int = 2022) -> dict:
    """Cambio anual promedio desde `desde` hasta el último año, con IC 95 % agrupado por localidad."""
    s = d[d["anio"] >= desde].reset_index(drop=True)
    X = sm.add_constant(pd.concat([_efectos_fijos(s), (s["anio"] - desde).rename("anio")], axis=1))
    r = _nb(s, X)
    b, (lo, hi) = r.params["anio"], r.conf_int().loc["anio"]
    return {"cambio_anual_pct": (np.exp(b) - 1) * 100, "ic_inf": (np.exp(lo) - 1) * 100, "ic_sup": (np.exp(hi) - 1) * 100,
            "p": float(r.pvalues["anio"]), "alpha": float(r.params.get("alpha", np.nan))}


def perfil_anual(d: pd.DataFrame, base: int = 2022) -> pd.DataFrame:
    """Razón de tasas de cada año frente al año base (efectos fijos de localidad)."""
    s = d.reset_index(drop=True)
    anios = pd.get_dummies(s["anio"], prefix="a", dtype=float).drop(columns=f"a_{base}")
    r = _nb(s, sm.add_constant(pd.concat([_efectos_fijos(s), anios], axis=1)))
    ic = r.conf_int()
    filas = [{"anio": base, "irr": 1.0, "ic_inf": 1.0, "ic_sup": 1.0, "p": np.nan}]
    for c in anios.columns:
        filas.append({"anio": int(c[2:]), "irr": float(np.exp(r.params[c])), "ic_inf": float(np.exp(ic.loc[c, 0])),
                      "ic_sup": float(np.exp(ic.loc[c, 1])), "p": float(r.pvalues[c])})
    return pd.DataFrame(filas).sort_values("anio")


def correr() -> dict:
    """Estima la tendencia anual de cada delito en su ventana comparable y guarda el resumen."""
    delitos = pd.read_csv(RAIZ / "data" / "procesados" / "scj_delitos_localidad_largo.csv")
    poblacion = pd.read_csv(RAIZ / "data" / "procesados" / "sdp_poblacion_localidad_grupos.csv")
    P = panel(delitos, poblacion)
    E = VR.estado_series().set_index("codigo")
    bogota = VR.serie_bogota_validada(delitos, E.reset_index()).pivot(index="codigo", columns="anio", values="casos")
    resumen, perfiles = [], []
    for cod, nombre in TIPOS.items():
        d = P[P["codigo"] == cod]
        if d.empty or E.loc[cod, "estado"] == "no_coincide":
            continue
        estado = E.loc[cod, "estado"]
        desde = 2023 if estado == "quiebre" else 2022
        ultimo = int(d["anio"].max())
        bog = bogota.loc[cod].dropna()
        t = tendencia_post(d, desde)
        pa = perfil_anual(d[d["anio"] >= desde] if estado == "quiebre" else d, base=desde).assign(codigo=cod, tipo=nombre)
        perfiles.append(pa)
        pa = pa.set_index("anio")
        comparable = estado != "quiebre"
        r23 = pa.loc[2023] if comparable else pd.Series({"irr": np.nan, "ic_inf": np.nan, "ic_sup": np.nan, "p": np.nan})
        resumen.append({
            "codigo": cod, "tipo": nombre, "estado": estado, "ventana": f"{desde}-{ultimo}", "ultimo_anio": ultimo,
            "fuente_bogota": "SIEDCO" if estado == "quiebre" else "SCJ",
            "casos_2019": bog.get(2019), "casos_2022": bog.get(2022), "casos_ultimo": bog.get(ultimo),
            "cambio_bruto_2022_ultimo_pct": (bog.get(ultimo) / bog.get(2022) - 1) * 100,
            **{f"post_{k}": v for k, v in t.items()},
            "irr_2023_vs_2022": r23["irr"], "irr_2023_ic_inf": r23["ic_inf"], "irr_2023_ic_sup": r23["ic_sup"], "irr_2023_p": r23["p"],
            "irr_ultimo_vs_2019": pa.loc[ultimo, "irr"] / pa.loc[2019, "irr"] if comparable else np.nan,
        })
    R = pd.DataFrame(resumen)
    PF = pd.concat(perfiles, ignore_index=True)
    sal = RAIZ / "outputs" / "tablas"
    R.to_csv(sal / "tendencias_resumen.csv", index=False)
    PF.to_csv(sal / "tendencias_perfil_anual.csv", index=False)
    return {"resumen": R, "perfil": PF}


if __name__ == "__main__":
    out = correr()
    pd.set_option("display.width", 220)
    cols = ["tipo", "estado", "ventana", "cambio_bruto_2022_ultimo_pct", "post_cambio_anual_pct", "post_ic_inf", "post_ic_sup", "post_p",
            "irr_2023_vs_2022", "irr_2023_ic_inf", "irr_2023_ic_sup", "irr_ultimo_vs_2019"]
    print(out["resumen"][cols].round(3).to_string(index=False))
