"""
Modelos: diagnóstico (logit ponderado con efectos marginales), robustez,
capacidad predictiva por bloques y simulación de escenarios.

Decisiones de método (y por qué):
- Logit ponderado con el factor de expansión de la encuesta: las estimaciones
  representan a la población adulta urbana, no a la muestra.
- Efectos marginales promedio (AME) en puntos porcentuales: se leen directo
  ("+X pp de probabilidad"), igual que el ejemplo que mostró la SDP.
- Intervalos por bootstrap de conglomerados (se remuestrean localidades):
  con solo 19 conglomerados los errores agrupados analíticos son optimistas.
- Validación cruzada para comparar qué bloque de variables predice mejor
  la percepción: el entorno o el delito registrado.
"""
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")


def _ajustar(df: pd.DataFrame, y: str, xs: list[str], peso: str = "peso"):
    """Ajusta un logit ponderado (GLM binomial con pesos de frecuencia normalizados)."""
    w = df[peso] / df[peso].mean()
    X = sm.add_constant(df[xs], has_constant="add")
    return sm.GLM(df[y], X, family=sm.families.Binomial(), freq_weights=w).fit(), X, w


def _ame(res, X: pd.DataFrame, w: pd.Series, xs: list[str]) -> dict:
    """Efecto marginal promedio de cada variable, en puntos porcentuales, a partir del modelo ajustado."""
    p = res.predict(X)
    out = {}
    for c in xs:
        vals = X[c].dropna().unique()
        if set(np.round(vals, 6)) <= {0.0, 1.0}:
            a, b = X.copy(), X.copy()
            a[c], b[c] = 1.0, 0.0
            out[c] = float(np.average(res.predict(a) - res.predict(b), weights=w)) * 100
        else:
            out[c] = float(np.average(p * (1 - p) * res.params[c], weights=w)) * 100
    return out


def logit_ame(df: pd.DataFrame, y: str, xs: list[str], cluster: str = "localidad", n_boot: int = 300,
              semilla: int = 16, peso: str = "peso") -> pd.DataFrame:
    """AME (pp) con IC 95 % por bootstrap de conglomerados y p-valor agrupado analítico."""
    d = df.dropna(subset=[y, peso] + xs).copy()
    res, X, w = _ajustar(d, y, xs, peso)
    ame = _ame(res, X, w, xs)
    robust = sm.GLM(d[y], X, family=sm.families.Binomial(), freq_weights=w).fit(
        cov_type="cluster", cov_kwds={"groups": d[cluster]})
    rng = np.random.default_rng(semilla)
    grupos = d[cluster].unique()
    idx = {g: d.index[d[cluster] == g] for g in grupos}
    boots = []
    for _ in range(n_boot):
        muestra = rng.choice(grupos, size=len(grupos), replace=True)
        b = d.loc[np.concatenate([idx[g] for g in muestra])]
        try:
            rb, Xb, wb = _ajustar(b.reset_index(drop=True), y, xs, peso)
            boots.append(_ame(rb, Xb, wb, xs))
        except Exception:
            continue
    B = pd.DataFrame(boots)
    filas = []
    for c in xs:
        lo, hi = np.percentile(B[c], [2.5, 97.5])
        filas.append({"variable": c, "ame_pp": ame[c], "ic_inf": lo, "ic_sup": hi,
                      "p": float(robust.pvalues[c]), "coef": float(res.params[c])})
    out = pd.DataFrame(filas)
    out.attrs.update(n=int(len(d)), y=y, media=float(np.average(d[y], weights=d[peso])), n_boot=len(B),
                     replicas={c: [float(v) for v in B[c]] for c in xs})  # listas: un DataFrame en attrs rompe pd.concat
    return out


def lpm_wild(df: pd.DataFrame, y: str, xs: list[str], cluster: str = "localidad", n_boot: int = 999,
             semilla: int = 7, peso: str = "peso", probar: list[str] | None = None) -> pd.DataFrame:
    """Modelo lineal de probabilidad ponderado con p-valor por wild cluster bootstrap (pesos de Webb)."""
    d = df.dropna(subset=[y, peso] + xs).copy()
    X = sm.add_constant(d[xs], has_constant="add")
    w = d[peso] / d[peso].mean()
    res = sm.WLS(d[y], X, weights=w).fit(cov_type="cluster", cov_kwds={"groups": d[cluster]})
    rng = np.random.default_rng(semilla)
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
    grupos = d[cluster].values
    unicos = np.unique(grupos)
    filas = []
    for c in (probar or xs):
        # bootstrap bajo la hipótesis nula (coeficiente c = 0)
        Xr = X.drop(columns=c)
        r0 = sm.WLS(d[y], Xr, weights=w).fit()
        ajuste, resid = r0.fittedvalues, r0.resid
        t_obs = res.tvalues[c]
        t_b = []
        for _ in range(n_boot):
            v = dict(zip(unicos, rng.choice(webb, size=len(unicos))))
            yb = ajuste + resid * np.vectorize(v.get)(grupos)
            rb = sm.WLS(yb, X, weights=w).fit(cov_type="cluster", cov_kwds={"groups": grupos})
            t_b.append(rb.tvalues[c])
        p_wild = float(np.mean(np.abs(t_b) >= abs(t_obs)))
        filas.append({"variable": c, "coef_pp": float(res.params[c]) * 100, "p_cluster": float(res.pvalues[c]),
                      "p_wild": p_wild})
    return pd.DataFrame(filas)


def auc_por_bloques(df: pd.DataFrame, y: str, bloques: dict[str, list[str]], peso: str = "peso",
                    k: int = 5, repeticiones: int = 5, semilla: int = 3) -> pd.DataFrame:
    """AUC fuera de muestra (validación cruzada estratificada repetida) para cada bloque de variables."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import RepeatedStratifiedKFold

    todas = sorted({v for vs in bloques.values() for v in vs})
    d = df.dropna(subset=[y, peso] + todas).reset_index(drop=True)
    cv = RepeatedStratifiedKFold(n_splits=k, n_repeats=repeticiones, random_state=semilla)
    filas = []
    for nombre, xs in bloques.items():
        aucs = []
        for tr, te in cv.split(d, d[y]):
            m = LogisticRegression(max_iter=2000)
            m.fit(d.loc[tr, xs], d.loc[tr, y], sample_weight=d.loc[tr, peso])
            aucs.append(roc_auc_score(d.loc[te, y], m.predict_proba(d.loc[te, xs])[:, 1], sample_weight=d.loc[te, peso]))
        filas.append({"bloque": nombre, "variables": ", ".join(xs), "auc": float(np.mean(aucs)),
                      "auc_sd": float(np.std(aucs)), "pliegues": len(aucs)})
    return pd.DataFrame(filas)


def escenarios(df: pd.DataFrame, y: str, xs: list[str], palancas: tuple[str, str], peso: str = "peso",
               por: str = "localidad") -> pd.DataFrame:
    """
    Probabilidad predicha media por territorio en 4 escenarios extremos:
    p00 = situación actual, p10 = palanca 1 resuelta para todos, p01 = palanca 2, p11 = ambas.
    Con fracciones f1, f2 de cobertura, el visor interpola: (1-f1)(1-f2)p00 + f1(1-f2)p10 + (1-f1)f2p01 + f1f2p11.
    Es un ejercicio de sensibilidad del modelo, no una predicción causal.
    """
    d = df.dropna(subset=[y, peso] + xs).copy()
    res, X, w = _ajustar(d, y, xs, peso)
    a, b = palancas
    casos = {"p00": {}, "p10": {a: 0.0}, "p01": {b: 0.0}, "p11": {a: 0.0, b: 0.0}}
    for k, cambio in casos.items():
        Xk = X.copy()
        for c, v in cambio.items():
            Xk[c] = v
        d[k] = res.predict(Xk) * 100
    filas = []
    for grupo, sub in [("total", d)] + [(s, d[d["mujer"] == v]) for s, v in (("mujeres", 1.0), ("hombres", 0.0))]:
        for loc, g in list(sub.groupby(por)) + [(0, sub)]:
            fila = {"grupo": grupo, por: int(loc)}
            for k in casos:
                fila[k] = float(np.average(g[k], weights=g[peso]))
            fila["observado"] = float(np.average(g[y], weights=g[peso])) * 100
            filas.append(fila)
    return pd.DataFrame(filas)
