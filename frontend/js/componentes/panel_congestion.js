import { obtenerCongestion } from "../api.js";
import { escapeHtml, estadoVacio } from "../presentacion.js";

// PanelCongestion: nivel de congestión y tiempo estimado por restaurante abierto (RF9).
export class PanelCongestion {
  static ETIQUETAS_NIVEL = { bajo: "Baja", medio: "Media", alto: "Alta" };

  constructor(pagina, contenedor) {
    this.pagina = pagina;
    this.contenedor = contenedor;
  }

  async cargar() {
    try {
      this.mostrar(await obtenerCongestion());
    } catch (error) {
      this.pagina.mostrarError(error.message);
    }
  }

  mostrar(estados) {
    if (estados.length === 0) {
      this.contenedor.innerHTML = estadoVacio("No hay restaurantes abiertos");
      return;
    }
    this.contenedor.innerHTML = estados.map((estado) => `
      <article class="congestion-card">
        <h3>${escapeHtml(estado.restaurante)}</h3>
        <span class="congestion-nivel nivel-${escapeHtml(estado.congestion)}">
          ${escapeHtml(PanelCongestion.ETIQUETAS_NIVEL[estado.congestion] ?? estado.congestion)} congestión
        </span>
        <p class="congestion-tiempo">~${estado.tiempo_estimado_min} min</p>
      </article>
    `).join("");
  }
}
