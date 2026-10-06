"use client";
import Link from "next/link";
import { DIAPOS } from "./Clase";

/** Guion imprimible de la clase. También publica los datos en JSON para el respaldo en PDF y PowerPoint. */
export function Guion() {
  const datos = DIAPOS.map(({ id, corto, titulo, pasos, quien, tiempo, nota, soloClase }) => ({ id, corto, titulo: titulo ?? corto, pasos, quien, tiempo, nota, soloClase: !!soloClase }));
  let n = 0;
  const nPitch = datos.filter((d) => !d.soloClase).length;
  return (
    <div className="contenedor pagina" style={{ maxWidth: 900 }}>
      <script type="application/json" id="guion-datos" dangerouslySetInnerHTML={{ __html: JSON.stringify(datos) }} />
      <header className="cabecera-pagina">
        <p className="antetitulo">Guion de la presentación · pitch de 6 minutos</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Quién dice qué, y cuándo</h1>
        <p className="bajada">
          {nPitch} láminas en modo pitch (unos 5:25) y {datos.length - nPitch} más en la clase completa. Cuatro actos: el problema, lo que hicimos, lo que encontramos y por qué importa. → avanza un paso; N muestra estas notas en pantalla; D abre «¿Cómo lo sabemos?» para las preguntas del jurado.
        </p>
        <p><Link className="boton" href="/presentar">▶ Abrir la presentación</Link></p>
      </header>
      <ol style={{ listStyle: "none", padding: 0, display: "grid", gap: 14 }}>
        {datos.map((d) => {
          if (!d.soloClase) n++;
          return (
            <li key={d.id} className="tarjeta" style={{ gap: 6, borderLeft: `5px solid ${d.soloClase ? "var(--neutro)" : "var(--rojo)"}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                <b>{d.soloClase ? "Solo clase completa" : `${n}.`} {d.titulo}</b>
                <span className="mono" style={{ color: "var(--tinta-2)" }}>{d.quien} · {d.tiempo} · {d.pasos} {d.pasos === 1 ? "paso" : "pasos"}</span>
              </div>
              <p style={{ margin: 0, color: "var(--tinta-2)" }}>{d.nota}</p>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
