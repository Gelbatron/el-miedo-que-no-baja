import type { ReactNode } from "react";

/** Lo que dice la página, en palabras de todos los días. Va antes del detalle técnico. */
export function EnSimple({ children }: { children: ReactNode }) {
  return (
    <div className="en-simple">
      <b>En simple</b>
      <p>{children}</p>
    </div>
  );
}
