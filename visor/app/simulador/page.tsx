import { EnSimple } from "@/components/EnSimple";
import { D, R, fmt } from "@/lib/datos";
import { Simulador } from "@/components/Simulador";

export const metadata = { title: "Simulador · El miedo que no baja" };

const esc = D.escenarios.find((e) => e.grupo === "total" && e.localidad === 0)!;
const personas50 = ((esc.p00 - (esc.p00 + esc.p10 + esc.p01 + esc.p11) / 4) / 100) * (R.adultos_urbanos_bienal as number);

export default function PaginaSimulador() {
  return (
    <div className="contenedor pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Prescriptivo · escenarios del modelo</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>¿Cuánto bajaría el miedo si arreglamos el entorno?</h1>
        <EnSimple>{`Muevan los dos controles: si mejora el alumbrado y dejan de verse atracos en parte de los parques, ¿cuánta gente dejaría de sentir insegura su zona? Con la mitad y la mitad, del orden de ${fmt(personas50 / 1000, 0)} mil personas. Es una estimación del modelo, no una promesa.`}</EnSimple>
        <p className="bajada">
          Mueve las dos palancas que el modelo identifica: el alumbrado de la zona y los atracos en el parque cercano. El visor recalcula el porcentaje que
          se sentiría inseguro en cada localidad, para comparar dónde rinde más una misma inversión.
        </p>
      </header>
      <Simulador />
    </div>
  );
}
