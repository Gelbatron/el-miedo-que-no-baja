import { D } from "./datos";

/** La historia que cuenta el visor, en el orden en que se recorre. */
export const ACTOS = ["El problema", "Lo que hicimos", "Lo que encontramos", "Por qué importa", "Para revisar"] as const;
export const RECORRIDO: { href: string; titulo: string; acto: number }[] = [
  { href: "/", titulo: "La historia en cuatro pasos", acto: 0 },
  { href: "/tendencia", titulo: "Lo que se registra, año por año", acto: 0 },
  { href: "/mapa", titulo: "El mapa del miedo y el de las denuncias", acto: 0 },
  { href: "/brecha", titulo: "El índice y el delito que no se denuncia", acto: 1 },
  { href: "/que-explica", titulo: "Qué le da miedo a la gente", acto: 2 },
  { href: "/genero", titulo: "Las mujeres", acto: 2 },
  { href: "/simulador", titulo: "¿Cuánto bajaría el miedo?", acto: 3 },
  { href: "/indicador", titulo: "Cómo saber si funciona", acto: 3 },
  { href: "/metodologia", titulo: "Cómo lo hicimos, paso a paso", acto: 4 },
  { href: "/datos", titulo: "Los datos para descargar", acto: 4 },
  { href: "/entregables", titulo: "Todos los entregables", acto: 4 },
];

/** Franja de la pandemia en las series anuales (cubre 2020 y 2021). */
export const BANDA_PANDEMIA = { desde: 2019.55, hasta: 2021.45, etiqueta: "Pandemia" };

const serie = (cod: string) => Object.fromEntries(D.serie_delitos.filter((f) => f.codigo === cod).map((f) => [f.anio, f.casos])) as Record<number, number>;
const pct = (a: number, b: number) => (b / a - 1) * 100;

/** El efecto pandemia en el registro, calculado de la serie de la SCJ (enero-agosto). */
export const PANDEMIA = (() => {
  const hp = serie("HP"), vi = serie("VI");
  const caidas2023 = ["HP", "HCE", "HM", "HR", "HA"].map((c) => { const s = serie(c); return -pct(s[2022], s[2023]); });
  return {
    hurto2020: pct(hp[2019], hp[2020]),
    hurto2022sobre2019: (hp[2022] / hp[2019]) * 100,
    hurto2022a2026: pct(hp[2022], hp[2026]),
    caida2023min: Math.min(...caidas2023),
    caida2023max: Math.max(...caidas2023),
    vif2020: pct(vi[2019], vi[2020]),
    vif2022a2026: pct(vi[2022], vi[2026]),
  };
})();

/** «a, b y c» */
export const enLista = (xs: string[]) => (xs.length > 1 ? `${xs.slice(0, -1).join(", ")} y ${xs[xs.length - 1]}` : xs[0] ?? "");
