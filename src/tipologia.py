"""
Aprendizaje no supervisado: tipología de las 19 localidades según los cuatro frentes de la seguridad.

Pregunta: ¿qué localidades se parecen entre sí cuando la seguridad se mide en todos sus frentes a la vez
(lo que se registra, lo que se vive, lo que se siente y las condiciones del entorno)? Una localidad puede
parecer segura en un frente e insegura en otro; los perfiles muestran esas combinaciones.

Método:
- Indicadores estandarizados (z) por localidad. Las tasas muy asimétricas van en logaritmo.
- Análisis de componentes principales (PCA) para ver las dimensiones que ordenan a las localidades.
- Agrupamiento jerárquico de Ward sobre los indicadores estandarizados; k se elige con el
  coeficiente de silueta (entre 3 y 5 perfiles, para que sean interpretables con 19 localidades).
- Estabilidad: el agrupamiento se repite 500 veces quitando un indicador al azar y remuestreando
  localidades; se reporta con qué frecuencia cada par de localidades queda junto (consenso).
  Con 19 localidades los perfiles son descriptivos, no inferenciales, y así se presentan.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from territorio import LOCALIDADES  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data" / "procesados"

# frente → (columna, etiqueta, logaritmo)
INDICADORES = {
    "Lo que se registra": [("delitos_alto_impacto_100k", "Delitos de alto impacto por 100.000", True),
                           ("homicidios_100k", "Homicidios por 100.000", True)],
    "Lo que se vive": [("emv_victima", "% víctima de un delito (EMV)", False),
                       ("vif_ds_100k_mujeres", "Violencia intrafamiliar y sexual por 100.000 mujeres", True)],
    "Lo que se siente": [("zona_insegura", "% siente insegura su zona", False),
                         ("miedo_espacio_publico", "% con miedo en el espacio público", False)],
    "Las condiciones": [("luminarias_km2_2019", "Luminarias por km² (UAESP 2019)", True),
                        ("ep_efectivo_m2_hab", "Espacio público efectivo por habitante (DADEP)", True)],
}
# La auditoría nocturna de la Secretaría de la Mujer (2019) queda fuera: 86 % de sus puntos salen con
# iluminación «brillante» (efecto techo) y el orden de localidades no se sostiene frente a 2016.
# La siniestralidad vial tampoco entra: se registra donde ocurre (actividad y tránsito), no donde vive la gente;
# se prueba aparte en src/fuentes_movilidad.py.
EXTERNOS: list[tuple] = []  # (archivo, columna, etiqueta, log, frente) — se usan solo si el archivo existe


def tabla() -> tuple[pd.DataFrame, dict]:
    """Arma la tabla de indicadores por localidad para la tipología, con sus etiquetas."""
    P = pd.read_csv(PROC / "panel_localidad_2025.csv").set_index("localidad")
    etiquetas, cols = {}, []
    for frente, inds in INDICADORES.items():
        for c, e, lg in inds:
            cols.append(c)
            etiquetas[c] = (e, frente, lg)
    T = P[cols].copy()
    for archivo, c, e, lg, frente in EXTERNOS:
        ruta = PROC / archivo
        if not ruta.exists():
            continue
        X = pd.read_csv(ruta)
        if "anio" in X.columns:  # último año con dato completo para todas las localidades
            X = X[X["anio"] == X.groupby("anio")["localidad"].transform("nunique").pipe(lambda s: X.loc[s == s.max(), "anio"].max())]
        if c not in X.columns or "localidad" not in X.columns:
            continue
        T[c] = X.groupby("localidad")[c].mean()
        etiquetas[c] = (e, frente, lg)
    return T.loc[[l for l in T.index if l in LOCALIDADES and l != 20]], etiquetas


def estandarizar(T: pd.DataFrame, etiquetas: dict) -> pd.DataFrame:
    """Estandariza los indicadores e invierte los que van en sentido contrario."""
    Z = T.copy()
    for c in Z.columns:
        if etiquetas[c][2]:
            Z[c] = np.log(Z[c].clip(lower=1e-6))
    Z = Z.fillna(Z.median())
    return (Z - Z.mean()) / Z.std(ddof=0)


def agrupar(Z: pd.DataFrame, k_rango=range(3, 6)) -> tuple[int, pd.Series, dict]:
    """Agrupa las localidades con Ward y elige el número de grupos por silueta."""
    L = linkage(Z.values, method="ward")
    sil = {k: silhouette_score(Z.values, fcluster(L, k, "maxclust")) for k in k_rango}
    k = max(sil, key=sil.get)
    return k, pd.Series(fcluster(L, k, "maxclust"), index=Z.index, name="perfil"), sil


def nombrar(m: pd.Series) -> str:
    """Nombre de un perfil a partir de su centroide estandarizado (reglas fijas, no a mano)."""
    g = m.get
    if g("zona_insegura", 0) < -1:
        return "Se sienten seguras"
    if g("delitos_alto_impacto_100k", 0) > 1 and g("homicidios_100k", 0) > 1:
        return "Todo alto: registro, violencia y miedo"
    if g("zona_insegura", 0) > 0.8 and g("luminarias_km2_2019", 0) < -1:
        return "Miedo alto, poca luz, más homicidios"
    if g("emv_victima", 0) > 0.3 and g("delitos_alto_impacto_100k", 0) < -0.5:
        return "Más víctimas que denuncias"
    if g("delitos_alto_impacto_100k", 0) > 0.5:
        return "Mucho registro, miedo promedio"
    return "Perfil intermedio"


def estabilidad(Z: pd.DataFrame, k: int, n: int = 500, semilla: int = 7) -> pd.DataFrame:
    """Frecuencia con que cada par de localidades queda en el mismo grupo al perturbar indicadores y localidades."""
    rng = np.random.default_rng(semilla)
    idx = list(Z.index)
    juntos = pd.DataFrame(0.0, index=idx, columns=idx)
    veces = pd.DataFrame(0.0, index=idx, columns=idx)
    for _ in range(n):
        cols = [c for c in Z.columns if c != rng.choice(Z.columns)]
        filas = sorted(set(rng.choice(idx, size=len(idx), replace=True)))
        Zs = Z.loc[filas, cols]
        g = pd.Series(fcluster(linkage(Zs.values, "ward"), k, "maxclust"), index=filas)
        for a in filas:
            for b in filas:
                veces.loc[a, b] += 1
                juntos.loc[a, b] += g[a] == g[b]
    return juntos / veces.replace(0, np.nan)


def correr() -> dict:
    """Ejecuta la tipología: componentes principales, agrupamiento y estabilidad por localidad."""
    T, etiquetas = tabla()
    Z = estandarizar(T, etiquetas)
    pca = PCA(n_components=min(3, Z.shape[1]))
    comp = pd.DataFrame(pca.fit_transform(Z.values), index=Z.index, columns=[f"CP{i + 1}" for i in range(pca.n_components_)])
    cargas = pd.DataFrame(pca.components_.T, index=Z.columns, columns=comp.columns)
    k, perfil, sil = agrupar(Z)
    cons = estabilidad(Z, k)
    estab = {l: float(cons.loc[l, perfil[perfil == perfil[l]].index].drop(l).mean()) if (perfil == perfil[l]).sum() > 1 else 1.0 for l in Z.index}
    medias = Z.groupby(perfil).mean()
    medias["perfil_nombre"] = [nombrar(medias.loc[i]) for i in medias.index]
    out = T.join(comp).join(perfil)
    out["perfil_nombre"] = out["perfil"].map(medias["perfil_nombre"])
    out["nombre"] = [LOCALIDADES[l] for l in out.index]
    out["estabilidad"] = pd.Series(estab)
    sal = RAIZ / "outputs" / "tablas"
    out.to_csv(sal / "tipologia_localidades.csv")
    medias.to_csv(sal / "tipologia_perfiles_z.csv")
    cargas.to_csv(sal / "tipologia_pca_cargas.csv")
    pd.Series(sil, name="silueta").to_csv(sal / "tipologia_silueta.csv")
    return {"tabla": out, "medias": medias, "cargas": cargas, "varianza": pca.explained_variance_ratio_, "k": k, "silueta": sil, "etiquetas": etiquetas}


if __name__ == "__main__":
    r = correr()
    print("indicadores:", list(r["etiquetas"]))
    print("k =", r["k"], "silueta:", {k: round(v, 3) for k, v in r["silueta"].items()})
    print("varianza PCA:", np.round(r["varianza"], 3))
    print(r["cargas"].round(2).to_string())
    print(r["medias"].round(2).to_string())
    print(r["tabla"][["nombre", "perfil", "perfil_nombre", "estabilidad", "CP1", "CP2"]].sort_values("perfil").round(2).to_string())
