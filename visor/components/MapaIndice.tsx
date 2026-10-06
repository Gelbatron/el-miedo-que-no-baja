"use client";
import { D } from "@/lib/datos";
import { Mapa } from "./Mapa";

export function MapaIndice() {
  return <Mapa valores={D.valores.ibs.total} tipo="div" unidad="(z)" dec={2} />;
}
