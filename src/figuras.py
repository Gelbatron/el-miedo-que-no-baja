"""
Figuras estáticas (PNG, 200 dpi) para el notebook, el README, la nota técnica y el pitch.
Misma identidad del visor: oro = lo que se siente, azul = lo que se registra.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

from territorio import LOCALIDADES  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "outputs" / "figuras"
# Paleta del visor: oro = lo que se siente, azul = lo que se registra, rojo para títulos
PERC, REG, MUJ, HOM, NEUTRO, TINTA, TINTA2, LINEA = "#d99a16", "#3366cc", "#8e44c8", "#2a9d4b", "#b9b9b9", "#1e1e1e", "#4b4b4b", "#dcdcdc"
ROJO = "#bf0a00"
RAMPA_P = ListedColormap(["#fff5db", "#fadd95", "#f0bf4f", "#d99a16", "#9c6a08"])
RAMPA_R = ListedColormap(["#dde7f8", "#a9c1ee", "#6d95e0", "#3366cc", "#1f3f8a"])

# Tipografías del visor (OFL, incluidas en assets/fuentes); si faltan, se usa la fuente por defecto
FUENTES = Path(__file__).resolve().parents[1] / "assets" / "fuentes"
_f = {n: FUENTES / f"{n}.ttf" for n in ("Montserrat-ExtraBold", "WorkSans-Regular", "WorkSans-SemiBold")}
if all(r.exists() for r in _f.values()):
    font_manager.fontManager.addfont(str(_f["WorkSans-Regular"]))
    CUERPO = "Work Sans"
    TITULO = font_manager.FontProperties(fname=str(_f["Montserrat-ExtraBold"]))
    NEGRITA = font_manager.FontProperties(fname=str(_f["WorkSans-SemiBold"]))
else:
    CUERPO, TITULO, NEGRITA = "DejaVu Sans", font_manager.FontProperties(weight="bold"), font_manager.FontProperties(weight="bold")

plt.rcParams.update({
    "font.family": CUERPO, "font.size": 10, "axes.edgecolor": LINEA, "axes.labelcolor": TINTA2,
    "xtick.color": TINTA2, "ytick.color": TINTA2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#ececec", "grid.linewidth": .8, "axes.titlesize": 12,
    "axes.titlelocation": "left", "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def _titulo(ax, texto, fontsize=12.5, **kw):
    """Título en Montserrat rojo, como los encabezados del visor."""
    tp = TITULO.copy()
    tp.set_size(fontsize)
    return ax.set_title(texto, fontproperties=tp, color=ROJO, pad=12, **kw)


def _guardar(fig, nombre):
    FIG.mkdir(parents=True, exist_ok=True)
    ruta = FIG / f"{nombre}.png"
    fig.savefig(ruta, facecolor="white")
    plt.close(fig)
    return ruta


def serie(validada: pd.DataFrame):
    """Serie validada (src/validacion_registro.py): hurto a personas del SIEDCO y, punteada, la capa SCJ con su quiebre."""
    s = validada.pivot(index="codigo", columns="anio", values="casos")
    capa = validada[validada["codigo"] == "HP"].set_index("anio")["casos_capa_scj"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.axvspan(2019.55, 2021.45, color=TINTA, alpha=0.06, lw=0)
    ax.text(2020.5, 192, "Pandemia", ha="center", va="top", fontsize=8.5, color=TINTA2)
    yc = capa / capa.loc[2018] * 100
    ax.plot(yc.index, yc.values, color=REG, lw=1.6, ls=(0, (3, 2)), alpha=0.75)
    finales = [[yc.iloc[-1], yc.index[-1], f"Hurto, capa abierta SCJ {yc.iloc[-1]:.0f}"]]
    for cod, nombre, col in (("HP", "Hurto a personas, Policía", REG), ("VI", "Violencia intrafamiliar", MUJ), ("DS", "Delitos sexuales", PERC)):
        y = s.loc[cod].dropna() / s.loc[cod, 2018] * 100
        ax.plot(y.index, y.values, color=col, lw=2.2, marker="o", ms=4)
        finales.append([y.iloc[-1], y.index[-1], f"{nombre} {y.iloc[-1]:.0f}"])
    ax.annotate("En 2023 la capa cambia de escala: antes\ncontaba 2,3 a 2,6 veces lo de la Policía", (2023, yc.loc[2023]), xytext=(2023.25, 14),
                fontsize=8, color=TINTA2, arrowprops=dict(arrowstyle="-", color=TINTA2, lw=0.8))
    finales.sort()  # etiquetas sin choque: mínimo 9 puntos de índice entre una y otra
    for i in range(1, len(finales)):
        finales[i][0] = max(finales[i][0], finales[i - 1][0] + 9)
    for yy, xx, txt in finales:
        ax.annotate(txt, (xx, yy), xytext=(8, 0), textcoords="offset points", va="center", color=TINTA, fontsize=9, fontproperties=NEGRITA)
    ax.axhline(100, color=TINTA2, lw=1)
    ax.set_xlim(2017.7, 2029.6)  # aire a la derecha para las etiquetas finales
    ax.set_xticks(range(2018, 2027, 2))
    ax.spines["bottom"].set_bounds(2018, 2026)
    ax.set_ylim(0, 200)
    _titulo(ax, "Delitos registrados en Bogotá, enero-agosto (índice 2018 = 100)")
    ax.text(0, -0.16, "Fuentes: Policía Nacional (SIEDCO, datos.gov.co) para hurto a personas; SCJ, Delitos de alto impacto, para "
            "violencia intrafamiliar y delitos sexuales (validadas con SIEDCO).", transform=ax.transAxes, fontsize=7.5, color=TINTA2)
    return _guardar(fig, "fig1_serie_delitos")


def mapas(geo, panel: pd.DataFrame):
    g = geo[geo["localidad"] != 20].merge(panel, on="localidad")
    fig, axs = plt.subplots(1, 2, figsize=(8.5, 7))
    for ax, col, cmap, titulo in ((axs[0], "zona_insegura", RAMPA_P, "Califica mala la seguridad\nde su zona (%, Bienal 2025)"),
                                  (axs[1], "delitos_alto_impacto_100k", RAMPA_R, "Delitos de alto impacto por\n100.000 hab. (SCJ, ene-ago 2025)")):
        g["q"] = pd.qcut(g[col], 5, labels=False)
        g.plot(column="q", cmap=cmap, ax=ax, edgecolor="white", linewidth=.6)
        ax.set_axis_off()
        _titulo(ax, titulo, fontsize=10.5)
        cortes = np.quantile(g[col], [0, .2, .4, .6, .8, 1])
        for i in range(5):
            ax.add_patch(plt.Rectangle((0.70, 0.02 + i * 0.045), 0.05, 0.035, transform=ax.transAxes, color=cmap(i)))
            ax.text(0.77, 0.035 + i * 0.045, f"{cortes[i]:,.0f}–{cortes[i + 1]:,.0f}".replace(",", "."), transform=ax.transAxes, fontsize=7.5, va="center")
    fig.suptitle("Percepción y registro no dibujan el mismo mapa", x=0.02, y=1.03, ha="left", fontproperties=TITULO.copy(), color=ROJO, fontsize=14)
    return _guardar(fig, "fig2_mapas_percepcion_registro")


def efectos(ame: pd.DataFrame, etiquetas: dict, nombre="fig3_efectos_marginales", titulo=None):
    d = ame.copy()
    d["etiqueta"] = d["variable"].map(etiquetas)
    d = d.sort_values("ame_pp")
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(d) + 1))
    for i, r in enumerate(d.itertuples()):
        sig = r.ic_inf > 0 or r.ic_sup < 0
        col = (PERC if r.ame_pp > 0 else REG) if sig else NEUTRO
        ax.plot([r.ic_inf, r.ic_sup], [i, i], color=col, lw=2.5, solid_capstyle="round")
        ax.plot(r.ame_pp, i, "o", color=col, ms=7, mec="white")
        ax.text(ax.get_xlim()[1] if False else d["ic_sup"].max() + 2, i, f"{r.ame_pp:+.1f}".replace(".", ",") + ("" if sig else " n.s."),
                va="center", fontsize=8.5, color=TINTA2)
    ax.axvline(0, color=TINTA2, lw=1)
    ax.set_yticks(range(len(d)), d["etiqueta"])
    ax.set_xlabel("Efecto marginal promedio (puntos porcentuales) e IC 95 %")
    _titulo(ax, titulo or "Qué explica sentir insegura la zona (logit ponderado, Bienal 2025)")
    ax.grid(axis="y", visible=False)
    return _guardar(fig, nombre)


def auc(tabla: pd.DataFrame):
    d = tabla.iloc[::-1]
    col = [PERC if any(k in b for k in ("hechos", "calificación", "Todo")) else (REG if "delito" in b else NEUTRO) for b in d["bloque"]]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.barh(d["bloque"], d["auc"], color=col, height=.55)
    for i, v in enumerate(d["auc"]):
        ax.text(v + .004, i, f"{v:.3f}".replace(".", ","), va="center", fontsize=9)
    ax.set_xlim(0.5, 0.85)
    _titulo(ax, "Capacidad predictiva fuera de muestra (AUC, validación cruzada)")
    ax.grid(axis="y", visible=False)
    return _guardar(fig, "fig4_auc_bloques")


def _etiquetar(ax, xs, ys, nombres, fontsize=7.5):
    """Etiquetas de puntos sin choques: prueba posiciones alrededor del punto y toma la primera libre."""
    fig = ax.figure
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    puntos = [ax.transData.transform((x, y)) for x, y in zip(xs, ys)]
    ocupado = [((px - 5, py - 5), (px + 5, py + 5)) for px, py in puntos]
    opciones = [((5, 4), "left", "bottom"), ((5, -4), "left", "top"), ((-5, 4), "right", "bottom"), ((-5, -4), "right", "top"),
                ((0, 8), "center", "bottom"), ((0, -8), "center", "top"), ((8, 14), "left", "bottom"), ((8, -14), "left", "top")]
    caja_ax = ax.get_window_extent(rend)
    for (x, y), nombre in sorted(zip(zip(xs, ys), nombres), key=lambda t: -t[0][1]):
        for desp, ha, va in opciones:
            t = ax.annotate(nombre, (x, y), xytext=desp, textcoords="offset points", fontsize=fontsize, color=TINTA, ha=ha, va=va)
            b = t.get_window_extent(rend).expanded(1.04, 1.1)
            dentro = caja_ax.x0 <= b.x0 and b.x1 <= caja_ax.x1 and caja_ax.y0 <= b.y0 and b.y1 <= caja_ax.y1
            libre = all(b.x1 < a[0] or b.x0 > c[0] or b.y1 < a[1] or b.y0 > c[1] for a, c in ocupado)
            if dentro and libre:
                break
            t.remove()
        else:
            t = ax.annotate(nombre, (x, y), xytext=(5, 4), textcoords="offset points", fontsize=fontsize, color=TINTA)
            b = t.get_window_extent(rend)
        ocupado.append(((b.x0, b.y0), (b.x1, b.y1)))


def brecha_cifra(ibs: pd.DataFrame, co: pd.DataFrame, rho: float, rho_parcial: float | None = None):
    m = ibs.merge(co[["localidad", "razon"]], on="localidad")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(m["razon"], m["ibs"], s=60, c=[PERC if v > 0 else REG for v in m["ibs"]], edgecolor="white", zorder=3)
    b, a = np.polyfit(m["razon"], m["ibs"], 1)
    xs = np.linspace(m["razon"].min(), m["razon"].max(), 10)
    ax.plot(xs, a + b * xs, ls="--", color=TINTA2, lw=1)
    _etiquetar(ax, m["razon"], m["ibs"], [LOCALIDADES[int(c)] for c in m["localidad"]])
    ax.axhline(0, color=TINTA2, lw=.8)
    ax.set_xlabel("Víctimas estimadas por cada delito registrado (EMV 2024 / SCJ 2024)")
    ax.set_ylabel("Índice de Brecha de Seguridad (z)")
    titulo = f"Índice de Brecha y cifra oculta: Spearman {rho:.2f}"
    if rho_parcial is not None:  # los dos índices comparten el delito registrado: la relación es mecánica
        titulo += f", pero controlando el delito registrado {rho_parcial:.2f}"
    _titulo(ax, titulo.replace(".", ","), fontsize=11.5)
    return _guardar(fig, "fig5_brecha_vs_cifra_oculta")


def genero(por_sexo: dict):
    filas = [("teme_acoso_sexual", "Teme el acoso sexual"), ("no_sale_noche", "Evita salir de noche"),
             ("barrio_inseguro", "Se siente insegura/o en su barrio"), ("victima", "Fue víctima de un delito")]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    for i, (k, et) in enumerate(filas[::-1]):
        m, h = por_sexo[k]["mujeres"], por_sexo[k]["hombres"]
        ax.plot([m, h], [i, i], color=LINEA, lw=5, solid_capstyle="round", zorder=1)
        ax.plot(h, i, "o", color=HOM, ms=9, mec="white", zorder=2)
        ax.plot(m, i, "s", color=MUJ, ms=9, mec="white", zorder=2)
        ax.text(max(m, h) + 2, i, f"{max(m, h):.1f}".replace(".", ","), va="center", fontsize=8.5)
        ax.text(min(m, h) - 2, i, f"{min(m, h):.1f}".replace(".", ","), va="center", ha="right", fontsize=8.5)
    ax.set_yticks(range(len(filas)), [f[1] for f in filas[::-1]])
    ax.set_xlim(0, 100)
    ax.set_xlabel("% de adultos en Bogotá (EMV 2024, ponderado)")
    ax.legend(handles=[plt.Line2D([], [], marker="s", ls="", color=MUJ, label="Mujeres"),
                       plt.Line2D([], [], marker="o", ls="", color=HOM, label="Hombres")], loc="lower right", frameon=False)
    _titulo(ax, "Mujeres frente a hombres en Bogotá (% de adultos, EMV 2024)")
    ax.grid(axis="y", visible=False)
    return _guardar(fig, "fig6_genero")


def ranking_ibs(ibs: pd.DataFrame):
    d = ibs.sort_values("ibs")
    fig, ax = plt.subplots(figsize=(7, 6))
    for i, r in enumerate(d.itertuples()):
        col = PERC if r.ibs > 0 else REG
        ax.plot([r.ibs_p05, r.ibs_p95], [i, i], color=col, lw=2.5, solid_capstyle="round")
        ax.plot(r.ibs, i, "o", color=col, ms=7, mec="white")
    ax.axvline(0, color=TINTA2, lw=1)
    ax.set_yticks(range(len(d)), [LOCALIDADES[int(l)] for l in d["localidad"]])
    ax.set_xlabel("Índice de Brecha de Seguridad (z) e intervalo del 90 %")
    _titulo(ax, "Índice de Brecha de Seguridad por localidad, 2025")
    ax.grid(axis="y", visible=False)
    return _guardar(fig, "fig7_indice_brecha")
