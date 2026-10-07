"""
Frente de victimización y denuncia: ¿cayó el delito o cayó la denuncia?

Ejecutar desde la raíz del repo:  python src/fuentes_victimizacion.py
(La primera vez baja unos 15 MB; después trabaja con la caché de data/crudos/.)

Qué hace
1. Baja con caché los anexos en Excel de la Encuesta de Convivencia y Seguridad Ciudadana (ECSC) del
   DANE, ediciones 2014 a 2024, a data/crudos/ecsc/, más el boletín 2024 y la metodología (para citar
   los quiebres). Cada descarga queda en data/crudos/registro_descargas.csv (fuentes._registrar).
2. Lee de cada anexo la fila «Bogotá D.C.» de seis cuadros: victimización por cualquier delito, denuncia
   por cualquier delito, victimización por hurto a personas, denuncia del hurto a personas, percepción
   de inseguridad en la ciudad y en el barrio. Guarda el porcentaje, el coeficiente de variación (cve)
   y la celda exacta de donde sale cada número.
3. Suma las cifras de la Encuesta de Percepción y Victimización de la Cámara de Comercio de Bogotá (CCB).
   Los informes publican esas cifras como etiquetas de gráficos, que no se pueden leer por máquina sin
   riesgo de desordenarlas: están transcritas a mano, con documento, página y gráfico, en
   data/crudos/victimizacion_transcritos.csv (estado = «transcrito»). El PDF fuente se baja a
   data/crudos/ccb/ para poder verificarlas.
4. Baja de datos.gov.co, mes a mes y solo para Bogotá, el registro de la Policía Nacional (SIEDCO,
   publicado por MinDefensa) y los presuntos homicidios de Medicina Legal (INMLCF), y los pone al lado
   de la capa de la SCJ que usa el resto del proyecto (data/procesados/scj_delitos_localidad_largo.csv).

Escribe
  data/procesados/victimizacion_denuncia_bogota.csv   serie de las encuestas (formato largo)
  data/procesados/registro_contraste_bogota.csv       SCJ vs. SIEDCO vs. INMLCF, por delito y año
  data/procesados/confiabilidad_victimizacion.csv     ficha de cada fuente para el score de confiabilidad

Decisiones
- Año. La ECSC de la edición N pregunta por la victimización del año N-1 (enero-diciembre) y por la
  percepción en el momento de la encuesta. En las tablas, «anio» es el año de referencia para
  victimización y denuncia, y el año de la encuesta para percepción. La edición va en «fuente».
- Ediciones. Se usan las que preguntan por un año calendario cerrado: 2014 a 2017 (28 ciudades) y 2019
  a 2024 (nacional con 13 ciudades). Las de 2012 y 2013 preguntaban por «los últimos doce meses» con
  otros dominios (Bogotá con Soacha en 2012) y quedan fuera. No existen: la de 2018 (sin productos de
  difusión) y la de 2023 (no se recolectó «por motivos presupuestales»; met-ECSC.pdf, p. 7). Por eso no
  hay victimización para 2017 ni para 2022.
- Delitos incluidos. Desde el año de referencia 2020 la victimización y la denuncia «por cualquier
  delito» incluyen los incidentes de seguridad digital. Se publican como dos series:
  cualquier_delito_sin_isd (2013-2020) y cualquier_delito_con_isd (2020-2023). El año 2020 aparece en
  ambas (cuadros 5/9 y 6/10 del anexo 2021). El hurto a personas se define igual en todas las ediciones.
- Error. Los anexos traen el cve (%) de cada porcentaje. Se publica junto con el error estándar
  EE = valor × cve / 100, en puntos porcentuales. El DANE recomienda usar como tendencia, no como nivel,
  las cifras con cve > 15 %.
- Contrastes entre años. Prueba z para dos muestras independientes con los EE publicados; las ediciones
  son muestras distintas. No corrige por pruebas múltiples: se reportan pocas comparaciones fijadas antes.
- Registro. La capa de la SCJ solo trae enero-agosto, así que el contraste usa enero-agosto en las tres
  fuentes. SIEDCO e INMLCF se bajan por mes para poder cortar igual.
"""
import math
import re
import sys
import warnings
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fuentes import CRUDOS, RAIZ, UA, _get, _registrar  # noqa: E402

ECSC_DIR = CRUDOS / "ecsc"
CCB_DIR = CRUDOS / "ccb"
VAL_DIR = CRUDOS / "validacion_registro"
PROC = RAIZ / "data" / "procesados"
TRANSCRITOS = CRUDOS / "victimizacion_transcritos.csv"
DANE = "https://www.dane.gov.co/files"
SOCRATA = "https://www.datos.gov.co/resource"

POB15 = "Personas de 15 años y más, cabecera de Bogotá D.C."
POB_VICT = "Víctimas de 15 años y más de al menos un delito, cabecera de Bogotá D.C."
POB_VICT_HP = "Víctimas de hurto a personas de 15 años y más, cabecera de Bogotá D.C."

# Ediciones de la ECSC. «cuadros»: clave -> nombre de la hoja, o (hoja, etiqueta del bloque) cuando el
# porcentaje buscado no es el primero de la hoja.
EDICIONES = [
    dict(edicion=2014, ref=2013, archivo="anexos_ecsc_2013_2014.xls", ruta="investigaciones/poblacion/convivencia/2014/anexos_ecsc_2013_2014.xls",
         campo="febrero-mayo 2014", cuadros={"vict": "Cuadro 4", "den": ("Cuadro 4", r"^Denunci"), "hp": "Cuadro 8",
                                               "hp_den": ("Cuadro 8", r"^Denuncia"), "ciudad": "Cuadro 19", "barrio": "Cuadro 21"}),
    dict(edicion=2015, ref=2014, archivo="anexos_ecsc_2015.xls", ruta="investigaciones/poblacion/convivencia/2015/anexos_ecsc_2015.xls",
         campo="abril-junio 2015", cuadros={"vict": "Cuadro 5", "den": ("Cuadro 5", r"^Denunci"), "hp": "Cuadro 9",
                                             "hp_den": ("Cuadro 9", r"^Denuncia"), "ciudad": "Cuadro 21", "barrio": "Cuadro 23"}),
    dict(edicion=2016, ref=2015, archivo="anexos_ecsc_2016.xls", ruta="investigaciones/poblacion/convivencia/2016/anexos_ecsc_2016.xls",
         campo="febrero-marzo 2016", cuadros={"vict": "Cuadro 5", "den": ("Cuadro 5", r"^Denunci"), "hp": "Cuadro 9",
                                               "hp_den": ("Cuadro 9", r"^Denuncia"), "ciudad": "Cuadro 21", "barrio": "Cuadro 23"}),
    dict(edicion=2017, ref=2016, archivo="anexos_ecsc_2017.xls", ruta="investigaciones/poblacion/convivencia/2017/anexos_ecsc_2017.xls",
         campo="abril-junio 2017", cuadros={"vict": "Cuadro 5", "den": ("Cuadro 5", r"^Denunci"), "hp": "Cuadro 9",
                                             "hp_den": ("Cuadro 9", r"^Denuncia"), "ciudad": "Cuadro 21", "barrio": "Cuadro 23"}),
    dict(edicion=2019, ref=2018, archivo="anexos_ecsc_2018.xls", ruta="investigaciones/poblacion/convivencia/2018/anexos_ecsc_2018.xls",
         campo="abril-junio 2019", cuadros={"vict": "Cuadro 5", "den": "Cuadro 7", "hp": "Cuadro 12",
                                             "hp_den": ("Cuadro 12", r"^Denuncia"), "ciudad": "Cuadro 24", "barrio": "Cuadro 26"}),
    dict(edicion=2020, ref=2019, archivo="anexos_ecsc_2019.xlsx", ruta="investigaciones/poblacion/convivencia/2019/anexos_ecsc_2019.xlsx",
         campo="agosto-octubre 2020 (aplazada por la pandemia)", cuadros={"vict": "Cuadro 5", "den": "Cuadro 7", "hp": "Cuadro 12",
                                                                          "hp_den": ("Cuadro 12", r"^Denuncia"), "ciudad": "Cuadro 24", "barrio": "Cuadro 26"}),
    dict(edicion=2021, ref=2020, archivo="anexos_ecsc_2020.xlsx", ruta="investigaciones/poblacion/convivencia/2020/anexos_ecsc_2020.xlsx",
         campo="junio-agosto 2021", cuadros={"vict": "Cuadro 5", "vict_isd": "Cuadro 6", "den": "Cuadro 9", "den_isd": "Cuadro 10",
                                              "hp": "Cuadro 15", "hp_den": ("Cuadro 15", r"^Denuncia"), "ciudad": "Cuadro 32", "barrio": "Cuadro 34 "}),
    dict(edicion=2022, ref=2021, archivo="anexos_ecsc_2021.xlsx", ruta="investigaciones/poblacion/convivencia/2021/anexos_ecsc_2021.xlsx",
         campo="septiembre-noviembre 2022", cuadros={"vict_isd": "Cuadro 5", "den_isd": "Cuadro 7", "hp": "Cuadro 12",
                                                      "hp_den": ("Cuadro 12", r"^Denuncia"), "ciudad": "Cuadro 32", "barrio": "Cuadro 34"}),
    dict(edicion=2024, ref=2023, archivo="anex-ECSC-2024.xlsx", ruta="operaciones/ECSC/anex-ECSC-2024.xlsx",
         campo="octubre-diciembre 2024; en Bogotá se extendió del 1 de marzo al 29 de abril de 2025",
         cuadros={"vict_isd": "Cuadro 5", "den_isd": "Cuadro 7", "hp": "Cuadro 12", "hp_den": ("Cuadro 12", r"^Denuncia"),
                  "ciudad": "Cuadro 32", "barrio": "Cuadro 34"}),
]

# clave -> (indicador, delito, población objetivo, el año es de referencia (True) o de percepción (False))
INDICADORES = {
    "vict": ("victimizacion", "cualquier_delito_sin_isd", POB15, True),
    "vict_isd": ("victimizacion", "cualquier_delito_con_isd", POB15, True),
    "den": ("tasa_denuncia", "cualquier_delito_sin_isd", POB_VICT, True),
    "den_isd": ("tasa_denuncia", "cualquier_delito_con_isd", POB_VICT, True),
    "hp": ("victimizacion", "hurto_personas", POB15, True),
    "hp_den": ("tasa_denuncia", "hurto_personas", POB_VICT_HP, True),
    "ciudad": ("percepcion_inseguridad_ciudad", "no_aplica", POB15, False),
    "barrio": ("percepcion_inseguridad_barrio", "no_aplica", POB15, False),
}

# Cifras del boletín ECSC 2024 (bol-ECSC-2024.pdf, gráficos 2, 4, 11 y 12) para verificar la extracción.
CONTROL_2024 = {"vict_isd": 14.7, "hp": 6.9, "den_isd": 43.1, "ciudad": 78.7}

DOCUMENTOS = {
    "ecsc_boletin_2024": (f"{DANE}/operaciones/ECSC/bol-ECSC-2024.pdf", ECSC_DIR / "bol-ECSC-2024.pdf"),
    "ecsc_metodologia": (f"{DANE}/operaciones/ECSC/met-ECSC.pdf", ECSC_DIR / "met-ECSC.pdf"),
    "ccb_epv_2025": ("https://assets.ctfassets.net/n1ptkpqt763u/4K3x5p5DuldDQiWajUfAHu/61a2b7a5a0392c06953d6dc6124baa03/"
                     "2026.02.16_EPV_2025_WEB.pdf", CCB_DIR / "2026.02.16_EPV_2025_WEB.pdf"),
    "ccb_epv_2024": ("https://www.valoraanalitik.com/wp-content/uploads/2025/06/Encuesta-de-Percepcion-y-Victimizacion-2024-VF-Bogota_.pdf",
                     CCB_DIR / "Encuesta-de-Percepcion-y-Victimizacion-2024-VF-Bogota_.pdf"),
}

# Registro de la Policía Nacional (SIEDCO) en datos.gov.co: id del conjunto -> códigos de la capa SCJ.
SIEDCO = {
    "HP": ("4rxi-8m8d", "Hurto a personas"), "HR": ("7mn7-vzqp", "Hurto a residencias"), "HC": ("7i2x-h5vp", "Hurto a comercio"),
    "HV": ("csb4-y6v2", "Hurto a vehículos"), "H": ("m8fd-ahd9", "Homicidios"), "LP": ("jr6v-i33g", "Lesiones personales"),
    "DS": ("bz43-8ahq", "Delitos sexuales"), "VI": ("gepp-dxcs", "Violencia intrafamiliar"),
}
INMLCF = {"definitivo": ("vtub-3de2", "a_o_del_hecho"), "preliminar": ("2kpj-cktv", "a_o_del_hecho")}
MESES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                      "septiembre", "octubre", "noviembre", "diciembre"], start=1)}


# ---------------------------------------------------------------- descargas

def _bajar(clave: str, url: str, ruta: Path, forzar: bool = False) -> Path:
    if ruta.exists() and not forzar:
        return ruta
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(_get(url).content)
    _registrar(clave, ruta, url)
    return ruta


def _socrata(clave: str, recurso: str, params: dict, ruta: Path, forzar: bool = False) -> pd.DataFrame:
    """Consulta agregada (SoQL) a datos.gov.co; guarda el resultado como CSV en la caché."""
    if ruta.exists() and not forzar:
        return pd.read_csv(ruta)
    url = f"{SOCRATA}/{recurso}.json?{urlencode({**params, '$limit': 50000})}"
    r = requests.get(url, headers=UA, timeout=(20, 300))
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")
    _registrar(clave, ruta, url)
    return df


def descargar(forzar: bool = False) -> None:
    for e in EDICIONES:
        _bajar(f"ecsc_{e['edicion']}", f"{DANE}/{e['ruta']}", ECSC_DIR / e["archivo"], forzar)
    for clave, (url, ruta) in DOCUMENTOS.items():
        _bajar(clave, url, ruta, forzar)


# ---------------------------------------------------------------- ECSC

def _celda(fila: int, col: int) -> str:
    letras, n = "", col + 1
    while n:
        n, r = divmod(n - 1, 26)
        letras = chr(65 + r) + letras
    return f"{letras}{fila + 1}"


def _num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return np.nan


def _bogota(x: pd.DataFrame, etiqueta: str | None = None) -> dict:
    """Porcentaje, cve y total (miles) de la fila Bogotá en el bloque pedido de un cuadro del anexo."""
    txt = np.array([["" if pd.isna(v) else str(v).strip() for v in fila] for fila in x.itertuples(index=False)], dtype=object)
    hdr = next(i for i in range(min(40, len(x))) if (txt[i] == "%").any())
    cols = [j for j in range(x.shape[1]) if txt[hdr, j] == "%"]
    if etiqueta is None:
        c = cols[0]
    else:
        marcas = [j for i in range(max(0, hdr - 3), hdr) for j in range(x.shape[1]) if re.match(etiqueta, txt[i, j])]
        if not marcas:
            raise ValueError(f"No encontré el bloque {etiqueta!r}")
        c = min(j for j in cols if j >= max(marcas))
    fila = next(i for i in range(hdr + 1, len(x)) if txt[i, 0].startswith("Bogot") or txt[i, 1].startswith("Bogot"))
    tiene_cve = txt[hdr, c + 1].lower() == "cve"
    tiene_total = txt[hdr, c - 1].lower() == "total"
    titulo = " ".join(t for t in txt[:12, 0] if t and not t.startswith("Encuesta de Convivencia"))
    return {"pct": _num(x.iat[fila, c]), "cve": _num(x.iat[fila, c + 1]) if tiene_cve else np.nan,
            "total": _num(x.iat[fila, c - 1]) if tiene_total else np.nan,
            "celda_pct": _celda(fila, c), "celda_cve": _celda(fila, c + 1) if tiene_cve else "",
            "celda_total": _celda(fila, c - 1) if tiene_total else "", "titulo": re.sub(r"\s+", " ", titulo)[:220]}


def _error(pct: float, cve: float) -> str:
    if np.isnan(cve):
        return "cve no publicado"
    return f"cve {cve:.2f} % | EE {pct * cve / 100:.2f} pp"


def _nota_edicion(e: dict, clave: str) -> str:
    n = [f"Edición {e['edicion']}; recolección {e['campo']}."]
    if e["ref"] == 2019 and clave in ("vict", "den", "hp", "hp_den"):
        n.append("Quiebre: primera edición recolectada en el segundo semestre del año siguiente (más tiempo para recordar).")
    if e["ref"] == 2023 and clave in ("vict_isd", "den_isd", "hp", "hp_den"):
        n.append("Recordación de 10 a 28 meses: preguntas sobre 2023 hechas entre oct-2024 y abr-2025.")
    if e["ref"] <= 2016 and clave in ("vict", "den", "hp", "hp_den"):
        n.append("Diseño de 28 ciudades (área urbana).")
    if e["ref"] == 2018 and clave in ("vict", "den"):
        n.append("En 2018 la lista de delitos incluye lesiones personales en vez de riñas y peleas.")
    return " ".join(n)


def extraer_ecsc() -> pd.DataFrame:
    filas = []
    for e in EDICIONES:
        ruta = ECSC_DIR / e["archivo"]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            hojas = pd.read_excel(ruta, sheet_name=None, header=None)
        for clave, spec in e["cuadros"].items():
            hoja, etiqueta = spec if isinstance(spec, tuple) else (spec, None)
            b = _bogota(hojas[hoja], etiqueta)
            indicador, delito, pob, es_ref = INDICADORES[clave]
            anio = e["ref"] if es_ref else e["edicion"]
            fuente = f"DANE ECSC {e['edicion']} | {e['archivo']} | {hoja.strip()} | {b['celda_pct']} (cve {b['celda_cve']})"
            nota = _nota_edicion(e, clave)
            if b["cve"] > 15:
                nota += " cve > 15 %: el DANE recomienda usarla solo como tendencia."
            filas.append(dict(anio=anio, fuente=fuente, indicador=indicador, delito=delito, valor=round(b["pct"], 3),
                              error_estandar_o_cv=_error(b["pct"], b["cve"]), poblacion_objetivo=pob, nota=nota,
                              _clave=clave, _edicion=e["edicion"], _cve=b["cve"], _titulo=b["titulo"]))
            if clave in ("hp", "hp_den"):  # el total expandido sirve para pasar de tasas a personas
                filas.append(dict(anio=anio, fuente=f"DANE ECSC {e['edicion']} | {e['archivo']} | {hoja.strip()} | {b['celda_total']}",
                                  indicador="victimas_miles" if clave == "hp" else "denunciantes_miles", delito="hurto_personas",
                                  valor=round(b["total"], 3), error_estandar_o_cv="cve del total no publicado",
                                  poblacion_objetivo="Miles de personas de 15 años y más (expandido), cabecera de Bogotá D.C.",
                                  nota=nota, _clave=clave + "_total", _edicion=e["edicion"], _cve=np.nan, _titulo=b["titulo"]))
    T = pd.DataFrame(filas)
    # Control de extracción contra el boletín publicado (cifras redondeadas a un decimal).
    for clave, esperado in CONTROL_2024.items():
        v = T.query("_edicion == 2024 and _clave == @clave")["valor"].iloc[0]
        assert abs(v - esperado) < 0.051, f"ECSC 2024 {clave}: {v} no coincide con el boletín ({esperado})"
    assert T.loc[~T._clave.str.endswith("_total"), "valor"].between(0, 100).all()
    return T


def transcritos() -> pd.DataFrame:
    """Cifras CCB transcritas a mano, más la victimización por hurto a personas que se deriva de ellas."""
    t = pd.read_csv(TRANSCRITOS)
    t["fuente"] = t.apply(lambda r: f"{r.fuente} | {r.documento} | {r.ubicacion}", axis=1)
    t["nota"] = ("transcrito. " + t["nota"].fillna("")).str.strip()
    base = t[["anio", "fuente", "indicador", "delito", "valor", "error_estandar_o_cv", "poblacion_objetivo", "nota"]].copy()
    v = t.query("indicador == 'victimizacion' and delito == 'cualquier_delito'").set_index("anio")["valor"]
    s = t.query("indicador == 'porcentaje_victimas_con_este_delito' and delito == 'hurto_personas'").set_index("anio")["valor"]
    deriv = [dict(anio=a, fuente="CCB EPV (cálculo propio) | 2026.02.16_EPV_2025_WEB.pdf | p. 6 × p. 8",
                  indicador="victimizacion", delito="hurto_personas", valor=round(v[a] * s[a] / 100, 2),
                  error_estandar_o_cv="no publicado", poblacion_objetivo="Personas de 18 años y más residentes en Bogotá",
                  nota="calculado: victimización por cualquier delito × % de víctimas que sufrieron hurto a personas (respuesta múltiple).")
             for a in s.index if a in v.index]
    return pd.concat([base, pd.DataFrame(deriv)], ignore_index=True)


# ---------------------------------------------------------------- registro administrativo

def registro(forzar: bool = False) -> pd.DataFrame:
    """Enero-agosto y año completo por delito: capa SCJ (proyecto), SIEDCO (datos.gov.co) e INMLCF."""
    filas = []
    for cod, (recurso, nombre) in SIEDCO.items():
        sel = "date_extract_y(fecha_hecho) as anio, date_extract_m(fecha_hecho) as mes, sum(cantidad) as casos"
        grp = "anio, mes"
        if cod == "HV":
            sel += ", tipo_delito"
            grp += ", tipo_delito"
        d = _socrata(f"siedco_{cod.lower()}_bogota", recurso, {"$select": sel, "$where": "cod_muni='11001'", "$group": grp},
                     VAL_DIR / f"siedco_{cod.lower()}_bogota_mensual.csv", forzar)
        d["casos"] = d["casos"].astype(float)
        d[["anio", "mes"]] = d[["anio", "mes"]].apply(pd.to_numeric)
        if cod == "HV":
            d["cod"] = np.where(d["tipo_delito"].str.contains("AUTOMOTORES"), "HA", "HM")
        else:
            d["cod"] = cod
        for c, g in d.groupby("cod"):
            for anio, h in g.groupby("anio"):
                filas += [dict(anio=int(anio), codigo=c, fuente="SIEDCO (Policía Nacional, datos.gov.co)", periodo="ene-ago",
                               casos=h.loc[h.mes <= 8, "casos"].sum(), meses=h.mes.nunique()),
                          dict(anio=int(anio), codigo=c, fuente="SIEDCO (Policía Nacional, datos.gov.co)", periodo="anio",
                               casos=h["casos"].sum(), meses=h.mes.nunique())]
    for clave, (recurso, campo) in INMLCF.items():
        where = "codigo_dane_municipio='11001'" + (" AND manera_de_muerte='1 Presuntos Homicidios'" if clave == "preliminar" else "")
        d = _socrata(f"inmlcf_homicidios_{clave}_bogota", recurso,
                     {"$select": f"{campo} as anio, mes_del_hecho as mes_txt, count(*) as casos", "$where": where, "$group": "anio, mes_txt"},
                     VAL_DIR / f"inmlcf_homicidios_{clave}_bogota_mensual.csv", forzar)
        d["mes"] = d["mes_txt"].astype(str).str.strip().str.lower().map(MESES)
        d["anio"] = pd.to_numeric(d["anio"])
        for anio, h in d.groupby("anio"):
            filas += [dict(anio=int(anio), codigo="H", fuente=f"INMLCF presuntos homicidios ({clave})", periodo="ene-ago",
                           casos=float(h.loc[h.mes <= 8, "casos"].astype(float).sum()), meses=h.mes.nunique()),
                      dict(anio=int(anio), codigo="H", fuente=f"INMLCF presuntos homicidios ({clave})", periodo="anio",
                           casos=float(h["casos"].astype(float).sum()), meses=h.mes.nunique())]
    # Capa SCJ cruda (la misma que usa el proyecto), sumando las 21 filas: 20 localidades más «Sin localización».
    # El procesado del proyecto deja fuera esa fila (3.889 hurtos a personas en 2025), así que aquí se usa el crudo.
    crudo = pd.read_csv(CRUDOS / "scj_delitos_alto_impacto_localidad.csv")
    cols = [c for c in crudo.columns if re.fullmatch(r"CM[A-Z]+?\d\dCONT", c)]
    scj = crudo[cols].apply(pd.to_numeric, errors="coerce").sum(min_count=1).rename("casos").reset_index()
    scj["codigo"] = scj["index"].str.extract(r"CM([A-Z]+?)\d\dCONT")[0]
    scj["anio"] = 2000 + scj["index"].str.extract(r"(\d\d)CONT")[0].astype(int)
    scj = scj.drop(columns="index").dropna(subset=["casos"]).assign(fuente="SCJ capa Delitos Alto Impacto", periodo="ene-ago", meses=8)
    R = pd.concat([pd.DataFrame(filas), scj], ignore_index=True)
    nombres = {**{k: v[1] for k, v in SIEDCO.items()}, "HA": "Hurto de automotores", "HM": "Hurto de motocicletas",
               "HB": "Hurto de bicicletas", "HCE": "Hurto de celulares"}
    R["delito"] = R["codigo"].map(nombres)
    R = R.query("anio >= 2015").copy()
    # Año en curso o con meses faltantes: se marca para no compararlo como año completo.
    R["completo"] = np.where(R.periodo == "anio", R.meses == 12, R.meses >= 8)
    return R[["anio", "codigo", "delito", "fuente", "periodo", "casos", "completo"]].sort_values(["codigo", "fuente", "periodo", "anio"])


# ---------------------------------------------------------------- análisis

def contraste(T: pd.DataFrame, indicador: str, delito: str, a: int, b: int) -> dict:
    """Diferencia b - a (pp) con prueba z de dos muestras independientes, usando los EE publicados."""
    def get(anio):
        r = T[(T.indicador == indicador) & (T.delito == delito) & (T.anio == anio) & T.fuente.str.startswith("DANE")]
        return float(r.valor.iloc[0]), float(r.valor.iloc[0]) * float(r._cve.iloc[0]) / 100
    (pa, ea), (pb, eb) = get(a), get(b)
    d, se = pb - pa, math.hypot(ea, eb)
    z = d / se
    p = math.erfc(abs(z) / math.sqrt(2))
    return dict(indicador=indicador, delito=delito, desde=a, hasta=b, valor_desde=pa, valor_hasta=pb, dif_pp=round(d, 2),
                ee_dif=round(se, 2), ic95=(round(d - 1.96 * se, 2), round(d + 1.96 * se, 2)), z=round(z, 2), p=round(p, 3))


def confiabilidad(T: pd.DataFrame) -> pd.DataFrame:
    hp = T.query("fuente.str.startswith('DANE') and delito == 'hurto_personas' and indicador in ['victimizacion', 'tasa_denuncia']")
    cves = f"cve {hp._cve.min():.1f}-{hp._cve.max():.1f} % (hurto a personas, Bogotá)"
    return pd.DataFrame([
        dict(fuente="Encuesta de Convivencia y Seguridad Ciudadana (ECSC)", entidad="DANE", frente="Lo que se vive",
             anios_cubiertos="2013-2016, 2018-2021, 2023 (año de referencia)", periodicidad="anual con huecos (sin 2017 ni 2022)",
             tipo="Encuesta probabilística de hogares", tamano_muestra_bogota="311 segmentos de unas 10 viviendas en la ronda 2024 (met-ECSC.pdf, tabla 1, p. 39); n de personas de Bogotá no publicado en los anexos",
             error_o_cv=cves, nivel_territorial="ciudad (cabecera)", ultima_actualizacion="2025-11-20 (anexo ECSC 2024, año de referencia 2023)",
             advertencia="Sin dato para 2022 ni 2024-2026; quiebre en 2019 (recolección pasa al semestre siguiente); recordación de 10-28 meses en 2023.",
             anios=4, ultimo=2023, precision="encuesta_250", territorio="ciudad", validez="directa"),
        dict(fuente="Encuesta de Percepción y Victimización (EPV)", entidad="Cámara de Comercio de Bogotá", frente="Lo que se vive",
             anios_cubiertos="2015-2025 (victimización); 2022-2025 (denuncia del hurto a personas)", periodicidad="anual",
             tipo="Encuesta presencial por muestreo estratificado multietápico", tamano_muestra_bogota="20.038 personas en 2025; 19.354 en 2024",
             error_o_cv="margen de error global 1,0 % (2025) y 0,7 % promedio (2024), 95 %; sin EE por indicador",
             nivel_territorial="localidad", ultima_actualizacion="2026-02-17 (EPV 2025)",
             advertencia="Universo 18+; pregunta por «este año» con campo en meses distintos; denuncia ponderada desde 2020; cifras leídas de gráficos.",
             anios=6, ultimo=2025, precision="encuesta_250", territorio="localidad", validez="directa"),
        dict(fuente="Delitos de alto impacto (capa CifrasSCJ, enero-agosto)", entidad="SCJ (OAIEE)", frente="Lo que se registra",
             anios_cubiertos="2018-2026 (enero-agosto)", periodicidad="anual (corte enero-agosto)", tipo="Registro administrativo procesado",
             tamano_muestra_bogota="universo de casos registrados", error_o_cv="no aplica (registro)", nivel_territorial="localidad",
             ultima_actualizacion="2026-08-31 (fecha de corte de la capa)",
             advertencia=("Quiebre en 2023: hurto a personas, residencias y automotores de 2018-2022 valen 2 a 3 veces lo que publica la Policía "
                          "(SIEDCO); desde 2023 coinciden. Homicidio, lesiones, delitos sexuales y VIF coinciden en todos los años (razón 1,00-1,09)."),
             anios=4, ultimo=2026, precision="universo", territorio="localidad", validez="sesgo"),
        dict(fuente="SIEDCO, delitos por municipio (datos.gov.co)", entidad="Policía Nacional / MinDefensa", frente="Lo que se registra",
             anios_cubiertos="2003-2026 (diario)", periodicidad="diaria, actualización mensual", tipo="Registro administrativo",
             tamano_muestra_bogota="universo de casos registrados", error_o_cv="no aplica (registro)", nivel_territorial="municipio",
             ultima_actualizacion="2026-09-16",
             advertencia="Solo lo denunciado (subregistro); año en curso preliminar; salto de nivel en 2017 en hurto a personas (×2).",
             anios=9, ultimo=2026, precision="universo", territorio="ciudad", validez="sesgo"),
        dict(fuente="Presuntos homicidios (necropsias)", entidad="Instituto Nacional de Medicina Legal (INMLCF)", frente="Validación externa",
             anios_cubiertos="2015-2024 definitivo; 2025-jul 2026 preliminar", periodicidad="anual definitiva, mensual preliminar",
             tipo="Registro forense", tamano_muestra_bogota="universo de casos con necropsia", error_o_cv="no aplica (registro)",
             nivel_territorial="localidad del hecho", ultima_actualizacion="2026-09-21 (preliminar); 2025-09-19 (definitivo)",
             advertencia="Valida homicidios, no hurtos; 2025-2026 preliminar.",
             anios=10, ultimo=2026, precision="universo", territorio="localidad", validez="directa"),
    ])


def main(forzar: bool = False) -> None:
    descargar(forzar)
    T = extraer_ecsc()
    C = transcritos()
    R = registro(forzar)
    cols = ["anio", "fuente", "indicador", "delito", "valor", "error_estandar_o_cv", "poblacion_objetivo", "nota"]
    S = pd.concat([T[cols], C[cols]], ignore_index=True).sort_values(["indicador", "delito", "anio", "fuente"])
    PROC.mkdir(parents=True, exist_ok=True)
    S.to_csv(PROC / "victimizacion_denuncia_bogota.csv", index=False, encoding="utf-8")
    R.to_csv(PROC / "registro_contraste_bogota.csv", index=False, encoding="utf-8")
    confiabilidad(T).to_csv(PROC / "confiabilidad_victimizacion.csv", index=False, encoding="utf-8")

    # Resumen para la nota
    pd.set_option("display.width", 200)
    print("\nTítulos de los cuadros leídos (control):")
    print(T.drop_duplicates(["_edicion", "_clave"])[["_edicion", "_clave", "_titulo"]].to_string(index=False, max_colwidth=110))
    piv = T[~T._clave.str.endswith("_total")].pivot_table(index="anio", columns=["indicador", "delito"], values="valor")
    print("\nECSC, Bogotá:\n", piv.round(2).to_string())
    print("\nContrastes ECSC (Bogotá):")
    for args in [("victimizacion", "hurto_personas", 2021, 2023), ("tasa_denuncia", "hurto_personas", 2021, 2023),
                 ("victimizacion", "cualquier_delito_con_isd", 2021, 2023), ("tasa_denuncia", "cualquier_delito_con_isd", 2021, 2023),
                 ("victimizacion", "hurto_personas", 2018, 2019), ("victimizacion", "hurto_personas", 2019, 2021),
                 ("tasa_denuncia", "hurto_personas", 2018, 2023)]:
        print("  ", contraste(T, *args))
    w = R.pivot_table(index="anio", columns=["codigo", "fuente", "periodo"], values="casos")
    hp = pd.DataFrame({"SCJ ene-ago": w[("HP", "SCJ capa Delitos Alto Impacto", "ene-ago")],
                       "SIEDCO ene-ago": w[("HP", "SIEDCO (Policía Nacional, datos.gov.co)", "ene-ago")],
                       "SIEDCO año": w[("HP", "SIEDCO (Policía Nacional, datos.gov.co)", "anio")]})
    hp["SCJ/SIEDCO"] = hp["SCJ ene-ago"] / hp["SIEDCO ene-ago"]
    print("\nHurto a personas, registro:\n", hp.round(2).to_string())
    razones = {c: (w[(c, "SCJ capa Delitos Alto Impacto", "ene-ago")]
                   / w[(c, "SIEDCO (Policía Nacional, datos.gov.co)", "ene-ago")]).round(2) for c in ["HP", "HR", "HA", "HM", "HC", "H", "LP", "DS", "VI"]}
    print("\nRazón SCJ / SIEDCO (enero-agosto):\n", pd.DataFrame(razones).to_string())
    h = pd.DataFrame({"SCJ": w[("H", "SCJ capa Delitos Alto Impacto", "ene-ago")],
                      "SIEDCO": w[("H", "SIEDCO (Policía Nacional, datos.gov.co)", "ene-ago")],
                      "INMLCF def": w.get(("H", "INMLCF presuntos homicidios (definitivo)", "ene-ago")),
                      "INMLCF prel": w.get(("H", "INMLCF presuntos homicidios (preliminar)", "ene-ago"))})
    print("\nHomicidios enero-agosto:\n", h.to_string())
    pob = pd.read_csv(PROC / "sdp_poblacion_localidad_grupos.csv").query("grupo == 'total'").groupby("anio")["personas"].sum()
    ha = R.query("codigo == 'H' and periodo == 'anio' and completo").pivot_table(index="anio", columns="fuente", values="casos")
    ha = ha.assign(INMLCF=ha.filter(like="INMLCF").sum(axis=1, min_count=1)).drop(columns=list(ha.filter(like="INMLCF (").columns))
    tasas = ha[["SIEDCO (Policía Nacional, datos.gov.co)", "INMLCF"]].div(pob, axis=0).mul(1e5).dropna(how="all").round(1)
    print("\nHomicidios por 100.000 habitantes, año completo (población SDP):\n", tasas.to_string())

    # Cambios clave: registro frente a encuestas
    def var(a, b):
        return f"{100 * (b / a - 1):+.1f} %"
    scj, sie = hp["SCJ ene-ago"], hp["SIEDCO ene-ago"]
    print("\nHurto a personas, enero-agosto (SCJ | SIEDCO):")
    for a, b in [(2022, 2026), (2022, 2023), (2021, 2023), (2023, 2025), (2023, 2026), (2022, 2025)]:
        print(f"   {a}->{b}: SCJ {var(scj[a], scj[b])} | SIEDCO {var(sie[a], sie[b])}")
    e = T[T._clave.isin(["hp_total", "hp_den_total"])].pivot_table(index="anio", columns="indicador", values="valor")
    print("\nECSC, miles de personas (víctimas y denunciantes de hurto a personas):\n", e.round(1).to_string())
    # Razón 2023/2021 de personas con IC 95 % aproximado: método delta en logaritmos, con el cv de cada total
    # aproximado por la raíz de la suma de los cv² de los porcentajes que lo forman (sin covarianza ni error
    # de la proyección de población). Se compara con la razón del registro en el mismo intervalo.
    def cv(anio, clave):
        return T[(T._clave == clave) & (T.anio == anio)]["_cve"].iloc[0] / 100
    reg = {"SCJ ene-ago": scj[2023] / scj[2021], "SIEDCO ene-ago": sie[2023] / sie[2021],
           "SIEDCO año": hp.loc[2023, "SIEDCO año"] / hp.loc[2021, "SIEDCO año"]}
    for nombre, col, claves in [("víctimas", "victimas_miles", ["hp"]), ("denunciantes", "denunciantes_miles", ["hp", "hp_den"])]:
        razon = e.loc[2023, col] / e.loc[2021, col]
        se = math.sqrt(sum(cv(a, k) ** 2 for a in (2021, 2023) for k in claves))
        lo, hi = razon * math.exp(-1.96 * se), razon * math.exp(1.96 * se)
        print(f"   2021->2023 ECSC {nombre}: razón {razon:.3f} (IC95 {lo:.2f}-{hi:.2f}); registro: "
              + ", ".join(f"{k} {v:.3f}{'' if lo <= v <= hi else ' (fuera del IC)'}" for k, v in reg.items()))
    req = (T[(T._clave == "hp_den") & (T.anio == 2021)].valor.iloc[0] * reg["SCJ ene-ago"]
           * e.loc[2021, "victimas_miles"] / e.loc[2023, "victimas_miles"])
    den23 = T[(T._clave == "hp_den") & (T.anio == 2023)]
    print(f"   Denuncia del hurto que haría falta en 2023 para explicar la caída SCJ 2021->2023: {req:.1f} % "
          f"(ECSC 2023: {den23.valor.iloc[0]:.1f} %, EE {den23.valor.iloc[0] * den23._cve.iloc[0] / 100:.2f} pp)")
    ccb = C[C.fuente.str.startswith("CCB")].pivot_table(index="anio", columns=["indicador", "delito"], values="valor")
    vic, den = ccb[("victimizacion", "hurto_personas")], ccb[("tasa_denuncia", "hurto_personas")]
    prod = (vic * den / 100).dropna()
    print("\nCCB: victimización por hurto a personas (calculada), denuncia del hurto y su producto:\n",
          pd.DataFrame({"vict_hp": vic, "den_hp": den, "vict_x_den": prod}).dropna(how="all").round(2).to_string())
    for a, b in [(2022, 2023), (2023, 2025), (2022, 2025)]:
        print(f"   {a}->{b}: vict_hp {var(vic[a], vic[b])}, denuncia {den[b] - den[a]:+.1f} pp, producto {var(prod[a], prod[b])}")
    print(f"\nEscrito: {PROC / 'victimizacion_denuncia_bogota.csv'} ({len(S)} filas), registro_contraste_bogota.csv, confiabilidad_victimizacion.csv")


if __name__ == "__main__":
    main(forzar="--forzar" in sys.argv)
