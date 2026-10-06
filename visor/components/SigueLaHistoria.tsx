"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ACTOS, RECORRIDO } from "@/lib/historia";

/** Al final de cada página: dónde va la historia y cuál es el siguiente paso. */
export function SigueLaHistoria() {
  const ruta = usePathname();
  const i = RECORRIDO.findIndex((r) => r.href === ruta);
  if (i < 0) return null;
  const ant = RECORRIDO[i - 1], sig = RECORRIDO[i + 1], aqui = RECORRIDO[i];
  return (
    <nav className="contenedor sigue" aria-label="Recorrido de la historia">
      <p className="antetitulo">Paso {i + 1} de {RECORRIDO.length} · {ACTOS[aqui.acto]}</p>
      <div className="sigue-fila">
        {ant ? (
          <Link href={ant.href} className="sigue-tarjeta">
            <span>← Anterior</span><b>{ant.titulo}</b>
          </Link>
        ) : <span />}
        {sig && (
          <Link href={sig.href} className="sigue-tarjeta sig">
            <span>Siguiente · {ACTOS[sig.acto]} →</span><b>{sig.titulo}</b>
          </Link>
        )}
      </div>
    </nav>
  );
}
