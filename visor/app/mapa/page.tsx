import { EnSimple } from "@/components/EnSimple";
import { Explorador } from "@/components/Explorador";

export const metadata = { title: "Mapa · El miedo que no baja" };

export default function PaginaMapa() {
  return (
    <div className="contenedor pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Explorador territorial</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Cada indicador en el mapa</h1>
        <EnSimple>Cada localidad se pinta según el indicador que elijan. Oro es lo que la gente siente; azul, lo que el Estado registra. Comparen los dos: no dibujan el mismo mapa.</EnSimple>
        <p className="bajada">
          Veinte indicadores integrados por código de localidad: percepción y entorno (Bienal 2025), victimización (EMV 2024), registro oficial
          (SCJ y Línea 123) y contexto. Las llamadas a la Línea 123 también se ven por UPZ. El oro es lo que se siente; el azul, lo que se registra.
        </p>
      </header>
      <Explorador />
    </div>
  );
}
