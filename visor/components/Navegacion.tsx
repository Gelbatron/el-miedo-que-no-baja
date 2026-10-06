"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const RUTAS = [
  ["/", "Resumen"], ["/mapa", "Mapa"], ["/brecha", "La brecha"], ["/que-explica", "Qué la explica"],
  ["/genero", "Género"], ["/tendencia", "Tendencia"], ["/simulador", "Simulador"], ["/indicador", "Indicador"],
  ["/metodologia", "Método"], ["/datos", "Datos"], ["/entregables", "Entregables"],
] as const;

export function Navegacion() {
  const ruta = usePathname();
  if (ruta === "/acceso") return null;
  return (
    <header className="barra">
      <div className="contenedor barra-int">
        <Link href="/" className="marca" aria-label="El miedo que no baja, inicio">
          <Farol />
          <span>El miedo que no baja</span>
        </Link>
        <nav className="nav" aria-label="Secciones">
          {RUTAS.map(([href, txt]) => (
            <Link key={href} href={href} aria-current={ruta === href ? "page" : undefined}>{txt}</Link>
          ))}
        </nav>
        <form action="/api/salir" method="post">
          <button className="salir" type="submit">Salir</button>
        </form>
      </div>
    </header>
  );
}

export function Farol({ tam = 26 }: { tam?: number }) {
  // farol de alumbrado: el haz ámbar (lo que se siente) sobre la base azul (lo que se registra)
  return (
    <svg width={tam} height={tam} viewBox="0 0 32 32" aria-hidden="true">
      <path d="M9 7h14l-3 6h-8z" fill="var(--tinta)" />
      <path d="M12 13h8l5 14H7z" fill="var(--percepcion)" opacity=".85" />
      <rect x="15" y="2" width="2" height="5" fill="var(--tinta)" />
      <rect x="6" y="27" width="20" height="3" rx="1.5" fill="var(--registro)" />
    </svg>
  );
}
