# Guion del pitch · 6 minutos

**El miedo que no baja** · The data squad. Se presenta desde el visor (botón ▶ Presentar, modo «Pitch 6 min»). → avanza un paso, N muestra estas notas, D abre «¿Cómo lo sabemos?» para las preguntas. Respaldo sin internet: `Pitch_El_miedo_que_no_baja_The_data_squad.pdf` en una USB. Ensayar con el cronómetro hasta cerrar en 5:30.

| Lámina | Tiempo | Quién | Qué decir (idea, no para leer) |
|---|---|---|---|
| 1 · Portada | 0:00-0:15 | Brandow | Somos The data squad. Venimos a explicar una paradoja de Bogotá: el delito registrado baja, pero el miedo no. ¿Por qué pasa, y dónde debe actuar primero el Distrito? |
| 2 · Bogotá registra menos delitos, pero no se siente más segura | 0:15-0:45 | Brandow | (Aparece la línea azul) El hurto a personas registrado cayó 65 % entre 2019 y 2026. (→) Pero no todo baja: la violencia intrafamiliar y los delitos sexuales suben, y pasan sobre todo en la casa. (→) Y el 74 % de los adultos siente insegura la ciudad. Lo que se cuenta baja; lo que se siente, no. |
| 3 · Si el miedo siguiera al delito, veríamos una diagonal | 0:45-1:15 | Brandow | Pregúntenle al público antes de mostrar: si el miedo siguiera al delito, ¿dónde esperarían más miedo? (→) Donde más se registra: esta diagonal. (→) Pero no: Usme y Ciudad Bolívar registran poco y tienen el miedo más alto; Teusaquillo y Los Mártires registran mucho y tienen menos. La correlación es −0,25: ninguna. El registro no dice dónde está el miedo. |
| 4 · Siete fuentes públicas unidas por una sola llave | 1:15-1:40 | Rafael | ¿Cómo lo sabemos? Unimos siete fuentes públicas: dos encuestas para lo que se siente, la Secretaría de Seguridad para lo que se registra y cuatro de contexto. (→) Cada fuente escribe la localidad distinto: todo se lleva al código oficial. (→) Y siempre comparamos por habitante: en casos gana Suba porque es enorme; por habitante, el centro. |
| 5 · Índice de Brecha: cuánto miedo sobra frente al registro | 1:40-2:25 | Rafael | Para medir la brecha con una sola cifra construimos el Índice de Brecha. Primero el miedo en una regla común: desviaciones frente al promedio de la ciudad. (→) Luego el registro en la misma regla. (→) Y restamos: Usme tiene +1,40 de miedo y −1,27 de registro, brecha de +2,67. (→) Como toda estimación tiene margen de error, la repetimos 1.000 veces: Usme y Ciudad Bolívar quedan en el top 5 en todas, Bosa en el 99,5 %. |
| 6 · Donde sobra miedo, el delito no se está registrando | 2:25-3:05 | Rafael | Primer hallazgo. Hagamos la cuenta en tres pasos (señálenlos): el 24,6 % de los adultos dice haber sido víctima de un delito en el último año, unos 1,5 millones de personas; la Secretaría registró unos 275 mil delitos. Por cada 100 víctimas, el registro tiene 18 delitos. (Cambien el selector a Bosa: 9 de cada 100.) (→) Y donde hay más miedo que registro, más delito se queda sin registrar: correlación de 0,72. (→) ¿Casualidad? Probamos siete relaciones y solo esta sobrevive a la corrección por pruebas múltiples. El miedo de la periferia no es exagerado: es delito que no llega a las cifras. |
| 7 · Dos vecinos iguales: qué cambia el miedo y qué no | 3:05-3:45 | Samuel | ¿Qué hace que alguien sienta insegura su zona? Comparemos personas iguales en todo menos en una cosa. Esta vecina parte de 39 %. (→ muevan el deslizador de hurtos de punta a punta) Del menor al mayor hurto registrado: casi nada. Los homicidios sí pesan algo. (→ activen «atracos en el parque» y suban los conflictos) Ver atracos en el parque: +14 puntos. Conflictos con vecinos: hasta +16. El barrio se siente por lo que pasa en él. |
| 8 · Repetimos el análisis 300 veces, sorteando las localidades | 3:45-4:05 | Samuel | ¿Y si fue suerte? Repetimos el análisis 300 veces sorteando localidades. (Los puntos caen) Los atracos en el parque nunca tocan el cero. (→) El hurto registrado cae a los dos lados del cero: no se distingue de nada. |
| 9 · Las mujeres reportan menos delitos y recortan más su vida | 4:05-4:40 | Samuel | Tercer hallazgo. Las mujeres dicen haber sido víctimas menos que los hombres. (→) Pero temen más el acoso y evitan más salir de noche. (→) Comparando iguales, con la misma edad, estrato y victimización, ser mujer suma 18 puntos de temor al acoso sexual. El costo del miedo se paga en autonomía. |
| 10 · Un indicador para toda la ciudad y cuatro decisiones | 4:40-5:15 | Brandow | Proponemos un indicador para toda la ciudad: el Índice de Brecha, con fuentes que ya existen, cada semestre y por UPL. (→) Y cuatro decisiones: medir con victimización; priorizar entornos con la regla del índice, que hoy señala a Usme, Ciudad Bolívar, Bosa, Kennedy y San Cristóbal; medir la autonomía de las mujeres; y abrir los datos para evaluar. |
| 11 · Cierre | 5:15-5:25 | Brandow | Bogotá ya produce los datos para cerrar esta brecha. Hay que leerlos juntos. Gracias. |

En la clase completa se suman «¿Qué predice mejor el miedo?» (validación cruzada) y el simulador.

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
