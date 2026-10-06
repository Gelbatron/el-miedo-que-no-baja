"use client";
import { D, R, fmt, signo } from "@/lib/datos";
import { C } from "@/lib/clase";
import { PANDEMIA } from "@/lib/historia";
import { Motor, type Diapo } from "./Motor";
import { BOGOTA, CifraOculta, Datos, Indice, Paradoja, Portada, Prueba, Termometros } from "./diapos-a";
import { Cierre, Genero, Prediccion, Propuesta, Repeticiones, SimuladorClase, Vecinos } from "./diapos-b";

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
const cada100 = (r: number) => fmt(100 / r, 0);

// Cuatro actos, la historia que cuenta el equipo:
// 0 el problema · 1 lo que hicimos · 2 lo que encontramos · 3 por qué importa
export const DIAPOS: Diapo[] = [
  {
    id: "inicio", corto: "Portada", pasos: 1, roja: true, quien: "Brandow", tiempo: "0:00-0:10",
    nota: "Somos The data squad. Les vamos a contar algo que encontramos en los datos de Bogotá y que no cuadra.",
    render: () => <Portada />,
  },

  /* ---------- Acto 1 · El problema ---------- */
  {
    id: "paradoja", corto: "En el papel mejora", acto: 0, ante: "El problema · 1", titulo: "En el papel, Bogotá mejora. La gente no lo siente.", pasos: 3,
    quien: "Brandow", tiempo: "0:10-0:45",
    nota: `Resulta que estuvimos revisando los datos de la Secretaría de Seguridad y el hurto viene bajando muchísimo: ${signo(R.hurto_personas.cambio_pct, 0)} % desde 2019. Ojo, ahí está la pandemia (la franja gris): en 2020 cayó por el encierro, pero en 2022 volvió casi a lo de antes y desde entonces bajó ${fmt(-PANDEMIA.hurto2022a2026, 0)} %. No es solo la pandemia. (→) Pero hay hechos violentos que van al revés: la violencia intrafamiliar y los delitos sexuales subieron cerca de 45 %. (→) Y cuando lo cruzamos con las encuestas, 3 de cada 4 personas dicen que Bogotá es insegura. O sea: en el papel la ciudad mejora, pero la gente no lo siente.`,
    profundizar: (
      <>
        <h3>El efecto pandemia</h3>
        <p>En 2020 el hurto a personas registrado cayó {fmt(-PANDEMIA.hurto2020, 0)} % por el encierro. En 2022 volvió al {fmt(PANDEMIA.hurto2022sobre2019, 0)} % de su nivel de 2019, y desde ahí bajó {fmt(-PANDEMIA.hurto2022a2026, 0)} % hasta 2026: la caída no es solo pandemia.</p>
        <p>Una señal para revisar: entre 2022 y 2023 todos los tipos de hurto (personas, celulares, motos, residencias y automotores) cayeron a la vez, entre {fmt(PANDEMIA.caida2023min, 0)} % y {fmt(PANDEMIA.caida2023max, 0)} % en un solo año. Una caída tan pareja puede ser menos delito o menos denuncia; el registro solo no lo distingue. Por eso medimos también con encuestas.</p>
        <p>La violencia intrafamiliar casi no se movió con la pandemia ({signo(PANDEMIA.vif2020, 0)} % en 2020) y desde 2022 subió {fmt(PANDEMIA.vif2022a2026, 0)} %.</p>
      </>
    ),
    render: (p) => <Paradoja paso={p} />,
  },
  {
    id: "cifra-oculta", corto: "Mucho delito no se denuncia", acto: 0, ante: "El problema · 2", titulo: "Y mucho delito ni siquiera se denuncia", pasos: 1,
    quien: "Brandow", tiempo: "0:45-1:15",
    nota: `Y nos dimos cuenta de que mucho delito ni siquiera llega a las cifras. Hagan la cuenta con nosotros (señalen los tres pasos): el ${fmt(BOGOTA.emv_victima)} % de los adultos dice haber sido víctima en el último año, unos ${fmt(Math.round(BOGOTA.victimas_estimadas / 1e5) / 10, 1)} millones de personas; la Secretaría registró unos ${fmt(Math.round(BOGOTA.delitos_registrados / 1e3), 0)} mil delitos. Por cada 100 víctimas, solo ${cada100(BOGOTA.razon)} quedan en el registro. (Cambien el selector a Bosa: ${cada100(bosa.razon)}.)`,
    profundizar: (
      <>
        <h3>Cómo se calcula la cifra oculta</h3>
        <p><b>Víctimas:</b> % de adultos que dicen haber sido víctimas en el último año (Encuesta Mundial de Valores 2024) × adultos de la localidad (SDP). <b>Delitos:</b> registro de la Secretaría de Seguridad en 2024, enero a agosto llevado a 12 meses.</p>
        <p>Compara personas con hechos, así que se lee como orden de magnitud. Con 96 encuestas por localidad, cada razón lleva su intervalo: Bosa {fmt(bosa.razon)} víctimas por delito (IC 95 % de {fmt(bosa.razon_inf)} a {fmt(bosa.razon_sup)}).</p>
        <p>En el centro (Los Mártires, La Candelaria) se registran tantos delitos como víctimas residentes o más: allí llega gente de toda la ciudad.</p>
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
    id: "prueba", corto: "No es casualidad", acto: 1, ante: "Lo que hicimos · 3", titulo: "No es casualidad: donde sobra miedo, falta denuncia", pasos: 2,
    quien: "Rafael", tiempo: "2:40-3:05",
    nota: "¿Y eso es real? Donde el índice marca más miedo, más delito se queda sin denunciar: correlación de 0,72. (→) Probamos siete relaciones distintas y esta es la única que pasa la corrección por azar. O sea: el miedo de la periferia no es exagerado, es delito que no llega a las cifras.",
    profundizar: (
      <>
        <h3>Pruebas múltiples</h3>
        <p>Cruzamos siete pares de indicadores entre localidades (miedo y delito, víctimas y delito, alumbrado y luminarias, entre otros). Con siete pruebas, alguna saldría «significativa» por puro azar.</p>
        <p>La corrección de Benjamini-Hochberg ajusta los valores p por el número de pruebas. Solo el Índice de Brecha frente a la cifra oculta queda bajo 0,05 (p ajustado 0,004).</p>
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

export function Clase() {
  return <Motor diapos={DIAPOS} />;
}
