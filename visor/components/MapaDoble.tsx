"use client";
import { D } from "@/lib/datos";
import { Mapa } from "./Mapa";

export function MapaDoble() {
  return (
    <div className="rejilla r2">
      <Mapa valores={D.valores.zona_insegura.total} tipo="percepcion" unidad="%" titulo="Califica mala la seguridad de su zona (Bienal 2025)" />
      <Mapa valores={D.valores.delitos_alto_impacto_100k.total} tipo="registro" unidad="por 100.000 hab." dec={0} titulo="Delitos de alto impacto por 100.000 hab. (SCJ, ene-ago 2025)" />
    </div>
  );
}
