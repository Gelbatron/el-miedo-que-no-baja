import Link from "next/link";
import type { ReactNode } from "react";
import { D, R, fmt, signo } from "@/lib/datos";
import { BANDA_PANDEMIA, HURTO, PANDEMIA, enLista } from "@/lib/historia";
import { F } from "@/lib/frentes";
import { MapaDoble } from "@/components/MapaDoble";
import { Icono } from "@/components/Iconos";
import { Lineas } from "@/components/Graficos";

export default function Historia() {
  const a = R.ame_hechos, w = R.emv_mujer_ame;
  const top5 = new Set((D.ibs as Record<string, number>[]).slice(0, 5).map((f) => Number(f.localidad)));
  const { ancho, alto } = D.geo;
  const porDiez = 10 / R.cifra_oculta_bogota;
  const bosa = (D.cifra_oculta as unknown as { localidad: number; razon: number }[]).find((f) => f.localidad === 7)!;
  const esc = D.escenarios.find((e) => e.grupo === "total" && e.localidad === 0)!;
  const menos50 = esc.p00 - (esc.p00 + esc.p10 + esc.p01 + esc.p11) / 4;
  const indice = (cod: string, nombre: string, color: string, capa = false) => {
    const f = D.serie_delitos.filter((x) => x.codigo === cod).sort((p, q) => p.anio - q.anio);
    const v = (p: (typeof f)[number]) => (capa ? p.casos_capa_scj ?? p.casos : p.casos);
    return { nombre, color, punteada: capa, puntos: f.map((p) => ({ x: p.anio, y: (v(p) / v(f[0])) * 100, tip: `<b>${nombre}</b> · ${p.anio}<br>${fmt(v(p), 0)} casos (ene-ago)` })) };
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
              La capa abierta de la Secretaría de Seguridad dice que el hurto cayó {fmt(Math.abs(HURTO.capa2022a2026), 0)} % desde 2022. El registro de la Policía dice {fmt(Math.abs(HURTO.policia2022a2026), 0)} %.
              La violencia sube y 3 de cada 4 personas sienten insegura la ciudad. Esta es la historia de por qué el miedo no baja, en cuatro pasos.
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
          <Cifra etiqueta="El hurto, según la Policía" valor={`${signo(HURTO.policia2022a2026, 0)} %`} tono="registro"
            texto={`desde 2022, enero a agosto (${fmt(HURTO.policia2022, 0)} → ${fmt(HURTO.policia2026, 0)} casos). La capa abierta de la SCJ dice ${signo(HURTO.capa2022a2026, 0)} %: tiene un quiebre en 2023.`} />
          <Cifra etiqueta="Y la gente lo siente · Bienal 2025" valor={`${fmt(R.ciudad_insegura_pct, 0)} %`} tono="percepcion"
            texto="dice que Bogotá es insegura: 3 de cada 4 personas." />
          <Cifra etiqueta="Y mucho delito no se denuncia" valor={`${fmt(porDiez, 1)} de 10`} tono="vino" compacto
            texto="víctimas tiene su delito en el registro oficial. Las demás no llegan a las cifras." />
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

          <Acto n={1} nombre="El problema" frase="En el papel, Bogotá mejora. ¿De verdad?">
            <p className="relato">
              La capa abierta de la Secretaría de Seguridad dice que el hurto a personas cayó <b>{fmt(Math.abs(HURTO.capa2019a2026), 0)} % desde 2019</b>. Pero el registro de la Policía,
              el mismo hurto y los mismos meses, dice <b>{signo(HURTO.policia2019a2026, 0)} %</b>: hasta 2022 la capa contaba más del doble, y desde 2023 coinciden caso por caso.
              Mientras tanto, la <b>violencia intrafamiliar subió {fmt(R.vif_cambio_pct_2018_2026, 0)} %</b> y los <b>delitos sexuales {fmt(R.delitos_sexuales_cambio_pct_2018_2026, 0)} %</b> desde 2018.
              Y <b>3 de cada 4 personas dicen que Bogotá es insegura</b>. El miedo no contradice los datos.
            </p>
            <div className="tarjeta">
              <div className="leyenda">
                <span><i style={{ background: "var(--registro)" }} />Hurto a personas, Policía</span>
                <span><i style={{ background: "var(--tinta-3)" }} />Hurto, capa abierta SCJ (punteada)</span>
                <span><i style={{ background: "var(--mujeres)" }} />Violencia intrafamiliar</span>
                <span><i style={{ background: "var(--vino)" }} />Delitos sexuales</span>
                <span className="nota">Casos registrados enero-agosto, índice 2018 = 100</span>
              </div>
              <Lineas base={100} ymax={200} bandas={[BANDA_PANDEMIA]} series={[indice("HP", "Hurto, Policía", "var(--registro)"), indice("HP", "Hurto, capa SCJ", "var(--tinta-3)", true), indice("VI", "Violencia intrafamiliar", "var(--mujeres)"), indice("DS", "Delitos sexuales", "var(--vino)")]} />
            </div>
            <div className="ojo">
              <b className="t">Ojo con la pandemia y con la serie</b>
              <p className="relato" style={{ fontSize: "1.02rem" }}>
                Con la serie de la Policía, en 2020 el hurto cayó {fmt(-PANDEMIA.hurto2020, 0)} % por el encierro y en 2022 volvió al {fmt(PANDEMIA.hurto2022sobre2019, 0)} % de 2019.
                En 2023 <b>subió {fmt(PANDEMIA.hurto2023, 0)} %</b>, y en 2026 está {fmt(Math.abs(PANDEMIA.hurto2022a2026), 0)} % por debajo de 2022. La capa abierta muestra lo contrario en 2023
                porque ese año cambia de escala. Lo comprobamos con la Policía, con Medicina Legal y con la encuesta del DANE: la denuncia no cayó, subió.
              </p>
            </div>
            <p className="relato">
              <b>Y mucho delito ni siquiera se denuncia.</b> De cada 10 personas que dicen haber sido víctimas, el registro oficial tiene <b>{fmt(porDiez, 1)} delitos</b>; en Bosa, {fmt(10 / bosa.razon, 1)}.
              Por eso el mapa de las denuncias no es el mapa del miedo:
            </p>
            <div className="tarjeta"><MapaDoble /></div>
            <p className="relato"><b>O sea, el Distrito está tomando decisiones con un mapa incompleto.</b></p>
            <Detalle enlaces={[["/tendencia", "Lo que se registra, año por año"], ["/mapa", "El mapa por indicador"]]} />
          </Acto>

          <Acto n={2} nombre="Lo que hicimos" frase="Validamos las fuentes entre sí y después las juntamos.">
            <p className="relato">
              Juntamos {F.confiabilidad.length} fuentes públicas de los cuatro frentes: lo que se registra, lo que la gente vive, lo que siente y las condiciones del entorno. Cada una lleva un <b>score de confiabilidad</b>.
              Antes de modelar comparamos cada serie con otra independiente, y así apareció el quiebre del hurto. Después armamos un <b>índice que dice en qué localidades hay más miedo del que muestran las cifras</b>.
            </p>
            <div className="rejilla r3">
              <Paso n="1" titulo="Juntamos y validamos" texto={`Encuestas (${fmt(R.n_bienal, 0)} y ${fmt(R.n_emv_bogota, 0)} personas, más el DANE y la Cámara de Comercio), registros de la SCJ, la Policía, Medicina Legal y Salud, y población, alumbrado y espacio público, unidos por localidad.`} />
              <Paso n="2" titulo="Armamos un índice" texto="Pusimos el miedo y el delito en la misma regla y los restamos: así se ve dónde sobra miedo frente a lo que se registra." />
              <Paso n="3" titulo="Lo comprobamos" texto={`Probamos ocho hipótesis y reportamos también las que no se sostienen. Ejemplo: el índice y la cifra oculta se correlacionan (${fmt(R.ibs_vs_cifra_oculta.rho, 2)}), pero al controlar el delito registrado queda en ${fmt(R.ibs_vs_cifra_oculta_parcial.rho, 2)}: es mecánica.`} />
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
          {[[String(F.confiabilidad.length), "fuentes públicas, cada una con su score"], [fmt(R.n_bienal, 0), "adultos en la Bienal de Cultura Ciudadana 2025"],
            [fmt(R.n_emv_bogota, 0), "encuestas de la EMV 2024 en Bogotá"], ["2018-2026", "series validadas con la Policía y Medicina Legal"]].map(([v, t]) => (
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
