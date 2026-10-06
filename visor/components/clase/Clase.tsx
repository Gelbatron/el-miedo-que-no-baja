"use client";
import { D, R, fmt, signo } from "@/lib/datos";
import { C } from "@/lib/clase";
import { Motor, type Diapo } from "./Motor";
import { CifraOculta, Datos, Indice, Paradoja, Portada, Termometros } from "./diapos-a";
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

export const DIAPOS: Diapo[] = [
  {
    id: "inicio", corto: "Portada", pasos: 1, roja: true, quien: "Brandow", tiempo: "0:00-0:15",
    nota: "Somos The data squad. Venimos a explicar una paradoja de Bogotá: el delito registrado baja, pero el miedo no. ¿Por qué pasa, y dónde debe actuar primero el Distrito?",
    render: () => <Portada />,
  },
  {
    id: "paradoja", corto: "La paradoja", ante: "1 · La paradoja", titulo: "Bogotá registra menos delitos, pero no se siente más segura", pasos: 3,
    quien: "Brandow", tiempo: "0:15-0:45",
    nota: "(Aparece la línea azul) El hurto a personas registrado cayó 65 % entre 2019 y 2026. (→) Pero no todo baja: la violencia intrafamiliar y los delitos sexuales suben, y pasan sobre todo en la casa. (→) Y el 74 % de los adultos siente insegura la ciudad. Lo que se cuenta baja; lo que se siente, no.",
    render: (p) => <Paradoja paso={p} />,
  },
  {
    id: "termometros", corto: "Si el miedo siguiera al delito", ante: "2 · La primera pista", titulo: "Si el miedo siguiera al delito, veríamos una diagonal", pasos: 3,
    quien: "Brandow", tiempo: "0:45-1:15",
    nota: "Pregúntenle al público antes de mostrar: si el miedo siguiera al delito, ¿dónde esperarían más miedo? (→) Donde más se registra: esta diagonal. (→) Pero no: Usme y Ciudad Bolívar registran poco y tienen el miedo más alto; Teusaquillo y Los Mártires registran mucho y tienen menos. La correlación es −0,25: ninguna. El registro no dice dónde está el miedo.",
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
  {
    id: "datos", corto: "Cómo llegamos", ante: "3 · Cómo llegamos al análisis", titulo: "Siete fuentes públicas unidas por una sola llave", pasos: 3,
    quien: "Rafael", tiempo: "1:15-1:40",
    nota: "¿Cómo lo sabemos? Unimos siete fuentes públicas: dos encuestas para lo que se siente, la Secretaría de Seguridad para lo que se registra y cuatro de contexto. (→) Cada fuente escribe la localidad distinto: todo se lleva al código oficial. (→) Y siempre comparamos por habitante: en casos gana Suba porque es enorme; por habitante, el centro.",
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
    id: "indice", corto: "Índice de Brecha", ante: "4 · Una sola cifra para la brecha", titulo: "Índice de Brecha: cuánto miedo sobra frente al registro", pasos: 4,
    quien: "Rafael", tiempo: "1:40-2:25",
    nota: `Para medir la brecha con una sola cifra construimos el Índice de Brecha. Primero el miedo en una regla común: desviaciones frente al promedio de la ciudad. (→) Luego el registro en la misma regla. (→) Y restamos: Usme tiene ${signo(usme.z_percepcion, 2)} de miedo y ${signo(usme.z_registro, 2)} de registro, brecha de ${signo(usme.ibs, 2)}. (→) Como toda estimación tiene margen de error, la repetimos 1.000 veces: Usme y Ciudad Bolívar quedan en el top 5 en todas, Bosa en el 99,5 %.`,
    profundizar: (
      <>
        <h3>Cómo se calcula y qué tan estable es</h3>
        <p><b>Fórmula:</b> z(% que califica mala la seguridad de su zona) − z(logaritmo de los delitos de alto impacto por 100.000). z = (valor − promedio) / desviación estándar entre las 19 localidades.</p>
        <p><b>Por qué logaritmo:</b> el centro recibe población flotante; sin él, dos localidades definirían toda la escala.</p>
        <p><b>Incertidumbre:</b> remuestreamos 1.000 veces a los encuestados de la Bienal dentro de cada localidad. Probabilidad de estar en el top 5: {top5.map((f) => `${f.nombre} ${fmt(f.prob_top5 * 100, 0)} %`).join(", ")}.</p>
        <p><b>Escala:</b> con la Encuesta Distrital de Percepción se calcula igual para las 33 UPL, cada semestre.</p>
      </>
    ),
    render: (p) => <Indice paso={p} />,
  },
  {
    id: "cifra-oculta", corto: "Hallazgo 1 · cifra oculta", ante: "5 · Hallazgo 1", titulo: "Donde sobra miedo, el delito no se está registrando", pasos: 3,
    quien: "Rafael", tiempo: "2:25-3:05",
    nota: `Primer hallazgo: por cada delito registrado hay ${fmt(R.cifra_oculta_bogota)} víctimas según la Encuesta Mundial de Valores; en Bosa, 10,6 (cambien el selector). (→) Y donde hay más miedo que registro, hay más delito sin registrar: correlación de 0,72. (→) ¿Casualidad? Probamos siete relaciones y solo esta sobrevive a la corrección por pruebas múltiples. El miedo de la periferia no es exagerado: es delito que no llega a las cifras.`,
    profundizar: (
      <>
        <h3>Cifra oculta y pruebas múltiples</h3>
        <p><b>Víctimas:</b> % de adultos que dicen haber sido víctimas en el último año (EMV 2024) × adultos de la localidad (SDP). <b>Delitos:</b> registro de la SCJ en 2024, enero-agosto llevado a 12 meses.</p>
        <p>Compara personas con hechos, así que se lee como orden de magnitud. Con 96 encuestas por localidad, cada razón lleva su intervalo: Bosa {fmt(bosa.razon)} (IC 95 % de {fmt(bosa.razon_inf)} a {fmt(bosa.razon_sup)}).</p>
        <p><b>Benjamini-Hochberg:</b> al probar siete relaciones, alguna saldría «significativa» por azar. La corrección ajusta los valores p por el número de pruebas; solo el Índice de Brecha frente a la cifra oculta queda bajo 0,05 (p ajustado 0,004).</p>
      </>
    ),
    render: (p) => <CifraOculta paso={p} />,
  },
  {
    id: "vecinos", corto: "Hallazgo 2 · entorno", ante: "6 · Hallazgo 2", titulo: "Dos vecinos iguales: qué cambia el miedo y qué no", pasos: 3,
    quien: "Samuel", tiempo: "3:05-3:45",
    nota: `¿Qué hace que alguien sienta insegura su zona? Comparemos personas iguales en todo menos en una cosa. Esta vecina parte de ${fmt(vecina.p0, 0)} %. (→ muevan el deslizador de hurtos de punta a punta) Del menor al mayor hurto registrado: casi nada. Los homicidios sí pesan algo. (→ activen «atracos en el parque» y suban los conflictos) Ver atracos en el parque: ${signo(vecina.atracos, 0)} puntos. Conflictos con vecinos: hasta ${signo(vecina.conflictos, 0)}. El barrio se siente por lo que pasa en él.`,
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
    id: "repeticiones", corto: "¿Y si fue suerte?", ante: "7 · ¿Y si fue suerte?", titulo: "Repetimos el análisis 300 veces, sorteando las localidades", pasos: 2,
    quien: "Samuel", tiempo: "3:45-4:05",
    nota: "¿Y si fue suerte? Repetimos el análisis 300 veces sorteando localidades. (Los puntos caen) Los atracos en el parque nunca tocan el cero. (→) El hurto registrado cae a los dos lados del cero: no se distingue de nada.",
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
    id: "prediccion", corto: "¿El modelo adivina?", ante: "8 · ¿Qué predice mejor el miedo?", titulo: "El entorno predice el miedo; el delito registrado, casi nada", pasos: 4, soloClase: true,
    quien: "Samuel", tiempo: "clase",
    nota: "Le damos al modelo dos personas al azar, una que siente insegura su zona y otra que no. Una moneda acierta 50 de cada 100. Con el perfil, 61. (→) Sumar el delito registrado: 61,1. Nada. (→) Sumar los hechos del entorno: 65,5. (→) Todo junto: 78.",
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
    id: "genero", corto: "Hallazgo 3 · género", ante: "9 · Hallazgo 3", titulo: "Las mujeres reportan menos delitos y recortan más su vida", pasos: 3,
    quien: "Samuel", tiempo: "4:05-4:40",
    nota: "Tercer hallazgo. Las mujeres dicen haber sido víctimas menos que los hombres. (→) Pero temen más el acoso y evitan más salir de noche. (→) Comparando iguales, con la misma edad, estrato y victimización, ser mujer suma 18 puntos de temor al acoso sexual. El costo del miedo se paga en autonomía.",
    profundizar: (
      <>
        <h3>Encuesta Mundial de Valores 2024</h3>
        <p>{fmt(R.n_emv_bogota, 0)} encuestas en Bogotá (96 por localidad), ponderadas con su factor. Logit ponderado con sexo, edad, estrato y si fue víctima; intervalos por bootstrap de localidades.</p>
        <p>Contexto del registro: violencia intrafamiliar {signo(R.vif_cambio_pct_2018_2026, 1)} % y delitos sexuales {signo(R.delitos_sexuales_cambio_pct_2018_2026, 1)} % entre 2018 y 2026. Ocurren sobre todo en la casa y el entorno cercano, por eso la recomendación de género va más allá del espacio público.</p>
      </>
    ),
    render: (p) => <Genero paso={p} />,
  },
  {
    id: "simulador", corto: "¿Cuánto cambiaría?", ante: "10 · ¿Cuánto cambiaría?", titulo: "Si mejoramos alumbrado y parques, ¿cuánto baja el miedo?", pasos: 1, soloClase: true,
    quien: "Brandow", tiempo: "clase",
    nota: "Muevan los deslizadores. Con la mitad de las zonas con buen alumbrado y la mitad de los parques sin atracos, la inseguridad percibida baja 7,4 puntos en Bogotá: unos 467 mil adultos. Es una sensibilidad del modelo, no una promesa causal.",
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
    id: "propuesta", corto: "Qué proponemos", ante: "11 · Qué proponemos", titulo: "Un indicador para toda la ciudad y cuatro decisiones", pasos: 2,
    quien: "Brandow", tiempo: "4:40-5:15",
    nota: "Proponemos un indicador para toda la ciudad: el Índice de Brecha, con fuentes que ya existen, cada semestre y por UPL. (→) Y cuatro decisiones: medir con victimización; priorizar entornos con la regla del índice, que hoy señala a Usme, Ciudad Bolívar, Bosa, Kennedy y San Cristóbal; medir la autonomía de las mujeres; y abrir los datos para evaluar.",
    render: (p) => <Propuesta paso={p} />,
  },
  {
    id: "cierre", corto: "Cierre", pasos: 1, roja: true, quien: "Brandow", tiempo: "5:15-5:25",
    nota: "Bogotá ya produce los datos para cerrar esta brecha. Hay que leerlos juntos. Gracias.",
    render: () => <Cierre />,
  },
];

export function Clase() {
  return <Motor diapos={DIAPOS} />;
}
