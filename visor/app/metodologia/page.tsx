import { D, fmt, pval } from "@/lib/datos";

export const metadata = { title: "Método · El miedo que no baja" };

const AUDITORIA = [
  ["Delito ocurrido por barrio y mes", "Delitos de alto impacto por localidad, ene-ago 2018-2026 (SCJ)", "Localidad, corte ene-ago", "Registro = denuncias; se cruza con victimización EMV (cifra oculta)"],
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
        <p className="bajada">Siete fuentes públicas integradas por el código oficial de localidad, con la población de la SDP como denominador. Todo el proceso está en el notebook del repositorio y se puede repetir desde cero.</p>
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

      <section className="rejilla r2">
        <div className="tarjeta">
          <h3>Escalera analítica</h3>
          <ol style={{ margin: 0, paddingLeft: "1.2em", display: "grid", gap: 8, color: "var(--tinta-2)" }}>
            <li><b style={{ color: "var(--tinta)" }}>Descriptivo:</b> series 2018-2026, tasas por 100.000, porcentajes ponderados con error estándar.</li>
            <li><b style={{ color: "var(--tinta)" }}>Diagnóstico:</b> logit ponderado con efectos marginales e IC por bootstrap de localidades; robustez con efectos fijos, modelo lineal y wild cluster bootstrap.</li>
            <li><b style={{ color: "var(--tinta)" }}>Predictivo:</b> AUC fuera de muestra por bloques de variables (validación cruzada repetida).</li>
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
