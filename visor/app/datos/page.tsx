import { EnSimple } from "@/components/EnSimple";
import { D } from "@/lib/datos";

export const metadata = { title: "Datos · El miedo que no baja" };

const DESCARGAS = [
  ["panel_localidad_2025.csv", "Panel integrado por localidad: percepción, entorno, victimización, registro, índices y contexto (CSV)"],
  ["indice_brecha_seguridad.csv", "Índice de Brecha de Seguridad con intervalos y puesto (CSV)"],
  ["cifra_oculta_localidad.csv", "Víctimas estimadas frente a delitos registrados por localidad (CSV)"],
  ["efectos_marginales_modelo_principal.csv", "Efectos marginales del modelo principal con intervalos (CSV)"],
  ["serie_delitos_bogota_ene_ago.csv", "Delitos de alto impacto en Bogotá, enero a agosto 2018-2026 (CSV)"],
  ["incidentes_123_upz_2025.csv", "Llamadas a la Línea 123 por UPZ y tipo, con tasas (CSV)"],
  ["localidades_brecha_seguridad.geojson", "Localidades (huella urbana) con todos los indicadores (GeoJSON, EPSG:4326)"],
  ["upz_incidentes_123.geojson", "UPZ con tasas de llamadas 123 (GeoJSON, EPSG:4326)"],
];

export default function Datos() {
  return (
    <div className="contenedor pagina">
      <header className="cabecera-pagina">
        <p className="antetitulo">Exportable e interoperable</p>
        <h1 style={{ fontSize: "clamp(2rem,4vw,3rem)" }}>Datos y entregables</h1>
        <EnSimple>Todo lo que usamos y producimos, listo para descargar y revisar: tablas, mapas, el notebook y el tablero de Power BI.</EnSimple>
        <p className="bajada">Todo lo que muestra el visor se puede descargar en formatos abiertos para integrarlo en visores institucionales (Mapas Bogotá, IDECA, Power BI).</p>
      </header>
      <section className="tarjeta">
        <h2>Descargas</h2>
        <div className="tabla-wrap">
          <table>
            <thead><tr><th>Archivo</th><th>Contenido</th></tr></thead>
            <tbody>{DESCARGAS.map(([f, d]) => <tr key={f}><td><a href={`/descargas/${f}`} download className="mono">{f}</a></td><td>{d}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
      <section className="rejilla r2">
        <div className="tarjeta">
          <h3>Entregables del DataJam</h3>
          <ul style={{ margin: 0, paddingLeft: "1.2em", display: "grid", gap: 8, color: "var(--tinta-2)" }}>
            <li>Notebook, repositorio, formulario, nota técnica, presentación y ficha del indicador: <a href="/entregables">página Entregables</a>.</li>
            <li>Libro de Excel con todas las cifras, fórmulas vivas y simulador: <a href="/entregables/Libro_de_datos_El_miedo_que_no_baja.xlsx" download>Libro_de_datos_El_miedo_que_no_baja.xlsx</a>.</li>
            <li>Tablero de Power BI: <a href="/entregables/ElMiedoQueNoBaja.pbix" download>ElMiedoQueNoBaja.pbix</a> (también como proyecto PBIP en la carpeta <span className="mono">powerbi/</span> del repositorio).</li>
          </ul>
        </div>
        <div className="tarjeta">
          <h3>Fuentes oficiales</h3>
          <ul style={{ margin: 0, paddingLeft: "1.2em", display: "grid", gap: 8, color: "var(--tinta-2)", fontSize: ".92rem" }}>
            {D.fuentes.map((f) => <li key={f.clave}><b style={{ color: "var(--tinta)" }}>{f.entidad}</b>: <a href={f.portal} target="_blank" rel="noreferrer">{f.conjunto}</a></li>)}
          </ul>
        </div>
      </section>
      <p className="nota">Datos generados el {D.generado.replace("T", " a las ")}.</p>
    </div>
  );
}
