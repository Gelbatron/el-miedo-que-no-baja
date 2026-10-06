# Ficha técnica · Índice de Brecha de Seguridad (IBS)

| Campo | Definición |
|---|---|
| **Nombre** | Índice de Brecha de Seguridad (IBS) |
| **Objetivo** | Identificar los territorios donde la inseguridad percibida supera lo que explica el delito registrado, para priorizar intervenciones de entorno y mejorar el registro. |
| **Fórmula** | IBS = z(% de adultos que califican mala o muy mala la seguridad de su zona) − z(ln de delitos de alto impacto por 100.000 habitantes). La estandarización z se hace entre las localidades (o UPL) del mismo periodo. |
| **Unidad** | Desviaciones estándar. Positivo: más miedo que registro. Negativo: más registro que miedo entre quienes viven ahí. |
| **Fuentes** | Percepción: Encuesta Distrital de Percepción (SDP) o Encuesta Bienal de Cultura Ciudadana (SCRD). Delito: SCJ, delitos de alto impacto (sin lesiones personales). Población: SDP, proyecciones 2005-2035. |
| **Periodicidad** | Semestral por sector de UPL y anual por localidad y UPL (representatividad de la EDP); bienal con la Bienal de Cultura Ciudadana. |
| **Desagregación** | Localidad, UPL, sexo, grupo de edad y estrato (la percepción admite todas; el delito, solo territorio). |
| **Incertidumbre** | Intervalo del 90 % por bootstrap ponderado de la encuesta (1.000 réplicas); se reporta la probabilidad de cada territorio de estar en el top 5. |
| **Línea base 2025** | 48,4 % de los adultos califica mala la seguridad de su zona y 74,0 % califica insegura la ciudad. Top 5: Usme (+2,67), Ciudad Bolívar (+2,34), Bosa (+1,97), Kennedy (+1,72) y San Cristóbal (+1,54). Tabla completa: `outputs/tablas/ibs.csv`. |
| **Indicadores acompañantes** | (1) Víctimas por delito registrado (cifra oculta): EMV o EDP frente a SCJ. (2) % de mujeres que evita salir de noche (EMV o EDP), por sexo. |
| **Meta sugerida** | IBS menor a +1 en las cinco localidades priorizadas y menor cifra oculta en la periferia al cierre del periodo de gobierno. |
| **Limitaciones** | El delito registrado son denuncias y tiene subregistro. En el centro, la tasa por residente se infla por la población flotante. La percepción tiene error muestral (ver intervalos). |
| **Cálculo** | `src/indicadores.py`, función `indice_brecha`. |
