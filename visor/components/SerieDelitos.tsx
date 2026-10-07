"use client";
import { useState } from "react";
import { D, fmt } from "@/lib/datos";
import { Lineas } from "./Graficos";
import { BANDA_PANDEMIA } from "@/lib/historia";

const TIPOS = Array.from(new Set(D.serie_delitos.map((f) => `${f.codigo}|${f.tipo}`))).map((s) => s.split("|") as [string, string]);
const COLORES = ["var(--registro)", "var(--percepcion)", "var(--mujeres)", "var(--hombres)"];

export function SerieDelitos() {
  const [sel, setSel] = useState<string[]>(["HP", "HR", "VI", "DS"]);
  const [modo, setModo] = useState<"indice" | "casos">("indice");
  const series = sel.slice(0, 4).map((cod, i) => {
    const f = D.serie_delitos.filter((x) => x.codigo === cod).sort((a, b) => a.anio - b.anio);
    const base = f[0]?.casos ?? 1;
    const nombre = TIPOS.find(([c]) => c === cod)?.[1] ?? cod;
    return {
      nombre, color: COLORES[i],
      puntos: f.map((p) => ({ x: p.anio, y: modo === "indice" ? (p.casos / base) * 100 : p.casos, tip: `<b>${nombre}</b> · ${p.anio}<br>${fmt(p.casos, 0)} casos (ene-ago)<br>Índice ${fmt((p.casos / base) * 100, 0)}<br><small>${p.fuente}</small>` })),
    };
  });
  const alternar = (cod: string) => setSel((s) => (s.includes(cod) ? s.filter((c) => c !== cod) : s.length >= 4 ? [...s.slice(1), cod] : [...s, cod]));
  return (
    <section className="tarjeta">
      <div className="controles">
        <div className="segmentado" role="group" aria-label="Escala">
          <button aria-pressed={modo === "indice"} onClick={() => setModo("indice")}>Índice 2018 = 100</button>
          <button aria-pressed={modo === "casos"} onClick={() => setModo("casos")}>Casos</button>
        </div>
        <span className="nota">Elige hasta cuatro delitos:</span>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {TIPOS.map(([c, n]) => (
          <button key={c} onClick={() => alternar(c)} aria-pressed={sel.includes(c)} className="pastilla"
            style={{ cursor: "pointer", borderColor: sel.includes(c) ? COLORES[sel.indexOf(c)] : undefined, color: sel.includes(c) ? "var(--tinta)" : undefined }}>
            {sel.includes(c) && <i style={{ width: 8, height: 8, borderRadius: 4, background: COLORES[sel.indexOf(c)], display: "inline-block" }} />}{n}
          </button>
        ))}
      </div>
      {series.length > 0 && <Lineas series={series} bandas={[BANDA_PANDEMIA]} base={modo === "indice" ? 100 : undefined} ymax={modo === "indice" ? 200 : undefined} unidad={modo === "indice" ? "" : "casos"} />}
      <p className="nota">Hurto a personas, residencias y automotores: registro de la Policía (SIEDCO), porque la capa SCJ cambia de escala en 2023. Bicicletas: capa SCJ, sin serie externa para validarla.
        Comercio, celulares y motocicletas no se muestran: desde 2023 esas columnas de la capa no coinciden con su nombre. Lesiones personales no tiene dato de 2026 en la fuente.</p>
    </section>
  );
}
