import crudo from "@/data/frentes.json";

// Resultados de los cuatro frentes y de los modelos (los exporta src/frentes.py).
export type Tendencia = {
  codigo: string; tipo: string; estado: "validada" | "quiebre" | "sin_validar"; ventana: string; fuente_bogota: string;
  ultimo_anio: number; casos_2019: number; casos_2022: number; casos_ultimo: number;
  cambio_bruto_2022_ultimo_pct: number; post_cambio_anual_pct: number; post_ic_inf: number; post_ic_sup: number; post_p: number;
  irr_2023_vs_2022: number; irr_2023_ic_inf: number; irr_2023_ic_sup: number; irr_2023_p: number; irr_ultimo_vs_2019: number;
};
export type Ficha = { fuente: string; frente: string; entidad: string; tipo: string; anios: number; ultimo: number; verificacion: string; score: number; semaforo: "alta" | "media" | "baja"; advertencia: string };
export type HurtoAnio = {
  anio: number; capa_scj: number; siedco: number; siedco_anio_completo: number | null; ecsc_victimizacion: number | null; ecsc_denuncia: number | null;
  ccb_victimizacion: number | null; ccb_denuncia: number | null; capa_scj_2022_100: number; siedco_2022_100: number; ccb_victimizacion_2022_100: number | null;
};
type Fila = Record<string, number | string | null>;

type Datos = {
  tendencias: Tendencia[];
  ml: {
    completo: { modelo: string; mean: number; std: number }[];
    sin_calificaciones: { modelo: string; mean: number; std: number }[];
    bloques_sin_calificaciones: { bloque: string; mean: number; std: number }[];
    contexto_localidad: { spec: string; mean: number; std: number }[];
  };
  confianza_policia: { bogota_desconfia_pct: number };
  homicidios_localidad?: Fila[];
  confiabilidad: Ficha[];
  tipologia?: { localidades: Fila[]; perfiles_z: Fila[] };
  registro: {
    hurto_personas: HurtoAnio[];
    razones: { codigo: string; anio: number; scj: number | null; siedco: number | null; inmlcf: number | null; razon_scj_siedco: number | null; razon_scj_inmlcf: number | null }[];
    estado: { codigo: string; tipo: string; estado: string; desde: number | null; fuente_bogota: string; detalle: string; razon_min_2018_2022: number | null; razon_max_2018_2022: number | null }[];
    etiquetas: { columna_capa: string; dice: string; coincide_con_siedco: string; que_es_en_siedco: string; capa_2023: number; capa_2024: number; capa_2025: number; siedco_2023: number; siedco_2024: number; siedco_2025: number }[];
  };
  encuestas: { anio: number; fuente: string; indicador: string; delito: string; valor: number }[];
  genero: { localidades?: Fila[]; perfil?: Fila[]; acoso?: Fila[]; pruebas?: Fila[] };
  movilidad?: { pruebas: Fila[] };
};

export const F = crudo as unknown as Datos;
export const tendencia = (codigo: string) => F.tendencias.find((t) => t.codigo === codigo)!;
export const hurto = (anio: number) => F.registro.hurto_personas.find((h) => h.anio === anio)!;
export const encuesta = (fuente: "DANE" | "CCB", indicador: string, delito: string, anio: number) =>
  F.encuestas.find((e) => e.fuente.startsWith(fuente) && e.indicador === indicador && e.delito === delito && e.anio === anio)?.valor;
export const ficha = (fuente: string) => F.confiabilidad.find((f) => f.fuente === fuente);
export const COLOR_SEMAFORO = { alta: "var(--hombres)", media: "var(--oro)", baja: "var(--rojo)" } as const;
