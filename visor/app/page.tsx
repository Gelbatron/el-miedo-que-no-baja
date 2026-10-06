import Link from "next/link";
import { D, R, fmt, signo } from "@/lib/datos";
import { MapaDoble } from "@/components/MapaDoble";

export default function Resumen() {
  const a = R.ame_hechos, w = R.emv_mujer_ame, auc = R.auc;
  const wild = Object.fromEntries(D.lpm_wild.map((f) => [f.variable, f]));
  return (
    <div className="pagina">
      <section className="cabecera-pagina" style={{ maxWidth: 880, gap: 14 }}>
        <p className="antetitulo">Bogotá DataJam Edición 5 · Seguridad ciudadana con enfoque de género</p>
        <h1>El miedo que no baja</h1>
        <p className="bajada">
          Bogotá registra muchos menos hurtos que hace siete años, pero tres de cada cuatro adultos la sienten insegura. Cruzamos los
          registros de la Secretaría de Seguridad con dos encuestas distritales para explicar esa distancia y decidir dónde intervenir.
        </p>
      </section>

      <section className="rejilla r2">
        <div className="tarjeta" style={{ borderTop: "4px solid var(--registro)" }}>
          <p className="antetitulo registro">Lo que se cuenta · registro SCJ</p>
          <div className="cifra">
            <b className="registro">{signo(R.hurto_personas.cambio_pct, 0)} %</b>
            <span>hurto a personas entre enero y agosto, de {fmt(R.hurto_personas["2019"], 0)} casos en 2019 a {fmt(R.hurto_personas["2026"], 0)} en 2026.</span>
          </div>
        </div>
        <div className="tarjeta" style={{ borderTop: "4px solid var(--percepcion)" }}>
          <p className="antetitulo percepcion">Lo que se siente · Bienal 2025</p>
          <div className="cifra">
            <b className="percepcion">{fmt(R.ciudad_insegura_pct, 0)} %</b>
            <span>de los adultos califica a Bogotá como insegura o muy insegura; el {fmt(R.zona_insegura_pct, 0)} % dice lo mismo de su propia zona.</span>
          </div>
        </div>
      </section>

      <section className="tarjeta plana" style={{ background: "var(--superficie-2)" }}>
        <p className="antetitulo">Pregunta analítica</p>
        <h2 style={{ fontSize: "clamp(1.25rem,2.4vw,1.6rem)" }}>
          ¿Por qué la inseguridad percibida no baja cuando el delito registrado sí, y en qué territorios debe intervenir primero el Distrito?
        </h2>
      </section>

      <section className="rejilla r3">
        <Hallazgo
          n="1" titulo="La ciudad no ve buena parte de su delito"
          cifra={`${fmt(R.cifra_oculta_bogota)} a 1`}
          texto={`Por cada delito de alto impacto registrado hay unas ${fmt(R.cifra_oculta_bogota)} víctimas según la Encuesta Mundial de Valores. En ${R.cifra_oculta_max[0]} la razón es ${fmt(R.cifra_oculta_max[1])}; en ${R.cifra_oculta_min[0]}, ${fmt(R.cifra_oculta_min[1])}. Donde hay más miedo que delito registrado es justo donde más se subregistra (ρ = ${fmt(R.ibs_vs_cifra_oculta.rho, 2)}).`}
          href="/brecha" tono="registro"
        />
        <Hallazgo
          n="2" titulo="El barrio se siente por lo que pasa en él"
          cifra={`${signo(a.parque_atracos.ame_pp)} pp`}
          texto={`Ver atracos en el parque más cercano sube ${fmt(a.parque_atracos.ame_pp)} puntos la probabilidad de sentir insegura la zona, y los conflictos vecinales hasta ${fmt(a.conflictos_vecinos.ame_pp)}. El hurto registrado de la localidad no tiene efecto (p = ${fmt(wild.hurtos_100k_miles?.p_wild ?? 1, 2)}) y no mejora la predicción (AUC ${fmt(auc["Perfil (sexo, edad, estrato, tenencia)"], 3)} → ${fmt(auc["Perfil + delito registrado"], 3)}).`}
          href="/que-explica" tono="percepcion"
        />
        <Hallazgo
          n="3" titulo="Las mujeres pagan el miedo con autonomía"
          cifra={`${signo(w.teme_acoso_sexual.ame_pp)} pp`}
          texto={`Con la misma edad, estrato y experiencia de victimización, las mujeres tienen ${fmt(w.teme_acoso_sexual.ame_pp)} puntos más de temor al acoso sexual y ${fmt(w.no_sale_noche.ame_pp)} más de evitar salir de noche, aunque reportan menos delitos (${fmt(R.emv_por_sexo.victima.mujeres)} % frente a ${fmt(R.emv_por_sexo.victima.hombres)} %).`}
          href="/genero" tono="mujeres"
        />
      </section>

      <section className="tarjeta">
        <div style={{ display: "grid", gap: 6 }}>
          <h2>Percepción y registro no dibujan el mismo mapa</h2>
          <p className="nota">Área urbana de las 19 localidades. Cinco clases por quintiles. Pasa el cursor o el dedo por una localidad para ver su valor.</p>
        </div>
        <MapaDoble />
        <Link className="boton sec" href="/mapa" style={{ justifySelf: "start" }}>Explorar todos los indicadores en el mapa →</Link>
      </section>

      <section className="tarjeta">
        <h2>Qué recomendamos a la ciudad</h2>
        <ol style={{ margin: 0, paddingLeft: "1.2em", display: "grid", gap: 10, color: "var(--tinta-2)" }}>
          <li><b style={{ color: "var(--tinta)" }}>Medir la seguridad con victimización, no solo con registros.</b> Usar las preguntas de victimización de la Encuesta Distrital de Percepción (representativa por UPL) para corregir la asignación de recursos donde el registro subestima.</li>
          <li><b style={{ color: "var(--tinta)" }}>Entornos que se sienten seguros, priorizados por el Índice de Brecha.</b> Parques sin atracos, alumbrado y mediación de conflictos vecinales, empezando por {R.ibs_top5.join(", ")}.</li>
          <li><b style={{ color: "var(--tinta)" }}>La autonomía de las mujeres como resultado de la política.</b> Seguir cada semestre, por sexo, el porcentaje que evita salir de noche.</li>
          <li><b style={{ color: "var(--tinta)" }}>Datos que permitan evaluar.</b> Publicar el inventario georreferenciado de alumbrado (el del portal es de 2019) y los delitos por UPZ.</li>
        </ol>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Link className="boton" href="/indicador">Ver la ficha del indicador</Link>
          <Link className="boton sec" href="/simulador">Probar el simulador</Link>
        </div>
      </section>
    </div>
  );
}

function Hallazgo({ n, titulo, cifra, texto, href, tono }: { n: string; titulo: string; cifra: string; texto: string; href: string; tono: string }) {
  return (
    <Link href={href} className="tarjeta" style={{ textDecoration: "none", color: "inherit" }}>
      <p className="antetitulo">Hallazgo {n}</p>
      <h3>{titulo}</h3>
      <b style={{ fontFamily: "var(--f-display)", fontSize: "2.3rem", letterSpacing: "-.03em", color: `var(--${tono === "mujeres" ? "mujeres" : tono + "-texto"})`, lineHeight: 1 }}>{cifra}</b>
      <p style={{ color: "var(--tinta-2)", fontSize: ".95rem" }}>{texto}</p>
      <span style={{ color: "var(--registro-texto)", fontSize: ".9rem" }}>Ver la evidencia →</span>
    </Link>
  );
}
