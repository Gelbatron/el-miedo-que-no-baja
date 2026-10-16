"use client";
import { D, R, fmt, signo } from "@/lib/datos";
import { C } from "@/lib/clase";
import { HURTO, PANDEMIA } from "@/lib/historia";
import { Motor, type Diapo } from "./Motor";
import { BOGOTA, CifraOculta, Datos, Indice, Paradoja, Portada, Prueba, Termometros } from "./diapos-a";
import { Cierre, Genero, Prediccion, Propuesta, Repeticiones, SimuladorClase, Vecinos } from "./diapos-b";
import { Frentes, Modelos, Tendencias, Validacion } from "./diapos-c";
import { Estrategias, Hipotesis, Lecturas, Mujeres, Tipologia, Union } from "./diapos-d";
import { F, encuesta, ficha, tendencia } from "@/lib/frentes";

const AME = Object.fromEntries(D.ame.m_hechos.map((f) => [f.variable, f]));
const FE = Object.fromEntries(D.ame_efectos_fijos.map((f) => [f.variable, f]));
const WILD = Object.fromEntries(D.lpm_wild.map((f) => [f.variable, f]));
const pw = (p: number) => (p < 0.001 ? "p < 0,001" : `p = ${fmt(p, 3)}`);
const top5 = (D.ibs as unknown as { nombre: string; prob_top5: number }[]).slice(0, 5);
const usme = C.indice.find((f) => f.localidad === 5)!;
const bosa = (D.cifra_oculta as unknown as { localidad: number; razon: number; razon_inf: number; razon_sup: number }[]).find((f) => f.localidad === 7)!;
const vecina = (() => {
  const r = C.logit.referencia;
  const pr = (x: Record<string, number>) => { let s = C.logit.coef.const; for (const [k, v] of Object.entries(x)) s += (C.logit.coef[k] ?? 0) * v; return 100 / (1 + Math.exp(-s)); };
  const p0 = pr(r);
  return { p0, atracos: pr({ ...r, parque_atracos: 1 }) - p0, conflictos: pr({ ...r, conflictos_vecinos: 1 }) - p0 };
})();
const g = D.emv_genero.teme_acoso_sexual.find((f) => f.variable === "mujer")!;

// Cuatro actos, la historia que cuenta el equipo:
// 0 el problema · 1 lo que hicimos · 2 lo que encontramos · 3 por qué importa
const ANTERIORES: Diapo[] = [
  {
    id: "inicio", corto: "Portada", pasos: 1, roja: true, quien: "Brandow", tiempo: "0:00-0:10",
    nota: "Somos The data squad. Les vamos a contar algo que encontramos en los datos de Bogotá y que no cuadra.",
    render: () => <Portada />,
  },

  /* ---------- Acto 1 · El problema ---------- */
  {
    id: "paradoja", corto: "En el papel mejora", acto: 0, ante: "El problema · 1", titulo: "En el papel, Bogotá mejora. ¿De verdad?", pasos: 4,
    quien: "Brandow", tiempo: "0:10-0:45",
    nota: `La capa abierta de la Secretaría de Seguridad dice que el hurto a personas cayó ${signo(HURTO.capa2019a2026, 0)} % desde 2019. (→) Pero el registro de la Policía, el mismo hurto y los mismos meses, dice ${signo(HURTO.policia2019a2026, 0)} %. Hasta 2022 la capa contaba más del doble; desde 2023 son idénticas. (→) Y los hechos violentos suben: violencia intrafamiliar y delitos sexuales cerca de 45 %. (→) Con eso, que 3 de cada 4 personas digan que Bogotá es insegura ya no es una paradoja.`,
    profundizar: (
      <>
        <h3>El efecto pandemia, con la serie de la Policía</h3>
        <p>En 2020 el hurto a personas registrado cayó {fmt(-PANDEMIA.hurto2020, 0)} % por el encierro. En 2022 volvió al {fmt(PANDEMIA.hurto2022sobre2019, 0)} % de su nivel de 2019; en 2023 subió {fmt(PANDEMIA.hurto2023, 0)} %, y en 2026 está {fmt(Math.abs(PANDEMIA.hurto2022a2026), 0)} % por debajo de 2022.</p>
        <p>La capa abierta de la SCJ dice otra cosa porque de 2018 a 2022 cuenta {fmt(HURTO.razonMin, 2)} a {fmt(HURTO.razonMax, 2)} veces lo que registra la Policía, y desde 2023 coincide caso por caso. La caída de 2023 es el paso de una escala a la otra.</p>
        <p>La violencia intrafamiliar casi no se movió con la pandemia ({signo(PANDEMIA.vif2020, 0)} % en 2020) y desde 2022 subió {fmt(PANDEMIA.vif2022a2026, 0)} %. Esa serie sí coincide con la Policía todos los años.</p>
      </>
    ),
    render: (p) => <Paradoja paso={p} />,
  },
  {
    id: "cifra-oculta", corto: "Mucho delito no se denuncia", acto: 0, ante: "El problema · 2", titulo: "Y mucho delito ni siquiera se denuncia", pasos: 1,
    quien: "Brandow", tiempo: "0:45-1:15",
    nota: `Y nos dimos cuenta de que mucho delito ni siquiera llega a las cifras. Hagan la cuenta con nosotros (señalen los tres pasos): el ${fmt(BOGOTA.emv_victima)} % de los adultos dice haber sido víctima en el último año, unos ${fmt(Math.round(BOGOTA.victimas_estimadas / 1e5) / 10, 1)} millones de personas; la Secretaría registró unos ${fmt(Math.round(BOGOTA.delitos_registrados / 1e3), 0)} mil delitos. De cada 10 víctimas, ${fmt(10 / BOGOTA.razon, 1)} quedan en el registro. Con las encuestas del DANE y de la Cámara de Comercio la cuenta da cerca de 3 de cada 10: cambia el nivel, no la conclusión. (Cambien el selector a Bosa: ${fmt(10 / bosa.razon, 1)}.)`,
    profundizar: (
      <>
        <h3>Cómo se calcula la cifra oculta</h3>
        <p><b>Víctimas:</b> % de adultos que dicen haber sido víctimas en el último año (Encuesta Mundial de Valores 2024) × adultos de la localidad (SDP). <b>Delitos:</b> registro de la Secretaría de Seguridad en 2024, enero a agosto llevado a 12 meses.</p>
        <p>Compara personas con hechos, así que se lee como orden de magnitud. Con 96 encuestas por localidad, cada razón lleva su intervalo: Bosa {fmt(bosa.razon)} víctimas por delito (IC 95 % de {fmt(bosa.razon_inf)} a {fmt(bosa.razon_sup)}).</p>
        <p><b>Dónde pasa y dónde vive:</b> la encuesta pregunta si la persona fue víctima, sin decir dónde; el registro cuenta dónde ocurrió el delito. Al centro (Los Mártires, La Candelaria, Santa Fe, Chapinero) llega gente de toda la ciudad, así que allí la razón sale baja, y en la periferia puede salir alta. En el total de Bogotá ese efecto se compensa: por eso la cifra principal es la de la ciudad.</p>
      </>
    ),
    render: () => <CifraOculta />,
  },
  {
    id: "termometros", corto: "Un mapa incompleto", acto: 0, ante: "El problema · 3", titulo: "El mapa de las denuncias no es el mapa del miedo", pasos: 3,
    quien: "Brandow", tiempo: "1:15-1:40",
    nota: "Pregúntenle al público: si el miedo siguiera al delito registrado, ¿dónde esperarían más miedo? (→) Donde más se registra: esta diagonal. (→) Pero no: Usme y Ciudad Bolívar registran poco y tienen el miedo más alto. El Distrito está tomando decisiones con un mapa al que le falta más de la mitad.",
    profundizar: (
      <>
        <h3>Correlación de rangos (Spearman)</h3>
        <p>Ordenamos las 19 localidades dos veces, por delito registrado y por miedo, y comparamos los puestos. +1 es el mismo orden, 0 es ninguna relación y −1 es el orden invertido.</p>
        <p>Usamos rangos y no valores porque el centro (La Candelaria registra {fmt(11351, 0)} delitos por 100 mil residentes) aplastaría una correlación lineal. Por la misma razón el eje horizontal va en escala logarítmica.</p>
        <p>Resultado: −0,25 con intervalo del 95 % de −0,69 a 0,30, que incluye el cero. Tampoco coinciden las víctimas que reporta la encuesta con los delitos registrados (ρ = 0,03).</p>
      </>
    ),
    render: (p) => <Termometros paso={p} />,
  },

  /* ---------- Acto 2 · Lo que hicimos ---------- */
  {
    id: "datos", corto: "Juntamos todo", acto: 1, ante: "Lo que hicimos · 1", titulo: "Juntamos lo que la gente siente con lo que el Estado registra", pasos: 3,
    quien: "Rafael", tiempo: "1:40-2:00",
    nota: "¿Qué hicimos? Juntamos todo: lo que la gente siente, de dos encuestas; lo que el Estado registra, de la Secretaría de Seguridad; y población, parques y alumbrado. (→) Cada fuente escribe la localidad distinto, así que todo lo llevamos al mismo código. (→) Y comparamos por habitante, para que Suba no gane solo por ser grande.",
    profundizar: (
      <>
        <h3>Bitácora de limpieza</h3>
        <ul>
          <li>Bienal 2025: 5.860 personas; quedan 5.639 adultos y 5.538 en las 19 localidades urbanas. Las escalas se recodifican a «malo o muy malo»; «no sabe» queda vacío.</li>
          <li>Factor de expansión: la muestra representa a {fmt(R.adultos_urbanos_bienal, 0)} adultos urbanos.</li>
          <li>SCJ: 117 columnas año por tipo pasadas a formato largo, con el mismo corte enero-agosto para todos los años.</li>
          <li>Encuesta Mundial de Valores: la base publicada no trae la localidad. La recuperamos del tablero oficial de Datos para la Transparencia, registro por registro, y verificamos 96 encuestas por localidad.</li>
          <li>Población de la SDP como denominador: Bogotá 2025 = {fmt(R.poblacion_2025, 0)} habitantes.</li>
        </ul>
        <p>Todo corre con un comando (<span className="mono">python src/pipeline.py</span>) y una prueba en limpio dio los mismos resultados.</p>
      </>
    ),
    render: (p) => <Datos paso={p} />,
  },
  {
    id: "indice", corto: "El índice", acto: 1, ante: "Lo que hicimos · 2", titulo: "Un índice: dónde hay más miedo del que muestran las cifras", pasos: 4,
    quien: "Rafael", tiempo: "2:00-2:40",
    nota: `Con eso armamos un índice que dice en qué localidades hay más miedo del que muestran las cifras. Pasamos el miedo y el delito a la misma regla, cuánto se alejan del promedio de la ciudad, (→ →) y los restamos: Usme tiene ${signo(usme.z_percepcion, 2)} de miedo y ${signo(usme.z_registro, 2)} de registro, brecha de ${signo(usme.ibs, 2)}. (→) Las que más brecha tienen: Usme, Ciudad Bolívar, Bosa, Kennedy y San Cristóbal. Lo repetimos 1.000 veces y casi siempre son las mismas.`,
    profundizar: (
      <>
        <h3>Cómo se calcula y qué tan estable es</h3>
        <p><b>Fórmula:</b> z(% que califica mala la seguridad de su zona) − z(logaritmo de los delitos de alto impacto por 100.000). z = (valor − promedio) / desviación estándar entre las 19 localidades.</p>
        <p><b>Por qué logaritmo:</b> el centro recibe población flotante; sin él, dos localidades definirían toda la escala.</p>
        <p><b>Incertidumbre:</b> remuestreamos 1.000 veces a los encuestados de la Bienal dentro de cada localidad. Probabilidad de estar en el top 5: {top5.map((f) => `${f.nombre} ${fmt(f.prob_top5 * 100, f.prob_top5 > 0.99 && f.prob_top5 < 1 ? 1 : 0)} %`).join(", ")}.</p>
        <p><b>Escala:</b> con la Encuesta Distrital de Percepción se calcula igual para las 33 UPL, cada semestre.</p>
      </>
    ),
    render: (p) => <Indice paso={p} />,
  },
  {
    id: "prueba", corto: "¿Falta denuncia donde sobra miedo?", acto: 1, ante: "Lo que hicimos · 3", titulo: "¿Donde sobra miedo, falta denuncia? Parecía que sí", pasos: 2,
    quien: "Rafael", tiempo: "2:40-3:05",
    nota: `¿Donde el índice marca más miedo, más delito se queda sin denunciar? La correlación da 0,72 y pasa la corrección por pruebas múltiples. (→) Pero los dos índices usan el delito registrado: uno lo resta y el otro lo divide. Controlando por él, la correlación queda en ${fmt(R.ibs_vs_cifra_oculta_parcial.rho, 2)}. Es mecánica, y lo decimos. Lo que sí se sostiene: las víctimas que reporta la encuesta no siguen al registro.`,
    profundizar: (
      <>
        <h3>Pruebas múltiples</h3>
        <p>Cruzamos ocho pares de indicadores entre localidades (miedo y delito, víctimas y delito, miedo y cifra oculta, alumbrado y luminarias, entre otros). Con ocho pruebas, alguna saldría «significativa» por puro azar.</p>
        <p>La corrección de Benjamini-Hochberg ajusta los valores p por el número de pruebas. Solo el Índice de Brecha frente a la cifra oculta queda bajo 0,05, pero esa relación es mecánica: el índice resta el log del delito registrado y la cifra oculta lo divide. Spearman parcial controlando el delito registrado: {fmt(R.ibs_vs_cifra_oculta_parcial.rho, 2)} (p = {fmt(R.ibs_vs_cifra_oculta_parcial.p, 2)}). La prueba directa, miedo frente a cifra oculta, da ρ = {fmt(R.zona_vs_cifra_oculta.rho, 2)}, no significativa.</p>
        <p><b>Límite:</b> parte de la razón alta de la periferia puede venir de residentes que son víctimas en otras localidades (el registro cuenta dónde pasa el delito). Por eso se lee como señal fuerte, no como medida exacta, y por eso proponemos encuestas de victimización por UPL que pregunten dónde ocurrió.</p>
      </>
    ),
    render: (p) => <Prueba paso={p} />,
  },

  /* ---------- Acto 3 · Lo que encontramos ---------- */
  {
    id: "vecinos", corto: "Lo que da miedo", acto: 2, ante: "Lo que encontramos · 1", titulo: "El miedo sale del barrio, no de las estadísticas", pasos: 3,
    quien: "Samuel", tiempo: "3:05-3:45",
    nota: `¿Qué es lo que de verdad le da miedo a la gente? Comparamos personas iguales en todo menos en una cosa. Esta vecina parte de ${fmt(vecina.p0, 0)} %. (→ muevan el hurto de punta a punta) Las estadísticas de hurto de su localidad: casi nada. (→ activen atracos y suban los conflictos) Ver atracos en el parque: ${signo(vecina.atracos, 0)} puntos. Peleas entre vecinos: hasta ${signo(vecina.conflictos, 0)}. Lo que da miedo es lo que se ve en el barrio.`,
    profundizar: (
      <>
        <h3>El modelo y su robustez</h3>
        <p><b>Modelo:</b> logit ponderado con el factor de expansión sobre {fmt(C.logit.n, 0)} adultos de la Bienal 2025. Controla sexo, edad, estrato, arriendo y el delito registrado de su localidad.</p>
        <p><b>Efectos marginales promedio</b> (cambio en puntos porcentuales, promediado sobre todos los encuestados): atracos en el parque {signo(AME.parque_atracos.ame_pp, 1)} pp; conflictos vecinales {signo(AME.conflictos_vecinos.ame_pp, 1)}; hurto registrado {signo(AME.hurtos_100k_miles.ame_pp, 1)}; homicidios {signo(AME.homicidios_100k.ame_pp, 2)} por cada uno.</p>
        <p><b>Robustez:</b> wild cluster bootstrap con pesos de Webb: hurto {pw(WILD.hurtos_100k_miles.p_wild)}, atracos {pw(WILD.parque_atracos.p_wild)}, homicidios {pw(WILD.homicidios_100k.p_wild)}. Con efectos fijos de localidad, los atracos siguen en {signo(FE.parque_atracos.ame_pp, 1)} pp.</p>
        <p>Usamos <b>hechos</b> (atracos, conflictos) y no la calificación del alumbrado, que comparte batería con la pregunta de seguridad y la inflaría.</p>
      </>
    ),
    render: (p) => <Vecinos paso={p} />,
  },
  {
    id: "repeticiones", corto: "No fue suerte", acto: 2, ante: "Lo que encontramos · 2", titulo: "Y no fue suerte: repetimos el análisis 300 veces", pasos: 2,
    quien: "Samuel", tiempo: "3:45-4:00",
    nota: "Y no fue suerte: repetimos el análisis 300 veces sorteando las localidades. (Los puntos caen) Los atracos nunca bajan de cero. (→) El hurto registrado cae a los dos lados: no explica nada.",
    profundizar: (
      <>
        <h3>Bootstrap por conglomerados</h3>
        <p>Las personas de una misma localidad comparten contexto, así que no son 5.538 observaciones independientes. Con solo 19 conglomerados, los errores analíticos son optimistas.</p>
        <p>Por eso sorteamos localidades completas con reemplazo, reestimamos el modelo y guardamos el efecto. El intervalo del 95 % son los percentiles 2,5 y 97,5 de las 300 réplicas: los mismos que publica el notebook.</p>
      </>
    ),
    render: (p) => <Repeticiones paso={p} />,
  },
  {
    id: "prediccion", corto: "¿Qué predice el miedo?", acto: 2, ante: "Lo que encontramos · extra", titulo: "El entorno predice el miedo; el delito registrado, casi nada", pasos: 4, soloClase: true,
    quien: "Samuel", tiempo: "clase",
    nota: "Le damos al modelo dos personas al azar, una que siente insegura su zona y otra que no. Una moneda acierta 50 de cada 100. Con el perfil, 61. (→) Sumar el delito registrado: 61,1. Nada. (→) Sumar lo que pasa en el barrio: 65,5. (→) Todo junto: 78.",
    profundizar: (
      <>
        <h3>Área bajo la curva (AUC)</h3>
        <p>Es la probabilidad de que el modelo le asigne más riesgo a la persona que sí siente insegura su zona que a la que no. 0,5 es azar; 1 es acierto perfecto.</p>
        <p>Se mide fuera de muestra: validación cruzada con 25 particiones; el modelo nunca ve a las personas con las que se evalúa.</p>
        <p>La calificación del entorno sube mucho el acierto, pero comparte batería con la pregunta de seguridad (sesgo de método común). Por eso el modelo principal usa solo hechos.</p>
      </>
    ),
    render: (p) => <Prediccion paso={p} />,
  },
  {
    id: "genero", corto: "Las mujeres", acto: 2, ante: "Lo que encontramos · 3", titulo: "Ellas denuncian menos, pero temen más y salen menos de noche", pasos: 3,
    quien: "Samuel", tiempo: "4:00-4:35",
    nota: `Con las mujeres es más fuerte. Denuncian menos que los hombres. (→) Pero tienen mucho más miedo al acoso y dejan de salir de noche. (→) Comparando mujeres y hombres de igual edad, estrato y victimización: ${signo(g.ame_pp, 0)} puntos de temor al acoso. El miedo les cuesta libertad.`,
    profundizar: (
      <>
        <h3>Encuesta Mundial de Valores 2024</h3>
        <p>{fmt(R.n_emv_bogota, 0)} encuestas en Bogotá (96 por localidad), ponderadas con su factor. Logit ponderado con sexo, edad, estrato y si fue víctima; intervalos por bootstrap de localidades.</p>
        <p>Contexto del registro: violencia intrafamiliar {signo(R.vif_cambio_pct_2018_2026, 1)} % y delitos sexuales {signo(R.delitos_sexuales_cambio_pct_2018_2026, 1)} % entre 2018 y 2026. Ocurren sobre todo en la casa y el entorno cercano, por eso la recomendación de género va más allá del espacio público.</p>
      </>
    ),
    render: (p) => <Genero paso={p} />,
  },

  /* ---------- Acto 4 · Por qué importa ---------- */
  {
    id: "simulador", corto: "¿Cuánto cambiaría?", acto: 3, ante: "Por qué importa · extra", titulo: "Si mejoramos alumbrado y parques, ¿cuánto baja el miedo?", pasos: 1, soloClase: true,
    quien: "Brandow", tiempo: "clase",
    nota: "Muevan los deslizadores. Con la mitad de las zonas con buen alumbrado y la mitad de los parques sin atracos, la inseguridad percibida baja 7,4 puntos en Bogotá: unos 467 mil adultos. Es una estimación del modelo, no una promesa.",
    profundizar: (
      <>
        <h3>Cómo calcula el simulador</h3>
        <p>Con el modelo (hechos del entorno + alumbrado) se predice la probabilidad de cada encuestado en cuatro mundos: hoy (p00), con el alumbrado resuelto (p10), sin atracos en ningún parque (p01) y con ambas cosas (p11).</p>
        <p>El escenario mezcla esos mundos según la cobertura elegida: (1 − f₁)(1 − f₂)·p00 + f₁(1 − f₂)·p10 + (1 − f₁)f₂·p01 + f₁f₂·p11.</p>
      </>
    ),
    render: () => <SimuladorClase />,
  },
  {
    id: "propuesta", corto: "Por qué importa", acto: 3, ante: "Por qué importa", titulo: "Dónde actuar, qué arreglar y cómo saber si funciona", pasos: 3,
    quien: "Brandow", tiempo: "4:35-5:15",
    nota: "¿Por qué importa? Porque le decimos al Distrito dónde actuar primero: estas cinco localidades. (→) Qué arreglar: lo que la gente ve en su barrio, parques, convivencia y alumbrado, pensando en las mujeres. (→) Y cómo saber si de verdad la gente se siente más segura, no solo si bajan las denuncias: este índice cada semestre. Todo con datos que el Distrito ya tiene.",
    render: (p) => <Propuesta paso={p} />,
  },
  {
    id: "cierre", corto: "Cierre", pasos: 1, roja: true, quien: "Brandow", tiempo: "5:15-5:25",
    nota: "Bogotá ya tiene los datos para cerrar esta brecha. Solo hay que leerlos juntos. Gracias.",
    render: () => <Cierre />,
  },
];

/* ====== La historia: inicio (cómo se mide y qué dice cada fuente), nudo (validar, unir y modelar), desenlace (estrategias) ====== */
const B = (id: string) => ANTERIORES.find((d) => d.id === id)!;
const hp = tendencia("HP"), hom = tendencia("H"), vif = tendencia("VI"), ds = tendencia("DS");
const ctx = F.ml.contexto_localidad;
const fichaScore = (f: string) => fmt(ficha(f)?.score ?? NaN, 0);
const noDen = { dane: 100 - (encuesta("DANE", "tasa_denuncia", "cualquier_delito_con_isd", 2023) ?? 0), ccb: 100 - (encuesta("CCB", "tasa_denuncia", "cualquier_delito", 2025) ?? 0) };
const tip = (F.tipologia?.localidades ?? []) as Record<string, string | number>[];
const perfilDe = (nombre: string) => String(tip.find((l) => l.nombre === nombre)?.perfil_nombre ?? "");

export const DIAPOS: Diapo[] = [
  { ...B("inicio"), tiempo: "0:00-0:10",
    nota: "Somos The data squad. ¿Qué tan segura es Bogotá? Depende de a quién le preguntes. Y una de las respuestas que más circula tiene un problema que encontramos en los datos." },

  /* ---------- Inicio · El problema ---------- */
  {
    id: "frentes", corto: "Cómo se mide", acto: 0, ante: "El problema · 1", titulo: "¿Qué tan segura es Bogotá? Depende de cómo la midas", pasos: 3,
    quien: "Brandow", tiempo: "0:10-0:30",
    nota: "La seguridad se mide desde cuatro frentes: lo que se registra, lo que la gente vive, lo que siente y las condiciones del entorno. (→) Cada fuente lleva un score de confiabilidad de 0 a 100: años comparables, actualidad, precisión, detalle territorial, validez y si cuadra con otra fuente. No todas pesan igual. (→) Y ninguna, sola, cubre los cuatro frentes.",
    profundizar: (
      <>
        <h3>Cómo se calcula el score de confiabilidad</h3>
        <p>Seis criterios de 0 a 1, ponderados: años comparables de la serie (20 %), actualidad (15 %), precisión o tamaño de muestra (20 %), detalle territorial (15 %), validez para medir el fenómeno (15 %) y verificación externa, es decir, si coincide con una fuente independiente (15 %).</p>
        <p>Un quiebre corta la serie: los hurtos de la capa SCJ solo son comparables desde 2023 y no cuadran con la Policía antes, así que bajan a {fichaScore("SCJ · hurtos")}. Homicidios, lesiones, sexuales y violencia intrafamiliar de la misma capa coinciden con la Policía y con Medicina Legal: {fichaScore("SCJ · homicidios, lesiones, sexuales y VIF")}.</p>
        <p>La Encuesta Mundial de Valores mide la victimización de forma directa, pero tiene 96 encuestas por localidad y una sola edición: {fichaScore("Encuesta Mundial de Valores 2024")}. La encuesta de acoso callejero es un formulario en línea (autoselección): {fichaScore("Encuesta de acoso callejero 2025")}.</p>
        <p>Semáforo: 75 o más, alta; 55 a 74, media; menos de 55, baja. Cálculo en <span className="mono">src/confiabilidad.py</span>.</p>
      </>
    ),
    render: (p) => <Frentes paso={p} />,
  },
  {
    id: "lecturas", corto: "Cada fuente por separado", acto: 0, ante: "El problema · 2", titulo: "Cada fuente, por separado, cuenta otra historia", pasos: 6,
    quien: "Brandow", tiempo: "0:30-1:25",
    nota: `Leamos cada fuente sola y qué concluiríamos con ella. (en cada →, lean la conclusión) La capa abierta de la Secretaría: el hurto cayó ${signo(HURTO.capa2022a2026, 0)} % desde 2022, «Bogotá es mucho más segura». Pero la Policía, el mismo hurto y los mismos meses: ${signo(HURTO.policia2022a2026, 0)} %, «el hurto casi no bajó». Los homicidios suben ${fmt(hom.post_cambio_anual_pct, 1)} % al año y la violencia intrafamiliar ${fmt(vif.post_cambio_anual_pct, 0)} %, «la violencia sube». Entre ${fmt(Math.min(noDen.dane, noDen.ccb), 0)} y ${fmt(Math.max(noDen.dane, noDen.ccb), 0)} % de las víctimas no denuncia, «la mayoría no denuncia». Y 3 de cada 4 dicen que la ciudad es insegura. (→) El miedo no contradice los datos.`,
    profundizar: (
      <>
        <h3>De dónde sale cada cifra</h3>
        <ul>
          <li>Hurto a personas, enero-agosto: capa «Delitos de alto impacto» de la SCJ ({fmt(HURTO.capa2022, 0)} → {fmt(HURTO.capa2026, 0)}) y SIEDCO de la Policía en datos.gov.co ({fmt(HURTO.policia2022, 0)} → {fmt(HURTO.policia2026, 0)}).</li>
          <li>Homicidios, violencia intrafamiliar y delitos sexuales: binomial negativa de panel, 19 localidades, 2022-2026, con efectos fijos y población como exposición; series que coinciden con la Policía todos los años.</li>
          <li>Denuncia: Encuesta de Convivencia del DANE (2023, cualquier delito) y Encuesta de Percepción y Victimización de la Cámara de Comercio (2025).</li>
          <li>Percepción y confianza en la Policía: Bienal de Cultura Ciudadana 2025, ponderada; el DANE mide lo mismo en 2024.</li>
        </ul>
      </>
    ),
    render: (p) => <Lecturas paso={p} />,
  },
  { ...B("paradoja"), acto: 0, ante: "El problema · clase", soloClase: true, tiempo: "clase" },
  { ...B("termometros"), acto: 0, ante: "El problema · clase", soloClase: true, tiempo: "clase" },

  /* ---------- Nudo · Lo que hicimos ---------- */
  {
    id: "union", corto: "Unir las fuentes", acto: 1, ante: "Lo que hicimos · 1", titulo: "Unimos las fuentes para responder cuatro preguntas", pasos: 3,
    quien: "Rafael", tiempo: "1:25-1:40",
    nota: "Por eso unimos las fuentes para responder cuatro preguntas: quién es más vulnerable, dónde y en qué crece la inseguridad, si la percepción y las cifras cuadran, y qué hacer primero. (→) Con una sola llave territorial, tasas por habitante, los factores de expansión de cada encuesta y el mismo corte de meses. (→) Y con tres modelos. Pero antes de modelar, validamos.",
    profundizar: B("datos").profundizar,
    render: (p) => <Union paso={p} />,
  },
  { ...B("datos"), acto: 1, ante: "Lo que hicimos · clase", soloClase: true, tiempo: "clase" },
  {
    id: "validacion", corto: "Validar antes de modelar", acto: 1, ante: "Lo que hicimos · 2 · validación cruzada", titulo: "Antes de modelar, validamos: la serie de hurto tenía un quiebre", pasos: 3,
    quien: "Rafael", tiempo: "1:40-2:10",
    nota: `Antes de modelar comparamos cada serie con una fuente independiente. La capa abierta dice ${signo(HURTO.capa2022a2026, 0)} % en hurto desde 2022. (→) La Policía, ${signo(HURTO.policia2022a2026, 0)} %. De 2018 a 2022 la capa contaba ${fmt(HURTO.razonMin, 1)} a ${fmt(HURTO.razonMax, 1)} veces más; desde 2023 coinciden caso por caso. En homicidios, lesiones, delitos sexuales y violencia intrafamiliar coinciden todos los años, y los homicidios cuadran con Medicina Legal. (→) ¿Y si cayó la denuncia? La encuesta del DANE dice que no: la denuncia subió. Para que la caída fuera real, la denuncia habría tenido que desplomarse. Cambió cómo se arma la serie, no la calle.`,
    profundizar: (
      <>
        <h3>Cómo se validó</h3>
        <p>Para cada delito y año (enero-agosto, Bogotá) dividimos los casos de la capa SCJ entre los del SIEDCO publicado por la Policía en datos.gov.co, y los homicidios también entre los de Medicina Legal. Una razón entre 0,95 y 1,10 cuenta como la misma serie.</p>
        <p><b>Resultado:</b> homicidios, lesiones, delitos sexuales y violencia intrafamiliar, validadas en 2018-2025. Hurto a personas, residencias y automotores, con quiebre: comparables solo desde 2023 (para Bogotá usamos el SIEDCO). La razón exacta de 2,00 en automotores sugiere hechos contados dos veces, pero la capa no documenta su método: es una hipótesis.</p>
        <p><b>Hallazgo adicional:</b> desde 2023, la columna «motocicletas» de la capa repite caso por caso el hurto a comercio de la Policía, y la de «celulares» repite el de motos. Esas tres columnas no se usan por tipo.</p>
        <p><b>Contrafactual (DANE, 2021 frente a 2023):</b> la victimización por hurto no cambió (de 7,3 % a 6,9 %, p = 0,50) y la denuncia subió de 36 % a 43 %. Para explicar la caída de la capa, la denuncia tendría que haber bajado a cerca de 25 %. El 5 de septiembre de 2023 la Alcaldía informó que el hurto iba 23 % por encima de 2022: la misma dirección que el SIEDCO.</p>
        <p>Código: <span className="mono">src/fuentes_victimizacion.py</span> y <span className="mono">src/validacion_registro.py</span>. Es una recomendación técnica de documentación, no una evaluación de ninguna entidad.</p>
      </>
    ),
    render: (p) => <Validacion paso={p} />,
  },
  {
    id: "tendencias", corto: "Modelo 1: tendencias", acto: 1, ante: "Lo que hicimos · 3 · modelo estadístico", titulo: "Con series comparables: el hurto está casi igual y la violencia sube", pasos: 3,
    quien: "Rafael", tiempo: "2:10-2:30",
    nota: `Primer modelo, ya con series comparables: los hurtos bajan desde 2023, ${signo(hp.post_cambio_anual_pct, 0)} % al año, pero 2023 fue un pico. Frente a 2022 la Policía registra ${signo(HURTO.policia2022a2026, 0)} %. (→) Y la violencia sube: homicidios ${signo(hom.post_cambio_anual_pct, 1)} % al año, delitos sexuales ${signo(ds.post_cambio_anual_pct, 1)} % y violencia intrafamiliar ${signo(vif.post_cambio_anual_pct, 1)} %. (→) El modelo controla tamaño, localidad y sobredispersión, y deja la pandemia fuera.`,
    profundizar: (
      <>
        <h3>El modelo de tendencias</h3>
        <p>Para cada delito: binomial negativa de panel, 19 localidades, enero-agosto, con efectos fijos de localidad y log(población) como exposición. Errores agrupados por localidad. Cambio anual = exp(β) − 1 del término lineal de año.</p>
        <p><b>Ventana:</b> 2022-2026 para las series validadas; 2023-2026 para hurto a personas, residencias y automotores, la parte comparable. Bicicletas no tiene con qué validarse y su tendencia no es significativa. Comercio, celulares y motocicletas no se modelan.</p>
        <p>Cálculo en <span className="mono">src/tendencias.py</span>; resultados en <span className="mono">outputs/tablas/tendencias_resumen.csv</span>.</p>
      </>
    ),
    render: (p) => <Tendencias paso={p} />,
  },
  {
    id: "modelos", corto: "Modelo 2: qué explica el miedo", acto: 1, ante: "Lo que hicimos · 4 · modelo supervisado", titulo: "Machine learning: qué explica el miedo, y qué no", pasos: 3,
    quien: "Rafael", tiempo: "2:30-2:55",
    nota: `Segundo modelo: entrenamos tres modelos para predecir quién siente insegura su zona y los probamos con personas que no vieron. Con hechos y contexto ordenan bien 72 de cada 100 parejas; con las calificaciones del barrio, 85. (→) Lo que más explica es lo que pasa en el barrio: atracos, conflictos, parques. (→) Y la prueba clave: el delito registrado no agrega nada a saber en qué localidad vive la persona: ${fmt(ctx[1].mean, 3)} frente a ${fmt(ctx[2].mean, 3)}. El miedo sigue a lo que la gente vive, no a la estadística.`,
    profundizar: (
      <>
        <h3>Diseño del aprendizaje supervisado</h3>
        <p>Bienal 2025, 5.538 adultos. Regresión logística, bosque aleatorio y gradient boosting, entrenados con el factor de expansión. Validación: 5 particiones × 5 repeticiones; AUC ponderada fuera de muestra.</p>
        <p><b>Importancia por bloques:</b> se permutan juntas las variables de un bloque en los datos de prueba y se mide cuánta AUC se pierde.</p>
        <p><b>Cuidado:</b> las calificaciones del barrio comparten cuestionario con la pregunta de seguridad (efecto halo: ruido y aire pesan casi como el alumbrado). Por eso las conclusiones se apoyan en hechos.</p>
        <p><b>Prueba de contexto:</b> con 19 localidades, tres tasas identifican la localidad. Comparar con efectos fijos de localidad muestra que el delito registrado no aporta información propia. Las tasas son de 2025, posteriores al quiebre de la serie.</p>
      </>
    ),
    render: (p) => <Modelos paso={p} />,
  },
  { ...B("prediccion"), acto: 1, ante: "Lo que hicimos · clase", soloClase: true },
  { ...B("vecinos"), acto: 1, ante: "Lo que hicimos · clase", soloClase: true, tiempo: "clase" },
  { ...B("repeticiones"), acto: 1, ante: "Lo que hicimos · clase", soloClase: true, tiempo: "clase" },
  {
    id: "tipologia", corto: "Modelo 3: tipos de localidad", acto: 1, ante: "Lo que hicimos · 5 · modelo no supervisado", titulo: "Cinco tipos de localidad, cada uno con su estrategia", pasos: 2,
    quien: "Samuel", tiempo: "2:55-3:15",
    nota: `Tercer modelo, sin variable objetivo: agrupamos las 19 localidades por sus cuatro frentes a la vez. (→) Salen cinco perfiles. Por ejemplo, San Cristóbal, Usme y Ciudad Bolívar: «${perfilDe("Usme")}». Bosa, Kennedy, Suba: «${perfilDe("Bosa")}». Cada perfil pide una estrategia distinta.`,
    profundizar: (
      <>
        <h3>Tipología de localidades</h3>
        <p>Ocho indicadores estandarizados de los cuatro frentes (los asimétricos en logaritmo): delitos y homicidios por 100.000, víctimas (EMV), violencia contra mujeres registrada, % que siente insegura su zona, miedo en el espacio público, luminarias por km² y espacio público por habitante.</p>
        <p>Componentes principales para ver las dimensiones y agrupamiento jerárquico de Ward. El número de perfiles se eligió con el coeficiente de silueta: 0,16 para 4 y 5 perfiles. Es una estructura débil: los perfiles describen, no son grupos naturales.</p>
        <p>Estabilidad: 500 repeticiones quitando un indicador y remuestreando localidades. Los nombres salen de reglas fijas sobre el centroide de cada perfil, no a mano. Quedó fuera la auditoría nocturna de 2019: el 86 % de sus puntos sale «brillante» y no distingue entre localidades.</p>
      </>
    ),
    render: (p) => <Tipologia paso={p} />,
  },

  /* ---------- Nudo · Lo que encontramos ---------- */
  { ...B("cifra-oculta"), acto: 2, ante: "Lo que encontramos · 1", titulo: "De cada 10 víctimas, menos de 2 llegan al registro", quien: "Samuel", tiempo: "3:15-3:35" },
  { ...B("indice"), acto: 2, ante: "Lo que encontramos · 2", quien: "Samuel", tiempo: "3:35-3:55" },
  { ...B("prueba"), acto: 2, ante: "Lo que encontramos · clase", soloClase: true, tiempo: "clase" },
  {
    id: "genero", corto: "Las mujeres", acto: 2, ante: "Lo que encontramos · 3", titulo: "Las mujeres: el miedo en la calle, la violencia en la casa", pasos: 3,
    quien: "Samuel", tiempo: "3:55-4:20",
    nota: "Con las mujeres hay dos problemas distintos. En la calle: 5 de cada 10 mujeres fueron acosadas el último año, y casi ninguna denuncia. (→) En la casa: la violencia contra ellas que llega a Salud subió 43 % desde 2019, y 8 de cada 10 casos pasan en la vivienda. Las más afectadas son niñas y adolescentes. (→) Son dos problemas distintos: una luminaria no resuelve la violencia en la casa.",
    profundizar: (
      <>
        <h3>Fuentes y cuidados</h3>
        <p><b>SIVIM</b> (Secretaría de Salud), 2019-2025: casos notificados al sector salud, tasa por 100.000 mujeres con la población de la SDP. Intervalo del cambio con binomial negativa. El 65 % del aumento está en niñas de 6 a 17 años, y desde 2022 crece la notificación escolar: parte del aumento es mejor registro. La violencia de pareja o expareja pasó de 5.298 a 10.525 casos.</p>
        <p><b>Acoso callejero</b> (Veeduría 2025): formulario en línea sin factor de expansión; describe a quienes respondieron (2.742 mujeres, 877 hombres), no estima la población.</p>
        <p><b>Temor al acoso</b> (Encuesta Mundial de Valores 2024): logit ponderado con sexo, edad, estrato y victimización.</p>
        <p><b>Hipótesis probadas</b> (Spearman, 19 localidades, Benjamini-Hochberg): iluminación, estado del sendero e internet público frente a la tasa de violencia contra mujeres. Ninguna sobrevive. Con n = 19 solo se detectaría |ρ| ≥ 0,60 con 80 % de potencia: es ausencia de evidencia de una relación fuerte, no prueba de que no exista.</p>
      </>
    ),
    render: (p) => <Mujeres paso={p} />,
  },
  { ...B("genero"), id: "genero-emv", corto: "Ellas temen más", acto: 2, ante: "Lo que encontramos · clase", soloClase: true, tiempo: "clase" },
  {
    id: "hipotesis", corto: "Lo que probamos", acto: 2, ante: "Lo que encontramos · 4", titulo: "Lo que probamos: ocho hipótesis, con su veredicto", pasos: 3,
    quien: "Samuel", tiempo: "4:20-4:40",
    nota: "Probamos ocho hipótesis, incluidas las que cualquiera daría por ciertas. (→) Seis no se sostienen: la serie de hurto no era comparable, el delito registrado no explica el miedo, peor alumbrado o peores vías no traen más hurto, más luz o internet no se asocian con menos violencia contra ellas, y la relación entre miedo y cifra oculta era mecánica. Dos sí: el entorno del barrio y el miedo de las mujeres. (→) Un nulo también es evidencia: evita gastar en lo que no mueve la aguja.",
    profundizar: (
      <>
        <h3>Cómo se probó cada una</h3>
        <ul>
          <li><b>Alumbrado y vías:</b> Spearman entre las 19 localidades urbanas, IC por bootstrap (10.000), p por permutación y Benjamini-Hochberg dentro de cada bloque. 0 de 23 pruebas sobreviven en la especificación principal (hurtos 2025). El inventario de luminarias sigue a la vía (40 a 57 por km), así que no mide «peor alumbrado»; no hay datos abiertos de luminarias apagadas ni de lux.</li>
          <li><b>Mujeres:</b> Spearman con la tasa SIVIM 2025, IC BCa y Benjamini-Hochberg.</li>
          <li><b>Potencia:</b> con n = 19, solo se detecta |ρ| ≥ 0,60 con 80 % de potencia. «No se sostiene» quiere decir que no hay evidencia de una relación fuerte por localidad, no que no exista en la cuadra.</li>
          <li><b>Lo que sí se asocia con el hurto:</b> las muertes en vía (ρ ≈ 0,55 con el promedio 2023-2025), pero ambas tasas comparten el denominador de residentes y miden actividad y tránsito, no alumbrado.</li>
        </ul>
        <p>Código: <span className="mono">src/fuentes_movilidad.py</span>, <span className="mono">src/fuentes_genero.py</span>, <span className="mono">src/modelos.py</span> y <span className="mono">src/aprendizaje.py</span>.</p>
      </>
    ),
    render: (p) => <Hipotesis paso={p} />,
  },

  /* ---------- Desenlace · Qué proponemos ---------- */
  {
    id: "estrategias", corto: "Estrategias", acto: 3, ante: "Qué proponemos", titulo: "Estrategias que solo aparecen al unir los datos", pasos: 3,
    quien: "Brandow", tiempo: "4:40-5:35",
    nota: "Y aquí está lo que ninguna fuente sola deja ver. Cada estrategia trae el dato que la sostiene, su nivel de evidencia y cómo se mide. (→ recorran de a dos)",
    profundizar: (
      <>
        <h3>Nivel de evidencia</h3>
        <p><b>Alta:</b> fuentes con score de 70 o más, prueba significativa tras corregir por pruebas múltiples y robusta a otra especificación.</p>
        <p><b>Media:</b> falla una de las dos condiciones.</p>
        <p><b>Exploratoria:</b> fuente débil o resultado no significativo. Se reporta igual, porque un nulo también es evidencia.</p>
      </>
    ),
    render: (p) => <Estrategias paso={p} />,
  },
  { ...B("simulador"), acto: 3, ante: "Qué proponemos · clase", soloClase: true },
  { ...B("propuesta"), acto: 3, ante: "Qué proponemos · clase", soloClase: true, tiempo: "clase" },
  { ...B("cierre"), tiempo: "5:35-5:45", nota: "Bogotá ya tiene los datos para cerrar esta brecha. Solo hay que validarlos y leerlos juntos. Gracias." },
];

export function Clase() {
  return <Motor diapos={DIAPOS} />;
}
