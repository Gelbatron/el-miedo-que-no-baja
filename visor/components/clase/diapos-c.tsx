"use client";
import { fmt, signo } from "@/lib/datos";
import { COLOR_SEMAFORO, F, encuesta, type Ficha } from "@/lib/frentes";
import { BANDA_PANDEMIA, HURTO } from "@/lib/historia";
import { Ap, Cifra, lin } from "./piezas";

/* ---------- Cómo se mide la seguridad: cuatro frentes ---------- */
const FRENTES: { nombre: string; que: string; color: string }[] = [
  { nombre: "Lo que se registra", que: "Policía, Medicina Legal, Salud y Línea 123.", color: "var(--registro)" },
  { nombre: "Lo que se vive", que: "Víctimas, lo denuncien o no.", color: "var(--mujeres)" },
  { nombre: "Lo que se siente", que: "Cómo califica la gente su seguridad.", color: "var(--percepcion)" },
  { nombre: "Las condiciones", que: "Vías, alumbrado, espacio público, internet.", color: "var(--tinta-3)" },
];

function Fuente({ f }: { f: Ficha }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 8, alignItems: "center", padding: "4px 9px", background: "var(--superficie)", borderRadius: 8 }}>
      <span style={{ fontSize: 13.5, lineHeight: 1.2 }}><b>{f.fuente}</b><br /><span style={{ color: "var(--tinta-3)", fontSize: 12 }}>{f.entidad} · {f.anios} {f.anios === 1 ? "año" : "años"} · hasta {f.ultimo}</span></span>
      <span title={f.advertencia} style={{ minWidth: 42, textAlign: "center", padding: "3px 6px", borderRadius: 999, background: COLOR_SEMAFORO[f.semaforo], color: "#fff", fontWeight: 700, fontSize: 13 }}>{fmt(f.score, 0)}</span>
    </div>
  );
}

export function Frentes({ paso }: { paso: number }) {
  return (
    <div style={{ display: "grid", gap: 10, height: "100%", alignContent: "start" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1.45fr 1.1fr 0.85fr 1.1fr", gap: 12 }}>
        {FRENTES.map((fr, k) => (
          <Ap key={fr.nombre} si={paso >= 0} retraso={k * 120}>
            <div className="cl-tarjeta" style={{ borderTop: `6px solid ${fr.color}`, height: "100%", gap: 6, alignContent: "start", padding: "12px 14px" }}>
              <b style={{ fontFamily: "var(--f-display)", fontSize: 18 }}>{fr.nombre}</b>
              <span style={{ fontSize: 13.5, color: "var(--tinta-2)", lineHeight: 1.3 }}>{fr.que}</span>
              <Ap si={paso >= 1} retraso={k * 120} style={{ display: "grid", gap: 5 }}>
                {F.confiabilidad.filter((f) => f.frente === fr.nombre).map((f) => <Fuente key={f.fuente} f={f} />)}
              </Ap>
            </div>
          </Ap>
        ))}
      </div>
      <Ap si={paso >= 1}>
        <div style={{ display: "flex", gap: 18, alignItems: "center", fontSize: 14, color: "var(--tinta-2)", flexWrap: "wrap" }}>
          <span><b>Score de confiabilidad (0-100):</b> años comparables, actualidad, precisión, detalle territorial, validez y si cuadra con otra fuente.</span>
          {(["alta", "media", "baja"] as const).map((s) => <span key={s}><b style={{ color: COLOR_SEMAFORO[s] }}>●</b> {s}</span>)}
        </div>
      </Ap>
      <Ap si={paso >= 2}><p className="cl-clave" style={{ fontSize: 19, margin: 0 }}>Ninguna fuente sola cubre los cuatro frentes, y no todas pesan igual.</p></Ap>
    </div>
  );
}

/* ---------- Validar antes de modelar: la capa abierta frente a la Policía ---------- */
const rangoRazon = (cod: string, antes: boolean) => {
  const r = F.registro.razones.filter((x) => x.codigo === cod && (antes ? x.anio < 2023 : x.anio >= 2023 && x.anio <= 2025)).map((x) => x.razon_scj_siedco ?? NaN).filter((x) => !Number.isNaN(x));
  const a = Math.min(...r), b = Math.max(...r);
  return fmt(a, 1) === fmt(b, 1) ? `${fmt(a, 2)}×` : `${fmt(a, 1)}-${fmt(b, 1)}×`;
};

export function Validacion({ paso }: { paso: number }) {
  const H_ = F.registro.hurto_personas;
  const W = 660, H = 400, ml = 60, mr = 150, mt = 24, mb = 36;
  const X = lin(2018, 2026, ml, W - mr), Y = lin(0, 220000, H - mb, mt);
  const linea = (k: "capa_scj" | "siedco") => "M" + H_.map((h) => `${X(h.anio).toFixed(1)},${Y(h[k]).toFixed(1)}`).join("L");
  const u = H_[H_.length - 1];
  const e = (ind: string, a: number) => encuesta("DANE", ind, "hurto_personas", a) ?? 0;
  const capa21 = H_.find((h) => h.anio === 2021)!.capa_scj, capa23 = H_.find((h) => h.anio === 2023)!.capa_scj;
  const necesaria = e("tasa_denuncia", 2021) * (capa23 / capa21) / (e("victimas_miles", 2023) / e("victimas_miles", 2021));
  const homML = F.registro.razones.filter((r) => r.codigo === "H" && r.razon_scj_inmlcf).map((r) => r.razon_scj_inmlcf! * 100);
  const filas: [string, string, string][] = [
    ["Hurto a personas", rangoRazon("HP", true), rangoRazon("HP", false)],
    ["Hurto a residencias", rangoRazon("HR", true), rangoRazon("HR", false)],
    ["Hurto de automotores", rangoRazon("HA", true), rangoRazon("HA", false)],
    ["Homicidios, lesiones, sexuales, VIF", "1,0×", "1,0×"],
  ];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "660px 1fr", gap: 34, height: "100%" }}>
      <div>
        <p className="cl-ante" style={{ color: "var(--tinta-2)" }}>Hurto a personas registrado en Bogotá · enero a agosto · casos</p>
        <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Hurto a personas: capa abierta de la SCJ frente al registro de la Policía">
          {[0, 50000, 100000, 150000, 200000].map((t) => (
            <g key={t}><line x1={ml} x2={W - mr} y1={Y(t)} y2={Y(t)} className="grid" /><text x={ml - 8} y={Y(t) + 5} className="tick" textAnchor="end">{t === 0 ? "0" : `${t / 1000} mil`}</text></g>
          ))}
          {[2018, 2020, 2022, 2024, 2026].map((a) => <text key={a} x={X(a)} y={H - 10} className="tick" textAnchor="middle">{a}</text>)}
          <rect x={X(BANDA_PANDEMIA.desde)} y={mt} width={X(BANDA_PANDEMIA.hasta) - X(BANDA_PANDEMIA.desde)} height={H - mb - mt} fill="var(--tinta)" opacity={0.06} />
          <text x={(X(BANDA_PANDEMIA.desde) + X(BANDA_PANDEMIA.hasta)) / 2} y={mt + 16} textAnchor="middle" style={{ fontSize: 13, fill: "var(--tinta-2)" }}>Pandemia</text>
          <g className={`cl-sap${paso >= 1 ? " si" : ""}`}>
            <line x1={X(2022.5)} x2={X(2022.5)} y1={mt} y2={H - mb} stroke="var(--rojo)" strokeWidth={1.5} strokeDasharray="4 4" />
            <text x={X(2022.5) + 6} y={mt + 34} style={{ fontSize: 13, fontWeight: 700, fill: "var(--rojo)" }}>desde 2023, idénticas</text>
            {H_.filter((h) => h.anio < 2023).map((h) => (
              <text key={h.anio} x={X(h.anio)} y={(Y(h.capa_scj) + Y(h.siedco)) / 2 + 5} textAnchor="middle" style={{ fontSize: 13, fontWeight: 700, fill: "var(--tinta-2)" }}>×{fmt(h.capa_scj / h.siedco, 1)}</text>
            ))}
          </g>
          <path d={linea("capa_scj")} fill="none" stroke="var(--tinta-3)" strokeWidth={3} strokeDasharray="7 5" strokeLinejoin="round" />
          {H_.map((h) => <circle key={h.anio} cx={X(h.anio)} cy={Y(h.capa_scj)} r={4} fill="var(--tinta-3)" data-tip={`<b>Capa abierta SCJ</b> · ${h.anio}<br>${fmt(h.capa_scj, 0)} casos`} />)}
          <text x={X(2026) + 12} y={Y(u.capa_scj) + 22} style={{ fontSize: 14, fontWeight: 700, fill: "var(--tinta-2)" }}>Capa abierta</text>
          <text x={X(2026) + 12} y={Y(u.capa_scj) + 40} style={{ fontSize: 14, fill: "var(--tinta-2)" }}>{signo(HURTO.capa2022a2026, 0)} % desde 2022</text>
          <g className={`cl-sap${paso >= 1 ? " si" : ""}`}>
            <path d={linea("siedco")} fill="none" stroke="var(--registro)" strokeWidth={4.5} strokeLinejoin="round" />
            {H_.map((h) => <circle key={h.anio} cx={X(h.anio)} cy={Y(h.siedco)} r={5} fill="var(--registro)" data-tip={`<b>Policía (SIEDCO)</b> · ${h.anio}<br>${fmt(h.siedco, 0)} casos`} />)}
            <text x={X(2026) + 12} y={Y(u.siedco) - 22} style={{ fontSize: 14, fontWeight: 700, fill: "var(--registro-texto)" }}>Policía</text>
            <text x={X(2026) + 12} y={Y(u.siedco) - 4} style={{ fontSize: 14, fill: "var(--registro-texto)" }}>{signo(HURTO.policia2022a2026, 0)} % desde 2022</text>
          </g>
        </svg>
        <Ap si={paso >= 2} retraso={300}><p className="cl-clave" style={{ fontSize: 21, marginTop: 6 }}>La caída de 2023 no la ve ninguna otra fuente: cambió cómo se arma la serie, no la calle.</p></Ap>
      </div>
      <div style={{ display: "grid", gap: 12, alignContent: "start" }}>
        <Ap si={paso >= 0}>
          <Cifra ante="La capa abierta dice" valor={`${signo(HURTO.capa2022a2026, 0)} %`} color="var(--tinta-2)" tam={44}
            texto="en el hurto a personas desde 2022. Antes de modelar, la contrastamos con dos fuentes independientes." />
        </Ap>
        <Ap si={paso >= 1}>
          <div className="cl-tarjeta" style={{ gap: 4, padding: "12px 16px" }}>
            <span style={{ display: "grid", gridTemplateColumns: "1fr 84px 84px", gap: 6, fontSize: 13, color: "var(--tinta-3)" }}><span>Capa SCJ ÷ Policía</span><span style={{ textAlign: "right" }}>2018-22</span><span style={{ textAlign: "right" }}>2023-25</span></span>
            {filas.map(([n, a, b]) => (
              <span key={n} style={{ display: "grid", gridTemplateColumns: "1fr 84px 84px", gap: 6, fontSize: 15 }}>
                <span>{n}</span><b style={{ textAlign: "right", color: a.startsWith("1,0") ? "var(--hombres)" : "var(--rojo)" }}>{a}</b><b style={{ textAlign: "right", color: "var(--hombres)" }}>{b}</b>
              </span>
            ))}
            <span style={{ fontSize: 13, color: "var(--tinta-3)" }}>Y los homicidios coinciden con Medicina Legal: {fmt(Math.min(...homML), 0)} a {fmt(Math.max(...homML), 0)} %.</span>
          </div>
        </Ap>
        <Ap si={paso >= 2}>
          <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--mujeres)", gap: 4, padding: "12px 16px" }}>
            <b style={{ fontSize: 16 }}>Y la encuesta del DANE le da la razón a la Policía</b>
            <span style={{ fontSize: 14.5 }}>2021 → 2023: víctimas de hurto {fmt(e("victimizacion", 2021), 1)} % → {fmt(e("victimizacion", 2023), 1)} % (sin diferencia significativa); denuncia {fmt(e("tasa_denuncia", 2021), 0)} % → {fmt(e("tasa_denuncia", 2023), 0)} %.</span>
            <span style={{ fontSize: 14.5 }}>Para que la caída de la capa fuera real, la denuncia tendría que haber bajado a <b>{fmt(necesaria, 0)} %</b>.</span>
          </div>
        </Ap>
      </div>
    </div>
  );
}

/* ---------- Tendencias en la ventana comparable de cada serie ---------- */
export function Tendencias({ paso }: { paso: number }) {
  const T = [...F.tendencias].sort((a, b) => a.post_cambio_anual_pct - b.post_cambio_anual_pct);
  const sube = (t: (typeof T)[number]) => t.post_cambio_anual_pct > 0;
  const W = 700, fila = 44, top = 30, H = T.length * fila + top + 34, X = lin(-20, 20, 290, W - 80);
  const t = (c: string) => F.tendencias.find((x) => x.codigo === c)!;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "700px 1fr", gap: 36, height: "100%" }}>
      <div>
        <p className="cl-ante" style={{ color: "var(--tinta-2)" }}>Cambio anual promedio · ventana comparable · IC 95 %</p>
        <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Cambio anual por tipo de delito con intervalo de confianza">
          {[-20, -10, 0, 10, 20].map((v) => (
            <g key={v}>
              <line x1={X(v)} x2={X(v)} y1={top - 8} y2={H - 30} className={v === 0 ? "eje" : "grid"} strokeWidth={v === 0 ? 2 : 1} />
              <text x={X(v)} y={H - 10} className="tick" textAnchor="middle">{v > 0 ? `+${v}` : v === 0 ? "0" : `−${-v}`} %</text>
            </g>
          ))}
          {T.map((x, k) => {
            const y = top + k * fila, si = sube(x) ? paso >= 1 : true, c = sube(x) ? "var(--vino)" : x.post_p < 0.05 ? "var(--registro)" : "var(--neutro)";
            const nota = x.estado === "quiebre" ? `desde 2023 · serie con quiebre` : x.estado === "sin_validar" ? "sin serie externa" : `${x.ventana.replace("-20", "-")} · validada`;
            return (
              <g key={x.codigo} className={`cl-sap${si ? " si" : ""}`}>
                <text x={280} y={y + 1} textAnchor="end" style={{ fontSize: 15, fill: "var(--tinta)", fontWeight: sube(x) ? 700 : 400 }}>{x.tipo}</text>
                <text x={280} y={y + 17} textAnchor="end" style={{ fontSize: 12, fill: "var(--tinta-3)" }}>{nota}</text>
                <line x1={X(Math.max(-20, x.post_ic_inf))} x2={X(Math.min(20, x.post_ic_sup))} y1={y + 4} y2={y + 4} stroke={c} strokeWidth={4} strokeLinecap="round" opacity={0.55} />
                <circle cx={X(x.post_cambio_anual_pct)} cy={y + 4} r={7} fill={c} stroke={x.estado === "quiebre" ? "var(--superficie)" : "none"} strokeWidth={2} />
                <text x={W - 2} y={y + 9} textAnchor="end" style={{ fontSize: 14, fontWeight: 700, fill: c }}>{signo(x.post_cambio_anual_pct, 1)} %{x.post_p >= 0.05 ? " n.s." : ""}</text>
              </g>
            );
          })}
        </svg>
      </div>
      <div style={{ display: "grid", gap: 14, alignContent: "start" }}>
        <Ap si={paso >= 0}><p className="cl-txt" style={{ fontSize: 18 }}><b style={{ color: "var(--registro-texto)" }}>Los hurtos bajan desde 2023</b> ({signo(t("HP").post_cambio_anual_pct, 0)} % al año el hurto a personas), pero 2023 fue un pico: frente a 2022, la Policía registra {signo(HURTO.policia2022a2026, 0)} %.</p></Ap>
        <Ap si={paso >= 1}><p className="cl-txt" style={{ fontSize: 18 }}><b style={{ color: "var(--vino)" }}>Y la violencia sube</b>, en series validadas: homicidios {signo(t("H").post_cambio_anual_pct, 1)} %, delitos sexuales {signo(t("DS").post_cambio_anual_pct, 1)} % y violencia intrafamiliar {signo(t("VI").post_cambio_anual_pct, 1)} % por año.</p></Ap>
        <Ap si={paso >= 2}>
          <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--oro)", gap: 4 }}>
            <b style={{ fontSize: 17 }}>Lo que controla el modelo</b>
            <span style={{ fontSize: 15 }}>Binomial negativa de panel, 19 localidades:</span>
            <span style={{ fontSize: 15 }}>· el tamaño de cada localidad (población como exposición)</span>
            <span style={{ fontSize: 15 }}>· lo propio de cada una (efectos fijos)</span>
            <span style={{ fontSize: 15 }}>· la sobredispersión de los conteos</span>
            <span style={{ fontSize: 15 }}>· años de una localidad no independientes (errores agrupados)</span>
            <span style={{ fontSize: 15 }}>· y la pandemia fuera de la ventana.</span>
          </div>
        </Ap>
      </div>
    </div>
  );
}

/* ---------- Lo que explica el aprendizaje supervisado ---------- */
function BarrasH({ filas, min, max, alto = 40, dec = 3, colores }: { filas: { n: string; v: number; e?: number }[]; min: number; max: number; alto?: number; dec?: number; colores?: string[] }) {
  const W = 640, H = filas.length * alto + 30, X = lin(min, max, 250, W - 70);
  return (
    <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Barras">
      {filas.map((f, k) => {
        const y = 10 + k * alto, c = colores?.[k] ?? "var(--registro)";
        return (
          <g key={f.n}>
            <text x={240} y={y + alto / 2 + 1} textAnchor="end" style={{ fontSize: 15, fill: "var(--tinta)" }}>{f.n}</text>
            <rect x={X(min)} y={y + 6} width={Math.max(0, X(f.v) - X(min))} height={alto - 14} rx={5} fill={c} />
            {f.e !== undefined && <line x1={X(f.v - f.e)} x2={X(f.v + f.e)} y1={y + alto / 2} y2={y + alto / 2} stroke="var(--tinta)" strokeWidth={1.5} />}
            <text x={X(f.v + (f.e ?? 0)) + 8} y={y + alto / 2 + 5} style={{ fontSize: 15, fontWeight: 800, fill: "var(--tinta)", fontFamily: "var(--f-display)" }}>{fmt(f.v, dec)}</text>
          </g>
        );
      })}
    </svg>
  );
}

export function Modelos({ paso }: { paso: number }) {
  const orden = ["Regresión logística", "Bosque aleatorio", "Gradient boosting"];
  const auc = (lista: { modelo: string; mean: number; std: number }[]) => orden.map((m) => lista.find((x) => x.modelo === m)!);
  const sin = auc(F.ml.sin_calificaciones), con = auc(F.ml.completo);
  const bloques = F.ml.bloques_sin_calificaciones;
  const ctx = F.ml.contexto_localidad;
  const capa = (activa: boolean) => ({ opacity: activa ? 1 : 0, transition: "opacity .45s", pointerEvents: activa ? "auto" : "none" } as const);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "640px 1fr", gap: 40, height: "100%" }}>
      <div style={{ position: "relative" }}>
        <div className="cl-capa" style={capa(paso === 0)}>
          <p className="cl-ante" style={{ color: "var(--tinta-2)" }}>Acierto fuera de muestra (AUC) · 25 particiones · 5.538 personas</p>
          <BarrasH min={0.5} max={0.9} filas={sin.map((m) => ({ n: `${m.modelo} · hechos y contexto`, v: m.mean, e: m.std }))} colores={["var(--neutro)", "var(--registro)", "var(--registro)"]} />
          <BarrasH min={0.5} max={0.9} filas={con.map((m) => ({ n: `${m.modelo} · + calificaciones`, v: m.mean, e: m.std }))} colores={["var(--neutro)", "var(--percepcion)", "var(--percepcion)"]} />
        </div>
        <div className="cl-capa" style={capa(paso === 1)}>
          <p className="cl-ante" style={{ color: "var(--tinta-2)" }}>Acierto que se pierde al quitar cada bloque · gradient boosting</p>
          <BarrasH min={0} max={0.12} alto={52} filas={bloques.map((b) => ({ n: b.bloque, v: b.mean, e: b.std }))}
            colores={bloques.map((b) => b.bloque.startsWith("Hechos") ? "var(--percepcion)" : b.bloque.startsWith("Delito") ? "var(--registro)" : "var(--neutro)")} />
        </div>
        <div className="cl-capa" style={capa(paso >= 2)}>
          <p className="cl-ante" style={{ color: "var(--tinta-2)" }}>¿El delito registrado aporta algo más que saber dónde vive la persona?</p>
          <BarrasH min={0.68} max={0.74} alto={56} filas={ctx.map((c) => ({ n: c.spec.replace("sin contexto de localidad", "Sin datos de la localidad"), v: c.mean }))}
            colores={["var(--neutro)", "var(--registro)", "var(--percepcion)", "var(--vino)"]} />
        </div>
      </div>
      <div style={{ display: "grid", gap: 14, alignContent: "start" }}>
        <Ap si={paso >= 0}><p className="cl-txt" style={{ fontSize: 18 }}>Entrenamos tres modelos para predecir quién siente insegura su zona y los probamos con personas que no vieron. Los flexibles (bosque y gradient boosting) aciertan <b>{fmt(sin[2].mean * 100, 0)} de cada 100 parejas</b>; con las calificaciones del barrio, <b>{fmt(con[2].mean * 100, 0)}</b>.</p></Ap>
        <Ap si={paso >= 1}><p className="cl-txt" style={{ fontSize: 18 }}><b style={{ color: "var(--percepcion-texto)" }}>Lo que más explica es lo que pasa en el barrio</b> (atracos, conflictos, parques). Las calificaciones del barrio pesan aún más, pero comparten cuestionario con la pregunta de seguridad: las tratamos con cuidado.</p></Ap>
        <Ap si={paso >= 2}>
          <div className="cl-tarjeta" style={{ borderLeft: "6px solid var(--vino)" }}>
            <b style={{ fontSize: 19 }}>El delito registrado no agrega nada a saber en qué localidad vive la persona.</b>
            <span className="cl-txt" style={{ fontSize: 15 }}>Su aporte ({fmt(ctx[1].mean, 3)}) es el mismo que el de la localidad sola ({fmt(ctx[2].mean, 3)}), y sumado a ella no mejora nada ({fmt(ctx[3].mean, 3)}).</span>
          </div>
        </Ap>
      </div>
    </div>
  );
}
