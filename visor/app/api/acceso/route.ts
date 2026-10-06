import { NextResponse } from "next/server";
import { COOKIE, crearToken, iguales } from "@/lib/sesion";

export async function POST(request: Request) {
  const form = await request.formData();
  const clave = String(form.get("clave") ?? "");
  const siguiente = String(form.get("siguiente") ?? "/");
  const destino = siguiente.startsWith("/") && !siguiente.startsWith("//") ? siguiente : "/";
  const esperada = process.env.VISOR_CLAVE ?? "";

  if (!esperada || !iguales(clave.trim(), esperada)) {
    const url = new URL("/acceso", request.url);
    url.searchParams.set("error", "1");
    if (destino !== "/") url.searchParams.set("siguiente", destino);
    return NextResponse.redirect(url, 303);
  }
  const { token, maxAge } = await crearToken();
  const res = NextResponse.redirect(new URL(destino, request.url), 303);
  res.cookies.set(COOKIE, token, { httpOnly: true, secure: true, sameSite: "lax", path: "/", maxAge });
  return res;
}
