import { EnSimple } from "@/components/EnSimple";
import { VideoGuiado, type DatosVideo } from "@/components/VideoGuiado";
import datos from "@/data/video.json";

export const metadata = { title: "Video · El miedo que no baja" };

export default function Video() {
  const d = datos as unknown as DatosVideo;
  const min = Math.round(d.duracion / 60);
  return (
    <div className="contenedor pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">El video · {min} minutos · para la Secretaría General de Bogotá</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Lo que hay detrás de las cifras de seguridad</h1>
        <EnSimple>
          Qué dice cada fuente por separado, qué encontramos al cruzarlas, cómo lo hicimos y los 4 frentes de trabajo que proponemos.
          Debajo del video está la explicación de cada capítulo con sus cifras y fuentes; al lado, todo lo que se dice, palabra por palabra.
        </EnSimple>
      </header>
      <VideoGuiado datos={d} />
      <p className="vg-pie">
        Video del equipo The data squad para el Bogotá DataJam 2026; no es una pieza oficial de la Alcaldía. Las cifras salen del repositorio del proyecto y
        cada una está en la página del visor que enlaza su capítulo. <a href={d.video} download>Descargar el video (MP4)</a>
      </p>
    </div>
  );
}
