import { seleccionarPerfil } from "../api.js";
import { escapeHtml, formatCOP } from "../presentacion.js";

// SelectorPerfil: aplica el perfil elegido y refresca SeccionRecomendaciones (RF3).
export class SelectorPerfil {
  constructor(pagina, selector, pista, seccionRecomendaciones) {
    this.pagina = pagina;
    this.selector = selector;
    this.pista = pista;
    this.seccionRecomendaciones = seccionRecomendaciones;
    this.slugAplicado = "";

    selector.addEventListener("change", () => this.seleccionar(selector.value));
  }

  async seleccionar(slug) {
    try {
      const perfil = await seleccionarPerfil(slug);
      this.slugAplicado = slug;
      this.pista.innerHTML =
        `Presupuesto: <strong>${formatCOP(perfil.presupuesto)}</strong>` +
        ` · Cocina preferida: <strong>${escapeHtml(perfil.cocina_preferida ?? "sin preferencia")}</strong>`;
      await this.seccionRecomendaciones.cargar();
    } catch (error) {
      this.selector.value = this.slugAplicado;
      this.pagina.mostrarError(error.message);
    }
  }
}
