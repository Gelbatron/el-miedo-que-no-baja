import type { Metadata } from "next";
import { Bricolage_Grotesque, Hanken_Grotesk, IBM_Plex_Mono } from "next/font/google";
import { Navegacion } from "@/components/Navegacion";
import { Tooltip } from "@/components/Tooltip";
import "./globals.css";

const display = Bricolage_Grotesque({ subsets: ["latin"], weight: ["600", "700", "800"], variable: "--f-display" });
const texto = Hanken_Grotesk({ subsets: ["latin"], weight: ["400", "500", "600", "700"], variable: "--f-texto" });
const mono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--f-mono" });

export const metadata: Metadata = {
  title: "El miedo que no baja · Visor de la brecha de seguridad",
  description: "Inseguridad percibida frente a delito registrado en Bogotá. DataJam Edición 5 · The data squad.",
  robots: { index: false, follow: false },
  icons: { icon: "/icon.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={`${display.variable} ${texto.variable} ${mono.variable}`}>
      <body>
        <Navegacion />
        <main className="contenedor">{children}</main>
        <footer className="pie">
          <div className="contenedor">
            <span>
              Bogotá DataJam Edición 5 · Equipo #16 <b>The data squad</b>: Rafael Estiven Londoño Camacho, Brandow Brusly
              León Rodríguez y Samuel Esteban Riveros Cubides.
            </span>
            <span>
              Fuentes: SCJ, SDP, SCRD (Encuesta Bienal de Cultura Ciudadana 2025), Encuesta Mundial de Valores 2024, UAESP,
              DADEP e IDECA. Todas las cifras salen del notebook reproducible del repositorio.
            </span>
          </div>
        </footer>
        <Tooltip />
      </body>
    </html>
  );
}
