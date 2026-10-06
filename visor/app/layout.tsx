import type { Metadata } from "next";
import { IBM_Plex_Mono, Kanit, Montserrat, Work_Sans } from "next/font/google";
import { Navegacion } from "@/components/Navegacion";
import { Tooltip } from "@/components/Tooltip";
import "./globals.css";

const display = Montserrat({ subsets: ["latin"], weight: ["600", "700", "800"], variable: "--f-display" });
const heroe = Kanit({ subsets: ["latin"], weight: ["600", "700"], variable: "--f-heroe" });
const texto = Work_Sans({ subsets: ["latin"], weight: ["400", "500", "600"], variable: "--f-texto" });
const mono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--f-mono" });

export const metadata: Metadata = {
  title: "El miedo que no baja · Visor de la brecha de seguridad",
  description: "Inseguridad percibida frente a delito registrado en Bogotá. Bogotá DataJam Edición 5 · The data squad.",
  robots: { index: false, follow: false },
  icons: { icon: "/icon.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={`${display.variable} ${heroe.variable} ${texto.variable} ${mono.variable}`}>
      <body>
        <Navegacion />
        <main>{children}</main>
        <footer className="pie">
          <div className="contenedor">
            <span>
              <b>El miedo que no baja</b> · Bogotá DataJam Edición 5 · Equipo #16 <b>The data squad</b>: Rafael Estiven Londoño Camacho,
              Brandow Brusly León Rodríguez y Samuel Esteban Riveros Cubides.
            </span>
            <span>
              Fuentes: Secretaría de Seguridad (SCJ), Secretaría de Planeación (SDP), Secretaría de Cultura (Encuesta Bienal de Cultura
              Ciudadana 2025), Encuesta Mundial de Valores 2024, UAESP, DADEP e IDECA. Todas las cifras salen del notebook reproducible.
            </span>
            <span className="aviso">
              Proyecto académico presentado al Bogotá DataJam 5 (Alcaldía de Bogotá · UCompensar). No es un sitio oficial de la Alcaldía de Bogotá
              ni de sus entidades.
            </span>
          </div>
        </footer>
        <Tooltip />
      </body>
    </html>
  );
}
