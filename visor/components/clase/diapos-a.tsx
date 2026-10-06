"use client";
import { useState } from "react";
import { D, R, fmt, signo } from "@/lib/datos";
import { C } from "@/lib/clase";
import { Ap, Cifra, lin, useListo } from "./piezas";

type Panel = { localidad: number; nombre: string; poblacion: number; zona_insegura: number; delitos_alto_impacto_100k: number; ibs: number };
type Ibs = { localidad: number; nombre: string; ibs: number; ibs_p05: number; ibs_p95: number; prob_top5: number };
type Oculta = { localidad: number; nombre: string; emv_victima: number; victimas_estimadas: number; delitos_registrados: number; razon: number; razon_inf: number; razon_sup: number };
const PANEL = D.panel as unknown as Panel[];
const IBS = D.ibs as unknown as Ibs[];
const OCULTA = D.cifra_oculta as unknown as Oculta[];
const TOP5 = new Set(IBS.slice(0, 5).map((f) => f.localidad));
const zfmt = (t: number) => (t > 0 ? `+${t}` : t === 0 ? "0" : `−${-t}`);

/* ---------- 1 · Portada ---------- */
export function Portada() {
  const { ancho, alto } = D.geo;
  return (
    <div className="cl-portada">
      <div>
        <p className="cl-ante" style={{ color: "#ffd98a" }}>Bogotá DataJam Edición 5 · Seguridad ciudadana con enfoque de género</p>
        <h1 className="cl-heroe">El miedo<br /><span>que no baja</span></h1>
        <div className="cl-raya" />
        <p className="cl-pregunta">¿Por qué la inseguridad percibida no baja cuando el delito registrado sí, y en qué territorios debe intervenir primero el Distrito?</p>
        <p className="cl-equipo"><b>Equipo #16 · The data squad</b><br />Rafael Estiven Londoño Camacho · Brandow Brusly León Rodríguez · Samuel Esteban Riveros Cubides</p>
      </div>
      <svg className="cl-silueta" viewBox={`-4 -4 ${ancho + 8} ${alto + 8}`} role="img" aria-label="Bogotá urbana; en oro, las cinco localidades con mayor Índice de Brecha">
        {D.geo.localidades.map((l) => <path key={l.id} d={l.d} className={TOP5.has(l.id) ? "brilla" : undefined} />)}
      </svg>
    </div>
  );
}

/* ---------- 2 · La paradoja ---------- */
export function Paradoja({ paso }: { paso: number }) {
  const listo = useListo();
  const W = 700, H = 470, ml = 52, mr = 210, mt = 26, mb = 40;
  const X = lin(2018, 2026, ml, W - mr), Y = lin(0, 200, H - mb, mt);
  const indice = (cod: string) => {
    const f = D.serie_delitos.filter((x) => x.codigo === cod).sort((a, b) => a.anio - b.anio);
    return f.map((p) => ({ x: p.anio, y: (p.casos / f[0].casos) * 100, casos: p.casos }));
  };
  const series = [
    { cod: "HP", nombre: "Hurto a personas", color: "var(--registro)", desde: 0 },
    { cod: "VI", nombre: "Violencia intrafamiliar", color: "var(--mujeres)", desde: 1 },
    { cod: "DS", nombre: "Delitos sexuales", color: "var(--vino)", desde: 1 },
  ].map((s) => ({ ...s, puntos: indice(s.cod) }));
  const finales = series.map((s) => ({ s, y: Y(s.puntos[s.puntos.length - 1].y) })).sort((a, b) => a.y - b.y);
  for (let k = 1; k < finales.length; k++) if (finales[k].y - finales[k - 1].y < 22) finales[k].y = finales[k - 1].y + 22;
  const vis = (s: { desde: number }) => listo && paso >= s.desde;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "700px 1fr", gap: 36, height: "100%", alignItems: "start" }}>
      <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Delitos registrados en Bogotá, enero a agosto, índice 2018 = 100">
        <text x={ml} y={12} style={{ fontSize: 14, fill: "var(--tinta-3)" }}>Casos registrados enero-agosto · índice 2018 = 100 · SCJ</text>
        {[0, 50, 100, 150, 200].map((t) => (
          <g key={t}>
            <line x1={ml} x2={W - mr} y1={Y(t)} y2={Y(t)} className={t === 100 ? "eje" : "grid"} />
            <text x={ml - 10} y={Y(t) + 5} className="tick" textAnchor="end">{t}</text>
          </g>
        ))}
        {[2018, 2020, 2022, 2024, 2026].map((a) => <text key={a} x={X(a)} y={H - 12} className="tick" textAnchor="middle">{a}</text>)}
        {series.map((s) => (
          <g key={s.cod}>
            <path pathLength={1} className={`cl-trazo${vis(s) ? " si" : ""}`} fill="none" stroke={s.color} strokeWidth={4.5} strokeLinejoin="round" strokeLinecap="round"
              d={"M" + s.puntos.map((p) => `${X(p.x).toFixed(1)},${Y(p.y).toFixed(1)}`).join("L")} />
            <g className={`cl-sap${vis(s) ? " si" : ""}`} style={{ transitionDelay: vis(s) ? "1.1s" : "0s" }}>
              {s.puntos.map((p) => (
                <circle key={p.x} cx={X(p.x)} cy={Y(p.y)} r={5} fill={s.color} data-tip={`<b>${s.nombre}</b> · ${p.x}<br>${fmt(p.casos, 0)} casos (ene-ago)`} />
              ))}
            </g>
          </g>
        ))}
        {finales.map(({ s, y }) => (
          <text key={s.cod} x={X(2026) + 14} y={y + 5} className={`etq cl-sap${vis(s) ? " si" : ""}`} style={{ transitionDelay: vis(s) ? "1.3s" : "0s" }}>
            {s.nombre} {fmt(s.puntos[s.puntos.length - 1].y, 0)}
          </text>
        ))}
      </svg>
      <div style={{ display: "grid", gap: 12 }}>
        <Ap si={paso >= 0}>
          <Cifra ante="El hurto baja muchísimo · SCJ" valor={`${signo(R.hurto_personas.cambio_pct, 0)} %`} color="var(--registro-texto)" tam={46}
            texto={<>hurto a personas: {fmt(R.hurto_personas["2019"], 0)} casos en 2019, {fmt(R.hurto_personas["2026"], 0)} en 2026.</>} />
        </Ap>
        <Ap si={paso >= 1}>
          <div className="cl-tarjeta" style={{ borderTop: "6px solid var(--mujeres)", gap: 2 }}>
            <span className="cl-ante" style={{ color: "var(--mujeres)" }}>Pero los hechos violentos van al revés</span>
            <div style={{ display: "flex", gap: 22, alignItems: "baseline" }}>
              <span><span className="cl-num" style={{ fontSize: 36, color: "var(--mujeres)" }}>{signo(R.vif_cambio_pct_2018_2026, 0)} %</span><br /><span style={{ fontSize: 15 }}>violencia intrafamiliar</span></span>
              <span><span className="cl-num" style={{ fontSize: 36, color: "var(--vino)" }}>{signo(R.delitos_sexuales_cambio_pct_2018_2026, 0)} %</span><br /><span style={{ fontSize: 15 }}>delitos sexuales</span></span>
              <span style={{ fontSize: 13, color: "var(--tinta-3)", alignSelf: "end" }}>2018-2026</span>
            </div>
          </div>
        </Ap>
        <Ap si={paso >= 2}>
          <Cifra ante="Y la gente no lo siente · Bienal 2025" valor={`${fmt(R.ciudad_insegura_pct, 0)} %`} color="var(--percepcion-texto)" tam={46}
            texto={<>dice que Bogotá es insegura: 3 de cada 4.</>} />
        </Ap>
        <Ap si={paso >= 2} retraso={350}><p className="cl-clave" style={{ fontSize: 22 }}>En el papel la ciudad mejora, pero la gente no lo siente.</p></Ap>
      </div>
    </div>
  );
}

/* ---------- 3 · Si el miedo siguiera al delito ---------- */
const ETQ_T: Record<number, { dx: number; dy: number; a: "start" | "middle" | "end" }> = {
  5: { dx: 0, dy: -17, a: "middle" }, 19: { dx: 12, dy: -12, a: "start" }, 17: { dx: 0, dy: 28, a: "middle" },
  3: { dx: 0, dy: 28, a: "middle" }, 14: { dx: 14, dy: 5, a: "start" }, 13: { dx: -12, dy: 22, a: "end" }, 1: { dx: 0, dy: 28, a: "middle" },
};
export function Termometros({ paso }: { paso: number }) {
  const W = 720, H = 500, ml = 78, mr = 24, mt = 20, mb = 64;
  const lx0 = Math.log10(900), lx1 = Math.log10(13000);
  const X = (v: number) => ml + ((Math.log10(v) - lx0) / (lx1 - lx0)) * (W - ml - mr);
  const Y = lin(15, 75, H - mb, mt);
  const v = D.validaciones.find((f) => f.prueba.startsWith("Zona insegura (Bienal) vs delitos"))!;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "720px 1fr", gap: 36, height: "100%", alignItems: "center" }}>
      <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Miedo frente a delito registrado por localidad">
        {[20, 30, 40, 50, 60, 70].map((t) => (
          <g key={t}><line x1={ml} x2={W - mr} y1={Y(t)} y2={Y(t)} className="grid" /><text x={ml - 10} y={Y(t) + 5} className="tick" textAnchor="end">{t} %</text></g>
        ))}
        {[1000, 2000, 5000, 10000].map((t) => (
          <g key={t}><line x1={X(t)} x2={X(t)} y1={mt} y2={H - mb} className="grid" /><text x={X(t)} y={H - mb + 22} className="tick" textAnchor="middle">{fmt(t, 0)}</text></g>
        ))}
        <text x={(ml + W - mr) / 2} y={H - 8} textAnchor="middle" style={{ fontSize: 15 }}>Delitos de alto impacto registrados por 100.000 hab. (SCJ, ene-ago 2025) · escala log</text>
        <text transform={`translate(20 ${(mt + H - mb) / 2}) rotate(-90)`} textAnchor="middle" style={{ fontSize: 15 }}>% que siente insegura su zona (Bienal 2025)</text>
        <g className={`cl-sap${paso >= 1 ? " si" : ""}`}>
          <line x1={X(900)} y1={Y(15)} x2={X(13000)} y2={Y(75)} stroke="var(--tinta-3)" strokeWidth={2.5} strokeDasharray="9 7" />
          <line x1={X(3300)} x2={X(4300)} y1={Y(21)} y2={Y(21)} stroke="var(--tinta-3)" strokeWidth={2.5} strokeDasharray="9 7" />
          <text x={X(4300) + 10} y={Y(21) + 5} style={{ fontSize: 15, fill: "var(--tinta-2)", fontStyle: "italic" }}>lo esperado: más delito, más miedo</text>
        </g>
        <g className={`cl-sap${paso >= 2 ? " si" : ""}`}>
          {PANEL.map((p) => {
            const x = X(p.delitos_alto_impacto_100k), y = Y(p.zona_insegura), e = ETQ_T[p.localidad];
            return (
              <g key={p.localidad} data-tip={`<b>${p.nombre}</b><br>${fmt(p.zona_insegura)} % siente insegura su zona<br>${fmt(p.delitos_alto_impacto_100k, 0)} delitos por 100.000 hab.`}>
                <circle cx={x} cy={y} r={15} fill="transparent" />
                <circle cx={x} cy={y} r={8.5} fill="var(--vino)" stroke="var(--superficie)" strokeWidth={2} />
                {e && <text x={x + e.dx} y={y + e.dy} textAnchor={e.a} className="etq">{p.nombre}</text>}
              </g>
            );
          })}
        </g>
      </svg>
      <div style={{ display: "grid", gap: 14 }}>
        <Ap si={paso >= 0}><p className="cl-txt" style={{ fontSize: 18 }}>Cada punto, una localidad. Hacia la derecha, más delito registrado; hacia arriba, más gente que siente insegura su zona.</p></Ap>
        <Ap si={paso >= 0} retraso={250}><p className="cl-clave">Antes de verlo: ¿dónde esperarían más miedo?</p></Ap>
        <Ap si={paso >= 1}><p className="cl-txt" style={{ fontSize: 18 }}>Si el miedo siguiera al registro, los puntos subirían por la <b>diagonal</b>.</p></Ap>
        <Ap si={paso >= 2}>
          <p className="cl-txt" style={{ fontSize: 18 }}><b style={{ color: "var(--percepcion-texto)" }}>Usme y Ciudad Bolívar</b> registran poco y tienen el miedo más alto;{" "}
            <b style={{ color: "var(--registro-texto)" }}>Teusaquillo y Los Mártires</b> registran mucho y tienen menos.</p>
        </Ap>
        <Ap si={paso >= 2} retraso={300}>
          <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--rojo)" }}>
            <span className="cl-num" style={{ fontSize: 42, color: "var(--rojo)" }}>ρ = {fmt(v.rho, 2)}</span>
            <span className="cl-txt" style={{ fontSize: 16 }}>Correlación entre los dos rankings; no se distingue de cero (IC 95 %: {fmt(v.ic_inf, 2)} a {fmt(v.ic_sup, 2)}).</span>
            <b style={{ fontSize: 18 }}>El Distrito está decidiendo con un mapa incompleto.</b>
          </div>
        </Ap>
      </div>
    </div>
  );
}

/* ---------- 4 · Cómo llegamos al análisis ---------- */
function Grupo({ titulo, color, items }: { titulo: string; color: string; items: [string, string][] }) {
  return (
    <div className="cl-tarjeta" style={{ borderLeft: `6px solid ${color}` }}>
      <span className="cl-ante" style={{ color }}>{titulo}</span>
      {items.map(([a, b]) => (
        <div key={a} style={{ fontSize: 17, lineHeight: 1.35 }}><b>{a}</b><br /><span style={{ color: "var(--tinta-2)" }}>{b}</span></div>
      ))}
    </div>
  );
}
function Barras({ titulo, filas, color }: { titulo: string; filas: [string, number][]; color: string }) {
  const max = Math.max(...filas.map((f) => f[1]));
  return (
    <div>
      <div className="cl-ante" style={{ color: "var(--tinta-2)", marginBottom: 8 }}>{titulo}</div>
      {filas.map(([n, v]) => (
        <div key={n} style={{ display: "grid", gridTemplateColumns: "128px 1fr 62px", alignItems: "center", gap: 8, fontSize: 15, marginBottom: 6 }}>
          <span>{n}</span>
          <span style={{ height: 13, borderRadius: 3, background: color, width: `${(v / max) * 100}%` }} />
          <span className="mono" style={{ textAlign: "right" }}>{fmt(v, 0)}</span>
        </div>
      ))}
    </div>
  );
}
export function Datos({ paso }: { paso: number }) {
  const porPersona = R.adultos_urbanos_bienal / R.n_bienal;
  const filas = PANEL.map((p) => ({ nombre: p.nombre, casos: (p.delitos_alto_impacto_100k * p.poblacion) / 1e5, tasa: p.delitos_alto_impacto_100k, pob: p.poblacion }));
  const porCasos = [...filas].sort((a, b) => b.casos - a.casos).slice(0, 5);
  const porTasa = [...filas].sort((a, b) => b.tasa - a.tasa).slice(0, 5);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "500px 1fr", gap: 40, height: "100%" }}>
      <Ap si={paso >= 0} style={{ display: "grid", gap: 12, alignContent: "start" }}>
        <Grupo titulo="Lo que se siente" color="var(--percepcion)" items={[
          ["Bienal de Cultura Ciudadana 2025 (SCRD)", `${fmt(R.n_bienal, 0)} adultos; cada respuesta representa a unos ${fmt(porPersona, 0)} (factor de expansión)`],
          ["Encuesta Mundial de Valores 2024", `${fmt(R.n_emv_bogota, 0)} personas en Bogotá, 96 por localidad`]]} />
        <Grupo titulo="Lo que se registra" color="var(--registro)" items={[["Secretaría de Seguridad (SCJ)", "delitos de alto impacto 2018-2026 y llamadas a la Línea 123"]]} />
        <Grupo titulo="Contexto" color="var(--tinta-3)" items={[["SDP · UAESP · DADEP · IDECA", "población, alumbrado, espacio público y límites oficiales"]]} />
      </Ap>
      <div style={{ display: "grid", gap: 26, alignContent: "start" }}>
        <Ap si={paso >= 1}>
          <p className="cl-clave">Una llave para unirlas</p>
          <p className="cl-txt" style={{ fontSize: 17, margin: "6px 0 12px" }}>La misma localidad llega escrita de muchas formas. Todo se lleva al código oficial:</p>
          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            {["USAQUÉN", "01 - Usaquen", "01", "1"].map((t, k) => (
              <Ap key={t} si={paso >= 1} retraso={150 * k}><span className="cl-chip mono">«{t}»</span></Ap>
            ))}
            <Ap si={paso >= 1} retraso={700}><span style={{ fontSize: 30, color: "var(--rojo)", fontWeight: 700 }}>→</span></Ap>
            <Ap si={paso >= 1} retraso={850}><span className="cl-chip" style={{ background: "var(--rojo)", color: "#fff", fontSize: 18 }}>1 · Usaquén</span></Ap>
          </div>
        </Ap>
        <Ap si={paso >= 2}>
          <p className="cl-clave" style={{ marginBottom: 10 }}>Contar no es comparar</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 22 }}>
            <Barras titulo="Delitos registrados, casos" filas={porCasos.map((f) => [f.nombre, f.casos])} color="var(--neutro)" />
            <Barras titulo="Por 100.000 habitantes" filas={porTasa.map((f) => [f.nombre, f.tasa])} color="var(--registro)" />
          </div>
          <p className="cl-txt" style={{ fontSize: 16, marginTop: 8 }}>
            {porCasos[0].nombre} suma más casos porque tiene {fmt(porCasos[0].pob / 1e6, 1)} millones de habitantes. Por habitante, el centro. Todo se compara en tasas.
          </p>
        </Ap>
      </div>
    </div>
  );
}

/* ---------- 5 · Índice de Brecha, paso a paso ---------- */
function Linea({ titulo, detalle, color, colorTxt, valores, sel, onSel }: {
  titulo: string; detalle: string; color: string; colorTxt: string; valores: { id: number; v: number; n: string }[]; sel: number; onSel: (id: number) => void;
}) {
  const W = 690, H = 104, X = lin(-3, 3, 26, W - 26), y = 56;
  const s = valores.find((v) => v.id === sel)!;
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
        <b style={{ fontSize: 19, color: colorTxt }}>{titulo}</b>
        <span style={{ fontSize: 16, color: "var(--tinta-2)" }}>{s.n}: {detalle}</span>
      </div>
      <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={titulo}>
        <line x1={X(-3)} x2={X(3)} y1={y} y2={y} className="eje" strokeWidth={2} />
        {[-2, -1, 0, 1, 2].map((t) => (
          <g key={t}>
            <line x1={X(t)} x2={X(t)} y1={y - 6} y2={y + 6} className="eje" />
            <text x={X(t)} y={y + 26} className="tick" textAnchor="middle">{zfmt(t)}</text>
          </g>
        ))}
        <text x={X(0)} y={y + 44} textAnchor="middle" style={{ fontSize: 13, fill: "var(--tinta-3)" }}>promedio de Bogotá</text>
        {valores.filter((v) => v.id !== sel).map((v) => (
          <circle key={v.id} cx={X(v.v)} cy={y} r={7.5} fill={color} opacity={0.35} style={{ cursor: "pointer" }} onClick={() => onSel(v.id)} data-tip={`<b>${v.n}</b>: ${signo(v.v, 2)}`} />
        ))}
        <g style={{ transition: "transform .5s ease", transform: `translateX(${X(s.v)}px)` }}>
          <circle cx={0} cy={y} r={13} fill={color} stroke="var(--superficie)" strokeWidth={3} />
          <text x={0} y={y - 21} textAnchor="middle" className="etq" style={{ fontSize: 17 }}>{signo(s.v, 2)}</text>
        </g>
      </svg>
    </div>
  );
}
function Ranking19({ sel, onSel }: { sel: number; onSel: (id: number) => void }) {
  const porId = Object.fromEntries(IBS.map((x) => [x.localidad, x]));
  const W = 470, fila = 21, H = C.indice.length * fila + 30, X = lin(-3, 3.2, 150, W - 54);
  return (
    <div>
      <div className="cl-ante" style={{ color: "var(--tinta-2)", marginBottom: 6 }}>Las 19 localidades · margen de error del 90 %</div>
      <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Índice de Brecha por localidad con intervalo">
        <line x1={X(0)} x2={X(0)} y1={0} y2={H - 26} className="eje" />
        {C.indice.map((f, k) => {
          const y = k * fila + 11, b = porId[f.localidad], c = f.ibs > 0 ? "var(--percepcion)" : "var(--registro)", s = f.localidad === sel;
          return (
            <g key={f.localidad} onClick={() => onSel(f.localidad)} style={{ cursor: "pointer" }}
              data-tip={`<b>${f.nombre}</b><br>Índice ${fmt(f.ibs, 2)} (90 %: ${fmt(b.ibs_p05, 2)} a ${fmt(b.ibs_p95, 2)})<br>Top 5 en el ${fmt(b.prob_top5 * 100, 0)} % de las réplicas`}>
              <rect x={0} y={y - 10} width={W} height={fila} rx={4} fill={s ? "var(--superficie-2)" : "transparent"} />
              <text x={140} y={y + 5} textAnchor="end" style={{ fontSize: 14, fontWeight: s ? 700 : 400, fill: "var(--tinta)" }}>{f.nombre}</text>
              <line x1={X(b.ibs_p05)} x2={X(b.ibs_p95)} y1={y} y2={y} stroke={c} strokeWidth={3} strokeLinecap="round" />
              <circle cx={X(f.ibs)} cy={y} r={s ? 7 : 5} fill={c} />
              <text x={W - 2} y={y + 5} textAnchor="end" className="tick" style={{ fontSize: 13 }}>{signo(f.ibs, 2)}</text>
            </g>
          );
        })}
        {[-2, 0, 2].map((t) => <text key={t} x={X(t)} y={H - 6} className="tick" textAnchor="middle">{zfmt(t)}</text>)}
      </svg>
      <p className="cl-txt" style={{ fontSize: 15, marginTop: 4 }}>
        En 1.000 réplicas, top 5: {IBS.slice(0, 5).map((x) => `${x.nombre} ${fmt(x.prob_top5 * 100, x.prob_top5 > 0.99 && x.prob_top5 < 1 ? 1 : 0)} %`).join(" · ")}
      </p>
    </div>
  );
}
export function Indice({ paso }: { paso: number }) {
  const [sel, setSel] = useState(5);
  const f = C.indice.find((x) => x.localidad === sel)!;
  const orden = [...C.indice].sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));
  const ver = paso >= 3;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "690px 1fr", gap: 36, height: "100%" }}>
      <div style={{ display: "grid", gap: 8, alignContent: "start" }}>
        <label className="cl-control" style={{ display: "flex", alignItems: "center", gap: 10 }}>
          Localidad
          <select className="cl-sel" value={sel} onChange={(e) => setSel(Number(e.target.value))}>
            {orden.map((x) => <option key={x.localidad} value={x.localidad}>{x.nombre}</option>)}
          </select>
        </label>
        <Ap si={paso >= 0}>
          <Linea titulo="Lo que se siente" detalle={`${fmt(f.zona_insegura)} % califica mala la seguridad de su zona`} color="var(--percepcion)" colorTxt="var(--percepcion-texto)"
            valores={C.indice.map((x) => ({ id: x.localidad, v: x.z_percepcion, n: x.nombre }))} sel={sel} onSel={setSel} />
        </Ap>
        <Ap si={paso >= 1}>
          <Linea titulo="Lo que se registra" detalle={`${fmt(f.delitos_100k, 0)} delitos por 100.000 hab.`} color="var(--registro)" colorTxt="var(--registro-texto)"
            valores={C.indice.map((x) => ({ id: x.localidad, v: x.z_registro, n: x.nombre }))} sel={sel} onSel={setSel} />
        </Ap>
        <Ap si={paso >= 2}>
          <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--rojo)" }}>
            <span className="cl-ante">Índice de Brecha de {f.nombre} = sentir − registrar</span>
            <span className="cl-num" style={{ fontSize: 40 }}>
              <span style={{ color: "var(--percepcion-texto)" }}>({signo(f.z_percepcion, 2)})</span> − <span style={{ color: "var(--registro-texto)" }}>({signo(f.z_registro, 2)})</span> ={" "}
              <span style={{ color: "var(--rojo)" }}>{signo(f.ibs, 2)}</span>
            </span>
            <span className="cl-txt" style={{ fontSize: 17 }}>{f.ibs > 0 ? "Más miedo del que su registro haría esperar." : "Más registro que miedo entre quienes viven ahí."}</span>
          </div>
        </Ap>
      </div>
      <div style={{ position: "relative" }}>
        <div className="cl-capa" style={{ display: "grid", gap: 16, alignContent: "start", opacity: ver ? 0 : 1, transition: "opacity .4s", pointerEvents: ver ? "none" : "auto" }}>
          <Ap si={paso >= 0}><p className="cl-txt"><b>1.</b> Pasamos el miedo a una regla común: cuántas <b>desviaciones estándar</b> está cada localidad por encima o por debajo del promedio de la ciudad.</p></Ap>
          <Ap si={paso >= 1}><p className="cl-txt"><b>2.</b> Lo mismo con el registro, en logaritmo: el centro recibe población flotante y dispararía la escala.</p></Ap>
          <Ap si={paso >= 2}><p className="cl-txt"><b>3.</b> Restamos. <b style={{ color: "var(--percepcion-texto)" }}>Positivo</b>: más miedo del que explica el registro. <b style={{ color: "var(--registro-texto)" }}>Negativo</b>: más registro que miedo.</p></Ap>
          <Ap si={paso >= 0} retraso={400}><p className="cl-txt" style={{ fontSize: 15, color: "var(--tinta-3)" }}>Toquen cualquier punto o elijan otra localidad.</p></Ap>
        </div>
        <div className="cl-capa" style={{ opacity: ver ? 1 : 0, transition: "opacity .5s", pointerEvents: ver ? "auto" : "none" }}>
          <Ranking19 sel={sel} onSel={setSel} />
        </div>
      </div>
    </div>
  );
}

/* ---------- 6 · Hallazgo 1: la cifra oculta ---------- */
const PRUEBAS: [string, string][] = [
  ["Índice de Brecha", "Índice de Brecha vs cifra oculta"], ["Barrio inseguro", "Miedo según la EMV vs según la Bienal"],
  ["Zona insegura (Bienal) vs delitos", "Miedo en la zona vs delitos registrados"], ["Zona insegura (Bienal) vs ri", "Miedo en la zona vs llamadas por riñas"],
  ["Drogas", "Drogas en el parque vs llamadas por narcóticos"], ["Alumbrado", "Alumbrado malo vs luminarias por km² (2019)"],
  ["Víctimas", "Víctimas (encuesta) vs delitos registrados"],
];
const corto = (p: string) => PRUEBAS.find(([k]) => p.startsWith(k))?.[1] ?? p;

function DispersionOculta() {
  const W = 640, H = 420, ml = 66, mr = 20, mt = 16, mb = 58;
  const X = lin(0, 11.5, ml, W - mr), Y = lin(-2.6, 3.0, H - mb, mt);
  const pts = IBS.map((f) => ({ ...f, razon: OCULTA.find((c) => c.localidad === f.localidad)!.razon }));
  const n = pts.length, mx = pts.reduce((s, p) => s + p.razon, 0) / n, my = pts.reduce((s, p) => s + p.ibs, 0) / n;
  const b = pts.reduce((s, p) => s + (p.razon - mx) * (p.ibs - my), 0) / pts.reduce((s, p) => s + (p.razon - mx) ** 2, 0), a = my - b * mx;
  const etq: Record<number, { dx: number; dy: number; an: "start" | "middle" | "end" }> = {
    5: { dx: 0, dy: -16, an: "middle" }, 19: { dx: -13, dy: 5, an: "end" }, 7: { dx: 0, dy: -16, an: "middle" }, 14: { dx: 13, dy: 5, an: "start" }, 13: { dx: 13, dy: 5, an: "start" },
  };
  return (
    <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Índice de Brecha frente a cifra oculta">
      {[-2, -1, 0, 1, 2].map((t) => (
        <g key={t}><line x1={ml} x2={W - mr} y1={Y(t)} y2={Y(t)} className={t === 0 ? "eje" : "grid"} /><text x={ml - 10} y={Y(t) + 5} className="tick" textAnchor="end">{zfmt(t)}</text></g>
      ))}
      {[0, 2, 4, 6, 8, 10].map((t) => <text key={t} x={X(t)} y={H - mb + 22} className="tick" textAnchor="middle">{t}</text>)}
      <text x={(ml + W - mr) / 2} y={H - 8} textAnchor="middle" style={{ fontSize: 15 }}>Víctimas (encuesta) por cada delito registrado</text>
      <text transform={`translate(18 ${(mt + H - mb) / 2}) rotate(-90)`} textAnchor="middle" style={{ fontSize: 15 }}>Índice de Brecha</text>
      <line x1={X(0.3)} x2={X(11)} y1={Y(a + b * 0.3)} y2={Y(a + b * 11)} stroke="var(--tinta-3)" strokeWidth={2} strokeDasharray="7 6" />
      {pts.map((p) => {
        const e = etq[p.localidad];
        return (
          <g key={p.localidad} data-tip={`<b>${p.nombre}</b><br>Índice de Brecha ${fmt(p.ibs, 2)}<br>${fmt(p.razon)} víctimas por delito registrado`}>
            <circle cx={X(p.razon)} cy={Y(p.ibs)} r={15} fill="transparent" />
            <circle cx={X(p.razon)} cy={Y(p.ibs)} r={8.5} fill={p.ibs > 0 ? "var(--percepcion)" : "var(--registro)"} stroke="var(--superficie)" strokeWidth={2} />
            {e && <text x={X(p.razon) + e.dx} y={Y(p.ibs) + e.dy} textAnchor={e.an} className="etq">{p.nombre}</text>}
          </g>
        );
      })}
    </svg>
  );
}
function Pruebas() {
  const filas = [...D.validaciones].sort((a, b) => a.p_bh - b.p_bh);
  const W = 640, fila = 48, top = 34, H = filas.length * fila + top + 8, x0 = 330, xr = W - 70;
  const X = (p: number) => x0 + ((Math.log10(Math.max(p, 0.001)) + 3) / 3) * (xr - x0);
  return (
    <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Valor p ajustado de siete relaciones entre localidades">
      {[0.001, 0.01, 0.1, 1].map((t) => <text key={t} x={X(t)} y={18} className="tick" textAnchor="middle">{fmt(t, t < 0.01 ? 3 : t < 0.1 ? 2 : t < 1 ? 1 : 0)}</text>)}
      <rect x={x0} y={top - 6} width={X(0.05) - x0} height={H - top} fill="var(--rojo)" opacity={0.07} />
      <line x1={X(0.05)} x2={X(0.05)} y1={top - 8} y2={H} stroke="var(--rojo)" strokeWidth={2} strokeDasharray="6 5" />
      <text x={X(0.05) + 6} y={top + 2} style={{ fontSize: 13, fill: "var(--rojo)", fontWeight: 700 }}>umbral 0,05</text>
      {filas.map((f, k) => {
        const y = top + 18 + k * fila, ok = f.p_bh < 0.05;
        return (
          <g key={f.prueba}>
            <line x1={x0} x2={xr} y1={y} y2={y} className="grid" />
            <text x={x0 - 14} y={y + 5} textAnchor="end" style={{ fontSize: 15, fill: ok ? "var(--tinta)" : "var(--tinta-2)", fontWeight: ok ? 700 : 400 }}>{corto(f.prueba)}</text>
            <circle cx={X(f.p_bh)} cy={y} r={9} fill={ok ? "var(--rojo)" : "var(--neutro)"} />
            <text x={W - 2} y={y + 5} textAnchor="end" className="tick" style={{ fill: ok ? "var(--rojo)" : undefined }}>{fmt(f.p_bh, 3)}</text>
          </g>
        );
      })}
    </svg>
  );
}
/** Bogotá completa: suma de víctimas estimadas y de delitos registrados de las 19 localidades. */
export const BOGOTA: Oculta = (() => {
  const v = OCULTA.reduce((a, c) => a + c.victimas_estimadas, 0), d = OCULTA.reduce((a, c) => a + c.delitos_registrados, 0);
  const adultos = OCULTA.reduce((a, c) => a + c.victimas_estimadas / (c.emv_victima / 100), 0);
  return { localidad: 0, nombre: "Bogotá", emv_victima: (v / adultos) * 100, victimas_estimadas: v, delitos_registrados: d, razon: v / d, razon_inf: NaN, razon_sup: NaN };
})();
const cien = (n: number) => Math.round(n / 100) * 100;

/** 100 víctimas; en azul, cuántos delitos tiene el registro por cada 100. */
function CienVictimas({ registrados }: { registrados: number }) {
  const lado = 36, t = 27;
  return (
    <svg className="cl-g" viewBox={`0 0 ${10 * lado} ${10 * lado}`} role="img" aria-label={`Por cada 100 víctimas, ${registrados} delitos registrados`} style={{ maxWidth: 360 }}>
      {Array.from({ length: 100 }, (_, k) => {
        const azul = k < registrados, x = (k % 10) * lado + lado / 2, y = Math.floor(k / 10) * lado + lado / 2 + 2;
        return (
          <g key={k} style={{ color: azul ? "var(--registro)" : "var(--percepcion)", transition: `color .3s ease ${k * 7}ms` }}>
            <circle cx={x} cy={y - t * 0.3} r={t * 0.18} fill="currentColor" />
            <path d={`M${x - t * 0.3},${y + t * 0.42} Q${x - t * 0.3},${y - t * 0.06} ${x},${y - t * 0.06} Q${x + t * 0.3},${y - t * 0.06} ${x + t * 0.3},${y + t * 0.42} Z`} fill="currentColor" />
          </g>
        );
      })}
    </svg>
  );
}

function PasoCuenta({ n, titulo, fuente, children, color }: { n: number; titulo: string; fuente: string; children: React.ReactNode; color: string }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "40px 1fr", gap: 14, alignItems: "start" }}>
      <span style={{ width: 38, height: 38, borderRadius: 999, background: color, color: "#fff", display: "grid", placeItems: "center", fontFamily: "var(--f-display)", fontWeight: 800, fontSize: 18 }}>{n}</span>
      <div style={{ display: "grid", gap: 2 }}>
        <span style={{ fontSize: 17 }}><b>{titulo}</b> <span style={{ color: "var(--tinta-3)", fontSize: 14 }}>· {fuente}</span></span>
        {children}
      </div>
    </div>
  );
}

export function CifraOculta() {
  const [sel, setSel] = useState(0);
  const f = OCULTA.find((c) => c.localidad === sel) ?? BOGOTA;
  const adultos = f.victimas_estimadas / (f.emv_victima / 100);
  const porCien = 100 / f.razon, k = Math.min(100, Math.round(porCien));
  const orden = [...OCULTA].sort((a, b) => b.razon - a.razon);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "520px 1fr", gap: 44, height: "100%" }}>
      <div style={{ display: "grid", gap: 16, alignContent: "start" }}>
        <label className="cl-control" style={{ display: "flex", alignItems: "center", gap: 10 }}>
          Ver
          <select className="cl-sel" value={sel} onChange={(e) => setSel(Number(e.target.value))}>
            <option value={0}>Bogotá (las 19 localidades)</option>
            {orden.map((c) => <option key={c.localidad} value={c.localidad}>{c.nombre}</option>)}
          </select>
        </label>
        <PasoCuenta n={1} titulo="Lo que dicen las personas" fuente="Encuesta Mundial de Valores" color="var(--percepcion)">
          <span className="cl-txt" style={{ fontSize: 16 }}>El {fmt(f.emv_victima)} % de los {fmt(cien(adultos), 0)} adultos de {f.nombre} dice haber sido víctima de un delito en el último año.</span>
          <span className="cl-num" style={{ fontSize: 32, color: "var(--percepcion-texto)" }}>≈ {fmt(cien(f.victimas_estimadas), 0)} víctimas</span>
        </PasoCuenta>
        <PasoCuenta n={2} titulo="Lo que registra la Secretaría" fuente="SCJ, 2024" color="var(--registro)">
          <span className="cl-txt" style={{ fontSize: 16 }}>Delitos de alto impacto registrados ese año (enero a agosto, llevado a 12 meses).</span>
          <span className="cl-num" style={{ fontSize: 32, color: "var(--registro-texto)" }}>≈ {fmt(cien(f.delitos_registrados), 0)} delitos</span>
        </PasoCuenta>
        <PasoCuenta n={3} titulo="La cuenta" fuente="víctimas entre delitos" color="var(--vino)">
          <span className="cl-num" style={{ fontSize: 32, color: "var(--vino)" }}>{fmt(f.razon)} víctimas por cada delito</span>
          {Number.isFinite(f.razon_inf) && (
            <span className="cl-txt" style={{ fontSize: 14, color: "var(--tinta-3)" }}>Margen de la encuesta: de {fmt(f.razon_inf)} a {fmt(f.razon_sup)}. Compara personas con hechos: es un orden de magnitud.</span>
          )}
        </PasoCuenta>
      </div>
      <div style={{ display: "grid", gap: 10, alignContent: "start", justifyItems: "start" }}>
        <p className="cl-clave">Por cada <span style={{ color: "var(--percepcion-texto)" }}>100 víctimas</span>, el registro oficial tiene <span style={{ color: "var(--registro-texto)" }}>{fmt(porCien, 0)} delitos</span>.</p>
        <CienVictimas registrados={k} />
        <div style={{ display: "flex", gap: 20, fontSize: 16, color: "var(--tinta-2)" }}>
          <span><b style={{ color: "var(--registro)" }}>●</b> {k} quedan en el registro</span>
          <span><b style={{ color: "var(--percepcion)" }}>●</b> {100 - k} no llegan a las cifras</span>
        </div>
        {f.razon < 1.05 && <p className="cl-txt" style={{ fontSize: 15 }}>En {f.nombre} se registran tantos delitos como víctimas residentes, o más: allí llega gente de toda la ciudad.</p>}
      </div>
    </div>
  );
}

/* ---------- La prueba: el índice y el delito escondido van juntos ---------- */
export function Prueba({ paso }: { paso: number }) {
  const v = D.validaciones.find((x) => x.prueba.startsWith("Índice de Brecha"))!;
  const p0 = paso === 0;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "420px 1fr", gap: 44, height: "100%" }}>
      <div style={{ position: "relative" }}>
        <div className="cl-capa" style={{ display: "grid", gap: 16, alignContent: "start", opacity: p0 ? 1 : 0, transition: "opacity .4s" }}>
          <p className="cl-txt" style={{ fontSize: 18 }}>Cada punto es una localidad.</p>
          <p className="cl-txt" style={{ fontSize: 18 }}><b>Hacia arriba:</b> más miedo del que muestran sus cifras (el índice).</p>
          <p className="cl-txt" style={{ fontSize: 18 }}><b>Hacia la derecha:</b> más delito que no llega al registro.</p>
          <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--rojo)" }}>
            <span className="cl-num" style={{ fontSize: 44, color: "var(--rojo)" }}>ρ = {fmt(v.rho, 2)}</span>
            <span className="cl-txt" style={{ fontSize: 16 }}>Suben juntas (IC 95 % de {fmt(v.ic_inf, 2)} a {fmt(v.ic_sup, 2)}).</span>
            <b style={{ fontSize: 18 }}>Donde la gente tiene más miedo, más delito se queda escondido.</b>
          </div>
        </div>
        <div className="cl-capa" style={{ display: "grid", gap: 16, alignContent: "start", opacity: p0 ? 0 : 1, transition: "opacity .4s" }}>
          <p className="cl-txt" style={{ fontSize: 18 }}>¿Y si es casualidad? Probamos <b>siete relaciones</b> entre localidades.</p>
          <p className="cl-txt" style={{ fontSize: 18 }}>Con tantas pruebas, alguna sale «significativa» por azar. Corregimos por eso (Benjamini-Hochberg).</p>
          <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--rojo)" }}>
            <b style={{ fontSize: 20 }}>Solo esta sobrevive.</b>
            <span className="cl-txt" style={{ fontSize: 17 }}>El miedo de la periferia no es exagerado: es delito que no llega a las cifras.</span>
          </div>
        </div>
      </div>
      <div style={{ position: "relative" }}>
        <div className="cl-capa" style={{ opacity: p0 ? 1 : 0, transition: "opacity .5s", pointerEvents: p0 ? "auto" : "none" }}>
          <DispersionOculta />
        </div>
        <div className="cl-capa" style={{ opacity: p0 ? 0 : 1, transition: "opacity .5s", pointerEvents: p0 ? "none" : "auto" }}>
          <p className="cl-txt" style={{ fontSize: 15, marginBottom: 6 }}>Valor p ajustado: a la izquierda de la línea roja, la relación no es azar.</p>
          <Pruebas />
        </div>
      </div>
    </div>
  );
}
