"use client";
import { useEffect, useState, type CSSProperties, type ReactNode } from "react";

/** Bloque que aparece (sube y se aclara) cuando llega su paso. */
export function Ap({ si, children, retraso = 0, style, className = "" }: { si: boolean; children: ReactNode; retraso?: number; style?: CSSProperties; className?: string }) {
  return (
    <div className={`cl-ap${si ? " si" : ""} ${className}`} style={{ transitionDelay: si ? `${retraso}ms` : "0ms", ...style }} aria-hidden={!si}>
      {children}
    </div>
  );
}

/** true un instante después de montar: permite animar lo que ya es visible en el paso 0. */
export function useListo() {
  const [ok, setOk] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setOk(true), 60);
    return () => clearTimeout(t);
  }, []);
  return ok;
}

/** Cuenta de 0 a total mientras está activo (para que los puntos «caigan» uno a uno). */
export function useConteo(activo: boolean, total: number, ms = 2600) {
  const [n, setN] = useState(0);
  useEffect(() => {
    if (!activo) { setN(0); return; }
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) { setN(total); return; }
    const t0 = performance.now();
    const reloj = setInterval(() => {
      const f = Math.min(1, (performance.now() - t0) / ms);
      setN(Math.round(total * (1 - Math.pow(1 - f, 2))));
      if (f >= 1) clearInterval(reloj);
    }, 30);
    return () => clearInterval(reloj);
  }, [activo, total, ms]);
  return n;
}

export const lin = (d0: number, d1: number, r0: number, r1: number) => (v: number) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);

/** Cifra grande con su lectura. */
export function Cifra({ ante, valor, color, texto, style }: { ante?: string; valor: string; color: string; texto: ReactNode; style?: CSSProperties }) {
  return (
    <div className="cl-tarjeta" style={{ borderTop: `6px solid ${color}`, gap: 4, ...style }}>
      {ante && <span className="cl-ante" style={{ color }}>{ante}</span>}
      <span className="cl-num" style={{ color, fontSize: 56 }}>{valor}</span>
      <span className="cl-txt" style={{ fontSize: 17 }}>{texto}</span>
    </div>
  );
}

/** Silueta de persona para los arreglos de íconos. */
export function Persona({ x, y, t, lleno, color }: { x: number; y: number; t: number; lleno: boolean; color: string }) {
  return (
    <g>
      <circle cx={x} cy={y - t * 0.3} r={t * 0.17} fill={lleno ? color : "none"} stroke={color} strokeWidth={2.5} />
      <path d={`M${x - t * 0.3},${y + t * 0.42} Q${x - t * 0.3},${y - t * 0.06} ${x},${y - t * 0.06} Q${x + t * 0.3},${y - t * 0.06} ${x + t * 0.3},${y + t * 0.42} Z`}
        fill={lleno ? color : "none"} stroke={color} strokeWidth={2.5} strokeLinejoin="round" />
    </g>
  );
}

/** Interruptor sí/no grande, legible en proyector. */
export function Interruptor({ etiqueta, valor, onCambio, detalle }: { etiqueta: string; valor: boolean; onCambio: (v: boolean) => void; detalle?: string }) {
  return (
    <div className="cl-interruptor">
      <span>{etiqueta}{detalle && <small style={{ display: "block", color: "var(--tinta-3)", fontSize: 13 }}>{detalle}</small>}</span>
      <div className="segmentado" role="group" aria-label={etiqueta}>
        <button aria-pressed={!valor} onClick={() => onCambio(false)}>No</button>
        <button aria-pressed={valor} onClick={() => onCambio(true)}>Sí</button>
      </div>
    </div>
  );
}
