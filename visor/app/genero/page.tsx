import { EnSimple } from "@/components/EnSimple";
import { BANDA_PANDEMIA } from "@/lib/historia";
import { D, R, fmt, signo } from "@/lib/datos";
import { Forest, LeyendaSexo, Lineas, Mancuerna } from "@/components/Graficos";

export const metadata = { title: "Género · El miedo que no baja" };

export default function Genero() {
  const s = R.emv_por_sexo;
  const mujer = (filas: typeof D.ame.m_hechos, etiqueta: string) => ({ ...filas.find((f) => f.variable === "mujer")!, etiqueta });
  const efectos = [
    mujer(D.emv_genero.teme_acoso_sexual, "Teme mucho o bastante el acoso sexual (EMV)"),
    mujer(D.emv_genero.barrio_inseguro, "Se siente insegura en su barrio (EMV)"),
    mujer(D.emv_genero.no_sale_noche, "Evita salir de noche (EMV)"),
    mujer(D.ame.m_miedo, "Siente miedo en el espacio público (Bienal)"),
    mujer(D.ame.m_ciudad, "Califica a Bogotá como insegura (Bienal)"),
    mujer(D.ame.m_hechos, "Califica mala la seguridad de su zona (Bienal)"),
  ];
  const serie = (cod: string) => D.serie_delitos.filter((f) => f.codigo === cod).sort((a, b) => a.anio - b.anio);
  const indice = (cod: string, nombre: string, color: string) => {
    const f = serie(cod), base = f[0].casos;
    return { nombre, color, puntos: f.map((p) => ({ x: p.anio, y: (p.casos / base) * 100, tip: `<b>${nombre}</b> · ${p.anio}<br>${fmt(p.casos, 0)} casos (ene-ago)` })) };
  };
  return (
    <div className="contenedor pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Enfoque de género · EMV 2024 y Bienal 2025</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Las mujeres reportan menos delitos y recortan más su vida</h1>
        <EnSimple>{`Las mujeres dicen haber sido víctimas menos que los hombres (${fmt(R.emv_por_sexo.victima.mujeres)} % frente a ${fmt(R.emv_por_sexo.victima.hombres)} %), pero tienen mucho más miedo al acoso y evitan más salir de noche. Comparando iguales, ser mujer suma ${fmt(R.emv_mujer_ame.teme_acoso_sexual.ame_pp, 0)} puntos de temor al acoso sexual. El miedo les cuesta libertad.`}</EnSimple>
        <p className="bajada">
          El {fmt(s.victima.mujeres)} % de las mujeres y el {fmt(s.victima.hombres)} % de los hombres dicen haber sido víctimas de un delito en el último año.
          Aun así, ellas evitan más salir de noche y temen más el acoso sexual. El costo de la inseguridad no se mide solo en delitos: se mide en autonomía.
        </p>
      </header>

      <section className="rejilla">
        <div className="tarjeta">
          <h3>Mujeres frente a hombres en Bogotá</h3>
          <LeyendaSexo />
          <Mancuerna filas={[
            { etiqueta: "Teme mucho o bastante el acoso sexual", ...s.teme_acoso_sexual },
            { etiqueta: "Evita salir de noche", ...s.no_sale_noche },
            { etiqueta: "Se siente insegura/o en su barrio", ...s.barrio_inseguro },
            { etiqueta: "Fue víctima de un delito (último año)", ...s.victima },
          ]} />
          <p className="nota">Encuesta Mundial de Valores, ola 8 (2024), {fmt(R.n_emv_bogota, 0)} casos en Bogotá, ponderados con su factor.</p>
        </div>
        <div className="tarjeta">
          <h3>Diferencia por ser mujer, a igual edad, estrato y victimización</h3>
          <p className="nota">Efecto marginal promedio (pp) e intervalo del 95 % por bootstrap de localidades. EMV controla además haber sido víctima; la Bienal controla entorno y delito registrado.</p>
          <Forest filas={efectos} min={-8} max={26} />
        </div>
      </section>

      <section className="tarjeta">
        <h2>Mientras el hurto casi no se mueve, las violencias de género suben</h2>
        <p className="nota">Casos registrados por la SCJ entre enero y agosto de cada año, índice 2018 = 100.</p>
        <div className="leyenda">
          <span><i style={{ background: "var(--registro)" }} />Hurto a personas</span>
          <span><i style={{ background: "var(--mujeres)" }} />Violencia intrafamiliar</span>
          <span><i style={{ background: "var(--percepcion)" }} />Delitos sexuales</span>
        </div>
        <Lineas base={100} ymax={200} bandas={[BANDA_PANDEMIA]} series={[indice("HP", "Hurto a personas", "var(--registro)"), indice("VI", "Violencia intrafamiliar", "var(--mujeres)"), indice("DS", "Delitos sexuales", "var(--vino)")]} />
        <p style={{ color: "var(--tinta-2)" }}>
          Violencia intrafamiliar {signo(R.vif_cambio_pct_2018_2026)} % y delitos sexuales {signo(R.delitos_sexuales_cambio_pct_2018_2026)} % entre 2018 y 2026.
          Ocurren sobre todo en la casa y en el entorno cercano, donde el alumbrado y los parques no llegan: por eso la recomendación de género va más allá del espacio público.
        </p>
      </section>
    </div>
  );
}
