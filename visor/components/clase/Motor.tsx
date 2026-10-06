"use client";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";

/** Una lámina: se revela por pasos (→ avanza un paso; al terminar, pasa a la siguiente). */
export type Diapo = {
  id: string;
  corto: string;
  ante?: string;
  titulo?: string;
  pasos: number;
  quien: string;
  tiempo: string;
  nota: string;
  roja?: boolean;
  soloClase?: boolean;
  profundizar?: ReactNode;
  render: (paso: number) => ReactNode;
};

type Modo = "pitch" | "clase";
const ANCHO = 1280, ALTO = 720, DURACION = 6 * 60;

export function Motor({ diapos }: { diapos: Diapo[] }) {
  const [modo, setModo] = useState<Modo>("pitch");
  const lista = useMemo(() => diapos.filter((d) => modo === "clase" || !d.soloClase), [diapos, modo]);
  const [pos, setPos] = useState({ i: 0, paso: 0 });
  const [notas, setNotas] = useState(false);
  const [prof, setProf] = useState(false);
  const [inicio, setInicio] = useState<number | null>(null);
  const [ahora, setAhora] = useState(0);
  const [escala, setEscala] = useState(0.5);
  const [captura, setCaptura] = useState(false);
  const marco = useRef<HTMLDivElement>(null);
  const i = Math.min(pos.i, lista.length - 1);
  const d = lista[i];

  // modo guardado y lámina del enlace (#indice abre esa lámina)
  useEffect(() => {
    let m: Modo = "pitch";
    try { if (localStorage.getItem("clase-modo") === "clase") m = "clase"; } catch {}
    // #indice abre esa lámina; #indice~2, en su tercer paso; #indice~0~d, con «¿Cómo lo sabemos?» abierto
    const [id, pasoTxt, extra] = window.location.hash.slice(1).split("~");
    if (extra === "d") abrirAlCargar.current = true;
    if (extra === "c") setCaptura(true); // sin controles ni márgenes: para el respaldo en PDF
    const pedida = diapos.find((x) => x.id === id);
    if (pedida?.soloClase) m = "clase";
    setModo(m);
    const k = diapos.filter((x) => m === "clase" || !x.soloClase).findIndex((x) => x.id === id);
    if (k >= 0 && pedida) setPos({ i: k, paso: Math.min(Math.max(0, Number(pasoTxt) || 0), pedida.pasos - 1) });
  }, [diapos]);

  const abrirAlCargar = useRef(false);
  useEffect(() => {
    if (abrirAlCargar.current && d.profundizar) { abrirAlCargar.current = false; setProf(true); return; }
    setProf(false);
  }, [d.id, d.profundizar]);
  useEffect(() => { window.history.replaceState(null, "", `#${d.id}${pos.paso ? `~${pos.paso}` : ""}`); }, [d.id, pos.paso]);

  // escala del escenario al tamaño disponible
  useEffect(() => {
    const el = marco.current;
    if (!el) return;
    const margen = captura ? 0 : 24;
    const medir = () => setEscala(Math.min((el.clientWidth - margen) / ANCHO, (el.clientHeight - margen) / ALTO));
    medir();
    const ro = new ResizeObserver(medir);
    ro.observe(el);
    return () => ro.disconnect();
  }, [captura]);

  const arrancar = () => setInicio((v) => v ?? Date.now());
  const avanzar = useCallback(() => {
    arrancar();
    setPos(({ i, paso }) => {
      const dd = lista[Math.min(i, lista.length - 1)];
      if (paso < dd.pasos - 1) return { i, paso: paso + 1 };
      if (i < lista.length - 1) return { i: i + 1, paso: 0 };
      return { i, paso };
    });
  }, [lista]);
  const retroceder = useCallback(() => {
    setPos(({ i, paso }) => (paso > 0 ? { i, paso: paso - 1 } : i > 0 ? { i: i - 1, paso: lista[i - 1].pasos - 1 } : { i, paso }));
  }, [lista]);

  const cambiarModo = (m: Modo) => {
    try { localStorage.setItem("clase-modo", m); } catch {}
    const nueva = diapos.filter((x) => m === "clase" || !x.soloClase);
    const k = nueva.findIndex((x) => x.id === d.id);
    setModo(m);
    setPos({ i: k >= 0 ? k : Math.min(i, nueva.length - 1), paso: 0 });
    setInicio(null);
  };

  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement | null;
      if (e.key === "PageDown") { e.preventDefault(); avanzar(); return; } // control remoto
      if (e.key === "PageUp") { e.preventDefault(); retroceder(); return; }
      if (el?.closest?.("input, select, textarea")) return;
      if (e.key === "ArrowRight" || (e.key === " " && el?.tagName !== "BUTTON")) { e.preventDefault(); avanzar(); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); retroceder(); }
      else if (e.key === "n" || e.key === "N") setNotas((v) => !v);
      else if ((e.key === "d" || e.key === "D") && d.profundizar) setProf((v) => !v);
      else if (e.key === "Escape") setProf(false);
      else if (e.key === "f" || e.key === "F") document.documentElement.requestFullscreen?.().catch(() => {});
      else if (e.key === "Home") setPos({ i: 0, paso: 0 });
      else if (e.key === "End") setPos({ i: lista.length - 1, paso: 0 });
    };
    // al soltar un deslizador, las flechas vuelven a mover la presentación
    const soltar = (e: PointerEvent) => { const t = e.target as HTMLElement; if (t?.matches?.('input[type="range"]')) setTimeout(() => t.blur(), 0); };
    window.addEventListener("keydown", tecla);
    window.addEventListener("pointerup", soltar);
    return () => { window.removeEventListener("keydown", tecla); window.removeEventListener("pointerup", soltar); };
  }, [avanzar, retroceder, d, lista.length]);

  useEffect(() => {
    if (inicio === null) return;
    const t = setInterval(() => setAhora(Date.now()), 500);
    return () => clearInterval(t);
  }, [inicio]);

  const seg = inicio === null ? 0 : Math.floor((ahora - inicio) / 1000);
  const reloj = modo === "pitch" ? DURACION - seg : seg;
  const mmss = (s: number) => `${s < 0 ? "−" : ""}${Math.floor(Math.abs(s) / 60)}:${String(Math.abs(s) % 60).padStart(2, "0")}`;
  const estadoReloj = modo === "pitch" ? (reloj <= 0 ? " fuera" : reloj <= 60 ? " alerta" : "") : "";

  return (
    <div className="modo-presentacion" role="region" aria-roledescription="presentación" aria-label="Clase: El miedo que no baja">
      <div className="cl-marco" ref={marco}>
        <div className="cl-lienzo" style={{ width: ANCHO * escala, height: ALTO * escala }}>
          <section className={`cl-escenario${d.roja ? " roja" : ""}`} style={{ transform: `scale(${escala})` }}
            aria-roledescription="diapositiva" aria-label={`${i + 1} de ${lista.length}: ${d.corto}`}>
            {!d.roja && <div className="cl-franja" />}
            {d.titulo && (
              <header className="cl-cabeza">
                <p className="cl-ante">{d.ante}</p>
                <h2 className="cl-titulo">{d.titulo}</h2>
              </header>
            )}
            <div key={d.id} className={`cl-cuerpo${d.titulo ? "" : " pleno"}`}>{d.render(pos.paso)}</div>
            {!d.roja && (
              <footer className="cl-pie">
                <span>El miedo que no baja · The data squad · Bogotá DataJam 5</span>
                <span>{d.profundizar ? "Tecla D: ¿cómo lo sabemos?" : ""}</span>
              </footer>
            )}
            {d.profundizar && (
              <aside className={`cl-prof${prof ? " si" : ""}`} aria-hidden={!prof}>
                <p className="cl-ante">¿Cómo lo sabemos?</p>
                {d.profundizar}
                <button className="salir" style={{ justifySelf: "start" }} onClick={() => setProf(false)} tabIndex={prof ? 0 : -1}>Cerrar (Esc)</button>
              </aside>
            )}
          </section>
        </div>
        {notas && <div className="notas-pres cl-notas"><b>{d.quien} · {d.tiempo}:</b> {d.nota}</div>}
      </div>
      {!captura && <nav className="controles-pres" aria-label="Controles de la presentación">
        <button className="salir" onClick={retroceder} aria-label="Anterior">←</button>
        <button className="salir" onClick={avanzar} aria-label="Siguiente">→</button>
        <span className="mono" style={{ whiteSpace: "nowrap" }}>{i + 1}/{lista.length}</span>
        <div className="cl-prog" aria-hidden="true">
          {lista.map((x, k) => (
            <button key={x.id} title={x.corto} tabIndex={-1} onClick={() => setPos({ i: k, paso: 0 })}>
              <i style={{ width: `${k < i ? 100 : k > i ? 0 : ((pos.paso + 1) / x.pasos) * 100}%` }} />
            </button>
          ))}
        </div>
        <div className="segmentado cl-modo" role="group" aria-label="Modo">
          <button aria-pressed={modo === "pitch"} onClick={() => cambiarModo("pitch")}>Pitch 6 min</button>
          <button aria-pressed={modo === "clase"} onClick={() => cambiarModo("clase")}>Clase completa</button>
        </div>
        <button className={`reloj${estadoReloj}`} onClick={() => setInicio(inicio === null ? Date.now() : null)}
          title="Iniciar o reiniciar el cronómetro" style={{ border: 0, cursor: "pointer", font: "inherit" }}>
          {inicio === null ? (modo === "pitch" ? "6:00 ▶" : "0:00 ▶") : mmss(reloj)}
        </button>
        <button className="salir" onClick={() => setNotas((v) => !v)} aria-pressed={notas}>Notas (N)</button>
        <button className="salir" onClick={() => setProf((v) => !v)} aria-pressed={prof} disabled={!d.profundizar}
          style={{ opacity: d.profundizar ? 1 : 0.4 }}>¿Cómo lo sabemos? (D)</button>
        <button className="salir" onClick={() => document.documentElement.requestFullscreen?.().catch(() => {})} aria-label="Pantalla completa" title="Pantalla completa (F)">⛶</button>
        <Link className="salir" href="/" style={{ textDecoration: "none" }}>Salir</Link>
      </nav>}
    </div>
  );
}
