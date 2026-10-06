import type { NextConfig } from "next";
import path from "node:path";

const config: NextConfig = {
  // sin esto Turbopack toma la carpeta Projects como raíz del espacio de trabajo
  turbopack: { root: path.join(__dirname) },
  poweredByHeader: false,
};

export default config;
