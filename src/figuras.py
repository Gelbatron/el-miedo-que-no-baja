"""
Figuras estáticas (PNG, 200 dpi) para el notebook, el README, la nota técnica y el pitch.
Misma identidad del visor: ámbar = lo que se siente, azul = lo que se registra.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

from territorio import LOCALIDADES  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "outputs" / "figuras"
PERC, REG, MUJ, HOM, NEUTRO, TINTA, TINTA2, LINEA = "#d98a0b", "#2f63d6", "#8e44c8", "#2a9d4b", "#b9c0cd", "#0f1729", "#475069", "#dce1ea"
RAMPA_P = ListedColormap(["#fdf0d5", "#f8d48f", "#efb14a", "#d98a0b", "#a5650a"])
RAMPA_R = ListedColormap(["#dbe6fb", "#a9c2f3", "#6f97e8", "#2f63d6", "#1d43a0"])

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": LINEA, "axes.labelcolor": TINTA2,
    "xtick.color": TINTA2, "ytick.color": TINTA2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e9edf3", "grid.linewidth": .8, "axes.titleweight": "bold", "axes.titlesize": 12,
    "axes.titlelocation": "left", "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def _guardar(fig, nombre):
    FIG.mkdir(parents=True, exist_ok=True)
    ruta = FIG / f"{nombre}.png"
    fig.savefig(ruta, facecolor="white")
    plt.close(fig)
    return ruta


def serie(delitos: pd.DataFrame):
    s = delitos.groupby(["codigo", "anio"])["casos"].sum().unstack()
    fig, ax = plt.subplots(figsize=(8, 4))
    finales = []
    for cod, nombre, col in (("HP", "Hurto a personas", REG), ("VI", "Violencia intrafamiliar", MUJ), ("DS", "Delitos sexuales", PERC)):
        y = s.loc[cod] / s.loc[cod, 2018] * 100
        ax.plot(y.index, y.values, color=col, lw=2.2, marker="o", ms=4)
        finales.append([y.iloc[-1], y.index[-1], f"{nombre} {y.iloc[-1]:.0f}"])
    finales.sort()  # etiquetas sin choque: mínimo 9 puntos de índice entre una y otra
    for i in range(1, len(finales)):
        finales[i][0] = max(finales[i][0], finales[i - 1][0] + 9)
    for yy, xx, txt in finales:
        ax.annotate(txt, (xx, yy), xytext=(8, 0), textcoords="offset points", va="center", color=TINTA, fontsize=9, fontweight="bold")
    ax.axhline(100, color=TINTA2, lw=1)
    ax.set_xlim(2017.7, 2028.2)
    ax.set_ylim(0, 200)
    ax.set_title("Delitos registrados en Bogotá, enero-agosto (índice 2018 = 100)")
    ax.text(0, -0.16, "Fuente: SCJ, Delitos de alto impacto por localidad.", transform=ax.transAxes, fontsize=8, color=TINTA2)
    return _guardar(fig, "fig1_serie_delitos")


def mapas(geo, panel: pd.DataFrame):
    g = geo[geo["localidad"] != 20].merge(panel, on="localidad")
    fig, axs = plt.subplots(1, 2, figsize=(8.5, 7))
    for ax, col, cmap, titulo in ((axs[0], "zona_insegura", RAMPA_P, "Califica mala la seguridad\nde su zona (%, Bienal 2025)"),
                                  (axs[1], "delitos_alto_impacto_100k", RAMPA_R, "Delitos de alto impacto por\n100.000 hab. (SCJ, ene-ago 2025)")):
        g["q"] = pd.qcut(g[col], 5, labels=False)
        g.plot(column="q", cmap=cmap, ax=ax, edgecolor="white", linewidth=.6)
        ax.set_axis_off()
        ax.set_title(titulo, fontsize=10.5)
        cortes = np.quantile(g[col], [0, .2, .4, .6, .8, 1])
        for i in range(5):
            ax.add_patch(plt.Rectangle((0.02, 0.02 + i * 0.045), 0.05, 0.035, transform=ax.transAxes, color=cmap(i)))
            ax.text(0.09, 0.035 + i * 0.045, f"{cortes[i]:,.0f}–{cortes[i + 1]:,.0f}".replace(",", "."), transform=ax.transAxes, fontsize=7.5, va="center")
    fig.suptitle("Percepción y registro no dibujan el mismo mapa", x=0.02, ha="left", fontweight="bold")
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
    ax.set_title(titulo or "Qué explica sentir insegura la zona (logit ponderado, Bienal 2025)")
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
    ax.set_title("Capacidad predictiva fuera de muestra (AUC, validación cruzada)")
    ax.grid(axis="y", visible=False)
    return _guardar(fig, "fig4_auc_bloques")


def brecha_cifra(ibs: pd.DataFrame, co: pd.DataFrame, rho: float):
    m = ibs.merge(co[["localidad", "razon"]], on="localidad")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(m["razon"], m["ibs"], s=60, c=[PERC if v > 0 else REG for v in m["ibs"]], edgecolor="white", zorder=3)
    b, a = np.polyfit(m["razon"], m["ibs"], 1)
    xs = np.linspace(m["razon"].min(), m["razon"].max(), 10)
    ax.plot(xs, a + b * xs, ls="--", color=TINTA2, lw=1)
    for r in m.itertuples():
        ax.annotate(LOCALIDADES[int(r.localidad)], (r.razon, r.ibs), xytext=(5, 4), textcoords="offset points", fontsize=7.5, color=TINTA)
    ax.axhline(0, color=TINTA2, lw=.8)
    ax.set_xlabel("Víctimas estimadas por cada delito registrado (EMV 2024 / SCJ 2024)")
    ax.set_ylabel("Índice de Brecha de Seguridad (z)")
    ax.set_title(f"Donde hay más miedo que delito, más delito queda sin registrar (ρ = {rho:.2f})".replace(".", ","))
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
    ax.set_title("Las mujeres reportan menos delitos y recortan más su vida")
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
    ax.set_title("Índice de Brecha de Seguridad por localidad, 2025")
    ax.grid(axis="y", visible=False)
    return _guardar(fig, "fig7_indice_brecha")
