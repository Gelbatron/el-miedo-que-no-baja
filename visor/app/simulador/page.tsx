import { Simulador } from "@/components/Simulador";

export const metadata = { title: "Simulador · El miedo que no baja" };

export default function PaginaSimulador() {
  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Prescriptivo · escenarios del modelo</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>¿Cuánto bajaría el miedo si arreglamos el entorno?</h1>
        <p className="bajada">
          Mueve las dos palancas que el modelo identifica: el alumbrado de la zona y los atracos en el parque cercano. El visor recalcula el porcentaje que
          se sentiría inseguro en cada localidad, para comparar dónde rinde más una misma inversión.
        </p>
      </header>
      <Simulador />
    </div>
  );
}
