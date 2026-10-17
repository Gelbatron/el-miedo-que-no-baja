"use client";
import { useMemo, useState } from "react";
import { D, R, fmt, signo } from "@/lib/datos";
import { C, percentil, prob } from "@/lib/clase";
import { Mapa } from "@/components/Mapa";
import { Ap, Interruptor, lin, useConteo, useListo } from "./piezas";

const AME = Object.fromEntries(D.ame.m_hechos.map((f) => [f.variable, f]));
const AUC = Object.fromEntries(D.auc.map((f) => [f.bloque, f.auc * 100]));

/* ---------- 7 · Dos vecinos iguales ---------- */
export function Vecinos({ paso }: { paso: number }) {
  const ref = C.logit.referencia, rg = C.logit.rangos_localidad;
  const [mujer, setMujer] = useState(1);
  const [hurto, setHurto] = useState(ref.hurtos_100k_miles);
  const [homi, setHomi] = useState(ref.homicidios_100k);
  const [atracos, setAtracos] = useState(false);
  const [conflictos, setConflictos] = useState(0);
  const [acoso, setAcoso] = useState(false);
  const base = prob({ ...ref, mujer });
  const p = prob({ ...ref, mujer, hurtos_100k_miles: hurto, homicidios_100k: homi, parque_atracos: atracos ? 1 : 0, conflictos_vecinos: conflictos / 6, presencio_acoso: acoso ? 1 : 0 });
  const d = p - base;
  const p0 = prob(ref);
  const hMin = prob({ ...ref, hurtos_100k_miles: rg.hurtos_100k_miles[0] }), hMax = prob({ ...ref, hurtos_100k_miles: rg.hurtos_100k_miles[1] });
  const conAtracos = prob({ ...ref, parque_atracos: 1 }) - p0, conConf = prob({ ...ref, conflictos_vecinos: 1 }) - p0;
  const colorD = Math.abs(d) < 1 ? "var(--tinta-3)" : d > 0 ? "var(--percepcion-texto)" : "var(--registro-texto)";
  return (
    <div style={{ display: "grid", gridTemplateColumns: "560px 1fr", gap: 44, height: "100%" }}>
      <div style={{ display: "grid", gap: 14, alignContent: "start" }}>
        <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--tinta-3)" }}>
          <span className="cl-ante" style={{ color: "var(--tinta-2)" }}>La persona</span>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <div className="segmentado" role="group" aria-label="Sexo">
              <button aria-pressed={mujer === 1} onClick={() => setMujer(1)}>Mujer</button>
              <button aria-pressed={mujer === 0} onClick={() => setMujer(0)}>Hombre</button>
            </div>
            <span className="cl-chip">{ref.edad} años</span>
            <span className="cl-chip">estrato {ref.estrato}</span>
            <span className="cl-chip">{ref.arrienda ? "vive en arriendo" : "vivienda propia"}</span>
          </div>
        </div>
        <div className={`cl-tarjeta${paso >= 1 ? "" : " cl-desact"}`} style={{ borderLeft: "6px solid var(--registro)" }}>
          <span className="cl-ante" style={{ color: "var(--registro-texto)" }}>Delito registrado en su localidad (SCJ)</span>
          <label className="cl-control">
            <span>Hurtos: <b>{fmt(hurto * 1000, 0)}</b> por 100.000 hab.</span>
            <input className="cl-rango" type="range" min={rg.hurtos_100k_miles[0]} max={rg.hurtos_100k_miles[1]} step={0.05} value={hurto} onChange={(e) => setHurto(Number(e.target.value))} />
          </label>
          <label className="cl-control">
            <span>Homicidios: <b>{fmt(homi, 1)}</b> por 100.000 hab.</span>
            <input className="cl-rango" type="range" min={rg.homicidios_100k[0]} max={rg.homicidios_100k[1]} step={0.1} value={homi} onChange={(e) => setHomi(Number(e.target.value))} />
          </label>
        </div>
        <div className={`cl-tarjeta${paso >= 2 ? "" : " cl-desact"}`} style={{ borderLeft: "6px solid var(--percepcion)" }}>
          <span className="cl-ante" style={{ color: "var(--percepcion-texto)" }}>Lo que pasa en su barrio (Bienal)</span>
          <Interruptor etiqueta="Ve atracos en el parque más cercano" valor={atracos} onCambio={setAtracos} />
          <label className="cl-control">
            <span>Conflictos entre vecinos: <b>{conflictos} de 6</b> situaciones</span>
            <input className="cl-rango" type="range" min={0} max={6} step={1} value={conflictos} onChange={(e) => setConflictos(Number(e.target.value))} />
          </label>
          <Interruptor etiqueta="Presenció acoso a mujeres" valor={acoso} onCambio={setAcoso} />
        </div>
      </div>
      <div style={{ display: "grid", gap: 16, alignContent: "start" }}>
        <div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 16 }}>
            <span className="cl-num" style={{ fontSize: 92, color: "var(--percepcion-texto)" }}>{fmt(p, 0)} %</span>
            <span className="cl-chip" style={{ fontSize: 20, color: colorD, transition: "color .3s" }}>{signo(d, 1)} pp</span>
          </div>
          <p className="cl-txt" style={{ fontSize: 17 }}>probabilidad de que sienta insegura su zona (modelo logit, {fmt(C.logit.n, 0)} adultos de la Bienal)</p>
          <svg className="cl-g" viewBox="0 0 560 60" role="img" aria-label={`Probabilidad ${fmt(p, 0)} %`} style={{ marginTop: 8 }}>
            <rect x={0} y={14} width={560} height={22} rx={11} fill="var(--superficie-2)" />
            <rect x={0} y={14} width={5.6 * p} height={22} rx={11} fill="var(--percepcion)" style={{ transition: "width .45s ease" }} />
            <line x1={5.6 * base} x2={5.6 * base} y1={6} y2={44} stroke="var(--tinta)" strokeWidth={2.5} />
            <text x={5.6 * base} y={58} textAnchor="middle" style={{ fontSize: 13, fill: "var(--tinta-2)" }}>punto de partida {fmt(base, 0)} %</text>
          </svg>
        </div>
        <p className="cl-txt">El modelo compara a personas <b>iguales en todo menos en una cosa</b>. Esta vecina parte de {fmt(p0, 0)} %.</p>
        <Ap si={paso >= 1}>
          <p className="cl-txt">Del menor al mayor hurto registrado entre localidades: {fmt(hMin, 1)} % → {fmt(hMax, 1)} %. <b>Casi nada.</b> Los homicidios sí pesan algo: {signo(AME.homicidios_100k.ame_pp, 1)} pp por cada homicidio más por 100 mil.</p>
        </Ap>
        <Ap si={paso >= 2}>
          <p className="cl-txt">Ver atracos en el parque le suma <b style={{ color: "var(--percepcion-texto)" }}>{signo(conAtracos, 0)} pp</b>; los conflictos vecinales, hasta <b style={{ color: "var(--percepcion-texto)" }}>{signo(conConf, 0)}</b>.</p>
        </Ap>
        <Ap si={paso >= 2} retraso={300}><p className="cl-clave">El barrio se siente por lo que pasa en él.</p></Ap>
      </div>
    </div>
  );
}

/* ---------- 8 · ¿Y si fue suerte? 300 repeticiones ---------- */
function apilar(v: number[], ancho = 0.5) {
  const cuenta = new Map<number, number>();
  return v.map((x) => {
    const b = Math.round(x / ancho);
    const k = cuenta.get(b) ?? 0;
    cuenta.set(b, k + 1);
    return { x: b * ancho, nivel: k };
  });
}
export function Repeticiones({ paso }: { paso: number }) {
  const listo = useListo();
  const A = C.bootstrap.parque_atracos, Hh = C.bootstrap.hurtos_100k_miles;
  const nA = useConteo(listo && paso >= 0, A.length), nH = useConteo(paso >= 1, Hh.length);
  const W = 1168, H = 432, X = lin(-8, 20, 300, W - 20);
  const filas = [
    { clave: "parque_atracos", nombre: "Ver atracos en el parque más cercano", v: A, n: nA, base: 196, color: "var(--percepcion)", txt: "var(--percepcion-texto)" },
    { clave: "hurtos_100k_miles", nombre: "Hurto registrado en la localidad (+1.000 por 100 mil)", v: Hh, n: nH, base: 392, color: "var(--registro)", txt: "var(--registro-texto)" },
  ];
  const pilas = useMemo(() => filas.map((f) => apilar(f.v)), []); // eslint-disable-line react-hooks/exhaustive-deps
  const maxNivel = Math.max(...pilas.flat().map((p) => p.nivel)) + 1;
  const dy = Math.min(7.4, 172 / maxNivel), radio = Math.min(3.3, dy / 2 - 0.25);
  return (
    <div style={{ display: "grid", gap: 8, height: "100%", alignContent: "start" }}>
      <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Distribución de 300 réplicas bootstrap de dos efectos">
        {[-5, 0, 5, 10, 15, 20].map((t) => (
          <g key={t}>
            <line x1={X(t)} x2={X(t)} y1={10} y2={H - 22} className={t === 0 ? "eje" : "grid"} strokeWidth={t === 0 ? 2.5 : 1} />
            <text x={X(t)} y={H - 4} className="tick" textAnchor="middle">{t > 0 ? `+${t}` : t === 0 ? "0" : `−${-t}`} pp</text>
          </g>
        ))}
        <text x={X(0) + 8} y={22} style={{ fontSize: 14, fill: "var(--tinta-2)", fontWeight: 600 }}>0 = no cambia nada</text>
        {filas.map((f, k) => {
          const lo = percentil(f.v, 0.025), hi = percentil(f.v, 0.975), lleno = f.n >= f.v.length, vis = k === 0 || paso >= 1;
          return (
            <g key={f.clave} className={`cl-sap${vis ? " si" : ""}`}>
              <text x={0} y={f.base - 112} style={{ fontSize: 17, fontWeight: 700, fill: f.txt }}>{f.nombre}</text>
              <text x={0} y={f.base - 88} style={{ fontSize: 15, fill: "var(--tinta-2)" }}>Estimación: {signo(AME[f.clave].ame_pp, 1)} pp</text>
              <text x={0} y={f.base - 66} style={{ fontSize: 15, fill: "var(--tinta-2)" }}>{fmt(f.n, 0)} de {fmt(f.v.length, 0)} repeticiones</text>
              <line x1={X(-8)} x2={X(20)} y1={f.base} y2={f.base} className="grid" />
              {pilas[k].slice(0, f.n).map((p, j) => <circle key={j} cx={X(p.x)} cy={f.base - 5 - p.nivel * dy} r={radio} fill={f.color} />)}
              <g className={`cl-sap${lleno ? " si" : ""}`}>
                <line x1={X(lo)} x2={X(hi)} y1={f.base + 12} y2={f.base + 12} stroke="var(--tinta)" strokeWidth={3} />
                <line x1={X(lo)} x2={X(lo)} y1={f.base + 5} y2={f.base + 19} stroke="var(--tinta)" strokeWidth={3} />
                <line x1={X(hi)} x2={X(hi)} y1={f.base + 5} y2={f.base + 19} stroke="var(--tinta)" strokeWidth={3} />
                <text x={0} y={f.base - 40} style={{ fontSize: 16, fill: "var(--tinta)", fontWeight: 700 }}>
                  95 %: {signo(lo, 1)} a {signo(hi, 1)} pp {lo > 0 || hi < 0 ? "· no toca el cero" : "· cruza el cero"}
                </text>
              </g>
            </g>
          );
        })}
      </svg>
      <p className="cl-txt" style={{ fontSize: 18 }}>
        Cada punto es el mismo modelo estimado con un sorteo distinto de las 19 localidades. <b>Si la nube no toca el cero, el efecto no depende de qué localidades entraron.</b>
      </p>
    </div>
  );
}

/* ---------- 9 · ¿El modelo adivina? (AUC) ---------- */
export function Prediccion({ paso }: { paso: number }) {
  const filas = [
    { n: "Lanzar una moneda", v: 50, c: "var(--neutro)", desde: 0 },
    { n: "Perfil: sexo, edad, estrato, arriendo", v: AUC["Perfil (sexo, edad, estrato, tenencia)"], c: "var(--tinta-3)", desde: 0 },
    { n: "+ delito registrado de su localidad", v: AUC["Perfil + delito registrado"], c: "var(--registro)", desde: 1 },
    { n: "+ hechos de su entorno", v: AUC["Perfil + hechos del entorno"], c: "var(--percepcion)", desde: 2 },
    { n: "Todo, con la calificación del entorno", v: AUC["Todo"], c: "var(--rojo)", desde: 3 },
  ];
  const W = 1168, fila = 64, H = filas.length * fila + 40, X = lin(45, 85, 400, W - 110);
  return (
    <div style={{ display: "grid", gap: 14, alignContent: "start" }}>
      <p className="cl-txt">Le damos al modelo dos personas al azar: una que siente insegura su zona y otra que no. <b>¿Cuántas veces de cada 100 acierta cuál es cuál?</b> Medido con personas que el modelo no vio (validación cruzada).</p>
      <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Aciertos de cada 100 parejas por bloque de variables">
        {[50, 60, 70, 80].map((t) => (
          <g key={t}><line x1={X(t)} x2={X(t)} y1={0} y2={H - 26} className={t === 50 ? "eje" : "grid"} /><text x={X(t)} y={H - 6} className="tick" textAnchor="middle">{t}</text></g>
        ))}
        {filas.map((f, k) => {
          const y = 14 + k * fila, si = paso >= f.desde;
          return (
            <g key={f.n} className={`cl-sap${si ? " si" : ""}`}>
              <text x={385} y={y + 27} textAnchor="end" style={{ fontSize: 18, fill: "var(--tinta)", fontWeight: k === 2 ? 700 : 500 }}>{f.n}</text>
              <rect x={X(45)} y={y + 8} height={30} rx={6} fill={f.c} width={si ? X(f.v) - X(45) : 0} style={{ transition: "width .9s ease" }} />
              <text x={X(f.v) + 12} y={y + 30} style={{ fontSize: 20, fontWeight: 800, fill: "var(--tinta)", fontFamily: "var(--f-display)" }}>{fmt(f.v, 1)}</text>
            </g>
          );
        })}
      </svg>
      <Ap si={paso >= 1}>
        <p className="cl-clave" style={{ fontSize: 22 }}>
          Sumar el delito registrado mejora {fmt(AUC["Perfil + delito registrado"] - AUC["Perfil (sexo, edad, estrato, tenencia)"], 1)} aciertos de cada 100.
          {paso >= 2 ? ` Sumar el entorno, ${fmt(AUC["Perfil + hechos del entorno"] - AUC["Perfil (sexo, edad, estrato, tenencia)"], 1)}.` : ""}
        </p>
      </Ap>
    </div>
  );
}

/* ---------- 10 · Hallazgo 3: género ---------- */
export function Genero({ paso }: { paso: number }) {
  const s = R.emv_por_sexo;
  const filas: [string, { mujeres: number; hombres: number }, number][] = [
    ["Fue víctima de un delito", s.victima, 0], ["Teme el acoso sexual", s.teme_acoso_sexual, 1],
    ["Evita salir de noche", s.no_sale_noche, 1], ["Se siente insegura/o en su barrio", s.barrio_inseguro, 1],
  ];
  const W = 640, fila = 74, H = filas.length * fila + 40, X = lin(0, 100, 250, W - 30);
  const mujer = (k: "teme_acoso_sexual" | "barrio_inseguro" | "no_sale_noche") => D.emv_genero[k].find((f) => f.variable === "mujer")!;
  const efectos: [string, ReturnType<typeof mujer>][] = [["Temor al acoso sexual", mujer("teme_acoso_sexual")], ["Insegura en su barrio", mujer("barrio_inseguro")], ["Evita salir de noche", mujer("no_sale_noche")]];
  const XE = lin(0, 25, 0, 180);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "640px 1fr", gap: 44, height: "100%" }}>
      <div style={{ display: "grid", gap: 6, alignContent: "start" }}>
        <div style={{ display: "flex", gap: 18, fontSize: 16, color: "var(--tinta-2)" }}>
          <span><b style={{ color: "var(--mujeres)" }}>■</b> Mujeres</span><span><b style={{ color: "var(--hombres)" }}>●</b> Hombres</span>
          <span>% de adultos en Bogotá · EMV 2024</span>
        </div>
        <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Mujeres frente a hombres">
          {[0, 25, 50, 75, 100].map((t) => <g key={t}><line x1={X(t)} x2={X(t)} y1={0} y2={H - 26} className="grid" /><text x={X(t)} y={H - 6} className="tick" textAnchor="middle">{t} %</text></g>)}
          {filas.map(([n, v, desde], k) => {
            const y = 30 + k * fila, si = paso >= desde, xm = X(v.mujeres), xh = X(v.hombres);
            return (
              <g key={n} className={`cl-sap${si ? " si" : ""}`}>
                <text x={236} y={y + 6} textAnchor="end" style={{ fontSize: 17, fill: "var(--tinta)", fontWeight: k === 0 ? 700 : 500 }}>{n}</text>
                <line x1={Math.min(xm, xh)} x2={Math.max(xm, xh)} y1={y} y2={y} stroke="var(--linea)" strokeWidth={8} strokeLinecap="round" />
                <circle cx={xh} cy={y} r={10} fill="var(--hombres)" />
                <rect x={xm - 10} y={y - 10} width={20} height={20} rx={3} fill="var(--mujeres)" />
                <text x={xm + (xm > xh ? 18 : -18)} y={y + 6} textAnchor={xm > xh ? "start" : "end"} style={{ fontSize: 16, fontWeight: 700, fill: "var(--mujeres)" }}>{fmt(v.mujeres)}</text>
                <text x={xh + (xh > xm ? 18 : -18)} y={y + 6} textAnchor={xh > xm ? "start" : "end"} style={{ fontSize: 16, fontWeight: 700, fill: "var(--hombres)" }}>{fmt(v.hombres)}</text>
              </g>
            );
          })}
        </svg>
      </div>
      <div style={{ display: "grid", gap: 16, alignContent: "start" }}>
        <Ap si={paso >= 0}><p className="cl-txt">Ellas dicen haber sido víctimas <b>menos</b> que ellos: {fmt(s.victima.mujeres)} % frente a {fmt(s.victima.hombres)} %.</p></Ap>
        <Ap si={paso >= 1}><p className="cl-txt">…pero <b>temen más</b> el acoso y <b>evitan más</b> salir de noche.</p></Ap>
        <Ap si={paso >= 2}>
          <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--mujeres)" }}>
            <span className="cl-ante" style={{ color: "var(--mujeres)" }}>Comparando iguales: misma edad, estrato y victimización</span>
            <svg className="cl-g" viewBox="0 0 440 150" role="img" aria-label="Efecto de ser mujer con intervalo de confianza">
              {efectos.map(([n, e], k) => {
                const y = 26 + k * 46;
                return (
                  <g key={n}>
                    <text x={0} y={y + 5} style={{ fontSize: 15, fill: "var(--tinta)" }}>{n}</text>
                    <line x1={180 + XE(e.ic_inf)} x2={180 + XE(Math.min(e.ic_sup, 25))} y1={y} y2={y} stroke="var(--mujeres)" strokeWidth={4} strokeLinecap="round" opacity={0.5} />
                    <circle cx={180 + XE(e.ame_pp)} cy={y} r={7} fill="var(--mujeres)" />
                    <text x={440} y={y + 6} textAnchor="end" style={{ fontSize: 17, fontWeight: 800, fill: "var(--mujeres)", fontFamily: "var(--f-display)" }}>{signo(e.ame_pp, 1)} pp</text>
                  </g>
                );
              })}
            </svg>
          </div>
        </Ap>
        <Ap si={paso >= 2} retraso={300}><p className="cl-clave">El costo del miedo se paga en autonomía.</p></Ap>
      </div>
    </div>
  );
}

/* ---------- 11 · Simulador ---------- */
type Esc = (typeof D.escenarios)[number];
const interp = (e: Esc, f1: number, f2: number) => (1 - f1) * (1 - f2) * e.p00 + f1 * (1 - f2) * e.p10 + (1 - f1) * f2 * e.p01 + f1 * f2 * e.p11;
export function SimuladorClase() {
  const [alumbrado, setAlumbrado] = useState(50);
  const [parques, setParques] = useState(50);
  const f1 = alumbrado / 100, f2 = parques / 100;
  const filas = D.escenarios.filter((e) => e.grupo === "total").map((e) => ({ ...e, sim: interp(e, f1, f2) }));
  const bog = filas.find((e) => e.localidad === 0)!;
  const cambio = Object.fromEntries(filas.filter((e) => e.localidad > 0).map((e) => [String(e.localidad), -(e.sim - e.p00)]));
  const adultos: number = R.adultos_urbanos_bienal;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "470px 1fr", gap: 40, height: "100%" }}>
      <div style={{ display: "grid", gap: 16, alignContent: "start" }}>
        <label className="cl-control">
          <span>Zonas donde el alumbrado deja de ser malo: <b>{alumbrado} %</b></span>
          <input className="cl-rango" type="range" min={0} max={100} step={5} value={alumbrado} onChange={(e) => setAlumbrado(Number(e.target.value))} />
        </label>
        <label className="cl-control">
          <span>Parques donde dejan de verse atracos: <b>{parques} %</b></span>
          <input className="cl-rango" type="range" min={0} max={100} step={5} value={parques} onChange={(e) => setParques(Number(e.target.value))} />
        </label>
        <div>
          <span className="cl-num" style={{ fontSize: 84, color: "var(--rojo)" }}>{signo(bog.sim - bog.p00, 1)} pp</span>
          <p className="cl-txt">en Bogotá: {fmt(bog.p00)} % → {fmt(bog.sim)} % siente insegura su zona. Del orden de <b>{fmt((Math.abs(bog.sim - bog.p00) / 100) * adultos / 1000, 0)} mil adultos</b>.</p>
        </div>
        <p className="cl-txt" style={{ fontSize: 15, color: "var(--tinta-3)" }}>Es una sensibilidad del modelo para comparar territorios, no la promesa de un efecto causal. Un piloto con línea base lo confirmaría.</p>
      </div>
      <div>
        <p className="cl-ante" style={{ color: "var(--tinta-2)" }}>Cuánto bajaría en cada localidad (puntos porcentuales)</p>
        <Mapa valores={cambio} tipo="percepcion" unidad="pp menos" dec={1} alto={470} />
      </div>
    </div>
  );
}

/* ---------- 12 · Qué proponemos ---------- */
export function Propuesta({ paso }: { paso: number }) {
  const valores = Object.fromEntries(C.indice.map((f) => [String(f.localidad), f.ibs]));
  const top5 = R.ibs_top5 as string[];
  const bloques: [string, string, string][] = [
    ["Dónde actuar primero", `${top5.slice(0, 4).join(", ")} y ${top5[4]}: donde hay más miedo del que muestran las cifras. La misma regla sirve para las 33 UPL.`, "var(--rojo)"],
    ["Qué arreglar", "Lo que la gente ve en su barrio: parques sin atracos, convivencia entre vecinos y alumbrado. Con las mujeres en el centro: acoso y moverse de noche.", "var(--percepcion)"],
    ["Cómo saber si funciona", "Que la gente se sienta más segura, no solo que bajen las denuncias: el Índice de Brecha cada semestre, encuestas de victimización y el % de mujeres que evita salir de noche.", "var(--registro)"],
  ];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "430px 1fr", gap: 40, height: "100%" }}>
      <div>
        <Mapa valores={valores} tipo="div" unidad="" dec={2} alto={430} />
        <p className="cl-txt" style={{ fontSize: 14 }}>Índice de Brecha 2025. Oro: más miedo del que muestran las cifras.</p>
      </div>
      <div style={{ display: "grid", gap: 16, alignContent: "start" }}>
        {bloques.map(([t, d, c], k) => (
          <Ap key={t} si={paso >= k}>
            <div style={{ display: "grid", gridTemplateColumns: "48px 1fr", gap: 14, alignItems: "start" }}>
              <span style={{ width: 44, height: 44, borderRadius: 999, background: c, display: "grid", placeItems: "center", fontFamily: "var(--f-display)", fontWeight: 800, fontSize: 20, color: "#fff" }}>{k + 1}</span>
              <div><b style={{ fontFamily: "var(--f-display)", fontSize: 22, color: "var(--tinta)" }}>{t}</b><p className="cl-txt" style={{ fontSize: 17 }}>{d}</p></div>
            </div>
          </Ap>
        ))}
        <Ap si={paso >= 2} retraso={350}>
          <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--rojo)" }}>
            <b style={{ fontSize: 20 }}>Todo con datos que el Distrito ya tiene.</b>
            <span className="cl-txt" style={{ fontSize: 15 }}>Y dos que faltan por publicar: alumbrado georreferenciado (el del portal es de 2019) y delitos por UPZ.</span>
          </div>
        </Ap>
      </div>
    </div>
  );
}

/* ---------- 13 · Cierre ---------- */
export function Cierre() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: 48, height: "100%", alignItems: "center" }}>
      <div>
        <p className="cl-ante" style={{ color: "#ffd98a" }}>El miedo que no baja · The data squad</p>
        <p className="cl-heroe" style={{ fontSize: 62, lineHeight: 1.02 }}>Bogotá ya produce los datos para cerrar esta brecha.<br /><span>Hay que validarlos y leerlos juntos.</span></p>
        <div className="cl-raya" />
        <p className="cl-pregunta" style={{ fontSize: 22 }}>Visor, notebook, repositorio, Power BI y Excel: todo reproducible con fuentes públicas.</p>
        <div style={{ display: "flex", gap: 26, marginTop: 18 }}>
          {[["/equipo/brandow.jpg", "Brandow León"], ["/equipo/samuel.jpg", "Samuel Riveros"], ["/equipo/rafael.jpg", "Rafael Londoño"]].map(([f, n]) => (
            <figure key={f} style={{ margin: 0, display: "flex", alignItems: "center", gap: 12 }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={f} alt={n} width={76} height={76} style={{ borderRadius: "50%", border: "3px solid #ffd98a", objectFit: "cover" }} />
              <figcaption style={{ lineHeight: 1.2 }}><b style={{ color: "#fff", fontSize: 17 }}>{n}</b></figcaption>
            </figure>
          ))}
        </div>
        <p style={{ marginTop: 12, color: "#ffd98a", fontSize: 14, letterSpacing: ".1em", textTransform: "uppercase", fontWeight: 700 }}>Estudiantes de Ciencia de Datos</p>
      </div>
      <div style={{ background: "#fff", borderRadius: 16, padding: 16, display: "grid", gap: 8, justifyItems: "center" }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/qr_visor.png" alt="Código QR del visor" width={220} height={220} style={{ imageRendering: "pixelated" }} />
        <span style={{ color: "#1e1e1e", fontSize: 13, fontWeight: 600, whiteSpace: "nowrap" }}>el-miedo-que-no-baja.vercel.app</span>
      </div>
    </div>
  );
}

