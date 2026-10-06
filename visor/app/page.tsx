import Link from "next/link";
import { D, R, fmt, signo } from "@/lib/datos";
import { MapaDoble } from "@/components/MapaDoble";
import { Icono } from "@/components/Iconos";

export default function Resumen() {
  const a = R.ame_hechos, w = R.emv_mujer_ame, auc = R.auc;
  const wild = Object.fromEntries(D.lpm_wild.map((f) => [f.variable, f]));
  const top5 = new Set((D.ibs as Record<string, number>[]).slice(0, 5).map((f) => Number(f.localidad)));
  const { ancho, alto } = D.geo;
  return (
    <>
      <section className="heroe">
        <div className="contenedor heroe-int">
          <div style={{ display: "grid", gap: 18 }}>
            <p className="antetitulo">Bogotá DataJam Edición 5 · Seguridad ciudadana con enfoque de género</p>
            <h1>El miedo <em>que no baja</em></h1>
            <div className="heroe-raya" />
            <p className="bajada">
              Bogotá registra muchos menos hurtos que hace siete años, pero tres de cada cuatro adultos la sienten insegura. Cruzamos los
              registros de la Secretaría de Seguridad con dos encuestas distritales para explicar esa distancia y decidir dónde intervenir.
            </p>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <Link className="boton blanco" href="/brecha">Ver la brecha</Link>
              <Link className="boton sec" href="/simulador" style={{ color: "#fff", borderColor: "rgba(255,255,255,.7)" }}>Probar el simulador</Link>
            </div>
          </div>
          <figure style={{ margin: 0, display: "grid", gap: 8, justifyItems: "center" }}>
            <svg className="silueta" viewBox={`-4 -4 ${ancho + 8} ${alto + 8}`} role="img"
              aria-label="Bogotá urbana; en oro, las cinco localidades con mayor Índice de Brecha">
              {D.geo.localidades.map((l) => (
                <path key={l.id} d={l.d} className={top5.has(l.id) ? "brilla" : undefined} data-tip={`<b>${l.nombre}</b>${top5.has(l.id) ? "<br>Prioridad: top 5 del Índice de Brecha" : ""}`} />
              ))}
            </svg>
            <figcaption style={{ fontSize: ".8rem", color: "rgba(255,255,255,.85)" }}>En oro: las cinco localidades donde intervenir primero</figcaption>
          </figure>
        </div>
      </section>

      <div className="contenedor">
        <section className="cifras-heroe">
          <Cifra etiqueta="Lo que se cuenta · registro SCJ" valor={`${signo(R.hurto_personas.cambio_pct, 0)} %`} tono="registro"
            texto={`hurto a personas entre enero y agosto, de ${fmt(R.hurto_personas["2019"], 0)} casos en 2019 a ${fmt(R.hurto_personas["2026"], 0)} en 2026.`} />
          <Cifra etiqueta="Lo que se siente · Bienal 2025" valor={`${fmt(R.ciudad_insegura_pct, 0)} %`} tono="percepcion"
            texto={`de los adultos califica a Bogotá como insegura o muy insegura; el ${fmt(R.zona_insegura_pct, 0)} % dice lo mismo de su propia zona.`} />
          <Cifra etiqueta="Lo que no se ve · cifra oculta" valor={`${fmt(R.cifra_oculta_bogota)} a 1`} tono="vino"
            texto="víctimas (Encuesta Mundial de Valores) por cada delito de alto impacto que registra la Secretaría de Seguridad." />
        </section>
      </div>

      <section className="banda">
        <div className="contenedor titulo-seccion" style={{ marginBottom: 0 }}>
          <p className="antetitulo">Pregunta analítica</p>
          <h2 style={{ color: "var(--tinta)", fontSize: "clamp(1.4rem,3vw,2.1rem)", maxWidth: 900 }}>
            ¿Por qué la inseguridad percibida no baja cuando el delito registrado sí, y en qué territorios debe intervenir primero el Distrito?
          </h2>
        </div>
      </section>

      <section className="banda gris">
        <div className="contenedor">
          <div className="titulo-seccion">
            <h2>Lo que encontramos</h2>
            <p>Tres hallazgos sostenidos con siete fuentes públicas, modelos ponderados y pruebas de robustez.</p>
          </div>
          <div className="rejilla r3">
            <Hallazgo n="1" titulo="La ciudad no ve buena parte de su delito" cifra={`${fmt(R.cifra_oculta_bogota)} a 1`} href="/brecha"
              texto={`En ${R.cifra_oculta_max[0]} hay ${fmt(R.cifra_oculta_max[1])} víctimas por delito registrado; en ${R.cifra_oculta_min[0]}, ${fmt(R.cifra_oculta_min[1])}. Donde hay más miedo que delito registrado es justo donde más se subregistra (ρ = ${fmt(R.ibs_vs_cifra_oculta.rho, 2)}).`} />
            <Hallazgo n="2" titulo="El barrio se siente por lo que pasa en él" cifra={`${signo(a.parque_atracos.ame_pp)} pp`} href="/que-explica"
              texto={`Ver atracos en el parque cercano sube ${fmt(a.parque_atracos.ame_pp)} puntos la probabilidad de sentir insegura la zona; los conflictos vecinales, hasta ${fmt(a.conflictos_vecinos.ame_pp)}. El hurto registrado no pesa (p = ${fmt(wild.hurtos_100k_miles?.p_wild ?? 1, 2)}) ni mejora la predicción (AUC ${fmt(auc["Perfil (sexo, edad, estrato, tenencia)"], 3)} → ${fmt(auc["Perfil + delito registrado"], 3)}).`} />
            <Hallazgo n="3" titulo="Las mujeres pagan el miedo con autonomía" cifra={`${signo(w.teme_acoso_sexual.ame_pp)} pp`} href="/genero"
              texto={`A igual edad, estrato y victimización, las mujeres tienen ${fmt(w.teme_acoso_sexual.ame_pp)} puntos más de temor al acoso sexual y ${fmt(w.no_sale_noche.ame_pp)} más de evitar salir de noche, aunque reportan menos delitos (${fmt(R.emv_por_sexo.victima.mujeres)} % frente a ${fmt(R.emv_por_sexo.victima.hombres)} %).`} />
          </div>
        </div>
      </section>

      <section className="banda">
        <div className="contenedor">
          <div className="titulo-seccion">
            <h2>Percepción y registro no dibujan el mismo mapa</h2>
            <p>Área urbana de las 19 localidades, cinco clases por quintiles. Oro: lo que se siente. Azul: lo que se registra.</p>
          </div>
          <div className="tarjeta"><MapaDoble /></div>
          <div style={{ display: "flex", justifyContent: "center", marginTop: 18 }}>
            <Link className="boton sec" href="/mapa">Explorar los 20 indicadores en el mapa</Link>
          </div>
        </div>
      </section>

      <section className="banda gris">
        <div className="contenedor">
          <div className="titulo-seccion">
            <h2>Qué recomendamos a la ciudad</h2>
            <p>Cuatro acciones a escala distrital, medibles con fuentes que el Distrito ya produce.</p>
          </div>
          <div className="rejilla r4">
            <Accion icono="encuesta" titulo="Medir con victimización" texto="Sumar las preguntas de victimización de la Encuesta Distrital de Percepción (por UPL) al registro de la SCJ para corregir la asignación donde se subregistra." />
            <Accion icono="parque" titulo="Entornos que se sienten seguros" texto={`Parques sin atracos, mediación de conflictos vecinales y alumbrado, empezando por ${R.ibs_top5.join(", ")}.`} />
            <Accion icono="mujer" titulo="La autonomía de las mujeres" texto="Seguir cada semestre, por sexo, el porcentaje que evita salir de noche como indicador de resultado de la política de seguridad." />
            <Accion icono="datos" titulo="Datos para evaluar" texto="Publicar el inventario georreferenciado de alumbrado (el del portal es de 2019) y los delitos por UPZ y mes." />
          </div>
          <div style={{ display: "flex", justifyContent: "center", gap: 10, flexWrap: "wrap", marginTop: 26 }}>
            <Link className="boton" href="/indicador">Ver la ficha del indicador</Link>
            <Link className="boton sec" href="/entregables">Ver todos los entregables</Link>
          </div>
        </div>
      </section>

      <section className="banda">
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

function Cifra({ etiqueta, valor, texto, tono }: { etiqueta: string; valor: string; texto: string; tono: "registro" | "percepcion" | "vino" }) {
  const col = tono === "vino" ? "var(--vino)" : `var(--${tono}-texto)`;
  const borde = tono === "vino" ? "var(--vino)" : `var(--${tono})`;
  return (
    <div className="tarjeta" style={{ borderTop: `5px solid ${borde}` }}>
      <p className="antetitulo" style={{ color: col }}>{etiqueta}</p>
      <div className="cifra"><b style={{ color: col }}>{valor}</b><span>{texto}</span></div>
    </div>
  );
}

function Hallazgo({ n, titulo, cifra, texto, href }: { n: string; titulo: string; cifra: string; texto: string; href: string }) {
  return (
    <Link href={href} className="tarjeta-vino">
      <span className="etiqueta">Hallazgo {n}</span>
      <h3>{titulo}</h3>
      <span className="grande">{cifra}</span>
      <p>{texto}</p>
      <span className="mas">Ver la evidencia →</span>
    </Link>
  );
}

function Accion({ icono, titulo, texto }: { icono: "encuesta" | "parque" | "mujer" | "datos"; titulo: string; texto: string }) {
  return (
    <div className="tarjeta" style={{ justifyItems: "center", textAlign: "center" }}>
      <span className="icono-circulo" style={{ width: 76, height: 76 }}><Icono nombre={icono} /></span>
      <h3>{titulo}</h3>
      <p className="nota" style={{ fontSize: ".92rem", color: "var(--tinta-2)" }}>{texto}</p>
    </div>
  );
}
