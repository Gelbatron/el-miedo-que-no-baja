import { EnSimple } from "@/components/EnSimple";
import { D, fmt, pval } from "@/lib/datos";
import { COLOR_SEMAFORO, F } from "@/lib/frentes";
import { HURTO } from "@/lib/historia";

export const metadata = { title: "Método · El miedo que no baja" };

const AUDITORIA = [
  ["Delito ocurrido por barrio y mes", "Delitos de alto impacto por localidad, ene-ago 2018-2026 (SCJ), validados con el SIEDCO de la Policía y Medicina Legal", "Localidad, corte ene-ago", "Registro = denuncias; los hurtos de la capa solo son comparables desde 2023 (antes valen 2 a 3 veces el SIEDCO)"],
  ["Victimización y denuncia en el tiempo", "Encuesta de Convivencia (DANE) y Encuesta de Percepción y Victimización (Cámara de Comercio)", "Bogotá; CCB por localidad", "DANE sin 2022 ni 2024-2026; CCB sin errores publicados por indicador"],
  ["Violencia contra las mujeres", "SIVIM (Secretaría de Salud) 2013-2026 y encuesta de acoso callejero 2025 (Veeduría)", "UPZ y localidad; persona", "SIVIM cuenta casos notificados; la de acoso es un formulario en línea"],
  ["Percepción de seguridad por UPL, frecuente", "Bienal de Cultura Ciudadana 2025, microdatos ponderados", "Persona; representativa por localidad", "Un solo año; la EDP (bimestral, por UPL) es la fuente de seguimiento propuesta"],
  ["Victimización por localidad", "EMV ola 8 (2024), 96 encuestas por localidad", "Persona; localidad recuperada del tablero oficial", "Intervalos amplios (±10 pp); factor nacional"],
  ["Estado real del alumbrado por cuadra", "Luminarias por localidad, UAESP agosto 2019", "Localidad, 2019", "Desactualizado y agregado: no permite validar el efecto"],
  ["Desorden en el espacio público", "Llamadas 123 por narcóticos, riñas y maltrato (SCJ)", "Localidad y UPZ, ene-ago", "Mide llamadas, no hechos; depende de que la gente llame"],
  ["Calidad del entorno inmediato", "Hechos reportados por la persona (Bienal): atracos y drogas en el parque, conflictos vecinales", "Persona", "Autorreporte; se separa de las calificaciones de la misma batería"],
  ["Población para tasas", "Proyecciones SDP 2005-2035 por sexo y edad", "Localidad y UPZ", "Proyecciones, no conteos"],
];

export default function Metodologia() {
  return (
    <div className="contenedor pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Trazabilidad: problema → datos → método → resultados → recomendaciones</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Cómo se hizo</h1>
        <EnSimple>Cómo lo hicimos, paso a paso: qué fuentes usamos, cómo las limpiamos y unimos, qué modelos corrimos y qué pruebas hicimos para no engañarnos.</EnSimple>
        <p className="bajada">{F.confiabilidad.length} fuentes públicas integradas por el código oficial de localidad, con la población de la SDP como denominador. Todo el proceso está en el notebook del repositorio y se puede repetir desde cero.</p>
      </header>

      <section className="tarjeta">
        <h2>Flujo de integración</h2>
        <Flujo />
      </section>

      <section className="tarjeta">
        <h2>Auditoría de datos: lo ideal frente a lo disponible</h2>
        <p className="nota">El paso 2 de la metodología DIPEA. Cada proxy está justificado y su limitación queda explícita.</p>
        <div className="tabla-wrap">
          <table>
            <thead><tr><th>Variable ideal</th><th>Lo que hay</th><th>Granularidad</th><th>Limitación y manejo</th></tr></thead>
            <tbody>{AUDITORIA.map((r) => <tr key={r[0]}>{r.map((c, i) => <td key={i}>{c}</td>)}</tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="tarjeta" style={{ borderLeft: "5px solid var(--rojo)" }}>
        <h2>Antes de modelar: validar cada serie</h2>
        <p style={{ color: "var(--tinta-2)" }}>
          Para cada delito y año (enero-agosto, Bogotá) dividimos los casos de la capa de la SCJ entre los del SIEDCO de la Policía, y los homicidios también entre los de Medicina Legal.
          Homicidios, lesiones, delitos sexuales y violencia intrafamiliar coinciden todos los años. El hurto a personas de 2018 a 2022 vale {fmt(HURTO.razonMin, 2)} a {fmt(HURTO.razonMax, 2)} veces lo de la Policía y desde 2023 coincide caso por caso:
          con la capa, el hurto «cae» {fmt(Math.abs(HURTO.capa2022a2026), 0)} % de 2022 a 2026; con la Policía, {fmt(Math.abs(HURTO.policia2022a2026), 0)} %. La encuesta del DANE confirma a la Policía.
          Desde 2023, además, las columnas «motocicletas» y «celulares» de la capa repiten caso por caso el hurto a comercio y el de motos del SIEDCO.
        </p>
        <div className="tabla-wrap">
          <table>
            <thead><tr><th>Serie</th><th>Estado</th><th>Qué se usa</th><th>Detalle</th></tr></thead>
            <tbody>{F.registro.estado.map((e) => (
              <tr key={e.codigo}><td>{e.tipo}</td><td>{{ validada: "Validada", quiebre: "Quiebre en 2023", sin_validar: "Sin serie externa", no_coincide: "No coincide con su nombre" }[e.estado] ?? e.estado}</td>
                <td>{e.fuente_bogota === "ninguna" ? "No se usa por tipo" : e.fuente_bogota === "SIEDCO" ? "SIEDCO (Bogotá); SCJ desde 2023 (localidades)" : "SCJ"}</td><td>{e.detalle}</td></tr>
            ))}</tbody>
          </table>
        </div>
      </section>

      <section className="tarjeta">
        <h2>Score de confiabilidad de las fuentes</h2>
        <p className="nota">Seis criterios de 0 a 1: años comparables (20 %), actualidad (15 %), precisión (20 %), detalle territorial (15 %), validez (15 %) y verificación externa (15 %). Alta ≥ 75, media 55-74, baja &lt; 55.</p>
        <div className="tabla-wrap">
          <table>
            <thead><tr><th>Fuente</th><th>Frente</th><th>Entidad</th><th className="n">Años comparables</th><th className="n">Último</th><th className="n">Score</th><th>Advertencia</th></tr></thead>
            <tbody>{F.confiabilidad.map((f) => (
              <tr key={f.fuente}><td>{f.fuente}</td><td>{f.frente}</td><td>{f.entidad}</td><td className="n">{f.anios}</td><td className="n">{f.ultimo}</td>
                <td className="n"><b style={{ color: COLOR_SEMAFORO[f.semaforo] }}>{fmt(f.score, 0)}</b></td><td>{f.advertencia}</td></tr>
            ))}</tbody>
          </table>
        </div>
      </section>

      <section className="rejilla r2">
        <div className="tarjeta">
          <h3>Escalera analítica</h3>
          <ol style={{ margin: 0, paddingLeft: "1.2em", display: "grid", gap: 8, color: "var(--tinta-2)" }}>
            <li><b style={{ color: "var(--tinta)" }}>Descriptivo:</b> series validadas 2018-2026, tasas por 100.000, porcentajes ponderados con error estándar; tendencias con binomial negativa de panel en la ventana comparable.</li>
            <li><b style={{ color: "var(--tinta)" }}>Diagnóstico:</b> logit ponderado con efectos marginales e IC por bootstrap de localidades; robustez con efectos fijos, modelo lineal y wild cluster bootstrap.</li>
            <li><b style={{ color: "var(--tinta)" }}>Predictivo:</b> AUC fuera de muestra por bloques de variables (validación cruzada repetida); bosque aleatorio y gradient boosting con importancia por bloques; tipología no supervisada (componentes principales y Ward).</li>
            <li><b style={{ color: "var(--tinta)" }}>Prescriptivo:</b> Índice de Brecha con incertidumbre, priorización y simulación de escenarios.</li>
          </ol>
        </div>
        <div className="tarjeta">
          <h3>Validaciones territoriales (19 localidades)</h3>
          <div className="tabla-wrap">
            <table>
              <thead><tr><th>Prueba</th><th className="n">ρ</th><th className="n">p ajustado (BH)</th></tr></thead>
              <tbody>{D.validaciones.map((v) => <tr key={v.prueba}><td>{v.prueba}</td><td className="n">{fmt(v.rho, 2)}</td><td className="n">{fmt(v.p_bh, 3)}</td></tr>)}</tbody>
            </table>
          </div>
          <p className="nota">Seis de siete pruebas son nulas: los registros administrativos no reflejan la percepción ni la victimización. La única que sobrevive (Índice de Brecha frente a cifra oculta, {pval(D.validaciones.at(-1)!.p)}) es el hallazgo central.</p>
        </div>
      </section>

      <section className="tarjeta">
        <h2>Limitaciones</h2>
        <ul style={{ margin: 0, paddingLeft: "1.2em", display: "grid", gap: 8, color: "var(--tinta-2)" }}>
          <li>Asociación, no causalidad: los modelos controlan perfil y territorio, pero no hay asignación aleatoria. El simulador es una sensibilidad del modelo.</li>
          <li>Las calificaciones de alumbrado y ventas informales comparten batería con la seguridad de la zona (sesgo de método común). Por eso el modelo principal usa solo hechos.</li>
          <li>Personas y hechos no son la misma unidad: la cifra oculta es un orden de magnitud. La EMV tiene 96 encuestas por localidad y un factor de ponderación nacional.</li>
          <li>La localidad de la EMV no viene en el archivo publicado; se recuperó del tablero oficial de Datos para la Transparencia y se verificó el cruce registro a registro.</li>
          <li>El delito solo se publica por localidad. La Encuesta Distrital de Percepción 2025 no se pudo descargar en forma automatizada; es la fuente propuesta para el seguimiento por UPL.</li>
          <li>Sumapaz (rural) se excluye. Los mapas muestran la huella urbana de cada localidad.</li>
        </ul>
      </section>
    </div>
  );
}

function Flujo() {
  const cajas = [
    { x: 10, y: 10, t: "SCJ · delitos e incidentes 123", c: "registro" }, { x: 10, y: 70, t: "SDP · población 2005-2035", c: "registro" },
    { x: 10, y: 130, t: "UAESP · alumbrado / DADEP · espacio público", c: "registro" }, { x: 10, y: 190, t: "IDECA · límites", c: "registro" },
    { x: 10, y: 250, t: "Bienal 2025 · 5.538 adultos", c: "percepcion" }, { x: 10, y: 310, t: "EMV 2024 · 1.824 en Bogotá", c: "percepcion" },
  ];
  return (
    <div style={{ overflowX: "auto" }}>
      <svg viewBox="0 0 920 370" className="g" style={{ minWidth: 700 }} role="img" aria-label="Flujo de integración de fuentes">
        {cajas.map((b) => (
          <g key={b.t}>
            <rect x={b.x} y={b.y} width={300} height={44} rx={10} fill="var(--superficie-2)" stroke={`var(--${b.c})`} strokeWidth={2} />
            <text x={b.x + 14} y={b.y + 27} className="etq">{b.t}</text>
            <path d={`M${b.x + 300},${b.y + 22} C 360,${b.y + 22} 360,185 400,185`} fill="none" stroke="var(--linea)" strokeWidth={2} />
          </g>
        ))}
        <rect x={400} y={140} width={210} height={90} rx={12} fill="var(--tinta)" />
        <text x={505} y={176} textAnchor="middle" style={{ fill: "var(--fondo)", fontWeight: 650, fontSize: 14 }}>Llave territorial</text>
        <text x={505} y={198} textAnchor="middle" style={{ fill: "var(--fondo)", fontSize: 12 }}>código de localidad 1-19</text>
        <text x={505} y={216} textAnchor="middle" style={{ fill: "var(--fondo)", fontSize: 12 }}>+ tasas por 100.000</text>
        {[["Panel por localidad", 60], ["Microdatos + contexto", 160], ["Modelos y validaciones", 260]].map(([t, y]) => (
          <g key={t as string}>
            <path d={`M610,185 C 650,185 650,${Number(y) + 22} 690,${Number(y) + 22}`} fill="none" stroke="var(--linea)" strokeWidth={2} />
            <rect x={690} y={Number(y)} width={220} height={44} rx={10} fill="var(--superficie)" stroke="var(--tinta-3)" />
            <text x={704} y={Number(y) + 27} className="etq">{t}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}
