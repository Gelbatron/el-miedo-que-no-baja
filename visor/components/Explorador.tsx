"use client";
import { useMemo, useState } from "react";
import { D, LOCALIDADES, fmt } from "@/lib/datos";
import { Mapa } from "./Mapa";

const GRUPOS = Array.from(new Set(D.indicadores.map((i) => i.grupo)));
const UPZ_OPC = [["N", "Narcóticos"], ["R", "Riñas"], ["MM", "Maltrato a mujer"], ["H", "Hurto"]] as const;

export function Explorador() {
  const [clave, setClave] = useState("zona_insegura");
  const [sexo, setSexo] = useState<"total" | "mujeres" | "hombres">("total");
  const [nivel, setNivel] = useState<"localidad" | "upz">("localidad");
  const [upzCod, setUpzCod] = useState<string>("N");
  const [sel, setSel] = useState<number | null>(5);
  const [vista, setVista] = useState<"mapa" | "tabla">("mapa");

  const ind = D.indicadores.find((i) => i.clave === clave)!;
  const s = ind.sexo ? sexo : "total";
  const valores = nivel === "upz" ? D.upz[upzCod].valores : D.valores[clave][s];
  const dec = ind.unidad === "por 100.000" ? 0 : 1;
  const filas = useMemo(() => Object.entries(valores).filter(([, v]) => v !== null).sort((a, b) => (b[1] as number) - (a[1] as number)), [valores]);
  const nombreDe = (id: string) => (nivel === "upz" ? D.geo.upz.find((u) => String(u.id) === id)?.nombre ?? id : LOCALIDADES[Number(id)]);
  const fila = D.panel.find((p) => p.localidad === sel) as Record<string, number | string> | undefined;

  return (
    <div className="rejilla" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 340px), 1fr))", alignItems: "start" }}>
      <div className="tarjeta" style={{ gridColumn: "span 2", minWidth: 0 }}>
        <div className="controles">
          <div className="segmentado" role="group" aria-label="Nivel territorial">
            <button aria-pressed={nivel === "localidad"} onClick={() => setNivel("localidad")}>Localidad</button>
            <button aria-pressed={nivel === "upz"} onClick={() => setNivel("upz")}>UPZ (Línea 123)</button>
          </div>
          {nivel === "localidad" ? (
            <label className="campo" htmlFor="ind">Indicador
              <select id="ind" value={clave} onChange={(e) => setClave(e.target.value)}>
                {GRUPOS.map((g) => (
                  <optgroup key={g} label={g}>
                    {D.indicadores.filter((i) => i.grupo === g).map((i) => <option key={i.clave} value={i.clave}>{i.nombre}</option>)}
                  </optgroup>
                ))}
              </select>
            </label>
          ) : (
            <label className="campo" htmlFor="upz">Tipo de llamada
              <select id="upz" value={upzCod} onChange={(e) => setUpzCod(e.target.value)}>
                {UPZ_OPC.map(([c, n]) => <option key={c} value={c}>{n}</option>)}
              </select>
            </label>
          )}
          {nivel === "localidad" && ind.sexo && (
            <div className="segmentado" role="group" aria-label="Sexo">
              {(["total", "mujeres", "hombres"] as const).map((k) => (
                <button key={k} aria-pressed={sexo === k} onClick={() => setSexo(k)}>{k === "total" ? "Total" : k[0].toUpperCase() + k.slice(1)}</button>
              ))}
            </div>
          )}
          <div className="segmentado" role="group" aria-label="Vista" style={{ marginLeft: "auto" }}>
            <button aria-pressed={vista === "mapa"} onClick={() => setVista("mapa")}>Mapa</button>
            <button aria-pressed={vista === "tabla"} onClick={() => setVista("tabla")}>Tabla</button>
          </div>
        </div>
        <p className="nota">
          {nivel === "upz" ? D.upz[upzCod].nombre : `${ind.nombre} · ${ind.fuente}${ind.sexo && s !== "total" ? ` · ${s}` : ""}`}
          {nivel === "upz" && " · UPZ con menos de 1.000 habitantes sin dato"}
        </p>
        {vista === "mapa" ? (
          <Mapa valores={valores} tipo={nivel === "upz" ? "registro" : ind.color} unidad={nivel === "upz" ? "por 100.000 hab." : ind.unidad} nivel={nivel}
            seleccion={nivel === "localidad" ? sel : null} onSelect={nivel === "localidad" ? setSel : undefined} dec={nivel === "upz" ? 0 : dec} alto={640} />
        ) : (
          <div className="tabla-wrap" style={{ maxHeight: 620 }}>
            <table>
              <thead><tr><th>#</th><th>{nivel === "upz" ? "UPZ" : "Localidad"}</th><th className="n">Valor</th>{nivel === "upz" && <th className="n">Llamadas</th>}</tr></thead>
              <tbody>
                {filas.map(([id, v], i) => (
                  <tr key={id}><td className="n">{i + 1}</td><td>{nombreDe(id)}</td><td className="n">{fmt(v as number, nivel === "upz" ? 0 : dec)}</td>
                    {nivel === "upz" && <td className="n">{fmt(D.upz[upzCod].casos[id], 0)}</td>}</tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {nivel === "localidad" && fila && (
        <aside className="tarjeta" aria-live="polite">
          <p className="antetitulo">Ficha de localidad</p>
          <h2 style={{ fontSize: "1.6rem" }}>{String(fila.nombre)}</h2>
          <p className="nota">{fmt(Number(fila.poblacion), 0)} habitantes (SDP 2025). Puesto {fila.puesto} de 19 en el Índice de Brecha.</p>
          <Ficha f={fila} />
        </aside>
      )}
    </div>
  );
}

function Ficha({ f }: { f: Record<string, number | string> }) {
  const g = (k: string, dec = 1) => fmt(f[k] as number, dec);
  const filas: [string, string, string][] = [
    ["Zona insegura", `${g("zona_insegura")} %`, "percepcion"],
    ["Ciudad insegura", `${g("ciudad_insegura")} %`, "percepcion"],
    ["Alumbrado malo", `${g("alumbrado_malo")} %`, "percepcion"],
    ["Drogas en su parque", `${g("parque_spa")} %`, "percepcion"],
    ["Víctimas último año (EMV)", `${g("emv_victima")} %`, "percepcion"],
    ["Evita salir de noche (EMV)", `${g("emv_no_sale_noche")} %`, "percepcion"],
    ["Delitos alto impacto / 100.000", g("delitos_alto_impacto_100k", 0), "registro"],
    ["Homicidios / 100.000", g("homicidios_100k"), "registro"],
    ["Llamadas 123 narcóticos / 100.000", g("incidentes_narcoticos_100k", 0), "registro"],
    ["Víctimas por delito registrado", g("cifra_oculta"), "percepcion"],
    ["Índice de Brecha", g("ibs", 2), "percepcion"],
    ["Espacio público efectivo", `${g("ep_efectivo_m2_hab")} m²/hab.`, "registro"],
  ];
  return (
    <dl style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: "8px 14px", margin: 0, fontSize: ".92rem" }}>
      {filas.map(([k, v, t]) => (
        <div key={k} style={{ display: "contents" }}>
          <dt style={{ color: "var(--tinta-2)", borderLeft: `3px solid var(--${t})`, paddingLeft: 8 }}>{k}</dt>
          <dd className="num" style={{ margin: 0, textAlign: "right" }}>{v}</dd>
        </div>
      ))}
    </dl>
  );
}
