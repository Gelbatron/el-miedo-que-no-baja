"use client";
import { D, R, fmt, signo } from "@/lib/datos";
import { COLOR_SEMAFORO, F, encuesta, tendencia } from "@/lib/frentes";
import { HURTO, enLista } from "@/lib/historia";
import { Ap, lin } from "./piezas";

const score = (fuente: string) => F.confiabilidad.find((f) => f.fuente === fuente);
const Insignia = ({ fuente }: { fuente: string }) => {
  const f = score(fuente);
  if (!f) return null;
  return <span title={f.advertencia} style={{ padding: "3px 10px", borderRadius: 999, background: COLOR_SEMAFORO[f.semaforo], color: "#fff", fontWeight: 700, fontSize: 13 }}>confiabilidad {fmt(f.score, 0)}</span>;
};

/* ---------- Cada fuente, por separado, cuenta otra historia ---------- */
type Lectura = { fuente: string; ficha: string; cifra: string; texto: string; conclusion: string; color: string };

/** «5 a 6 de cada 10»: porcentajes llevados a personas de cada 10, redondeados. */
const deCada10 = (a: number, b: number) => { const x = Math.round(Math.min(a, b) / 10), y = Math.round(Math.max(a, b) / 10); return x === y ? `${x} de cada 10` : `${x} a ${y} de cada 10`; };

export function lecturas(): Lectura[] {
  const h = tendencia("H"), vi = tendencia("VI"), ds = tendencia("DS");
  const desconfia = F.confianza_policia.bogota_desconfia_pct;
  const noDenDane = 100 - (encuesta("DANE", "tasa_denuncia", "cualquier_delito_con_isd", 2023) ?? 0);
  const noDenCcb = 100 - (encuesta("CCB", "tasa_denuncia", "cualquier_delito", 2025) ?? 0);
  const dane = encuesta("DANE", "percepcion_inseguridad_ciudad", "no_aplica", 2024) ?? 0;
  return [
    { fuente: "Capa abierta de la Secretaría de Seguridad", ficha: "SCJ · hurtos", cifra: `${signo(HURTO.capa2022a2026, 0)} %`,
      texto: `en el hurto a personas entre 2022 y 2026 (enero a agosto), ya sin pandemia: de ${fmt(HURTO.capa2022, 0)} a ${fmt(HURTO.capa2026, 0)} casos.`,
      conclusion: "Bogotá es mucho más segura.", color: "var(--registro-texto)" },
    { fuente: "Registro de la Policía Nacional", ficha: "Registro de la Policía (SIEDCO)", cifra: `${signo(HURTO.policia2022a2026, 0)} %`,
      texto: `en el mismo hurto y los mismos meses. Antes de 2023 la capa contaba ${fmt(HURTO.razonMin, 1)} a ${fmt(HURTO.razonMax, 1)} veces más hurtos que la Policía; desde 2023 son idénticas.`,
      conclusion: "El hurto casi no bajó.", color: "var(--registro-texto)" },
    { fuente: "Registro validado con Medicina Legal", ficha: "SCJ · homicidios, lesiones, sexuales y VIF", cifra: `${signo(h.post_cambio_anual_pct, 1)} % al año`,
      texto: `suben los homicidios desde 2022. La violencia intrafamiliar, ${signo(vi.post_cambio_anual_pct, 0)} % al año; los delitos sexuales, ${signo(ds.post_cambio_anual_pct, 1)} %.`,
      conclusion: "Y la violencia sube.", color: "var(--vino)" },
    { fuente: "Encuestas del DANE y de la Cámara de Comercio", ficha: "Encuesta de Convivencia (ECSC)", cifra: deCada10(noDenDane, noDenCcb),
      texto: `víctimas no denuncian (DANE 2023: ${fmt(noDenDane, 0)} %; Cámara de Comercio 2025: ${fmt(noDenCcb, 0)} %). Lo que no se denuncia no aparece en ningún registro.`,
      conclusion: "La mayoría no denuncia.", color: "var(--mujeres)" },
    { fuente: "Bienal de Cultura Ciudadana 2025", ficha: "Bienal de Cultura Ciudadana 2025", cifra: "3 de cada 4",
      texto: `dicen que Bogotá es insegura (el DANE mide ${fmt(dane, 0)} % en 2024), y el ${fmt(desconfia, 0)} % confía nada o poco en la Policía.`,
      conclusion: "Y la gente lo siente.", color: "var(--percepcion-texto)" },
  ];
}

export function Lecturas({ paso }: { paso: number }) {
  const L = lecturas();
  const i = Math.min(paso, L.length - 1), l = L[i], fin = paso >= L.length;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "470px 1fr", gap: 44, height: "100%" }}>
      <div style={{ display: "grid", gap: 10, alignContent: "start" }}>
        <p className="cl-ante" style={{ color: "var(--tinta-2)" }}>Si solo miráramos esta fuente, concluiríamos:</p>
        {L.slice(0, i + 1).map((x, k) => (
          <p key={x.conclusion} style={{
            margin: 0, fontFamily: "var(--f-display)", fontWeight: 800, lineHeight: 1.15, transition: "all .4s",
            fontSize: k === i && !fin ? 34 : 20, color: k === i && !fin ? x.color : "var(--tinta-3)",
            textDecoration: k < i || fin ? "line-through" : "none", textDecorationThickness: 2,
          }}>{x.conclusion}</p>
        ))}
        <Ap si={fin}><p className="cl-clave" style={{ fontSize: 25, color: "var(--rojo)", marginTop: 8 }}>El miedo no contradice los datos: el hurto no bajó como parecía, y la violencia sube.</p></Ap>
      </div>
      <div key={i} className="cl-tarjeta" style={{ borderTop: `6px solid ${l.color}`, alignContent: "start", gap: 12, padding: "22px 26px", animation: "cl-entra .45s ease both" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <span className="cl-ante" style={{ color: l.color }}>{i + 1} de {L.length} · {l.fuente}</span>
          <Insignia fuente={l.ficha} />
        </div>
        <span className="cl-num" style={{ fontSize: 68, color: l.color }}>{l.cifra}</span>
        <p className="cl-txt" style={{ fontSize: 21 }}>{l.texto}</p>
      </div>
    </div>
  );
}

/* ---------- Unir las fuentes para responder cuatro preguntas ---------- */
export function Union({ paso }: { paso: number }) {
  const preguntas: [string, string][] = [
    ["¿Quién es más vulnerable?", "Personas, sexo, edad y territorio."],
    ["¿Dónde y en qué crece la inseguridad?", "Tendencias por delito y por localidad, sin el efecto pandemia."],
    ["¿Cuadran la percepción y las estadísticas? Si no, ¿por qué?", "Lo que se siente frente a lo que se registra y lo que se vive."],
    ["¿Qué hacer, y dónde primero?", "Estrategias con su nivel de evidencia."],
  ];
  const modelos: [string, string, string][] = [
    ["Estadístico", "Tendencias de panel (binomial negativa, efectos fijos) en la ventana comparable de cada serie", "Pregunta 2"],
    ["Supervisado", "Logística, bosque aleatorio y gradient boosting: qué predice el miedo", "Pregunta 3"],
    ["No supervisado", "Componentes principales y agrupamiento: tipos de localidad", "Preguntas 1 y 4"],
  ];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40, height: "100%" }}>
      <div style={{ display: "grid", gap: 14, alignContent: "start" }}>
        <p className="cl-ante" style={{ color: "var(--tinta-2)" }}>Las cuatro preguntas</p>
        {preguntas.map(([q, d], k) => (
          <Ap key={q} si={paso >= 0} retraso={k * 120}>
            <div style={{ display: "grid", gridTemplateColumns: "44px 1fr", gap: 12, alignItems: "start" }}>
              <span style={{ width: 40, height: 40, borderRadius: 999, background: "var(--rojo)", color: "#fff", display: "grid", placeItems: "center", fontFamily: "var(--f-display)", fontWeight: 800, fontSize: 18 }}>{k + 1}</span>
              <div><b style={{ fontSize: 19 }}>{q}</b><p className="cl-txt" style={{ fontSize: 16 }}>{d}</p></div>
            </div>
          </Ap>
        ))}
      </div>
      <div style={{ display: "grid", gap: 16, alignContent: "start" }}>
        <Ap si={paso >= 1}>
          <p className="cl-ante" style={{ color: "var(--tinta-2)", marginBottom: 8 }}>Cómo las unimos</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {["Una llave: el código oficial de localidad", "Tasas por 100.000 habitantes", "Factor de expansión de cada encuesta", "Mismo corte enero-agosto, 2018-2026",
              `${fmt(R.n_bienal, 0)} personas enlazadas con el delito de su localidad`, "Score de confiabilidad por fuente", "Cada serie validada con la Policía y Medicina Legal"].map((t) => <span key={t} className="cl-chip">{t}</span>)}
          </div>
        </Ap>
        <Ap si={paso >= 2}>
          <p className="cl-ante" style={{ color: "var(--tinta-2)", marginBottom: 8 }}>Y tres modelos</p>
          <div style={{ display: "grid", gap: 8 }}>
            {modelos.map(([n, d, q]) => (
              <div key={n} className="cl-tarjeta" style={{ padding: "10px 14px", borderLeft: "5px solid var(--oro)", gap: 2 }}>
                <span style={{ display: "flex", justifyContent: "space-between", gap: 10 }}><b style={{ fontSize: 17 }}>{n}</b><span style={{ fontSize: 13, color: "var(--tinta-3)" }}>{q}</span></span>
                <span style={{ fontSize: 15, color: "var(--tinta-2)" }}>{d}</span>
              </div>
            ))}
          </div>
        </Ap>
      </div>
    </div>
  );
}

/* ---------- Tipos de localidad (no supervisado) ---------- */
const RASGO: Record<string, string> = {
  delitos_alto_impacto_100k: "delito registrado", homicidios_100k: "homicidios", emv_victima: "víctimas (encuesta)",
  vif_ds_100k_mujeres: "violencia contra mujeres", zona_insegura: "miedo en su zona", miedo_espacio_publico: "miedo en la calle",
  luminarias_km2_2019: "luminarias", ep_efectivo_m2_hab: "espacio público",
};
export function Tipologia({ paso }: { paso: number }) {
  const T = F.tipologia;
  if (!T) return <p className="cl-txt">La tipología se calcula con src/tipologia.py.</p>;
  const locs = T.localidades as Record<string, number & string>[];
  const perfiles = Array.from(new Set(locs.map((l) => Number(l.perfil)))).sort();
  const paleta = ["var(--vino)", "var(--percepcion)", "var(--hombres)", "var(--registro)", "var(--mujeres)"];
  const color = (p: number) => paleta[(p - 1) % paleta.length];
  const nombre = (p: number) => String(locs.find((l) => Number(l.perfil) === p)?.perfil_nombre ?? `Perfil ${p}`);
  const perfilDe = Object.fromEntries(locs.map((l) => [Number(l.localidad), Number(l.perfil)]));
  const rasgos = (p: number) => {
    const z = (T.perfiles_z as Record<string, number | string>[]).find((f) => Number(f.perfil) === p) ?? {};
    return Object.keys(RASGO).map((k) => ({ k, v: Number(z[k] ?? 0) })).sort((a, b) => Math.abs(b.v) - Math.abs(a.v)).slice(0, 3);
  };
  const { ancho, alto } = D.geo;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "430px 1fr", gap: 32, height: "100%" }}>
      <svg className="cl-g" viewBox={`-4 -4 ${ancho + 8} ${alto + 8}`} role="img" aria-label="Bogotá urbana coloreada por tipo de localidad" style={{ maxHeight: 520 }}>
        {D.geo.localidades.map((l) => {
          const p = perfilDe[l.id];
          return <path key={l.id} d={l.d} style={{ fill: p && paso >= 1 ? color(p) : "var(--superficie-2)", stroke: "var(--superficie)", strokeWidth: 1.5, transition: "fill .5s" }}
            data-tip={`<b>${l.nombre}</b>${p ? `<br>${nombre(p)}` : ""}`} />;
        })}
      </svg>
      <div style={{ display: "grid", gap: 8, alignContent: "start" }}>
        <p className="cl-ante" style={{ color: "var(--tinta-2)" }}>8 indicadores de los 4 frentes · rasgos en desviaciones frente al promedio</p>
        {perfiles.map((p, k) => (
          <Ap key={p} si={paso >= 1} retraso={k * 120}>
            <div className="cl-tarjeta" style={{ borderLeft: `6px solid ${color(p)}`, padding: "8px 14px", gap: 3 }}>
              <span style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "baseline", flexWrap: "wrap" }}>
                <b style={{ fontSize: 16.5 }}>{nombre(p)}</b>
                <span style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {rasgos(p).map((r) => (
                    <span key={r.k} style={{ fontSize: 12.5, padding: "1px 8px", borderRadius: 999, background: "var(--superficie)", color: r.v > 0 ? "var(--vino)" : "var(--registro-texto)", fontWeight: 600 }}>
                      {signo(r.v, 1)} {RASGO[r.k]}
                    </span>
                  ))}
                </span>
              </span>
              <span style={{ fontSize: 13.5, color: "var(--tinta-2)" }}>{enLista(locs.filter((l) => Number(l.perfil) === p).map((l) => String(l.nombre)))}</span>
            </div>
          </Ap>
        ))}
      </div>
    </div>
  );
}

/* ---------- Las mujeres: el miedo en la calle y la violencia en la casa ---------- */
type FilaG = Record<string, number | string | null>;
const num = (f: FilaG | undefined, k: string) => Number(f?.[k] ?? NaN);
export function Mujeres({ paso }: { paso: number }) {
  const G = F.genero;
  const perfil = (G.perfil ?? []) as FilaG[];
  const edad = (sexo: string, cat: string) => perfil.find((f) => f.dimension === "grupo_edad" && f.sexo_victima === sexo && f.categoria === cat);
  const grupos: [string, string][] = [["De 1 - 5 años", "1 a 5"], ["De 6 - 13 años", "6 a 13"], ["De 14 - 17 años", "14 a 17"], ["De 18 - 26 años", "18 a 26"],
    ["De 27 - 44 años", "27 a 44"], ["De 45 - 59 años", "45 a 59"], ["De 60 - 69 años", "60 a 69"]];
  const vivienda = perfil.find((f) => f.dimension === "lugar_del_caso" && f.sexo_victima === "Mujeres" && f.categoria === "Vivienda");
  const via = perfil.find((f) => f.dimension === "lugar_del_caso" && f.sexo_victima === "Mujeres" && f.categoria === "Vía Pública");
  const bog = ((G.localidades ?? []) as FilaG[]).find((f) => Number(f.localidad) === 0);
  const aco = (g: string) => ((G.acoso ?? []) as FilaG[]).find((f) => f.nivel === "Género" && f.genero === g);
  const s = R.emv_por_sexo.teme_acoso_sexual, ame = D.emv_genero.teme_acoso_sexual.find((f) => f.variable === "mujer")!;
  const j18 = num(edad("Mujeres", "De 18 - 26 años"), "tasa_2025") / num(edad("Hombres", "De 18 - 26 años"), "tasa_2025");
  const W = 560, fila = 50, top = 36, H = grupos.length * fila + top + 30, X = lin(0, 3400, 90, W - 70);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "560px 1fr", gap: 36, height: "100%" }}>
      <div className={`cl-sap${paso >= 1 ? " si" : ""}`}>
        <p className="cl-ante" style={{ color: "var(--mujeres)" }}>Violencia contra mujeres notificada a Salud (SIVIM) · por 100.000 mujeres</p>
        <svg className="cl-g" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Tasa de violencia contra mujeres por edad, 2019 y 2025">
          {[0, 1000, 2000, 3000].map((t) => <g key={t}><line x1={X(t)} x2={X(t)} y1={top - 14} y2={H - 26} className="grid" /><text x={X(t)} y={H - 8} className="tick" textAnchor="middle">{fmt(t, 0)}</text></g>)}
          <text x={X(0)} y={14} style={{ fontSize: 13, fill: "var(--tinta-3)" }}>○ 2019   ● 2025 · edad</text>
          {grupos.map(([cat, n], k) => {
            const f = edad("Mujeres", cat), y = top + k * fila, a = num(f, "tasa_2019"), b = num(f, "tasa_2025"), alto = cat === "De 14 - 17 años" || cat === "De 6 - 13 años";
            return (
              <g key={cat}>
                <text x={80} y={y + 5} textAnchor="end" style={{ fontSize: 15, fill: "var(--tinta)", fontWeight: alto ? 700 : 400 }}>{n}</text>
                <line x1={X(a)} x2={X(b)} y1={y} y2={y} stroke="var(--mujeres)" strokeWidth={4} opacity={0.35} />
                <circle cx={X(a)} cy={y} r={7} fill="var(--superficie)" stroke="var(--mujeres)" strokeWidth={2.5} />
                <circle cx={X(b)} cy={y} r={8} fill="var(--mujeres)" data-tip={`<b>Mujeres de ${n} años</b><br>2019: ${fmt(a, 0)} · 2025: ${fmt(b, 0)} por 100.000`} />
                <text x={X(Math.max(a, b)) + 14} y={y + 5} style={{ fontSize: 14, fontWeight: 700, fill: "var(--mujeres)" }}>{fmt(b, 0)}</text>
              </g>
            );
          })}
        </svg>
        <p className="cl-txt" style={{ fontSize: 13.5, color: "var(--tinta-3)" }}>Casos notificados, no personas: desde 2022 crece la notificación desde los colegios, así que parte del aumento es mejor registro.</p>
      </div>
      <div style={{ display: "grid", gap: 12, alignContent: "start" }}>
        <Ap si={paso >= 0}>
          <div className="cl-tarjeta" style={{ borderTop: "6px solid var(--percepcion)", gap: 4 }}>
            <span className="cl-ante" style={{ color: "var(--percepcion-texto)" }}>En la calle</span>
            <span style={{ fontSize: 16 }}><b className="cl-num" style={{ fontSize: 30, color: "var(--mujeres)" }}>{deCada10(num(aco("Mujeres"), "pct_acoso_12_meses"), num(aco("Mujeres"), "pct_acoso_12_meses"))}</b> mujeres fueron acosadas en la calle el último año; hombres, {deCada10(num(aco("Hombres"), "pct_acoso_12_meses"), num(aco("Hombres"), "pct_acoso_12_meses")).replace(" de cada 10", "")}. Denunció menos de 1 de cada 10.</span>
            <span style={{ fontSize: 15 }}>{deCada10(s.mujeres, s.mujeres)} temen el acoso sexual ({deCada10(s.hombres, s.hombres).replace(" de cada 10", "")} de cada 10 hombres): {signo(ame.ame_pp, 0)} puntos a igual edad, estrato y victimización.</span>
            <span style={{ fontSize: 12, color: "var(--tinta-3)" }}>Acoso: Veeduría 2025, formulario en línea (describe, no estima). Temor: EMV 2024.</span>
          </div>
        </Ap>
        <Ap si={paso >= 1}>
          <div className="cl-tarjeta" style={{ borderTop: "6px solid var(--mujeres)", gap: 4 }}>
            <span className="cl-ante" style={{ color: "var(--mujeres)" }}>En la casa</span>
            <span style={{ fontSize: 16 }}><b className="cl-num" style={{ fontSize: 30, color: "var(--mujeres)" }}>{signo(num(bog, "cambio_pct_2019_2025"), 0)} %</b> la violencia contra mujeres notificada a Salud, 2019 → 2025 (IC 95 %: {signo(num(bog, "cambio_pct_2019_2025_ic_inf"), 0)} a {signo(num(bog, "cambio_pct_2019_2025_ic_sup"), 0)} %).</span>
            <span style={{ fontSize: 15 }}><b>{fmt(num(vivienda, "pct_2025") / 10, 0)} de cada 10 casos pasan en la vivienda</b>; en la vía pública, {fmt(num(via, "pct_2025"), 1)} %. Las más afectadas: niñas y adolescentes. Entre 18 y 26 años, la tasa de ellas es {fmt(j18, 1)} veces la de ellos.</span>
          </div>
        </Ap>
        <Ap si={paso >= 2}><p className="cl-clave" style={{ fontSize: 20 }}>Dos problemas distintos: el miedo en la calle y la violencia en la casa. Una luminaria no resuelve el segundo.</p></Ap>
      </div>
    </div>
  );
}

/* ---------- Lo que probamos: el marcador de hipótesis ---------- */
type Hip = { h: string; prueba: string; dato: string; sostiene: boolean };
export function hipotesis(): Hip[] {
  const mov = (F.movilidad?.pruebas ?? []) as FilaG[];
  const m = (x: string, y = "hp_100k_2025") => mov.find((f) => f.x === x && f.y === y);
  const gp = (x: string) => ((F.genero.pruebas ?? []) as FilaG[]).find((f) => f.bloque === "principal" && String(f.x).startsWith(x));
  const lum = m("luminarias_km_via_2024_05"), pci = m("pct_pci_menor_56_2024_12"), alu = m("alumbrado_malo_bienal_2025");
  const wild = D.lpm_wild.find((f) => f.variable === "hurtos_100k_miles")!;
  const ctx = F.ml.contexto_localidad, at = R.ame_hechos.parque_atracos, mu = R.emv_mujer_ame.teme_acoso_sexual, v = R.ibs_vs_cifra_oculta;
  const rho = (f: FilaG | undefined) => `ρ = ${signo(num(f, "rho"), 2)}`;
  return [
    { h: "La serie de hurto es comparable en el tiempo", prueba: "Capa SCJ ÷ Policía, por año", dato: `${fmt(HURTO.razonMin, 1)}-${fmt(HURTO.razonMax, 1)}× hasta 2022; 1,0× desde 2023`, sostiene: false },
    { h: "El delito registrado explica el miedo", prueba: "Logit + wild bootstrap; ML con prueba de contexto", dato: `p = ${fmt(wild.p_wild, 2)}; AUC ${fmt(ctx[2].mean, 3)} sin él, ${fmt(ctx[3].mean, 3)} con él`, sostiene: false },
    { h: "Peor alumbrado, más hurto", prueba: "Spearman, 19 localidades, Benjamini-Hochberg", dato: `luminarias por km de vía ${rho(lum)} (al revés); alumbrado malo ${rho(alu)}`, sostiene: false },
    { h: "Vías en mal estado, más hurto", prueba: "Spearman con el PCI del IDU", dato: `${rho(pci)}, no significativa`, sostiene: false },
    { h: "Más luz o internet, menos violencia contra ellas", prueba: "Spearman con la tasa SIVIM", dato: `${rho(gp("Iluminación"))} y ${rho(gp("Puntos de conectividad"))}`, sostiene: false },
    { h: "El entorno del barrio explica el miedo", prueba: "Efecto marginal, IC por bootstrap de localidades", dato: `atracos en el parque ${signo(at.ame_pp, 1)} pp (IC ${fmt(at.ic_inf, 1)} a ${fmt(at.ic_sup, 1)})`, sostiene: true },
    { h: "Donde sobra miedo, falta denuncia", prueba: "Spearman con corrección por pruebas múltiples", dato: `ρ = ${fmt(v.rho, 2)}, p ajustado = ${fmt(v.p_bh, 3)}`, sostiene: true },
    { h: "A igual victimización, ellas temen más", prueba: "Logit ponderado (EMV)", dato: `${signo(mu.ame_pp, 1)} pp de temor al acoso (IC ${fmt(mu.ic_inf, 1)} a ${fmt(mu.ic_sup, 1)})`, sostiene: true },
  ];
}

export function Hipotesis({ paso }: { paso: number }) {
  const H = hipotesis();
  const si = H.filter((x) => x.sostiene).length;
  return (
    <div style={{ display: "grid", gap: 6, alignContent: "start", height: "100%" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1.15fr 1fr 1.35fr 150px", gap: 12, fontSize: 13, color: "var(--tinta-3)", padding: "0 14px", fontWeight: 600 }}>
        <span>Lo que esperábamos (o esperaba cualquiera)</span><span>Cómo lo probamos</span><span>Lo que salió</span><span style={{ textAlign: "right" }}>Veredicto</span>
      </div>
      {H.map((x, k) => (
        <div key={x.h} style={{ display: "grid", gridTemplateColumns: "1.15fr 1fr 1.35fr 150px", gap: 12, alignItems: "center", padding: "8px 14px", borderRadius: 10, background: "var(--superficie-2)" }}>
          <b style={{ fontSize: 15.5, lineHeight: 1.25 }}>{x.h}</b>
          <span style={{ fontSize: 13.5, color: "var(--tinta-2)", lineHeight: 1.3 }}>{x.prueba}</span>
          <Ap si={paso >= 1} retraso={k * 90}><span style={{ fontSize: 13.5, lineHeight: 1.3 }}>{x.dato}</span></Ap>
          <Ap si={paso >= 1} retraso={k * 90} style={{ justifySelf: "end" }}>
            <span style={{ padding: "4px 12px", borderRadius: 999, fontWeight: 700, fontSize: 13.5, background: x.sostiene ? "var(--hombres)" : "var(--neutro)", color: x.sostiene ? "#fff" : "#1e1e1e" }}>
              {x.sostiene ? "✓ se sostiene" : "✗ no se sostiene"}
            </span>
          </Ap>
        </div>
      ))}
      <Ap si={paso >= 2}><p className="cl-clave" style={{ fontSize: 20, marginTop: 4 }}>{si} se sostienen y {H.length - si} no. Un resultado nulo también es evidencia: evita gastar en lo que no mueve la aguja.</p></Ap>
    </div>
  );
}

/* ---------- Estrategias que solo aparecen al unir los datos ---------- */
export type Estrategia = { titulo: string; porque: string; accion: string; evidencia: "alta" | "media" | "exploratoria"; mide: string };
const COLOR_EVIDENCIA = { alta: "var(--hombres)", media: "var(--oro)", exploratoria: "var(--neutro)" } as const;

export function estrategias(): Estrategia[] {
  const v = R.ibs_vs_cifra_oculta, a = R.ame_hechos;
  const esc = D.escenarios.find((e) => e.grupo === "total" && e.localidad === 0)!;
  const menos = esc.p00 - (esc.p00 + esc.p10 + esc.p01 + esc.p11) / 4;
  const noDen = 100 - (encuesta("DANE", "tasa_denuncia", "cualquier_delito_con_isd", 2023) ?? 0);
  const hom = ((F.homicidios_localidad ?? []) as Record<string, number | string>[]).find((h) => h.nombre === "San Cristóbal");
  const tip = (F.tipologia?.localidades ?? []) as Record<string, string | number>[];
  const periferia = tip.filter((l) => l.perfil === tip.find((x) => x.nombre === "Usme")?.perfil).map((l) => String(l.nombre));
  const perfil = (F.genero.perfil ?? []) as Record<string, string | number | null>[];
  const casa = Number(perfil.find((f) => f.dimension === "lugar_del_caso" && f.sexo_victima === "Mujeres" && f.categoria === "Vivienda")?.pct_2025 ?? NaN);
  return [
    { titulo: "Validar antes de decidir", evidencia: "alta",
      porque: `La capa abierta dice ${signo(HURTO.capa2022a2026, 0)} % de hurto desde 2022; la Policía, ${signo(HURTO.policia2022a2026, 0)} %. Con una sola serie, el hurto se habría dado por resuelto.`,
      accion: "Documentar el cambio de 2023 en los metadatos, publicar la serie empalmada y contrastar cada serie con la Policía y Medicina Legal.", mide: "Razón capa ÷ Policía = 1 en todo delito y año" },
    { titulo: "Repartir por víctimas, no por denuncias", evidencia: "media",
      porque: `Donde sobra miedo, falta denuncia (ρ = ${fmt(v.rho, 2)}). Si los recursos siguen a las denuncias, la periferia que no denuncia recibe menos.`,
      accion: "Asignar con el Índice de Brecha y las víctimas estimadas, no solo con el registro.", mide: "Índice de Brecha por UPL" },
    { titulo: "Medir lo que no se denuncia", evidencia: "media",
      porque: `${fmt(noDen, 0)} % de las víctimas no denuncia, y la encuesta oficial no se hizo en 2022 ni tiene datos de 2024 a 2026.`,
      accion: "Encuesta de victimización por UPL cada semestre, que pregunte si denunció y dónde ocurrió.", mide: "Tasa de denuncia por UPL" },
    { titulo: "Barrios que se sienten seguros", evidencia: "alta",
      porque: `Atracos en el parque: ${signo(a.parque_atracos.ame_pp, 0)} puntos de miedo; conflictos entre vecinos: ${signo(a.conflictos_vecinos.ame_pp, 0)}. El hurto registrado no pesa.`,
      accion: `Parques activos y mediación vecinal: unas ${fmt((menos / 100) * R.adultos_urbanos_bienal / 1000, 0)} mil personas menos con miedo si se mejora la mitad.`, mide: "% que siente insegura su zona" },
    { titulo: `Paquete para ${enLista(periferia)}`, evidencia: "exploratoria",
      porque: `El mismo perfil: miedo alto, pocas luminarias, más homicidios y pocas denuncias.${hom ? ` En San Cristóbal los homicidios subieron ${fmt(Number(hom.cambio_22_25), 0)} % frente a 2022-2023.` : ""}`,
      accion: "Alumbrado y senderos, presencia en parques y foco en homicidios, juntos y en el mismo territorio.", mide: "Índice de Brecha y homicidios por 100.000" },
    { titulo: "Dos rutas para las mujeres", evidencia: "media",
      porque: `${fmt(casa / 10, 0)} de cada 10 casos de violencia contra ellas pasan en la vivienda; en la calle, la mitad fue acosada. El alumbrado no explica lo primero.`,
      accion: "Calle: rutas nocturnas y denuncia fácil del acoso. Casa: detección en colegios y salud, donde ya llegan los casos.", mide: "Tasa SIVIM y % de acoso denunciado" },
  ];
}

export function Estrategias({ paso }: { paso: number }) {
  const E = estrategias();
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, alignContent: "start", height: "100%" }}>
      {E.map((e, k) => (
        <Ap key={e.titulo} si={paso >= Math.floor(k / 2)} retraso={(k % 2) * 160}>
          <div style={{ display: "grid", gridTemplateColumns: "38px 1fr", gap: 12, alignItems: "start", padding: "12px 14px", borderRadius: 12, background: "var(--superficie-2)", height: "100%" }}>
            <span style={{ width: 36, height: 36, borderRadius: 999, background: "var(--rojo)", color: "#fff", display: "grid", placeItems: "center", fontFamily: "var(--f-display)", fontWeight: 800, fontSize: 17 }}>{k + 1}</span>
            <div style={{ display: "grid", gap: 3 }}>
              <span style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "start" }}>
                <b style={{ fontFamily: "var(--f-display)", fontSize: 17.5, lineHeight: 1.2 }}>{e.titulo}</b>
                <span style={{ flex: "none", padding: "2px 9px", borderRadius: 999, background: COLOR_EVIDENCIA[e.evidencia], color: e.evidencia === "exploratoria" ? "#1e1e1e" : "#fff", fontWeight: 700, fontSize: 12 }}>{e.evidencia}</span>
              </span>
              <span style={{ fontSize: 13.5, color: "var(--tinta-2)", lineHeight: 1.35 }}><b>Por qué:</b> {e.porque}</span>
              <span style={{ fontSize: 13.5, color: "var(--tinta)", lineHeight: 1.35 }}><b>Qué hacer:</b> {e.accion}</span>
              <span style={{ fontSize: 12, color: "var(--tinta-3)" }}>Se mide con: {e.mide}</span>
            </div>
          </div>
        </Ap>
      ))}
    </div>
  );
}
