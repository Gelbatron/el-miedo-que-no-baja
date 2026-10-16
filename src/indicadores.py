"""
Integración territorial: un panel por localidad con todas las fuentes.

Llave: código oficial de localidad (1-19 urbanas). Denominador: población SDP.
Las tasas de delitos e incidentes usan el corte enero-agosto que publica la SCJ
(comparable entre años; 2026 solo trae ese periodo).
"""
import numpy as np
import pandas as pd
from scipy import stats

from limpieza import HURTOS
from territorio import LOCALIDADES, URBANAS

ANIO = 2025  # último año completo en encuestas y en población


def pct_ponderado(df: pd.DataFrame, col: str, por: str = "localidad", peso: str = "peso") -> pd.DataFrame:
    """% ponderado con error estándar (n efectivo de Kish), por territorio y para Bogotá (localidad = 0)."""
    filas = []
    for loc, g in list(df.groupby(por)) + [(0, df)]:
        g = g.dropna(subset=[col, peso])
        w, y = g[peso], g[col]
        m = float(np.average(y, weights=w))
        n_ef = w.sum() ** 2 / (w ** 2).sum()
        filas.append({por: int(loc), "valor": m * 100, "ee": float(np.sqrt(m * (1 - m) / n_ef)) * 100, "n": len(g)})
    return pd.DataFrame(filas)


def tasas(eventos: pd.DataFrame, pob: pd.DataFrame, grupo: str = "total", por: float = 1e5) -> pd.DataFrame:
    p = pob[pob["grupo"] == grupo][["localidad", "anio", "personas"]]
    m = eventos.merge(p, on=["localidad", "anio"])
    m["tasa"] = m["casos"] / m["personas"] * por
    return m


def serie_bogota(d: pd.DataFrame) -> pd.DataFrame:
    """Casos de Bogotá por tipo y año (ene-ago) e índice 2018 = 100."""
    s = d.groupby(["codigo", "tipo", "anio"], as_index=False)["casos"].sum()
    base = s[s["anio"] == 2018].set_index("codigo")["casos"]
    s["indice_2018"] = s["casos"] / s["codigo"].map(base) * 100
    return s


def panel_localidad(delitos, incidentes, pob, ebcc, emv, alumbrado, ep, geo) -> pd.DataFrame:
    """Una fila por localidad urbana con percepción, entorno, delito registrado y contexto físico."""
    P = pd.DataFrame({"localidad": URBANAS})
    P["nombre"] = P["localidad"].map(LOCALIDADES)
    pob25 = pob[(pob["anio"] == ANIO) & (pob["grupo"] == "total")].set_index("localidad")["personas"]
    P["poblacion"] = P["localidad"].map(pob25)

    # percepción y entorno (Bienal 2025), total y por sexo
    for col in ["zona_insegura", "ciudad_insegura", "ciudad_peor_que_antes", "miedo_espacio_publico",
                "alumbrado_malo", "parque_spa", "parque_acoso", "presencio_acoso"]:
        t = pct_ponderado(ebcc, col).set_index("localidad")
        P[col] = P["localidad"].map(t["valor"])
        P[col + "_ee"] = P["localidad"].map(t["ee"])
        for s, v in (("mujeres", 1.0), ("hombres", 0.0)):
            ts = pct_ponderado(ebcc[ebcc["mujer"] == v], col).set_index("localidad")
            P[f"{col}_{s}"] = P["localidad"].map(ts["valor"])

    # victimización y autoprotección (EMV 2024)
    for col in ["victima", "barrio_inseguro", "no_sale_noche", "teme_acoso_sexual"]:
        t = pct_ponderado(emv, col).set_index("localidad")
        P["emv_" + col] = P["localidad"].map(t["valor"])
        P["emv_" + col + "_ee"] = P["localidad"].map(t["ee"])

    # delito registrado (SCJ, ene-ago 2025) por 100.000 habitantes
    d25 = tasas(delitos[delitos["anio"] == ANIO], pob)
    tot = d25[d25["codigo"] != "LP"].groupby("localidad")["tasa"].sum()
    P["delitos_alto_impacto_100k"] = P["localidad"].map(tot)
    P["hurtos_100k"] = P["localidad"].map(d25[d25["codigo"].isin(HURTOS)].groupby("localidad")["tasa"].sum())
    P["homicidios_100k"] = P["localidad"].map(d25[d25["codigo"] == "H"].set_index("localidad")["tasa"])
    muj = tasas(delitos[(delitos["anio"] == ANIO) & delitos["codigo"].isin(["VI", "DS"])], pob, "mujeres")
    P["vif_ds_100k_mujeres"] = P["localidad"].map(muj.groupby("localidad")["tasa"].sum())

    # incidentes reportados a la Línea 123 (desorden registrado)
    i25 = tasas(incidentes[incidentes["anio"] == ANIO], pob)
    for cod, nom in (("N", "narcoticos"), ("R", "rinas"), ("MM", "maltrato_mujer")):
        P[f"incidentes_{nom}_100k"] = P["localidad"].map(i25[i25["codigo"] == cod].set_index("localidad")["tasa"])

    # contexto físico
    g = geo.set_index("localidad")
    P["area_km2"] = P["localidad"].map(g["area_km2"])
    a = alumbrado.set_index("localidad")
    P["luminarias_km2_2019"] = P["localidad"].map(a["luminarias"]) / P["area_km2"]
    P["ep_efectivo_m2_hab"] = P["localidad"].map(ep.set_index("localidad")["ep_efectivo_m2_hab"])
    return P


def z(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std()


def indice_brecha(P: pd.DataFrame, ebcc: pd.DataFrame, n_boot: int = 1000, semilla: int = 11) -> pd.DataFrame:
    """
    Índice de Brecha de Seguridad (IBS) = z(% zona insegura) - z(log delitos de alto impacto por 100.000).
    Positivo: más miedo del que explica el delito registrado. Se usa log porque la tasa es muy asimétrica
    (el centro concentra delito de población flotante). Incertidumbre: bootstrap ponderado dentro de cada localidad.
    """
    delito = np.log(P.set_index("localidad")["delitos_alto_impacto_100k"])
    base = z(P.set_index("localidad")["zona_insegura"]) - z(delito)
    rng = np.random.default_rng(semilla)
    grupos = {l: g.dropna(subset=["zona_insegura"]) for l, g in ebcc.groupby("localidad")}
    sims = []
    for _ in range(n_boot):
        per = {}
        for l, g in grupos.items():
            i = rng.integers(0, len(g), len(g))
            gg = g.iloc[i]
            per[l] = np.average(gg["zona_insegura"], weights=gg["peso"]) * 100
        sims.append((z(pd.Series(per)) - z(delito)).rename(None))
    S = pd.DataFrame(sims)
    rangos = S.rank(axis=1, ascending=False)
    out = pd.DataFrame({"localidad": base.index, "ibs": base.values,
                        "ibs_p05": S.quantile(0.05).reindex(base.index).values,
                        "ibs_p95": S.quantile(0.95).reindex(base.index).values,
                        "puesto": base.rank(ascending=False).astype(int).values,
                        "puesto_p05": rangos.quantile(0.05).reindex(base.index).values,
                        "puesto_p95": rangos.quantile(0.95).reindex(base.index).values,
                        "prob_top5": (rangos <= 5).mean().reindex(base.index).values})
    return out.sort_values("ibs", ascending=False)


def cifra_oculta(P: pd.DataFrame, delitos: pd.DataFrame, pob: pd.DataFrame, anio: int = 2024) -> pd.DataFrame:
    """
    Orden de magnitud del subregistro: adultos que dicen haber sido víctimas (EMV, último año)
    frente a delitos de alto impacto registrados por la SCJ en el mismo año (ene-ago llevado a 12 meses).
    No son la misma unidad (personas frente a hechos): se reporta como razón indicativa.
    """
    adultos = pob[(pob["anio"] == anio) & (pob["grupo"] == "adultos")].set_index("localidad")["personas"]
    reg = delitos[delitos["anio"] == anio].groupby("localidad")["casos"].sum() * 12 / 8
    out = P[["localidad", "nombre", "emv_victima", "emv_victima_ee"]].copy()
    out["victimas_estimadas"] = out["emv_victima"] / 100 * out["localidad"].map(adultos)
    out["victimas_inf"] = (out["emv_victima"] - 1.96 * out["emv_victima_ee"]).clip(lower=0) / 100 * out["localidad"].map(adultos)
    out["victimas_sup"] = (out["emv_victima"] + 1.96 * out["emv_victima_ee"]) / 100 * out["localidad"].map(adultos)
    out["delitos_registrados"] = out["localidad"].map(reg)
    out["razon"] = out["victimas_estimadas"] / out["delitos_registrados"]
    out["razon_inf"] = out["victimas_inf"] / out["delitos_registrados"]
    out["razon_sup"] = out["victimas_sup"] / out["delitos_registrados"]
    return out


def spearman(x: pd.Series, y: pd.Series, n_boot: int = 2000, semilla: int = 5) -> dict:
    d = pd.concat([x, y], axis=1).dropna()
    rho, p = stats.spearmanr(d.iloc[:, 0], d.iloc[:, 1])
    rng = np.random.default_rng(semilla)
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(d), len(d))
        r = stats.spearmanr(d.iloc[i, 0], d.iloc[i, 1])[0]
        if np.isfinite(r):
            bs.append(r)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"rho": float(rho), "p": float(p), "ic_inf": float(lo), "ic_sup": float(hi), "n": int(len(d))}


def spearman_parcial(x: pd.Series, y: pd.Series, z: pd.Series, n_boot: int = 2000, semilla: int = 5) -> dict:
    """Spearman parcial de x e y controlando z: correlación de los residuos de los rangos (gl = n - 3).
    Sirve para ver si una relación entre dos índices sobrevive cuando se quita lo que ambos comparten."""
    d = pd.concat([x, y, z], axis=1).dropna()

    def calc(dd):
        r = dd.rank()
        ex = r.iloc[:, 0] - np.polyval(np.polyfit(r.iloc[:, 2], r.iloc[:, 0], 1), r.iloc[:, 2])
        ey = r.iloc[:, 1] - np.polyval(np.polyfit(r.iloc[:, 2], r.iloc[:, 1], 1), r.iloc[:, 2])
        return float(np.corrcoef(ex, ey)[0, 1])

    rho, n = calc(d), len(d)
    t = rho * np.sqrt((n - 3) / max(1e-12, 1 - rho ** 2))
    p = float(2 * stats.t.sf(abs(t), n - 3))
    rng = np.random.default_rng(semilla)
    bs = []
    for _ in range(n_boot):
        r = calc(d.iloc[rng.integers(0, n, n)])
        if np.isfinite(r):
            bs.append(r)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"rho": rho, "p": p, "ic_inf": float(lo), "ic_sup": float(hi), "n": int(n)}


def bh(pvalores) -> np.ndarray:
    """Benjamini-Hochberg: p-valores ajustados por pruebas múltiples."""
    p = np.asarray(pvalores, dtype=float)
    n = len(p)
    orden = np.argsort(p)
    aj = np.empty(n)
    acum = 1.0
    for i in range(n - 1, -1, -1):
        acum = min(acum, p[orden[i]] * n / (i + 1))
        aj[orden[i]] = acum
    return aj
