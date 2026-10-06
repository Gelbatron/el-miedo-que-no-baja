"""
Tabla derivada: cifras de Bogotá que NO se pueden calcular desde los CSV por localidad.

Los porcentajes de Bogotá de la Bienal 2025 y los efectos marginales de ser mujer (EMV 2024)
salen de los microdatos con su factor de expansión; un promedio de las 19 localidades no los
reproduce (ni simple ni ponderado por población). Por eso se copian tal cual de las salidas
oficiales del pipeline del proyecto (src/pipeline.py):

  - outputs/resultados.json
  - outputs/tablas/cifra_oculta.csv  (víctimas estimadas y delitos registrados por localidad)

No se inventa ningún número: cada fila trae la ruta y la clave de donde sale.
Uso:  python powerbi/_build/derivar_bogota.py
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "powerbi" / "datos" / "dim_bogota.csv"

r = json.loads((RAIZ / "outputs" / "resultados.json").read_text(encoding="utf-8"))
co = pd.read_csv(RAIZ / "outputs" / "tablas" / "cifra_oculta.csv", encoding="utf-8-sig")

BIENAL = "Encuesta Bienal de Cultura Ciudadana 2025, microdatos con factor de expansión"
EMV = "Encuesta Mundial de Valores ola 8 (2024), logit ponderado: efecto de ser mujer a igual edad, estrato y victimización"

filas = [
    ("ciudad_insegura_pct", "Califica la ciudad como insegura", r["ciudad_insegura_pct"], "%", BIENAL, "resultados.json:ciudad_insegura_pct"),
    ("zona_insegura_pct", "Califica insegura su propia zona", r["zona_insegura_pct"], "%", BIENAL, "resultados.json:zona_insegura_pct"),
    ("ciudad_peor_que_antes_pct", "Cree que la ciudad está peor que antes", r["ciudad_peor_que_antes_pct"], "%", BIENAL, "resultados.json:ciudad_peor_que_antes_pct"),
    ("miedo_espacio_publico_pct", "Siente miedo en el espacio público", r["miedo_espacio_publico_pct"], "%", BIENAL, "resultados.json:miedo_espacio_publico_pct"),
    ("cifra_oculta_bogota", "Víctimas estimadas por cada delito registrado",
     co["victimas_estimadas"].sum() / co["delitos_registrados"].sum(), "veces",
     "EMV 2024 (víctimas) / SCJ 2024 (delitos de alto impacto registrados)", "cifra_oculta.csv: suma víctimas / suma delitos"),
    ("rho_ibs_cifra_oculta", "Correlación de Spearman entre el Índice de Brecha y la cifra oculta",
     r["ibs_vs_cifra_oculta"]["rho"], "rho", "Panel por localidad (19 localidades)", "resultados.json:ibs_vs_cifra_oculta.rho"),
    ("n_bienal", "Encuestas de la Bienal 2025 usadas", r["n_bienal"], "personas", BIENAL, "resultados.json:n_bienal"),
    ("n_emv_bogota", "Encuestas de la EMV 2024 en Bogotá", r["n_emv_bogota"], "personas", EMV, "resultados.json:n_emv_bogota"),
]
for k, et in (("teme_acoso_sexual", "Ser mujer: temor al acoso sexual"),
              ("no_sale_noche", "Ser mujer: evita salir de noche"),
              ("barrio_inseguro", "Ser mujer: se siente insegura en su barrio")):
    a = r["emv_mujer_ame"][k]
    filas.append((f"ame_mujer_{k}", et, a["ame_pp"], "pp", EMV, f"resultados.json:emv_mujer_ame.{k}.ame_pp"))
    filas.append((f"ame_mujer_{k}_ic_inf", et + " (IC 95 % inferior)", a["ic_inf"], "pp", EMV, f"resultados.json:emv_mujer_ame.{k}.ic_inf"))
    filas.append((f"ame_mujer_{k}_ic_sup", et + " (IC 95 % superior)", a["ic_sup"], "pp", EMV, f"resultados.json:emv_mujer_ame.{k}.ic_sup"))

df = pd.DataFrame(filas, columns=["indicador", "descripcion", "valor", "unidad", "fuente", "origen"])
df.to_csv(SALIDA, index=False, encoding="utf-8-sig")
print(df[["indicador", "valor", "unidad"]].to_string(index=False))
print(f"-> {SALIDA}")
