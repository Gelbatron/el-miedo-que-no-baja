# Guion del pitch · 6 minutos

**El miedo que no baja** · The data squad. Ensayar con cronómetro hasta cerrar en 5:40; el jurado corta a los 6:00.

Reparto sugerido (ajústenlo a quien se sienta más cómodo con cada parte):
- **Brandow** abre con el problema y cierra con las recomendaciones.
- **Rafael** presenta los datos, el método y los dos primeros hallazgos.
- **Samuel** presenta el enfoque de género y el visor.

| Lámina | Tiempo | Quién | Qué decir (idea, no para leer) |
|---|---|---|---|
| 1 · Portada | 0:00-0:20 | Brandow | «Somos The data squad. Nuestra pregunta es por qué la gente en Bogotá no se siente más segura aunque las cifras de delito bajan, y dónde debería actuar primero el Distrito.» |
| 2 · El problema | 0:20-1:00 | Brandow | «Entre enero y agosto, el hurto a personas registrado cayó 65 % desde 2019. Pero el 74 % de los adultos dice que la ciudad es insegura. La política se planea con el registro, y la gente vive otra cosa. Esa distancia es el problema.» Señalar en la gráfica que la violencia intrafamiliar y los delitos sexuales van en sentido contrario. |
| 3 · Datos y método | 1:00-1:50 | Rafael | «Integramos siete fuentes públicas: Seguridad, Planeación, la Bienal de Cultura Ciudadana, la Encuesta Mundial de Valores, UAESP, DADEP e IDECA. Las unimos por el código de localidad y pasamos todo a tasas por 100.000 habitantes. Subimos la escalera completa: descripción, diagnóstico con un logit ponderado, predicción fuera de muestra y escenarios.» |
| 4 · Hallazgo 1 | 1:50-2:40 | Rafael | «Por cada delito registrado hay unas 5,6 víctimas según la Encuesta Mundial de Valores. En Bosa son más de 10; en Los Mártires, menos de 1. Y donde la gente tiene más miedo del que explica el registro, más delito queda sin registrar: correlación de 0,72, la única que sobrevive cuando corregimos por pruebas múltiples. El miedo de la periferia no es exagerado: es delito que no llega a las cifras.» |
| 5 · Hallazgo 2 | 2:40-3:30 | Rafael | «¿Qué hace que alguien sienta insegura su zona? Ver atracos en el parque cercano suma 13 puntos; los conflictos vecinales, hasta 15. El hurto registrado de su localidad no suma nada. Si al modelo le agregamos el delito registrado, la predicción no mejora (0,609 a 0,611); si le agregamos el entorno, sube a 0,78.» |
| 6 · Hallazgo 3 | 3:30-4:15 | Samuel | «Las mujeres reportan menos delitos que los hombres, pero a igual edad, estrato y victimización tienen 18 puntos más de temor al acoso sexual y 6,5 más de evitar salir de noche. El costo del miedo para ellas se paga en autonomía.» |
| 7 · Recomendación | 4:15-5:10 | Brandow | Cuatro recomendaciones, una frase cada una: medir con victimización por UPL; entornos que se sienten seguros en Usme, Ciudad Bolívar, Bosa, Kennedy y San Cristóbal; la autonomía de las mujeres como indicador; y publicar alumbrado georreferenciado y delitos por UPZ. |
| 8 · Indicador y visor | 5:10-5:45 | Samuel | «Proponemos el Índice de Brecha de Seguridad: se calcula cada semestre con fuentes que ya existen. Todo está en el visor (QR) y en el repositorio, reproducible de punta a punta.» Si sobra tiempo, abrir el simulador y mover un control. |
| Cierre | 5:45-5:55 | Brandow | «Bogotá ya produce los datos para cerrar esta brecha; solo hay que leerlos juntos. Gracias.» |

## Preguntas que probablemente hará el jurado

**¿Esto es causal?**
No. Son asociaciones a escala de persona: controlamos sexo, edad, estrato, tenencia y el delito de la localidad, y repetimos el análisis con efectos fijos de localidad. Lo que sí afirmamos con solidez es que el delito registrado no explica la percepción del barrio. La prueba causal sería un piloto con línea base y grupo de comparación en las UPL priorizadas.

**Alumbrado y seguridad los responde la misma persona, ¿no infla eso el resultado?**
Sí, puede inflarlo. Por eso el modelo principal usa solo hechos que vienen de otras preguntas: atracos en el parque, conflictos vecinales y acoso presenciado. El alumbrado lo mostramos aparte. Intentamos validarlo con el inventario de luminarias de la UAESP, pero el último corte publicado es de 2019 y está por localidad. Por eso una de las recomendaciones es publicarlo georreferenciado.

**¿Cómo comparan personas con delitos en la cifra oculta?**
No son la misma unidad, y lo decimos: es un orden de magnitud. Lo importante es la comparación entre localidades: la razón va de 0,7 a 10,6, y esa variación coincide con la brecha entre miedo y registro.

**La Encuesta Mundial de Valores no trae la localidad, ¿de dónde la sacaron?**
Del tablero oficial de Datos para la Transparencia de la Alcaldía, que sí la tiene. La cruzamos registro por registro y verificamos que quedaran 96 encuestas por localidad, como dice la ficha técnica.

**¿Por qué no usaron la Encuesta Distrital de Percepción?**
El sitio de la SDP corta las descargas automatizadas y no pudimos integrarla en el flujo reproducible. Es justamente la fuente que proponemos para el seguimiento: es bimestral y representativa por UPL.

**¿Cómo escala a la ciudad?**
El índice usa fuentes distritales que ya se producen y se actualizan (EDP, SCJ, SDP). Se calcula para las 19 localidades y, con la EDP, para las 33 UPL. El código está abierto y corre con un solo comando.
