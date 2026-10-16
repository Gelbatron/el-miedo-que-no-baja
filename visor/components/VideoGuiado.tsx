"use client";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

type Palabra = { t: number; w: string };
type Frase = { cap: number; ini: number; fin: number; palabras: Palabra[] };
export type Capitulo = {
  id: string; titulo: string; ini: number; fin: number; resumen: string; datos: string[]; fuentes: string;
  enlace: [string, string]; imagen: string;
};
export type DatosVideo = { video: string; poster: string; duracion: number; capitulos: Capitulo[]; frases: Frase[] };

const mmss = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

/** Video con capítulos, explicación de cada parte y transcripción que sigue la voz palabra por palabra. */
export function VideoGuiado({ datos }: { datos: DatosVideo }) {
  const video = useRef<HTMLVideoElement>(null);
  const lista = useRef<HTMLDivElement>(null);
  const tocado = useRef(0); // último momento en que la persona movió la transcripción a mano
  const [t, setT] = useState(0);
  const caps = datos.capitulos;
  const cap = Math.max(0, caps.findLastIndex((c) => c.ini <= t + 0.05));
  const ultima = datos.frases.findLastIndex((f) => f.ini <= t + 0.05);
  const frase = ultima >= 0 && datos.frases[ultima].cap === cap ? ultima : datos.frases.findIndex((f) => f.cap === cap);
  const actual = caps[cap];
  const [animar, setAnimar] = useState(false); // la primera vista llega quieta; las siguientes entran con transición
  useEffect(() => { const id = setTimeout(() => setAnimar(true), 600); return () => clearTimeout(id); }, []);

  // tiempo del video: con requestAnimationFrame mientras suena (timeupdate llega solo 4 veces por segundo)
  useEffect(() => {
    const v = video.current;
    if (!v) return;
    let id = 0;
    const paso = () => { setT(v.currentTime); if (!v.paused) id = requestAnimationFrame(paso); };
    const arrancar = () => { cancelAnimationFrame(id); id = requestAnimationFrame(paso); };
    const leer = () => setT(v.currentTime);
    v.addEventListener("play", arrancar);
    v.addEventListener("seeked", leer);
    v.addEventListener("timeupdate", leer);
    return () => { cancelAnimationFrame(id); v.removeEventListener("play", arrancar); v.removeEventListener("seeked", leer); v.removeEventListener("timeupdate", leer); };
  }, []);

  // enlace directo: /video#c3 abre en el capítulo 3; /video#t95, en el segundo 95
  useEffect(() => {
    const v = video.current;
    const m = window.location.hash.match(/^#(c|t)(\d+)$/);
    if (!v || !m) return;
    const s = m[1] === "c" ? caps[Math.min(caps.length, Math.max(1, Number(m[2]))) - 1].ini + 0.7 : Number(m[2]);
    setT(s);
    const fijar = () => { v.currentTime = s; };
    if (v.readyState >= 1) fijar(); else v.addEventListener("loadedmetadata", fijar, { once: true });
  }, [caps]);

  // la transcripción acompaña a la voz, salvo que la persona la esté leyendo por su cuenta
  useEffect(() => {
    const caja = lista.current;
    const el = caja?.querySelector<HTMLElement>(`[data-frase="${frase}"]`);
    if (!caja || !el || Date.now() - tocado.current < 5000) return;
    const arriba = el.offsetTop - caja.offsetTop - caja.clientHeight * 0.3;
    caja.scrollTo({ top: Math.max(0, arriba), behavior: "smooth" });
  }, [frase]);

  const ir = useCallback((s: number) => {
    const v = video.current;
    if (!v) return;
    v.currentTime = s;
    setT(s);
    v.play().catch(() => {});
    const r = v.getBoundingClientRect();
    if (r.top < 0 || r.bottom > window.innerHeight) v.scrollIntoView({ behavior: "smooth", block: "center" });
  }, []);

  const avance = (c: Capitulo) => Math.min(1, Math.max(0, (t - c.ini) / (c.fin - c.ini)));

  return (
    <>
      <section className="vg">
        <div className="vg-izq">
          <div className="vg-marco">
            <video ref={video} src={datos.video} poster={datos.poster} controls playsInline preload="metadata"
              aria-label="Video: El miedo que no baja, lo que hay detrás de las cifras de seguridad" />
          </div>
          <div className="vg-capbar" role="tablist" aria-label="Capítulos del video">
            {caps.map((c, k) => (
              <button key={c.id} role="tab" aria-selected={k === cap} className={`vg-seg${k === cap ? " act" : ""}${k < cap ? " visto" : ""}`}
                style={{ flexGrow: c.fin - c.ini }} onClick={() => ir(c.ini + 0.25)} title={`${k + 1}. ${c.titulo} · ${mmss(c.ini)}`}>
                <i style={{ transform: `scaleX(${k < cap ? 1 : k === cap ? avance(c) : 0})` }} />
                <span>{k + 1}</span>
              </button>
            ))}
          </div>
          <article key={actual.id} className={`vg-explica tarjeta${animar ? " vg-anim" : ""}`} aria-live="polite">
            <div className="vg-cab">
              <span className="antetitulo">Capítulo {cap + 1} de {caps.length} · {mmss(actual.ini)}</span>
              <div className="vg-nav">
                <button className="vg-flecha" onClick={() => ir(caps[Math.max(0, cap - 1)].ini + 0.25)} disabled={cap === 0} aria-label="Capítulo anterior">←</button>
                <button className="vg-flecha" onClick={() => ir(caps[Math.min(caps.length - 1, cap + 1)].ini + 0.25)} disabled={cap === caps.length - 1} aria-label="Capítulo siguiente">→</button>
              </div>
            </div>
            <h2>{actual.titulo}</h2>
            <p className="vg-resumen">{actual.resumen}</p>
            <ul className="vg-datos">{actual.datos.map((d) => <li key={d}>{d}</li>)}</ul>
            <p className="vg-fuentes"><b>Fuentes:</b> {actual.fuentes}</p>
            <Link className="vg-mas" href={actual.enlace[0]}>{actual.enlace[1]} →</Link>
          </article>
        </div>

        <aside className="vg-trans tarjeta" aria-label="Transcripción">
          <div className="vg-trans-cab"><b>Transcripción</b><span>Toca una frase para ir a ese momento</span></div>
          <div className="vg-lista" ref={lista} onWheel={() => { tocado.current = Date.now(); }} onTouchMove={() => { tocado.current = Date.now(); }}>
            {caps.map((c, k) => (
              <div key={c.id} className={`vg-grupo${k === cap ? " act" : ""}`}>
                <button className="vg-gt" onClick={() => ir(c.ini + 0.25)}><span>{k + 1}</span>{c.titulo}<em>{mmss(c.ini)}</em></button>
                {datos.frases.map((f, i) => f.cap !== k ? null : (
                  <button key={i} data-frase={i} className={`vg-frase${i === frase ? " act" : ""}${i < frase ? " dicha" : ""}`} onClick={() => ir(f.ini)}>
                    {f.palabras.map((p, j) => (
                      <span key={j} className={i === frase && p.t <= t + 0.03 ? "vg-dicha" : undefined}>{p.w} </span>
                    ))}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </aside>
      </section>

      <section className="vg-caps" aria-label="Capítulos">
        {caps.map((c, k) => (
          <button key={c.id} className={`vg-carta${k === cap ? " act" : ""}`} onClick={() => ir(c.ini + 0.25)}>
            <span className="vg-img"><img src={c.imagen} alt="" loading="lazy" /><em>{mmss(c.ini)}</em></span>
            <span className="vg-ct"><b>{k + 1}. {c.titulo}</b><span>{c.resumen}</span></span>
          </button>
        ))}
      </section>
    </>
  );
}
