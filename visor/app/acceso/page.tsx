import { Farol } from "@/components/Navegacion";

export const metadata = { title: "Acceso · El miedo que no baja" };

export default async function Acceso({ searchParams }: { searchParams: Promise<{ error?: string; siguiente?: string }> }) {
  const { error, siguiente } = await searchParams;
  return (
    <div style={{ minHeight: "82vh", display: "grid", placeItems: "center", paddingBlock: 40 }}>
      <form action="/api/acceso" method="post" className="tarjeta" style={{ width: "min(100%, 420px)", gap: 18 }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <Farol tam={34} />
          <div>
            <p className="antetitulo">DataJam 5 · The data squad</p>
            <h2 style={{ fontSize: "1.5rem" }}>El miedo que no baja</h2>
          </div>
        </div>
        <p className="nota" style={{ fontSize: ".95rem" }}>
          Visor de la brecha entre inseguridad percibida y delito registrado en Bogotá. Ingresa la clave que recibiste con la entrega.
        </p>
        <label className="campo" htmlFor="clave">
          Clave de acceso
          <input id="clave" name="clave" type="password" autoComplete="current-password" required autoFocus />
        </label>
        <input type="hidden" name="siguiente" value={siguiente ?? "/"} />
        {error && <p role="alert" style={{ color: "var(--percepcion-texto)", fontSize: ".9rem" }}>La clave no coincide. Revísala e inténtalo de nuevo.</p>}
        <button className="boton" type="submit" style={{ justifyContent: "center" }}>Entrar</button>
      </form>
    </div>
  );
}
