// Sesión firmada (HMAC-SHA256) para el acceso con clave. Funciona en Node y en Edge (Web Crypto).
export const COOKIE = "brecha_sesion";
const DURACION_S = 60 * 60 * 24 * 30; // 30 días

const enc = new TextEncoder();

async function clave(secreto: string) {
  return crypto.subtle.importKey("raw", enc.encode(secreto), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
}

function hex(buf: ArrayBuffer) {
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function secreto() {
  return process.env.VISOR_SECRETO || process.env.VISOR_CLAVE || "";
}

export async function crearToken(): Promise<{ token: string; maxAge: number }> {
  const exp = Math.floor(Date.now() / 1000) + DURACION_S;
  const firma = hex(await crypto.subtle.sign("HMAC", await clave(secreto()), enc.encode(`v1.${exp}`)));
  return { token: `v1.${exp}.${firma}`, maxAge: DURACION_S };
}

export async function tokenValido(token: string | undefined): Promise<boolean> {
  if (!token || !secreto()) return false;
  const [v, exp, firma] = token.split(".");
  if (v !== "v1" || !exp || !firma || Number(exp) < Date.now() / 1000) return false;
  const esperada = hex(await crypto.subtle.sign("HMAC", await clave(secreto()), enc.encode(`v1.${exp}`)));
  return iguales(esperada, firma);
}

// comparación en tiempo constante
export function iguales(a: string, b: string) {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}
