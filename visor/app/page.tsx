import Link from "next/link";
import type { ReactNode } from "react";
import { D, R, fmt, signo } from "@/lib/datos";
import { BANDA_PANDEMIA, PANDEMIA, enLista } from "@/lib/historia";
import { MapaDoble } from "@/components/MapaDoble";
import { Icono } from "@/components/Iconos";
import { Lineas } from "@/components/Graficos";

export default function Historia() {
  const a = R.ame_hechos, w = R.emv_mujer_ame;
  const top5 = new Set((D.ibs as Record<string, number>[]).slice(0, 5).map((f) => Number(f.localidad)));
  const { ancho, alto } = D.geo;
  const porCien = 100 / R.cifra_oculta_bogota;
  const bosa = (D.cifra_oculta as unknown as { localidad: number; razon: number }[]).find((f) => f.localidad === 7)!;
  const esc = D.escenarios.find((e) => e.grupo === "total" && e.localidad === 0)!;
  const menos50 = esc.p00 - (esc.p00 + esc.p10 + esc.p01 + esc.p11) / 4;
  const indice = (cod: string, nombre: string, color: string) => {
    const f = D.serie_delitos.filter((x) => x.codigo === cod).sort((p, q) => p.anio - q.anio);
    return { nombre, color, puntos: f.map((p) => ({ x: p.anio, y: (p.casos / f[0].casos) * 100, tip: `<b>${nombre}</b> · ${p.anio}<br>${fmt(p.casos, 0)} casos (ene-ago)` })) };
  };
  return (
    <>
      <section className="heroe">
        <div className="contenedor heroe-int">
          <div style={{ display: "grid", gap: 18 }}>
            <p className="antetitulo">Bogotá DataJam Edición 5 · Seguridad ciudadana con enfoque de género</p>
            <h1>El miedo <em>que no baja</em></h1>
            <div className="heroe-raya" />
            <p className="bajada">
              Revisamos los datos de la Secretaría de Seguridad: el hurto viene bajando muchísimo. Pero los hechos violentos van al revés y la gente no lo siente.
              Esta es la historia de esa brecha, en cuatro pasos.
            </p>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <a className="boton blanco" href="#historia">Empezar la historia ↓</a>
              <Link className="boton sec" href="/presentar" style={{ color: "#fff", borderColor: "rgba(255,255,255,.7)" }}>▶ Ver la presentación</Link>
            </div>
          </div>
          <figure style={{ margin: 0, display: "grid", gap: 8, justifyItems: "center" }}>
            <svg className="silueta" viewBox={`-4 -4 ${ancho + 8} ${alto + 8}`} role="img" aria-label="Bogotá urbana; en oro, las cinco localidades con mayor Índice de Brecha">
              {D.geo.localidades.map((l) => (
                <path key={l.id} d={l.d} className={top5.has(l.id) ? "brilla" : undefined} data-tip={`<b>${l.nombre}</b>${top5.has(l.id) ? "<br>Prioridad: top 5 del Índice de Brecha" : ""}`} />
              ))}
            </svg>
            <figcaption style={{ fontSize: ".8rem", color: "rgba(255,255,255,.85)" }}>En oro: las cinco localidades donde actuar primero</figcaption>
          </figure>
        </div>
      </section>

      <div className="contenedor">
        <section className="cifras-heroe">
          <Cifra etiqueta="El hurto baja muchísimo · SCJ" valor={`${signo(R.hurto_personas.cambio_pct, 0)} %`} tono="registro"
            texto={`hurto a personas registrado entre enero y agosto, de ${fmt(R.hurto_personas["2019"], 0)} casos en 2019 a ${fmt(R.hurto_personas["2026"], 0)} en 2026.`} />
          <Cifra etiqueta="Pero la gente no lo siente · Bienal 2025" valor={`${fmt(R.ciudad_insegura_pct, 0)} %`} tono="percepcion"
            texto="dice que Bogotá es insegura: 3 de cada 4 personas." />
          <Cifra etiqueta="Y mucho delito no se denuncia" valor={`${fmt(porCien, 0)} de 100`} tono="vino" compacto
            texto="víctimas tiene su delito en el registro oficial. Las otras no llegan a las cifras." />
        </section>
      </div>

      <section className="banda" id="historia">
        <div className="contenedor">
          <div className="titulo-seccion" style={{ marginBottom: 8 }}>
            <p className="antetitulo">La pregunta</p>
            <h2 style={{ color: "var(--tinta)", fontSize: "clamp(1.3rem,2.6vw,1.9rem)", maxWidth: 900 }}>
              ¿Por qué la inseguridad percibida no baja cuando el delito registrado sí, y en qué territorios debe intervenir primero el Distrito?
            </h2>
          </div>

          <Acto n={1} nombre="El problema" frase="En el papel, Bogotá mejora. La gente no lo siente.">
            <p className="relato">
              Resulta que estuvimos revisando los datos de la Secretaría de Seguridad y el hurto a personas viene bajando muchísimo: <b>{signo(R.hurto_personas.cambio_pct, 0)} % desde 2019</b>.
              Pero hay hechos violentos que van al revés: la <b>violencia intrafamiliar subió {fmt(R.vif_cambio_pct_2018_2026, 0)} %</b> y los <b>delitos sexuales {fmt(R.delitos_sexuales_cambio_pct_2018_2026, 0)} %</b> desde 2018.
              Y cuando lo cruzamos con las encuestas, <b>3 de cada 4 personas dicen que Bogotá es insegura</b>.
            </p>
            <div className="tarjeta">
              <div className="leyenda">
                <span><i style={{ background: "var(--registro)" }} />Hurto a personas</span>
                <span><i style={{ background: "var(--mujeres)" }} />Violencia intrafamiliar</span>
                <span><i style={{ background: "var(--vino)" }} />Delitos sexuales</span>
                <span className="nota">Casos registrados enero-agosto, índice 2018 = 100</span>
              </div>
              <Lineas base={100} ymax={200} bandas={[BANDA_PANDEMIA]} series={[indice("HP", "Hurto a personas", "var(--registro)"), indice("VI", "Violencia intrafamiliar", "var(--mujeres)"), indice("DS", "Delitos sexuales", "var(--vino)")]} />
            </div>
            <div className="ojo">
              <b className="t">Ojo con la pandemia</b>
              <p className="relato" style={{ fontSize: "1.02rem" }}>
                En 2020 el hurto cayó {fmt(-PANDEMIA.hurto2020, 0)} % por el encierro y en 2022 volvió casi a lo de antes ({fmt(PANDEMIA.hurto2022sobre2019, 0)} % de 2019).
                Pero desde 2022 siguió bajando: <b>{fmt(-PANDEMIA.hurto2022a2026, 0)} % menos</b>. O sea, no es solo la pandemia. Eso sí: en 2023 cayeron todos los tipos de hurto a la vez,
                entre {fmt(PANDEMIA.caida2023min, 0)} % y {fmt(PANDEMIA.caida2023max, 0)} % en un solo año. ¿Menos delito o menos denuncia? El registro solo no lo dice.
              </p>
            </div>
            <p className="relato">
              <b>Y mucho delito ni siquiera se denuncia.</b> Por cada 100 personas que dicen haber sido víctimas, el registro oficial tiene <b>{fmt(porCien, 0)} delitos</b>; en Bosa, {fmt(100 / bosa.razon, 0)}.
              Por eso el mapa de las denuncias no es el mapa del miedo:
            </p>
            <div className="tarjeta"><MapaDoble /></div>
            <p className="relato"><b>O sea, el Distrito está tomando decisiones con un mapa incompleto.</b></p>
            <Detalle enlaces={[["/tendencia", "Lo que se registra, año por año"], ["/mapa", "El mapa por indicador"]]} />
          </Acto>

          <Acto n={2} nombre="Lo que hicimos" frase="Juntamos lo que la gente siente con lo que el Estado registra.">
            <p className="relato">
              Juntamos siete fuentes públicas: dos encuestas para lo que la gente siente, la Secretaría de Seguridad para lo que el Estado registra, y población, parques y alumbrado.
              Con eso armamos un <b>índice que dice en qué localidades hay más miedo del que muestran las cifras</b>. Y lo comprobamos de varias formas para no engañarnos.
            </p>
            <div className="rejilla r3">
              <Paso n="1" titulo="Juntamos todo" texto={`Dos encuestas (${fmt(R.n_bienal, 0)} y ${fmt(R.n_emv_bogota, 0)} personas), los registros de la Secretaría de Seguridad 2018-2026 y datos de población, alumbrado y espacio público, unidos por localidad.`} />
              <Paso n="2" titulo="Armamos un índice" texto="Pusimos el miedo y el delito en la misma regla y los restamos: así se ve dónde sobra miedo frente a lo que se registra." />
              <Paso n="3" titulo="Lo comprobamos" texto={`Donde sobra miedo, más delito se queda sin denunciar (correlación de ${fmt(R.ibs_vs_cifra_oculta.rho, 2)}), y fue la única de siete relaciones que pasó la prueba contra el azar.`} />
            </div>
            <p className="relato">Donde hay más miedo del que muestran las cifras: <b>{enLista(R.ibs_top5)}</b>.</p>
            <Detalle enlaces={[["/brecha", "El índice y el delito que no se denuncia"], ["/metodologia", "Cómo lo hicimos, paso a paso"]]} />
          </Acto>

          <Acto n={3} nombre="Lo que encontramos" frase="El miedo sale del barrio, no de las estadísticas.">
            <p className="relato">
              Comparamos personas iguales en todo menos en una cosa. Lo que de verdad le da miedo a la gente no son las estadísticas de su localidad: <b>es lo que ve en su barrio</b>.
              Y con las mujeres es más fuerte: denuncian menos, pero tienen mucho más miedo al acoso y dejan de salir de noche.
            </p>
            <div className="rejilla r3">
              <Hallazgo valor={`${signo(a.parque_atracos.ame_pp, 0)} puntos`} color="var(--percepcion-texto)" titulo="si ve atracos en el parque cercano"
                texto={`Peleas entre vecinos: hasta ${signo(a.conflictos_vecinos.ame_pp, 0)}. Es la probabilidad de sentir insegura su zona.`} href="/que-explica" />
              <Hallazgo valor="≈ 0" color="var(--registro-texto)" titulo="por el hurto registrado en su localidad"
                texto="Las estadísticas de hurto no cambian el miedo. Lo repetimos 300 veces: el resultado cae a los dos lados del cero." href="/que-explica" />
              <Hallazgo valor={`${signo(w.teme_acoso_sexual.ame_pp, 0)} puntos`} color="var(--mujeres)" titulo="de temor al acoso sexual por ser mujer"
                texto={`A igual edad, estrato y victimización. Y ${signo(w.no_sale_noche.ame_pp, 1)} de evitar salir de noche. El miedo les cuesta libertad.`} href="/genero" />
            </div>
            <Detalle enlaces={[["/que-explica", "Qué le da miedo a la gente"], ["/genero", "Las mujeres"]]} />
          </Acto>

          <Acto n={4} nombre="Por qué importa" frase="Dónde actuar, qué arreglar y cómo saber si funciona.">
            <p className="relato">
              Le estamos diciendo al Distrito <b>dónde actuar primero</b>, <b>qué arreglar</b> y <b>cómo medir si de verdad la gente se siente más segura</b>, no solo si bajan las denuncias.
              Todo con datos que el Distrito ya tiene.
            </p>
            <div className="rejilla r3">
              <Accion icono="parque" titulo="Dónde actuar primero" texto={`${enLista(R.ibs_top5)}. La misma regla sirve para las 33 UPL.`} />
              <Accion icono="mujer" titulo="Qué arreglar" texto="Lo que la gente ve en su barrio: parques sin atracos, convivencia entre vecinos y alumbrado. Con las mujeres en el centro." />
              <Accion icono="encuesta" titulo="Cómo saber si funciona" texto="El Índice de Brecha cada semestre, encuestas de victimización y el % de mujeres que evita salir de noche." />
            </div>
            <div className="ojo">
              <b className="t">¿Cuánto cambiaría?</b>
              <p className="relato" style={{ fontSize: "1.02rem" }}>
                Si mejora el alumbrado en la mitad de las zonas y dejan de verse atracos en la mitad de los parques, el modelo estima que la inseguridad percibida bajaría {fmt(menos50)} puntos:
                del orden de <b>{fmt((menos50 / 100) * R.adultos_urbanos_bienal / 1000, 0)} mil personas</b> menos con miedo. Es una estimación, no una promesa.
              </p>
            </div>
            <Detalle enlaces={[["/simulador", "Pruébalo en el simulador"], ["/indicador", "La ficha del indicador"]]} />
          </Acto>
        </div>
      </section>

      <section className="banda gris">
        <div className="contenedor rejilla r4" style={{ textAlign: "center" }}>
          {[["7", "fuentes públicas integradas por localidad"], [fmt(R.n_bienal, 0), "adultos en la Bienal de Cultura Ciudadana 2025"],
            [fmt(R.n_emv_bogota, 0), "encuestas de la EMV 2024 en Bogotá"], ["2018-2026", "series de delitos con el mismo corte"]].map(([v, t]) => (
            <div key={t} style={{ display: "grid", gap: 4 }}>
              <b style={{ fontFamily: "var(--f-display)", fontWeight: 800, fontSize: "2rem", color: "var(--rojo)" }}>{v}</b>
              <span className="nota" style={{ fontSize: ".9rem" }}>{t}</span>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

function Acto({ n, nombre, frase, children }: { n: number; nombre: string; frase: string; children: ReactNode }) {
  return (
    <article className="acto" aria-labelledby={`acto-${n}`}>
      <div className="acto-cab">
        <span className="acto-num">{n}</span>
        <div>
          <p className="antetitulo">{nombre}</p>
          <h2 id={`acto-${n}`}>{frase}</h2>
        </div>
      </div>
      {children}
    </article>
  );
}

function Cifra({ etiqueta, valor, texto, tono, compacto = false }: { etiqueta: string; valor: string; texto: string; tono: "registro" | "percepcion" | "vino"; compacto?: boolean }) {
  const col = tono === "vino" ? "var(--vino)" : `var(--${tono}-texto)`;
  const borde = tono === "vino" ? "var(--vino)" : `var(--${tono})`;
  return (
    <div className="tarjeta" style={{ borderTop: `5px solid ${borde}` }}>
      <p className="antetitulo" style={{ color: col }}>{etiqueta}</p>
      <div className="cifra"><b style={{ color: col, ...(compacto ? { fontSize: "clamp(2rem, 4.2vw, 3rem)", whiteSpace: "nowrap" } : {}) }}>{valor}</b><span>{texto}</span></div>
    </div>
  );
}

function Paso({ n, titulo, texto }: { n: string; titulo: string; texto: string }) {
  return (
    <div className="tarjeta" style={{ gap: 8 }}>
      <span className="icono-circulo" style={{ width: 44, height: 44, fontFamily: "var(--f-display)", fontWeight: 800, color: "#1e1e1e" }}>{n}</span>
      <h3>{titulo}</h3>
      <p style={{ margin: 0, color: "var(--tinta-2)" }}>{texto}</p>
    </div>
  );
}

function Hallazgo({ valor, color, titulo, texto, href }: { valor: string; color: string; titulo: string; texto: string; href: string }) {
  return (
    <Link href={href} className="tarjeta" style={{ textDecoration: "none", color: "inherit", gap: 6, borderTop: `5px solid ${color}` }}>
      <b style={{ fontFamily: "var(--f-display)", fontWeight: 800, fontSize: "2.2rem", color, lineHeight: 1 }}>{valor}</b>
      <b>{titulo}</b>
      <p style={{ margin: 0, color: "var(--tinta-2)" }}>{texto}</p>
    </Link>
  );
}

function Accion({ icono, titulo, texto }: { icono: "encuesta" | "parque" | "mujer" | "datos"; titulo: string; texto: string }) {
  return (
    <div className="tarjeta" style={{ justifyItems: "center", textAlign: "center" }}>
      <span className="icono-circulo" style={{ width: 76, height: 76 }}><Icono nombre={icono} /></span>
      <h3>{titulo}</h3>
      <p className="nota" style={{ fontSize: ".95rem", color: "var(--tinta-2)" }}>{texto}</p>
    </div>
  );
}

function Detalle({ enlaces }: { enlaces: [string, string][] }) {
  return (
    <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
      {enlaces.map(([href, txt], k) => <Link key={href} className={`boton${k ? " sec" : ""}`} href={href}>{txt} →</Link>)}
    </div>
  );
}
