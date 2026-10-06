import { D, R, fmt, pval } from "@/lib/datos";
import { Dispersion, Forest } from "@/components/Graficos";
import { MapaIndice } from "@/components/MapaIndice";

export const metadata = { title: "La brecha · El miedo que no baja" };

export default function Brecha() {
  const ibs = D.ibs as Record<string, number & string>[];
  const co = Object.fromEntries((D.cifra_oculta as Record<string, number>[]).map((c) => [c.localidad, c]));
  const v = R.ibs_vs_cifra_oculta;
  const filasIbs = ibs.map((f) => ({
    etiqueta: String(f.nombre), ame_pp: Number(f.ibs), ic_inf: Number(f.ibs_p05), ic_sup: Number(f.ibs_p95), p: 0,
    tip: `<b>${f.nombre}</b><br>Índice ${fmt(Number(f.ibs), 2)} (90 %: ${fmt(Number(f.ibs_p05), 2)} a ${fmt(Number(f.ibs_p95), 2)})<br>Puesto ${f.puesto}; probabilidad de estar en el top 5: ${fmt(Number(f.prob_top5) * 100, 0)} %`,
  }));
  const disp1 = (D.panel as Record<string, number & string>[]).map((p) => ({
    id: Number(p.localidad), nombre: String(p.nombre), x: Number(p.delitos_alto_impacto_100k), y: Number(p.zona_insegura),
    tip: `<b>${p.nombre}</b><br>Zona insegura: ${fmt(Number(p.zona_insegura))} %<br>Delitos: ${fmt(Number(p.delitos_alto_impacto_100k), 0)} por 100.000`,
  }));
  const disp2 = ibs.map((f) => ({
    id: Number(f.localidad), nombre: String(f.nombre), x: Number(co[f.localidad].razon), y: Number(f.ibs),
    tip: `<b>${f.nombre}</b><br>Índice de Brecha: ${fmt(Number(f.ibs), 2)}<br>Víctimas por delito registrado: ${fmt(Number(co[f.localidad].razon))}`,
  }));
  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Índice de Brecha de Seguridad · cifra oculta</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Donde hay más miedo que delito, el delito no se está registrando</h1>
        <p className="bajada">
          El índice compara, en desviaciones estándar, el porcentaje que siente insegura su zona con el logaritmo de los delitos de alto impacto
          registrados por 100.000 habitantes. Positivo: más miedo del que explica el registro. Negativo: más registro que miedo entre quienes viven ahí.
        </p>
      </header>

      <section className="rejilla r2">
        <div className="tarjeta">
          <h3>Índice de Brecha por localidad, con intervalo del 90 %</h3>
          <p className="nota">Intervalo por bootstrap ponderado de la Bienal (1.000 réplicas). Las cinco primeras quedan en el top 5 en más del 90 % de las réplicas.</p>
          <Forest filas={filasIbs} unidad="" dec={2} min={-3} max={3.2} paso={1} ancho={460} />
        </div>
        <div className="tarjeta">
          <h3>Mapa del índice</h3>
          <MapaIndice />
          <p className="nota">Ámbar: más miedo que delito registrado. Azul: más delito registrado que miedo. En el centro (La Candelaria, Los Mártires, Santa Fe) la tasa por residente se infla con la población flotante.</p>
        </div>
      </section>

      <section className="tarjeta">
        <h2>La prueba: la brecha va donde va el subregistro</h2>
        <p className="bajada" style={{ fontSize: "1rem" }}>
          Cruzamos el índice con la cifra oculta: adultos que dicen haber sido víctimas en el último año (EMV 2024) por cada delito de alto impacto
          que registró la SCJ en 2024. Spearman <b>ρ = {fmt(v.rho, 2)}</b> (IC 95 % {fmt(v.ic_inf, 2)} a {fmt(v.ic_sup, 2)}; {pval(v.p)}; ajustado por siete
          pruebas con Benjamini-Hochberg, p = {fmt(v.p_bh, 3)}). Es la única relación territorial que sobrevive a la corrección.
        </p>
        <Dispersion puntos={disp2} ejeX="Víctimas estimadas por cada delito registrado (EMV 2024 / SCJ 2024)" ejeY="Índice de Brecha (z)"
          colorDe={(p) => (p.y > 0 ? "var(--percepcion)" : "var(--registro)")} />
        <p className="nota">
          Lectura: en Bosa, Kennedy y San Cristóbal hay unas 9 a 11 víctimas por cada delito registrado; en Los Mártires y La Candelaria, cerca de 1.
          Parte del miedo &ldquo;sobrante&rdquo; de la periferia es delito real que no llega a los registros. Advertencia: personas y hechos no son la misma unidad;
          la razón es un orden de magnitud, con intervalo por la muestra de la EMV (96 encuestas por localidad).
        </p>
      </section>

      <section className="rejilla">
        <div className="tarjeta">
          <h3>Percepción frente a delito registrado</h3>
          <p className="nota">Escala logarítmica en el eje horizontal. Sin relación entre localidades: ρ = {fmt(D.validaciones.find((x) => x.prueba.startsWith("Zona insegura (Bienal) vs delitos"))?.rho ?? 0, 2)}.</p>
          <Dispersion puntos={disp1} logX ejeX="Delitos de alto impacto por 100.000 hab. (SCJ, ene-ago 2025)" ejeY="% que califica mala la seguridad de su zona" alto={400}
            colorDe={() => "var(--registro)"} />
        </div>
        <div className="tarjeta">
          <h3>Cifra oculta por localidad</h3>
          <div className="tabla-wrap" style={{ maxHeight: 440 }}>
            <table>
              <thead><tr><th>Localidad</th><th className="n">Víctimas (EMV)</th><th className="n">Delitos SCJ</th><th className="n">Razón</th><th className="n">IC 95 %</th></tr></thead>
              <tbody>
                {[...(D.cifra_oculta as Record<string, number & string>[])].sort((a, b) => Number(b.razon) - Number(a.razon)).map((c) => (
                  <tr key={c.localidad}>
                    <td>{c.nombre}</td>
                    <td className="n">{fmt(Number(c.victimas_estimadas), 0)}</td>
                    <td className="n">{fmt(Number(c.delitos_registrados), 0)}</td>
                    <td className="n"><b>{fmt(Number(c.razon))}</b></td>
                    <td className="n">{fmt(Number(c.razon_inf))}–{fmt(Number(c.razon_sup))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="nota">Delitos de 2024 (ene-ago llevados a 12 meses). Bogotá: {fmt(R.cifra_oculta_bogota)} víctimas por delito registrado. Población adulta: SDP.</p>
          <p className="nota">Espacio público efectivo por localidad (DADEP) y percepción: sin relación (ver Método). Panel completo en Datos.</p>
        </div>
      </section>
    </div>
  );
}
