"""
Score de confiabilidad de las fuentes y nivel de evidencia de cada hallazgo.

No todas las fuentes pesan igual: una encuesta de un solo año con 96 personas por localidad no
sostiene lo mismo que un registro administrativo de nueve años. El score hace explícito ese peso con
criterios que cualquiera puede revisar y recalcular.

Score de una fuente (0-100) = 100 × Σ peso × criterio, cada criterio entre 0 y 1:
- Cobertura temporal (20 %): años COMPARABLES de la serie (un quiebre corta la serie). ≥8 → 1 · 5-7 → 0,75 · 3-4 → 0,5 · 2 → 0,35 · 1 → 0,2.
- Actualidad (15 %): años desde el último dato (referencia 2026). 0 → 1 · 1 → 0,85 · 2 → 0,7 · 3-4 → 0,5 · ≥5 → 0,2.
- Precisión (20 %): universo o registro completo → 1 · encuesta con ≥250 casos por localidad → 0,9 · 100-249 → 0,7 ·
  <100 → 0,5 · proyección demográfica → 0,8 · auditoría en campo sin muestreo probabilístico → 0,6 ·
  encuesta sin error publicado por indicador → 0,4 · encuesta no probabilística (autoselección) → 0,3.
- Detalle territorial (15 %): punto o segmento → 1 · UPZ o UPL → 0,85 · localidad → 0,7 · solo ciudad → 0,3.
- Validez (15 %): mide directamente el fenómeno → 1 · con sesgo conocido (subregistro, autoreporte,
  llamadas sin verificar, ventana de recordación variable) → 0,6 · aproximación indirecta → 0,4.
- Verificación externa (15 %): se contrastó con una fuente independiente y coincide → 1 · no hay con qué
  contrastarla → 0,6 · coincide solo en parte (en un tramo de la serie, o en la conclusión pero no en el nivel) → 0,4 ·
  la contradice → 0.
Semáforo: ≥75 alta · 55-74 media · <55 baja.

Nivel de evidencia de un hallazgo: combina la fuente más débil que usa con la prueba estadística.
- Alta: fuentes con score ≥70, prueba significativa tras corregir por pruebas múltiples y robusta a otra especificación.
- Media: una de las dos condiciones falla, o el efecto es significativo sin prueba de robustez.
- Exploratoria: fuente débil o resultado no significativo (se reporta igual: un nulo también es evidencia).
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
REFERENCIA = 2026
PESOS = {"cobertura": 0.20, "actualidad": 0.15, "precision": 0.20, "territorio": 0.15, "validez": 0.15, "verificacion": 0.15}


def _cobertura(anios: int) -> float:
    """Puntaje de cobertura temporal según los años que tiene la serie."""
    return 1.0 if anios >= 8 else 0.75 if anios >= 5 else 0.5 if anios >= 3 else 0.35 if anios == 2 else 0.2


def _actualidad(ultimo: int) -> float:
    """Puntaje de actualidad según los años desde el último dato."""
    d = REFERENCIA - ultimo
    return 1.0 if d <= 0 else 0.85 if d == 1 else 0.7 if d == 2 else 0.5 if d <= 4 else 0.2


PRECISION = {"universo": 1.0, "encuesta_250": 0.9, "encuesta_100": 0.7, "encuesta_<100": 0.5, "proyeccion": 0.8, "auditoria": 0.6,
             "encuesta_sin_error": 0.4, "no_probabilistica": 0.3}
TERRITORIO = {"punto": 1.0, "upz": 0.85, "localidad": 0.7, "ciudad": 0.3}
VALIDEZ = {"directa": 1.0, "sesgo": 0.6, "indirecta": 0.4}
VERIFICACION = {"coincide": 1.0, "no_contrastable": 0.6, "parcial": 0.4, "contradice": 0.0}

# Fichas de las fuentes. `anios` cuenta solo años comparables; `verificacion` resume el contraste con otra fuente
# (src/validacion_registro.py para el registro; docs/notas/frente_victimizacion.md para las encuestas).
FICHAS = [
    # Lo que se registra
    dict(fuente="SCJ · homicidios, lesiones, sexuales y VIF", frente="Lo que se registra", entidad="Secretaría de Seguridad", tipo="Registro administrativo",
         anios=9, ultimo=2026, precision="universo", territorio="localidad", validez="sesgo", verificacion="coincide",
         advertencia="Coincide con la Policía todos los años (razón 1,00-1,09) y los homicidios con Medicina Legal (95-100 %). Cuenta lo denunciado."),
    dict(fuente="SCJ · hurtos", frente="Lo que se registra", entidad="Secretaría de Seguridad", tipo="Registro administrativo",
         anios=4, ultimo=2026, precision="universo", territorio="localidad", validez="sesgo", verificacion="parcial",
         advertencia="Comparable solo desde 2023: antes la capa cuenta 2 a 3 veces lo que registra la Policía. Comercio, celulares y motos no coinciden con su nombre."),
    dict(fuente="Registro de la Policía (SIEDCO)", frente="Lo que se registra", entidad="Policía Nacional", tipo="Registro administrativo",
         anios=9, ultimo=2026, precision="universo", territorio="ciudad", validez="sesgo", verificacion="coincide",
         advertencia="Solo trae municipio. Coincide con Medicina Legal en homicidios y con la capa SCJ desde 2023."),
    dict(fuente="Medicina Legal · homicidios", frente="Lo que se registra", entidad="INMLCF", tipo="Registro forense",
         anios=9, ultimo=2026, precision="universo", territorio="localidad", validez="directa", verificacion="coincide",
         advertencia="Valida homicidios, no hurtos. 2025-2026 preliminar."),
    dict(fuente="SIVIM · violencia contra las mujeres", frente="Lo que se registra", entidad="Secretaría de Salud", tipo="Vigilancia en salud",
         anios=5, ultimo=2026, precision="universo", territorio="upz", validez="sesgo", verificacion="no_contrastable",
         advertencia="Casos notificados al sector salud. Desde 2022 crece la notificación escolar: el aumento mezcla violencia y registro."),
    dict(fuente="Incidentes Línea 123", frente="Lo que se registra", entidad="Secretaría de Seguridad", tipo="Registro administrativo",
         anios=9, ultimo=2026, precision="universo", territorio="upz", validez="sesgo", verificacion="no_contrastable",
         advertencia="Llamadas, no delitos verificados."),
    # Lo que se vive
    dict(fuente="Encuesta Mundial de Valores 2024", frente="Lo que se vive", entidad="Datos para la Transparencia", tipo="Encuesta probabilística",
         anios=1, ultimo=2024, precision="encuesta_<100", territorio="localidad", validez="directa", verificacion="parcial",
         advertencia="96 encuestas por localidad. Mide más victimización (25 %) que el DANE y la CCB (15 %); las tres coinciden en que la mayoría no llega al registro."),
    dict(fuente="Encuesta de Convivencia (ECSC)", frente="Lo que se vive", entidad="DANE", tipo="Encuesta probabilística",
         anios=4, ultimo=2023, precision="encuesta_250", territorio="ciudad", validez="directa", verificacion="coincide",
         advertencia="Sin 2022 ni 2024-2026. Quiebre en 2019 (cambió el mes de campo). Su 2021-2023 cuadra con la Policía, no con la capa SCJ."),
    dict(fuente="Percepción y Victimización (CCB)", frente="Lo que se vive", entidad="Cámara de Comercio de Bogotá", tipo="Encuesta probabilística",
         anios=6, ultimo=2025, precision="encuesta_sin_error", territorio="localidad", validez="sesgo", verificacion="coincide",
         advertencia="Sin error por indicador; pregunta por «este año» con campo en meses distintos. Su 2022-2023 cuadra con la Policía."),
    dict(fuente="Encuesta de acoso callejero 2025", frente="Lo que se vive", entidad="Veeduría Distrital", tipo="Encuesta en línea",
         anios=1, ultimo=2025, precision="no_probabilistica", territorio="localidad", validez="sesgo", verificacion="no_contrastable",
         advertencia="Responde quien quiere (autoselección): sirve para describir, no para estimar."),
    # Lo que se siente
    dict(fuente="Bienal de Cultura Ciudadana 2025", frente="Lo que se siente", entidad="Secretaría de Cultura", tipo="Encuesta probabilística",
         anios=1, ultimo=2025, precision="encuesta_250", territorio="localidad", validez="directa", verificacion="coincide",
         advertencia="Una sola edición comparable. Su 74 % de ciudad insegura cuadra con el 79 % del DANE (2024)."),
    # Las condiciones
    dict(fuente="Seguridad nocturna para las mujeres 2019", frente="Las condiciones", entidad="Secretaría de la Mujer", tipo="Auditoría en campo",
         anios=1, ultimo=2019, precision="auditoria", territorio="punto", validez="indirecta", verificacion="parcial",
         advertencia="Solo vías principales y ciclorrutas. El orden de localidades no se sostiene entre 2016 y 2019."),
    dict(fuente="Inventario de luminarias 2017-2024", frente="Las condiciones", entidad="UAESP", tipo="Inventario",
         anios=8, ultimo=2024, precision="universo", territorio="localidad", validez="indirecta", verificacion="no_contrastable",
         advertencia="Cuenta luminarias, no su estado: sigue a la vía (40 a 57 por km). De 2019 a 2024 el total cambia 0,7 % y lo LED pasa a 70 %."),
    dict(fuente="Estado de la malla vial (PCI)", frente="Las condiciones", entidad="IDU", tipo="Inventario técnico",
         anios=2, ultimo=2026, precision="universo", territorio="punto", validez="directa", verificacion="no_contrastable",
         advertencia="Dos cortes comparables (diciembre 2024 y junio 2026); 22 % de los km-carril en mal estado."),
    dict(fuente="Siniestralidad vial", frente="Las condiciones", entidad="SDM y Medicina Legal", tipo="Registro administrativo",
         anios=11, ultimo=2026, precision="universo", territorio="localidad", validez="directa", verificacion="coincide",
         advertencia="Muertes en vía: Medicina Legal 612 y Movilidad 597 en 2025. Se cuentan donde ocurren, no donde vive la víctima."),
    dict(fuente="Espacio público efectivo", frente="Las condiciones", entidad="DADEP", tipo="Inventario",
         anios=1, ultimo=2022, precision="universo", territorio="localidad", validez="indirecta", verificacion="no_contrastable",
         advertencia="La capa no informa su año de corte: se trata como de hace 3-4 años."),
    dict(fuente="Puntos de internet gratuito", frente="Las condiciones", entidad="Secretaría General", tipo="Inventario",
         anios=1, ultimo=2026, precision="universo", territorio="punto", validez="indirecta", verificacion="no_contrastable",
         advertencia="Inventario de zonas wifi y centros CETIC; no mide uso."),
    # Base de las tasas
    dict(fuente="Proyecciones de población", frente="Base para las tasas", entidad="SDP", tipo="Proyección demográfica",
         anios=9, ultimo=2026, precision="proyeccion", territorio="upz", validez="directa", verificacion="no_contrastable",
         advertencia="Proyección post-censo 2018."),
]


def puntaje(f: dict) -> float:
    """Score de confiabilidad de una fuente (0 a 100): suma ponderada de sus criterios."""
    x = {"cobertura": _cobertura(int(f["anios"])), "actualidad": _actualidad(int(f["ultimo"])), "precision": PRECISION[f["precision"]],
         "territorio": TERRITORIO[f["territorio"]], "validez": VALIDEZ[f["validez"]], "verificacion": VERIFICACION[f["verificacion"]]}
    return round(100 * sum(PESOS[k] * v for k, v in x.items()), 1)


def semaforo(s: float) -> str:
    """Clasifica el score en alta, media o baja."""
    return "alta" if s >= 75 else "media" if s >= 55 else "baja"


def tabla(fichas: list[dict] | None = None) -> pd.DataFrame:
    """Tabla con el score y el semáforo de cada fuente."""
    T = pd.DataFrame(fichas or FICHAS)
    T["score"] = T.apply(lambda f: puntaje(f.to_dict()), axis=1)
    T["semaforo"] = T["score"].map(semaforo)
    return T.sort_values("score", ascending=False)


def nivel_evidencia(score_min: float, significativo_corregido: bool, robusto: bool) -> str:
    """Nivel de evidencia de una estrategia: combina la fuente más débil con la prueba estadística."""
    if score_min >= 70 and significativo_corregido and robusto:
        return "alta"
    if (score_min >= 55 and significativo_corregido) or (score_min >= 70 and robusto):
        return "media"
    return "exploratoria"


if __name__ == "__main__":
    T = tabla()
    T.to_csv(RAIZ / "outputs" / "tablas" / "confiabilidad_fuentes.csv", index=False)
    print(T[["fuente", "frente", "anios", "ultimo", "verificacion", "score", "semaforo"]].to_string(index=False))
