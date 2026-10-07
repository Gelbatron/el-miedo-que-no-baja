// Gráficos en SVG puro, dibujados a escala. Los colores salen de los tokens del tema.
import { fmt, pval, signo } from "@/lib/datos";

/* ---------- efectos marginales con intervalo (forest plot) ---------- */
export function Forest({ filas, ancho = 760, min, max, unidad = "pp", dec = 1, paso: pasoFijo }: { filas: { etiqueta: string; ame_pp: number; ic_inf: number; ic_sup: number; p: number; tip?: string }[]; ancho?: number; min?: number; max?: number; unidad?: string; dec?: number; paso?: number }) {
  const fila = 34, ml = Math.min(330, ancho * 0.44), mr = 92, alto = filas.length * fila + 34;
  const lo = min ?? Math.min(-5, ...filas.map((f) => f.ic_inf)) - 2;
  const hi = max ?? Math.max(5, ...filas.map((f) => f.ic_sup)) + 2;
  const X = (v: number) => ml + ((v - lo) / (hi - lo)) * (ancho - ml - mr);
  const paso = pasoFijo ?? (hi - lo > 40 ? 10 : 5);
  const ticks: number[] = [];
  for (let t = Math.ceil(lo / paso) * paso; t <= hi; t += paso) ticks.push(t);
  return (
    <div className="g-scroll"><svg className="g" viewBox={`0 0 ${ancho} ${alto}`} role="img" aria-label="Efectos marginales promedio con intervalo de 95 %">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={X(t)} x2={X(t)} y1={0} y2={alto - 26} className={t === 0 ? "base" : "grid"} />
          <text x={X(t)} y={alto - 8} className="tick" textAnchor="middle">{t === 0 ? "0" : `${t > 0 ? "+" : "−"}${fmt(Math.abs(t), Number.isInteger(t) ? 0 : 1)}${unidad ? ` ${unidad}` : ""}`}</text>
        </g>
      ))}
      {filas.map((f, i) => {
        const y = 14 + i * fila;
        const sig = f.ic_inf > 0 || f.ic_sup < 0;
        const col = sig ? (f.ame_pp > 0 ? "var(--percepcion)" : "var(--registro)") : "var(--neutro)";
        const tip = f.tip ?? `<b>${f.etiqueta}</b><br>${signo(f.ame_pp, dec)} ${unidad} · IC 95 %: ${signo(f.ic_inf, dec)} a ${signo(f.ic_sup, dec)}<br>${pval(f.p)}`;
        return (
          <g key={f.etiqueta} data-tip={tip}>
            <rect x={0} y={y - 14} width={ancho} height={fila} className="hit" />
            <text x={ml - 12} y={y + 4} className="etq" textAnchor="end">{f.etiqueta}</text>
            <line x1={X(f.ic_inf)} x2={X(f.ic_sup)} y1={y} y2={y} className="ic" stroke={col} />
            <circle cx={X(f.ame_pp)} cy={y} r={6} fill={col} className="punto" />
            <text x={ancho - mr + 12} y={y + 4} className="val">{signo(f.ame_pp, dec)}{sig ? "" : " n.s."}</text>
          </g>
        );
      })}
    </svg></div>
  );
}

/* ---------- barras horizontales ---------- */
export function Barras({ filas, ancho = 760, unidad = "", dec = 1, maximo, color = "var(--registro)", resaltar }: {
  filas: { etiqueta: string; valor: number; detalle?: string; color?: string }[]; ancho?: number; unidad?: string; dec?: number; maximo?: number; color?: string; resaltar?: (i: number) => boolean;
}) {
  const fila = 32, ml = Math.min(320, ancho * 0.42), mr = 70, alto = filas.length * fila + 6;
  const mx = maximo ?? Math.max(...filas.map((f) => f.valor));
  const X = (v: number) => ml + (v / mx) * (ancho - ml - mr);
  return (
    <div className="g-scroll"><svg className="g" viewBox={`0 0 ${ancho} ${alto}`} role="img" aria-label="Barras">
      {filas.map((f, i) => {
        const y = 4 + i * fila;
        const col = f.color ?? (resaltar ? (resaltar(i) ? color : "var(--neutro)") : color);
        return (
          <g key={f.etiqueta} data-tip={`<b>${f.etiqueta}</b><br>${fmt(f.valor, dec)} ${unidad}${f.detalle ? `<br>${f.detalle}` : ""}`}>
            <rect x={0} y={y} width={ancho} height={fila} className="hit" />
            <text x={ml - 12} y={y + 19} className="etq" textAnchor="end">{f.etiqueta}</text>
            <rect x={ml} y={y + 7} width={Math.max(2, X(f.valor) - ml)} height={16} rx={4} fill={col} />
            <text x={X(f.valor) + 8} y={y + 19} className="val">{fmt(f.valor, dec)}{unidad === "%" ? " %" : ""}</text>
          </g>
        );
      })}
    </svg></div>
  );
}

/* ---------- líneas (series en el tiempo) ---------- */
export function Lineas({ series, ancho = 760, alto = 320, ymin = 0, ymax, unidad = "", base, bandas }: {
  series: { nombre: string; color: string; punteada?: boolean; puntos: { x: number; y: number; tip?: string }[] }[]; ancho?: number; alto?: number; ymin?: number; ymax?: number; unidad?: string; base?: number;
  bandas?: { desde: number; hasta: number; etiqueta: string }[];
}) {
  const ml = 46, mr = 190, mt = 14, mb = 30;
  const xs = series.flatMap((s) => s.puntos.map((p) => p.x));
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y1 = ymax ?? Math.ceil(Math.max(...series.flatMap((s) => s.puntos.map((p) => p.y))) / 50) * 50;
  const X = (v: number) => ml + ((v - x0) / (x1 - x0 || 1)) * (ancho - ml - mr);
  const Y = (v: number) => mt + (1 - (v - ymin) / (y1 - ymin)) * (alto - mt - mb);
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => ymin + f * (y1 - ymin));
  // etiquetas finales sin choque
  const finales = series.map((s) => ({ s, y: Y(s.puntos[s.puntos.length - 1].y) })).sort((a, b) => a.y - b.y);
  for (let i = 1; i < finales.length; i++) if (finales[i].y - finales[i - 1].y < 16) finales[i].y = finales[i - 1].y + 16;
  return (
    <div className="g-scroll"><svg className="g" viewBox={`0 0 ${ancho} ${alto}`} role="img" aria-label="Serie de tiempo">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={ml} x2={ancho - mr} y1={Y(t)} y2={Y(t)} className={base !== undefined && Math.abs(t - base) < 1e-9 ? "base" : "grid"} />
          <text x={ml - 8} y={Y(t) + 4} className="tick" textAnchor="end">{fmt(t, 0)}</text>
        </g>
      ))}
      {bandas?.map((b) => {
        const a = X(Math.max(b.desde, x0)), z = X(Math.min(b.hasta, x1));
        return (
          <g key={b.etiqueta}>
            <rect x={a} y={mt} width={z - a} height={alto - mt - mb} fill="var(--tinta)" opacity={0.06} />
            <text x={(a + z) / 2} y={mt + 13} className="tick" textAnchor="middle" style={{ fontWeight: 600 }}>{b.etiqueta}</text>
          </g>
        );
      })}
      {base !== undefined && !ticks.includes(base) && <line x1={ml} x2={ancho - mr} y1={Y(base)} y2={Y(base)} className="base" />}
      {Array.from({ length: x1 - x0 + 1 }, (_, i) => x0 + i).map((a) => (
        <text key={a} x={X(a)} y={alto - 10} className="tick" textAnchor="middle">{a}</text>
      ))}
      {series.map((s) => (
        <g key={s.nombre}>
          <path d={"M" + s.puntos.map((p) => `${X(p.x).toFixed(1)},${Y(p.y).toFixed(1)}`).join("L")} className="linea" style={{ stroke: s.color, ...(s.punteada ? { strokeDasharray: "6 5", strokeWidth: 2 } : {}) }} />
          {s.puntos.map((p) => (
            <circle key={p.x} cx={X(p.x)} cy={Y(p.y)} r={4.5} fill={s.color} className="punto" data-tip={p.tip ?? `<b>${s.nombre}</b> · ${p.x}<br>${fmt(p.y, 0)} ${unidad}`} />
          ))}
        </g>
      ))}
      {finales.map(({ s, y }) => (
        <text key={s.nombre} x={X(x1) + 12} y={y + 4} className="etq" style={{ fontWeight: 600 }}>{s.nombre} {fmt(s.puntos[s.puntos.length - 1].y, 0)}</text>
      ))}
    </svg></div>
  );
}

/** Marcas en valores redondos (1, 2, 2,5 o 5 por potencia de 10) dentro de [a, b] */
function redondos(a: number, b: number, objetivo = 5) {
  const crudo = (b - a) / objetivo, pot = 10 ** Math.floor(Math.log10(crudo));
  const paso = [1, 2, 2.5, 5, 10].map((m) => m * pot).find((p) => p >= crudo) ?? 10 * pot;
  const valores: number[] = [];
  for (let t = Math.ceil(a / paso) * paso; t <= b + 1e-9; t += paso) valores.push(Math.abs(t) < 1e-9 ? 0 : t);
  return { valores, dec: Math.max(0, -Math.floor(Math.log10(paso) + 1e-9) + (paso / pot === 2.5 ? 1 : 0)) };
}

/* ---------- dispersión con etiquetas ---------- */
export function Dispersion({ puntos, ancho = 760, alto = 420, ejeX, ejeY, logX = false, colorDe, recta = true }: {
  puntos: { id: number; nombre: string; x: number; y: number; tip?: string }[]; ancho?: number; alto?: number; ejeX: string; ejeY: string; logX?: boolean; colorDe?: (p: { x: number; y: number }) => string; recta?: boolean;
}) {
  const ml = 56, mr = 24, mt = 16, mb = 46;
  const tx = (v: number) => (logX ? Math.log10(v) : v);
  const xs = puntos.map((p) => tx(p.x)), ys = puntos.map((p) => p.y);
  const pad = (a: number, b: number) => (b - a) * 0.08;
  const x0 = Math.min(...xs) - pad(Math.min(...xs), Math.max(...xs)), x1 = Math.max(...xs) + pad(Math.min(...xs), Math.max(...xs));
  const y0 = Math.min(...ys) - pad(Math.min(...ys), Math.max(...ys)), y1 = Math.max(...ys) + pad(Math.min(...ys), Math.max(...ys));
  const X = (v: number) => ml + ((tx(v) - x0) / (x1 - x0)) * (ancho - ml - mr);
  const Y = (v: number) => mt + (1 - (v - y0) / (y1 - y0)) * (alto - mt - mb);
  // recta por mínimos cuadrados (solo guía visual)
  const n = xs.length, mx = xs.reduce((a, b) => a + b) / n, my = ys.reduce((a, b) => a + b) / n;
  const b = xs.reduce((s, x, i) => s + (x - mx) * (ys[i] - my), 0) / xs.reduce((s, x) => s + (x - mx) ** 2, 0);
  const a = my - b * mx;
  const ticksX = logX
    ? [100, 300, 1000, 3000, 10000, 30000].filter((t) => Math.log10(t) >= x0 && Math.log10(t) <= x1)
    : redondos(x0, x1).valores;
  const ry = redondos(y0, y1), ticksY = ry.valores, rx = redondos(x0, x1);
  return (
    <div className="g-scroll"><svg className="g" viewBox={`0 0 ${ancho} ${alto}`} role="img" aria-label={`${ejeY} frente a ${ejeX}`}>
      {ticksY.map((t) => (
        <g key={t}><line x1={ml} x2={ancho - mr} y1={Y(t)} y2={Y(t)} className="grid" /><text x={ml - 8} y={Y(t) + 4} className="tick" textAnchor="end">{fmt(t, ry.dec)}</text></g>
      ))}
      {ticksX.map((t) => (
        <text key={t} x={X(logX ? t : t)} y={alto - mb + 18} className="tick" textAnchor="middle">{fmt(t, logX ? 0 : rx.dec)}</text>
      ))}
      <text x={(ml + ancho - mr) / 2} y={alto - 6} className="etq2" textAnchor="middle">{ejeX}</text>
      <text x={14} y={(mt + alto - mb) / 2} className="etq2" textAnchor="middle" transform={`rotate(-90 14 ${(mt + alto - mb) / 2})`}>{ejeY}</text>
      {recta && <line x1={ml} x2={ancho - mr} y1={Y(a + b * x0)} y2={Y(a + b * x1)} stroke="var(--tinta-3)" strokeDasharray="4 4" strokeWidth={1.2} />}
      {colocarEtiquetas(puntos.map((p) => ({ p, x: X(p.x), y: Y(p.y) })), ancho - mr).map(({ p, x, y, lx, ly, anc }) => (
        <g key={p.id} data-tip={p.tip ?? `<b>${p.nombre}</b>`}>
          <circle cx={x} cy={y} r={14} className="hit" />
          {Math.abs(ly - 4 - y) > 14 && <line x1={x} y1={y} x2={anc === "start" ? lx - 2 : lx + 2} y2={ly - 4} stroke="var(--linea)" />}
          <circle cx={x} cy={y} r={6.5} fill={colorDe ? colorDe(p) : "var(--registro)"} className="punto" />
          <text x={lx} y={ly} className="etq2" style={{ fontSize: 11.5 }} textAnchor={anc}>{p.nombre}</text>
        </g>
      ))}
    </svg></div>
  );
}

/* ---------- mancuerna (mujeres frente a hombres) ---------- */
export function Mancuerna({ filas, ancho = 760 }: { filas: { etiqueta: string; mujeres: number; hombres: number }[]; ancho?: number }) {
  const fila = 44, ml = Math.min(330, ancho * 0.44), mr = 40, alto = filas.length * fila + 34;
  const X = (v: number) => ml + (v / 100) * (ancho - ml - mr);
  return (
    <div className="g-scroll"><svg className="g" viewBox={`0 0 ${ancho} ${alto}`} role="img" aria-label="Mujeres frente a hombres">
      {[0, 25, 50, 75, 100].map((t) => (
        <g key={t}><line x1={X(t)} x2={X(t)} y1={0} y2={alto - 26} className="grid" /><text x={X(t)} y={alto - 8} className="tick" textAnchor="middle">{t} %</text></g>
      ))}
      {filas.map((f, i) => {
        const y = 20 + i * fila;
        const [izq, der] = f.mujeres < f.hombres ? [f.mujeres, f.hombres] : [f.hombres, f.mujeres];
        return (
          <g key={f.etiqueta}>
            <text x={ml - 12} y={y + 4} className="etq" textAnchor="end">{f.etiqueta}</text>
            <line x1={X(izq)} x2={X(der)} y1={y} y2={y} stroke="var(--linea)" strokeWidth={5} strokeLinecap="round" />
            <circle cx={X(f.hombres)} cy={y} r={7} fill="var(--hombres)" className="punto" data-tip={`<b>Hombres</b> · ${fmt(f.hombres)} %`} />
            <rect x={X(f.mujeres) - 6.5} y={y - 6.5} width={13} height={13} rx={2} fill="var(--mujeres)" className="punto" data-tip={`<b>Mujeres</b> · ${fmt(f.mujeres)} %`} />
            <text x={X(der) + 12} y={y + 4} className="val">{fmt(der)}</text>
            <text x={X(izq) - 12} y={y + 4} className="val" textAnchor="end">{fmt(izq)}</text>
          </g>
        );
      })}
    </svg></div>
  );
}

export function LeyendaSexo() {
  return (
    <div className="leyenda">
      <span><i style={{ background: "var(--mujeres)", borderRadius: 2 }} />Mujeres (cuadrado)</span>
      <span><i style={{ background: "var(--hombres)", borderRadius: "50%" }} />Hombres (círculo)</span>
    </div>
  );
}

/** Coloca etiquetas evitando choques: prueba derecha/izquierda y desplaza en vertical. */
function colocarEtiquetas<T extends { nombre: string }>(pts: { p: T; x: number; y: number }[], limite: number) {
  const cajas: { x0: number; x1: number; y0: number; y1: number }[] = [];
  const choca = (b: { x0: number; x1: number; y0: number; y1: number }) => cajas.some((c) => b.x0 < c.x1 && b.x1 > c.x0 && b.y0 < c.y1 && b.y1 > c.y0);
  pts.forEach(({ x, y }) => cajas.push({ x0: x - 7, x1: x + 7, y0: y - 7, y1: y + 7 }));
  return [...pts].sort((a, b) => a.y - b.y).map(({ p, x, y }) => {
    const w = p.nombre.length * 6.4 + 4, h = 13;
    for (const dy of [-9, 17, -24, 31, -38, 45, -52]) {
      for (const lado of ["start", "end"] as const) {
        const lx = lado === "start" ? x + 9 : x - 9;
        if (lado === "start" && lx + w > limite) continue;
        const ly = y + dy;
        const b = { x0: lado === "start" ? lx : lx - w, x1: lado === "start" ? lx + w : lx, y0: ly - h + 2, y1: ly + 3 };
        if (!choca(b)) { cajas.push(b); return { p, x, y, lx, ly, anc: lado }; }
      }
    }
    return { p, x, y, lx: x + 9, ly: y - 9, anc: "start" as const };
  });
}
