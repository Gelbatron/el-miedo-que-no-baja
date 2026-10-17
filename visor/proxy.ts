import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE, tokenValido } from "./lib/sesion";

// Todo el visor (páginas, datos y descargas) exige la clave, salvo la pantalla de acceso.
export async function proxy(request: NextRequest) {
  // solo para revisión local (nunca se define en Vercel)
  if (process.env.VISOR_SIN_CLAVE === "1" && process.env.VERCEL !== "1") return NextResponse.next();
  if (await tokenValido(request.cookies.get(COOKIE)?.value)) return NextResponse.next();
  const url = new URL("/acceso", request.url);
  const destino = request.nextUrl.pathname + request.nextUrl.search;
  if (destino !== "/") url.searchParams.set("siguiente", destino);
  return NextResponse.redirect(url);
}

export const config = {
  matcher: ["/((?!acceso|api/acceso|equipo/|_next/static|_next/image|favicon.ico|icon.svg|robots.txt).*)"],
};
