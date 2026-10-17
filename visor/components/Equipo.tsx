/* eslint-disable @next/next/no-img-element */
export const EQUIPO = [
  { nombre: "Brandow Brusly León Rodríguez", corto: "Brandow León", rol: "Analista de políticas públicas", foto: "/equipo/brandow.jpg" },
  { nombre: "Samuel Esteban Riveros Cubides", corto: "Samuel Riveros", rol: "Experto temático", foto: "/equipo/samuel.jpg" },
  { nombre: "Rafael Estiven Londoño Camacho", corto: "Rafael Londoño", rol: "Analista de datos", foto: "/equipo/rafael.jpg" },
] as const;

export const PROGRAMA = "Ciencia de Datos";

/** El equipo, con foto, nombre completo, rol del formulario de caracterización y programa. */
export function Equipo({ titulo = "El equipo" }: { titulo?: string }) {
  return (
    <section className="equipo tarjeta" aria-label={titulo}>
      <div className="equipo-cab">
        <p className="antetitulo">The data squad · equipo #16 · estudiantes de {PROGRAMA}</p>
        <h2>{titulo}</h2>
      </div>
      <div className="equipo-lista">
        {EQUIPO.map((p) => (
          <figure key={p.foto} className="equipo-p">
            <img src={p.foto} alt={`Foto de ${p.nombre}`} width={120} height={120} loading="lazy" />
            <figcaption><b>{p.nombre}</b><span>{p.rol}</span><span className="equipo-prog">{PROGRAMA}</span></figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

/** Versión compacta para fondos rojos (pantalla de acceso). */
export function EquipoMini() {
  return (
    <div className="equipo-mini" aria-label="Equipo">
      {EQUIPO.map((p) => (
        <figure key={p.foto}>
          <img src={p.foto} alt={`Foto de ${p.nombre}`} width={64} height={64} />
          <figcaption><b>{p.corto}</b><span>{p.rol}</span></figcaption>
        </figure>
      ))}
      <p>Estudiantes de {PROGRAMA}</p>
    </div>
  );
}
