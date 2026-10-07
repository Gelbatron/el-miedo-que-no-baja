"""
Aprendizaje supervisado: ¿qué información predice que una persona sienta insegura su zona?

Complementa al logit ponderado (modelos.py), que da efectos interpretables en puntos porcentuales,
con modelos flexibles que capturan no linealidades e interacciones sin especificarlas a mano.
Si los modelos flexibles llegan a la misma conclusión, el resultado no depende de la forma funcional.

Diseño:
- Datos: Bienal de Cultura Ciudadana 2025 (5.538 adultos de las 19 localidades urbanas), con el
  delito registrado de su localidad (SCJ) y la confianza en la Policía (P28.5).
- Modelos: regresión logística (L2, variables estandarizadas), bosque aleatorio y gradient boosting
  por histogramas. Todos se entrenan con el factor de expansión como peso.
- Validación: 5 particiones estratificadas × 5 repeticiones (25 evaluaciones fuera de muestra);
  AUC ponderada por el factor de expansión.
- Importancia por BLOQUES: se permutan juntas todas las variables de un bloque en los datos de
  prueba y se mide cuánta AUC se pierde. Responde «¿cuánto acierto se pierde sin esta información?»,
  más fácil de leer y más estable que la importancia variable por variable.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]

BLOQUES = {
    "Perfil (sexo, edad, estrato, arriendo)": ["mujer", "edad", "estrato", "arrienda"],
    "Delito registrado en su localidad": ["hurtos_100k_miles", "homicidios_100k", "narcoticos_100k_cientos"],
    "Hechos en su entorno": ["parque_atracos", "parque_spa", "parque_acoso", "parque_rinas", "sin_parque",
                             "presencio_acoso", "conflictos_vecinos"],
    "Condiciones del barrio": ["alumbrado_malo", "conexion_peatonal_mala", "zonas_verdes_malas", "aire_malo", "ruido_malo",
                               "ventas_informales_malo"],
    "Confianza en la Policía": ["desconfia_policia"],
}
ETIQUETAS = {
    "mujer": "Ser mujer", "edad": "Edad", "estrato": "Estrato", "arrienda": "Vive en arriendo",
    "hurtos_100k_miles": "Hurtos registrados en la localidad", "homicidios_100k": "Homicidios en la localidad",
    "narcoticos_100k_cientos": "Llamadas 123 por narcóticos", "parque_atracos": "Atracos en el parque cercano",
    "parque_spa": "Venta o consumo de drogas en el parque", "parque_acoso": "Acoso en el parque", "parque_rinas": "Riñas en el parque",
    "sin_parque": "No tiene parque cerca", "presencio_acoso": "Presenció acoso a mujeres", "conflictos_vecinos": "Conflictos entre vecinos",
    "alumbrado_malo": "Alumbrado malo", "conexion_peatonal_mala": "Andenes y conexión peatonal malos", "zonas_verdes_malas": "Zonas verdes malas",
    "aire_malo": "Calidad del aire mala", "ruido_malo": "Ruido", "ventas_informales_malo": "Ventas informales",
    "desconfia_policia": "No confía en la Policía (nada o poco)",
}


def datos() -> pd.DataFrame:
    eb = pd.read_csv(RAIZ / "data" / "procesados" / "ebcc_2025_analitica.csv")
    crudo = pd.read_excel(RAIZ / "data" / "crudos" / "ebcc_2025_cultura_ciudadana.xlsx", sheet_name="datos",
                          usecols=["encuestado_id", "P28.5"])
    crudo["desconfia_policia"] = crudo["P28.5"].map({1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0})
    eb = eb.merge(crudo[["encuestado_id", "desconfia_policia"]].rename(columns={"encuestado_id": "id"}), on="id", how="left")
    return eb.dropna(subset=["zona_insegura", "peso"]).reset_index(drop=True)


def modelos() -> dict:
    return {
        "Regresión logística": lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)),
        "Bosque aleatorio": lambda: make_pipeline(SimpleImputer(strategy="median"),
                                                  RandomForestClassifier(n_estimators=400, min_samples_leaf=20, n_jobs=-1, random_state=16)),
        "Gradient boosting": lambda: HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                                                    min_samples_leaf=40, l2_regularization=1.0, random_state=16),
    }


def _ajustar(modelo, X, y, w):
    paso = modelo.steps[-1][0] if hasattr(modelo, "steps") else None
    if paso:
        return modelo.fit(X, y, **{f"{paso}__sample_weight": w})
    return modelo.fit(X, y, sample_weight=w)


def comparar(eb: pd.DataFrame, columnas: list, repeticiones: int = 5, semilla: int = 16) -> tuple[pd.DataFrame, pd.DataFrame]:
    """AUC fuera de muestra de cada modelo y pérdida de AUC al permutar cada bloque (en el mejor modelo flexible)."""
    X, y, w = eb[columnas], eb["zona_insegura"].astype(int).values, (eb["peso"] / eb["peso"].mean()).values
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=repeticiones, random_state=semilla)
    rng = np.random.default_rng(semilla)
    aucs, perdidas = [], []
    for k, (tr, te) in enumerate(cv.split(X, y)):
        for nombre, fabrica in modelos().items():
            m = _ajustar(fabrica(), X.iloc[tr], y[tr], w[tr])
            p = m.predict_proba(X.iloc[te])[:, 1]
            base = roc_auc_score(y[te], p, sample_weight=w[te])
            aucs.append({"modelo": nombre, "particion": k, "auc": base})
            if nombre != "Gradient boosting":
                continue
            for bloque, cols in BLOQUES.items():
                cols = [c for c in cols if c in columnas]
                Xp = X.iloc[te].copy()
                orden = rng.permutation(len(Xp))
                Xp[cols] = Xp[cols].values[orden]  # se permuta el bloque completo, conservando su estructura interna
                pp = m.predict_proba(Xp)[:, 1]
                perdidas.append({"bloque": bloque, "particion": k, "perdida_auc": base - roc_auc_score(y[te], pp, sample_weight=w[te])})
    A = pd.DataFrame(aucs).groupby("modelo")["auc"].agg(["mean", "std", "count"]).reset_index()
    B = pd.DataFrame(perdidas).groupby("bloque")["perdida_auc"].agg(["mean", "std"]).reset_index().sort_values("mean", ascending=False)
    return A, B


def importancia_variables(eb: pd.DataFrame, columnas: list, semilla: int = 16) -> pd.DataFrame:
    """Importancia por permutación de cada variable en el gradient boosting (5 particiones, datos de prueba)."""
    from sklearn.model_selection import StratifiedKFold
    X, y, w = eb[columnas], eb["zona_insegura"].astype(int).values, (eb["peso"] / eb["peso"].mean()).values
    rng = np.random.default_rng(semilla)
    filas = []
    for tr, te in StratifiedKFold(n_splits=5, shuffle=True, random_state=semilla).split(X, y):
        m = _ajustar(modelos()["Gradient boosting"](), X.iloc[tr], y[tr], w[tr])
        base = roc_auc_score(y[te], m.predict_proba(X.iloc[te])[:, 1], sample_weight=w[te])
        for c in columnas:
            for _ in range(5):
                Xp = X.iloc[te].copy()
                Xp[c] = Xp[c].values[rng.permutation(len(Xp))]
                filas.append({"variable": c, "perdida_auc": base - roc_auc_score(y[te], m.predict_proba(Xp)[:, 1], sample_weight=w[te])})
    I = pd.DataFrame(filas).groupby("variable")["perdida_auc"].agg(["mean", "std"]).reset_index()
    I["etiqueta"] = I["variable"].map(ETIQUETAS)
    I["bloque"] = I["variable"].map({c: b for b, cs in BLOQUES.items() for c in cs})
    return I.sort_values("mean", ascending=False)


def correr() -> dict:
    eb = datos()
    columnas = [c for cs in BLOQUES.values() for c in cs]
    A, B = comparar(eb, columnas)
    I = importancia_variables(eb, columnas)
    sal = RAIZ / "outputs" / "tablas"
    A.to_csv(sal / "ml_comparacion_modelos.csv", index=False)
    B.to_csv(sal / "ml_importancia_bloques.csv", index=False)
    I.to_csv(sal / "ml_importancia_variables.csv", index=False)
    m = eb["desconfia_policia"].notna()
    pd.DataFrame([{"indicador": "desconfia_policia_pct", "valor": float(np.average(eb.loc[m, "desconfia_policia"], weights=eb.loc[m, "peso"]) * 100),
                   "n": int(m.sum())}]).to_csv(sal / "confianza_policia_bogota.csv", index=False)
    return {"modelos": A, "bloques": B, "variables": I, "n": len(eb), "desconfia_policia": float(np.average(eb["desconfia_policia"].fillna(0), weights=eb["peso"]))}


if __name__ == "__main__":
    r = correr()
    print("n =", r["n"], "· desconfía de la Policía (ponderado):", round(r["desconfia_policia"] * 100, 1), "%")
    print(r["modelos"].round(4).to_string(index=False))
    print(r["bloques"].round(4).to_string(index=False))
    print(r["variables"][["etiqueta", "bloque", "mean", "std"]].round(4).to_string(index=False))
