import { EnSimple } from "@/components/EnSimple";
import { HURTO, PANDEMIA } from "@/lib/historia";
import { D, R, fmt, signo } from "@/lib/datos";
import { SerieDelitos } from "@/components/SerieDelitos";

export const metadata = { title: "Tendencia · El miedo que no baja" };

export default function Tendencia() {
  const ult = (cod: string, a: number) => D.serie_delitos.find((f) => f.codigo === cod && f.anio === a)?.casos ?? 0;
  const cambio = (cod: string) => ((ult(cod, 2025) / ult(cod, 2024)) - 1) * 100;
  return (
    <div className="contenedor pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Registro oficial 2018-2026 · validado con la Policía y Medicina Legal</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>El hurto casi no bajó; la violencia sube</h1>
        <EnSimple>{`Con el registro de la Policía, el hurto a personas de 2026 está ${fmt(Math.abs(HURTO.policia2022a2026), 0)} % por debajo de 2022. La capa abierta de la SCJ dice ${fmt(Math.abs(HURTO.capa2022a2026), 0)} %, pero hasta 2022 contaba más del doble de hurtos que la Policía. La violencia intrafamiliar subió ${fmt(PANDEMIA.vif2022a2026, 0)} % desde 2022.`}</EnSimple>
        <p className="bajada">
          Comparamos siempre enero a agosto, el único periodo publicado para todos los años, incluido 2026. Cada serie se contrastó con otra fuente: homicidios, lesiones, delitos sexuales y
          violencia intrafamiliar coinciden con la Policía todos los años; los hurtos de la capa SCJ solo desde 2023. El {fmt(R.ciudad_peor_que_antes_pct)} % de los adultos cree que la ciudad
          está menos segura que el año pasado (Bienal 2025), mientras el hurto a personas registrado cambió {signo(cambio("HP"))} % entre 2024 y 2025.
        </p>
      </header>
      <SerieDelitos />
      <section className="tarjeta" style={{ borderLeft: "5px solid var(--oro)" }}>
        <h3>El efecto pandemia y el quiebre de 2023</h3>
        <p style={{ color: "var(--tinta-2)" }}>
          Con la serie de la Policía, en 2020 el hurto a personas cayó {fmt(-PANDEMIA.hurto2020, 0)} % por el encierro y en 2022 volvió al {fmt(PANDEMIA.hurto2022sobre2019, 0)} % de lo que era en 2019.
          En 2023 subió {fmt(PANDEMIA.hurto2023, 0)} %, y en 2026 está {fmt(Math.abs(PANDEMIA.hurto2022a2026), 0)} % por debajo de 2022.
        </p>
        <p style={{ color: "var(--tinta-2)" }}>
          La capa abierta de la SCJ cuenta {fmt(HURTO.razonMin, 1)} a {fmt(HURTO.razonMax, 1)} veces más hurtos a personas que la Policía de 2018 a 2022, y desde 2023 coincide caso por caso.
          Por eso en esa capa el hurto «cae» {fmt(Math.abs(HURTO.capa2023), 0)} % en 2023. La encuesta del DANE no muestra menos denuncia ese periodo: la denuncia del hurto pasó de 36 % (2021) a 43 % (2023).
          En esta página, hurto a personas, residencias y automotores salen del registro de la Policía; los demás delitos, de la SCJ, validados.
        </p>
        <p style={{ color: "var(--tinta-2)" }}>
          La violencia intrafamiliar casi no se movió con la pandemia ({fmt(PANDEMIA.vif2020, 0)} % en 2020) y desde 2022 subió {fmt(PANDEMIA.vif2022a2026, 0)} %.
        </p>
      </section>
      <section className="tarjeta plana">
        <h3>Cómo leer esta serie</h3>
        <p style={{ color: "var(--tinta-2)" }}>
          Un delito registrado es una denuncia o un caso conocido por la autoridad, no un delito ocurrido. Que el hurto registrado baje puede reflejar menos hurtos
          o menos denuncias, y una serie puede cambiar de método. Por eso la serie se valida con otra fuente y se lee junto a la cifra oculta (página La brecha):
          en la periferia hay hasta {fmt(R.cifra_oculta_max[1])} víctimas por cada delito registrado.
        </p>
      </section>
    </div>
  );
}
