"""
Llave territorial única para Bogotá.

Cada entidad escribe la localidad a su manera ("USAQUÉN", "01 - Usaquen", "1",
"Localidad 1 Usaquén", "Rafael Uribe", "SANTAFE"...). Esta función la convierte
en el código oficial 1-20 de la SDP. Sin esta llave no hay integración posible.
"""
import re

from unidecode import unidecode

LOCALIDADES = {
    1: "Usaquén", 2: "Chapinero", 3: "Santa Fe", 4: "San Cristóbal", 5: "Usme",
    6: "Tunjuelito", 7: "Bosa", 8: "Kennedy", 9: "Fontibón", 10: "Engativá",
    11: "Suba", 12: "Barrios Unidos", 13: "Teusaquillo", 14: "Los Mártires",
    15: "Antonio Nariño", 16: "Puente Aranda", 17: "La Candelaria",
    18: "Rafael Uribe Uribe", 19: "Ciudad Bolívar", 20: "Sumapaz",
}
URBANAS = list(range(1, 20))  # Sumapaz es rural: se excluye de los análisis urbanos

_ALIAS = {
    "santafe": 3, "santa fe": 3, "san cristobal": 4, "martires": 14, "los martires": 14,
    "candelaria": 17, "la candelaria": 17, "rafael uribe": 18, "rafael uribe uribe": 18,
    "ciudad bolivar": 19, "antonio narino": 15, "barrios unidos": 12, "puente aranda": 16,
    "engativa": 10, "fontibon": 9, "usaquen": 1, "tunjuelito": 6, "teusaquillo": 13,
    "chapinero": 2, "kennedy": 8, "suba": 11, "bosa": 7, "usme": 5, "sumapaz": 20,
}
_NO_LOCALIDAD = {"bogota", "distrito", "total", "total bogota", "bogota d c", "sin informacion",
                 "sin dato", "fuera de bogota", "nd", "no aplica", "sin localidad"}


def normalizar(x) -> str:
    s = unidecode(str(x)).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def cod_localidad(valor) -> int | None:
    """Código oficial 1-20, o None si el valor no es una localidad reconocible."""
    if valor is None:
        return None
    s = normalizar(valor)
    if not s or s in _NO_LOCALIDAD:
        return None
    s = re.sub(r"^(localidad|loc)\s+", "", s)
    m = re.match(r"^0*(\d{1,2})(?:\s|$)", s)
    if m and 1 <= int(m.group(1)) <= 20:
        num = int(m.group(1))
        resto = s[m.end():].strip()
        if not resto or _ALIAS.get(resto) == num or resto.startswith(normalizar(LOCALIDADES[num])[:4]):
            return num
    if s in _ALIAS:
        return _ALIAS[s]
    for alias, num in sorted(_ALIAS.items(), key=lambda kv: -len(kv[0])):
        if re.search(rf"\b{alias}\b", s):
            return num
    return None


def nombre(cod) -> str:
    return LOCALIDADES.get(int(cod), "") if cod is not None else ""
