// Íconos de trazo, pensados para ir sobre el círculo oro (trazo oscuro, como los íconos de trámites del Distrito).
const P = { fill: "none", stroke: "#3d2a00", strokeWidth: 2.2, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

export function Icono({ nombre }: { nombre: "encuesta" | "parque" | "mujer" | "datos" }) {
  return (
    <svg viewBox="0 0 48 48" width="40" height="40" aria-hidden="true">
      {nombre === "encuesta" && (
        <g {...P}>
          <rect x="11" y="8" width="26" height="33" rx="3" />
          <path d="M18 8v-2h12v2" />
          <path d="M16 19l2.5 2.5L23 17M16 29l2.5 2.5L23 27" />
          <path d="M27 20h5M27 30h5" />
        </g>
      )}
      {nombre === "parque" && (
        <g {...P}>
          <path d="M14 41V18" />
          <path d="M9 18h10l-2.5-5h-5z" />
          <path d="M14 22c2 0 3 1 3 3" opacity=".6" />
          <circle cx="32" cy="20" r="7" />
          <path d="M32 27v14M24 41h18" />
        </g>
      )}
      {nombre === "mujer" && (
        <g {...P}>
          <circle cx="24" cy="14" r="6" />
          <path d="M24 20l-7 12h14z" />
          <path d="M20.5 32v8M27.5 32v8" />
          <path d="M33 10a14 14 0 0 1 0 20M15 10a14 14 0 0 0 0 20" opacity=".55" />
        </g>
      )}
      {nombre === "datos" && (
        <g {...P}>
          <path d="M24 42s-12-11.5-12-20a12 12 0 0 1 24 0c0 8.5-12 20-12 20z" />
          <path d="M19 25v-4M24 25v-8M29 25v-6" />
        </g>
      )}
    </svg>
  );
}
