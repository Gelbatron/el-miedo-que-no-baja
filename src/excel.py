"""
Libro de datos en Excel de la entrega (Bogotá DataJam 5 · equipo #16 The data squad).

    python src/excel.py              escribe docs/Libro_de_datos_El_miedo_que_no_baja.xlsx
    python src/excel.py --sin-excel  igual, pero sin abrir Excel para guardar los valores calculados

Lee solo salidas del pipeline (outputs/ y data/procesados/): no vuelve a estimar modelos ni
inventa cifras. Lo que depende de otras celdas queda como fórmula viva: el simulador, el Índice
de Brecha (recalculado desde sus dos componentes), la cifra oculta de Bogotá, el ρ de Spearman
sobre puestos y el índice 2018 = 100.

En Windows con Excel instalado, el libro se abre una vez en Excel (invisible) para recalcular y
guardar: así las fórmulas llevan su valor también para visores que no calculan (vista previa,
pandas, Power BI). Sin Excel, el libro se recalcula al abrirlo.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference, ScatterChart, Series
from openpyxl.chart.axis import ChartLines
from openpyxl.chart.data_source import NumDataSource, NumFmt, NumRef, StrRef
from openpyxl.chart.error_bar import ErrorBars
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.marker import DataPoint
from openpyxl.chart.series import SeriesLabel
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText
from openpyxl.comments import Comment
from openpyxl.drawing.colors import ColorChoice
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties
from openpyxl.drawing.text import Font as FuenteDibujo
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.pagebreak import Break
from openpyxl.worksheet.table import Table, TableStyleInfo

sys.path.insert(0, str(Path(__file__).parent))
from fuentes import FUENTES  # noqa: E402
from pipeline import CALIFICACIONES, DELITO, ETIQUETAS, HECHOS, PERFIL  # noqa: E402
from territorio import LOCALIDADES  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "outputs"
TAB = OUT / "tablas"
PROC = RAIZ / "data" / "procesados"
DESTINO = RAIZ / "docs" / "Libro_de_datos_El_miedo_que_no_baja.xlsx"

EQUIPO = ["Rafael Estiven Londoño Camacho", "Brandow Brusly León Rodríguez", "Samuel Esteban Riveros Cubides"]
PREGUNTA = ("¿Por qué la inseguridad percibida no baja cuando el delito registrado sí, "
            "y en qué territorios debe intervenir primero el Distrito?")

# ---------------------------------------------------------------- identidad visual (paleta del Distrito)
ROJO, VINO = "BF0A00", "AB0F24"
ORO, ORO1, ORO2, ORO3 = "D99A16", "FFF5DB", "FADD95", "F0BF4F"
AZUL, AZUL1, AZUL2, AZUL3 = "3366CC", "DDE7F8", "A9C1EE", "6D95E0"
GRIS, TINTA = "4B4B4B", "1E1E1E"
MUJER, HOMBRE = "8E44C8", "2A9D4B"
LINEA, FONDO, GRIS_NS, GRIS_CERO, BLANCO = "E3E3E3", "F6F6F6", "A6A6A6", "EDEDED", "FFFFFF"
LETRA = "Segoe UI"

# formatos de número
PCT = "0.0%"
PP = '+0.0" pp";"−"0.0" pp";0.0" pp"'
PP2 = '+0.00" pp";"−"0.00" pp";0.00" pp"'
ENT = "#,##0"
DEC1 = "#,##0.0"
DEC2 = "0.00"
DEC3 = "0.000"
SIG2 = '+0.00;"−"0.00;0.00'
VAR = '+0.0%;"−"0.0%;0.0%'
TXT, CEN = "txt", "cen"  # marcas de alineación para texto

BLOQUE = {**{v: "Perfil" for v in PERFIL}, **{v: "Delito registrado" for v in DELITO},
          **{v: "Hechos del entorno" for v in HECHOS}, **{v: "Calificación del entorno" for v in CALIFICACIONES},
          "victima": "Victimización"}

HOJAS = [
    ("Portada", "Portada, pregunta y contenido"),
    ("Resumen", "Cifras clave y los tres hallazgos"),
    ("Panel_localidad", "Las 19 localidades urbanas: percepción, entorno, victimización, registro y contexto"),
    ("Indice_brecha", "Ranking del Índice de Brecha de Seguridad con intervalo bootstrap de 90 %"),
    ("Cifra_oculta", "Víctimas por delito registrado y validaciones territoriales"),
    ("Modelos", "Efectos marginales del logit ponderado, robustez y capacidad predictiva (AUC)"),
    ("Genero", "Mujeres frente a hombres a igual edad, estrato y victimización"),
    ("Serie_delitos", "Delitos registrados 2018-2026 (enero-agosto) e índice 2018 = 100"),
    ("Simulador", "Escenarios de alumbrado y parques sin atracos con fórmulas vivas"),
    ("Diccionario", "Definición, unidad, fuente y año de cada indicador y variable"),
    ("Fuentes", "Entidades, conjuntos de datos y enlaces oficiales"),
    ("Bitacora", "Bitácora de limpieza e integración de cada fuente"),
    ("Datos_escenarios", "Probabilidades del modelo que alimentan el simulador"),
]
COLOR_PESTANA = {"Portada": ROJO, "Resumen": ROJO, "Simulador": ORO, "Datos_escenarios": "BFBFBF",
                 "Diccionario": GRIS, "Fuentes": GRIS, "Bitacora": GRIS}


# ---------------------------------------------------------------- utilidades de texto
def es(x: float, d: int = 1) -> str:
    """Número con formato español (coma decimal, punto de miles)."""
    return f"{x:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def signo(x: float, d: int = 1) -> str:
    return ("+" if x >= 0 else "−") + es(abs(x), d)


# ---------------------------------------------------------------- utilidades de estilo
_FUENTES: dict = {}


def F(size=10, bold=False, color=TINTA, italic=False, underline=None) -> Font:
    k = (size, bold, color, italic, underline)
    if k not in _FUENTES:
        _FUENTES[k] = Font(name=LETRA, size=size, bold=bold, color=color, italic=italic, underline=underline)
    return _FUENTES[k]


def relleno(color: str) -> PatternFill:
    return PatternFill("solid", fgColor=color)


FINA = Side(style="thin", color=LINEA)


def poner(ws, fila, col, valor=None, *, size=10, bold=False, color=TINTA, italic=False, fmt=None,
          h=None, v="center", wrap=False, fondo=None, indent=0):
    c = ws.cell(fila, col)
    if valor is not None:
        c.value = valor
    c.font = F(size, bold, color, italic)
    c.alignment = Alignment(horizontal=h, vertical=v, wrap_text=wrap, indent=indent)
    if fmt:
        c.number_format = fmt
    if fondo:
        c.fill = relleno(fondo)
    return c


def anchos(ws, valores: dict):
    for col, w in valores.items():
        ws.column_dimensions[col].width = w


def _ancho(ws, c1, c2) -> float:
    return sum(ws.column_dimensions[L(c)].width or 8.43 for c in range(c1, c2 + 1))


def cm(ws, c1, c2) -> float:
    """Ancho en centímetros de las columnas c1..c2 (≈ 7 px por unidad + 5 px de margen, 96 ppp)."""
    return sum((ws.column_dimensions[L(c)].width or 8.43) * 7 + 5 for c in range(c1, c2 + 1)) / 37.8


def _alto(txt, ancho, size) -> float:
    """Alto de fila (pt) para texto envuelto: Segoe UI ocupa ≈ 0,615 × tamaño px por carácter."""
    por_linea = max(8.0, (ancho * 7.2 - 14) / (0.615 * size) * 0.9)
    lineas = sum(max(1, math.ceil(len(p) / por_linea)) for p in str(txt).split("\n"))
    return round(lineas * size * 1.36 + 8, 1)


def texto(ws, fila, c1, c2, valor, *, size=10, alto=None, fondo=None, v="top", **kw):
    """Texto largo en celdas combinadas, con alto de fila estimado."""
    if c2 > c1:
        ws.merge_cells(start_row=fila, start_column=c1, end_row=fila, end_column=c2)
    c = poner(ws, fila, c1, valor, size=size, wrap=True, v=v, fondo=fondo, **kw)
    if fondo:
        for col in range(c1 + 1, c2 + 1):
            ws.cell(fila, col).fill = relleno(fondo)
    ws.row_dimensions[fila].height = alto or _alto(valor, _ancho(ws, c1, c2), size)
    return c


def vinculo(c, hoja: str, celda: str = "A1"):
    c.hyperlink = Hyperlink(ref=c.coordinate, location=f"'{hoja}'!{celda}", display=str(c.value))


def cabecera(ws, titulo: str, subtitulo: str, ultima: int):
    """Encabezado común: antetítulo, título, subtítulo, filete rojo y vínculo a la portada."""
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 90
    ws.column_dimensions["A"].width = 2.5
    if ultima - 1 > 2:
        ws.merge_cells(start_row=1, start_column=2, end_row=1, end_column=ultima - 1)
    poner(ws, 1, 2, "EL MIEDO QUE NO BAJA  ·  BOGOTÁ DATAJAM 5  ·  THE DATA SQUAD", size=8, bold=True, color=VINO, v="bottom")
    poner(ws, 2, 2, titulo, size=18, bold=True, color=ROJO, v="center")
    poner(ws, 3, 2, subtitulo, size=10, color=GRIS, v="top")
    if ws.title != "Portada":
        c = poner(ws, 1, ultima, "← Portada", size=8, color=AZUL, h="right", v="bottom")
        c.font = F(8, False, AZUL, underline="single")
        vinculo(c, "Portada")
    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 30
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 3
    ws.row_dimensions[5].height = 10
    for col in range(2, ultima + 1):
        ws.cell(4, col).fill = relleno(ROJO)


def seccion(ws, fila, col, titulo, detalle=None, ultima=None):
    poner(ws, fila, col, titulo, size=11.5, bold=True, color=TINTA, v="bottom")
    ws.row_dimensions[fila].height = 24
    if detalle:
        texto(ws, fila + 1, col, ultima or col, detalle, size=9, color=GRIS, v="top")
        return fila + 2
    return fila + 1


def encabezados(ws, fila, col, textos, fondo=VINO, alto=34):
    for i, t in enumerate(textos):
        c = ws.cell(fila, col + i, t)
        c.font = F(9, True, BLANCO)
        c.fill = relleno(fondo)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[fila].height = alto


def fila_datos(ws, fila, col, valores, formatos, *, bold=False, alto=19, fondo=None, color=TINTA, size=9.5):
    for i, (val, fmt) in enumerate(zip(valores, formatos)):
        c = ws.cell(fila, col + i)
        if val is not None:
            c.value = val
        c.font = F(size, bold, color)
        if fmt == TXT:
            c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        elif fmt == CEN:
            c.alignment = Alignment(horizontal="center", vertical="center")
        else:
            c.alignment = Alignment(horizontal="right", vertical="center", indent=1)
            c.number_format = fmt
        c.border = Border(bottom=FINA)
        if fondo:
            c.fill = relleno(fondo)
    ws.row_dimensions[fila].height = alto


def tabla_excel(ws, nombre, ref, franjas=False):
    t = Table(displayName=nombre, ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=franjas, showColumnStripes=False,
                                      showFirstColumn=False, showLastColumn=False)
    ws.add_table(t)


def gris_si_no_significativo(ws, rango, col_inf, col_sup, fila0):
    regla = FormulaRule(formula=[f"AND(${col_inf}{fila0}<0,${col_sup}{fila0}>0)"], font=Font(name=LETRA, color=GRIS_NS))
    ws.conditional_formatting.add(rango, regla)


def salto(ws, fila):
    """Salto de página manual: la fila indicada empieza una página nueva al imprimir."""
    ws.row_breaks.append(Break(id=fila - 1))


def imprimir(ws, area=None, titulos=None, vertical=False, paginas=0):
    """Carta, ajustado al ancho; `paginas` > 0 fija además el número de páginas de alto."""
    ws.page_setup.orientation = "portrait" if vertical else "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = paginas
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.45, bottom=0.6, header=0.2, footer=0.3)
    ws.oddFooter.left.text = "El miedo que no baja · The data squad · Bogotá DataJam 5"
    ws.oddFooter.left.size = 7
    ws.oddFooter.left.color = GRIS
    ws.oddFooter.right.text = "&A · &P de &N"
    ws.oddFooter.right.size = 7
    ws.oddFooter.right.color = GRIS
    if area:
        ws.print_area = area
    if titulos:
        ws.print_title_rows = titulos


# ---------------------------------------------------------------- utilidades de gráficos
def _rt(size=9, color=GRIS, bold=False) -> RichText:
    cp = CharacterProperties(sz=int(size * 100), b=bold, solidFill=ColorChoice(srgbClr=color),
                             latin=FuenteDibujo(typeface=LETRA))
    return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])


def _linea(color, ancho_pt=0.75) -> LineProperties:
    return LineProperties(solidFill=color, w=int(ancho_pt * 12700))


def grafico_base(ch, ancho_cm, alto_cm, leyenda=None):
    ch.width, ch.height = ancho_cm, alto_cm
    ch.title = None
    ch.roundedCorners = False
    ch.graphical_properties = GraphicalProperties(ln=LineProperties(noFill=True))
    if leyenda:
        ch.legend.position = leyenda
        ch.legend.overlay = False
        ch.legend.txPr = _rt(9, TINTA)
    else:
        ch.legend = None
    for ax in (ch.x_axis, ch.y_axis):
        ax.delete = False
        ax.txPr = _rt(9, GRIS)
        ax.majorTickMark = "none"
        ax.minorTickMark = "none"
    ch.x_axis.spPr = GraphicalProperties(ln=_linea("BFBFBF"))
    ch.y_axis.spPr = GraphicalProperties(ln=LineProperties(noFill=True))
    ch.y_axis.majorGridlines = ChartLines(spPr=GraphicalProperties(ln=_linea(LINEA, 0.5)))
    return ch


def color_serie(s, color):
    s.graphicalProperties = GraphicalProperties(solidFill=color, ln=LineProperties(noFill=True))


def colores_por_punto(s, colores):
    for i, color in enumerate(colores):
        pt = DataPoint(idx=i, invertIfNegative=False)
        pt.graphicalProperties = GraphicalProperties(solidFill=color, ln=LineProperties(noFill=True))
        s.dPt.append(pt)


def etiquetas(s, fmt, size=8.5, color=TINTA, posicion=None):
    d = DataLabelList()
    d.showVal = True
    for a in ("showLegendKey", "showCatName", "showSerName", "showPercent", "showBubbleSize"):
        setattr(d, a, False)
    d.numFmt = fmt
    d.txPr = _rt(size, color)
    if posicion:
        d.position = posicion
    s.dLbls = d


def barras_error(s, hoja, rango_mas, rango_menos, color=GRIS):
    s.errBars = ErrorBars(
        errBarType="both", errValType="cust", noEndCap=False,
        plus=NumDataSource(numRef=NumRef(f=f"'{hoja}'!{rango_mas}")),
        minus=NumDataSource(numRef=NumRef(f=f"'{hoja}'!{rango_menos}")),
        spPr=GraphicalProperties(ln=_linea(color, 1)))


def barras_horizontales(ancho_cm, alto_cm, fmt_eje):
    ch = grafico_base(BarChart(), ancho_cm, alto_cm)
    ch.type = "bar"
    ch.gapWidth = 45
    ch.x_axis.scaling.orientation = "maxMin"   # el primero de la tabla arriba
    ch.x_axis.tickLblPos = "low"               # nombres a la izquierda aunque haya negativos
    ch.y_axis.crosses = "max"                  # eje de valores abajo
    ch.y_axis.numFmt = NumFmt(formatCode=fmt_eje, sourceLinked=False)
    return ch


# ---------------------------------------------------------------- datos
def cargar() -> dict:
    d = {"res": json.loads((OUT / "resultados.json").read_text(encoding="utf-8")),
         "panel": pd.read_csv(PROC / "panel_localidad_2025.csv"),
         "delitos": pd.read_csv(PROC / "scj_delitos_localidad_largo.csv")}
    import validacion_registro as VR  # serie validada: SIEDCO donde la capa SCJ tiene quiebre
    d["serie"] = VR.serie_bogota_validada(d["delitos"])
    d["hurto"] = pd.read_csv(TAB / "registro_hurto_personas.csv")
    for n in ["ibs", "cifra_oculta", "m_hechos", "m_calif", "m_ciudad", "m_miedo", "m_efectos_fijos", "lpm_wild",
              "auc", "emv_no_sale_noche", "emv_teme_acoso_sexual", "emv_barrio_inseguro", "escenarios",
              "validaciones", "bitacora_limpieza"]:
        d[n] = pd.read_csv(TAB / f"{n}.csv")
    return d


# ================================================================ hojas
def hoja_datos_escenarios(ws, D, R):
    cabecera(ws, "Datos del simulador", "Probabilidad media predicha de sentir insegura la zona (logit ponderado, "
             "Bienal 2025), por grupo y localidad. Código 0 = Bogotá. Alimenta la hoja Simulador.", 9)
    anchos(ws, {"B": 11, "C": 9, "D": 22, "E": 13, "F": 15, "G": 15, "H": 14, "I": 14})
    cols = ["Grupo", "Código", "Localidad", "Hoy (p00)", "Alumbrado resuelto (p10)", "Parques sin atracos (p01)",
            "Ambas palancas (p11)", "Observado (Bienal 2025)"]
    f0 = 7
    encabezados(ws, f0, 2, cols, alto=40)
    e = D["escenarios"].copy()
    e["orden_g"] = e["grupo"].map({"total": 0, "mujeres": 1, "hombres": 2})
    e = e.sort_values(["orden_g", "localidad"])
    for i, r in enumerate(e.itertuples(), start=1):
        nombre = "Bogotá" if r.localidad == 0 else LOCALIDADES[r.localidad]
        fila_datos(ws, f0 + i, 2, [r.grupo.capitalize(), int(r.localidad), nombre, r.p00 / 100, r.p10 / 100,
                                   r.p01 / 100, r.p11 / 100, r.observado / 100],
                   [TXT, CEN, TXT, PCT, PCT, PCT, PCT, PCT], bold=r.localidad == 0)
    ultima = f0 + len(e)
    tabla_excel(ws, "tEscenarios", f"B{f0}:I{ultima}")
    ws.freeze_panes = f"B{f0 + 1}"
    texto(ws, ultima + 2, 2, 9, "Fuente: outputs/tablas/escenarios.csv (modelo con perfil, delito registrado, hechos "
          "del entorno y alumbrado malo). p10 = alumbrado deja de ser malo para todos; p01 = nadie ve atracos en su "
          "parque; p11 = ambas. Valores fijos: no editar.", size=8.5, color=GRIS, italic=True)
    R["esc"] = {"f0": f0 + 1, "f1": ultima}
    imprimir(ws, titulos=f"{f0}:{f0}", vertical=True)


def hoja_panel(ws, D, R):
    P = D["panel"].sort_values("localidad")
    grupos = [
        ("Identificación", FONDO, GRIS, [("localidad", "Código", CEN, 1), ("nombre", "Localidad", TXT, 1),
                                         ("poblacion", "Población 2025 (hab.)", ENT, 1)]),
        ("Percepción · Bienal 2025", ORO1, ORO, [
            ("zona_insegura", "Zona insegura (%)", PCT, 100), ("ciudad_insegura", "Ciudad insegura (%)", PCT, 100),
            ("ciudad_peor_que_antes", "Ciudad peor que antes (%)", PCT, 100),
            ("miedo_espacio_publico", "Miedo en el espacio público (%)", PCT, 100)]),
        ("Entorno · Bienal 2025", ORO1, ORO, [
            ("alumbrado_malo", "Alumbrado malo (%)", PCT, 100), ("parque_spa", "Drogas en el parque (%)", PCT, 100),
            ("parque_acoso", "Acoso en el parque (%)", PCT, 100),
            ("presencio_acoso", "Presenció acoso a mujeres (%)", PCT, 100)]),
        ("Victimización y autoprotección · EMV 2024", ORO1, ORO, [
            ("emv_victima", "Víctima de un delito, último año (%)", PCT, 100),
            ("emv_barrio_inseguro", "Barrio inseguro (%)", PCT, 100),
            ("emv_no_sale_noche", "No sale de noche (%)", PCT, 100),
            ("emv_teme_acoso_sexual", "Teme acoso sexual (%)", PCT, 100)]),
        ("Registro · SCJ, enero-agosto 2025", AZUL1, AZUL, [
            ("delitos_alto_impacto_100k", "Delitos de alto impacto (por 100.000 hab.)", ENT, 1),
            ("hurtos_100k", "Hurtos (por 100.000 hab.)", ENT, 1),
            ("homicidios_100k", "Homicidios (por 100.000 hab.)", DEC1, 1),
            ("vif_ds_100k_mujeres", "VIF y delitos sexuales (por 100.000 mujeres)", ENT, 1),
            ("incidentes_narcoticos_100k", "Llamadas 123 por narcóticos (por 100.000 hab.)", ENT, 1),
            ("incidentes_rinas_100k", "Llamadas 123 por riñas (por 100.000 hab.)", ENT, 1),
            ("incidentes_maltrato_mujer_100k", "Llamadas 123 por maltrato a mujer (por 100.000 hab.)", ENT, 1)]),
        ("Contexto", FONDO, GRIS, [("area_km2", "Área (km²)", DEC1, 1),
                                   ("luminarias_km2_2019", "Luminarias por km² (UAESP 2019)", ENT, 1),
                                   ("ep_efectivo_m2_hab", "Espacio público efectivo (m²/hab.)", DEC1, 1)]),
    ]
    columnas = [c for g in grupos for c in g[3]]
    ultima = 1 + len(columnas)
    cabecera(ws, "Panel por localidad", "Una fila por localidad urbana (19). Percepción y entorno: % ponderado de "
             "adultos. Registro: tasas por 100.000 habitantes con población SDP 2025.", ultima)
    ws.column_dimensions["B"].width = 8
    ws.column_dimensions["C"].width = 20
    for c in range(4, ultima + 1):
        ws.column_dimensions[L(c)].width = 12.5
    fb, fh = 6, 7
    col = 2
    for nombre, fondo, acento, cs in grupos:
        c2 = col + len(cs) - 1
        if c2 > col:
            ws.merge_cells(start_row=fb, start_column=col, end_row=fb, end_column=c2)
        poner(ws, fb, col, nombre, size=8.5, bold=True, color=TINTA, h="center", fondo=fondo)
        for cc in range(col, c2 + 1):
            ws.cell(fb, cc).fill = relleno(fondo)
            ws.cell(fb, cc).border = Border(bottom=Side(style="medium", color=acento))
        col = c2 + 1
    ws.row_dimensions[fb].height = 22
    encabezados(ws, fh, 2, [c[1] for c in columnas], alto=62)
    for i, r in enumerate(P.itertuples(), start=1):
        vals = [getattr(r, k) / div if div != 1 else getattr(r, k) for k, _, _, div in columnas]
        vals[0] = int(vals[0])
        fila_datos(ws, fh + i, 2, vals, [c[2] for c in columnas])
    f0, f1 = fh + 1, fh + len(P)
    tabla_excel(ws, "tPanelLocalidad", f"B{fh}:{L(ultima)}{f1}")
    # formato condicional: oro para percepción, entorno y victimización; azul para registro
    col = 2
    for nombre, _, acento, cs in grupos:
        for k, _, _, _ in cs:
            rango = f"{L(col)}{f0}:{L(col)}{f1}"
            if acento == ORO:
                ws.conditional_formatting.add(rango, ColorScaleRule(
                    start_type="min", start_color=ORO1, mid_type="percentile", mid_value=50, mid_color=ORO2,
                    end_type="max", end_color=ORO3))
            elif acento == AZUL:
                ws.conditional_formatting.add(rango, ColorScaleRule(
                    start_type="min", start_color=AZUL1, mid_type="percentile", mid_value=50, mid_color=AZUL2,
                    end_type="max", end_color=AZUL3))
            elif k == "poblacion":
                ws.conditional_formatting.add(rango, DataBarRule(start_type="num", start_value=0, end_type="max",
                                                                 color="C9C9C9", showValue=True, minLength=0,
                                                                 maxLength=100))
            col += 1
    ws.freeze_panes = f"D{f0}"
    n = f1 + 2
    texto(ws, n, 2, 14, "Lectura: más intenso = valor más alto entre las 19 localidades (cada columna con su propia "
          "escala). Oro: lo que la gente percibe o vive (encuestas). Azul: lo que registran las autoridades. "
          "Las tasas de 2025 usan el corte enero-agosto que publica la SCJ, comparable entre años.",
          size=8.5, color=GRIS, italic=True)
    texto(ws, n + 1, 2, 14, "Fuentes: Encuesta Bienal de Cultura Ciudadana 2025 (SCRD), Encuesta Mundial de Valores "
          "ola 8 2024 (Datos para la Transparencia), SCJ (delito de alto impacto y Línea 123), SDP (población), "
          "UAESP (alumbrado 2019), DADEP (espacio público), IDECA (área). Archivo: "
          "data/procesados/panel_localidad_2025.csv. Definiciones en la hoja Diccionario.",
          size=8.5, color=GRIS, italic=True)
    R["panel"] = {"f0": f0, "f1": f1, "col": {k: L(2 + i) for i, (k, _, _, _) in enumerate(columnas)}}
    imprimir(ws, titulos=f"{fb}:{fh}")


def hoja_indice(ws, D, R):
    cabecera(ws, "Índice de Brecha de Seguridad", "Dónde hay más miedo del que explica el delito registrado. "
             "IBS = z(% zona insegura) − z(ln delitos de alto impacto por 100.000).", 15)
    anchos(ws, {"B": 8, "C": 8, "D": 20, "E": 11, "F": 13, "G": 10, "H": 11, "I": 11, "J": 10, "K": 11, "L": 11,
                "M": 12, "N": 11, "O": 30, "P": 3, "Q": 10, "R": 10})
    ib = D["ibs"].sort_values("ibs", ascending=False).reset_index(drop=True)
    fh = 7
    encabezados(ws, fh, 2, ["Puesto", "Código", "Localidad", "Zona insegura (%)", "Delitos de alto impacto (por 100.000)",
                            "ln(delitos)", "z percepción", "z registro", "IBS", "IC 90 % inferior", "IC 90 % superior",
                            "Puesto en IC 90 %", "Prob. de top 5", "Lectura"], alto=46)
    f0, f1 = fh + 1, fh + len(ib)
    P = R["panel"]
    pz, pd_ = P["col"]["zona_insegura"], P["col"]["delitos_alto_impacto_100k"]
    pr = f"Panel_localidad!$B${P['f0']}:$B${P['f1']}"
    for i, r in enumerate(ib.itertuples()):
        f = f0 + i
        cod = int(r.localidad)
        a, b = int(round(r.puesto_p05)), int(round(r.puesto_p95))
        vals = [int(r.puesto), cod, LOCALIDADES[cod],
                f"=INDEX(Panel_localidad!${pz}${P['f0']}:${pz}${P['f1']},MATCH(C{f},{pr},0))",
                f"=INDEX(Panel_localidad!${pd_}${P['f0']}:${pd_}${P['f1']},MATCH(C{f},{pr},0))",
                f"=LN(F{f})",
                f"=STANDARDIZE(E{f},AVERAGE($E${f0}:$E${f1}),STDEV($E${f0}:$E${f1}))",
                f"=STANDARDIZE(G{f},AVERAGE($G${f0}:$G${f1}),STDEV($G${f0}:$G${f1}))",
                f"=H{f}-I{f}", r.ibs_p05, r.ibs_p95, f"{a}" if a == b else f"{a} a {b}", r.prob_top5,
                f'=IF(J{f}>0,"Más miedo que delito registrado","Menos miedo que delito registrado")']
        fila_datos(ws, f, 2, vals, [CEN, CEN, TXT, PCT, ENT, DEC2, SIG2, SIG2, SIG2, SIG2, SIG2, CEN, PCT, TXT])
        ws.cell(f, 10).font = F(9.5, True, TINTA)
        # auxiliares de las barras de error del gráfico
        poner(ws, f, 17, f"=L{f}-J{f}", size=8, color=GRIS_NS, fmt=DEC2)
        poner(ws, f, 18, f"=J{f}-K{f}", size=8, color=GRIS_NS, fmt=DEC2)
    poner(ws, fh, 17, "Auxiliar del gráfico: error +", size=7.5, color=GRIS_NS, wrap=True, h="center")
    poner(ws, fh, 18, "Auxiliar del gráfico: error −", size=7.5, color=GRIS_NS, wrap=True, h="center")
    ws.conditional_formatting.add(f"J{f0}:J{f1}", ColorScaleRule(
        start_type="min", start_color=AZUL3, mid_type="num", mid_value=0, mid_color=GRIS_CERO,
        end_type="max", end_color=ORO3))
    ws.conditional_formatting.add(f"N{f0}:N{f1}", DataBarRule(start_type="num", start_value=0, end_type="num",
                                                              end_value=1, color=ORO3, showValue=True,
                                                              minLength=0, maxLength=100))
    ws.conditional_formatting.add(f"B{f0}:D{f1}", FormulaRule(formula=[f"$N{f0}>=0.9"],
                                                              font=Font(name=LETRA, bold=True, color=ROJO)))
    ws.freeze_panes = f"E{f0}"
    n = f1 + 1
    texto(ws, n, 2, 15, "Cómo se lee: IBS positivo (oro) = la localidad siente más inseguridad de la que predice su "
          "delito registrado; negativo (azul) = menos. Columnas E a J son fórmulas vivas sobre la hoja "
          "Panel_localidad (z con media y desviación estándar de las 19 localidades; ln porque la tasa es muy "
          "asimétrica: el centro concentra delito de población flotante). El intervalo de 90 %, el rango de puestos "
          "y la probabilidad de top 5 vienen de 1.000 réplicas bootstrap ponderadas dentro de cada localidad "
          "(outputs/tablas/ibs.csv). En rojo, las localidades que quedan en el top 5 en al menos el 90 % de las réplicas.",
          size=8.5, color=GRIS, italic=True)
    g = seccion(ws, n + 2, 2, "IBS por localidad, con intervalo de 90 %")
    salto(ws, g - 1)
    ch = barras_horizontales(cm(ws, 2, 12), 11.5, '+0;"−"0;0')
    ch.y_axis.scaling.min, ch.y_axis.scaling.max, ch.y_axis.majorUnit = -3, 3, 1
    s = Series(Reference(ws, min_col=10, min_row=f0, max_row=f1), title="IBS")
    ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=4, min_row=f0, max_row=f1))
    colores_por_punto(s, [ORO if v > 0 else AZUL for v in ib["ibs"]])
    s.invertIfNegative = False
    barras_error(s, ws.title, f"$Q${f0}:$Q${f1}", f"$R${f0}:$R${f1}")
    ws.add_chart(ch, f"B{g}")
    R["ibs"] = {"f0": f0, "f1": f1}
    imprimir(ws, area=f"A1:O{g + 24}")


def hoja_cifra(ws, D, R):
    cabecera(ws, "Cifra oculta", "Víctimas estimadas (EMV 2024) por cada delito de alto impacto registrado por la "
             "SCJ en 2024. Personas frente a hechos: se lee como orden de magnitud.", 15)
    anchos(ws, {"B": 8, "C": 22, "D": 12, "E": 11, "F": 13, "G": 12, "H": 12, "I": 14, "J": 12, "K": 11, "L": 11,
                "M": 10, "N": 10, "O": 10, "P": 3, "Q": 10, "R": 10})
    co = D["cifra_oculta"].sort_values("razon", ascending=False).reset_index(drop=True)
    fh = 7
    encabezados(ws, fh, 2, ["Código", "Localidad", "Víctimas, último año (% adultos)", "Error estándar",
                            "Víctimas estimadas (adultos)", "IC 95 % inferior", "IC 95 % superior",
                            "Delitos registrados 2024 (anualizados)", "Víctimas por delito registrado",
                            "IC 95 % inferior", "IC 95 % superior", "IBS", "Puesto en cifra oculta",
                            "Puesto en IBS"], alto=58)
    f0, f1 = fh + 1, fh + len(co)
    rb = R["ibs"]
    for i, r in enumerate(co.itertuples()):
        f = f0 + i
        vals = [int(r.localidad), r.nombre, r.emv_victima / 100, r.emv_victima_ee, r.victimas_estimadas,
                r.victimas_inf, r.victimas_sup, r.delitos_registrados, f"=F{f}/I{f}", f"=G{f}/I{f}", f"=H{f}/I{f}",
                f"=INDEX(Indice_brecha!$J${rb['f0']}:$J${rb['f1']},MATCH(B{f},Indice_brecha!$C${rb['f0']}:$C${rb['f1']},0))",
                f"=RANK(J{f},$J${f0}:$J${f1},0)", f"=RANK(M{f},$M${f0}:$M${f1},0)"]
        fila_datos(ws, f, 2, vals, [CEN, TXT, PCT, '0.0" pp"', ENT, ENT, ENT, ENT, DEC1, DEC1, DEC1, SIG2, CEN, CEN])
        ws.cell(f, 10).font = F(9.5, True, TINTA)
        poner(ws, f, 17, f"=L{f}-J{f}", size=8, color=GRIS_NS, fmt=DEC2)
        poner(ws, f, 18, f"=J{f}-K{f}", size=8, color=GRIS_NS, fmt=DEC2)
    poner(ws, fh, 17, "Auxiliar del gráfico: error +", size=7.5, color=GRIS_NS, wrap=True, h="center")
    poner(ws, fh, 18, "Auxiliar del gráfico: error −", size=7.5, color=GRIS_NS, wrap=True, h="center")
    fb = f1 + 1
    fila_datos(ws, fb, 2, [None, "Bogotá (19 localidades)", None, None, f"=SUM(F{f0}:F{f1})", None, None,
                           f"=SUM(I{f0}:I{f1})", f"=F{fb}/I{fb}", None, None, None, None, None],
               [CEN, TXT, PCT, DEC1, ENT, ENT, ENT, ENT, DEC1, DEC1, DEC1, SIG2, CEN, CEN], bold=True, fondo=FONDO)
    for c in range(2, 16):
        ws.cell(fb, c).border = Border(top=Side(style="thin", color=GRIS), bottom=FINA)
    ws.conditional_formatting.add(f"J{f0}:J{f1}", ColorScaleRule(
        start_type="min", start_color=ORO1, mid_type="percentile", mid_value=50, mid_color=ORO2,
        end_type="max", end_color=ORO3))
    ws.freeze_panes = f"D{f0}"
    fr = fb + 2
    poner(ws, fr, 2, "ρ de Spearman entre IBS y cifra oculta (fórmula: correlación de los puestos de las columnas N y O)",
          size=9.5, bold=True)
    ws.merge_cells(start_row=fr, start_column=2, end_row=fr, end_column=9)
    c = poner(ws, fr, 10, f"=CORREL(N{f0}:N{f1},O{f0}:O{f1})", size=12, bold=True, color=ROJO, fmt='"ρ = "0.00', h="right")
    c.border = Border(bottom=Side(style="medium", color=ROJO))
    ws.row_dimensions[fr].height = 24
    texto(ws, fr + 1, 2, 15, "Víctimas estimadas = % de víctimas (EMV 2024, 96 encuestas por localidad) × adultos "
          "de la localidad (SDP 2024); IC 95 % con el error estándar de la encuesta. Delitos registrados = los 11 "
          "delitos de alto impacto de la SCJ en enero-agosto de 2024 llevados a 12 meses (× 12/8). La razón se "
          "recalcula con fórmulas (J = F / I). Fuente: outputs/tablas/cifra_oculta.csv.",
          size=8.5, color=GRIS, italic=True)
    g = seccion(ws, fr + 3, 2, "Víctimas por delito registrado, con IC 95 %")
    salto(ws, g - 1)
    ch = grafico_base(BarChart(), cm(ws, 2, 9) - 0.4, 9.5)
    ch.type = "col"
    ch.gapWidth = 40
    ch.y_axis.numFmt = NumFmt(formatCode="0", sourceLinked=False)
    ch.x_axis.txPr = _rt(8, GRIS)
    s = Series(Reference(ws, min_col=10, min_row=f0, max_row=f1), title="Víctimas por delito registrado")
    ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=3, min_row=f0, max_row=f1))
    color_serie(s, VINO)
    barras_error(s, ws.title, f"$Q${f0}:$Q${f1}", f"$R${f0}:$R${f1}")
    ws.add_chart(ch, f"B{g}")
    poner(ws, g - 1, 10, "Índice de Brecha frente a cifra oculta", size=11.5, bold=True, v="bottom")
    sc = grafico_base(ScatterChart(), cm(ws, 10, 15) - 0.2, 9.5)
    sc.x_axis.numFmt = NumFmt(formatCode="+0;−0;0", sourceLinked=False)
    sc.y_axis.numFmt = NumFmt(formatCode="0", sourceLinked=False)
    sc.x_axis.majorGridlines = None
    sc.x_axis.title = None
    ss = Series(Reference(ws, min_col=10, min_row=f0, max_row=f1), Reference(ws, min_col=13, min_row=f0, max_row=f1),
                title="Localidades")
    ss.marker.symbol = "circle"
    ss.marker.size = 8
    ss.marker.graphicalProperties = GraphicalProperties(solidFill=ROJO, ln=_linea(BLANCO, 0.75))
    ss.graphicalProperties = GraphicalProperties(ln=LineProperties(noFill=True))
    sc.series.append(ss)
    ws.add_chart(sc, f"J{g}")
    poner(ws, g + 19, 10, "Eje horizontal: IBS. Eje vertical: víctimas por delito registrado.", size=8, color=GRIS, italic=True)
    # validaciones territoriales
    fv = seccion(ws, g + 21, 2, "Validaciones territoriales (Spearman, n = 19, corrección de Benjamini-Hochberg)")
    encabezados(ws, fv, 2, ["Prueba", None, None, None, None, None, "ρ", "IC 95 % inferior", "IC 95 % superior", "p",
                            "p ajustado (BH)", "n", "¿Sobrevive a BH?"], alto=34)
    ws.merge_cells(start_row=fv, start_column=2, end_row=fv, end_column=7)
    V = D["validaciones"]
    for i, r in enumerate(V.itertuples(), start=1):
        f = fv + i
        fila_datos(ws, f, 2, [r.prueba, None, None, None, None, None, r.rho, r.ic_inf, r.ic_sup, r.p, r.p_bh, int(r.n),
                              f'=IF(L{f}<0.05,"Sí","No")'],
                   [TXT, TXT, TXT, TXT, TXT, TXT, SIG2, SIG2, SIG2, DEC3, DEC3, CEN, CEN])
        ws.merge_cells(start_row=f, start_column=2, end_row=f, end_column=7)
    fvu = fv + len(V)
    ws.conditional_formatting.add(f"B{fv + 1}:N{fvu}", FormulaRule(formula=[f'$N{fv + 1}="Sí"'],
                                                                     font=Font(name=LETRA, bold=True, color=ROJO)))
    texto(ws, fvu + 1, 2, 15, "La relación entre el Índice de Brecha y la cifra oculta sobrevive a la corrección, pero es "
          "mecánica: los dos usan el delito registrado y, al controlarlo, la correlación parcial es prácticamente cero "
          "(outputs/tablas/validacion_parcial.csv). El miedo no se parece a la cifra oculta. Fuente: outputs/tablas/validaciones.csv "
          "(IC por bootstrap de 2.000 réplicas).",
          size=8.5, color=GRIS, italic=True)
    rho_fila = V.index[V["prueba"].str.startswith("Índice de Brecha")][0] + fv + 1
    R["cifra"] = {"bogota": f"Cifra_oculta!$J${fb}", "rho": f"Cifra_oculta!$J${fr}",
                  "rho_bh": f"Cifra_oculta!$L${rho_fila}"}
    imprimir(ws, area=f"A1:O{fvu + 2}")


def tabla_modelo(ws, fila, df, titulo, detalle, R=None, clave=None, ultima=8):
    f = seccion(ws, fila, 2, titulo, detalle, ultima)
    encabezados(ws, f, 2, ["Variable", "Bloque", "Efecto marginal (pp)", "IC 95 % inferior", "IC 95 % superior", "p",
                           "¿IC excluye 0?"], alto=34)
    f0 = f + 1
    for i, r in enumerate(df.itertuples()):
        ff = f0 + i
        fila_datos(ws, ff, 2, [ETIQUETAS.get(r.variable, r.variable), BLOQUE.get(r.variable, ""), r.ame_pp, r.ic_inf,
                               r.ic_sup, r.p, f'=IF(OR(E{ff}>0,F{ff}<0),"Sí","No")'],
                   [TXT, TXT, PP2, PP2, PP2, DEC3, CEN])
        ws.cell(ff, 4).font = F(9.5, True, TINTA)
        if R is not None:
            R.setdefault("ame", {})[(clave, r.variable)] = f"Modelos!$D${ff}"
    f1 = f0 + len(df) - 1
    gris_si_no_significativo(ws, f"B{f0}:H{f1}", "E", "F", f0)
    return f0, f1


def hoja_modelos(ws, D, R):
    res = D["res"]
    cabecera(ws, "Modelos", "Qué explica sentir insegura la zona. Efectos marginales promedio en puntos porcentuales "
             "(pp) con IC 95 %.", 17)
    anchos(ws, {"B": 40, "C": 22, "D": 13, "E": 11, "F": 11, "G": 9, "H": 10, "I": 3})
    for c in "JKLMNOPQ":
        ws.column_dimensions[c].width = 11
    anchos(ws, {"R": 3, "S": 10, "T": 10})
    texto(ws, 6, 2, 17, "Nota metodológica. Logit ponderado con el factor de expansión de la Bienal 2025 (las "
          f"estimaciones representan a {es(res['adultos_urbanos_bienal'], 0)} adultos urbanos; n = "
          f"{es(res['n_bienal'], 0)}). Efecto marginal promedio (AME): cambio en la probabilidad, en pp, al pasar la "
          "variable de 0 a 1 (o por unidad indicada). IC 95 % por bootstrap de conglomerados que remuestrea las 19 "
          "localidades: con tan pocos conglomerados los errores analíticos agrupados son optimistas. En gris, los "
          "efectos cuyo IC cruza 0. El modelo principal usa solo hechos del entorno (no calificaciones) para evitar "
          "el sesgo de método común.", size=9, fondo=FONDO, color=TINTA, v="center")
    # 1. principal
    m = D["m_hechos"]
    f0, f1 = tabla_modelo(ws, 8, m, "1. Modelo principal: hechos del entorno",
                          "Resultado: siente insegura o muy insegura su zona (Bienal 2025). Variables: perfil, delito "
                          "registrado de la localidad y hechos del entorno.", R, "hechos")
    for i, r in enumerate(m.itertuples()):
        poner(ws, f0 + i, 19, f"=F{f0 + i}-D{f0 + i}", size=8, color=GRIS_NS, fmt=DEC2)
        poner(ws, f0 + i, 20, f"=D{f0 + i}-E{f0 + i}", size=8, color=GRIS_NS, fmt=DEC2)
    poner(ws, f0 - 1, 19, "Auxiliar del gráfico: error +", size=7.5, color=GRIS_NS, wrap=True, h="center")
    poner(ws, f0 - 1, 20, "Auxiliar del gráfico: error −", size=7.5, color=GRIS_NS, wrap=True, h="center")
    poner(ws, 8, 10, "Efecto marginal e IC 95 % (oro: IC excluye 0)", size=11.5, bold=True, v="bottom")
    ch = barras_horizontales(cm(ws, 10, 17) - 0.2, 9.2, '+0;"−"0;0')
    s = Series(Reference(ws, min_col=4, min_row=f0, max_row=f1), title="Efecto marginal (pp)")
    ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=2, min_row=f0, max_row=f1))
    colores_por_punto(s, [ORO if (r.ic_inf > 0 or r.ic_sup < 0) else "C8C8C8" for r in m.itertuples()])
    s.invertIfNegative = False
    barras_error(s, ws.title, f"$S${f0}:$S${f1}", f"$T${f0}:$T${f1}")
    ch.x_axis.txPr = _rt(8, GRIS)
    ws.add_chart(ch, f"J{f0 - 1}")
    # 2 a 5. robustez
    f = f1 + 2
    _, f = tabla_modelo(ws, f, D["m_calif"], "2. Con calificaciones del entorno",
                        "Agrega alumbrado malo y ventas informales. Comparten batería de preguntas con la seguridad de "
                        "la zona (sesgo de método común): se reportan aparte, no como causa.", R, "calif")
    salto(ws, f + 2)
    _, f = tabla_modelo(ws, f + 2, D["m_ciudad"], "3. Resultado alterno: la ciudad es insegura",
                        "Mismas variables del modelo principal. La percepción de la ciudad casi no depende del entorno "
                        "inmediato.")
    _, f = tabla_modelo(ws, f + 2, D["m_miedo"], "4. Resultado alterno: miedo en el espacio público",
                        "Mismas variables del modelo principal.")
    fe = D["m_efectos_fijos"][~D["m_efectos_fijos"]["variable"].str.startswith("loc_")]
    salto(ws, f + 2)
    _, f = tabla_modelo(ws, f + 2, fe, "5. Con efectos fijos de localidad",
                        "Controla todo lo que es común a cada localidad (incluido su delito registrado). Se estiman 18 "
                        "efectos fijos de localidad que no se muestran. Los hechos del entorno se mantienen.")
    # 6. LPM wild
    f = seccion(ws, f + 2, 2, "6. Modelo lineal con wild cluster bootstrap",
                "Modelo lineal de probabilidad con errores agrupados por localidad y p-valor por wild cluster bootstrap "
                "(pesos de Webb), robusto con pocos conglomerados.", 8)
    encabezados(ws, f, 2, ["Variable", "Bloque", "Coeficiente (pp)", "p agrupado", "p wild bootstrap",
                           "¿p wild < 0,05?"], alto=34)
    lw = D["lpm_wild"]
    for i, r in enumerate(lw.itertuples(), start=1):
        ff = f + i
        fila_datos(ws, ff, 2, [ETIQUETAS.get(r.variable, r.variable), BLOQUE.get(r.variable, ""), r.coef_pp,
                               r.p_cluster, r.p_wild, f'=IF(F{ff}<0.05,"Sí","No")'],
                   [TXT, TXT, PP2, DEC3, DEC3, CEN])
        if r.variable == "hurtos_100k_miles":
            R["p_wild_hurtos"] = f"Modelos!$F${ff}"
    ws.conditional_formatting.add(f"B{f + 1}:G{f + len(lw)}", FormulaRule(
        formula=[f"$F{f + 1}>=0.05"], font=Font(name=LETRA, color=GRIS_NS)))
    f = f + len(lw)
    # 7. AUC
    salto(ws, f + 2)
    fa = seccion(ws, f + 2, 2, "7. Capacidad predictiva por bloques de variables",
                 "AUC fuera de muestra con validación cruzada estratificada repetida (25 pliegues). 0,5 = azar. "
                 "Agregar el delito registrado casi no mejora la predicción; el entorno sí.", 8)
    encabezados(ws, fa, 2, ["Bloque de variables", "Composición (n.º de variables)", "AUC", "Desv. estándar",
                            "Pliegues"], alto=34)
    A = D["auc"]
    for i, r in enumerate(A.itertuples(), start=1):
        ff = fa + i
        cuenta: dict = {}
        for v in (x.strip() for x in r.variables.split(",")):
            cuenta[BLOQUE.get(v, v)] = cuenta.get(BLOQUE.get(v, v), 0) + 1
        composicion = " + ".join(f"{b} ({n})" for b, n in cuenta.items())
        fila_datos(ws, ff, 2, [r.bloque, composicion, r.auc, r.auc_sd, int(r.pliegues)], [TXT, TXT, DEC3, DEC3, CEN],
                   alto=max(20, _alto(composicion, 22, 8.5)))
        ws.cell(ff, 3).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
        ws.cell(ff, 3).font = F(8.5, False, GRIS)
        ws.cell(ff, 4).font = F(9.5, True, TINTA)
    R["auc"] = {b: f"Modelos!$D${fa + 1 + i}" for i, b in enumerate(A["bloque"])}
    ch = barras_horizontales(cm(ws, 10, 17) - 0.2, 7.6, "0.00")
    ch.y_axis.scaling.min = 0.5
    ch.y_axis.scaling.max = 0.8
    ch.y_axis.majorUnit = 0.05
    s = Series(Reference(ws, min_col=4, min_row=fa + 1, max_row=fa + len(A)), title="AUC")
    ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=2, min_row=fa + 1, max_row=fa + len(A)))

    def color_bloque(b):
        if b == "Todo":
            return ROJO
        if "calificación" in b:
            return ORO
        if "hechos" in b:
            return ORO3
        if "delito" in b:
            return AZUL
        return "B5B5B5"
    colores_por_punto(s, [color_bloque(b) for b in A["bloque"]])
    etiquetas(s, "0.000", posicion="outEnd")
    ch.x_axis.txPr = _rt(8, GRIS)
    ws.add_chart(ch, f"J{fa - 1}")
    poner(ws, fa - 2, 10, "AUC por bloque (eje desde 0,5 = azar)", size=11.5, bold=True, v="bottom")
    fin = fa + len(A) + 1
    texto(ws, fin + 1, 2, 17, "Fuentes: outputs/tablas/m_hechos.csv, m_calif.csv, m_ciudad.csv, m_miedo.csv, "
          "m_efectos_fijos.csv, lpm_wild.csv y auc.csv (src/modelos.py). Las variables continuas se leen por la unidad "
          "indicada en su nombre (por ejemplo, +1.000 hurtos por 100 mil).", size=8.5, color=GRIS, italic=True)
    imprimir(ws, area=f"A1:Q{fin + 2}")


def hoja_genero(ws, D, R):
    res = D["res"]
    cabecera(ws, "Género", "A igual edad, estrato y victimización, las mujeres temen más y restringen más su vida "
             "(Encuesta Mundial de Valores 2024, Bogotá).", 13)
    anchos(ws, {"B": 34, "C": 11, "D": 11, "E": 12, "F": 13, "G": 11, "H": 11, "I": 9, "J": 3, "K": 10, "L": 10, "M": 10})
    f = seccion(ws, 6, 2, "1. Mujeres frente a hombres",
                f"Porcentajes ponderados de adultos de Bogotá (n = {es(res['n_emv_bogota'], 0)}). Efecto de ser mujer: "
                "logit ponderado con edad, estrato y haber sido víctima; IC 95 % por bootstrap de localidades.", 9)
    encabezados(ws, f, 2, ["Indicador (EMV 2024)", "Mujeres", "Hombres", "Diferencia (pp)",
                           "Efecto de ser mujer (pp)", "IC 95 % inferior", "IC 95 % superior", "p"], alto=40)
    filas = [("victima", "Fue víctima de un delito (último año)"), ("no_sale_noche", "No sale de noche"),
             ("teme_acoso_sexual", "Teme acoso sexual"), ("barrio_inseguro", "Siente inseguro su barrio")]
    f0 = f + 1
    for i, (k, nombre) in enumerate(filas):
        ff = f0 + i
        sx = res["emv_por_sexo"][k]
        if k == "victima":
            vals = [nombre, sx["mujeres"] / 100, sx["hombres"] / 100, f"=(C{ff}-D{ff})*100", "Control del modelo",
                    None, None, None]
            fila_datos(ws, ff, 2, vals, [TXT, PCT, PCT, PP, CEN, PP, PP, DEC3])
            ws.cell(ff, 6).font = F(8.5, False, GRIS, True)
        else:
            a = D[f"emv_{k}"].set_index("variable").loc["mujer"]
            vals = [nombre, sx["mujeres"] / 100, sx["hombres"] / 100, f"=(C{ff}-D{ff})*100", a.ame_pp, a.ic_inf,
                    a.ic_sup, a.p]
            fila_datos(ws, ff, 2, vals, [TXT, PCT, PCT, PP, PP, PP, PP, DEC3])
            ws.cell(ff, 6).font = F(9.5, True, MUJER)
            poner(ws, ff, 12, f"=H{ff}-F{ff}", size=8, color=GRIS_NS, fmt=DEC2)
            poner(ws, ff, 13, f"=F{ff}-G{ff}", size=8, color=GRIS_NS, fmt=DEC2)
            R.setdefault("genero", {})[k] = f"Genero!$F${ff}"
        ws.cell(ff, 3).font = F(9.5, True, MUJER)
        ws.cell(ff, 4).font = F(9.5, True, HOMBRE)
    f1 = f0 + len(filas) - 1
    poner(ws, f, 12, "Auxiliar del gráfico: error +", size=7.5, color=GRIS_NS, wrap=True, h="center")
    poner(ws, f, 13, "Auxiliar del gráfico: error −", size=7.5, color=GRIS_NS, wrap=True, h="center")
    vb = D["emv_barrio_inseguro"].set_index("variable").loc["victima"]
    texto(ws, f1 + 1, 2, 9, f"Haber sido víctima suma {signo(vb.ame_pp)} pp a sentir inseguro el barrio (IC 95 % "
          f"{es(vb.ic_inf)} a {es(vb.ic_sup)}). Las mujeres reportan menos victimización y aun así temen más: el miedo "
          "no es solo experiencia de delito.", size=8.5, color=GRIS, italic=True)
    # gráficos
    g = f1 + 3
    poner(ws, g, 2, "Porcentaje de adultos por sexo", size=11.5, bold=True, v="bottom")
    poner(ws, g, 6, "Efecto de ser mujer, a igual victimización (pp)", size=11.5, bold=True, v="bottom")
    ws.row_dimensions[g].height = 24
    ch = grafico_base(BarChart(), cm(ws, 2, 5) - 0.3, 8.2, leyenda="t")
    ch.type = "col"
    ch.gapWidth = 70
    ch.overlap = -5
    ch.y_axis.numFmt = NumFmt(formatCode="0%", sourceLinked=False)
    ch.y_axis.scaling.min = 0
    ch.y_axis.scaling.max = 0.8
    for col, nombre, color in ((3, "Mujeres", MUJER), (4, "Hombres", HOMBRE)):
        s = Series(Reference(ws, min_col=col, min_row=f0, max_row=f1), title=nombre)
        color_serie(s, color)
        etiquetas(s, "0%", size=8, posicion="outEnd")
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=2, min_row=f0, max_row=f1))
    ch.x_axis.txPr = _rt(8, GRIS)
    ws.add_chart(ch, f"B{g + 1}")
    ch2 = grafico_base(BarChart(), cm(ws, 6, 9) - 0.1, 8.2)
    ch2.type = "col"
    ch2.gapWidth = 90
    ch2.y_axis.numFmt = NumFmt(formatCode='+0" pp";"−"0" pp";0', sourceLinked=False)
    ch2.y_axis.scaling.min = 0
    s = Series(Reference(ws, min_col=6, min_row=f0 + 1, max_row=f1), title="Efecto de ser mujer")
    color_serie(s, MUJER)
    barras_error(s, ws.title, f"$L${f0 + 1}:$L${f1}", f"$M${f0 + 1}:$M${f1}")
    ch2.series.append(s)
    ch2.set_categories(Reference(ws, min_col=2, min_row=f0 + 1, max_row=f1))
    ch2.x_axis.txPr = _rt(8, GRIS)
    ws.add_chart(ch2, f"F{g + 1}")
    # 2. Bienal por sexo y localidad
    P = D["panel"].copy()
    P["dif"] = P["zona_insegura_mujeres"] - P["zona_insegura_hombres"]
    P = P.sort_values("dif", ascending=False)
    salto(ws, g + 19)
    f = seccion(ws, g + 19, 2, "2. Zona insegura y miedo en el espacio público, por sexo y localidad (Bienal 2025)",
                "Porcentajes ponderados de adultos. Ordenado por la diferencia en zona insegura.", 9)
    encabezados(ws, f, 2, ["Localidad", "Zona insegura: mujeres", "Zona insegura: hombres", "Diferencia (pp)",
                           "Miedo en espacio público: mujeres", "Miedo en espacio público: hombres", "Diferencia (pp)"],
                alto=60)
    for i, r in enumerate(P.itertuples(), start=1):
        ff = f + i
        fila_datos(ws, ff, 2, [r.nombre, r.zona_insegura_mujeres / 100, r.zona_insegura_hombres / 100,
                               f"=(C{ff}-D{ff})*100", r.miedo_espacio_publico_mujeres / 100,
                               r.miedo_espacio_publico_hombres / 100, f"=(F{ff}-G{ff})*100"],
                   [TXT, PCT, PCT, PP, PCT, PCT, PP])
        for c, color in ((3, MUJER), (4, HOMBRE), (6, MUJER), (7, HOMBRE)):
            ws.cell(ff, c).font = F(9.5, False, color)
    fl = f + len(P)
    for col in ("E", "H"):
        ws.conditional_formatting.add(f"{col}{f + 1}:{col}{fl}", ColorScaleRule(
            start_type="min", start_color="EFE3F8", end_type="max", end_color="C9A3E6"))
    # 3. modelos EMV completos
    f = seccion(ws, fl + 2, 2, "3. Modelos completos (logit ponderado, EMV 2024)",
                "Efectos marginales promedio de cada variable sobre cada resultado.", 9)
    encabezados(ws, f, 2, ["Resultado · variable", "Efecto marginal (pp)", "IC 95 % inferior", "IC 95 % superior", "p",
                           "¿IC excluye 0?"], alto=34)
    ff = f
    for k, nombre in filas[1:]:
        ff += 1
        poner(ws, ff, 2, nombre, size=9.5, bold=True, color=VINO, indent=1)
        ws.row_dimensions[ff].height = 20
        for r in D[f"emv_{k}"].itertuples():
            ff += 1
            fila_datos(ws, ff, 2, [ETIQUETAS.get(r.variable, r.variable), r.ame_pp, r.ic_inf, r.ic_sup, r.p,
                                   f'=IF(OR(D{ff}>0,E{ff}<0),"Sí","No")'], [TXT, PP2, PP2, PP2, DEC3, CEN])
            ws.cell(ff, 2).alignment = Alignment(horizontal="left", vertical="center", indent=2)
        gris_si_no_significativo(ws, f"B{ff - 3}:G{ff}", "D", "E", ff - 3)
    texto(ws, ff + 2, 2, 9, "Fuentes: outputs/resultados.json (porcentajes por sexo), outputs/tablas/emv_*.csv y "
          "data/procesados/panel_localidad_2025.csv.", size=8.5, color=GRIS, italic=True)
    imprimir(ws, area=f"A1:I{ff + 3}", vertical=True, paginas=2)


def hoja_serie(ws, D, R):
    s = D["serie"][["codigo", "tipo", "anio", "casos", "fuente"]]
    anios = sorted(s["anio"].unique())
    orden = ["HP", "HR", "HA", "HB", "H", "LP", "VI", "DS"]
    t0 = s.drop_duplicates("codigo").set_index("codigo")
    tipos = {c: t0.loc[c, "tipo"] + (" (Policía)" if str(t0.loc[c, "fuente"]).startswith("Policía") else "") for c in orden}
    ancho_tabla = 3 + len(anios) + 2
    cabecera(ws, "Serie de delitos registrados", "Bogotá, enero-agosto de cada año. Hurto a personas, residencias y "
             "automotores: registro de la Policía (SIEDCO), porque la capa SCJ cambia de escala en 2023. Los demás: SCJ, "
             "validados con la Policía y Medicina Legal.", ancho_tabla)
    anchos(ws, {"B": 8, "C": 26})
    for i in range(len(anios)):
        ws.column_dimensions[L(4 + i)].width = 10
    cy = 4 + len(anios)
    anchos(ws, {L(cy): 13, L(cy + 1): 13})
    f = seccion(ws, 6, 2, "1. Casos registrados (enero-agosto)")
    encabezados(ws, f, 2, ["Código", "Tipo de delito"] + [str(a) for a in anios] +
                ["Cambio 2018 → 2026", "Cambio 2019 → 2026"], alto=34)
    piv = s.pivot(index="codigo", columns="anio", values="casos")
    filas = {}
    c18, c19, c26 = L(4 + anios.index(2018)), L(4 + anios.index(2019)), L(4 + anios.index(2026))
    for i, cod in enumerate(orden, start=1):
        ff = f + i
        filas[cod] = ff
        casos = [None if pd.isna(piv.loc[cod, a]) else int(piv.loc[cod, a]) for a in anios]
        fila_datos(ws, ff, 2, [cod, tipos[cod]] + casos +
                   [f'=IF({c26}{ff}="","",{c26}{ff}/{c18}{ff}-1)', f'=IF({c26}{ff}="","",{c26}{ff}/{c19}{ff}-1)'],
                   [CEN, TXT] + [ENT] * len(anios) + [VAR, VAR], bold=cod == "HP")
        if casos[-1] is None:
            c = ws.cell(ff, 3 + len(anios))
            c.value = None
            ws.cell(ff, 3 + len(anios)).comment = Comment("Sin dato publicado para 2026 en la fuente.", "The data squad")
    fu = f + len(orden)
    rango_cambio = f"{L(cy)}{f + 1}:{L(cy + 1)}{fu}"
    ws.conditional_formatting.add(rango_cambio, FormulaRule(formula=[f'AND(ISNUMBER({L(cy)}{f + 1}),{L(cy)}{f + 1}<0)'],
                                                            font=Font(name=LETRA, bold=True, color=AZUL)))
    ws.conditional_formatting.add(rango_cambio, FormulaRule(formula=[f'AND(ISNUMBER({L(cy)}{f + 1}),{L(cy)}{f + 1}>0)'],
                                                            font=Font(name=LETRA, bold=True, color=VINO)))
    R["hurto_cambio"] = f"Serie_delitos!${L(cy + 1)}${filas['HP']}"
    texto(ws, fu + 1, 2, ancho_tabla, "Lesiones personales no tiene dato publicado para 2026. Fuentes: Policía Nacional, "
          "SIEDCO en datos.gov.co (filas «Policía»); SCJ, Delito de alto impacto (las demás). Comercio, celulares y motocicletas "
          "no se muestran: desde 2023 esas columnas de la capa no coinciden con su nombre. Azul: baja; vino: sube.",
          size=8.5, color=GRIS, italic=True)
    # gráfico
    salto(ws, fu + 3)
    g = seccion(ws, fu + 3, 2, "2. Índice 2018 = 100: el hurto a personas no baja frente a 2018; la violencia intrafamiliar y los delitos sexuales suben")
    gi = g + 21
    fi = seccion(ws, gi, 2, "3. Índice 2018 = 100 (fórmulas sobre la tabla 1)")
    encabezados(ws, fi, 2, ["Código", "Tipo de delito"] + [str(a) for a in anios], alto=30)
    for i, cod in enumerate(orden, start=1):
        ff = fi + i
        fo = filas[cod]
        vals = [cod, tipos[cod]] + [f'=IF({L(4 + j)}{fo}="","",{L(4 + j)}{fo}/${c18}{fo}*100)' for j in range(len(anios))]
        fila_datos(ws, ff, 2, vals, [CEN, TXT] + ["0.0"] * len(anios), bold=cod in ("HP", "VI", "DS"))
    fiu = fi + len(orden)
    ws.conditional_formatting.add(f"{L(4)}{fi + 1}:{L(3 + len(anios))}{fiu}", ColorScaleRule(
        start_type="min", start_color=AZUL2, mid_type="num", mid_value=100, mid_color=BLANCO,
        end_type="max", end_color="E9A7AF"))
    ch = grafico_base(LineChart(), cm(ws, 2, 14) - 0.3, 10, leyenda="t")
    ch.y_axis.numFmt = NumFmt(formatCode="0", sourceLinked=False)
    ch.y_axis.scaling.min = 0
    ch.y_axis.scaling.max = 200
    ch.y_axis.majorUnit = 50
    for cod, color in (("HP", AZUL), ("VI", VINO), ("DS", MUJER)):
        ff = fi + 1 + orden.index(cod)
        se = Series(Reference(ws, min_col=4, max_col=3 + len(anios), min_row=ff), title=None)
        se.tx = SeriesLabel(strRef=StrRef(f"'{ws.title}'!$C${ff}"))
        se.graphicalProperties = GraphicalProperties(ln=_linea(color, 2.5))
        se.marker.symbol = "circle"
        se.marker.size = 6
        se.marker.graphicalProperties = GraphicalProperties(solidFill=color, ln=_linea(color, 1))
        se.smooth = False
        ch.series.append(se)
    ch.set_categories(Reference(ws, min_col=4, max_col=3 + len(anios), min_row=fi))
    ws.add_chart(ch, f"B{g}")
    texto(ws, fiu + 1, 2, ancho_tabla, "Cada celda = casos del año / casos de 2018 × 100. Más de 100: sube frente a "
          "2018 (rosado); menos de 100: baja (azul).", size=8.5, color=GRIS, italic=True)
    # 4. la capa abierta frente a la Policía
    fc = seccion(ws, fiu + 3, 2, "4. Hurto a personas: la capa abierta de la SCJ frente al registro de la Policía (enero-agosto)")
    encabezados(ws, fc, 2, ["", "Serie"] + [str(a) for a in anios], alto=30)
    hu = D["hurto"].set_index("anio")
    filas_c = [("SCJ", "Capa abierta SCJ", "capa_scj"), ("SIEDCO", "Policía (SIEDCO)", "siedco")]
    for i, (cod, nom, col) in enumerate(filas_c, start=1):
        fila_datos(ws, fc + i, 2, [cod, nom] + [None if pd.isna(hu.loc[a, col]) else int(hu.loc[a, col]) for a in anios], [CEN, TXT] + [ENT] * len(anios))
    fr_ = fc + 3
    fila_datos(ws, fr_, 2, ["÷", "Capa ÷ Policía"] + [f"={L(4 + j)}{fc + 1}/{L(4 + j)}{fc + 2}" for j in range(len(anios))],
               [CEN, TXT] + ["0.00"] * len(anios), bold=True)
    ws.conditional_formatting.add(f"{L(4)}{fr_}:{L(3 + len(anios))}{fr_}", FormulaRule(formula=[f"{L(4)}{fr_}>1.1"], font=Font(name=LETRA, bold=True, color=VINO)))
    texto(ws, fr_ + 1, 2, ancho_tabla, "De 2018 a 2022 la capa cuenta 2,3 a 2,6 veces lo que registra la Policía; desde 2023 coinciden caso por "
          "caso. Por eso en la capa el hurto «cae» 58 % de 2022 a 2026 y en la Policía, 4 %. La encuesta del DANE confirma a la Policía "
          "(denuncia del hurto: 36 % en 2021, 43 % en 2023). Fuente: outputs/tablas/registro_hurto_personas.csv.",
          size=8.5, color=GRIS, italic=True)
    ws.freeze_panes = "D6"
    imprimir(ws, area=f"A1:{L(ancho_tabla)}{fr_ + 2}")


def hoja_simulador(ws, D, R):
    res = D["res"]
    cabecera(ws, "Simulador de escenarios", "¿Cuánto bajaría la inseguridad percibida si mejoran el alumbrado y los "
             "parques? Cambia las celdas crema: todo se recalcula.", 16)
    anchos(ws, {"B": 8, "C": 24, "D": 12, "E": 12, "F": 12, "G": 13, "H": 3})
    for c in "IJKLMNOP":
        ws.column_dimensions[c].width = 10
    anchos(ws, {"Q": 3, "R": 8, "S": 8, "T": 20, "U": 10})
    e = R["esc"]
    rng = lambda col: f"Datos_escenarios!${col}${e['f0']}:${col}${e['f1']}"  # noqa: E731

    def sumifs(col, codigo):
        return f"SUMIFS({rng(col)},{rng('B')},grupo_sim,{rng('C')},{codigo})"

    # entradas
    poner(ws, 6, 2, "1. PALANCAS", size=8.5, bold=True, color=GRIS, v="bottom")
    entradas = [(7, "Zonas donde el alumbrado deja de ser malo", 0.5, PCT),
                (8, "Parques donde dejan de verse atracos", 0.5, PCT),
                (9, "Grupo de población", "Total", None)]
    for fila, etiqueta, valor, fmt in entradas:
        ws.merge_cells(start_row=fila, start_column=2, end_row=fila, end_column=5)
        poner(ws, fila, 2, etiqueta, size=10, color=TINTA, indent=1)
        for c in range(2, 6):
            ws.cell(fila, c).border = Border(bottom=FINA)
        c = poner(ws, fila, 6, valor, size=12, bold=True, color=AZUL, h="center", fondo=ORO1, fmt=fmt or "General")
        c.border = Border(*(Side(style="thin", color=ORO3),) * 4)
        ws.merge_cells(start_row=fila, start_column=6, end_row=fila, end_column=7)
        ws.cell(fila, 7).fill = relleno(ORO1)
        ws.cell(fila, 7).border = Border(*(Side(style="thin", color=ORO3),) * 4)
        ws.row_dimensions[fila].height = 26
    texto(ws, 10, 2, 7, "Celdas crema: editables. Coberturas de 0 % a 100 %; grupo: Total, Mujeres u Hombres "
          "(lista desplegable).", size=8, color=GRIS, italic=True)
    for nombre, ref in (("f_alumbrado", "$F$7"), ("f_parques", "$F$8"), ("grupo_sim", "$F$9")):
        wb = ws.parent
        wb.defined_names[nombre] = DefinedName(nombre, attr_text=f"Simulador!{ref}")
    dv = DataValidation(type="decimal", operator="between", formula1="0", formula2="1", allow_blank=False,
                        showErrorMessage=True, errorTitle="Valor fuera de rango",
                        error="Escribe un porcentaje entre 0 % y 100 %.", showInputMessage=True,
                        promptTitle="Cobertura", prompt="Porcentaje entre 0 % y 100 %.")
    dv.add("F7:F8")
    dl = DataValidation(type="list", formula1='"Total,Mujeres,Hombres"', allow_blank=False, showErrorMessage=True,
                        errorTitle="Grupo no válido", error="Elige Total, Mujeres u Hombres.")
    dl.add("F9")
    ws.add_data_validation(dv)
    ws.add_data_validation(dl)
    # tabla
    fh = 13
    poner(ws, 12, 2, "2. RESULTADO POR LOCALIDAD · PROBABILIDAD DE SENTIR INSEGURA LA ZONA", size=8.5, bold=True,
          color=GRIS, v="bottom")
    encabezados(ws, fh, 2, ["Código", "Localidad", "Hoy (modelo)", "Escenario", "Cambio (pp)",
                            "Observado (Bienal 2025)"], alto=36)

    def fila_sim(f, codigo_expr, codigo_val, nombre, bold=False, fondo=None):
        hoy = f"={sumifs('E', codigo_expr)}"
        esc = (f"=(1-f_alumbrado)*(1-f_parques)*D{f}+f_alumbrado*(1-f_parques)*{sumifs('F', codigo_expr)}"
               f"+(1-f_alumbrado)*f_parques*{sumifs('G', codigo_expr)}+f_alumbrado*f_parques*{sumifs('H', codigo_expr)}")
        fila_datos(ws, f, 2, [codigo_val, nombre, hoy, esc, f"=(E{f}-D{f})*100", f"={sumifs('I', codigo_expr)}"],
                   [CEN, TXT, PCT, PCT, PP, PCT], bold=bold, fondo=fondo, alto=19)
        ws.cell(f, 6).font = F(9.5, True, ROJO if not fondo else ROJO)

    fb = fh + 1
    fila_sim(fb, "0", None, "Bogotá", bold=True, fondo=FONDO)
    locs = sorted(LOCALIDADES)[:19]
    f0 = fb + 1
    for i, cod in enumerate(locs):
        fila_sim(f0 + i, f"$B{f0 + i}", cod, LOCALIDADES[cod])
    f1 = f0 + len(locs) - 1
    ws.conditional_formatting.add(f"F{f0}:F{f1}", ColorScaleRule(start_type="min", start_color=ORO3,
                                                                 end_type="num", end_value=0, end_color=BLANCO))
    # bloque de resultado de Bogotá
    poner(ws, 6, 9, "BOGOTÁ · PROBABILIDAD DE SENTIR INSEGURA LA ZONA", size=8.5, bold=True, color=GRIS, v="bottom")
    for c in range(9, 17):
        for f in range(7, 11):
            ws.cell(f, c).fill = relleno(FONDO)
    for c1, etiqueta, formula, fmt, color in ((9, "Hoy (modelo)", f"=D{fb}", PCT, TINTA),
                                              (12, "Escenario", f"=E{fb}", PCT, TINTA),
                                              (15, "Cambio", f"=F{fb}", PP, ROJO)):
        ws.merge_cells(start_row=7, start_column=c1, end_row=7, end_column=c1 + 1)
        poner(ws, 7, c1, etiqueta, size=8.5, color=GRIS, h="left", v="bottom", fondo=FONDO, indent=1)
        ws.merge_cells(start_row=8, start_column=c1, end_row=8, end_column=c1 + 1)
        poner(ws, 8, c1, formula, size=22, bold=True, color=color, fmt=fmt, h="left", fondo=FONDO, indent=1)
    poner(ws, 8, 11, "→", size=18, color=GRIS, h="center", fondo=FONDO)
    ws.row_dimensions[8].height = 40
    ws.merge_cells("I9:N9")
    poner(ws, 9, 9, "Adultos que dejarían de sentir insegura su zona (orden de magnitud, solo para el total)",
          size=8.5, color=GRIS, fondo=FONDO, indent=1, wrap=True)
    ws.merge_cells("O9:P9")
    c = poner(ws, 9, 15, f'=IF(grupo_sim="Total",-F{fb}/100*$P$10,"n. a.")', size=11, bold=True, color=TINTA,
              fmt=ENT, h="left", fondo=FONDO, indent=1)
    ws.merge_cells("I10:O10")
    poner(ws, 10, 9, "Adultos urbanos representados por la Bienal 2025 (factor de expansión)", size=8, color=GRIS,
          fondo=FONDO, indent=1, italic=True)
    c = poner(ws, 10, 16, res["adultos_urbanos_bienal"], size=8, color=GRIS, fmt=ENT, fondo=FONDO, h="right")
    c.comment = Comment("Fuente: outputs/resultados.json, adultos_urbanos_bienal (suma del factor de expansión).",
                        "The data squad")
    ws.row_dimensions[9].height = 30
    # orden automático para el gráfico (de la mayor baja a la menor)
    poner(ws, fh, 18, "Clave de orden", size=7.5, color=GRIS_NS, wrap=True, h="center")
    poner(ws, fh, 19, "Puesto", size=7.5, color=GRIS_NS, wrap=True, h="center")
    poner(ws, fh, 20, "Auxiliar del gráfico: localidad", size=7.5, color=GRIS_NS, wrap=True, h="center")
    poner(ws, fh, 21, "Auxiliar: cambio (pp)", size=7.5, color=GRIS_NS, wrap=True, h="center")
    for i in range(len(locs)):
        f = f0 + i
        poner(ws, f, 18, f"=F{f}+B{f}/10000000", size=8, color=GRIS_NS, fmt="0.000")
        poner(ws, f, 19, i + 1, size=8, color=GRIS_NS, h="center")
        poner(ws, f, 20, f"=INDEX($C${f0}:$C${f1},MATCH(SMALL($R${f0}:$R${f1},S{f}),$R${f0}:$R${f1},0))",
              size=8, color=GRIS_NS)
        poner(ws, f, 21, f"=INDEX($F${f0}:$F${f1},MATCH(SMALL($R${f0}:$R${f1},S{f}),$R${f0}:$R${f1},0))",
              size=8, color=GRIS_NS, fmt='+0.0;"−"0.0;0.0')
    poner(ws, 12, 9, "CAMBIO POR LOCALIDAD (pp), DE LA MAYOR BAJA A LA MENOR", size=8.5, bold=True, color=GRIS, v="bottom")
    ch = barras_horizontales(cm(ws, 9, 16) - 0.1, 11.2, '+0;"−"0;0')
    s = Series(Reference(ws, min_col=21, min_row=f0, max_row=f1), title="Cambio (pp)")
    ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=20, min_row=f0, max_row=f1))
    color_serie(s, ORO)
    s.invertIfNegative = False
    etiquetas(s, '+0.0;"−"0.0;0.0', size=8, posicion="outEnd")
    ch.x_axis.txPr = _rt(8, GRIS)
    ws.add_chart(ch, f"I{fh}")
    # advertencia
    fa = f1 + 2
    texto(ws, fa, 2, 16, "Es una sensibilidad del modelo, no un efecto causal.", size=10, bold=True, color=VINO,
          fondo=ORO1, alto=22, v="center", indent=1)
    texto(ws, fa + 1, 2, 16, "Escenario = (1 − f₁)(1 − f₂)·p00 + f₁(1 − f₂)·p10 + (1 − f₁)f₂·p01 + f₁f₂·p11, con "
          "f₁ = cobertura de alumbrado y f₂ = cobertura de parques sin atracos. p00 es la probabilidad media predicha "
          "hoy; p10, con el alumbrado resuelto para todos; p01, sin atracos en ningún parque; p11, con ambas palancas "
          "(hoja Datos_escenarios). Modelo: logit ponderado con perfil, delito registrado, hechos del entorno y "
          "alumbrado (Bienal 2025). Sirve para comparar territorios y priorizar; un piloto con línea base y grupo de "
          "comparación confirmaría el efecto.", size=9, color=TINTA, fondo=ORO1, indent=1)
    R["sim"] = {"bogota_cambio": f"Simulador!$F${fb}", "bogota_hoy": f"Simulador!$D${fb}",
                "bogota_esc": f"Simulador!$E${fb}"}
    imprimir(ws, area=f"A1:P{fa + 2}", paginas=1)


def hoja_diccionario(ws, D, R):
    cabecera(ws, "Diccionario", "Cada indicador y variable del libro: definición, unidad, fuente y año.", 9)
    bienal = "Encuesta Bienal de Cultura Ciudadana (SCRD)"
    emv = "Encuesta Mundial de Valores ola 8 (Datos para la Transparencia)"
    scj = "SCJ, Delito de alto impacto; SDP, población"
    l123 = "SCJ, Línea 123 (NUSE); SDP, población"
    ene = "2025, enero-agosto"
    pct, pct01 = "% de adultos", "% en el panel; 0/1 en los modelos"
    filas = [
        ("Indicador", "poblacion", "Población", "Población total proyectada de la localidad (cabecera más rural).",
         "habitantes", "SDP, proyecciones de población 2005-2035", "2025", "Panel_localidad"),
        ("Indicador", "zona_insegura", "Zona insegura", "Adultos que califican su zona como insegura o muy insegura "
         "(P66.8). Promedio ponderado con el factor de expansión. Resultado del modelo principal.", pct, bienal, "2025",
         "Panel_localidad, Indice_brecha, Modelos, Simulador"),
        ("Indicador", "ciudad_insegura", "Ciudad insegura", "Adultos que califican Bogotá como insegura o muy insegura "
         "(P74).", pct, bienal, "2025", "Panel_localidad, Resumen, Modelos"),
        ("Indicador", "ciudad_peor_que_antes", "Ciudad peor que antes", "Adultos que consideran que la seguridad de la "
         "ciudad está peor que antes (P77).", pct, bienal, "2025", "Panel_localidad"),
        ("Indicador", "miedo_espacio_publico", "Miedo en el espacio público", "Adultos que reportan miedo en el "
         "espacio público (P63).", pct, bienal, "2025", "Panel_localidad, Genero, Modelos"),
        ("Indicador", "alumbrado_malo", ETIQUETAS["alumbrado_malo"], "Califica como malo o muy malo el alumbrado "
         "público de su zona (P66.1). Palanca 1 del simulador.", pct01, bienal, "2025",
         "Panel_localidad, Modelos, Simulador"),
        ("Indicador", "parque_spa", ETIQUETAS["parque_spa"], "Reporta venta o consumo de drogas en el parque más "
         "cercano (P72.10 o P72.11).", pct01, bienal, "2025", "Panel_localidad, Modelos"),
        ("Indicador", "parque_acoso", "Acoso en el parque", "Reporta acoso en el parque más cercano (P72.12).", pct,
         bienal, "2025", "Panel_localidad"),
        ("Indicador", "presencio_acoso", ETIQUETAS["presencio_acoso"], "Presenció acoso a mujeres (P11.1 o P11.4).",
         pct01, bienal, "2025", "Panel_localidad, Modelos"),
        ("Indicador", "emv_victima", "Víctima de un delito", "Adultos que fueron víctimas de un delito en el último "
         "año (Q144). En los modelos de la EMV es la variable de control «victima».", pct01, emv, "2024",
         "Panel_localidad, Cifra_oculta, Genero"),
        ("Indicador", "emv_barrio_inseguro", "Barrio inseguro (EMV)", "Adultos que se sienten poco o nada seguros en "
         "su barrio (Q131, opciones 3 y 4).", pct01, emv, "2024", "Panel_localidad, Genero"),
        ("Indicador", "emv_no_sale_noche", "No sale de noche", "Adultos que prefirieron no salir de noche por "
         "seguridad (Q140).", pct01, emv, "2024", "Panel_localidad, Genero"),
        ("Indicador", "emv_teme_acoso_sexual", "Teme acoso sexual", "Adultos que temen mucho o bastante el acoso "
         "sexual (Q146_3, opciones 1 y 2).", pct01, emv, "2024", "Panel_localidad, Genero"),
        ("Indicador", "delitos_alto_impacto_100k", "Delitos de alto impacto", "Suma de 10 delitos registrados "
         "(homicidios, siete tipos de hurto, violencia intrafamiliar y delitos sexuales; sin lesiones personales) por "
         "100.000 habitantes.", "por 100.000 hab.", scj, ene, "Panel_localidad, Indice_brecha"),
        ("Indicador", "hurtos_100k", "Hurtos", "Hurto a personas, residencias, comercio, celulares, automotores, "
         "motocicletas y bicicletas por 100.000 habitantes.", "por 100.000 hab.", scj, ene, "Panel_localidad"),
        ("Indicador", "homicidios_100k", "Homicidios", "Homicidios registrados por 100.000 habitantes.",
         "por 100.000 hab.", scj, ene, "Panel_localidad, Modelos"),
        ("Indicador", "vif_ds_100k_mujeres", "VIF y delitos sexuales", "Violencia intrafamiliar más delitos sexuales "
         "por 100.000 mujeres.", "por 100.000 mujeres", scj, ene, "Panel_localidad"),
        ("Indicador", "incidentes_narcoticos_100k", "Llamadas 123 por narcóticos", "Incidentes reportados a la Línea "
         "123 por narcóticos por 100.000 habitantes.", "por 100.000 hab.", l123, ene, "Panel_localidad, Modelos"),
        ("Indicador", "incidentes_rinas_100k", "Llamadas 123 por riñas", "Incidentes reportados a la Línea 123 por "
         "riñas por 100.000 habitantes.", "por 100.000 hab.", l123, ene, "Panel_localidad"),
        ("Indicador", "incidentes_maltrato_mujer_100k", "Llamadas 123 por maltrato a mujer", "Incidentes reportados a "
         "la Línea 123 por maltrato a mujer por 100.000 habitantes.", "por 100.000 hab.", l123, ene, "Panel_localidad"),
        ("Indicador", "area_km2", "Área", "Área de la localidad.", "km²", "UAECD · IDECA, Localidad Bogotá D.C.",
         "Vigente", "Panel_localidad"),
        ("Indicador", "luminarias_km2_2019", "Luminarias por km²", "Luminarias de alumbrado público por km² de la "
         "localidad. Se usa solo como validación.", "luminarias por km²", "UAESP, alumbrado público por localidad",
         "2019, agosto (último publicado)", "Panel_localidad, Cifra_oculta"),
        ("Indicador", "ep_efectivo_m2_hab", "Espacio público efectivo", "Espacio público efectivo por habitante.",
         "m² por habitante", "DADEP, indicador de espacio público", "Último corte publicado", "Panel_localidad"),
        ("Serie", "casos (Serie_delitos)", "Casos registrados", "Casos de cada delito de alto impacto en Bogotá. "
         "Hurto a personas, residencias y automotores: Policía (SIEDCO); los demás: suma de las 20 localidades de la SCJ.",
         "casos", "Policía Nacional (SIEDCO); SCJ, Delito de alto impacto", "2018-2026, enero-agosto",
         "Serie_delitos, Resumen"),
        ("Serie", "indice_2018", "Índice 2018 = 100", "Casos del año / casos de 2018 × 100.", "índice",
         "Cálculo propio", "2018-2026, enero-agosto", "Serie_delitos"),
    ]
    for v in PERFIL + DELITO + HECHOS + CALIFICACIONES:
        if v in ("alumbrado_malo", "parque_spa", "presencio_acoso"):
            continue
        defin = {
            "mujer": ("1 si la persona es mujer (Bienal D1; EMV CS1).", "0/1", f"{bienal}; {emv}", "2025; 2024"),
            "edad": ("Edad en años; el efecto se lee por año adicional.", "años", f"{bienal}; {emv}", "2025; 2024"),
            "estrato": ("Estrato socioeconómico de la vivienda, 1 a 6; el efecto se lee por nivel.", "nivel 1 a 6",
                        f"{bienal}; {emv}", "2025; 2024"),
            "arrienda": ("1 si vive en arriendo (V4).", "0/1", bienal, "2025"),
            "hurtos_100k_miles": ("Hurtos por 100.000 hab. en la localidad de residencia, en miles: el efecto es por "
                                  "+1.000.", "miles por 100.000 hab.", scj, ene),
            "homicidios_100k": ("Homicidios por 100.000 hab. en la localidad de residencia: el efecto es por +1.",
                                "por 100.000 hab.", scj, ene),
            "narcoticos_100k_cientos": ("Llamadas 123 por narcóticos por 100.000 hab. en la localidad, en cientos: el "
                                        "efecto es por +100.", "cientos por 100.000 hab.", l123, ene),
            "parque_atracos": ("1 si reporta atracos en el parque más cercano (P72.13). Palanca 2 del simulador.",
                               "0/1", bienal, "2025"),
            "sin_parque": ("1 si no tiene un parque cerca (P67).", "0/1", bienal, "2025"),
            "conflictos_vecinos": ("Proporción de las 6 situaciones de conflicto vecinal (P53) que ocurren en su "
                                   "barrio: de ninguna (0) a todas (1).", "proporción 0 a 1", bienal, "2025"),
            "ventas_informales_malo": ("1 si califica como mala la situación de ventas informales en su zona (P66.9).",
                                       "0/1", bienal, "2025"),
        }[v]
        filas.append(("Variable de modelo", v, ETIQUETAS[v], defin[0], defin[1], defin[2], defin[3],
                      "Modelos" + (", Genero" if v in ("mujer", "edad", "estrato") else "")))
    propio = "Cálculo propio"
    filas += [
        ("Medida derivada", "ibs", "Índice de Brecha de Seguridad (IBS)", "z(% zona insegura) − z(ln delitos de alto "
         "impacto por 100.000) entre las 19 localidades urbanas. Positivo: más miedo del que explica el delito "
         "registrado. Intervalo de 90 % por bootstrap ponderado dentro de cada localidad (1.000 réplicas).",
         "desviaciones estándar", f"{propio} (Bienal 2025 + SCJ 2025)", "2025", "Indice_brecha, Cifra_oculta, Resumen"),
        ("Medida derivada", "prob_top5", "Probabilidad de top 5", "Proporción de réplicas bootstrap en que la "
         "localidad queda entre las 5 de mayor IBS.", "% de réplicas", propio, "2025", "Indice_brecha, Resumen"),
        ("Medida derivada", "razon", "Víctimas por delito registrado (cifra oculta)", "Víctimas estimadas (EMV 2024 × "
         "adultos SDP 2024) / delitos registrados por la SCJ en 2024 (11 tipos, enero-agosto × 12/8). Compara personas "
         "con hechos: es un orden de magnitud.", "víctimas por delito", f"{propio} (EMV + SCJ + SDP)", "2024",
         "Cifra_oculta, Resumen"),
        ("Medida derivada", "ame_pp", "Efecto marginal promedio (AME)", "Cambio promedio en la probabilidad del "
         "resultado al pasar la variable de 0 a 1 (o por la unidad indicada), con IC 95 % por bootstrap de "
         "conglomerados (localidades).", "puntos porcentuales (pp)", propio, "2025 (Bienal); 2024 (EMV)",
         "Modelos, Genero, Resumen"),
        ("Medida derivada", "auc", "AUC fuera de muestra", "Área bajo la curva ROC en validación cruzada estratificada "
         "repetida (25 pliegues). 0,5 = azar; 1 = predicción perfecta.", "0 a 1", propio, "2025", "Modelos, Resumen"),
        ("Medida derivada", "p_wild", "p wild cluster bootstrap", "p-valor del modelo lineal de probabilidad con wild "
         "cluster bootstrap (pesos de Webb), robusto con pocos conglomerados.", "0 a 1", propio, "2025", "Modelos"),
        ("Medida derivada", "rho / p_bh", "ρ de Spearman y p ajustado (BH)", "Correlación de rangos entre dos "
         "indicadores de las 19 localidades; p corregido por Benjamini-Hochberg sobre las 7 validaciones.",
         "-1 a 1; 0 a 1", propio, "2024-2025", "Cifra_oculta, Resumen"),
        ("Medida derivada", "p00, p10, p01, p11", "Escenarios del simulador", "Probabilidad media predicha de sentir "
         "insegura la zona hoy (p00), con alumbrado resuelto (p10), sin atracos en parques (p01) y con ambas (p11).",
         "% de adultos", propio, "2025", "Simulador, Datos_escenarios"),
    ]
    fh = 6
    encabezados(ws, fh, 2, ["Tipo", "Variable", "Nombre", "Definición", "Unidad", "Fuente", "Año / corte",
                            "Dónde aparece"], alto=30)
    anchos(ws, {"B": 17, "C": 26, "D": 30, "E": 58, "F": 18, "G": 30, "H": 18, "I": 24})
    for i, fila in enumerate(filas, start=1):
        f = fh + i
        fila_datos(ws, f, 2, list(fila), [TXT] * 8)
        for c in range(2, 10):
            ws.cell(f, c).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
        ws.cell(f, 3).font = F(9, False, GRIS)
        ws.cell(f, 4).font = F(9.5, True, TINTA)
        ws.row_dimensions[f].height = max([20] + [_alto(t, w, 9.5) for t, w in
                                                  zip(fila, (17, 26, 30, 58, 18, 30, 18, 24))])
    tabla_excel(ws, "tDiccionario", f"B{fh}:I{fh + len(filas)}")
    ws.freeze_panes = f"D{fh + 1}"
    imprimir(ws, titulos=f"{fh}:{fh}")


def hoja_fuentes(ws, D, R):
    res = D["res"]
    cabecera(ws, "Fuentes", "Conjuntos de datos oficiales usados. Cada uno se descarga desde su servicio con caché "
             "local y registro de URL, fecha y sha1 (src/fuentes.py).", 7)
    anchos(ws, {"B": 34, "C": 40, "D": 34, "E": 44, "F": 14, "G": 30})
    uso = {
        "scj_delitos_localidad": "11 delitos por localidad, enero-agosto 2018-2026",
        "scj_incidentes_localidad": "Llamadas 123 por narcóticos, riñas y maltrato a mujer, por localidad",
        "scj_incidentes_upz": "Llamadas 123 por UPZ (mapas del visor)",
        "ebcc_2025": f"Microdatos: percepción y entorno ({es(res['n_bienal'], 0)} adultos)",
        "emv_2024": f"Microdatos: victimización y género ({es(res['n_emv_bogota'], 0)} encuestas en Bogotá)",
        "sdp_poblacion_localidad": "Denominadores por localidad, sexo y edad",
        "sdp_poblacion_upz": "Denominadores por UPZ",
        "ideca_localidades": "Límites y área de las localidades",
        "uaesp_alumbrado": "Validación del alumbrado (último corte: agosto de 2019)",
        "dadep_espacio_publico": "Contexto: espacio público efectivo",
    }
    fh = 6
    encabezados(ws, fh, 2, ["Entidad", "Conjunto de datos", "Uso en el proyecto", "Portal (enlace)",
                            "Descarga directa", "Archivo local (data/crudos/)"], alto=30)
    for i, (clave, f) in enumerate(FUENTES.items(), start=1):
        ff = fh + i
        fila_datos(ws, ff, 2, [f["entidad"], f["conjunto"], uso.get(clave, ""), f["portal"], "Abrir", f["archivo"]],
                   [TXT] * 6)
        for c in range(2, 8):
            ws.cell(ff, c).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
        for col, url in ((5, f["portal"]), (6, f["url"])):
            c = ws.cell(ff, col)
            c.hyperlink = url
            c.font = F(9 if col == 5 else 9.5, False, AZUL, underline="single")
        ws.cell(ff, 7).font = F(8.5, False, GRIS)
        ws.row_dimensions[ff].height = max(20, _alto(f["entidad"], 34, 9.5), _alto(f["conjunto"], 40, 9.5),
                                           _alto(uso.get(clave, ""), 34, 9.5), _alto(f["portal"], 44, 9))
    fu = fh + len(FUENTES)
    tabla_excel(ws, "tFuentes", f"B{fh}:G{fu}")
    ws.freeze_panes = f"B{fh + 1}"
    texto(ws, fu + 2, 2, 7, "La localidad de cada encuesta de la EMV no viene en el archivo publicado: se recuperó del "
          "tablero oficial de Datos para la Transparencia (data/crudos/emv_localidad_por_registro.csv) y se verificó "
          "con la ficha técnica (96 encuestas por localidad). Los datos son de las entidades citadas y se usan bajo "
          "sus condiciones de datos abiertos.", size=8.5, color=GRIS, italic=True)
    imprimir(ws, titulos=f"{fh}:{fh}")


def hoja_bitacora(ws, D, R):
    cabecera(ws, "Bitácora de limpieza", "Cada paso de lectura, formato, llave territorial, recodificación e "
             "integración, tal como lo registró el pipeline (src/limpieza.py).", 5)
    anchos(ws, {"B": 6, "C": 22, "D": 18, "E": 96})
    B = D["bitacora_limpieza"]
    fh = 6
    encabezados(ws, fh, 2, ["N.º", "Fuente", "Paso", "Detalle"], alto=28)
    for i, r in enumerate(B.itertuples(), start=1):
        ff = fh + i
        fila_datos(ws, ff, 2, [i, r.fuente, r.paso, r.detalle], [CEN, TXT, TXT, TXT])
        ws.cell(ff, 5).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
        ws.cell(ff, 3).font = F(9.5, True, TINTA)
        ws.row_dimensions[ff].height = max(19, _alto(r.detalle, 96, 9.5))
    tabla_excel(ws, "tBitacora", f"B{fh}:E{fh + len(B)}")
    ws.freeze_panes = f"B{fh + 1}"
    texto(ws, fh + len(B) + 2, 2, 5, "Fuente: outputs/tablas/bitacora_limpieza.csv.", size=8.5, color=GRIS, italic=True)
    imprimir(ws, titulos=f"{fh}:{fh}")


def hoja_resumen(ws, D, R):
    res = D["res"]
    cabecera(ws, "Resumen", "El hurto casi no bajó, la violencia sube y el miedo no baja. Cifras clave y los cuatro hallazgos.", 16)
    for i in range(2, 17):
        ws.column_dimensions[L(i)].width = 2.2 if i in (5, 9, 13) else 11
    poner(ws, 6, 2, "CIFRAS CLAVE", size=8.5, bold=True, color=GRIS, v="bottom")
    hp = res["hurto_personas"]
    am = res["ame_hechos"]["parque_atracos"]
    mu = res["emv_mujer_ame"]["teme_acoso_sexual"]
    rho = res["ibs_vs_cifra_oculta"]
    auc = res["auc"]
    bloques = list(D["auc"]["bloque"])
    tarjetas = [
        ("REGISTRO · POLICÍA (SIEDCO)", AZUL, f"={R['hurto_cambio']}", VAR,
         f"en el hurto a personas, enero-agosto 2019 → 2026 ({es(hp['2019'], 0)} → {es(hp['2026'], 0)} casos). La capa "
         f"abierta de la SCJ dice {es(res['hurto_personas_capa']['cambio_pct'], 0)} %: tiene un quiebre en 2023.",
         "Serie_delitos"),
        ("PERCEPCIÓN · BIENAL 2025", ORO, res["ciudad_insegura_pct"] / 100, PCT,
         "de los adultos califica Bogotá como insegura o muy insegura.", "resultados.json (Bienal 2025, ponderado)"),
        ("PERCEPCIÓN · BIENAL 2025", ORO,
         f'=SUMIFS(Datos_escenarios!$I${R["esc"]["f0"]}:$I${R["esc"]["f1"]},Datos_escenarios!$B${R["esc"]["f0"]}:'
         f'$B${R["esc"]["f1"]},"Total",Datos_escenarios!$C${R["esc"]["f0"]}:$C${R["esc"]["f1"]},0)', PCT,
         "dice lo mismo de su propia zona: el resultado que se modela.", "Datos_escenarios (Bienal 2025, ponderado)"),
        ("CIFRA OCULTA · EMV 2024 + SCJ", VINO, f"={R['cifra']['bogota']}", "0.0",
         f"víctimas por cada delito de alto impacto registrado (de {es(res['cifra_oculta_max'][1])} en "
         f"{res['cifra_oculta_max'][0]} a {es(res['cifra_oculta_min'][1])} en {res['cifra_oculta_min'][0]}).",
         "Cifra_oculta"),
        ("ENTORNO · MODELO PRINCIPAL", ORO, f"={R['ame'][('hechos', 'parque_atracos')]}", PP,
         f"en la probabilidad de sentir insegura la zona si hay atracos en el parque cercano (IC 95 % "
         f"{es(am['ic_inf'])} a {es(am['ic_sup'])}).", "Modelos"),
        ("GÉNERO · EMV 2024", MUJER, f"={R['genero']['teme_acoso_sexual']}", PP,
         f"de temor al acoso sexual por ser mujer, a igual edad, estrato y victimización (IC 95 % {es(mu['ic_inf'])} "
         f"a {es(mu['ic_sup'])}).", "Genero"),
        ("TERRITORIO · CONTROL", ROJO, res["ibs_vs_cifra_oculta_parcial"]["rho"], '"ρ = "0.00;"ρ = −"0.00',
         f"entre el Índice de Brecha y la cifra oculta al controlar el delito registrado: la de {es(rho['rho'], 2)} era "
         "mecánica, porque ambos usan el mismo registro.", "Cifra_oculta"),
        ("PREDICCIÓN · AUC", AZUL, f"={R['auc'][bloques[1]]}-{R['auc'][bloques[0]]}", '+0.000;"−"0.000',
         f"de AUC al sumar el delito registrado al perfil ({es(auc[bloques[0]], 3)} → {es(auc[bloques[1]], 3)}); "
         f"con el entorno llega a {es(auc['Todo'], 3)}.", "Modelos"),
    ]
    for k, (etq, acento, valor, fmt, desc, fuente) in enumerate(tarjetas):
        r0 = 7 + (k // 4) * 5
        c0 = 2 + (k % 4) * 4
        for rr in range(r0, r0 + 4):
            ws.merge_cells(start_row=rr, start_column=c0, end_row=rr, end_column=c0 + 2)
            for cc in range(c0, c0 + 3):
                ws.cell(rr, cc).fill = relleno(FONDO)
        for cc in range(c0, c0 + 3):
            ws.cell(r0, cc).border = Border(top=Side(style="thick", color=acento))
        poner(ws, r0, c0, etq, size=7.5, bold=True, color=GRIS, v="bottom", fondo=FONDO, indent=1)
        poner(ws, r0 + 1, c0, valor, size=24, bold=True, color=TINTA, fmt=fmt, h="left", fondo=FONDO, indent=1)
        poner(ws, r0 + 2, c0, desc, size=8.5, color=TINTA, wrap=True, v="top", h="left", fondo=FONDO, indent=1)
        poner(ws, r0 + 3, c0, f"Fuente: {fuente}", size=7, italic=True, color=GRIS, v="center", fondo=FONDO, indent=1)
        ws.row_dimensions[r0].height = 22
        ws.row_dimensions[r0 + 1].height = 40
        ws.row_dimensions[r0 + 2].height = 48
        ws.row_dimensions[r0 + 3].height = 17
        ws.row_dimensions[r0 + 4].height = 12
    # hallazgos
    vb = res["emv_por_sexo"]["victima"]
    em = res["emv_mujer_ame"]
    cv = res["ame_hechos"]["conflictos_vecinos"]
    lw = D["lpm_wild"].set_index("variable").loc["hurtos_100k_miles", "p_wild"]
    hc = res["hurto_personas_capa"]
    hall = [
        ("El hurto no bajó como parecía.",
         f"La capa abierta de la SCJ muestra el hurto a personas {es(hc['cambio_2022_pct'], 0)} % de 2022 a 2026; el registro "
         f"de la Policía, {es(hp['cambio_2022_pct'], 0)} % (y {signo(hp['cambio_2022_2023_pct'], 0)} % en 2023). De 2018 a 2022 "
         f"la capa cuenta {es(hc['razon_min'], 2)} a {es(hc['razon_max'], 2)} veces lo de la Policía y desde 2023 coincide: es un "
         "quiebre de serie, no un cambio en la calle. La encuesta del DANE lo confirma (la denuncia del hurto subió de 36 % a 43 %). "
         "Homicidios, delitos sexuales y violencia intrafamiliar suben en series validadas."),
        ("La ciudad no ve buena parte de su delito.",
         f"Hay unas {es(res['cifra_oculta_bogota'])} víctimas por cada delito de alto impacto registrado, de "
         f"{es(res['cifra_oculta_max'][1])} en {res['cifra_oculta_max'][0]} a {es(res['cifra_oculta_min'][1])} en "
         f"{res['cifra_oculta_min'][0]}. Las víctimas que reporta la encuesta no siguen al delito registrado entre localidades "
         f"(ρ = {es(res['victimas_vs_registro']['rho'], 2)}). La relación entre el Índice de Brecha y la cifra oculta "
         f"(ρ = {es(rho['rho'], 2)}) es mecánica: al controlar el delito registrado queda en "
         f"{es(res['ibs_vs_cifra_oculta_parcial']['rho'], 2)}."),
        ("El barrio se siente por lo que pasa en él.",
         f"Ver atracos en el parque cercano suma {signo(am['ame_pp'])} pp a la probabilidad de sentir insegura la "
         f"zona y los conflictos vecinales hasta {signo(cv['ame_pp'])} pp. El hurto registrado de la localidad no tiene "
         f"efecto (p wild = {es(lw, 2)}) y casi no mejora la predicción: AUC {es(auc[bloques[0]], 3)} → "
         f"{es(auc[bloques[1]], 3)}. Con el entorno llega a {es(auc['Todo'], 3)}."),
        ("Las mujeres pagan el miedo con autonomía.",
         f"A igual edad, estrato y victimización, ser mujer suma {signo(em['teme_acoso_sexual']['ame_pp'])} pp de "
         f"temor al acoso sexual, {signo(em['no_sale_noche']['ame_pp'])} pp de evitar salir de noche y "
         f"{signo(em['barrio_inseguro']['ame_pp'])} pp de sentir inseguro el barrio, aunque ellas reportan menos "
         f"victimización ({es(vb['mujeres'])} % frente a {es(vb['hombres'])} %)."),
    ]
    f = 17
    poner(ws, f, 2, "CUATRO HALLAZGOS", size=8.5, bold=True, color=GRIS, v="bottom")
    ws.row_dimensions[f].height = 22
    for i, (tit, txt) in enumerate(hall, start=1):
        f += 1
        ws.merge_cells(start_row=f, start_column=2, end_row=f + 1, end_column=2)
        poner(ws, f, 2, i, size=24, bold=True, color=ROJO, h="center", v="top")
        ws.merge_cells(start_row=f, start_column=3, end_row=f, end_column=16)
        poner(ws, f, 3, tit, size=11, bold=True, color=TINTA, v="bottom")
        ws.row_dimensions[f].height = 22
        f += 1
        texto(ws, f, 3, 16, txt, size=9.5, color=GRIS)
        for cc in range(2, 17):
            ws.cell(f, cc).border = Border(bottom=FINA)
        f += 1
        ws.row_dimensions[f].height = 8
    # prioridad territorial
    f += 1
    poner(ws, f, 2, "DÓNDE INTERVENIR PRIMERO · TOP 5 DEL ÍNDICE DE BRECHA", size=8.5, bold=True, color=GRIS, v="bottom")
    ws.row_dimensions[f].height = 22
    f += 1
    heads = [(2, 2, "Puesto"), (3, 5, "Localidad"), (6, 8, "Índice de Brecha"), (9, 12, "IC 90 %"),
             (13, 16, "Top 5 en las réplicas bootstrap")]
    for c1, c2, t in heads:
        if c2 > c1:
            ws.merge_cells(start_row=f, start_column=c1, end_row=f, end_column=c2)
        for cc in range(c1, c2 + 1):
            ws.cell(f, cc).fill = relleno(VINO)
        poner(ws, f, c1, t, size=9, bold=True, color=BLANCO, h="center", fondo=VINO)
    ws.row_dimensions[f].height = 24
    ib = R["ibs"]
    for k in range(5):
        f += 1
        fi = ib["f0"] + k
        # el IC va en dos celdas numéricas ("inferior" y "a superior") para no depender del idioma del Excel
        celdas = [(2, 2, f"=Indice_brecha!B{fi}", "0", "center"), (3, 5, f"=Indice_brecha!D{fi}", None, "left"),
                  (6, 8, f"=Indice_brecha!J{fi}", SIG2, "center"),
                  (9, 10, f"=Indice_brecha!K{fi}", SIG2, "right"),
                  (11, 12, f"=Indice_brecha!L{fi}", '"a  "+0.00;"a  −"0.00', "left"),
                  (13, 16, f"=Indice_brecha!N{fi}", "0%", "left")]
        for c1, c2, val, fmt, h in celdas:
            if c2 > c1:
                ws.merge_cells(start_row=f, start_column=c1, end_row=f, end_column=c2)
            poner(ws, f, c1, val, size=10, bold=c1 in (3, 6), color=TINTA, fmt=fmt, h=h,
                  indent=1 if h == "left" else 0)
            for cc in range(c1, c2 + 1):
                ws.cell(f, cc).border = Border(bottom=FINA)
        ws.row_dimensions[f].height = 20
    ws.conditional_formatting.add(f"M{f - 4}:M{f}", DataBarRule(start_type="num", start_value=0, end_type="num",
                                                                 end_value=1, color=ORO3, showValue=True,
                                                                 minLength=0, maxLength=100))
    f += 2
    texto(ws, f, 2, 16, f"Bogotá DataJam 5 · equipo #16 The data squad. Cifras de outputs/resultados.json y "
          "outputs/tablas/; las celdas con fórmula se recalculan desde las otras hojas.", size=8, color=GRIS,
          italic=True)
    imprimir(ws, area=f"A1:P{f}", paginas=1)


def hoja_portada(ws, D, R):
    res = D["res"]
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 90
    anchos(ws, {"A": 3, "B": 4, "C": 24, "D": 70, "E": 16})
    poner(ws, 2, 3, "BOGOTÁ DATAJAM 5  ·  2026  ·  LIBRO DE DATOS", size=9, bold=True, color=VINO, v="bottom")
    ws.row_dimensions[2].height = 22
    ws.merge_cells("C3:E3")
    poner(ws, 3, 3, "El miedo que no baja", size=34, bold=True, color=ROJO, v="center")
    ws.row_dimensions[3].height = 54
    ws.merge_cells("C4:E4")
    poner(ws, 4, 3, "Inseguridad percibida frente a delito registrado en Bogotá", size=14, color=GRIS, v="top")
    ws.row_dimensions[4].height = 26
    for c in range(3, 6):
        ws.cell(5, c).fill = relleno(ROJO)
    ws.row_dimensions[5].height = 3
    ws.row_dimensions[6].height = 14
    ws.merge_cells("C7:E7")
    poner(ws, 7, 3, f"{es(res['n_bienal'], 0)} adultos de la Bienal 2025  ·  {es(res['n_emv_bogota'], 0)} encuestas "
          f"de la EMV 2024 en Bogotá  ·  19 localidades urbanas  ·  {len(FUENTES)} conjuntos de datos oficiales",
          size=9.5, color=GRIS)
    ws.row_dimensions[7].height = 20
    f = 9
    poner(ws, f, 3, "PREGUNTA ANALÍTICA", size=8.5, bold=True, color=GRIS, v="bottom")
    texto(ws, f + 1, 3, 5, PREGUNTA, size=13, bold=True, color=TINTA, alto=44)
    hip = [("H1", "La percepción del barrio depende más del entorno inmediato que del delito registrado en la localidad."),
           ("H2", "Parte de la distancia entre miedo y registro es subregistro: donde hay más miedo que delito "
                  "registrado, más delito queda fuera de las cifras."),
           ("H3", "A igual victimización, las mujeres restringen más su vida y temen más el acoso sexual.")]
    f += 2
    for k, t in hip:
        poner(ws, f, 3, k, size=9.5, bold=True, color=VINO, h="right", v="top", indent=1)
        texto(ws, f, 4, 5, t, size=9.5, color=GRIS)
        f += 1
    f += 1
    poner(ws, f, 3, "EQUIPO #16 · THE DATA SQUAD", size=8.5, bold=True, color=GRIS, v="bottom")
    ws.row_dimensions[f].height = 22
    for n in EQUIPO:
        f += 1
        poner(ws, f, 3, n, size=10.5, color=TINTA)
        ws.merge_cells(start_row=f, start_column=3, end_row=f, end_column=4)
        ws.row_dimensions[f].height = 19
    f += 2
    poner(ws, f, 3, "CONTENIDO", size=8.5, bold=True, color=GRIS, v="bottom")
    ws.row_dimensions[f].height = 22
    for i, (hoja, desc) in enumerate(HOJAS[1:], start=1):
        f += 1
        poner(ws, f, 2, i, size=8.5, color=GRIS_NS, h="right")
        c = poner(ws, f, 3, hoja, size=10, bold=True, color=AZUL, indent=1)
        c.font = F(10, True, AZUL, underline="single")
        vinculo(c, hoja)
        poner(ws, f, 4, desc, size=9.5, color=GRIS, indent=1)
        for cc in range(2, 6):
            ws.cell(f, cc).border = Border(bottom=FINA)
        ws.row_dimensions[f].height = 20
    f += 2
    poner(ws, f, 3, "CÓMO LEER LOS COLORES", size=8.5, bold=True, color=GRIS, v="bottom")
    ws.row_dimensions[f].height = 22
    for color, t in ((ORO, "Oro: lo que la gente percibe o vive (encuestas de percepción, entorno y victimización)."),
                     (AZUL, "Azul: lo que registran las autoridades (SCJ, Línea 123)."),
                     (MUJER, "Morado y verde: mujeres y hombres."),
                     (ORO1, "Crema: celdas editables del simulador."),
                     (GRIS_NS, "Gris claro: efectos cuyo intervalo de confianza cruza 0 (no significativos).")):
        f += 1
        poner(ws, f, 2, None, fondo=color)
        poner(ws, f, 3, t, size=9.5, color=TINTA, indent=1)
        ws.merge_cells(start_row=f, start_column=3, end_row=f, end_column=5)
        ws.row_dimensions[f].height = 18
    f += 2
    texto(ws, f, 3, 5, "Reproducible: todas las cifras salen de outputs/ y data/procesados/ del repositorio, y el libro "
          "se regenera con «python src/excel.py». El simulador, el Índice de Brecha, la cifra oculta de Bogotá, el ρ "
          "de Spearman y los índices 2018 = 100 son fórmulas vivas.", size=9, color=GRIS)
    f += 2
    texto(ws, f, 3, 5, "Proyecto académico para el Bogotá DataJam 5. No es un producto oficial de la Alcaldía de "
          "Bogotá.", size=9.5, bold=True, color=VINO, fondo=ORO1, alto=26, v="center", indent=1)
    imprimir(ws, area=f"A1:E{f + 1}", vertical=True, paginas=1)


# ================================================================ libro
def construir_excel(destino: Path = DESTINO, recalcular: bool = True) -> Path:
    D = cargar()
    R: dict = {}
    wb = Workbook()
    wb.remove(wb.active)
    hojas = {n: wb.create_sheet(n) for n, _ in HOJAS}
    for n, ws in hojas.items():
        ws.sheet_properties.tabColor = COLOR_PESTANA.get(n, VINO)
    # orden de construcción: primero las hojas a las que otras hacen referencia
    hoja_datos_escenarios(hojas["Datos_escenarios"], D, R)
    hoja_panel(hojas["Panel_localidad"], D, R)
    hoja_indice(hojas["Indice_brecha"], D, R)
    hoja_cifra(hojas["Cifra_oculta"], D, R)
    hoja_modelos(hojas["Modelos"], D, R)
    hoja_genero(hojas["Genero"], D, R)
    hoja_serie(hojas["Serie_delitos"], D, R)
    hoja_simulador(hojas["Simulador"], D, R)
    hoja_diccionario(hojas["Diccionario"], D, R)
    hoja_fuentes(hojas["Fuentes"], D, R)
    hoja_bitacora(hojas["Bitacora"], D, R)
    hoja_resumen(hojas["Resumen"], D, R)
    hoja_portada(hojas["Portada"], D, R)
    wb.active = 0
    wb.calculation.fullCalcOnLoad = True
    wb.properties.title = "El miedo que no baja · Libro de datos"
    wb.properties.creator = "The data squad (Bogotá DataJam 5, equipo #16)"
    wb.properties.subject = "Inseguridad percibida frente a delito registrado en Bogotá"
    destino.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)
    if recalcular:
        guardar_valores_con_excel(destino)
    return destino


def guardar_valores_con_excel(ruta: Path) -> bool:
    """Abre el libro en Excel (invisible), recalcula todo y guarda, para que cada fórmula lleve su valor."""
    if sys.platform != "win32":
        return False
    p = str(ruta).replace("'", "''")
    ps = (
        "$ErrorActionPreference='Stop';"
        "$x=New-Object -ComObject Excel.Application;$x.Visible=$false;$x.DisplayAlerts=$false;"
        "try{"
        f"$wb=$x.Workbooks.Open('{p}');$x.CalculateFull();"
        "$wb.Worksheets.Item('Portada').Activate();$wb.Save();$wb.Close($false);"
        "[void][Runtime.InteropServices.Marshal]::ReleaseComObject($wb)"
        "}finally{$x.Quit();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($x);"
        "[GC]::Collect();[GC]::WaitForPendingFinalizers()}"
    )
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        return False
    if r.returncode != 0:
        print("Aviso: no se pudo recalcular con Excel; el libro se recalcula al abrirlo.", r.stderr.strip()[:300])
        return False
    return True


if __name__ == "__main__":
    ruta = construir_excel(recalcular="--sin-excel" not in sys.argv)
    print(f"Libro escrito en {ruta}")
