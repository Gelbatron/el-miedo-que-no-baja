import { D, R, fmt, pval, signo } from "@/lib/datos";
import { Barras, Forest } from "@/components/Graficos";

export const metadata = { title: "Qué la explica · El miedo que no baja" };

const ORDEN = ["parque_atracos", "conflictos_vecinos", "homicidios_100k", "presencio_acoso", "arrienda", "edad", "narcoticos_100k_cientos", "hurtos_100k_miles", "mujer", "parque_spa", "sin_parque", "estrato"];

export default function QueExplica() {
  const ord = (filas: typeof D.ame.m_hechos) => ORDEN.map((v) => filas.find((f) => f.variable === v)).filter(Boolean) as typeof filas;
  const calif = D.ame.m_calif.filter((f) => ["alumbrado_malo", "ventas_informales_malo", "parque_atracos", "conflictos_vecinos", "hurtos_100k_miles", "homicidios_100k"].includes(f.variable));
  const fe = Object.fromEntries(D.ame_efectos_fijos.map((f) => [f.variable, f]));
  const wild = Object.fromEntries(D.lpm_wild.map((f) => [f.variable, f]));
  const principal = Object.fromEntries(D.ame.m_hechos.map((f) => [f.variable, f]));
  const robust = ["parque_atracos", "conflictos_vecinos", "hurtos_100k_miles", "homicidios_100k", "narcoticos_100k_cientos"];
  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Diagnóstico · logit ponderado sobre {fmt(D.n.m_hechos, 0)} adultos de la Bienal 2025</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>El entorno explica la percepción; el hurto registrado, no</h1>
        <p className="bajada">
          Resultado: califica mala o muy mala la seguridad de su zona ({fmt(D.medias.m_hechos * 100)} % de los adultos). Se controla sexo, edad, estrato y
          tenencia de la vivienda, y se añade el delito registrado de su localidad (SCJ). Los efectos son marginales promedio en puntos porcentuales,
          con intervalos por bootstrap de localidades.
        </p>
      </header>

      <section className="tarjeta">
        <h2>Modelo principal: hechos del entorno</h2>
        <p className="nota">Solo variables de hechos (sí/no) que vienen de preguntas distintas a la de seguridad, para evitar que el mismo juicio contamine ambos lados. Ámbar: aumenta la inseguridad; azul: la reduce; gris: no significativo.</p>
        <Forest filas={ord(D.ame.m_hechos)} />
      </section>

      <section className="rejilla">
        <div className="tarjeta">
          <h3>Capacidad predictiva fuera de muestra</h3>
          <p className="nota">AUC con validación cruzada estratificada (5 pliegues × 5 repeticiones), ponderada. 0,5 es azar.</p>
          <div className="leyenda"><span><i style={{ background: "var(--neutro)" }} />Solo perfil</span><span><i style={{ background: "var(--registro)" }} />Con delito registrado</span><span><i style={{ background: "var(--percepcion)" }} />Con entorno</span></div>
          <Barras filas={D.auc.map((a) => ({ etiqueta: a.bloque, valor: a.auc, detalle: `±${fmt(a.auc_sd, 3)} entre pliegues`,
            color: /hechos|calificación|Todo/.test(a.bloque) ? "var(--percepcion)" : a.bloque.includes("delito") ? "var(--registro)" : "var(--neutro)" }))} dec={3} maximo={0.85} />
          <p style={{ color: "var(--tinta-2)", fontSize: ".95rem" }}>
            Agregar el delito registrado de la localidad mueve el AUC de {fmt(R.auc["Perfil (sexo, edad, estrato, tenencia)"], 3)} a {fmt(R.auc["Perfil + delito registrado"], 3)}.
            Agregar el entorno lo lleva a {fmt(R.auc["Perfil + hechos del entorno"], 3)} con hechos y a {fmt(R.auc["Perfil + calificación del entorno"], 3)} con calificaciones.
          </p>
        </div>
        <div className="tarjeta">
          <h3>Con las calificaciones del entorno</h3>
          <p className="nota">Alumbrado y ventas informales se califican en la misma batería que la seguridad de la zona: el efecto puede estar inflado por el juicio general de la persona. Se reportan como complemento, no como hallazgo principal.</p>
          <Forest filas={calif} />
        </div>
      </section>

      <section className="tarjeta">
        <h2>Robustez: el resultado no depende de la especificación</h2>
        <div className="tabla-wrap">
          <table>
            <thead><tr><th>Variable</th><th className="n">Logit principal (pp)</th><th className="n">Efectos fijos de localidad (pp)</th><th className="n">Lineal ponderado (pp)</th><th className="n">p wild bootstrap</th></tr></thead>
            <tbody>
              {robust.map((v) => (
                <tr key={v}>
                  <td>{principal[v]?.etiqueta}</td>
                  <td className="n">{signo(principal[v].ame_pp)} <span style={{ color: "var(--tinta-3)" }}>({pval(principal[v].p)})</span></td>
                  <td className="n">{fe[v] ? signo(fe[v].ame_pp) : "absorbido"}</td>
                  <td className="n">{wild[v] ? signo(wild[v].coef_pp) : "s. d."}</td>
                  <td className="n">{wild[v] ? fmt(wild[v].p_wild, 3) : "s. d."}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="nota">
          Efectos fijos: compara personas dentro de la misma localidad, así que el delito de la localidad queda absorbido. Wild cluster bootstrap con pesos de Webb (999 réplicas):
          corrige el error estándar cuando hay pocos conglomerados (19 localidades). El homicidio de la localidad sí pesa, poco: +{fmt(principal.homicidios_100k.ame_pp, 2)} pp por cada homicidio adicional por 100.000 habitantes.
        </p>
      </section>

      <section className="rejilla">
        <div className="tarjeta">
          <h3>Califica a Bogotá como insegura ({fmt(D.medias.m_ciudad * 100)} %)</h3>
          <p className="nota">La percepción de la ciudad no responde a nada local: ni al delito de la localidad ni al entorno. Pesa ser mujer ({signo(D.ame.m_ciudad.find((f) => f.variable === "mujer")!.ame_pp)} pp).</p>
          <Forest filas={ord(D.ame.m_ciudad)} />
        </div>
        <div className="tarjeta">
          <h3>Siente miedo en el espacio público ({fmt(D.medias.m_miedo * 100)} %)</h3>
          <p className="nota">Aquí sí pesan la venta o consumo de drogas en el parque ({signo(D.ame.m_miedo.find((f) => f.variable === "parque_spa")!.ame_pp)} pp) y ser mujer ({signo(D.ame.m_miedo.find((f) => f.variable === "mujer")!.ame_pp)} pp).</p>
          <Forest filas={ord(D.ame.m_miedo)} />
        </div>
      </section>
    </div>
  );
}
