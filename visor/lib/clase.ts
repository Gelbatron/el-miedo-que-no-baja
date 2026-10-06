import crudo from "@/data/clase.json";

// Datos de la presentación interactiva: los genera src/clase.py desde los mismos modelos del pipeline.
export type FilaIndice = { localidad: number; nombre: string; zona_insegura: number; delitos_100k: number; z_percepcion: number; z_registro: number; ibs: number };
type Datos = {
  indice: FilaIndice[];
  logit: { y: string; n: number; coef: Record<string, number>; referencia: Record<string, number>; rangos_localidad: Record<string, [number, number]> };
  bootstrap: Record<string, number[]>;
};

export const C = crudo as unknown as Datos;

/** Probabilidad (%) que da el logit principal para un perfil. */
export function prob(x: Record<string, number>) {
  const c = C.logit.coef;
  let s = c.const;
  for (const [k, v] of Object.entries(x)) s += (c[k] ?? 0) * v;
  return 100 / (1 + Math.exp(-s));
}

/** Percentil simple (para el intervalo de las réplicas). */
export function percentil(v: number[], q: number) {
  const s = [...v].sort((a, b) => a - b);
  const i = (s.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i);
  return s[lo] + (s[hi] - s[lo]) * (i - lo);
}
