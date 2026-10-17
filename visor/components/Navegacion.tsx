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
  // sello del proyecto: el registro (azul o blanco) baja; el miedo (oro) no baja; entre los dos, la brecha
  const fondo = claro ? "#ffffff" : "var(--rojo)";
  const registro = claro ? "var(--registro)" : "#ffffff";
  const miedo = claro ? "#d99a16" : "#f2c14e";
  return (
    <svg width={tam} height={tam} viewBox="0 0 40 40" aria-hidden="true">
      <rect width="40" height="40" rx="10" fill={fondo} />
      <path d="M8 14.5 L20 13.2 L32 11.8 L32 29.5 L20 23.8 L8 16.6 Z" fill={miedo} opacity=".28" />
      <path d="M8 16.6 L20 23.8 L32 29.5" fill="none" stroke={registro} strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M8 14.5 L20 13.2 L32 11.8" fill="none" stroke={miedo} strokeWidth="3.6" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="32" cy="11.8" r="3" fill={miedo} />
      <circle cx="32" cy="29.5" r="2.6" fill={registro} />
    </svg>
  );
}
