import { NextResponse } from "next/server";
import { COOKIE } from "@/lib/sesion";

export async function POST(request: Request) {
  const res = NextResponse.redirect(new URL("/acceso", request.url), 303);
  res.cookies.set(COOKIE, "", { path: "/", maxAge: 0 });
  return res;
}
