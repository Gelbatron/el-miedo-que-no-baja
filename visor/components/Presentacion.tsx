"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { D, R, fmt, signo } from "@/lib/datos";
import { Dispersion, Forest, Lineas, Mancuerna, LeyendaSexo } from "./Graficos";
import { Mapa } from "./Mapa";

const DURACION = 6 * 60; // segundos del pitch

type Diapo = { quien: string; nota: string; contenido: React.ReactNode; roja?: boolean };

export function Presentacion() {
  const [i, setI] = useState(0);
  const [notas, setNotas] = useState(false);
  const [inicio, setInicio] = useState<number | null>(null);
  const [ahora, setAhora] = useState(Date.now());
  const diapos = usarDiapos();
  const n = diapos.length;
  const ir = useCallback((k: number) => setI(Math.max(0, Math.min(n - 1, k))), [n]);

  // /presentar#4 abre directo en la lámina 4
  useEffect(() => {
    const k = Number(window.location.hash.slice(1));
    if (k >= 1 && k <= n) setI(k - 1);
  }, [n]);
  useEffect(() => {
    window.history.replaceState(null, "", `#${i + 1}`);
  }, [i]);

  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      if (["ArrowRight", "PageDown", " "].includes(e.key)) { e.preventDefault(); ir(i + 1); if (inicio === null) setInicio(Date.now()); }
      if (["ArrowLeft", "PageUp"].includes(e.key)) { e.preventDefault(); ir(i - 1); }
      if (e.key === "n" || e.key === "N") setNotas((v) => !v);
      if (e.key === "Home") ir(0);
      if (e.key === "End") ir(n - 1);
      if (e.key === "f" || e.key === "F") document.documentElement.requestFullscreen?.().catch(() => {});
    };
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  }, [i, ir, n, inicio]);

  useEffect(() => {
    if (inicio === null) return;
    const t = setInterval(() => setAhora(Date.now()), 500);
    return () => clearInterval(t);
  }, [inicio]);

  const transcurrido = inicio === null ? 0 : Math.floor((ahora - inicio) / 1000);
  const restante = DURACION - transcurrido;
  const mmss = (s: number) => `${s < 0 ? "−" : ""}${Math.floor(Math.abs(s) / 60)}:${String(Math.abs(s) % 60).padStart(2, "0")}`;
  const d = diapos[i];

  return (
    <div className="modo-presentacion" role="region" aria-roledescription="presentación" aria-label="Presentación del pitch">
      <section className={`diapo${d.roja ? " roja" : ""}`} aria-live="polite">{d.contenido}</section>
      <div>
        {notas && <div className="notas-pres"><b>{d.quien}:</b> {d.nota}</div>}
        <div className="controles-pres">
          <button className="salir" onClick={() => ir(i - 1)} disabled={i === 0} aria-label="Anterior">←</button>
          <button className="salir" onClick={() => { ir(i + 1); if (inicio === null) setInicio(Date.now()); }} disabled={i === n - 1} aria-label="Siguiente">→</button>
          <span className="mono">{i + 1} / {n}</span>
          <div className="progreso" aria-hidden="true"><i style={{ width: `${((i + 1) / n) * 100}%` }} /></div>
          <button className={`reloj${restante <= 0 ? " fuera" : restante <= 60 ? " alerta" : ""}`} onClick={() => setInicio(inicio === null ? Date.now() : null)}
            title="Iniciar o reiniciar el cronómetro de 6 minutos" style={{ border: 0, cursor: "pointer", font: "inherit" }}>
            {inicio === null ? "6:00 ▶" : mmss(restante)}
          </button>
          <button className="salir" onClick={() => setNotas((v) => !v)} aria-pressed={notas}>Notas (N)</button>
          <Link className="salir" href="/" style={{ textDecoration: "none" }}>Salir</Link>
        </div>
      </div>
    </div>
  );
}

function usarDiapos(): Diapo[] {
  const a = R.ame_hechos, g = R.emv_mujer_ame, v = R.ibs_vs_cifra_oculta, s = R.emv_por_sexo;
  const ibsLoc = Object.fromEntries((D.ibs as Record<string, number>[]).map((f) => [String(f.localidad), Number(f.ibs)]));
  const serie = (cod: string, nombre: string, color: string) => {
    const f = D.serie_delitos.filter((x) => x.codigo === cod).sort((p, q) => p.anio - q.anio);
    return { nombre, color, puntos: f.map((p) => ({ x: p.anio, y: (p.casos / f[0].casos) * 100 })) };
  };
  const co = Object.fromEntries((D.cifra_oculta as Record<string, number>[]).map((c) => [c.localidad, c]));
  const disp = (D.ibs as Record<string, number & string>[]).map((f) => ({ id: Number(f.localidad), nombre: String(f.nombre), x: Number(co[f.localidad].razon), y: Number(f.ibs) }));
  const ORD = ["parque_atracos", "conflictos_vecinos", "homicidios_100k", "presencio_acoso", "hurtos_100k_miles", "narcoticos_100k_cientos", "mujer", "sin_parque", "estrato"];
  const ame = ORD.map((k) => D.ame.m_hechos.find((f) => f.variable === k)!).filter(Boolean);
  const Cif = ({ v, t, c }: { v: string; t: string; c: string }) => (
    <div className="tarjeta" style={{ borderTop: `6px solid ${c}` }}>
      <b style={{ fontFamily: "var(--f-display)", fontWeight: 800, fontSize: "clamp(2.6rem,6vw,4.4rem)", color: c, letterSpacing: "-.04em", lineHeight: 1 }}>{v}</b>
      <span style={{ color: "var(--tinta-2)", fontSize: "1.05rem" }}>{t}</span>
    </div>
  );
  return [
    {
      quien: "Brandow", roja: true,
      nota: "Somos The data squad. Nuestra pregunta es por qué la gente en Bogotá no se siente más segura aunque las cifras de delito bajan, y dónde debería actuar primero el Distrito.",
      contenido: (
        <div style={{ display: "grid", gap: 20, maxWidth: 1000 }}>
          <p className="antetitulo" style={{ color: "#ffd98a" }}>Bogotá DataJam Edición 5 · Equipo #16 The data squad</p>
          <h1 style={{ fontFamily: "var(--f-heroe)", color: "#fff", fontSize: "clamp(3.2rem,9vw,7rem)", lineHeight: .95 }}>El miedo <span style={{ color: "var(--oro)" }}>que no baja</span></h1>
          <div className="heroe-raya" />
          <p style={{ fontSize: "clamp(1.2rem,2.4vw,1.8rem)", color: "#fff", maxWidth: 900, lineHeight: 1.35 }}>¿Por qué la inseguridad percibida no baja cuando el delito registrado sí, y en qué territorios debe intervenir primero el Distrito?</p>
          <p style={{ color: "rgba(255,255,255,.85)" }}>Rafael Estiven Londoño Camacho · Brandow Brusly León Rodríguez · Samuel Esteban Riveros Cubides</p>
        </div>
      ),
    },
    {
      quien: "Brandow",
      nota: "Entre enero y agosto, el hurto a personas registrado cayó 65 % desde 2019. Pero el 74 % de los adultos dice que la ciudad es insegura. Mientras tanto, la violencia intrafamiliar y los delitos sexuales suben.",
      contenido: (
        <>
          <p className="ant">El problema</p>
          <h2 className="dt">Bogotá registra menos delitos, pero no se siente más segura</h2>
          <div className="rejilla" style={{ gridTemplateColumns: "minmax(0,.8fr) minmax(0,1.2fr)", alignItems: "center" }}>
            <div className="rejilla">
              <Cif v={`${signo(R.hurto_personas.cambio_pct, 0)} %`} t="hurto a personas registrado, ene-ago 2019 → 2026 (SCJ)" c="var(--registro-texto)" />
              <Cif v={`${fmt(R.ciudad_insegura_pct, 0)} %`} t="de los adultos califica a Bogotá como insegura (Bienal 2025)" c="var(--percepcion-texto)" />
            </div>
            <div className="tarjeta">
              <div className="leyenda"><span><i style={{ background: "var(--registro)" }} />Hurto a personas</span><span><i style={{ background: "var(--mujeres)" }} />Violencia intrafamiliar</span><span><i style={{ background: "var(--percepcion)" }} />Delitos sexuales</span></div>
              <Lineas base={100} ymax={200} alto={330} series={[serie("HP", "Hurto a personas", "var(--registro)"), serie("VI", "Violencia intrafamiliar", "var(--mujeres)"), serie("DS", "Delitos sexuales", "var(--percepcion)")]} />
            </div>
          </div>
        </>
      ),
    },
    {
      quien: "Rafael",
      nota: "Integramos siete fuentes públicas por el código de localidad, con tasas por 100.000 habitantes. Subimos la escalera completa: descripción, diagnóstico con un logit ponderado, predicción fuera de muestra y escenarios.",
      contenido: (
        <>
          <p className="ant">Datos y método</p>
          <h2 className="dt">Siete fuentes públicas, una llave territorial y una escalera analítica</h2>
          <div className="rejilla r2" style={{ alignItems: "start" }}>
            <div className="rejilla">
              {[["SCJ", "Delitos de alto impacto 2018-2026 y Línea 123", "var(--registro)"], ["SDP", "Proyecciones de población (tasas por 100.000)", "var(--registro)"],
                ["SCRD", `Bienal de Cultura Ciudadana 2025 · ${fmt(R.n_bienal, 0)} adultos`, "var(--percepcion)"], ["EMV", `Encuesta Mundial de Valores 2024 · ${fmt(R.n_emv_bogota, 0)} en Bogotá`, "var(--percepcion)"],
                ["UAESP · DADEP · IDECA", "Alumbrado, espacio público y límites", "var(--registro)"]].map(([k, t, c]) => (
                <div key={k} className="tarjeta plana" style={{ padding: "12px 16px", gap: 2, borderLeft: `5px solid ${c}` }}><b>{k}</b><span className="nota" style={{ fontSize: ".95rem" }}>{t}</span></div>
              ))}
            </div>
            <ol style={{ margin: 0, paddingLeft: "1.3em", display: "grid", gap: 14, fontSize: "1.08rem" }}>
              <li><b>Descriptivo:</b> series con el mismo corte, tasas, porcentajes ponderados con error estándar.</li>
              <li><b>Diagnóstico:</b> logit ponderado con efectos marginales; IC por bootstrap de localidades; efectos fijos y wild cluster bootstrap.</li>
              <li><b>Predictivo:</b> AUC fuera de muestra por bloques de variables.</li>
              <li><b>Prescriptivo:</b> Índice de Brecha con incertidumbre y simulación de escenarios.</li>
            </ol>
          </div>
        </>
      ),
    },
    {
      quien: "Rafael",
      nota: `Por cada delito registrado hay unas ${fmt(R.cifra_oculta_bogota)} víctimas. En Bosa más de 10; en Los Mártires menos de 1. Donde hay más miedo que delito registrado, más delito queda sin registrar: ρ = ${fmt(v.rho, 2)}, la única relación que sobrevive a la corrección por pruebas múltiples.`,
      contenido: (
        <>
          <p className="ant">Hallazgo 1 · cifra oculta</p>
          <h2 className="dt">Donde hay más miedo que delito, el delito no se registra</h2>
          <div className="rejilla" style={{ gridTemplateColumns: "minmax(0,1.5fr) minmax(0,.7fr)", alignItems: "center" }}>
            <div className="tarjeta"><Dispersion puntos={disp} alto={380} ejeX="Víctimas por cada delito registrado (EMV 2024 / SCJ 2024)" ejeY="Índice de Brecha (z)" colorDe={(p) => (p.y > 0 ? "var(--percepcion)" : "var(--registro)")} /></div>
            <div className="rejilla">
              <Cif v={`${fmt(R.cifra_oculta_bogota)} a 1`} t="víctimas por cada delito de alto impacto registrado" c="var(--vino)" />
              <p style={{ fontSize: "1.05rem", color: "var(--tinta-2)" }}>ρ = {fmt(v.rho, 2)} (IC 95 % {fmt(v.ic_inf, 2)} a {fmt(v.ic_sup, 2)}; p ajustado {fmt(v.p_bh, 3)})</p>
            </div>
          </div>
        </>
      ),
    },
    {
      quien: "Rafael",
      nota: `Ver atracos en el parque suma ${fmt(a.parque_atracos.ame_pp)} puntos; los conflictos vecinales hasta ${fmt(a.conflictos_vecinos.ame_pp)}. El hurto registrado no suma nada. Agregar el delito registrado no mejora la predicción (0,609 a 0,611); el entorno la sube a 0,78.`,
      contenido: (
        <>
          <p className="ant">Hallazgo 2 · entorno</p>
          <h2 className="dt">El barrio se siente por su entorno, no por el hurto registrado</h2>
          <div className="rejilla" style={{ gridTemplateColumns: "minmax(0,1.5fr) minmax(0,.7fr)", alignItems: "center" }}>
            <div className="tarjeta"><Forest filas={ame} /></div>
            <div className="rejilla">
              <Cif v={`${signo(a.parque_atracos.ame_pp)} pp`} t="si hay atracos en el parque más cercano" c="var(--percepcion-texto)" />
              <div className="tarjeta plana" style={{ gap: 6 }}>
                <b>AUC fuera de muestra</b>
                <span>Solo perfil: {fmt(R.auc["Perfil (sexo, edad, estrato, tenencia)"], 3)}</span>
                <span style={{ color: "var(--registro-texto)" }}>+ delito registrado: {fmt(R.auc["Perfil + delito registrado"], 3)}</span>
                <span style={{ color: "var(--percepcion-texto)" }}>+ entorno: {fmt(R.auc["Perfil + hechos del entorno"], 3)} · todo: {fmt(R.auc["Todo"], 3)}</span>
              </div>
            </div>
          </div>
        </>
      ),
    },
    {
      quien: "Samuel",
      nota: `Las mujeres reportan menos delitos, pero a igual edad, estrato y victimización tienen ${fmt(g.teme_acoso_sexual.ame_pp)} puntos más de temor al acoso sexual y ${fmt(g.no_sale_noche.ame_pp)} más de evitar salir de noche. El costo del miedo se paga en autonomía.`,
      contenido: (
        <>
          <p className="ant">Hallazgo 3 · enfoque de género</p>
          <h2 className="dt">Las mujeres reportan menos delitos y recortan más su vida</h2>
          <div className="rejilla" style={{ gridTemplateColumns: "minmax(0,1.4fr) minmax(0,.8fr)", alignItems: "center" }}>
            <div className="tarjeta"><LeyendaSexo /><Mancuerna filas={[
              { etiqueta: "Teme el acoso sexual", ...s.teme_acoso_sexual }, { etiqueta: "Evita salir de noche", ...s.no_sale_noche },
              { etiqueta: "Se siente insegura/o en su barrio", ...s.barrio_inseguro }, { etiqueta: "Fue víctima de un delito", ...s.victima }]} /></div>
            <div className="rejilla">
              <Cif v={`${signo(g.teme_acoso_sexual.ame_pp)} pp`} t="temor al acoso sexual, a igual victimización" c="var(--mujeres)" />
              <Cif v={`${signo(g.no_sale_noche.ame_pp)} pp`} t="evitar salir de noche" c="var(--mujeres)" />
            </div>
          </div>
        </>
      ),
    },
    {
      quien: "Brandow",
      nota: `Cuatro recomendaciones: medir con victimización por UPL; entornos que se sienten seguros en ${R.ibs_top5.join(", ")}; la autonomía de las mujeres como indicador; y publicar alumbrado georreferenciado y delitos por UPZ.`,
      contenido: (
        <>
          <p className="ant">Recomendación</p>
          <h2 className="dt">Dónde intervenir primero y cómo medirlo</h2>
          <div className="rejilla" style={{ gridTemplateColumns: "minmax(0,.8fr) minmax(0,1.2fr)", alignItems: "center" }}>
            <div className="tarjeta"><Mapa valores={ibsLoc} tipo="div" unidad="" dec={2} alto={420} /><p className="nota">Índice de Brecha por localidad. Oro: más miedo que delito registrado. Prioridad: {R.ibs_top5.join(", ")}.</p></div>
            <ol style={{ margin: 0, paddingLeft: "1.3em", display: "grid", gap: 16, fontSize: "1.12rem" }}>
              <li><b className="titulo-rojo">Medir con victimización:</b> EDP por UPL junto al registro SCJ.</li>
              <li><b className="titulo-rojo">Entornos que se sienten seguros:</b> parques sin atracos, mediación vecinal y alumbrado en las cinco localidades priorizadas.</li>
              <li><b className="titulo-rojo">Autonomía de las mujeres:</b> «% que evita salir de noche, por sexo» como indicador de resultado.</li>
              <li><b className="titulo-rojo">Datos para evaluar:</b> alumbrado georreferenciado (el del portal es de 2019) y delitos por UPZ.</li>
            </ol>
          </div>
        </>
      ),
    },
    {
      quien: "Samuel", roja: true,
      nota: "Proponemos el Índice de Brecha de Seguridad: se calcula cada semestre con fuentes que ya existen. Todo está en este visor y en el repositorio, reproducible de punta a punta. Bogotá ya produce los datos para cerrar esta brecha; solo hay que leerlos juntos. Gracias.",
      contenido: (
        <div style={{ display: "grid", gap: 18, maxWidth: 1050 }}>
          <p className="antetitulo" style={{ color: "#ffd98a" }}>Indicador propuesto</p>
          <h2 style={{ fontFamily: "var(--f-heroe)", color: "#fff", fontSize: "clamp(2.2rem,5vw,4rem)", lineHeight: 1 }}>Índice de Brecha de Seguridad</h2>
          <div className="heroe-raya" />
          <p style={{ fontSize: "clamp(1.1rem,2vw,1.5rem)", color: "#fff" }}>z(% que siente insegura su zona) − z(ln delitos de alto impacto por 100.000)</p>
          <p style={{ color: "rgba(255,255,255,.9)", fontSize: "1.1rem" }}>Semestral por sector de UPL con la EDP · Línea base 2025: {fmt(R.zona_insegura_pct)} % siente insegura su zona · Reproducible: notebook, repositorio, Power BI, Excel y descargas abiertas.</p>
          <p style={{ fontFamily: "var(--f-heroe)", color: "var(--oro)", fontSize: "clamp(1.6rem,3.5vw,2.6rem)" }}>Bogotá ya produce los datos para cerrar esta brecha. Hay que leerlos juntos.</p>
        </div>
      ),
    },
  ];
}
