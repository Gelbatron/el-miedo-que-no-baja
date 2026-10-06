"""
Genera el proyecto Power BI (PBIP: modelo TMDL + informe PBIR) de «El miedo que no baja».

    python powerbi/_build/generar_pbip.py

Reescribe por completo:
  ElMiedoQueNoBaja.pbip
  ElMiedoQueNoBaja.SemanticModel/   (definition.pbism + definition/*.tmdl)
  ElMiedoQueNoBaja.Report/          (definition.pbir + definition/ + tema propio)
No toca powerbi/datos/ ni el tema base de Desktop (StaticResources/SharedResources).
Los cambios hechos a mano en Power BI Desktop se pierden si se vuelve a correr.

Versiones de formato: las que trae Power BI Desktop 2.158 (report 3.3.0, page 2.1.0,
visualContainer 2.13.0); los JSON se validan contra esos esquemas antes de abrir en Desktop.
"""
import json
import shutil
import uuid
from pathlib import Path

import pandas as pd

PB = Path(__file__).resolve().parents[1]
DATOS = PB / "datos"
NOMBRE = "ElMiedoQueNoBaja"
SM = PB / f"{NOMBRE}.SemanticModel"
RP = PB / f"{NOMBRE}.Report"
RUTA_DATOS = str(DATOS) + "\\"

# Identidad visual (la misma del visor y de las figuras del notebook)
AMBAR, AZUL, VIOLETA, VERDE, GRIS = "#D98A0B", "#2F63D6", "#8E44C8", "#2A9D4B", "#B9C0CD"
TINTA, TINTA2, LINEA, BLANCO, FONDO = "#0F1729", "#475069", "#E3E7EE", "#FFFFFF", "#F4F6F9"
FUENTE, FUENTE_FUERTE = "Segoe UI", "Segoe UI Semibold"

SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/"
V_REPORT, V_PAGE, V_VISUAL = "3.3.0", "2.1.0", "2.13.0"
BASE_THEME = "CY26SU09"
TEMA = f"{NOMBRE}.json"


def uid(*partes: str) -> str:
    """GUID determinista: regenerar no cambia los lineageTag ni los logicalId."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "el-miedo-que-no-baja/" + "/".join(partes)))


def hexid(*partes: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, "emqnb-visual/" + "/".join(partes)).hex[:20]


def escribir(ruta: Path, texto: str):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8", newline="\n")


def escribir_json(ruta: Path, obj):
    escribir(ruta, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


# ---------------------------------------------------------------------------
# 1. MODELO SEMÁNTICO (TMDL)
# ---------------------------------------------------------------------------

def q(nombre: str) -> str:
    """Nombre TMDL: comillas simples salvo identificadores ASCII simples."""
    if nombre.replace("_", "a").isascii() and nombre.replace("_", "a").isalnum() and not nombre[0].isdigit():
        return nombre
    return "'" + nombre.replace("'", "''") + "'"


FORMATOS = {  # formato por columna (cultura del modelo es-CO: coma decimal, punto de miles)
    "localidad": "0", "poblacion": "#,0", "puesto": "0", "anio": "0", "casos": "#,0", "pliegues": "0",
    "prob_top5": "0 %", "ibs": "0.00", "ibs_p05": "0.00", "ibs_p95": "0.00", "cifra_oculta": "0.0",
    "auc": "0.000", "auc_sd": "0.000", "p": "0.0000", "coef": "0.000", "area_km2": "#,0.0",
    "luminarias_km2_2019": "#,0.0", "ep_efectivo_m2_hab": "0.0", "orden": "0",
}
DESCRIPCIONES = {
    ("Localidades", "ibs"): "Índice de Brecha de Seguridad = z(% zona insegura) - z(log delitos de alto impacto por 100 mil). Positivo: más miedo del que explica el delito registrado.",
    ("Localidades", "cifra_oculta"): "Víctimas estimadas (EMV 2024) por cada delito de alto impacto registrado (SCJ 2024).",
    ("Localidades", "prob_top5"): "Proporción de réplicas bootstrap en que la localidad queda entre las 5 de mayor Índice de Brecha.",
    ("Localidades", "zona_insegura"): "% que califica insegura su zona (Bienal 2025, ponderado). Escala 0-100.",
    ("Localidades", "delitos_alto_impacto_100k"): "Delitos de alto impacto registrados por 100.000 habitantes (SCJ, ene-ago 2025, sin lesiones personales).",
}


def tipos_csv(archivo: str):
    df = pd.read_csv(DATOS / archivo, encoding="utf-8-sig")
    cols = []
    for c, t in df.dtypes.items():
        if pd.api.types.is_integer_dtype(t):
            cols.append((c, "int64", "Int64.Type"))
        elif pd.api.types.is_float_dtype(t):
            cols.append((c, "double", "type number"))
        else:
            cols.append((c, "string", "type text"))
    return df, cols


def m_csv(archivo: str, cols, pasos_extra: str = "", ultimo: str = "Tipos") -> str:
    lista = ", ".join(f'{{"{c}", {mt}}}' for c, _, mt in cols)
    return f"""let
    Carpeta = if Text.EndsWith(RutaDatos, "\\") then RutaDatos else RutaDatos & "\\",
    Origen = Csv.Document(File.Contents(Carpeta & "{archivo}"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados, {{{lista}}}, "en-US"){pasos_extra}
in
    {ultimo}"""


def tabla_csv(nombre, archivo, pasos_extra="", ultimo="Tipos", extra_cols=(), ocultas=(), sort_by=None):
    _, cols = tipos_csv(archivo)
    columnas = [{"name": c, "dataType": dt} for c, dt, _ in cols]
    columnas += [{"name": c, "dataType": dt} for c, dt in extra_cols]
    for col in columnas:
        col["fmt"] = FORMATOS.get(col["name"]) or ("0.0" if col["dataType"] == "double" else ("0" if col["dataType"] == "int64" else None))
        col["hidden"] = col["name"] in ocultas
        col["desc"] = DESCRIPCIONES.get((nombre, col["name"]))
        if sort_by and col["name"] in sort_by:
            col["sortBy"] = sort_by[col["name"]]
    return {"name": nombre, "columns": columnas, "m": m_csv(archivo, cols, pasos_extra, ultimo), "measures": []}


TABLAS = [
    tabla_csv("Localidades", "dim_localidad_indicadores.csv"),
    tabla_csv("Delitos", "fact_delitos_serie.csv"),
    tabla_csv("Efectos marginales", "fact_efectos_marginales.csv"),
    tabla_csv(
        "AUC por bloque", "fact_auc_bloques.csv",
        pasos_extra=',\n    ConOrden = Table.AddIndexColumn(Tipos, "orden", 1, 1, Int64.Type)',
        ultimo="ConOrden", extra_cols=[("orden", "int64")], ocultas={"orden"}, sort_by={"bloque": "orden"},
    ),
    tabla_csv(
        "Género", "fact_genero_emv.csv",
        pasos_extra=(
            ',\n    Etiquetas = [teme_acoso_sexual = "Teme el acoso sexual", no_sale_noche = "Evita salir de noche", '
            'barrio_inseguro = "Se siente insegura/o en su barrio", victima = "Fue víctima de un delito"],'
            '\n    Orden = [teme_acoso_sexual = 1, no_sale_noche = 2, barrio_inseguro = 3, victima = 4],'
            '\n    ConEtiqueta = Table.AddColumn(Tipos, "etiqueta", each Record.FieldOrDefault(Etiquetas, [indicador], [indicador]), type text),'
            '\n    ConOrden = Table.AddColumn(ConEtiqueta, "orden", each Record.FieldOrDefault(Orden, [indicador], 99), Int64.Type)'
        ),
        ultimo="ConOrden", extra_cols=[("etiqueta", "string"), ("orden", "int64")], ocultas={"orden"},
        sort_by={"etiqueta": "orden"},
    ),
    tabla_csv("Bogotá", "dim_bogota.csv"),
]

# --- Medidas -----------------------------------------------------------------
LOC = "IF(HASONEVALUE(Localidades[localidad]), {})"  # valor de UNA localidad; en blanco si hay varias
EF1 = "IF(COUNTROWS('Efectos marginales') = 1, {})"
BOG = "LOOKUPVALUE('Bogotá'[valor], 'Bogotá'[indicador], \"{}\")"
PCT, PCT_SIGNO, PP = "0.0 %", "+0.0 %;-0.0 %;0.0 %", "+0.0;-0.0;0.0"

MEDIDAS = [
    # 1. Resumen ------------------------------------------------------------
    ("1. Resumen", "Casos registrados", "SUM(Delitos[casos])", "#,0", "Casos de la serie SCJ (enero-agosto de cada año)."),
    ("1. Resumen", "Hurto a personas 2019", 'CALCULATE([Casos registrados], Delitos[codigo] = "HP", Delitos[anio] = 2019)', "#,0", None),
    ("1. Resumen", "Hurto a personas 2026", 'CALCULATE([Casos registrados], Delitos[codigo] = "HP", Delitos[anio] = 2026)', "#,0", None),
    ("1. Resumen", "Variación hurto a personas 2019-2026",
     "DIVIDE([Hurto a personas 2026] - [Hurto a personas 2019], [Hurto a personas 2019])", PCT_SIGNO,
     "Variación de los casos de hurto a personas, enero-agosto 2019 frente a enero-agosto 2026."),
    ("1. Resumen", "Violencia intrafamiliar 2018", 'CALCULATE([Casos registrados], Delitos[codigo] = "VI", Delitos[anio] = 2018)', "#,0", None),
    ("1. Resumen", "Violencia intrafamiliar 2026", 'CALCULATE([Casos registrados], Delitos[codigo] = "VI", Delitos[anio] = 2026)', "#,0", None),
    ("1. Resumen", "Variación violencia intrafamiliar 2018-2026",
     "DIVIDE([Violencia intrafamiliar 2026] - [Violencia intrafamiliar 2018], [Violencia intrafamiliar 2018])", PCT_SIGNO, None),
    ("1. Resumen", "Delitos sexuales 2018", 'CALCULATE([Casos registrados], Delitos[codigo] = "DS", Delitos[anio] = 2018)', "#,0", None),
    ("1. Resumen", "Delitos sexuales 2026", 'CALCULATE([Casos registrados], Delitos[codigo] = "DS", Delitos[anio] = 2026)', "#,0", None),
    ("1. Resumen", "Variación delitos sexuales 2018-2026",
     "DIVIDE([Delitos sexuales 2026] - [Delitos sexuales 2018], [Delitos sexuales 2018])", PCT_SIGNO, None),
    ("1. Resumen", "Ciudad insegura, Bogotá", f"DIVIDE({BOG.format('ciudad_insegura_pct')}, 100)", PCT,
     "Dato de Bogotá calculado con los microdatos de la Bienal 2025 y su factor de expansión (tabla Bogotá)."),
    ("1. Resumen", "Zona insegura, Bogotá", f"DIVIDE({BOG.format('zona_insegura_pct')}, 100)", PCT,
     "Dato de Bogotá calculado con los microdatos de la Bienal 2025 y su factor de expansión (tabla Bogotá)."),
    ("1. Resumen", "Víctimas por delito registrado, Bogotá", BOG.format("cifra_oculta_bogota"), "0.0",
     "Víctimas estimadas (EMV 2024) por cada delito de alto impacto registrado (SCJ 2024), Bogotá."),
    ("1. Resumen", "Localidades con IBS > 1", "COUNTROWS(FILTER(Localidades, Localidades[ibs] > 1))", "0",
     "Localidades con Índice de Brecha de Seguridad mayor que 1 (más de una desviación estándar de miedo por encima de su delito)."),
    ("1. Resumen", "Localidades en el top 5 en más del 90 % de réplicas",
     "COUNTROWS(FILTER(Localidades, Localidades[prob_top5] > 0.9))", "0", None),
    # 2. Serie --------------------------------------------------------------
    ("2. Serie de delitos", "Índice base 2018",
     "VAR base = CALCULATE([Casos registrados], Delitos[anio] = 2018)\nRETURN\n    DIVIDE([Casos registrados], base) * 100", "0",
     "Casos del año sobre casos de 2018, por 100 (enero-agosto)."),
    ("2. Serie de delitos", "Índice hurto a personas", 'CALCULATE([Índice base 2018], Delitos[codigo] = "HP")', "0", None),
    ("2. Serie de delitos", "Índice violencia intrafamiliar", 'CALCULATE([Índice base 2018], Delitos[codigo] = "VI")', "0", None),
    ("2. Serie de delitos", "Índice delitos sexuales", 'CALCULATE([Índice base 2018], Delitos[codigo] = "DS")', "0", None),
    # 3. Localidad ----------------------------------------------------------
    ("3. Localidad", "Índice de Brecha", LOC.format("MAX(Localidades[ibs])"), "0.00",
     "Índice de Brecha de Seguridad de la localidad (z). En blanco si hay más de una localidad en contexto."),
    ("3. Localidad", "Índice de Brecha, P5", LOC.format("MAX(Localidades[ibs_p05])"), "0.00", "Percentil 5 del bootstrap."),
    ("3. Localidad", "Índice de Brecha, P95", LOC.format("MAX(Localidades[ibs_p95])"), "0.00", "Percentil 95 del bootstrap."),
    ("3. Localidad", "Puesto en el Índice de Brecha", LOC.format("MAX(Localidades[puesto])"), "0", None),
    ("3. Localidad", "Réplicas en el top 5", LOC.format("MAX(Localidades[prob_top5])"), "0 %",
     "Proporción de réplicas bootstrap en que la localidad queda entre las 5 de mayor Índice de Brecha."),
    ("3. Localidad", "Víctimas por delito registrado", LOC.format("MAX(Localidades[cifra_oculta])"), "0.0",
     "Cifra oculta: víctimas estimadas por cada delito registrado."),
    ("3. Localidad", "Zona insegura (%)", LOC.format("DIVIDE(MAX(Localidades[zona_insegura]), 100)"), PCT, None),
    ("3. Localidad", "Ciudad insegura (%)", LOC.format("DIVIDE(MAX(Localidades[ciudad_insegura]), 100)"), PCT, None),
    ("3. Localidad", "Delitos de alto impacto por 100 mil", LOC.format("MAX(Localidades[delitos_alto_impacto_100k])"), "#,0", None),
    ("3. Localidad", "Zona insegura, mujeres (%)", LOC.format("DIVIDE(MAX(Localidades[zona_insegura_mujeres]), 100)"), PCT, None),
    ("3. Localidad", "Zona insegura, hombres (%)", LOC.format("DIVIDE(MAX(Localidades[zona_insegura_hombres]), 100)"), PCT, None),
    ("3. Localidad", "Diferencia mujeres - hombres (pp)",
     LOC.format("MAX(Localidades[zona_insegura_mujeres]) - MAX(Localidades[zona_insegura_hombres])"), PP,
     "Puntos porcentuales: % de mujeres menos % de hombres que califican insegura su zona."),
    ("3. Localidad", "Índice de Brecha, top 5",
     "VAR p = [Puesto en el Índice de Brecha]\nRETURN\n    IF(NOT ISBLANK(p) && p <= 5, [Índice de Brecha])", "0.00",
     "Índice de Brecha solo para las 5 localidades de mayor puesto."),
    ("3. Localidad", "Réplicas en el top 5, top 5",
     "VAR p = [Puesto en el Índice de Brecha]\nRETURN\n    IF(NOT ISBLANK(p) && p <= 5, [Réplicas en el top 5])", "0 %", None),
    ("3. Localidad", "Color Índice de Brecha",
     f'VAR v = [Índice de Brecha]\nRETURN\n    IF(ISBLANK(v), BLANK(), IF(v > 0, "{AMBAR}", "{AZUL}"))', None,
     "Ámbar: más miedo que delito registrado; azul: al revés."),
    ("3. Localidad", "Zona insegura, promedio simple de localidades", "DIVIDE(AVERAGE(Localidades[zona_insegura]), 100)", PCT,
     "Promedio simple de las localidades en contexto. NO es el dato de Bogotá (ese está en Zona insegura, Bogotá)."),
    ("3. Localidad", "Ciudad insegura, promedio simple de localidades", "DIVIDE(AVERAGE(Localidades[ciudad_insegura]), 100)", PCT,
     "Promedio simple de las localidades en contexto. NO es el dato de Bogotá (ese está en Ciudad insegura, Bogotá)."),
    # 4. Modelo -------------------------------------------------------------
    ("4. Modelo", "Efecto marginal (pp)", EF1.format("SUM('Efectos marginales'[ame_pp])"), PP,
     "Efecto marginal promedio en puntos porcentuales sobre la probabilidad de calificar insegura la zona."),
    ("4. Modelo", "IC 95 % inferior (pp)", EF1.format("SUM('Efectos marginales'[ic_inf])"), PP, None),
    ("4. Modelo", "IC 95 % superior (pp)", EF1.format("SUM('Efectos marginales'[ic_sup])"), PP, None),
    ("4. Modelo", "p-valor",
     "VAR p = " + EF1.format("SUM('Efectos marginales'[p])") +
     '\nRETURN\n    IF(ISBLANK(p), BLANK(), IF(p < 0.001, "< 0,001", FORMAT(p, "0.000")))', None, None),
    ("4. Modelo", "Significativo al 95 %",
     "VAR i = " + EF1.format("SUM('Efectos marginales'[ic_inf])") +
     "\nVAR s = " + EF1.format("SUM('Efectos marginales'[ic_sup])") +
     '\nRETURN\n    IF(ISBLANK(i), BLANK(), IF(i > 0 || s < 0, "Sí", "No"))', None,
     "Sí cuando el intervalo de confianza del 95 % no incluye el cero."),
    ("4. Modelo", "Color efecto marginal",
     "VAR i = " + EF1.format("SUM('Efectos marginales'[ic_inf])") +
     "\nVAR s = " + EF1.format("SUM('Efectos marginales'[ic_sup])") +
     "\nVAR a = [Efecto marginal (pp)]" +
     f'\nRETURN\n    IF(ISBLANK(a), BLANK(), IF(i > 0 || s < 0, IF(a > 0, "{AMBAR}", "{AZUL}"), "{GRIS}"))', None,
     "Ámbar: sube la inseguridad percibida; azul: la baja; gris: no significativo."),
    ("4. Modelo", "AUC (validación cruzada)", "IF(COUNTROWS('AUC por bloque') = 1, SUM('AUC por bloque'[auc]))", "0.000",
     "Área bajo la curva ROC fuera de muestra. 0,5 = azar; 1 = predicción perfecta."),
    ("4. Modelo", "AUC, desviación estándar", "IF(COUNTROWS('AUC por bloque') = 1, SUM('AUC por bloque'[auc_sd]))", "0.000", None),
    ("4. Modelo", "Color AUC",
     "VAR b = SELECTEDVALUE('AUC por bloque'[bloque])\nRETURN\n    SWITCH(\n        TRUE(),\n        ISBLANK(b), BLANK(),\n"
     f'        CONTAINSSTRING(b, "hechos") || CONTAINSSTRING(b, "calificación") || b = "Todo", "{AMBAR}",\n'
     f'        CONTAINSSTRING(b, "delito"), "{AZUL}",\n        "{GRIS}"\n    )', None,
     "Ámbar: bloques con variables del entorno; azul: con delito registrado; gris: solo perfil."),
    # 5. Género -------------------------------------------------------------
    ("5. Género", "Mujeres (%)", "IF(COUNTROWS('Género') = 1, DIVIDE(SUM('Género'[mujeres]), 100))", PCT, "EMV 2024, Bogotá, ponderado."),
    ("5. Género", "Hombres (%)", "IF(COUNTROWS('Género') = 1, DIVIDE(SUM('Género'[hombres]), 100))", PCT, "EMV 2024, Bogotá, ponderado."),
    ("5. Género", "Diferencia mujeres - hombres, EMV (pp)",
     "IF(COUNTROWS('Género') = 1, SUM('Género'[mujeres]) - SUM('Género'[hombres]))", PP, None),
    ("5. Género", "Ser mujer: temor al acoso sexual (pp)", BOG.format("ame_mujer_teme_acoso_sexual"), PP,
     "Efecto marginal de ser mujer a igual edad, estrato y victimización (EMV 2024)."),
    ("5. Género", "Ser mujer: evita salir de noche (pp)", BOG.format("ame_mujer_no_sale_noche"), PP,
     "Efecto marginal de ser mujer a igual edad, estrato y victimización (EMV 2024)."),
    ("5. Género", "Ser mujer: inseguridad en el barrio (pp)", BOG.format("ame_mujer_barrio_inseguro"), PP,
     "Efecto marginal de ser mujer a igual edad, estrato y victimización (EMV 2024)."),
    # 9. Textos dinámicos (subtítulos) --------------------------------------
    ("9. Textos", "Texto hurto a personas",
     '"De " & FORMAT([Hurto a personas 2019], "#,0") & " a " & FORMAT([Hurto a personas 2026], "#,0") & " casos (SCJ)"', None, None),
    ("9. Textos", "Texto violencia intrafamiliar",
     '"De " & FORMAT([Violencia intrafamiliar 2018], "#,0") & " a " & FORMAT([Violencia intrafamiliar 2026], "#,0") & " casos"', None, None),
    ("9. Textos", "Texto delitos sexuales",
     '"De " & FORMAT([Delitos sexuales 2018], "#,0") & " a " & FORMAT([Delitos sexuales 2026], "#,0") & " casos"', None, None),
    ("9. Textos", "Texto encuestas Bienal",
     f'"Bogotá, Bienal 2025 (" & FORMAT({BOG.format("n_bienal")}, "#,0") & " encuestas)"', None, None),
    ("9. Textos", "Texto AUC",
     "\"Validación cruzada con \" & FORMAT(MAX('AUC por bloque'[pliegues]), \"0\") & \" pliegues. 0,5 = azar; 1 = perfecto.\"", None, None),
]
for k, et in (("teme_acoso_sexual", "acoso"), ("no_sale_noche", "noche"), ("barrio_inseguro", "barrio")):
    MEDIDAS.append((
        "9. Textos", f"Texto IC mujer {et}",
        f'"IC 95 %: " & FORMAT({BOG.format(f"ame_mujer_{k}_ic_inf")}, "0.0") & " a " & '
        f'FORMAT({BOG.format(f"ame_mujer_{k}_ic_sup")}, "0.0") & " pp"', None, None))

TABLA_MEDIDAS = {
    "name": "Medidas",
    "columns": [{"name": "Columna", "dataType": "string", "hidden": True, "fmt": None, "desc": None}],
    "m": "let\n    Origen = #table(type table [Columna = text], {})\nin\n    Origen",
    "measures": [{"folder": f, "name": n, "expr": e, "fmt": fm, "desc": d} for f, n, e, fm, d in MEDIDAS],
}


def tmdl_tabla(t) -> str:
    L = [f"table {q(t['name'])}", f"\tlineageTag: {uid('table', t['name'])}", ""]
    for m in t["measures"]:
        if m.get("desc"):
            L.append(f"\t/// {m['desc']}")
        expr = m["expr"].strip()
        if "\n" in expr:
            L.append(f"\tmeasure {q(m['name'])} =")
            L += ["\t\t\t" + linea for linea in expr.split("\n")]
        else:
            L.append(f"\tmeasure {q(m['name'])} = {expr}")
        if m.get("fmt"):
            L.append(f"\t\tformatString: {m['fmt']}")
        L.append(f"\t\tdisplayFolder: {m['folder']}")
        L.append(f"\t\tlineageTag: {uid('measure', m['name'])}")
        L.append("")
    for c in t["columns"]:
        if c.get("desc"):
            L.append(f"\t/// {c['desc']}")
        L.append(f"\tcolumn {q(c['name'])}")
        L.append(f"\t\tdataType: {c['dataType']}")
        if c.get("fmt"):
            L.append(f"\t\tformatString: {c['fmt']}")
        if c.get("hidden"):
            L.append("\t\tisHidden")
        L.append(f"\t\tlineageTag: {uid('column', t['name'], c['name'])}")
        L.append("\t\tsummarizeBy: none")
        L.append(f"\t\tsourceColumn: {c['name']}")
        if c.get("sortBy"):
            L.append(f"\t\tsortByColumn: {q(c['sortBy'])}")
        L += ["", "\t\tannotation SummarizationSetBy = Automatic", ""]
    L += [f"\tpartition {q(t['name'])} = m", "\t\tmode: import", "\t\tsource ="]
    L += ["\t\t\t\t" + linea for linea in t["m"].split("\n")]
    L += ["", "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(L)


def generar_modelo():
    if SM.exists():
        for hijo in ("definition", "definition.pbism", ".platform"):
            p = SM / hijo
            shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
    d = SM / "definition"
    tablas = TABLAS + [TABLA_MEDIDAS]
    escribir(d / "database.tmdl", "database\n\tcompatibilityLevel: 1600\n\n")
    orden = json.dumps(["RutaDatos"] + [t["name"] for t in tablas], ensure_ascii=False)
    escribir(d / "model.tmdl", "\n".join([
        "model Model",
        "\tculture: es-CO",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tdiscourageImplicitMeasures",
        "\tsourceQueryCulture: es-CO",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        f"annotation PBI_QueryOrder = {orden}",
        "",
        "annotation __PBI_TimeIntelligenceEnabled = 0",
        "",
        'annotation PBI_ProTooling = ["DevMode"]',
        "",
        *[f"ref table {q(t['name'])}" for t in tablas],
        "",
    ]))
    escribir(d / "expressions.tmdl", "\n".join([
        "/// Carpeta con los CSV del tablero. Cámbiela en Transformar datos > Administrar parámetros.",
        f'expression RutaDatos = "{RUTA_DATOS}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]',
        f"\tlineageTag: {uid('expression', 'RutaDatos')}",
        "",
        "\tannotation PBI_ResultType = Text",
        "",
    ]))
    for t in tablas:
        escribir(d / "tables" / f"{t['name']}.tmdl", tmdl_tabla(t))
    escribir_json(SM / "definition.pbism", {
        "$schema": SCHEMA + "item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.0", "settings": {}})
    escribir_json(SM / ".platform", {
        "$schema": SCHEMA + "gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": NOMBRE},
        "config": {"version": "2.0", "logicalId": uid("logical", "semanticModel")}})


# ---------------------------------------------------------------------------
# 2. INFORME (PBIR)
# ---------------------------------------------------------------------------

def L(v):
    """Literal de formato PBIR: bool, número (D) o texto entre comillas simples."""
    if isinstance(v, bool):
        s = "true" if v else "false"
    elif isinstance(v, (int, float)):
        s = f"{float(v):g}D"
    else:
        s = "'" + str(v).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": s}}}


def C(hexcolor):
    return {"solid": {"color": L(hexcolor)}}


def MED(nombre, tabla="Medidas"):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": tabla}}, "Property": nombre}}


def COL(tabla, nombre):
    return {"Column": {"Expression": {"SourceRef": {"Entity": tabla}}, "Property": nombre}}


def CM(medida):
    """Color tomado de una medida (formato condicional por valor de campo)."""
    return {"solid": {"color": {"expr": MED(medida)}}}


def qref(campo):
    k = next(iter(campo))
    return f"{campo[k]['Expression']['SourceRef']['Entity']}.{campo[k]['Property']}"


def P(campo, nombre=None):
    k = next(iter(campo))
    d = {"field": campo, "queryRef": qref(campo), "nativeQueryRef": nombre or campo[k]["Property"]}
    if nombre:
        d["displayName"] = nombre
    return d


def props(selector=None, **kw):
    o = {"properties": kw}
    if selector:
        o["selector"] = selector
    return [o]


TODAS = {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}


def contenedor(titulo=None, subtitulo=None, subtitulo_medida=None, tam_titulo=None):
    o = {}
    if titulo:
        o["title"] = props(show=L(True), text=L(titulo), titleWrap=L(True))
        if tam_titulo:
            o["title"][0]["properties"]["fontSize"] = L(tam_titulo)
    else:
        o["title"] = props(show=L(False))
    if subtitulo or subtitulo_medida:
        o["subTitle"] = props(show=L(True), text=({"expr": MED(subtitulo_medida)} if subtitulo_medida else L(subtitulo)))
    return o


def ordenar(campo, sentido="Descending"):
    return {"sort": [{"field": campo, "direction": sentido}], "isDefaultSort": False}


def v_textbox(parrafos):
    """parrafos: lista de (texto, tamaño_pt, negrita, color)."""
    ps = []
    for texto, tam, negrita, color in parrafos:
        estilo = {"fontFamily": FUENTE_FUERTE if negrita else FUENTE, "fontSize": f"{tam}pt", "color": color}
        if negrita:
            estilo["fontWeight"] = "bold"
        ps.append({"textRuns": [{"value": texto, "textStyle": estilo}]})
    return {
        "visualType": "textbox",
        "objects": {"general": props(paragraphs=ps)},
        "visualContainerObjects": {
            "title": props(show=L(False)), "background": props(show=L(False)),
            "border": props(show=L(False)), "dropShadow": props(show=L(False))},
        "drillFilterOtherVisuals": True,
    }


def v_card(medida, titulo, color, subtitulo=None, subtitulo_medida=None, tam=24):
    return {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [P(MED(medida))]}}},
        "objects": {
            "labels": props(color=C(color), fontSize=L(tam), fontFamily=L(FUENTE_FUERTE), labelDisplayUnits=L(1)),
            "categoryLabels": props(show=L(False)),
        },
        "visualContainerObjects": {**contenedor(titulo, subtitulo, subtitulo_medida, tam_titulo=10),
                                   "padding": props(top=L(8), bottom=L(4), left=L(10), right=L(10))},
        "drillFilterOtherVisuals": True,
    }


EJE_VAL = props(fontSize=L(9), labelColor=C(TINTA2), showAxisTitle=L(False), gridlineShow=L(True), gridlineColor=C("#EEF1F5"))
ETIQUETAS = props(show=L(True), color=C(TINTA), fontSize=L(9))


def v_barras(categoria, valores, titulo, subtitulo=None, color_medida=None, colores_serie=None, orden=None,
             tooltips=(), eje_valor=None, leyenda=False, subtitulo_medida=None, margen=25):
    qs = {"Category": {"projections": [P(*categoria)]}, "Y": {"projections": [P(*v) for v in valores]}}
    if tooltips:
        qs["Tooltips"] = {"projections": [P(*t) for t in tooltips]}
    eje_cat = props(fontSize=L(9), labelColor=C(TINTA2), showAxisTitle=L(False), maxMarginFactor=L(margen))
    objetos = {"categoryAxis": eje_cat, "valueAxis": eje_valor or EJE_VAL, "labels": ETIQUETAS,
               "legend": props(show=L(leyenda), position=L("Top"), fontSize=L(9))}
    if color_medida:
        objetos["dataPoint"] = props(selector=TODAS, fill=CM(color_medida))
    if colores_serie:
        objetos["dataPoint"] = [{"properties": {"fill": C(col)}, "selector": {"metadata": qref(campo)}}
                                for campo, col in colores_serie]
    v = {"visualType": "clusteredBarChart", "query": {"queryState": qs}, "objects": objetos,
         "visualContainerObjects": contenedor(titulo, subtitulo, subtitulo_medida), "drillFilterOtherVisuals": True}
    if orden:
        v["query"]["sortDefinition"] = orden
    return v


def v_linea(eje, series, titulo, subtitulo=None):
    return {
        "visualType": "lineChart",
        "query": {
            "queryState": {"Category": {"projections": [P(*eje)]}, "Y": {"projections": [P(c, n) for c, n, _ in series]}},
            "sortDefinition": {"sort": [{"field": eje[0], "direction": "Ascending"}], "isDefaultSort": True},
        },
        "objects": {
            "categoryAxis": props(axisType=L("Categorical"), fontSize=L(9), labelColor=C(TINTA2), showAxisTitle=L(False)),
            "valueAxis": props(fontSize=L(9), labelColor=C(TINTA2), showAxisTitle=L(False), start=L(0),
                               gridlineShow=L(True), gridlineColor=C("#EEF1F5")),
            "legend": props(show=L(True), position=L("Top"), fontSize=L(10)),
            "lineStyles": props(strokeWidth=L(3), showMarker=L(True), markerSize=L(5)),
            "labels": props(show=L(False)),
            "dataPoint": [{"properties": {"fill": C(col)}, "selector": {"metadata": qref(c)}} for c, _, col in series],
        },
        "visualContainerObjects": contenedor(titulo, subtitulo),
        "drillFilterOtherVisuals": True,
    }


def v_dispersion(detalle, x, y, titulo, subtitulo, color_medida):
    return {
        "visualType": "scatterChart",
        "query": {"queryState": {
            "Category": {"projections": [P(*detalle)]},
            "X": {"projections": [P(*x)]},
            "Y": {"projections": [P(*y)]},
        }},
        "objects": {
            "categoryAxis": props(logAxisScale=L(True), start=L(900), end=L(14000), fontSize=L(9), labelColor=C(TINTA2), showAxisTitle=L(True),
                                  titleText=L(x[1] or x[0]["Measure"]["Property"]), titleFontSize=L(9),
                                  gridlineShow=L(True), gridlineColor=C("#EEF1F5")),
            "valueAxis": props(fontSize=L(9), labelColor=C(TINTA2), showAxisTitle=L(True),
                               titleText=L(y[1] or y[0]["Measure"]["Property"]), titleFontSize=L(9),
                               gridlineShow=L(True), gridlineColor=C("#EEF1F5")),
            "categoryLabels": props(show=L(True), color=C(TINTA2), fontSize=L(8)),
            "dataPoint": props(selector=TODAS, fill=CM(color_medida)),
            "bubbles": props(bubbleSize=L(6)),
            "legend": props(show=L(False)),
        },
        "visualContainerObjects": contenedor(titulo, subtitulo),
        "drillFilterOtherVisuals": True,
    }


def v_tabla(columnas, titulo, subtitulo=None, orden=None, colores=(), anchos=()):
    objetos = {
        "total": props(totals=L(False)),
        "columnHeaders": props(fontSize=L(9), fontColor=C(TINTA2), backColor=C("#F6F7FA"), wordWrap=L(True),
                               fontFamily=L(FUENTE_FUERTE)),
        "values": props(fontSize=L(10), fontColorPrimary=C(TINTA), fontColorSecondary=C(TINTA),
                        backColorPrimary=C(BLANCO), backColorSecondary=C("#FAFBFC"), fontFamily=L(FUENTE)),
        "grid": props(gridHorizontal=L(True), gridHorizontalColor=C("#EEF1F5"), gridVertical=L(False),
                      rowPadding=L(5), outlineColor=C(LINEA)),
    }
    if colores:
        objetos["columnFormatting"] = [{"properties": {"fontColor": C(col)}, "selector": {"metadata": qref(campo)}}
                                       for campo, col in colores]
    if anchos:
        objetos["columnWidth"] = [{"properties": {"value": L(w)}, "selector": {"metadata": qref(campo)}}
                                  for campo, w in anchos]
    v = {"visualType": "tableEx", "query": {"queryState": {"Values": {"projections": [P(*c) for c in columnas]}}},
         "objects": objetos, "visualContainerObjects": contenedor(titulo, subtitulo), "drillFilterOtherVisuals": True}
    if orden:
        v["query"]["sortDefinition"] = orden
    return v


def filtro_en(nombre, tabla, columna, valores):
    return {
        "name": nombre,
        "field": COL(tabla, columna),
        "type": "Categorical",
        "filter": {
            "Version": 2,
            "From": [{"Name": "t", "Entity": tabla, "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": columna}}],
                "Values": [[{"Literal": {"Value": "'" + v.replace("'", "''") + "'"}}] for v in valores],
            }}}],
        },
        "howCreated": "User",
    }


def encabezado(pagina, titulo, subtitulo, alto_titulo=44, tam=18):
    return [
        (f"{pagina}-titulo", 24, 14, 1232, alto_titulo, v_textbox([(titulo, tam, True, TINTA)])),
        (f"{pagina}-sub", 24, 14 + alto_titulo, 1232, 30, v_textbox([(subtitulo, 10, False, TINTA2)])),
    ]


# --- Campos frecuentes -------------------------------------------------------
NOMBRE_LOC = (COL("Localidades", "nombre"), "Localidad")
IBS = (MED("Índice de Brecha"), None)


def paginas():
    pags = []

    # Página 1: Resumen ---------------------------------------------------------
    vis = encabezado(
        "resumen",
        "¿Por qué la inseguridad percibida no baja cuando el delito registrado sí, "
        "y en qué territorios debe intervenir primero el Distrito?",
        "El miedo que no baja · Bogotá DataJam 5 · The data squad. Fuentes: SCJ (delitos de alto impacto, enero-agosto 2018-2026), "
        "Encuesta Bienal de Cultura Ciudadana 2025 y Encuesta Mundial de Valores 2024.",
        alto_titulo=64, tam=17)
    tarjetas = [
        ("Variación hurto a personas 2019-2026", "Hurto a personas 2019 → 2026", AZUL, None, "Texto hurto a personas"),
        ("Ciudad insegura, Bogotá", "Califica la ciudad insegura", AMBAR, None, "Texto encuestas Bienal"),
        ("Zona insegura, Bogotá", "Califica insegura su zona", AMBAR, None, "Texto encuestas Bienal"),
        ("Víctimas por delito registrado, Bogotá", "Víctimas por delito registrado", TINTA, "EMV 2024 frente a SCJ 2024", None),
        ("Localidades con IBS > 1", "Localidades con brecha > 1", AMBAR, "Índice de Brecha de Seguridad > 1", None),
    ]
    ancho = (1232 - 4 * 16) / 5
    for i, (m, t, col, sub, subm) in enumerate(tarjetas):
        vis.append((f"resumen-kpi{i}", 24 + i * (ancho + 16), 112, ancho, 128, v_card(m, t, col, sub, subm)))
    vis.append(("resumen-serie", 24, 256, 800, 440, v_linea(
        (COL("Delitos", "anio"), "Año"),
        [(MED("Índice hurto a personas"), "Hurto a personas", AZUL),
         (MED("Índice violencia intrafamiliar"), "Violencia intrafamiliar", VIOLETA),
         (MED("Índice delitos sexuales"), "Delitos sexuales", AMBAR)],
        "Delitos registrados en Bogotá, enero-agosto (índice 2018 = 100)",
        "Fuente: SCJ, delitos de alto impacto por localidad. El hurto cae; la violencia contra las mujeres sube.")))
    vis.append(("resumen-top5", 840, 256, 416, 268, v_tabla(
        [NOMBRE_LOC, (MED("Índice de Brecha, top 5"), "Índice de Brecha"),
         (MED("Réplicas en el top 5, top 5"), "Réplicas en el top 5")],
        "Dónde intervenir primero",
        "Réplicas: % de remuestreos bootstrap en que sigue en el top 5",
        orden=ordenar(MED("Índice de Brecha, top 5")))))
    vis.append(("resumen-vif", 840, 540, 200, 156, v_card(
        "Variación violencia intrafamiliar 2018-2026", "Violencia intrafamiliar, 2018 → 2026", VIOLETA,
        subtitulo_medida="Texto violencia intrafamiliar", tam=22)))
    vis.append(("resumen-ds", 1056, 540, 200, 156, v_card(
        "Variación delitos sexuales 2018-2026", "Delitos sexuales, 2018 → 2026", AMBAR,
        subtitulo_medida="Texto delitos sexuales", tam=22)))
    pags.append(("Resumen", vis))

    # Página 2: La brecha -------------------------------------------------------
    vis = encabezado(
        "brecha",
        "La brecha: dónde hay más miedo del que explica el delito registrado",
        "Índice de Brecha de Seguridad (IBS) = z(% que califica insegura su zona) − z(log de delitos de alto impacto por 100 mil). "
        "Ámbar: más miedo que delito registrado; azul: al revés.")
    vis.append(("brecha-barras", 24, 100, 500, 596, v_barras(
        NOMBRE_LOC, [IBS], "Índice de Brecha por localidad, 2025", "Ordenado de mayor a menor (z)",
        color_medida="Color Índice de Brecha", orden=ordenar(MED("Índice de Brecha")),
        tooltips=[(MED("Índice de Brecha, P5"), None), (MED("Índice de Brecha, P95"), None),
                  (MED("Puesto en el Índice de Brecha"), None), (MED("Réplicas en el top 5"), None)])))
    vis.append(("brecha-dispersion", 540, 100, 716, 300, v_dispersion(
        NOMBRE_LOC,
        (MED("Delitos de alto impacto por 100 mil"), "Delitos de alto impacto por 100 mil hab. (escala log)"),
        (MED("Zona insegura (%)"), "Califica insegura su zona"),
        "Miedo en la zona frente a delito registrado",
        "Cada punto es una localidad. El centro registra mucho delito (población flotante) y siente menos miedo.",
        "Color Índice de Brecha")))
    vis.append(("brecha-tabla", 540, 416, 716, 280, v_tabla(
        [NOMBRE_LOC, (MED("Índice de Brecha"), "Índice de Brecha"),
         (MED("Víctimas por delito registrado"), "Víctimas por delito registrado"),
         (MED("Zona insegura (%)"), "Zona insegura"),
         (MED("Delitos de alto impacto por 100 mil"), "Delitos alto impacto por 100 mil")],
        "Detalle por localidad", "Cifra oculta: víctimas estimadas (EMV 2024) por cada delito registrado (SCJ 2024)",
        orden=ordenar(MED("Índice de Brecha")))))
    pags.append(("La brecha", vis))

    # Página 3: Qué la explica --------------------------------------------------
    vis = encabezado(
        "explica",
        "Qué la explica: el entorno inmediato pesa más que el delito registrado",
        "Logit ponderado (Bienal 2025) de calificar insegura la propia zona. Efecto marginal promedio en puntos porcentuales (pp). "
        "Gris: no significativo al 95 %.")
    f_hechos = lambda n: [filtro_en(n, "Efectos marginales", "modelo", ["Hechos del entorno"])]  # noqa: E731
    vis.append(("explica-ame", 24, 100, 760, 372, v_barras(
        (COL("Efectos marginales", "etiqueta"), "Variable"), [(MED("Efecto marginal (pp)"), None)],
        "Efectos marginales, modelo «Hechos del entorno»",
        "Ámbar: sube la probabilidad de sentir insegura la zona; azul: la baja",
        color_medida="Color efecto marginal", orden=ordenar(MED("Efecto marginal (pp)")), margen=45,
        tooltips=[(MED("IC 95 % inferior (pp)"), None), (MED("IC 95 % superior (pp)"), None), (MED("p-valor"), None)]),
        f_hechos("filtroModeloHechosBarras")))
    vis.append(("explica-ic", 24, 488, 760, 208, v_tabla(
        [(COL("Efectos marginales", "etiqueta"), "Variable"), (MED("Efecto marginal (pp)"), "Efecto (pp)"),
         (MED("IC 95 % inferior (pp)"), "IC 95 % inf."), (MED("IC 95 % superior (pp)"), "IC 95 % sup."),
         (MED("p-valor"), "p-valor"), (MED("Significativo al 95 %"), "Significativo")],
        "Intervalos de confianza al 95 % (bootstrap de localidades)", None,
        orden=ordenar(MED("Efecto marginal (pp)")),
        anchos=[(COL("Efectos marginales", "etiqueta"), 300)]),
        f_hechos("filtroModeloHechosTabla")))
    vis.append(("explica-auc", 800, 100, 456, 420, v_barras(
        (COL("AUC por bloque", "bloque"), "Bloque de variables"), [(MED("AUC (validación cruzada)"), "AUC")],
        "Capacidad predictiva fuera de muestra (AUC)", subtitulo_medida="Texto AUC",
        color_medida="Color AUC", orden=ordenar(COL("AUC por bloque", "bloque"), "Ascending"), margen=50,
        tooltips=[(MED("AUC, desviación estándar"), None)],
        eje_valor=props(fontSize=L(9), labelColor=C(TINTA2), showAxisTitle=L(False), start=L(0.5), end=L(0.85),
                        gridlineShow=L(True), gridlineColor=C("#EEF1F5")))))
    vis.append(("explica-nota", 800, 536, 456, 160, v_textbox([
        ("Cómo leerlo", 11, True, TINTA),
        ("Sumar el delito registrado de la localidad al perfil de la persona casi no mejora la predicción. "
         "Sumar lo que pasa en su entorno inmediato (atracos en el parque, conflictos vecinales, alumbrado) sí.", 10, False, TINTA2),
        ("Ámbar: bloques con variables del entorno · Azul: con delito registrado · Gris: solo perfil.", 9, False, TINTA2),
    ])))
    pags.append(("Qué la explica", vis))

    # Página 4: Género ----------------------------------------------------------
    vis = encabezado(
        "genero",
        "Género: las mujeres reportan menos delitos y recortan más su vida",
        "Encuesta Mundial de Valores 2024 (Bogotá, ponderada) y Encuesta Bienal de Cultura Ciudadana 2025 por localidad.")
    vis.append(("genero-barras", 24, 100, 640, 372, v_barras(
        (COL("Género", "etiqueta"), "Indicador"),
        [(MED("Mujeres (%)"), "Mujeres"), (MED("Hombres (%)"), "Hombres")],
        "% de adultos en Bogotá, por sexo (EMV 2024)", None,
        colores_serie=[(MED("Mujeres (%)"), VIOLETA), (MED("Hombres (%)"), VERDE)],
        orden=ordenar(COL("Género", "etiqueta"), "Ascending"), leyenda=True, margen=40,
        eje_valor=props(fontSize=L(9), labelColor=C(TINTA2), showAxisTitle=L(False), start=L(0), end=L(1),
                        gridlineShow=L(True), gridlineColor=C("#EEF1F5")))))
    vis.append(("genero-nota", 24, 484, 640, 28, v_textbox([
        ("Efecto de ser mujer a igual edad, estrato y victimización (puntos porcentuales, EMV 2024)", 10, True, TINTA)])))
    ancho = (640 - 2 * 16) / 3
    for i, (m, t, subm) in enumerate([
        ("Ser mujer: temor al acoso sexual (pp)", "Temor al acoso sexual", "Texto IC mujer acoso"),
        ("Ser mujer: evita salir de noche (pp)", "Evita salir de noche", "Texto IC mujer noche"),
        ("Ser mujer: inseguridad en el barrio (pp)", "Se siente insegura en su barrio", "Texto IC mujer barrio"),
    ]):
        vis.append((f"genero-kpi{i}", 24 + i * (ancho + 16), 520, ancho, 176, v_card(m, t, VIOLETA, subtitulo_medida=subm)))
    vis.append(("genero-tabla", 680, 100, 576, 596, v_tabla(
        [NOMBRE_LOC, (MED("Zona insegura, mujeres (%)"), "Mujeres"), (MED("Zona insegura, hombres (%)"), "Hombres"),
         (MED("Diferencia mujeres - hombres (pp)"), "Diferencia (pp)")],
        "Califica insegura su zona, por sexo y localidad (Bienal 2025)",
        "Ordenado por la diferencia entre mujeres y hombres",
        orden=ordenar(MED("Diferencia mujeres - hombres (pp)")),
        colores=[(MED("Zona insegura, mujeres (%)"), VIOLETA), (MED("Zona insegura, hombres (%)"), VERDE)])))
    pags.append(("Género", vis))
    return pags


def tema():
    return {
        "name": "El miedo que no baja",
        "dataColors": [AMBAR, AZUL, VIOLETA, VERDE, GRIS, TINTA, "#A5650A", "#1D43A0", "#6B2F9C", "#1E7A39", TINTA2],
        "foreground": TINTA, "foregroundNeutralSecondary": TINTA2, "foregroundNeutralTertiary": GRIS,
        "background": BLANCO, "backgroundLight": FONDO, "backgroundNeutral": LINEA,
        "tableAccent": AZUL, "good": VERDE, "neutral": GRIS, "bad": AMBAR,
        "maximum": AMBAR, "center": "#F8D48F", "minimum": "#FDF0D5", "null": GRIS,
        "hyperlink": AZUL, "visitedHyperlink": AZUL,
        "textClasses": {
            "callout": {"fontSize": 26, "fontFace": FUENTE_FUERTE, "color": TINTA},
            "title": {"fontSize": 12, "fontFace": FUENTE_FUERTE, "color": TINTA},
            "header": {"fontSize": 12, "fontFace": FUENTE_FUERTE, "color": TINTA},
            "label": {"fontSize": 10, "fontFace": FUENTE, "color": TINTA2},
        },
        "visualStyles": {
            "*": {"*": {
                "title": [{"show": True, "fontFamily": FUENTE_FUERTE, "fontSize": 12, "fontColor": {"solid": {"color": TINTA}},
                           "titleWrap": True}],
                "subTitle": [{"fontFamily": FUENTE, "fontSize": 9, "fontColor": {"solid": {"color": TINTA2}}}],
                "background": [{"show": True, "color": {"solid": {"color": BLANCO}}, "transparency": 0}],
                "border": [{"show": True, "color": {"solid": {"color": LINEA}}, "radius": 8}],
                "dropShadow": [{"show": False}],
                "padding": [{"top": 10, "bottom": 10, "left": 12, "right": 12}],
            }},
            "textbox": {"*": {"background": [{"show": False}], "border": [{"show": False}],
                              "padding": [{"top": 0, "bottom": 0, "left": 0, "right": 0}]}},
            "page": {"*": {
                "background": [{"color": {"solid": {"color": BLANCO}}, "transparency": 0}],
                "outspace": [{"color": {"solid": {"color": FONDO}}, "transparency": 0}],
            }},
        },
    }


def generar_informe():
    for hijo in ("definition", "definition.pbir", ".platform", "StaticResources/RegisteredResources"):
        p = RP / hijo
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    base = RP / "StaticResources" / "SharedResources" / "BaseThemes" / f"{BASE_THEME}.json"
    if not base.exists():
        raise SystemExit(f"Falta el tema base de Power BI Desktop: {base}")
    d = RP / "definition"
    version_import = {"visual": V_VISUAL, "report": V_REPORT, "page": V_PAGE}
    escribir_json(RP / "definition.pbir", {
        "$schema": SCHEMA + "item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{NOMBRE}.SemanticModel"}}})
    escribir_json(RP / ".platform", {
        "$schema": SCHEMA + "gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": NOMBRE},
        "config": {"version": "2.0", "logicalId": uid("logical", "report")}})
    escribir_json(d / "version.json", {
        "$schema": SCHEMA + "item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    escribir_json(d / "report.json", {
        "$schema": SCHEMA + f"item/report/definition/report/{V_REPORT}/schema.json",
        "themeCollection": {
            "baseTheme": {"name": BASE_THEME, "reportVersionAtImport": version_import, "type": "SharedResources"},
            "customTheme": {"name": TEMA, "reportVersionAtImport": version_import, "type": "RegisteredResources"},
        },
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources",
             "items": [{"name": BASE_THEME, "path": f"BaseThemes/{BASE_THEME}.json", "type": "BaseTheme"}]},
            {"name": "RegisteredResources", "type": "RegisteredResources",
             "items": [{"name": TEMA, "path": TEMA, "type": "CustomTheme"}]},
        ],
        "settings": {
            "useStylableVisualContainerHeader": True, "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True, "useEnhancedTooltips": True, "useDefaultAggregateDisplayName": True,
            "locale": "es-CO",
        },
    })
    escribir_json(RP / "StaticResources" / "RegisteredResources" / TEMA, tema())
    escribir_json(PB / "tema_el_miedo_que_no_baja.json", tema())

    orden_paginas = []
    for nombre_pagina, visuales in paginas():
        pid = hexid("pagina", nombre_pagina)
        orden_paginas.append(pid)
        dp = d / "pages" / pid
        escribir_json(dp / "page.json", {
            "$schema": SCHEMA + f"item/report/definition/page/{V_PAGE}/schema.json",
            "name": pid, "displayName": nombre_pagina, "displayOption": "FitToPage", "height": 720, "width": 1280,
            "objects": {
                "background": props(color=C(BLANCO), transparency=L(0)),
                "outspace": props(color=C(FONDO), transparency=L(0)),
            },
        })
        for z, item in enumerate(visuales):
            clave, x, y, w, h, visual = item[:6]
            filtros = item[6] if len(item) > 6 else None
            vid = hexid("visual", clave)
            cont = {
                "$schema": SCHEMA + f"item/report/definition/visualContainer/{V_VISUAL}/schema.json",
                "name": vid,
                "position": {"x": round(x, 2), "y": y, "z": z * 1000, "height": h, "width": round(w, 2), "tabOrder": z * 1000},
                "visual": visual,
            }
            if filtros:
                cont["filterConfig"] = {"filters": filtros}
            escribir_json(dp / "visuals" / vid / "visual.json", cont)
    escribir_json(d / "pages" / "pages.json", {
        "$schema": SCHEMA + "item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": orden_paginas, "activePageName": orden_paginas[0]})


def generar_pbip():
    escribir_json(PB / f"{NOMBRE}.pbip", {
        "$schema": SCHEMA + "pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": f"{NOMBRE}.Report"}}],
        "settings": {"enableAutoRecovery": True},
    })


if __name__ == "__main__":
    generar_modelo()
    generar_informe()
    generar_pbip()
    print(f"PBIP generado en {PB}")
