import { obtenerResumen } from "../api.js";
import { escapeHtml } from "../presentacion.js";

// ResumenCampus: tarjetas de estadísticas del encabezado (RF6).
export class ResumenCampus {
  constructor(pagina, contenedor) {
    this.pagina = pagina;
    this.contenedor = contenedor;
  }

  async cargar() {
    try {
      this.mostrar(await obtenerResumen());
    } catch (error) {
      this.pagina.mostrarError(error.message);
    }
  }

  mostrar(resumen) {
    const rapido = resumen.plato_mas_rapido;
    this.contenedor.innerHTML = `
      <div class="stat-card">
        <strong>${resumen.platos_activos}</strong>
        <span>platos activos</span>
      </div>
      <div class="stat-card">
        <strong>${resumen.restaurantes_abiertos}</strong>
        <span>restaurantes abiertos</span>
      </div>
      <div class="stat-card">
        <strong>${resumen.ofertas_vigentes}</strong>
        <span>ofertas de excedentes</span>
      </div>
      <div class="stat-card">
        <strong>${rapido ? `${rapido.tiempo_preparacion}<small>min</small>` : "-"}</strong>
        <span>${rapido ? `más rápido: ${escapeHtml(rapido.nombre)}` : "plato más rápido"}</span>
      </div>
    `;
  }
}
