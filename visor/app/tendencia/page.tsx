import { EnSimple } from "@/components/EnSimple";
import { PANDEMIA } from "@/lib/historia";
import { D, R, fmt, signo } from "@/lib/datos";
import { SerieDelitos } from "@/components/SerieDelitos";

export const metadata = { title: "Tendencia · El miedo que no baja" };

export default function Tendencia() {
  const ult = (cod: string, a: number) => D.serie_delitos.find((f) => f.codigo === cod && f.anio === a)?.casos ?? 0;
  const cambio = (cod: string) => ((ult(cod, 2025) / ult(cod, 2024)) - 1) * 100;
  return (
    <div className="contenedor pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Registro oficial 2018-2026 · Secretaría de Seguridad</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Los delitos contra el patrimonio bajan; el miedo no lo registra</h1>
        <EnSimple>{`El hurto registrado viene bajando, con un bache por la pandemia en 2020 (${signo(PANDEMIA.hurto2020, 0)} %). En 2022 volvió casi a lo de antes y desde ahí cayó ${fmt(-PANDEMIA.hurto2022a2026, 0)} %. La violencia intrafamiliar, en cambio, subió ${fmt(PANDEMIA.vif2022a2026, 0)} % desde 2022. Ojo: en 2023 cayeron todos los hurtos a la vez; puede ser menos delito o menos denuncia.`}</EnSimple>
        <p className="bajada">
          Comparamos siempre enero a agosto, el único periodo que la SCJ publica para todos los años, incluido 2026. El {fmt(R.ciudad_peor_que_antes_pct)} % de los adultos cree que la ciudad
          está menos segura que el año pasado (Bienal 2025), mientras el hurto a personas registrado cambió {signo(cambio("HP"))} % entre 2024 y 2025.
        </p>
      </header>
      <SerieDelitos />
      <section className="tarjeta" style={{ borderLeft: "5px solid var(--oro)" }}>
        <h3>El efecto pandemia</h3>
        <p style={{ color: "var(--tinta-2)" }}>
          En 2020 el hurto a personas registrado cayó {fmt(-PANDEMIA.hurto2020, 0)} % por el encierro. En 2022 volvió al {fmt(PANDEMIA.hurto2022sobre2019, 0)} % de lo que era en 2019.
          Desde ahí siguió bajando: {fmt(-PANDEMIA.hurto2022a2026, 0)} % menos entre 2022 y 2026. O sea, la caída no es solo pandemia.
        </p>
        <p style={{ color: "var(--tinta-2)" }}>
          Pero hay una señal para revisar: entre 2022 y 2023 todos los tipos de hurto cayeron a la vez, entre {fmt(PANDEMIA.caida2023min, 0)} % y {fmt(PANDEMIA.caida2023max, 0)} % en un solo año
          (personas, celulares, motos, residencias y automotores). Una caída tan pareja puede ser menos delito o menos denuncia, y el registro solo no lo distingue.
          Por eso proponemos medir también con encuestas de victimización.
        </p>
        <p style={{ color: "var(--tinta-2)" }}>
          La violencia intrafamiliar casi no se movió con la pandemia ({fmt(PANDEMIA.vif2020, 0)} % en 2020) y desde 2022 subió {fmt(PANDEMIA.vif2022a2026, 0)} %.
        </p>
      </section>
      <section className="tarjeta plana">
        <h3>Cómo leer esta serie</h3>
        <p style={{ color: "var(--tinta-2)" }}>
          Un delito registrado es una denuncia o un caso conocido por la autoridad, no un delito ocurrido. Que el hurto registrado baje puede reflejar menos hurtos
          o menos denuncias. Por eso la serie se lee junto a la cifra oculta (página La brecha): en la periferia hay hasta {fmt(R.cifra_oculta_max[1])} víctimas por cada delito registrado.
        </p>
      </section>
    </div>
  );
}
