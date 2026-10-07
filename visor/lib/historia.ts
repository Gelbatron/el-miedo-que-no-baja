import { D } from "./datos";
import { F } from "./frentes";

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

/** El hurto a personas en las dos series: la capa abierta de la SCJ y el registro de la Policía (SIEDCO), enero-agosto. */
export const HURTO = (() => {
  const h = Object.fromEntries(F.registro.hurto_personas.map((f) => [f.anio, f])) as Record<number, (typeof F.registro.hurto_personas)[number]>;
  const raz = F.registro.razones.filter((r) => r.codigo === "HP" && r.anio < 2023).map((r) => r.razon_scj_siedco ?? 0);
  return {
    capa2022a2026: pct(h[2022].capa_scj, h[2026].capa_scj),
    capa2019a2026: pct(h[2019].capa_scj, h[2026].capa_scj),
    capa2023: pct(h[2022].capa_scj, h[2023].capa_scj),
    policia2022a2026: pct(h[2022].siedco, h[2026].siedco),
    policia2019a2026: pct(h[2019].siedco, h[2026].siedco),
    policia2023: pct(h[2022].siedco, h[2023].siedco),
    policia2022: h[2022].siedco, policia2026: h[2026].siedco, capa2022: h[2022].capa_scj, capa2026: h[2026].capa_scj,
    razonMin: Math.min(...raz), razonMax: Math.max(...raz),
  };
})();

/** El efecto pandemia en el registro (enero-agosto): hurto con la serie de la Policía; violencia intrafamiliar con la SCJ, validada. */
export const PANDEMIA = (() => {
  const vi = serie("VI");
  const h = Object.fromEntries(F.registro.hurto_personas.map((f) => [f.anio, f.siedco])) as Record<number, number>;
  return {
    hurto2020: pct(h[2019], h[2020]),
    hurto2022sobre2019: (h[2022] / h[2019]) * 100,
    hurto2022a2026: HURTO.policia2022a2026,
    hurto2023: HURTO.policia2023,
    vif2020: pct(vi[2019], vi[2020]),
    vif2022a2026: pct(vi[2022], vi[2026]),
  };
})();

/** «a, b y c» */
export const enLista = (xs: string[]) => (xs.length > 1 ? `${xs.slice(0, -1).join(", ")} y ${xs[xs.length - 1]}` : xs[0] ?? "");
