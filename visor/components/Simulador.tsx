"use client";
import { useMemo, useState } from "react";
import { D, LOCALIDADES, fmt, signo } from "@/lib/datos";
import { Mapa } from "./Mapa";

type Esc = (typeof D.escenarios)[number];
const interp = (e: Esc, f1: number, f2: number) => (1 - f1) * (1 - f2) * e.p00 + f1 * (1 - f2) * e.p10 + (1 - f1) * f2 * e.p01 + f1 * f2 * e.p11;

export function Simulador() {
  const [alumbrado, setAlumbrado] = useState(50);
  const [parques, setParques] = useState(50);
  const [grupo, setGrupo] = useState<"total" | "mujeres" | "hombres">("total");
  const f1 = alumbrado / 100, f2 = parques / 100;
  const filas = useMemo(() => D.escenarios.filter((e) => e.grupo === grupo).map((e) => ({ ...e, sim: interp(e, f1, f2) })), [grupo, f1, f2]);
  const bog = filas.find((e) => e.localidad === 0)!;
  const locs = filas.filter((e) => e.localidad > 0).sort((a, b) => (a.sim - a.p00) - (b.sim - b.p00));
  const cambio = Object.fromEntries(locs.map((e) => [String(e.localidad), e.sim - e.p00]));
  const adultos: number = D.resumen.adultos_urbanos_bienal;
  return (
    <div className="rejilla" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 360px), 1fr))", alignItems: "start" }}>
      <div className="tarjeta">
        <h3>Escenario</h3>
        <label className="campo" htmlFor="s1">
          <span>Zonas donde el alumbrado deja de ser malo: <b className="num" style={{ color: "var(--tinta)" }}>{alumbrado} %</b></span>
          <input id="s1" type="range" min={0} max={100} step={5} value={alumbrado} onChange={(e) => setAlumbrado(Number(e.target.value))} />
        </label>
        <label className="campo" htmlFor="s2">
          <span>Parques donde dejan de verse atracos: <b className="num" style={{ color: "var(--tinta)" }}>{parques} %</b></span>
          <input id="s2" type="range" min={0} max={100} step={5} value={parques} onChange={(e) => setParques(Number(e.target.value))} />
        </label>
        <div className="segmentado" role="group" aria-label="Grupo">
          {(["total", "mujeres", "hombres"] as const).map((g) => (
            <button key={g} aria-pressed={grupo === g} onClick={() => setGrupo(g)}>{g === "total" ? "Total" : g[0].toUpperCase() + g.slice(1)}</button>
          ))}
        </div>
        <div className="cifra" style={{ marginTop: 8 }}>
          <b className="percepcion">{signo(bog.sim - bog.p00)} pp</b>
          <span>en la probabilidad de sentir insegura la zona en Bogotá ({fmt(bog.p00)} % → {fmt(bog.sim)} %). Del orden de {fmt(Math.abs(bog.sim - bog.p00) / 100 * adultos / 1000, 0)} mil adultos menos.</span>
        </div>
        <p className="nota">
          Cálculo: el modelo logit (hechos del entorno + alumbrado) se evalúa con cada palanca resuelta y se promedia según la cobertura elegida. Es una sensibilidad
          del modelo, útil para comparar territorios, no la promesa de un efecto causal. Un piloto con línea base y grupo de comparación lo confirmaría.
        </p>
      </div>
      <div className="tarjeta" style={{ gridColumn: "span 2", minWidth: 0 }}>
        <h3>Cambio esperado por localidad (puntos porcentuales)</h3>
        <Mapa valores={Object.fromEntries(Object.entries(cambio).map(([k, v]) => [k, -v]))} tipo="percepcion" unidad="pp menos" dec={1} />
        <div className="tabla-wrap" style={{ maxHeight: 300 }}>
          <table>
            <thead><tr><th>Localidad</th><th className="n">Hoy (modelo)</th><th className="n">Escenario</th><th className="n">Cambio</th></tr></thead>
            <tbody>
              {locs.map((e) => (
                <tr key={e.localidad}><td>{LOCALIDADES[e.localidad]}</td><td className="n">{fmt(e.p00)} %</td><td className="n">{fmt(e.sim)} %</td><td className="n"><b>{signo(e.sim - e.p00)} pp</b></td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="nota">El mapa colorea la reducción: más oscuro, más baja la inseguridad percibida. Las localidades con más alumbrado malo y más atracos en parques ganan más.</p>
      </div>
    </div>
  );
}
