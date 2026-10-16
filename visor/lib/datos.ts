import crudo from "@/data/visor.json";

export type Fila = Record<string, number | string | null>;
export type Indicador = { clave: string; nombre: string; grupo: string; unidad: string; color: "percepcion" | "registro" | "div"; fuente: string; sexo: boolean };
export type Ame = { variable: string; etiqueta: string; ame_pp: number; ic_inf: number; ic_sup: number; p: number };

type Datos = {
  generado: string;
  resumen: any;
  geo: { ancho: number; alto: number; localidades: { id: number; nombre: string; d: string; cx: number; cy: number }[]; upz: { id: number; nombre: string; localidad: number | null; d: string }[] };
  indicadores: Indicador[];
  valores: Record<string, Record<string, Record<string, number | null>>>;
  upz: Record<string, { nombre: string; valores: Record<string, number>; casos: Record<string, number> }>;
  panel: Fila[];
  /** Serie validada (src/validacion_registro.py): SIEDCO donde la capa SCJ tiene quiebre; `casos_capa_scj` guarda la capa. */
  serie_delitos: { codigo: string; tipo: string; anio: number; casos: number; fuente: string; estado: string; casos_capa_scj: number | null }[];
  serie_incidentes: { codigo: string; tipo: string; anio: number; casos: number }[];
  ame: Record<"m_hechos" | "m_calif" | "m_ciudad" | "m_miedo", Ame[]>;
  ame_efectos_fijos: Ame[];
  lpm_wild: { variable: string; etiqueta: string; coef_pp: number; p_cluster: number; p_wild: number }[];
  auc: { bloque: string; variables: string; auc: number; auc_sd: number; pliegues: number }[];
  emv_genero: Record<string, Ame[]>;
  ibs: Fila[];
  cifra_oculta: Fila[];
  validaciones: { prueba: string; rho: number; p: number; ic_inf: number; ic_sup: number; n: number; p_bh: number }[];
  escenarios: { grupo: string; localidad: number; p00: number; p10: number; p01: number; p11: number; observado: number }[];
  medias: Record<string, number>;
  n: Record<string, number>;
  fuentes: { clave: string; entidad: string; conjunto: string; portal: string; url: string }[];
};

export const D = crudo as unknown as Datos;
export const R = D.resumen;

export const LOCALIDADES: Record<number, string> = Object.fromEntries(D.geo.localidades.map((l) => [l.id, l.nombre]));

const nf = (dec: number) => new Intl.NumberFormat("es-CO", { minimumFractionDigits: dec, maximumFractionDigits: dec });
export function fmt(x: number | null | undefined, dec = 1) {
  if (x === null || x === undefined || Number.isNaN(x)) return "s. d.";
  return nf(dec).format(x).replace("-", "−");
}
export function signo(x: number, dec = 1) {
  return `${x > 0 ? "+" : x < 0 ? "−" : ""}${fmt(Math.abs(x), dec)}`;
}
export function pval(p: number) {
  return p < 0.001 ? "p < 0,001" : `p = ${fmt(p, 3)}`;
}

/** Quintiles para colorear (5 clases) */
export function cortes(vals: number[]): number[] {
  const v = [...vals].sort((a, b) => a - b);
  const q = (f: number) => {
    const i = (v.length - 1) * f, lo = Math.floor(i), hi = Math.ceil(i);
    return v[lo] + (v[hi] - v[lo]) * (i - lo);
  };
  return [0.2, 0.4, 0.6, 0.8].map(q);
}
export function clase(x: number, c: number[]) {
  let k = 1;
  for (const t of c) if (x > t) k++;
  return k;
}
export function colorVar(tipo: string, k: number) {
  if (tipo === "div") return ["--d-neg2", "--d-neg1", "--d-0", "--d-pos1", "--d-pos2"][k - 1];
  return `--${tipo === "registro" ? "r" : "p"}${k}`;
}
/** Para el índice divergente: cortes simétricos alrededor de 0 */
export function claseDiv(x: number) {
  if (x <= -1) return 1;
  if (x <= -0.33) return 2;
  if (x < 0.33) return 3;
  if (x < 1) return 4;
  return 5;
}
