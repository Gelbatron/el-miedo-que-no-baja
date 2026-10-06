import { D, R, fmt } from "@/lib/datos";

export const metadata = { title: "Indicador · El miedo que no baja" };

export default function Indicador() {
  const ibs = D.ibs as Record<string, number & string>[];
  const panel = Object.fromEntries((D.panel as Record<string, number & string>[]).map((p) => [p.localidad, p]));
  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Regla 10.II · indicador medible, comparable y consistente</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Índice de Brecha de Seguridad</h1>
        <p className="bajada">Un indicador que el Distrito puede calcular cada semestre con fuentes que ya produce, para saber dónde la gente se siente más insegura de lo que el registro oficial explica.</p>
      </header>

      <section className="rejilla r2">
        <div className="tarjeta">
          <h3>Ficha técnica</h3>
          <dl style={{ display: "grid", gridTemplateColumns: "minmax(130px,max-content) 1fr", gap: "10px 18px", margin: 0, fontSize: ".94rem" }}>
            {([
              ["Nombre", "Índice de Brecha de Seguridad (IBS)"],
              ["Objetivo", "Identificar territorios donde la inseguridad percibida supera lo que explica el delito registrado, para priorizar intervenciones de entorno y mejorar el registro."],
              ["Fórmula", "IBS = z(% de adultos que califican mala o muy mala la seguridad de su zona) − z(ln de delitos de alto impacto por 100.000 hab.). z = estandarización entre localidades del mismo periodo."],
              ["Unidad", "Desviaciones estándar. Positivo: más miedo que registro. Negativo: más registro que miedo."],
              ["Fuentes", "Percepción: Encuesta Distrital de Percepción (SDP) o Encuesta Bienal de Cultura Ciudadana (SCRD). Delitos: SCJ, Delitos de alto impacto. Población: SDP, proyecciones 2005-2035."],
              ["Periodicidad", "Semestral por sector de UPL y anual por localidad y UPL, según la representatividad de la EDP. Bienal con la EBCC."],
              ["Desagregación", "Localidad, UPL, sexo, grupo de edad y estrato (la percepción se puede desagregar; el delito, por territorio)."],
              ["Línea base", `2025: ${fmt(R.zona_insegura_pct)} % de adultos califica mala la seguridad de su zona; ${fmt(R.ciudad_insegura_pct)} % califica a Bogotá como insegura. IBS por localidad en la tabla.`],
              ["Indicadores acompañantes", "Víctimas por delito registrado (cifra oculta, EMV/EDP y SCJ); % de mujeres que evita salir de noche (EMV/EDP)."],
              ["Meta sugerida", `Reducir a menos de +1 el IBS de las cinco localidades priorizadas (${R.ibs_top5.join(", ")}) y bajar la cifra oculta en la periferia.`],
              ["Limitaciones", "Delito registrado = denuncias (subregistro). En el centro la tasa por residente se infla por población flotante. La percepción tiene error muestral (ver intervalos)."],
            ] as const).map(([k, v]) => (
              <div key={k} style={{ display: "contents" }}>
                <dt className="antetitulo" style={{ paddingTop: 3 }}>{k}</dt>
                <dd style={{ margin: 0, color: "var(--tinta-2)" }}>{v}</dd>
              </div>
            ))}
          </dl>
        </div>
        <div className="tarjeta">
          <h3>Línea base 2025 por localidad</h3>
          <div className="tabla-wrap" style={{ maxHeight: 620 }}>
            <table>
              <thead><tr><th className="n">#</th><th>Localidad</th><th className="n">IBS</th><th className="n">Intervalo 90 %</th><th className="n">Zona insegura</th><th className="n">Delitos /100.000</th></tr></thead>
              <tbody>
                {ibs.map((f) => (
                  <tr key={f.localidad}>
                    <td className="n">{f.puesto}</td><td>{f.nombre}</td>
                    <td className="n" style={{ color: Number(f.ibs) > 0 ? "var(--percepcion-texto)" : "var(--registro-texto)", fontWeight: 600 }}>{fmt(Number(f.ibs), 2)}</td>
                    <td className="n">{fmt(Number(f.ibs_p05), 2)} a {fmt(Number(f.ibs_p95), 2)}</td>
                    <td className="n">{fmt(Number(panel[f.localidad].zona_insegura))} %</td>
                    <td className="n">{fmt(Number(panel[f.localidad].delitos_alto_impacto_100k), 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="nota">Delitos de alto impacto sin lesiones personales (no publicadas para 2026), enero a agosto de 2025.</p>
        </div>
      </section>
    </div>
  );
}
