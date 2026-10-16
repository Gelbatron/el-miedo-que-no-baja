"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const RUTAS = [
  ["/", "La historia"], ["/video", "Video"], ["/tendencia", "Tendencia"], ["/mapa", "Mapa"], ["/brecha", "La brecha"], ["/que-explica", "Qué la explica"],
  ["/genero", "Género"], ["/simulador", "Simulador"], ["/indicador", "Indicador"],
  ["/metodologia", "Método"], ["/modelos", "Modelos"], ["/datos", "Datos"], ["/entregables", "Entregables"],
] as const;

export function Navegacion() {
  const ruta = usePathname();
  if (ruta === "/acceso" || ruta === "/presentar") return null;
  return (
    <header className="barra">
      <div className="franja" aria-hidden="true" />
      <div className="contenedor barra-int">
        <Link href="/" className="marca" aria-label="El miedo que no baja, inicio">
          <Farol />
          <span><b>El miedo que no baja</b><small>DataJam 5 · The data squad</small></span>
        </Link>
        <div className="barra-acciones">
          <Link href="/presentar" className="boton" aria-label="Presentar" style={{ padding: "7px 14px", fontSize: ".82rem", whiteSpace: "nowrap" }}>▶<span className="solo-ancho"> Presentar</span></Link>
          <form action="/api/salir" method="post">
            <button className="salir" type="submit">Salir</button>
          </form>
        </div>
      </div>
      <div className="barra-nav">
        <nav className="contenedor nav" aria-label="Secciones">
          {RUTAS.map(([href, txt]) => (
            <Link key={href} href={href} aria-current={ruta === href ? "page" : undefined}>{txt}</Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

export function Farol({ tam = 34, claro = false }: { tam?: number; claro?: boolean }) {
  // farol de alumbrado: el haz oro (lo que se siente) sobre la base azul (lo que se registra)
  const cuerpo = claro ? "#ffffff" : "var(--rojo)";
  return (
    <svg width={tam} height={tam} viewBox="0 0 40 40" aria-hidden="true">
      <circle cx="20" cy="20" r="19" fill={claro ? "rgba(255,255,255,.12)" : "var(--superficie-2)"} />
      <rect x="19" y="5" width="2" height="6" rx="1" fill={cuerpo} />
      <path d="M12 11h16l-3.5 6.5h-9z" fill={cuerpo} />
      <path d="M15.5 17.5h9L30 31H10z" fill="var(--oro)" opacity=".9" />
      <rect x="9" y="31" width="22" height="3.2" rx="1.6" fill="var(--registro)" />
    </svg>
  );
}
