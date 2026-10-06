export const metadata = { title: "Entregables · El miedo que no baja" };

const REPO = "https://github.com/rlondono1620-max/el-miedo-que-no-baja";

type Item = { titulo: string; detalle: string; ver?: string; descargar?: { href: string; formato: string }[]; requisito: string };

const ITEMS: Item[] = [
  {
    titulo: "Producto analítico reproducible (notebook)",
    detalle: "Notebook de Python ejecutado de punta a punta: auditoría de datos, descarga desde los servicios oficiales, limpieza con bitácora, integración de siete fuentes, modelos, validaciones, índice y exportes.",
    ver: "/entregables/notebook_el_miedo_que_no_baja.html",
    descargar: [{ href: `${REPO}/blob/main/notebooks/el_miedo_que_no_baja.ipynb`, formato: ".ipynb en GitHub" }],
    requisito: "TdR 11.2",
  },
  {
    titulo: "Repositorio técnico estructurado",
    detalle: "data/, notebooks/, src/, outputs/, docs/, README con problema, fuentes, metodología, ejecución, despliegue y estructura; requirements.txt. Probado en limpio: clon nuevo + dependencias + pipeline = mismos resultados.",
    ver: REPO,
    requisito: "TdR 11.1",
  },
  {
    titulo: "Visualización o visor interpretativo",
    detalle: "Este visor (mapas, brecha, modelos, género, simulador, indicador) con descargas CSV y GeoJSON, y el tablero de Power BI en la carpeta powerbi/ del repositorio.",
    ver: "/",
    descargar: [{ href: "/datos", formato: "CSV y GeoJSON" }, { href: `${REPO}/tree/main/powerbi`, formato: "Power BI" }],
    requisito: "TdR 11.3",
  },
  {
    titulo: "Formulario de caracterización y formulación del problema",
    detalle: "Formulario oficial del DataJam diligenciado sobre el archivo original, con capturas de la herramienta.",
    ver: "/entregables/Formulario_caracterizacion_The_data_squad.pdf",
    descargar: [{ href: "/entregables/Formulario_caracterizacion_The_data_squad.docx", formato: "Word (.docx)" }],
    requisito: "TdR 11.4",
  },
  {
    titulo: "Nota técnica sobre integración de datos públicos",
    detalle: "Una página: disponibilidad y actualización, retos de integración, limitaciones, recomendaciones y utilidad de los datos, con cifras de la auditoría del catálogo completo del portal.",
    ver: "/entregables/Nota_tecnica_integracion_datos_The_data_squad.pdf",
    requisito: "TdR 11.5",
  },
  {
    titulo: "Presentación para la sustentación",
    detalle: "Ocho láminas para el pitch de 6 minutos: problema, datos y método, tres hallazgos, recomendaciones e indicador.",
    ver: "/entregables/Pitch_El_miedo_que_no_baja_The_data_squad.pdf",
    descargar: [{ href: "/entregables/Pitch_El_miedo_que_no_baja_The_data_squad.pptx", formato: "PowerPoint (.pptx)" }],
    requisito: "Jornada final",
  },
  {
    titulo: "Ficha técnica del indicador",
    detalle: "Índice de Brecha de Seguridad: fórmula, fuentes, periodicidad, desagregación, línea base 2025 y meta.",
    ver: "/indicador",
    requisito: "TdR 10.II",
  },
];

export default function Entregables() {
  return (
    <div className="pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Bogotá DataJam Edición 5 · Equipo #16 The data squad</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Entregables</h1>
        <p className="bajada">Todo lo que piden los términos de referencia, en un solo lugar. Cada documento se abre en el navegador o se descarga en su formato original.</p>
      </header>
      <section className="rejilla r2">
        {ITEMS.map((it) => (
          <article key={it.titulo} className="tarjeta">
            <span className="pastilla" style={{ justifySelf: "start" }}>{it.requisito}</span>
            <h3>{it.titulo}</h3>
            <p style={{ color: "var(--tinta-2)", fontSize: ".95rem" }}>{it.detalle}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 4 }}>
              {it.ver && (
                <a className="boton" href={it.ver} target={it.ver.startsWith("/") && !it.ver.includes(".") ? undefined : "_blank"} rel="noreferrer">
                  {it.ver.startsWith("http") ? "Abrir" : it.ver.includes(".") ? "Ver" : "Ir"}
                </a>
              )}
              {it.descargar?.map((d) => (
                <a key={d.href} className="boton sec" href={d.href} target={d.href.startsWith("http") ? "_blank" : undefined} rel="noreferrer"
                  download={d.href.startsWith("/entregables/") ? true : undefined}>{d.formato}</a>
              ))}
            </div>
          </article>
        ))}
      </section>
      <p className="nota">El repositorio es privado mientras se prepara la entrega; se habilita para el jurado el 16 de octubre.</p>
    </div>
  );
}
