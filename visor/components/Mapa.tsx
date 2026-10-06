"use client";
import { D, clase, claseDiv, colorVar, cortes, fmt } from "@/lib/datos";

type Props = {
  valores: Record<string, number | null>;
  tipo: "percepcion" | "registro" | "div";
  unidad: string;
  titulo?: string;
  nivel?: "localidad" | "upz";
  seleccion?: number | null;
  onSelect?: (id: number) => void;
  dec?: number;
  alto?: number;
};

export function Mapa({ valores, tipo, unidad, titulo, nivel = "localidad", seleccion, onSelect, dec = 1, alto = 600 }: Props) {
  const { ancho, alto: h } = D.geo;
  const nums = Object.values(valores).filter((v): v is number => v !== null && Number.isFinite(v));
  const c = cortes(nums);
  const kDe = (x: number) => (tipo === "div" ? claseDiv(x) : clase(x, c));
  const formas = nivel === "upz" ? D.geo.upz : D.geo.localidades;
  const etiquetaLeyenda =
    tipo === "div"
      ? ["≤ −1", "−1 a −0,33", "−0,33 a 0,33", "0,33 a 1", "≥ 1"]
      : [0, 1, 2, 3, 4].map((i) => {
          const lo = i === 0 ? Math.min(...nums) : c[i - 1];
          const hi = i === 4 ? Math.max(...nums) : c[i];
          return `${fmt(lo, dec)}–${fmt(hi, dec)}`;
        });
  return (
    <figure style={{ margin: 0, display: "grid", gap: 10 }}>
      {titulo && <figcaption style={{ fontWeight: 650 }}>{titulo}</figcaption>}
      <svg className="g" viewBox={`-4 -4 ${ancho + 8} ${h + 8}`} style={{ maxHeight: alto, margin: "0 auto" }} role="img" aria-label={titulo}>
        {formas.map((f) => {
          const v = valores[String(f.id)];
          const ok = v !== null && v !== undefined && Number.isFinite(v);
          const fill = ok ? `var(${colorVar(tipo, kDe(v as number))})` : "var(--sin-dato)";
          const loc = "localidad" in f && nivel === "upz" ? ` · ${f.localidad ? D.geo.localidades.find((l) => l.id === f.localidad)?.nombre ?? "" : ""}` : "";
          const tip = `<b>${f.nombre}</b>${loc}<br>${ok ? `${fmt(v as number, dec)} ${unidad}` : "sin dato"}`;
          return (
            <path
              key={f.id}
              d={f.d}
              fill={fill}
              className={`geo${seleccion === f.id ? " sel" : ""}`}
              data-tip={tip}
              tabIndex={onSelect ? 0 : -1}
              aria-label={`${f.nombre}: ${ok ? fmt(v as number, dec) : "sin dato"}`}
              onClick={() => onSelect?.(f.id)}
              onKeyDown={(e) => { if (e.key === "Enter") onSelect?.(f.id); }}
            />
          );
        })}
        {nivel === "upz" &&
          D.geo.localidades.map((l) => <path key={`b${l.id}`} d={l.d} fill="none" stroke="var(--tinta)" strokeWidth={0.9} opacity={0.55} pointerEvents="none" />)}
      </svg>
      <div className="leyenda" aria-label="Leyenda">
        {etiquetaLeyenda.map((t, i) => (
          <span key={t} className="mono" style={{ fontSize: ".74rem" }}><i style={{ background: `var(${colorVar(tipo, i + 1)})` }} />{t}</span>
        ))}
      </div>
    </figure>
  );
}
