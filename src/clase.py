"""
Datos para la presentación interactiva del visor (visor/data/clase.json).

Todo sale de los mismos modelos del pipeline, sin cifras nuevas:
- componentes del Índice de Brecha (z de percepción y z de registro por localidad);
- coeficientes del logit principal, para la calculadora «dos vecinos iguales»;
- las 300 réplicas del bootstrap de localidades del efecto de los atracos en el parque y del hurto
  registrado (misma semilla que modelos.logit_ame, así que sus percentiles 2,5 y 97,5 son el IC publicado).

Uso:  python src/clase.py   (o desde pipeline.figuras_y_exportes)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import indicadores as I  # noqa: E402
import modelos as M  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "visor" / "data" / "clase.json"


def _wmedia(s, w):
    return float(np.average(s, weights=w))


def _wmoda(s, w):
    return float(pd.Series(w.values, index=s.values).groupby(level=0).sum().idxmax())


def construir(P: pd.DataFrame, eb: pd.DataFrame, perfil: list, delito: list, hechos: list, n_boot: int = 300,
              replicas: dict | None = None) -> dict:
    """replicas: las del modelo principal (attrs de logit_ame) para no volver a estimarlas."""
    loc = P.set_index("localidad")

    # 1. Índice de Brecha por partes
    zp = I.z(loc["zona_insegura"])
    zr = I.z(np.log(loc["delitos_alto_impacto_100k"]))
    indice = [{"localidad": int(l), "nombre": loc.at[l, "nombre"], "zona_insegura": float(loc.at[l, "zona_insegura"]),
               "delitos_100k": float(loc.at[l, "delitos_alto_impacto_100k"]), "z_percepcion": float(zp[l]),
               "z_registro": float(zr[l]), "ibs": float(zp[l] - zr[l])} for l in loc.index]

    # 2. Logit principal (zona insegura ~ perfil + delito registrado + hechos del entorno)
    xs = perfil + delito + hechos
    y = "zona_insegura"
    d = eb.dropna(subset=[y, "peso"] + xs).copy()
    res, X, w = M._ajustar(d, y, xs)
    referencia = {
        "mujer": 1.0,
        "edad": float(np.round(_wmedia(d["edad"], w))),
        "estrato": _wmoda(d["estrato"], w),
        "arrienda": _wmoda(d["arrienda"], w),
        **{c: _wmedia(d[c], w) for c in delito},
        **{c: 0.0 for c in hechos},
    }
    rangos = {c: [float(d[c].min()), float(d[c].max())] for c in delito}  # entre localidades

    # 3. Réplicas del bootstrap de localidades (idéntico a modelos.logit_ame)
    claves = ["parque_atracos", "hurtos_100k_miles"]
    if replicas is not None:
        return {"indice": sorted(indice, key=lambda f: -f["ibs"]),
                "logit": {"y": y, "n": int(len(d)), "coef": {k: float(v) for k, v in res.params.items()},
                          "referencia": referencia, "rangos_localidad": rangos},
                "bootstrap": {k: [round(float(v), 3) for v in replicas[k]] for k in claves}}
    rng = np.random.default_rng(16)
    grupos = d["localidad"].unique()
    idx = {g: d.index[d["localidad"] == g] for g in grupos}
    replicas = {"parque_atracos": [], "hurtos_100k_miles": []}
    for _ in range(n_boot):
        muestra = rng.choice(grupos, size=len(grupos), replace=True)
        b = d.loc[np.concatenate([idx[g] for g in muestra])]
        try:
            rb, Xb, wb = M._ajustar(b.reset_index(drop=True), y, xs)
            a = M._ame(rb, Xb, wb, xs)
        except Exception:
            continue
        for k in replicas:
            replicas[k].append(round(a[k], 3))

    return {
        "indice": sorted(indice, key=lambda f: -f["ibs"]),
        "logit": {"y": y, "n": int(len(d)), "coef": {k: float(v) for k, v in res.params.items()},
                  "referencia": referencia, "rangos_localidad": rangos},
        "bootstrap": {k: v for k, v in replicas.items()},
    }


def guardar(datos: dict) -> Path:
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return SALIDA


if __name__ == "__main__":
    import pipeline as PL

    t = PL.cargar()
    P, eb, _ = PL.integrar(t)
    datos = construir(P, eb, PL.PERFIL, PL.DELITO, PL.HECHOS)
    ruta = guardar(datos)
    m = pd.read_csv(RAIZ / "outputs" / "tablas" / "m_hechos.csv").set_index("variable")
    for k, v in datos["bootstrap"].items():
        lo, hi = np.percentile(v, [2.5, 97.5])
        print(f"{k}: {len(v)} réplicas · IC {lo:.2f} a {hi:.2f} · publicado {m.at[k, 'ic_inf']:.2f} a {m.at[k, 'ic_sup']:.2f}")
    ibs = pd.read_csv(RAIZ / "outputs" / "tablas" / "ibs.csv").set_index("localidad")["ibs"]
    print("IBS igual al publicado:", all(abs(f["ibs"] - ibs[f["localidad"]]) < 1e-9 for f in datos["indice"]))
    print(ruta, round(ruta.stat().st_size / 1e3), "KB")
