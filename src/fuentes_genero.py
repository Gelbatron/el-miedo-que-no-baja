"""
Frente de género, noche y conectividad por localidad (y por año cuando existe).

Ejecutar desde la raíz del repo:  python src/fuentes_genero.py
La primera vez baja ~150 MB desde las URL oficiales a data/crudos/ (caché + registro_descargas.csv);
después trabaja sin red. Escribe 8 tablas en data/procesados/ (ver SALIDAS al final del docstring).

DECISIONES DE MÉTODO
1. Violencia intrafamiliar y de género (SIVIM, Secretaría Distrital de Salud)
   - Unidad: caso NOTIFICADO al sector salud (subsistema SIVIM). No son personas únicas (una víctima
     puede notificarse más de una vez) ni denuncias: solo se ve lo que llega a un servicio de salud o
     a una institución que notifica. Es un piso, no la incidencia real.
   - Localidad = localidad de RESIDENCIA de la víctima (metadato SDS), no del hecho. Por eso el
     denominador es la población residente de la misma localidad y año (SDP, proyecciones CNPV 2018,
     versión marzo 2025: data/procesados/sdp_poblacion_localidad_grupos.csv).
   - Tasa por 100.000 personas DEL MISMO SEXO que la víctima: casos en mujeres / mujeres residentes.
     Se usan mujeres de todas las edades porque SIVIM incluye niñas: más de la mitad de los casos son
     menores de 18. Para aislar a las adultas hay una tasa 18+ (casos 18+ / mujeres_adultas).
   - Años incompletos: el archivo no trae mes ni fecha. 2026 se marca incompleto (el recurso se
     actualizó el 28-07-2026, el metadato dice periodicidad semestral y 2026 trae ~49 % de los casos
     de 2025: lo más probable es enero-junio, pero no es verificable). No se calcula tasa de 2026 ni
     se compara con años completos. Último año completo = 2025.
   - Cortes de comparación: 2019 (último año antes de la pandemia) y 2022 (primer año sin
     restricciones; además es el año en que SIVIM abrió categorías nuevas de agresor).
   - Sumapaz (20) sale de las tablas por localidad (rural, ~3.600 habitantes) pero entra en el total
     de Bogotá, igual que los casos sin localidad. El total de Bogotá usa la población de las 20.
   - Cambio entre años: razón de tasas (RR) con IC 95 % binomial negativa NB2 (var = μ + αμ²), así
     que var(log conteo) ≈ 1/c + α. α sale de una NB2 de los casos en mujeres, 19 localidades ×
     2013-2025, con efectos fijos de localidad y de año y offset log(mujeres): es la variación entre
     años que no es azar de conteo (~17 % relativa). No se usa quasi-Poisson porque el φ de cada
     localidad crece casi proporcional a su media (se verifica: pendiente log-log ≈ 0,9). Para saber
     si una localidad creció MÁS que el resto se usa la razón de RR (localidad frente a la suma de
     las otras 18 urbanas), con corrección Benjamini-Hochberg sobre las 19.
   - Lugar de ocurrencia: hay una columna por tipo de violencia y "Sin dato" significa que ese tipo
     no ocurrió en el caso (metadato). La de violencia emocional está llena en ~99,7 % de los casos y
     el metadato dice que su suma da el total: se usa como "lugar del caso". "Vía pública" = algún
     tipo de violencia del caso ocurrió en vía pública.
   - Bases pequeñas: en el perfil no se publica cambio % si la base tiene menos de 20 casos.
2. Seguridad nocturna para las mujeres (Secretaría de la Mujer, OMEG)
   - Se usa la medición de 2019: 44.335 puntos auditados de noche con la app Safetipin (fotos de
     abril-mayo de 2019) en vías, arterias y ciclorrutas. Está en el GeoPackage "Versión 09.19" del
     conjunto oficial. Los CSV del mismo conjunto ("Versión 09.16", los que lista el inventario) son
     la medición 2015-2016 y son idénticos a los del conjunto "Año 2016".
   - Cada variable se califica 0-3 (dominio del servicio ArcGIS). Componente de la localidad =
     puntaje total / (3 × puntos) × 100. La fórmula reproduce el índice 2016 publicado con los
     puntos de 2015, lo que valida el método.
   - El CSV publicado de 2016 tiene tres errores (se verifican en controles_nocturna): las columnas
     "Total puntos transporte" y "Total puntos estado de sendero" están intercambiadas; las de
     distribución "alto" y "medio" también; y la fila de Usme no cuadra con sus propios totales
     (salvo iluminación). Por eso los valores 2016 que se dan como referencia se recalculan desde
     los puntos.
   - Error estándar de cada componente: el ingenuo de una media (desviación / raíz de n). Subestima
     la incertidumbre porque los puntos vecinos de un mismo recorrido se parecen.
3. Acoso sexual callejero (Veeduría Distrital, 2025)
   - Formulario en línea autoadministrado (marca temporal del 11-jun al 15-sep-2025), sin factor de
     expansión ni diseño muestral publicado, con ~36 % de posgrados entre quienes responden. Trae
     localidad, pero una muestra de autoselección no permite estimar localidades ni comparar entre
     ellas. Se entrega una tabla de Bogotá por sexo y edad, SIN PONDERAR, con el n de cada celda y sin
     margen de error (no es calculable en una muestra no probabilística). Celdas con n < 30 se omiten.
   - Universo: aceptó tratamiento de datos, mayor de 18 y vive en Bogotá.
4. Conectividad pública gratuita (Secretaría General)
   - 531 puntos del inventario oficial (zonas wifi + centros CETIC). Por 100.000 habitantes con la
     población 2026 (el corte de los datos es oct-2026) y por km²: área total del polígono IDECA y
     área urbana (UPZ, sin las UPR rurales), ambas en EPSG:3116 (MAGNA-SIRGAS Bogotá). La densidad
     por km² total castiga a las localidades con mucho suelo rural (Usme, Ciudad Bolívar, Suba...).
5. Pruebas exploratorias (n = 19 localidades)
   - Spearman, IC 95 % bootstrap BCa (10.000 remuestreos pareados de localidades), p por permutación
     (20.000), Benjamini-Hochberg dentro del bloque de 3 pruebas pedidas. Dos bloques aparte, cada uno
     con su propia corrección: "sensibilidad" (violencia contra mujeres en vía pública, más cercana al
     mecanismo de la calle de noche) y "robustez" (medición nocturna 2016, wifi por cruce espacial y
     solo zonas wifi). Son asociaciones ecológicas: no dicen nada de personas ni de causas, y la
     auditoría es de 2019 mientras la violencia es de 2025.

SALIDAS (data/procesados/)
   genero_violencia_localidad_anio.csv · genero_violencia_perfil.csv · genero_violencia_crecimiento.csv
   seguridad_nocturna_localidad.csv · acoso_callejero_bogota.csv · conectividad_localidad.csv
   confiabilidad_genero.csv · genero_pruebas_spearman.csv
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fuentes import CRUDOS, RAIZ, _arcgis_geojson, _get, _registrar  # noqa: E402
from territorio import LOCALIDADES, URBANAS, cod_localidad  # noqa: E402

PROC = RAIZ / "data" / "procesados"
CKAN_DESCARGA = "https://datosabiertos.bogota.gov.co/dataset"
UMBRAL_PESADO_MB = 50
Z95 = 1.959964
SEMILLA = 20261006

# ====================================================================== fuentes
FUENTES_GENERO = {
    "sds_sivim": {
        "entidad": "Secretaría Distrital de Salud (SDS) · Observatorio de Salud de Bogotá",
        "conjunto": "Violencia intrafamiliar y de género en Bogotá D.C. (SIVIM)",
        "url": f"{CKAN_DESCARGA}/a1e1ef90-10c0-436f-a290-d1f7c1cf2242/resource/bbe9e920-c564-40f2-a307-5ae1ff087168/download/osb_saludmental-vintrafamiliar.csv",
        "tipo": "archivo", "archivo": "sds_sivim_violencia_2013_2026.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/numero-de-casos-de-violencia-intrafamiliar",
    },
    "sds_sivim_metadato": {
        "entidad": "Secretaría Distrital de Salud (SDS)",
        "conjunto": "Metadato Violencia intrafamiliar y de género en Bogotá D.C.",
        "url": f"{CKAN_DESCARGA}/a1e1ef90-10c0-436f-a290-d1f7c1cf2242/resource/c5235ec1-4b0b-4282-bdca-02658e8d1e6a/download/metadato-osb_v-intrafamiliar.xlsx",
        "tipo": "archivo", "archivo": "sds_sivim_metadato.xlsx",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/numero-de-casos-de-violencia-intrafamiliar",
    },
    "sdmujer_nocturna_indice_v0916": {
        "entidad": "Secretaría Distrital de la Mujer (SDMujer) · OMEG",
        "conjunto": "Índice de Condiciones de Seguridad Nocturna por Localidad (%). Versión 09.16",
        "url": f"{CKAN_DESCARGA}/f714e477-8e2a-44a2-87c0-17b491a01bcc/resource/ab81ce58-7f7f-4d47-80db-3a80d69a69ec/download/indice-seguridad-por-localidad.csv",
        "tipo": "archivo", "archivo": "sdmujer_seguridad_nocturna_indice_v0916.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/evaluacion-de-seguridad-nocturna-para-las-mujeres-de-bogota-d-c",
    },
    "sdmujer_nocturna_puntos_v0916": {
        "entidad": "Secretaría Distrital de la Mujer (SDMujer) · OMEG",
        "conjunto": "Puntos de evaluación de Seguridad Nocturna para las Mujeres. Versión 09.16",
        "url": f"{CKAN_DESCARGA}/f714e477-8e2a-44a2-87c0-17b491a01bcc/resource/0328d2ae-75b9-4b0f-94cb-33402769afb7/download/puntos-evaluacion-seguridad-nocturna.csv",
        "tipo": "archivo", "archivo": "sdmujer_seguridad_nocturna_puntos_v0916.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/evaluacion-de-seguridad-nocturna-para-las-mujeres-de-bogota-d-c",
    },
    "sdmujer_nocturna_puntos_v0919": {
        "entidad": "Secretaría Distrital de la Mujer (SDMujer) · OMEG",
        "conjunto": "Evaluación de seguridad nocturna para las mujeres 2019 (GeoPackage, Versión 09.19)",
        "url": f"{CKAN_DESCARGA}/f714e477-8e2a-44a2-87c0-17b491a01bcc/resource/486903b6-42da-4b36-9bfd-6e17bd0b7c6e/download/puntosseguridadnocturna.gpkg",
        "tipo": "archivo", "archivo": "sdmujer_seguridad_nocturna_puntos_v0919.gpkg",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/evaluacion-de-seguridad-nocturna-para-las-mujeres-de-bogota-d-c",
    },
    "veeduria_acoso_2025": {
        "entidad": "Veeduría Distrital",
        "conjunto": "Base de Datos Encuesta Acoso Callejero 2025",
        "url": f"{CKAN_DESCARGA}/307da72b-f2a4-4e5c-bcbe-238a67844b71/resource/36041e75-2f97-436c-beb9-30587c5e2705/download/base_acososexualcallejero_2025.csv",
        "tipo": "archivo", "archivo": "veeduria_acoso_callejero_2025.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/base-de-datos-encuesta-acoso-callejero-2025",
    },
    "veeduria_acoso_mujeres": {
        "entidad": "Veeduría Distrital",
        "conjunto": "Encuesta Acoso Callejero Mujeres (publicada en 2024)",
        "url": f"{CKAN_DESCARGA}/2c9f67ff-37d8-48ca-9eab-33c577160084/resource/ca622e73-3175-4e21-8312-ed2a68f258e2/download/acosocallejero_mujer_eficiencia1.csv",
        "tipo": "archivo", "archivo": "veeduria_acoso_callejero_mujeres_2024.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/encuesta-acoso-callejero-mujeres",
    },
    "veeduria_acoso_hombres": {
        "entidad": "Veeduría Distrital",
        "conjunto": "Encuesta Acoso Callejero Hombres (publicada en 2024)",
        "url": f"{CKAN_DESCARGA}/ab896cc5-a215-455c-9176-4149d2772426/resource/dcfa96e3-196b-4735-be49-c0ce7a23beb5/download/acosocallejero_hombre-eficiencia1.csv",
        "tipo": "archivo", "archivo": "veeduria_acoso_callejero_hombres_2024.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/encuesta-acoso-callejero-hombres",
    },
    "sdmujer_acoso_kennedy": {
        "entidad": "Secretaría Distrital de la Mujer (SDMujer)",
        "conjunto": "Encuesta de percepción Acoso Callejero a mujeres, Línea base Ciudades Seguras Kennedy",
        "url": f"{CKAN_DESCARGA}/6f254a00-ed63-4a86-8f85-87d3fa106bb6/resource/1240872d-453b-4560-8fce-01149ddd661b/download/base-de-datos-se1.csv",
        "tipo": "archivo", "archivo": "sdmujer_acoso_kennedy_2019.csv",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/encuesta-de-percepcion-acoso-callejero-a-mujeres-linea-base-ciudades-seguras-kennedy",
    },
    "sg_conectividad": {
        "entidad": "Secretaría General de la Alcaldía Mayor de Bogotá",
        "conjunto": "Conectividad pública gratuita a internet. Bogotá D.C.",
        "url": "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/serviciospublicos/conectividad/MapServer/0",
        "tipo": "arcgis_geo", "archivo": "sg_conectividad_publica_gratuita.geojson",
        "portal": "https://datosabiertos.bogota.gov.co/dataset/conectividad-publica-gratuita-a-internet",
    },
}


def obtener(clave: str, forzar: bool = False) -> Path:
    """Ruta local de la fuente; la baja de la URL oficial si no está en caché y la registra."""
    f = FUENTES_GENERO[clave]
    ruta = CRUDOS / f["archivo"]
    if ruta.exists() and not forzar:
        return ruta
    CRUDOS.mkdir(parents=True, exist_ok=True)
    if f["tipo"] == "archivo":
        ruta.write_bytes(_get(f["url"]).content)
    elif f["tipo"] == "arcgis_geo":
        ruta.write_text(json.dumps(_arcgis_geojson(f["url"]), ensure_ascii=False), encoding="utf-8")
    _registrar(clave, ruta, f["url"])
    return ruta


def obtener_todas(forzar: bool = False) -> pd.DataFrame:
    filas = []
    for clave in FUENTES_GENERO:
        t0 = time.time()
        ruta = obtener(clave, forzar)
        mb = ruta.stat().st_size / 1e6
        filas.append({"fuente": clave, "archivo": ruta.name, "MB": round(mb, 1),
                      "mas_de_50MB": mb > UMBRAL_PESADO_MB, "segundos": round(time.time() - t0, 1)})
    return pd.DataFrame(filas)


# ====================================================================== utilidades
def _tasa(casos, poblacion):
    return casos / poblacion * 1e5


def _es(x, decimales: int = 0, signo: bool = False) -> str:
    """Número con formato español: 492.837 · 2,6 · +27,1."""
    s = f"{x:+,.{decimales}f}" if signo else f"{x:,.{decimales}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(parte, total):
    return np.where(total > 0, parte / np.where(total > 0, total, 1) * 100, np.nan)


def _nombre(cod) -> str:
    return "Bogotá D.C." if cod == 0 else LOCALIDADES.get(int(cod), "")


def _rango(serie: pd.Series, mayor_es_1: bool) -> pd.Series:
    return serie.rank(ascending=not mayor_es_1, method="min").astype("Int64")


def _codigos(valores: pd.Series) -> pd.Series:
    """cod_localidad sobre los valores únicos (rápido en tablas grandes)."""
    mapa = {v: cod_localidad(v) for v in valores.dropna().unique()}
    return valores.map(mapa).astype("Int64")


def _escribir(df: pd.DataFrame, archivo: str) -> pd.DataFrame:
    df.to_csv(PROC / archivo, index=False)
    return df


# ====================================================================== población (denominadores)
def poblacion_grupos() -> pd.DataFrame:
    """SDP por localidad × año × grupo (total, mujeres, hombres, adultos, mujeres_adultas...)."""
    return pd.read_csv(PROC / "sdp_poblacion_localidad_grupos.csv")


EDADES_SIVIM = [("Menor 1 año", 0, 0), ("De 1 - 5 años", 1, 5), ("De 6 - 13 años", 6, 13),
                ("De 14 - 17 años", 14, 17), ("De 18 - 26 años", 18, 26), ("De 27 - 44 años", 27, 44),
                ("De 45 - 59 años", 45, 59), ("De 60 - 69 años", 60, 69), ("De 70 - 79 años", 70, 79),
                ("De 80 años o más", 80, 200)]
ADULTOS = [e for e, a, _ in EDADES_SIVIM if a >= 18]


def poblacion_edad_sexo() -> pd.DataFrame:
    """Bogotá (20 localidades) por año × sexo × grupo de edad SIVIM, desde la edad simple de la SDP."""
    from limpieza import _poblacion  # lee el .ods de data/crudos con la misma rutina del pipeline

    largo = _poblacion("sdp_poblacion_localidad_2005_2035.ods", ["Código Localidad"], "SDP población")
    cortes = [a for _, a, _ in EDADES_SIVIM] + [201]
    largo["grupo_edad"] = pd.cut(largo["edad"], bins=cortes, right=False, labels=[e for e, _, _ in EDADES_SIVIM])
    return (largo.groupby(["anio", "sexo", "grupo_edad"], observed=True, as_index=False)["personas"].sum())


# ====================================================================== SIVIM
CORTE_SIVIM = date(2026, 7, 28)  # last_modified del recurso en el portal (consultado el 6-oct-2026)
ANIO_CIERRE = 2025
ANIOS_CORTE = (2019, 2022, ANIO_CIERRE)
TIPOS = {"emocional": "Emocional", "fisica": "Física", "sexual": "Sexual", "economica": "Económica",
         "negligencia": "Negligencia", "abandono": "Abandono"}
RECODIFICAR_EDAD = {"14 - 17 años": "De 14 - 17 años", "De 30 - 34 años": "De 27 - 44 años",
                    "De 80 - 99 años": "De 80 años o más", "De 100 - 105 años": "De 80 años o más"}
GRUPOS_RELACION = {
    "Pareja": "Pareja o expareja", "Expareja": "Pareja o expareja",
    "Madre": "Madre, padre o padrastros", "Padre": "Madre, padre o padrastros",
    "Padrastro": "Madre, padre o padrastros", "Madrastra": "Madre, padre o padrastros",
    "Hijo(a)": "Otro familiar", "Hermano(a)": "Otro familiar", "Abuelo(a)": "Otro familiar",
    "Otro familiar": "Otro familiar",
    "Estudiantes": "Entorno escolar", "Docentes": "Entorno escolar", "Administrativos": "Entorno escolar",
    "Conocido": "Conocido, amigo, vecino o del trabajo", "Amigo(a)": "Conocido, amigo, vecino o del trabajo",
    "Vecino": "Conocido, amigo, vecino o del trabajo", "Jefe": "Conocido, amigo, vecino o del trabajo",
    "Compañero(a) de trabajo": "Conocido, amigo, vecino o del trabajo",
    "Desconocido": "Desconocido", "Servidor Público": "Otro", "Sacerdote": "Otro",
    "Mujer gestante": "Mujer gestante (código de gestación)", "Sin dato": "Sin dato",
}


def anio_completo(anio: int) -> bool:
    return anio < CORTE_SIVIM.year


def leer_sivim() -> pd.DataFrame:
    s = pd.read_csv(obtener("sds_sivim"), sep=";", encoding="utf-8-sig", dtype=str)
    s.columns = s.columns.str.lower()
    s["anio"] = s["ano"].astype(int)
    s["localidad"] = _codigos(s["nombre_localidad"])
    s["grupo_edad"] = s["grupoedad"].replace(RECODIFICAR_EDAD)
    s["adulta"] = s["grupo_edad"].isin(ADULTOS)
    for t in TIPOS:
        s[f"tipo_{t}"] = s[f"lugocurrencia{t}"].ne("Sin dato")
    s["via_publica"] = s[[f"lugocurrencia{t}" for t in TIPOS]].eq("Vía Pública").any(axis=1)
    s["relacion_grupo"] = s["relacion_agresor"].map(GRUPOS_RELACION).fillna("Otro")
    return s


def _con_total_sexo(s: pd.DataFrame) -> pd.DataFrame:
    """Duplica los casos con sexo_victima = 'Total' para agregarlos en una sola pasada."""
    return pd.concat([s.assign(sexo_victima=s["sexo"]), s.assign(sexo_victima="Total")], ignore_index=True)


def _poblacion_sexo(pob: pd.DataFrame) -> pd.DataFrame:
    mapa = {"mujeres": "Mujeres", "hombres": "Hombres", "total": "Total"}
    p = pob[pob["grupo"].isin(mapa)].assign(sexo_victima=lambda d: d["grupo"].map(mapa))
    bog = p.groupby(["anio", "sexo_victima"], as_index=False)["personas"].sum().assign(localidad=0)
    return pd.concat([p[p["localidad"].isin(URBANAS)], bog], ignore_index=True)[
        ["localidad", "anio", "sexo_victima", "personas"]]


def tabla_violencia_localidad_anio(s: pd.DataFrame, pob: pd.DataFrame) -> pd.DataFrame:
    x = _con_total_sexo(s)
    loc = x[x["localidad"].isin(URBANAS)].groupby(["localidad", "anio", "sexo_victima"]).size()
    bog = x.groupby(["anio", "sexo_victima"]).size()
    bog.index = pd.MultiIndex.from_tuples([(0, a, sx) for a, sx in bog.index], names=loc.index.names)
    malla = pd.MultiIndex.from_product([URBANAS + [0], sorted(s["anio"].unique()), ["Mujeres", "Hombres", "Total"]],
                                       names=loc.index.names)
    t = pd.concat([loc, bog]).reindex(malla, fill_value=0).rename("casos").reset_index()
    t = t.merge(_poblacion_sexo(pob), on=["localidad", "anio", "sexo_victima"], how="left")
    t = t.rename(columns={"personas": "poblacion"})
    t["anio_completo"] = t["anio"].map(anio_completo)
    t["tasa_100k"] = np.where(t["anio_completo"], _tasa(t["casos"], t["poblacion"]), np.nan).round(1)
    t["periodo"] = np.where(t["anio_completo"], "ene-dic",
                            "parcial: probable ene-jun (el archivo no trae mes); no comparar con años completos")
    t["nombre"] = t["localidad"].map(_nombre)
    cols = ["localidad", "nombre", "anio", "sexo_victima", "casos", "poblacion", "tasa_100k", "anio_completo", "periodo"]
    return t[cols].sort_values(["localidad", "anio", "sexo_victima"]).reset_index(drop=True)


def _panel_mujeres(s: pd.DataFrame, pob: pd.DataFrame) -> pd.DataFrame:
    d = (s[(s["sexo"] == "Mujeres") & s["localidad"].isin(URBANAS) & s["anio"].map(anio_completo)]
         .groupby(["localidad", "anio"]).size().rename("casos").reset_index())
    p = pob[pob["grupo"] == "mujeres"][["localidad", "anio", "personas"]]
    return d.astype({"localidad": int}).merge(p, on=["localidad", "anio"])


def sobredispersion(s: pd.DataFrame, pob: pd.DataFrame) -> dict:
    """
    Ruido entre años que no es azar de conteo, en un panel de mujeres 19 localidades × 2013-2025 con efectos
    fijos de localidad y de año (offset log mujeres). Se elige NB2 (var = μ + αμ²) y no quasi-Poisson porque el
    φ de cada localidad crece casi proporcional a su media (pendiente log-log ≈ 0,9): la variación RELATIVA
    entre años es parecida en localidades grandes y pequeñas.
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    d = _panel_mujeres(s, pob)
    pois = smf.glm("casos ~ C(localidad) + C(anio)", data=d, family=sm.families.Poisson(),
                   offset=np.log(d["personas"])).fit()
    d["mu"], d["r2"] = pois.mu, pois.resid_pearson ** 2
    por_loc = d.groupby("localidad").agg(mu=("mu", "mean"), phi=("r2", "mean"))
    pendiente = np.polyfit(np.log(por_loc["mu"]), np.log(por_loc["phi"]), 1)[0]
    nb = smf.negativebinomial("casos ~ C(localidad) + C(anio)", data=d, offset=np.log(d["personas"])).fit(
        disp=0, maxiter=500)
    return {"alpha": float(nb.params["alpha"]), "phi_poisson": float(pois.pearson_chi2 / pois.df_resid),
            "pendiente_loglog": float(pendiente)}


def _var_log(conteos, alpha) -> float:
    """Varianza de log(suma de conteos NB2 independientes): 1/Σc + α·Σc²/(Σc)²."""
    c = np.atleast_1d(np.asarray(conteos, float))
    return 1 / c.sum() + alpha * (c ** 2).sum() / c.sum() ** 2


def _razon_tasas(c1, p1, c0, p0, alpha):
    """RR = tasa año final / tasa año base; c1 y c0 pueden ser vectores (suma de localidades)."""
    rr = (np.sum(c1) / p1) / (np.sum(c0) / p0)
    ee = np.sqrt(_var_log(c1, alpha) + _var_log(c0, alpha))
    return rr, rr * np.exp(-Z95 * ee), rr * np.exp(Z95 * ee)


def _razon_frente_resto(a1, a0, b1, b0, pa1, pa0, pb1, pb0, alpha):
    """Razón de RR: cuánto más (o menos) creció la tasa de la localidad que la del resto (b = vector de 18)."""
    from scipy.stats import norm

    rrr = ((a1 / pa1) / (a0 / pa0)) / ((np.sum(b1) / pb1) / (np.sum(b0) / pb0))
    ee = np.sqrt(_var_log(a1, alpha) + _var_log(a0, alpha) + _var_log(b1, alpha) + _var_log(b0, alpha))
    p = 2 * norm.sf(np.abs(np.log(rrr)) / ee)
    return rrr, rrr * np.exp(-Z95 * ee), rrr * np.exp(Z95 * ee), p


def tabla_violencia_crecimiento(s: pd.DataFrame, pob: pd.DataFrame, alpha: float) -> pd.DataFrame:
    from statsmodels.stats.multitest import multipletests

    m = s[(s["sexo"] == "Mujeres") & s["anio"].isin(ANIOS_CORTE)]
    urb = m[m["localidad"].isin(URBANAS)]
    casos = urb.groupby(["localidad", "anio"]).size().unstack().reindex(URBANAS, fill_value=0)
    adultas = urb[urb["adulta"]].groupby(["localidad", "anio"]).size().unstack().reindex(URBANAS, fill_value=0)
    via = urb[urb["via_publica"]].groupby(["localidad", "anio"]).size().unstack().reindex(URBANAS, fill_value=0)
    pm = pob[pob["grupo"] == "mujeres"].pivot(index="localidad", columns="anio", values="personas").loc[URBANAS]
    pa = pob[pob["grupo"] == "mujeres_adultas"].pivot(index="localidad", columns="anio", values="personas").loc[URBANAS]
    # Bogotá: todas las víctimas mujeres (incluidas Sumapaz y sin localidad) sobre las mujeres de las 20 localidades;
    # para la varianza cada localidad (y el grupo sin localidad) cuenta como una unidad NB2
    cb = m.groupby(["localidad", "anio"], dropna=False).size().unstack(fill_value=0)
    pb = pob[pob["grupo"] == "mujeres"].groupby("anio")["personas"].sum()

    filas = []
    for loc in URBANAS + [0]:
        c = cb if loc == 0 else casos.loc[[loc]]
        p = pb if loc == 0 else pm.loc[loc]
        f = {"localidad": loc, "nombre": _nombre(loc)}
        for a in ANIOS_CORTE:
            f[f"casos_mujeres_{a}"] = int(c[a].sum())
            f[f"mujeres_{a}"] = int(p[a])
            f[f"tasa_mujeres_{a}"] = round(_tasa(c[a].sum(), p[a]), 1)
        for a0 in (2022, 2019):
            rr, lo, hi = _razon_tasas(c[ANIO_CIERRE], p[ANIO_CIERRE], c[a0], p[a0], alpha)
            f[f"cambio_abs_{a0}_{ANIO_CIERRE}"] = round(f[f"tasa_mujeres_{ANIO_CIERRE}"] - f[f"tasa_mujeres_{a0}"], 1)
            f[f"cambio_pct_{a0}_{ANIO_CIERRE}"] = round((rr - 1) * 100, 1)
            f[f"cambio_pct_{a0}_{ANIO_CIERRE}_ic_inf"] = round((lo - 1) * 100, 1)
            f[f"cambio_pct_{a0}_{ANIO_CIERRE}_ic_sup"] = round((hi - 1) * 100, 1)
            if loc:
                b1, b0 = casos.drop(loc)[ANIO_CIERRE], casos.drop(loc)[a0]
                q1, q0 = pm.drop(loc)[ANIO_CIERRE].sum(), pm.drop(loc)[a0].sum()
                rrr, rlo, rhi, pv = _razon_frente_resto(c[ANIO_CIERRE].sum(), c[a0].sum(), b1, b0,
                                                        p[ANIO_CIERRE], p[a0], q1, q0, alpha)
                f[f"razon_frente_resto_{a0}_{ANIO_CIERRE}"] = round(rrr, 3)
                f[f"razon_frente_resto_{a0}_{ANIO_CIERRE}_ic_inf"] = round(rlo, 3)
                f[f"razon_frente_resto_{a0}_{ANIO_CIERRE}_ic_sup"] = round(rhi, 3)
                f[f"p_frente_resto_{a0}_{ANIO_CIERRE}"] = pv
        c18 = m[m["adulta"]].groupby("anio").size() if loc == 0 else adultas.loc[loc]
        p18 = pob[pob["grupo"] == "mujeres_adultas"].groupby("anio")["personas"].sum() if loc == 0 else pa.loc[loc]
        cvp = m[m["via_publica"]].groupby("anio").size() if loc == 0 else via.loc[loc]
        for a in (2019, ANIO_CIERRE):
            f[f"casos_mujeres_18mas_{a}"] = int(c18[a])
            f[f"tasa_mujeres_18mas_{a}"] = round(_tasa(c18[a], p18[a]), 1)
        f[f"cambio_pct_18mas_2019_{ANIO_CIERRE}"] = round(
            (f[f"tasa_mujeres_18mas_{ANIO_CIERRE}"] / f["tasa_mujeres_18mas_2019"] - 1) * 100, 1)
        f[f"casos_mujeres_via_publica_{ANIO_CIERRE}"] = int(cvp[ANIO_CIERRE])
        f[f"tasa_mujeres_via_publica_{ANIO_CIERRE}"] = round(_tasa(cvp[ANIO_CIERRE], p[ANIO_CIERRE]), 1)
        filas.append(f)
    t = pd.DataFrame(filas)
    u = t["localidad"] > 0
    for a0 in (2022, 2019):
        col = f"p_frente_resto_{a0}_{ANIO_CIERRE}"
        t.loc[u, f"q_bh_frente_resto_{a0}_{ANIO_CIERRE}"] = multipletests(t.loc[u, col], method="fdr_bh")[1]
        t.loc[u, f"rango_cambio_{a0}_{ANIO_CIERRE}"] = _rango(t.loc[u, f"cambio_pct_{a0}_{ANIO_CIERRE}"], True)
    t.loc[u, f"rango_tasa_{ANIO_CIERRE}"] = _rango(t.loc[u, f"tasa_mujeres_{ANIO_CIERRE}"], True)
    t["base_minima"] = t[[f"casos_mujeres_{a}" for a in ANIOS_CORTE]].min(axis=1)
    t["base_pequena"] = t["base_minima"] < 100
    t["alpha_nb2"] = round(alpha, 4)
    for c in [c for c in t.columns if c.startswith(("p_", "q_bh"))]:
        t[c] = t[c].round(4)
    for c in [c for c in t.columns if c.startswith("rango_")]:
        t[c] = t[c].astype("Int64")
    return t


def _bloque_perfil(s, columna, dimension, pob_edad=None, excluir=("Sin dato",)):
    x = _con_total_sexo(s[s["anio"].isin(ANIOS_CORTE)])
    validos = x[~x[columna].isin(excluir)]
    conteo = validos.groupby(["sexo_victima", columna, "anio"]).size().unstack("anio").reindex(columns=ANIOS_CORTE)
    totales = validos.groupby(["sexo_victima", "anio"]).size().unstack("anio").reindex(columns=ANIOS_CORTE)
    t = conteo.fillna(0).astype(int)
    t.columns = [f"casos_{a}" for a in ANIOS_CORTE]
    t = t.reset_index().rename(columns={columna: "categoria"})
    for a in ANIOS_CORTE:
        t[f"pct_{a}"] = (t[f"casos_{a}"] / t["sexo_victima"].map(totales[a]) * 100).round(1)
    if pob_edad is not None:
        pe = pd.concat([pob_edad, pob_edad.assign(sexo="Total")]).groupby(
            ["sexo", "grupo_edad", "anio"], observed=True)["personas"].sum()
        for a in ANIOS_CORTE:
            pobl = [pe.get((sx, cat, a), np.nan) for sx, cat in zip(t["sexo_victima"], t["categoria"])]
            t[f"poblacion_{a}"] = pobl
            t[f"tasa_{a}"] = _tasa(t[f"casos_{a}"], t[f"poblacion_{a}"]).round(1)
    t.insert(0, "dimension", dimension)
    return t


def _cambios_perfil(t: pd.DataFrame, base_minima: int = 20) -> pd.DataFrame:
    for a0 in (2019, 2022):
        ok = t[f"casos_{a0}"] >= base_minima
        t[f"cambio_casos_pct_{a0}_{ANIO_CIERRE}"] = np.where(
            ok, (t[f"casos_{ANIO_CIERRE}"] / t[f"casos_{a0}"].where(ok) - 1) * 100, np.nan).round(1)
        t[f"cambio_pp_{a0}_{ANIO_CIERRE}"] = (t[f"pct_{ANIO_CIERRE}"] - t[f"pct_{a0}"]).round(1)
        if f"tasa_{a0}" in t:
            t[f"cambio_tasa_pct_{a0}_{ANIO_CIERRE}"] = np.where(
                ok, (t[f"tasa_{ANIO_CIERRE}"] / t[f"tasa_{a0}"].where(ok) - 1) * 100, np.nan).round(1)
    t["base_pequena"] = (t[[f"casos_{a}" for a in ANIOS_CORTE]] < base_minima).any(axis=1)
    return t


def tabla_violencia_perfil(s: pd.DataFrame, pob_edad: pd.DataFrame) -> pd.DataFrame:
    bloques = [
        _bloque_perfil(s, "grupo_edad", "grupo_edad", pob_edad),
        _bloque_perfil(s, "relacion_grupo", "relacion_agresor_agrupada"),
        _bloque_perfil(s, "relacion_agresor", "relacion_agresor"),
        _bloque_perfil(s, "lugocurrenciaemocional", "lugar_del_caso"),
        _bloque_perfil(s, "lugocurrenciafisica", "lugar_violencia_fisica"),
        _bloque_perfil(s, "lugocurrenciasexual", "lugar_violencia_sexual"),
    ]
    # tipo de violencia: % de casos con ese tipo (no suman 100: un caso puede tener varios)
    largo = s[s["anio"].isin(ANIOS_CORTE)].melt(id_vars=["anio", "sexo"], value_vars=[f"tipo_{t}" for t in TIPOS],
                                                var_name="tipo", value_name="tiene")
    largo["tipo"] = largo["tipo"].str.replace("tipo_", "").map(TIPOS).where(largo["tiene"], "Sin dato")
    largo = largo.rename(columns={"tipo": "tipo_violencia"})
    tipo = _bloque_perfil(largo, "tipo_violencia", "tipo_violencia")
    tot = _con_total_sexo(s[s["anio"].isin(ANIOS_CORTE)]).groupby(["sexo_victima", "anio"]).size().unstack()
    for a in ANIOS_CORTE:
        tipo[f"pct_{a}"] = (tipo[f"casos_{a}"] / tipo["sexo_victima"].map(tot[a]) * 100).round(1)
    t = pd.concat(bloques + [tipo], ignore_index=True)
    orden = {"Mujeres": 0, "Hombres": 1, "Total": 2}
    t = t.sort_values(["dimension", "sexo_victima", f"casos_{ANIO_CIERRE}"], key=lambda c: c.map(orden) if c.name == "sexo_victima" else c,
                      ascending=[True, True, False])
    return _cambios_perfil(t.reset_index(drop=True))


def controles_sivim(s, t_loc, perfil) -> list[str]:
    out = []
    bog = t_loc[(t_loc["localidad"] == 0) & (t_loc["sexo_victima"] == "Total")]["casos"].sum()
    assert bog == len(s), "el total de Bogotá no suma los registros"
    out.append(f"SIVIM: {_es(len(s))} registros = suma de Bogotá (Total) en todos los años")
    urb = t_loc[(t_loc["localidad"] > 0) & (t_loc["sexo_victima"] == "Total")]["casos"].sum()
    resto = int((s["localidad"] == 20).sum()), int(s["localidad"].isna().sum())
    assert urb + sum(resto) == len(s)
    out.append(f"SIVIM: 19 urbanas {_es(urb)} + Sumapaz {_es(resto[0])} + sin localidad {_es(resto[1])} = {_es(len(s))}")
    sx = t_loc.pivot_table(index=["localidad", "anio"], columns="sexo_victima", values="casos")
    assert (sx["Mujeres"] + sx["Hombres"] == sx["Total"]).all()
    out.append("SIVIM: Mujeres + Hombres = Total en cada localidad-año")
    ed = perfil[(perfil["dimension"] == "grupo_edad") & (perfil["sexo_victima"] == "Total")][f"casos_{ANIO_CIERRE}"].sum()
    assert ed == (s["anio"] == ANIO_CIERRE).sum()
    out.append(f"SIVIM: grupos de edad {ANIO_CIERRE} suman {_es(ed)} = casos del año")
    por_anio = s.groupby("anio").size()
    ultimo = por_anio.index.max()
    out.append(f"SIVIM: {ultimo} trae {_es(por_anio[ultimo])} casos = {_es(por_anio[ultimo] / por_anio[ultimo - 1] * 100, 1)} % "
               f"de {ultimo - 1} (consistente con un semestre)")
    e = perfil[(perfil["dimension"] == "grupo_edad") & (perfil["sexo_victima"] == "Mujeres")].set_index("categoria")
    aumento = e[f"casos_{ANIO_CIERRE}"] - e["casos_2019"]
    ninas = aumento[["De 6 - 13 años", "De 14 - 17 años"]].sum() / aumento.sum() * 100
    out.append(f"SIVIM: aumento de casos de mujeres 2019-{ANIO_CIERRE} = {_es(aumento.sum())}; niñas de 6 a 17 años aportan "
               f"{_es(ninas, 1)} % ({_es(aumento['De 6 - 13 años'])} de 6-13 y {_es(aumento['De 14 - 17 años'])} de 14-17)")
    tot = s[s["anio"].isin([2019, ANIO_CIERRE])].groupby("anio").size()
    out.append(f"SIVIM: casos totales (ambos sexos) 2019 {_es(tot[2019])} -> {ANIO_CIERRE} {_es(tot[ANIO_CIERRE])} "
               f"({_es((tot[ANIO_CIERRE] / tot[2019] - 1) * 100, 1, True)} %)")
    return out


def control_convergencia(crec: pd.DataFrame) -> str:
    """Descriptivo: ¿crecieron más las localidades que partían de tasas bajas? (incluye regresión a la media)."""
    from scipy.stats import spearmanr

    u = crec[crec["localidad"] > 0]
    r = spearmanr(u["tasa_mujeres_2019"], u[f"cambio_pct_2019_{ANIO_CIERRE}"])
    r18 = spearmanr(u["tasa_mujeres_18mas_2019"], u[f"cambio_pct_18mas_2019_{ANIO_CIERRE}"])
    return (f"SIVIM (descriptivo): Spearman entre la tasa de mujeres 2019 y su cambio 2019-{ANIO_CIERRE} = "
            f"{_es(r.statistic, 2)} (18+: {_es(r18.statistic, 2)}); las localidades de tasa baja crecieron más")


# ====================================================================== seguridad nocturna
COMPONENTES = {"ILUMINACIO": "iluminacion", "QUE_VEO": "que_veo", "VISIBILIDA": "quien_me_ve",
               "P_SUFICIEN": "presencia_de_personas", "SEGURIDAD": "presencia_de_seguridad",
               "SENDERO": "estado_de_sendero", "T_PUBLICO": "transporte", "P_MIXTA": "presencia_mixta"}
NIVELES_INDICE = {0: "muy_bajo", 1: "bajo", 2: "medio", 3: "alto", 4: "muy_alto"}


def puntos_nocturna():
    import geopandas as gpd

    g = gpd.read_file(obtener("sdmujer_nocturna_puntos_v0919"))
    g["localidad"] = _codigos(g["LOCCODIGO"])
    g["medicion"] = g["Fecha"].dt.year.map({2019: "2019", 2015: "2016_vias", 2016: "2016_ciclorrutas"})
    g["fecha_foto"] = pd.to_datetime(g["URL_Fotogr"].str.extract(r"/(\d{8})/")[0], format="%Y%m%d", errors="coerce")
    return g


def _componentes(p: pd.DataFrame) -> pd.DataFrame:
    """Componentes del índice (0-100) por localidad, con la fórmula de la Secretaría de la Mujer."""
    def resumir(d):
        n = len(d)
        f = {"n_puntos": n, "n_puntos_vias": int((d["CLASIF"] == 1).sum()),
             "n_puntos_ciclorrutas": int((d["CLASIF"] == 0).sum())}
        for c, nombre in COMPONENTES.items():
            f[nombre] = d[c].sum() / (3 * n) * 100
        f["ee_iluminacion"] = d["ILUMINACIO"].std(ddof=1) / 3 * 100 / np.sqrt(n)
        f["ee_estado_de_sendero"] = d["SENDERO"].std(ddof=1) / 3 * 100 / np.sqrt(n)
        f["pct_iluminacion_poca_o_ninguna"] = (d["ILUMINACIO"] <= 1).mean() * 100
        f["pct_sendero_pobre_o_ninguno"] = (d["SENDERO"] <= 1).mean() * 100
        for k, v in NIVELES_INDICE.items():
            f[f"pct_indice_{v}"] = (d["INDICE_SEG"] == k).mean() * 100
        f["pct_indice_bajo_o_muy_bajo"] = (d["INDICE_SEG"] <= 1).mean() * 100
        constantes = [nombre for c, nombre in COMPONENTES.items() if d[c].value_counts(normalize=True).iloc[0] >= 0.999]
        f["alerta"] = ("valor único en ≥ 99,9 % de los puntos (posible valor por defecto): " + ", ".join(constantes)
                       if constantes else "")
        return pd.Series(f)

    urb = p[p["localidad"].isin(URBANAS)]
    t = urb.groupby("localidad").apply(resumir, include_groups=False)
    t.loc[0] = resumir(urb)
    numericas = [c for c in t.columns if c != "alerta"]
    t[numericas] = t[numericas].apply(pd.to_numeric)
    return t


def indice_publicado_2016() -> pd.DataFrame:
    x = pd.read_csv(obtener("sdmujer_nocturna_indice_v0916"), sep=";", encoding="latin-1", decimal=",")
    x["localidad"] = x["Código Localidad"].astype(int)
    return x[x["localidad"].isin(URBANAS)].set_index("localidad")


def controles_nocturna(p, pub) -> list[str]:
    out = []
    p19 = p[p["medicion"] == "2019"]
    out.append(f"Nocturna: {_es(len(p))} puntos en el GeoPackage = 2019 {_es(len(p19))} + 2016 vías "
               f"{_es((p['medicion'] == '2016_vias').sum())} + 2016 ciclorrutas {_es((p['medicion'] == '2016_ciclorrutas').sum())}")
    fotos = p19["fecha_foto"].dt.to_period("M").value_counts(normalize=True)
    out.append(f"Nocturna 2019: fotos de abril-mayo 2019 = {_es(fotos.get(pd.Period('2019-04'), 0) * 100 + fotos.get(pd.Period('2019-05'), 0) * 100, 2)} %")
    out.append(f"Nocturna 2019: puntos sin localidad urbana = {int((~p19['localidad'].isin(URBANAS)).sum())}")
    v16 = _componentes(p[p["medicion"] == "2016_vias"]).drop(index=0)
    sin_usme = pub.drop(index=5)
    tot = {c: sin_usme[f"Total puntos {c}"] / (3 * sin_usme["Total de puntos"]) * 100
           for c in ("transporte", "estado de sendero")}
    cruzado = ((tot["transporte"] - sin_usme["% estado de sendero"]).abs().max() < 1
               and (tot["estado de sendero"] - sin_usme["% transporte"]).abs().max() < 1)
    out.append(f"Índice 2016 publicado: 'Total puntos transporte' da el % de sendero y viceversa en las 18 "
               f"localidades sin Usme = {cruzado}; los % sí están bien rotulados (% sendero publicado vs "
               f"recalculado desde los puntos de 2015: dif. máx. "
               f"{_es((sin_usme['% estado de sendero'] - v16['estado_de_sendero']).abs().max(), 1)} pts)")
    alto_es_medio = (pub["Indice de Seguridad alto"] - v16["pct_indice_medio"]).abs().drop(index=5).median()
    out.append(f"Índice 2016 publicado: columna 'alto' vs % medio recalculado, dif. mediana {_es(alto_es_medio, 1)} pts "
               f"(columnas alto/medio intercambiadas)")
    usme = ", ".join(f"{c} {int(pub.loc[5, f'% {c}'])} vs {_es(v16.loc[5, k], 0)}" for c, k in
                     [("¿Qué veo?", "que_veo"), ("¿Quién me ve?", "quien_me_ve"), ("estado de sendero", "estado_de_sendero")])
    out.append(f"Índice 2016 publicado: Usme no cuadra (publicado vs recalculado desde puntos): {usme}")
    from scipy.stats import spearmanr

    v19 = _componentes(p19).drop(index=0)
    brillante = {m: (p.loc[p["medicion"] == m, "ILUMINACIO"] == 3).mean() * 100 for m in ("2016_vias", "2019")}
    out.append(f"Nocturna: puntos con iluminación 'brillante' 2016 {_es(brillante['2016_vias'], 1)} % vs 2019 "
               f"{_es(brillante['2019'], 1)} % (efecto techo en 2019; mediciones no comparables)")
    for c in ("iluminacion", "estado_de_sendero"):
        r = spearmanr(v16[c], v19[c])
        out.append(f"Nocturna: estabilidad del orden de localidades 2016 vs 2019 en {c}: Spearman {_es(r.statistic, 2)} "
                   f"(p = {_es(r.pvalue, 2)})")
    alertas = v19.loc[v19["alerta"] != "", "alerta"]
    out += [f"Nocturna 2019, {_nombre(k)}: {v}" for k, v in alertas.items()]
    p16 = p[p["medicion"] == "2016_vias"]
    casi_constantes = {nombre: p16[c].value_counts(normalize=True).iloc[0] * 100 for c, nombre in COMPONENTES.items()
                       if p16[c].value_counts(normalize=True).iloc[0] >= 0.95}
    out.append("Nocturna 2016 (vías): componentes con un mismo valor en ≥ 95 % de los puntos: "
               + ", ".join(f"{k} ({_es(v, 1)} %)" for k, v in casi_constantes.items()))
    return out


def tabla_seguridad_nocturna(p: pd.DataFrame, pub: pd.DataFrame) -> pd.DataFrame:
    t = _componentes(p[p["medicion"] == "2019"])
    v16 = _componentes(p[p["medicion"] == "2016_vias"])
    t["medicion"] = "2019 (fotos abr-may 2019, Safetipin)"
    t["n_puntos_2016"] = v16["n_puntos"]
    t["iluminacion_2016"] = v16["iluminacion"]
    t["estado_de_sendero_2016"] = v16["estado_de_sendero"]
    t["iluminacion_2016_publicado"] = pub["% Iluminación"]
    t["estado_de_sendero_2016_publicado"] = pub["% estado de sendero"]
    publicado = {"iluminacion": "% Iluminación", "que_veo": "% ¿Qué veo?", "quien_me_ve": "% ¿Quién me ve?",
                 "presencia_de_personas": "% presencia de personas", "presencia_de_seguridad": "% presencia de seguridad",
                 "estado_de_sendero": "% estado de sendero", "transporte": "% transporte",
                 "presencia_mixta": "% presencia mixta"}
    dif = pd.concat([(pub[col] - v16[c]).abs() for c, col in publicado.items()], axis=1).max(axis=1)
    t["dif_max_publicado_2016"] = dif
    t["publicado_2016_cuadra"] = (dif <= 2).reindex(t.index).astype("boolean")
    t.loc[0, "publicado_2016_cuadra"] = pd.NA
    u = t.index > 0
    t.loc[u, "rango_iluminacion_peor"] = _rango(t.loc[u, "iluminacion"], False)
    t.loc[u, "rango_sendero_peor"] = _rango(t.loc[u, "estado_de_sendero"], False)
    t = t.reset_index().rename(columns={"index": "localidad"})
    t["nombre"] = t["localidad"].map(_nombre)
    num = [c for c in t.columns if t[c].dtype.kind == "f" and not c.startswith(("n_", "rango"))]
    t[num] = t[num].round(1)
    for c in ["n_puntos", "n_puntos_vias", "n_puntos_ciclorrutas", "n_puntos_2016", "rango_iluminacion_peor", "rango_sendero_peor"]:
        t[c] = t[c].astype("Int64")
    primeras = ["localidad", "nombre", "medicion", "n_puntos", "n_puntos_vias", "n_puntos_ciclorrutas"]
    return t[primeras + [c for c in t.columns if c not in primeras]]


# ====================================================================== acoso callejero 2025
COL_ACOSO = {"Proteccion_Datos": "consentimiento", "¿Usted es una persona mayor de 18 años?": "mayor_18",
             "Seleccione alguna de las siguientes opciones:": "residencia",
             "Seleccione alguna de las siguientes opciones:.1": "localidad_texto"}
EDAD_ACOSO = {"18 a 29 años": "18-29", "30 a 44 años": "30-44", "45 a 59 años": "45-59",
              "60 a 69 más": "60 o más", "70 o más": "60 o más"}
GENERO_ACOSO = {"Femenino": "Mujeres", "Masculino": "Hombres", "No binario": "Otras identidades",
                "Transmasculino": "Otras identidades", "Transfemenino": "Otras identidades"}
N_MINIMO_CELDA = 30


def leer_acoso_2025() -> pd.DataFrame:
    a = pd.read_csv(obtener("veeduria_acoso_2025"), sep=";", encoding="cp850", dtype=str).rename(columns=COL_ACOSO)
    a["miedo_acoso_sexual"] = a["miedo_acoso_sexual"].replace({"Si": "Sí"})
    a["fecha"] = pd.to_datetime(a["marca_temporal"], errors="coerce")
    a["localidad"] = _codigos(a["localidad_texto"])
    a["en_universo"] = (a["consentimiento"].eq("Sí") & a["mayor_18"].eq("Sí")
                        & a["residencia"].eq("Sí, vivo en Bogotá"))
    a["grupo_genero"] = a["genero"].map(GENERO_ACOSO)
    a["grupo_edad"] = a["rango_edad"].map(EDAD_ACOSO)
    return a


def _indicadores_acoso(d: pd.DataFrame) -> dict:
    def pct(col, si, base=None):
        v = d[col] if base is None else d.loc[base, col]
        v = v[v.ne("No Aplica") & v.notna()]
        return (v.isin(si).mean() * 100 if len(v) else np.nan), len(v)

    respondio = d["momento_dia_acoso"].ne("No Aplica")
    f = {"n": len(d)}
    f["pct_acoso_12_meses"], f["n_acoso_12_meses"] = pct("acoso_ultimos_12_meses", ["Sí"])
    f["pct_acoso_12_meses_o_no_seguro"], _ = pct("acoso_ultimos_12_meses", ["Sí", "No estoy seguro/a"])
    f["pct_miedo_acoso"], _ = pct("miedo_acoso_sexual", ["Sí"])
    f["pct_miedo_acoso_si_o_a_veces"], _ = pct("miedo_acoso_sexual", ["Sí", "A veces"])
    f["pct_calles_inseguras"], _ = pct("percepcion_seguridad_calles_ep", ["Inseguro/a", "Muy inseguro/a"])
    f["pct_calles_oscuras_muy_inseguras"], _ = pct("calles_oscuras", ["1. Muy inseguro"])
    f["pct_mucho_miedo_calles_oscuras"], _ = pct("miedo_calles_oscuras", ["5. Mucho"])
    f["pct_siempre_busca_lugares_alumbrados"], _ = pct("medida_lugares_alumbrados", ["Siempre"])
    f["n_vivio_acoso"] = int(respondio.sum())
    momento = d.loc[respondio, "momento_dia_acoso"]
    f["pct_acoso_de_noche"] = momento.str.contains("Noche").mean() * 100 if len(momento) else np.nan
    f["pct_acoso_madrugada"] = momento.str.contains("Madrugada").mean() * 100 if len(momento) else np.nan
    f["pct_denuncio"], _ = pct("denuncio_acoso_sexual", ["Sí"], respondio)
    return f


def tabla_acoso_bogota(a: pd.DataFrame) -> pd.DataFrame:
    u = a[a["en_universo"]]
    celdas = [("Total", "Todas las personas", "Todas", u)]
    for g in ["Mujeres", "Hombres", "Otras identidades"]:
        celdas.append(("Género", g, "Todas", u[u["grupo_genero"] == g]))
    for e in ["18-29", "30-44", "45-59", "60 o más"]:
        celdas.append(("Edad", "Todas las personas", e, u[u["grupo_edad"] == e]))
    for g in ["Mujeres", "Hombres"]:
        for e in ["18-29", "30-44", "45-59", "60 o más"]:
            celdas.append(("Género × edad", g, e, u[(u["grupo_genero"] == g) & (u["grupo_edad"] == e)]))
    filas = []
    condicionados = ["pct_acoso_de_noche", "pct_acoso_madrugada", "pct_denuncio"]  # base: quienes vivieron acoso
    for nivel, g, e, d in celdas:
        f = {"nivel": nivel, "genero": g, "edad": e, **_indicadores_acoso(d)}
        if f["n"] < N_MINIMO_CELDA:
            f = {k: (v if not k.startswith("pct_") else np.nan) for k, v in f.items()}
        if f["n_vivio_acoso"] < N_MINIMO_CELDA:
            f.update({k: np.nan for k in condicionados})
        filas.append(f)
    t = pd.DataFrame(filas)
    t["ponderado"] = "no (la base no tiene factor de expansión)"
    t["fuente"] = "Veeduría Distrital, Encuesta de Acoso Sexual Callejero 2025 (formulario en línea, 11-jun a 15-sep-2025)"
    pcts = [c for c in t.columns if c.startswith("pct_")]
    t[pcts] = t[pcts].round(1)
    return t


def controles_acoso(a) -> list[str]:
    u = a[a["en_universo"]]
    n_loc = u.groupby("localidad").size().reindex(URBANAS, fill_value=0)
    educ = (u["nivel_educativo"] == "Posgrado").mean() * 100
    return [f"Acoso 2025: {_es(len(a))} respuestas; universo (consiente, 18+, vive en Bogotá) = {_es(len(u))}; "
            f"fechas {a['fecha'].min():%d-%m-%Y} a {a['fecha'].max():%d-%m-%Y}",
            f"Acoso 2025: n por localidad entre {n_loc.min()} ({_nombre(n_loc.idxmin())}) y {n_loc.max()} "
            f"({_nombre(n_loc.idxmax())}); {_es(educ, 0)} % con posgrado -> muestra de autoselección",
            "Acoso 2025: n por localidad " + ", ".join(f"{_nombre(k)} {v}" for k, v in n_loc.items())]


# ====================================================================== conectividad
def area_localidades() -> pd.DataFrame:
    """Área total (IDECA) y urbana (suma de UPZ, sin UPR) por localidad, en km², EPSG:3116."""
    import geopandas as gpd

    loc = gpd.read_file(CRUDOS / "ideca_localidades.geojson").to_crs(3116)
    loc["localidad"] = loc["LocCodigo"].astype(int)
    upz = gpd.read_file(CRUDOS / "scj_incidentes_123_upz.geojson").to_crs(3116)
    upz = upz[upz["CMIUUPLA"].astype(str).str.startswith("UPZ")][["geometry"]]
    urbana = gpd.overlay(loc[["localidad", "geometry"]], upz, how="intersection")
    t = pd.DataFrame({"area_total_km2": loc.set_index("localidad").area / 1e6,
                      "area_urbana_km2": urbana.dissolve("localidad").area / 1e6})
    return t


def tabla_conectividad(pob: pd.DataFrame, anio_pob: int = 2026) -> tuple[pd.DataFrame, list[str]]:
    import geopandas as gpd

    g = gpd.read_file(obtener("sg_conectividad"))
    g["localidad"] = g["LOCALIDAD"].astype(int)
    loc = gpd.read_file(CRUDOS / "ideca_localidades.geojson")[["LocCodigo", "geometry"]].to_crs(g.crs)
    j = gpd.sjoin(g, loc, how="left", predicate="within")
    j["localidad_espacial"] = pd.to_numeric(j["LocCodigo"])
    acuerdo = (j["localidad"] == j["localidad_espacial"]).mean() * 100
    cuenta = g.groupby("localidad").agg(puntos_conectividad=("OBJECTID", "size"),
                                        zonas_wifi=("CONTIPOEQUIPAMIENTO", lambda x: int((x == 1).sum())),
                                        centros_cetic=("CONTIPOEQUIPAMIENTO", lambda x: int((x == 2).sum())))
    t = cuenta.reindex(URBANAS, fill_value=0)
    t["puntos_cruce_espacial"] = j.groupby("localidad_espacial").size().reindex(URBANAS, fill_value=0)
    p = pob[(pob["grupo"] == "total") & (pob["anio"] == anio_pob)].set_index("localidad")["personas"]
    t[f"poblacion_{anio_pob}"] = p.reindex(URBANAS)
    t = t.join(area_localidades())
    t.loc[0] = t.sum()
    t[f"puntos_por_100k_hab"] = _tasa(t["puntos_conectividad"], t[f"poblacion_{anio_pob}"]).round(2)
    t["zonas_wifi_por_100k_hab"] = _tasa(t["zonas_wifi"], t[f"poblacion_{anio_pob}"]).round(2)
    t["puntos_por_km2_total"] = (t["puntos_conectividad"] / t["area_total_km2"]).round(3)
    t["puntos_por_km2_urbano"] = (t["puntos_conectividad"] / t["area_urbana_km2"]).round(3)
    t[["area_total_km2", "area_urbana_km2"]] = t[["area_total_km2", "area_urbana_km2"]].round(2)
    u = t.index > 0
    t.loc[u, "rango_por_100k_menor"] = _rango(t.loc[u, "puntos_por_100k_hab"], False)
    t = t.reset_index().rename(columns={"index": "localidad"})
    t["nombre"] = t["localidad"].map(_nombre).replace({"Bogotá D.C.": "Bogotá D.C. (19 localidades urbanas)"})
    t["corte_datos"] = "2026-10-01 (última actualización del recurso en el portal)"
    t["puntos_espacial_por_100k_hab"] = _tasa(t["puntos_cruce_espacial"], t[f"poblacion_{anio_pob}"]).round(2)
    for c in ["puntos_conectividad", "zonas_wifi", "centros_cetic", "puntos_cruce_espacial", f"poblacion_{anio_pob}",
              "rango_por_100k_menor"]:
        t[c] = t[c].astype("Int64")
    sumapaz = int((g["localidad"] == 20).sum())
    control = [f"Conectividad: {len(g)} puntos = 19 urbanas {int(t.loc[t['localidad'] > 0, 'puntos_conectividad'].sum())} "
               f"+ Sumapaz {sumapaz}; campo LOCALIDAD coincide con el cruce espacial (IDECA) en {_es(acuerdo, 1)} %",
               f"Conectividad: área urbana (UPZ) {_es(t.loc[t['localidad'] > 0, 'area_urbana_km2'].sum(), 0)} km² de "
               f"{_es(t.loc[t['localidad'] > 0, 'area_total_km2'].sum(), 0)} km² totales en las 19 urbanas"]
    primeras = ["localidad", "nombre"]
    return t[primeras + [c for c in t.columns if c not in primeras]], control


# ====================================================================== pruebas exploratorias
def spearman_bootstrap(x, y, n_boot=10_000, n_perm=20_000, semilla=SEMILLA) -> dict:
    from scipy.stats import bootstrap, rankdata, spearmanr

    x, y = np.asarray(x, float), np.asarray(y, float)
    rho = spearmanr(x, y).statistic
    ic = bootstrap((x, y), lambda a, b: spearmanr(a, b).statistic, paired=True, vectorized=False,
                   n_resamples=n_boot, method="BCa", random_state=np.random.default_rng(semilla)).confidence_interval
    rx, ry = rankdata(x), rankdata(y)
    rng = np.random.default_rng(semilla + 1)
    perm = rng.permuted(np.tile(ry, (n_perm, 1)), axis=1)
    rxc, pc = rx - rx.mean(), perm - perm.mean(axis=1, keepdims=True)
    rho_perm = (pc @ rxc) / (np.sqrt((pc ** 2).sum(axis=1)) * np.sqrt((rxc ** 2).sum()))
    p = (1 + (np.abs(rho_perm) >= abs(rho) - 1e-12).sum()) / (n_perm + 1)
    return {"n": len(x), "rho": rho, "ic95_inf": ic.low, "ic95_sup": ic.high, "p_permutacion": p}


def pruebas_exploratorias(crec, noct, conec) -> pd.DataFrame:
    from statsmodels.stats.multitest import multipletests

    d = (crec[crec["localidad"] > 0].set_index("localidad")
         .join(noct.set_index("localidad")[["iluminacion", "estado_de_sendero", "iluminacion_2016", "estado_de_sendero_2016"]])
         .join(conec.set_index("localidad")[["puntos_por_100k_hab", "puntos_espacial_por_100k_hab", "zonas_wifi_por_100k_hab"]]))
    y_mujeres = (f"tasa_mujeres_{ANIO_CIERRE}", f"Tasa de violencia contra mujeres {ANIO_CIERRE} (SIVIM, por 100.000 mujeres)")
    y_via = (f"tasa_mujeres_via_publica_{ANIO_CIERRE}", f"Tasa de casos en vía pública contra mujeres {ANIO_CIERRE} (por 100.000 mujeres)")
    xs = {"iluminacion": "Iluminación (índice SDMujer 2019, 0-100)",
          "estado_de_sendero": "Estado de sendero (índice SDMujer 2019, 0-100)",
          "puntos_por_100k_hab": "Puntos de conectividad pública gratuita por 100.000 hab. (2026)"}
    robustez = {"iluminacion_2016": "Iluminación (medición 2016, recalculada desde puntos)",
                "estado_de_sendero_2016": "Estado de sendero (medición 2016, recalculada desde puntos)",
                "puntos_espacial_por_100k_hab": "Puntos de conectividad por 100.000 hab. (localidad por cruce espacial)",
                "zonas_wifi_por_100k_hab": "Solo zonas wifi por 100.000 hab. (sin CETIC)"}
    bloques = [("principal", y_mujeres, xs), ("sensibilidad", y_via, xs), ("robustez", y_mujeres, robustez)]
    filas = []
    for bloque, (ycol, ydesc), equis in bloques:
        for xcol, xdesc in equis.items():
            filas.append({"bloque": bloque, "y": ydesc, "x": xdesc, **spearman_bootstrap(d[xcol], d[ycol])})
    t = pd.DataFrame(filas)
    for b in t["bloque"].unique():
        m = t["bloque"] == b
        t.loc[m, "p_ajustado_bh"] = multipletests(t.loc[m, "p_permutacion"], method="fdr_bh")[1]
    t["sobrevive_bh_5pct"] = t["p_ajustado_bh"] < 0.05
    t[["rho", "ic95_inf", "ic95_sup"]] = t[["rho", "ic95_inf", "ic95_sup"]].round(3)
    t[["p_permutacion", "p_ajustado_bh"]] = t[["p_permutacion", "p_ajustado_bh"]].round(4)
    return t


# ====================================================================== ficha de confiabilidad
def tabla_confiabilidad(s, p_noct, acoso, noct) -> pd.DataFrame:
    import geopandas as gpd

    rd = lambda clave: pd.read_csv(obtener(clave), sep=";", encoding="cp1252", dtype=str)  # noqa: E731
    muj, hom, ken = rd("veeduria_acoso_mujeres"), rd("veeduria_acoso_hombres"), rd("sdmujer_acoso_kennedy")
    wifi = gpd.read_file(obtener("sg_conectividad"))
    p19 = p_noct[p_noct["medicion"] == "2019"]
    sin_upz = (s.loc[s["anio"] == ANIO_CIERRE, "nombreupz"] == "Sin dato").mean() * 100
    ee_max = noct.loc[noct["localidad"] > 0, ["ee_iluminacion", "ee_estado_de_sendero"]].max().max()
    u = acoso[acoso["en_universo"]]
    filas = [
        ("SIVIM: violencia intrafamiliar y de género", "Secretaría Distrital de Salud", "2013-2026 (2026 parcial)",
         "Semestral según el metadato (el portal dice anual)", "Registro administrativo (vigilancia en salud)",
         f"{_es(len(s))} casos notificados", "UPZ de residencia de la víctima "
         f"({_es(sin_upz, 1)} % sin UPZ en {ANIO_CIERRE}); en este frente se usa localidad", "No aplica (registro)",
         "No aplica; error no muestral por subregistro y cambios de notificación", "2026-07-28",
         FUENTES_GENERO["sds_sivim"]["url"],
         "Cuenta casos notificados al sector salud, no personas ni denuncias. Categorías nuevas en 2018 (lugares) y 2022 "
         "(agresor amigo y compañero de trabajo) y auge de notificación escolar desde 2022: el crecimiento mezcla "
         "violencia y registro."),
        ("Seguridad nocturna para las mujeres 2019", "Secretaría Distrital de la Mujer (OMEG)", "2019 (fotos abr-may 2019)",
         "Según necesidad (dos mediciones: 2015-2016 y 2019)", "Auditoría en campo (app Safetipin, 6 a 11 p. m.)",
         f"{_es(len(p19))} puntos", "Punto georreferenciado en vía o ciclorruta", "No aplica (no es muestra probabilística)",
         f"No publicado; error estándar ingenuo de los componentes por localidad ≤ {_es(ee_max, 1)} pts (subestima: puntos "
         "autocorrelacionados)", "2019-09-10 (dato); ficha del portal modificada 2025-03-15",
         FUENTES_GENERO["sdmujer_nocturna_puntos_v0919"]["url"],
         "Tiene 7 años y solo cubre vías, arterias y ciclorrutas (no calles de barrio). Efecto techo: 86 % de los "
         "puntos con iluminación 'brillante' (12 % en 2016), así que discrimina poco entre localidades; el orden de "
         "localidades no se sostiene entre 2016 y 2019. Tunjuelito tiene sendero 'bueno' en el 100 % de sus puntos "
         "(posible valor por defecto). Es una auditoría del entorno, no la percepción de las mujeres."),
        ("Índice de seguridad nocturna por localidad 2016 (CSV 'Versión 09.16')", "Secretaría Distrital de la Mujer (OMEG)",
         "2015-2016", "Según necesidad", "Auditoría en campo (agregado por localidad)",
         f"{_es(pub_total_2016())} puntos (vías y arterias)", "Localidad", "No aplica", "No publicado",
         "Publicado 2024-05-07 (dato de nov-2015)", FUENTES_GENERO["sdmujer_nocturna_indice_v0916"]["url"],
         "Errores de publicación: totales de transporte y sendero intercambiados, distribución alto/medio "
         "intercambiada, fila de Usme inconsistente. Usar solo recalculado desde los puntos."),
        ("Encuesta de acoso sexual callejero 2025", "Veeduría Distrital", "2025 (11-jun a 15-sep)", "No planeada",
         "Encuesta en línea autoadministrada (no probabilística)", f"{_es(len(acoso))} respuestas; {_es(len(u))} en el universo "
         "analítico (18+, vive en Bogotá)", "Localidad de residencia autodeclarada (n de 40 a 551 por localidad)", "No",
         "No calculable (autoselección)", "2026-06-12", FUENTES_GENERO["veeduria_acoso_2025"]["url"],
         f"Sesgo de autoselección ({_es((u['nivel_educativo'] == 'Posgrado').mean() * 100, 0)} % con posgrado en el "
         "universo analítico). Sirve para describir a quienes respondieron, no para estimar prevalencias de Bogotá "
         "ni comparar localidades."),
        ("Encuesta de acoso callejero, mujeres", "Veeduría Distrital", "Publicada en 2024 (sin fecha de respuesta)",
         "Anual según el portal (una sola base publicada)", "Encuesta (diseño no documentado)", f"{_es(len(muj))} mujeres de 14+ años",
         "Localidad de residencia autodeclarada", "No", "No calculable", "2024-08-29", FUENTES_GENERO["veeduria_acoso_mujeres"]["url"],
         "Sin ficha técnica ni pesos; respuestas abiertas mezcladas en campos cerrados (calidad de captura baja)."),
        ("Encuesta de acoso callejero, hombres", "Veeduría Distrital", "Publicada en 2024 (sin fecha de respuesta)",
         "Anual según el portal (una sola base publicada)", "Encuesta (diseño no documentado)", f"{_es(len(hom))} hombres",
         "Localidad de residencia autodeclarada", "No", "No calculable", "2024-08-28", FUENTES_GENERO["veeduria_acoso_hombres"]["url"],
         "Mide percepción de los hombres sobre el acoso, no victimización. Sin pesos."),
        ("Línea base de acoso callejero, Ciudades Seguras Kennedy", "Secretaría Distrital de la Mujer", "2019",
         "No planeada", "Encuesta presencial con dispositivo (diseño no publicado)", f"{_es(len(ken))} mujeres de 14+ años",
         "UPZ (5 UPZ de Kennedy)", "No", "No calculable", "2019-12-13", FUENTES_GENERO["sdmujer_acoso_kennedy"]["url"],
         "Solo Kennedy: no sirve para comparar localidades."),
        ("Conectividad pública gratuita a internet", "Secretaría General de la Alcaldía Mayor", "Corte 2026",
         "Según necesidad", "Registro administrativo (inventario georreferenciado)",
         f"{_es(len(wifi))} puntos ({int((wifi['CONTIPOEQUIPAMIENTO'] == 1).sum())} zonas wifi y "
         f"{int((wifi['CONTIPOEQUIPAMIENTO'] == 2).sum())} centros CETIC)",
         "Punto georreferenciado", "No aplica", "No aplica", "2026-10-01", FUENTES_GENERO["sg_conectividad"]["url"],
         "Inventario de puntos: no mide calidad, horario, ancho de banda ni uso. El "
         f"{_es((wifi['ENTIDAD'] == 4).mean() * 100, 0)} % son zonas wifi del DADEP en espacio público."),
        ("Proyecciones de población por localidad (denominador)", "Secretaría Distrital de Planeación", "2005-2035",
         "Anual (proyección)", "Proyección demográfica (base CNPV 2018)", "20 localidades × edad simple × sexo",
         "Localidad (también UPZ)", "No aplica", "No publicado", "Versión 2025-03",
         "https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035",
         "Retroproyección para 2013-2017 y proyección después de 2018: los denominadores de años lejanos al censo "
         "tienen más error, sobre todo en localidades con migración reciente."),
    ]
    cols = ["fuente", "entidad", "anios_disponibles", "periodicidad", "tipo", "tamano", "nivel_territorial_mas_fino",
            "factor_expansion", "margen_error", "ultima_actualizacion", "url", "advertencia"]
    return pd.DataFrame(filas, columns=cols)


def pub_total_2016() -> int:
    return int(indice_publicado_2016()["Total de puntos"].sum())


# ====================================================================== triangulación con la SCJ
def triangulacion_scj() -> list[str]:
    """Denuncias de violencia intrafamiliar (SCJ, enero-agosto) frente a casos SIVIM, mismo periodo de años."""
    ruta = PROC / "scj_delitos_localidad_largo.csv"
    if not ruta.exists():
        return ["SCJ: no está scj_delitos_localidad_largo.csv; se omite la triangulación"]
    d = pd.read_csv(ruta)
    vi = d[d["codigo"] == "VI"].groupby("anio")["casos"].sum()
    return [f"SCJ violencia intrafamiliar (ene-ago, toda Bogotá): 2019 {_es(vi[2019])}, 2022 {_es(vi[2022])}, "
            f"{ANIO_CIERRE} {_es(vi[ANIO_CIERRE])} -> cambio 2019-{ANIO_CIERRE} {_es((vi[ANIO_CIERRE] / vi[2019] - 1) * 100, 1, True)} %"]


# ====================================================================== principal
def main():
    t0 = time.time()
    descargas = obtener_todas()
    pesados = descargas[descargas["mas_de_50MB"]]
    PROC.mkdir(parents=True, exist_ok=True)
    pob = poblacion_grupos()

    s = leer_sivim()
    t_loc = _escribir(tabla_violencia_localidad_anio(s, pob), "genero_violencia_localidad_anio.csv")
    perfil = _escribir(tabla_violencia_perfil(s, poblacion_edad_sexo()), "genero_violencia_perfil.csv")
    disp = sobredispersion(s, pob)
    crec = _escribir(tabla_violencia_crecimiento(s, pob, disp["alpha"]), "genero_violencia_crecimiento.csv")

    p_noct, pub16 = puntos_nocturna(), indice_publicado_2016()
    noct = _escribir(tabla_seguridad_nocturna(p_noct, pub16), "seguridad_nocturna_localidad.csv")

    acoso = leer_acoso_2025()
    _escribir(tabla_acoso_bogota(acoso), "acoso_callejero_bogota.csv")

    conec, ctrl_conec = tabla_conectividad(pob)
    _escribir(conec, "conectividad_localidad.csv")

    _escribir(tabla_confiabilidad(s, p_noct, acoso, noct), "confiabilidad_genero.csv")
    pruebas = _escribir(pruebas_exploratorias(crec, noct, conec), "genero_pruebas_spearman.csv")

    print("\n== Descargas")
    print(descargas.to_string(index=False))
    for _, f in pesados.iterrows():
        print(f"AVISO: {f['archivo']} pesa {f['MB']} MB (> {UMBRAL_PESADO_MB} MB); se guardó en data/crudos/")
    print("\n== Controles")
    sobre = (f"SIVIM: sobredispersión del panel mujeres 19 × 2013-{ANIO_CIERRE}: φ Poisson = {_es(disp['phi_poisson'], 1)}; "
             f"pendiente log φ_i ~ log μ_i = {_es(disp['pendiente_loglog'], 2)} (≈1 -> NB2); α NB2 = {_es(disp['alpha'], 4)} "
             f"(variación relativa entre años ≈ {_es(np.sqrt(disp['alpha']) * 100, 0)} %)")
    controles = (controles_sivim(s, t_loc, perfil) + [sobre, control_convergencia(crec)] + triangulacion_scj()
                 + controles_nocturna(p_noct, pub16) + controles_acoso(acoso) + ctrl_conec)
    for c in controles:
        print(" -", c)
    print("\n== Pruebas exploratorias (Spearman, n = 19)")
    print(pruebas[["bloque", "x", "rho", "ic95_inf", "ic95_sup", "p_permutacion", "p_ajustado_bh",
                   "sobrevive_bh_5pct"]].to_string(index=False))
    print(f"\nListo en {_es(time.time() - t0, 0)} s. Tablas en {PROC}")


if __name__ == "__main__":
    main()
