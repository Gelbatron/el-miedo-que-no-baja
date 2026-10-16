import Link from "next/link";
import type { ReactNode } from "react";
import { D, R, fmt, signo } from "@/lib/datos";
import { F, tendencia } from "@/lib/frentes";

export const metadata = { title: "Modelos · El miedo que no baja" };

type Bloque = { id: string; n: string; titulo: string; h?: string; pregunta: string; formula?: string; espec: ReactNode; incert: ReactNode; resultado: ReactNode; limites: ReactNode; salida: string };

const ic = (a: number, b: number, d = 1) => `IC 95 % ${fmt(a, d)} a ${fmt(b, d)}`;

function Modelo({ b }: { b: Bloque }) {
  return (
    <article id={b.id} className="md tarjeta">
      <header className="md-cab">
        <span className="md-n">{b.n}</span>
        <div><h2>{b.titulo}</h2><p className="md-preg">{b.pregunta}</p></div>
        {b.h && <span className="md-h">{b.h}</span>}
      </header>
      {b.formula && <pre className="md-f">{b.formula}</pre>}
      <dl className="md-dl">
        <dt>Especificación</dt><dd>{b.espec}</dd>
        <dt>Incertidumbre</dt><dd>{b.incert}</dd>
        <dt>Resultado</dt><dd className="md-res">{b.resultado}</dd>
        <dt>Supuestos y límites</dt><dd>{b.limites}</dd>
        <dt>Salida</dt><dd><code>{b.salida}</code></dd>
      </dl>
    </article>
  );
}

export default function Modelos() {
  const a = R.ame_hechos, w = (v: string) => D.lpm_wild.find((x) => x.variable === v)!;
  const t = { H: tendencia("H"), DS: tendencia("DS"), VI: tendencia("VI") };
  const raz = F.registro.razones.filter((r) => r.codigo === "HP");
  const pre = raz.filter((r) => r.anio < 2023).map((r) => Number(r.razon_scj_siedco)), pos = raz.filter((r) => r.anio >= 2023).map((r) => Number(r.razon_scj_siedco));
  const auc = (b: string) => D.auc.find((x) => x.bloque === b)!;
  const ml = F.ml.sin_calificaciones as { modelo: string; mean: number; std: number }[];
  const mlc = F.ml.completo as { modelo: string; mean: number }[];
  const ctx = F.ml.contexto_localidad as { spec: string; mean: number; std: number }[];
  const v = (p: string) => D.validaciones.find((x) => x.prueba.startsWith(p))!;
  const pa = R.ibs_vs_cifra_oculta_parcial, zc = R.zona_vs_cifra_oculta, vr = R.victimas_vs_registro;
  const top = [...D.ibs].sort((x, y) => Number(x.puesto) - Number(y.puesto)).slice(0, 5);
  const mujer = R.emv_mujer_ame.teme_acoso_sexual;
  const sivim = (F.genero.localidades as Record<string, number>[]).find((l) => Number(l.localidad) === 0)!;
  const esc = D.escenarios.find((e) => e.grupo === "total" && e.localidad === 0)!;
  const menos = esc.p00 - (esc.p00 + esc.p10 + esc.p01 + esc.p11) / 4;

  const B: Bloque[] = [
    {
      id: "integracion", n: "0", titulo: "Integración y llave territorial", pregunta: "¿Cómo se vuelven comparables 18 fuentes con unidades, años y nombres distintos?",
      espec: <>Normalizador de nombres y códigos al código oficial de localidad (1-20); análisis en las 19 urbanas. Tasas por 100.000 habitantes con la población SDP del mismo año. Microdatos con su factor de expansión (Bienal) o de ponderación (EMV); a cada persona de la Bienal se le asigna el delito y las llamadas 123 de su localidad. Delito siempre de enero a agosto. Cada fuente lleva una nota de confiabilidad de 0 a 100 con seis criterios (el sexto, verificación contra una fuente independiente).</>,
      incert: "Bitácora por fuente con conteos y controles de totales; la nota de confiabilidad acompaña cada cifra en el visor.",
      resultado: <>{F.confiabilidad.length} fuentes en 4 frentes y un panel de 19 localidades.</>,
      limites: "El delito solo existe abierto por localidad (no por UPZ); persona y hecho no son la misma unidad.", salida: "data/procesados/ · bitacora_limpieza.csv · confiabilidad",
    },
    {
      id: "validacion", n: "1", titulo: "Validación del registro", h: "H0", pregunta: "¿La serie abierta de hurtos es comparable en el tiempo?",
      formula: "razón(t) = casos capa SCJ(t) / casos SIEDCO(t)      criterio de misma serie: 0,95 ≤ razón ≤ 1,10",
      espec: "Razón capa SCJ ÷ SIEDCO (Policía) y ÷ Medicina Legal por delito y año, enero-agosto.",
      incert: "Contraste externo con la ECSC del DANE (victimización y denuncia, con errores publicados) y la EPV de la Cámara de Comercio.",
      resultado: <>Hurto a personas: razón {fmt(Math.min(...pre), 2)} a {fmt(Math.max(...pre), 2)} en 2018-2022 y {fmt(Math.min(...pos), 2)} a {fmt(Math.max(...pos), 2)} desde 2023. La caída de {fmt(Math.abs(R.hurto_personas_capa.cambio_2022_pct), 0)} % de la capa es {signo(R.hurto_personas.cambio_2022_pct, 1)} % con la Policía. <b>H0 no se sostiene.</b></>,
      limites: "No sabemos qué cambió en el método de 2023 (la capa no lo documenta); lo dejamos como recomendación, no como evaluación de la entidad.", salida: "registro_*.csv",
    },
    {
      id: "tendencias", n: "2", titulo: "Tendencias en series validadas", pregunta: "¿Qué delitos crecen cuando la serie es comparable?",
      formula: "log E[y_it] = log(población_it) + α_i + β · t        y_it ~ BinNeg(μ_it, α)",
      espec: "Binomial negativa de panel, 19 localidades × años, enero-agosto; efecto fijo de localidad y población como exposición. Ventana 2022-2026 en series validadas; 2023-2026 en hurtos con quiebre.",
      incert: "Errores agrupados por localidad; IC 95 % del cambio anual (exp(β) − 1).",
      resultado: <>Violencia intrafamiliar {signo(t.VI.post_cambio_anual_pct, 1)} % al año ({ic(t.VI.post_ic_inf, t.VI.post_ic_sup)}); delitos sexuales {signo(t.DS.post_cambio_anual_pct, 1)} % ({ic(t.DS.post_ic_inf, t.DS.post_ic_sup)}); homicidios {signo(t.H.post_cambio_anual_pct, 1)} % ({ic(t.H.post_ic_inf, t.H.post_ic_sup)}).</>,
      limites: "Cinco años por serie; el cambio anual es un promedio log-lineal, no una proyección.", salida: "tendencias_resumen.csv",
    },
    {
      id: "explicativo", n: "3", titulo: "Qué explica el miedo (modelo inferencial)", h: "H1", pregunta: "¿Pesa más el delito registrado de la localidad o lo que pasa en el barrio?",
      formula: "P(zona insegura_i = 1) = Λ(γ·perfil_i + δ·delito registrado_l(i) + θ·hechos del entorno_i)",
      espec: "Logit ponderado sobre la Bienal 2025 (resultado: califica mala o muy mala la seguridad de su zona). Perfil: sexo, edad, estrato, arriendo. Delito registrado de la localidad: hurtos y homicidios por 100.000, llamadas 123 por narcóticos. Hechos del entorno tomados de otras preguntas (atracos o consumo en el parque, conflictos entre vecinos, acoso presenciado). Se reportan efectos marginales promedio (AME).",
      incert: <>IC de los AME por bootstrap de conglomerados (300 réplicas, se remuestrean localidades). Con 19 conglomerados, la prueba del delito registrado usa wild cluster bootstrap con pesos de Webb (999 réplicas).</>,
      resultado: <>Atracos en el parque {signo(a.parque_atracos.ame_pp, 1)} pp ({ic(a.parque_atracos.ic_inf, a.parque_atracos.ic_sup)}); conflictos entre vecinos {signo(a.conflictos_vecinos.ame_pp, 1)} pp ({ic(a.conflictos_vecinos.ic_inf, a.conflictos_vecinos.ic_sup)}). Hurto registrado {signo(w("hurtos_100k_miles").coef_pp, 1)} pp, p wild = {fmt(w("hurtos_100k_miles").p_wild, 2)}. Homicidios {signo(w("homicidios_100k").coef_pp, 2)} pp por homicidio adicional por 100.000, p wild = {fmt(w("homicidios_100k").p_wild, 3)}.</>,
      limites: <>Asociación, no causalidad. Robustez: efectos fijos de localidad, modelo lineal ponderado y otros resultados (ciudad insegura, miedo en el espacio público). Las calificaciones del entorno (alumbrado, ventas) comparten batería con la pregunta de seguridad: van en un modelo aparte por sesgo de método común.</>,
      salida: "m_hechos.csv · lpm_wild.csv · m_efectos_fijos.csv · m_calif.csv",
    },
    {
      id: "ml", n: "4", titulo: "Aprendizaje supervisado", h: "H1", pregunta: "¿La conclusión depende de la forma funcional del logit?",
      espec: "Regresión logística L2, bosque aleatorio (400 árboles, hoja mínima 20) y gradient boosting por histogramas (300 iteraciones, tasa 0,05, 15 hojas, hoja mínima 40, L2 = 1), con el factor de expansión como peso. Importancia por bloques: se permutan juntas las variables de cada bloque en los datos de prueba. Prueba de contexto: delito registrado frente a efectos fijos de localidad.",
      incert: "Validación cruzada estratificada 5 × 5 (25 evaluaciones), AUC ponderada fuera de muestra; media y desviación estándar.",
      resultado: <>Sin calificaciones del barrio: {ml.map((m) => `${m.modelo} ${fmt(m.mean, 3)}`).join(" · ")}. Con calificaciones: hasta {fmt(Math.max(...mlc.map((m) => m.mean)), 2)}. Contexto: {ctx.map((c) => `${c.spec} ${fmt(c.mean, 3)}`).join(" · ")}. El delito registrado no aporta nada propio frente a saber la localidad.</>,
      limites: <>AUC = probabilidad de ordenar bien una pareja (una persona que siente insegura su zona y otra que no); 0,5 es azar. Los bloques del logit lineal: perfil {fmt(auc("Perfil (sexo, edad, estrato, tenencia)").auc, 3)}, + delito {fmt(auc("Perfil + delito registrado").auc, 3)}, + hechos {fmt(auc("Perfil + hechos del entorno").auc, 3)}.</>,
      salida: "ml_comparacion_modelos*.csv · ml_importancia_bloques*.csv · ml_contexto_localidad.csv · auc.csv",
    },
    {
      id: "tipologia", n: "5", titulo: "Aprendizaje no supervisado: perfiles de localidad", pregunta: "¿Hay grupos de localidades con el mismo problema?",
      espec: "Ocho indicadores estandarizados de los cuatro frentes (logaritmo en tasas asimétricas); componentes principales; agrupamiento jerárquico de Ward; k entre 3 y 5 elegido por silueta.",
      incert: "Estabilidad con 500 perturbaciones: se quita un indicador al azar y se remuestrean localidades.",
      resultado: "5 perfiles; el de miedo alto, poca luz y más homicidios reúne a San Cristóbal, Usme y Ciudad Bolívar.",
      limites: "Silueta 0,16 con k = 5: perfiles descriptivos, no clases nítidas. Sirven para agrupar intervenciones, no como tipología cerrada.", salida: "tipologia_*.csv",
    },
    {
      id: "validaciones", n: "6", titulo: "Validaciones territoriales y la hipótesis que descartamos", h: "H2", pregunta: "¿Donde sobra miedo, falta denuncia?",
      formula: "ρ_parcial(x, y | z) = corr(rango(x) − ŷ(rango z), rango(y) − ŷ(rango z))      gl = n − 3",
      espec: "Spearman entre las 19 localidades para ocho relaciones entre percepción, victimización, registro y entorno. Si dos índices comparten un componente, Spearman parcial sobre los residuos de los rangos.",
      incert: "IC bootstrap (2.000 réplicas) y corrección de Benjamini-Hochberg. Con n = 19, la potencia del 80 % exige |ρ| ≥ 0,60 (z de Fisher: 2,80 / √16 ≈ 0,70).",
      resultado: <>Índice de Brecha frente a cifra oculta: ρ = {fmt(R.ibs_vs_cifra_oculta.rho, 2)} (p BH = {fmt(v("Índice de Brecha").p_bh, 3)}), pero controlando el delito registrado ρ = {fmt(pa.rho, 2)} (p = {fmt(pa.p, 2)}). La prueba directa, miedo frente a cifra oculta: ρ = {fmt(zc.rho, 2)} (p = {fmt(zc.p, 2)}). <b>H2 no se sostiene: la relación era mecánica.</b> Víctimas frente a registro: ρ = {fmt(vr.rho, 2)}.</>,
      limites: "La parcial se agregó después de ver el primer resultado y así lo reportamos. Con 19 unidades, un nulo no prueba ausencia de relación.", salida: "validaciones.csv · validacion_parcial.csv",
    },
    {
      id: "cifra", n: "7", titulo: "Cifra oculta", pregunta: "¿Cuántas víctimas hay por cada delito registrado?",
      formula: "razón_l = (% víctima EMV_l × adultos SDP_l) / (delitos de alto impacto SCJ_l, enero-agosto × 12/8)",
      espec: "EMV 2024 (víctimas) frente a SCJ 2024 (delitos de alto impacto, anualizados).",
      incert: "IC con el error estándar de la EMV por localidad; sensibilidad con la ECSC del DANE y la EPV.",
      resultado: <>Bogotá: {fmt(R.cifra_oculta_bogota, 1)} víctimas por delito registrado ({fmt(10 / R.cifra_oculta_bogota, 1)} de cada 10 llegan al registro). Rango: {R.cifra_oculta_max[0]} {fmt(R.cifra_oculta_max[1], 1)} a {R.cifra_oculta_min[0]} {fmt(R.cifra_oculta_min[1], 1)}.</>,
      limites: "Compara personas con hechos, y lugar de residencia con lugar de ocurrencia: es un orden de magnitud, no una tasa de denuncia.", salida: "cifra_oculta.csv",
    },
    {
      id: "ibs", n: "8", titulo: "Índice de Brecha de Seguridad", pregunta: "¿Dónde hay más miedo del que explica el delito registrado?",
      formula: "IBS_l = z(% zona insegura_l) − z(ln delitos de alto impacto por 100.000_l)",
      espec: "Estandarización entre las 19 localidades; el logaritmo corrige la asimetría de la tasa en el centro.",
      incert: "Bootstrap ponderado dentro de cada localidad (1.000 réplicas): IC 90 % del índice y probabilidad de quedar en el top 5.",
      resultado: <>{top.map((l) => `${l.nombre} ${fmt(Number(l.ibs), 2)} (top 5 en ${fmt(Number(l.prob_top5) * 100, 0)} %)`).join(" · ")}.</>,
      limites: "Ordena dónde actuar primero; no prueba causas. Comparte el delito registrado con la cifra oculta, por eso no se usa para validarla.", salida: "ibs.csv · ficha del indicador (/indicador)",
    },
    {
      id: "genero", n: "9", titulo: "Enfoque de género", h: "H3", pregunta: "¿A igual victimización, las mujeres temen más?",
      espec: "EMV: logit ponderado con sexo, edad, estrato y haber sido víctima; AME de ser mujer. SIVIM (Salud): tasas por 100.000 mujeres y binomial negativa NB2 (α = 0,0276) en panel 19 × 2013-2025 con efectos fijos de localidad y año.",
      incert: "AME con bootstrap por localidades; IC de los cambios de tasa con el modelo de panel.",
      resultado: <>Temor al acoso sexual {signo(mujer.ame_pp, 1)} pp ({ic(mujer.ic_inf, mujer.ic_sup)}). Violencia contra las mujeres notificada a Salud {signo(sivim.cambio_pct_2019_2025, 1)} % de 2019 a 2025 ({ic(sivim.cambio_pct_2019_2025_ic_inf, sivim.cambio_pct_2019_2025_ic_sup, 0)}). <b>H3 se sostiene.</b></>,
      limites: "SIVIM mide casos notificados, que también responden a la capacidad de detección del sistema de salud.", salida: "emv_*.csv · genero_*",
    },
    {
      id: "entorno", n: "10", titulo: "Alumbrado, vías y violencia contra las mujeres", pregunta: "¿Las condiciones físicas explican el hurto o la violencia?",
      espec: "23 pruebas de Spearman entre condiciones (luminarias, malla vial, siniestralidad, calidad del alumbrado) y hurtos de 2025 por 100.000; iluminación y conectividad frente a la tasa SIVIM.",
      incert: "IC bootstrap (10.000 réplicas), p por permutación y Benjamini-Hochberg dentro de cada bloque.",
      resultado: "Ninguna relación sobrevive a la corrección: luminarias por km de vía ρ = +0,48 (en sentido contrario al esperado), alumbrado malo ρ = −0,02, estado de las vías ρ = −0,35 (p BH = 0,34). Son resultados nulos útiles: evitan invertir en lo que no mueve la aguja.",
      limites: "El inventario de alumbrado más reciente es de 2019; con 19 localidades la potencia es baja.", salida: "movilidad_pruebas_hipotesis.csv",
    },
    {
      id: "escenarios", n: "11", titulo: "Escenarios del simulador", pregunta: "¿Cuánto cambiaría la inseguridad percibida si mejora el entorno?",
      formula: "Δ = P̄(observado) − ¼ · [P̄(00) + P̄(10) + P̄(01) + P̄(11)]      sobre el modelo de hechos más alumbrado",
      espec: "Probabilidad predicha media con alumbrado malo = 0, atracos en el parque = 0, o ambos, promediando la mitad de los casos.",
      incert: "Sensibilidad del modelo, no efecto causal.",
      resultado: <>{fmt(menos, 1)} puntos menos de inseguridad percibida en la zona: del orden de {fmt((menos / 100) * R.adultos_urbanos_bienal / 1000, 0)} mil adultos.</>,
      limites: "Supone que la asociación se mantiene al intervenir; sirve para priorizar, no para prometer.", salida: "escenarios.csv · /simulador",
    },
  ];

  return (
    <div className="contenedor pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Para el jurado técnico · especificación, incertidumbre y validación</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Modelos: qué estimamos, cómo y con qué incertidumbre</h1>
        <p className="bajada">
          Cada componente con la pregunta que responde, su especificación, cómo medimos la incertidumbre, el resultado y sus límites.
          Todo corre con <code>python src/pipeline.py</code> con semillas fijas, y cada cifra sale de <code>outputs/</code>. El orden es el del trabajo: validar antes de modelar.
        </p>
      </header>

      <nav className="md-indice" aria-label="Componentes">
        {B.map((b) => <a key={b.id} href={`#${b.id}`}><span>{b.n}</span>{b.titulo}</a>)}
      </nav>

      <section className="md-lista">{B.map((b) => <Modelo key={b.id} b={b} />)}</section>

      <section className="tarjeta md-decide">
        <h2>Por qué estas decisiones</h2>
        <p>Con 19 localidades los errores agrupados analíticos son optimistas: por eso los IC de los AME salen de un bootstrap de conglomerados y la prueba clave del delito registrado usa wild cluster bootstrap.
          Las calificaciones del entorno comparten batería con la pregunta de seguridad y pueden inflarse por el juicio general de la persona: el modelo principal usa solo hechos de otras preguntas.
          Los modelos flexibles sirven para comprobar que la conclusión no depende de la forma funcional del logit. Y cuando dos índices comparten un componente, se controla antes de interpretar su correlación.</p>
        <div className="md-enlaces">
          <Link className="boton" href="/presentar#hipotesis">Ver el marcador de las 8 hipótesis →</Link>
          <Link className="boton sec" href="/metodologia">Fuentes y método →</Link>
          <a className="boton sec" href="/entregables/Informe_tecnico_El_miedo_que_no_baja.pdf">Informe técnico (PDF) →</a>
        </div>
      </section>
    </div>
  );
}
