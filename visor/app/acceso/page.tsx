import { Farol } from "@/components/Navegacion";
import { EquipoMini } from "@/components/Equipo";

export const metadata = { title: "Acceso · El miedo que no baja" };

export default async function Acceso({ searchParams }: { searchParams: Promise<{ error?: string; siguiente?: string }> }) {
  const { error, siguiente } = await searchParams;
  return (
    <div style={{ minHeight: "100vh", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 380px), 1fr))" }}>
      <section className="heroe" style={{ display: "grid", alignContent: "center", padding: "48px clamp(20px, 6vw, 72px)", gap: 18 }}>
        <Farol tam={56} claro />
        <p className="antetitulo">Bogotá DataJam Edición 5 · The data squad</p>
        <h1 style={{ fontSize: "clamp(2.4rem, 6vw, 4.2rem)" }}>El miedo <em>que no baja</em></h1>
        <div className="heroe-raya" />
        <p className="bajada">Inseguridad percibida frente a delito registrado en Bogotá: dónde está la brecha, qué la explica y dónde intervenir primero.</p>
        <EquipoMini />
        <div className="creditos">
          <span className="creditos-t">Reto</span>
          <span>Bogotá DataJam 2026 · Secretaría General de la Alcaldía Mayor de Bogotá y Universidad Compensar</span>
          <span className="creditos-t">Datos</span>
          <span>Datos Abiertos Bogotá · IDECA · Secretaría de Seguridad · Secretaría de Planeación · Secretaría de Cultura · Secretaría de Salud · UAESP · DANE · Policía Nacional</span>
        </div>
      </section>
      <section style={{ display: "grid", placeItems: "center", padding: "40px 20px", background: "var(--fondo)" }}>
        <form action="/api/acceso" method="post" className="tarjeta" style={{ width: "min(100%, 420px)", gap: 18 }}>
          <div style={{ display: "grid", gap: 6 }}>
            <p className="antetitulo">Acceso al visor</p>
            <h2 style={{ fontSize: "1.5rem" }}>Ingresa la clave</h2>
            <p className="nota" style={{ fontSize: ".95rem" }}>La clave viene en el correo de entrega del equipo.</p>
          </div>
          <label className="campo" htmlFor="clave">
            Clave de acceso
            <input id="clave" name="clave" type="password" autoComplete="current-password" required autoFocus />
          </label>
          <input type="hidden" name="siguiente" value={siguiente ?? "/"} />
          {error && <p role="alert" style={{ color: "var(--rojo)", fontSize: ".9rem", fontWeight: 600 }}>La clave no coincide. Revísala e inténtalo de nuevo.</p>}
          <button className="boton" type="submit">Entrar</button>
          <p className="nota" style={{ fontSize: ".78rem" }}>Proyecto académico del Bogotá DataJam 5. No es un sitio oficial de la Alcaldía de Bogotá.</p>
        </form>
      </section>
    </div>
  );
}
