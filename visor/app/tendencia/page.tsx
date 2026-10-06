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
        <p className="bajada">
          Comparamos siempre enero a agosto, el único periodo que la SCJ publica para todos los años, incluido 2026. El {fmt(R.ciudad_peor_que_antes_pct)} % de los adultos cree que la ciudad
          está menos segura que el año pasado (Bienal 2025), mientras el hurto a personas registrado cambió {signo(cambio("HP"))} % entre 2024 y 2025.
        </p>
      </header>
      <SerieDelitos />
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
