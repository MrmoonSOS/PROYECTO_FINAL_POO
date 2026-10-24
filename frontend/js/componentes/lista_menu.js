import { obtenerMenu } from "../api.js";
import { estadoVacio, tarjetaPlato } from "../presentacion.js";

// ListaMenu: zona de menú con las tarjetas de platos (RF1 y RF2).
export class ListaMenu {
  constructor(pagina, contenedor, contador, alRecibirPlatos) {
    this.pagina = pagina;
    this.contenedor = contenedor;
    this.contador = contador;
    this.alRecibirPlatos = alRecibirPlatos;
    this.criterios = {};
    this.solicitudActual = 0;
  }

  async cargarMenu(criterios = {}) {
    const solicitud = ++this.solicitudActual;
    try {
      const platos = await obtenerMenu(criterios);
      if (solicitud !== this.solicitudActual) {
        return;
      }
      this.criterios = criterios;
      this.mostrarPlatos(platos);
    } catch (error) {
      if (solicitud === this.solicitudActual) {
        this.pagina.mostrarError(error.message);
      }
    }
  }

  mostrarPlatos(platos) {
    const conFiltros = Object.keys(this.criterios).length > 0;
    let texto = `${platos.length} ${platos.length === 1 ? "plato disponible" : "platos disponibles"}`;
    if (conFiltros) {
      texto += " · con filtros activos";
    }
    this.contador.textContent = texto;

    if (platos.length === 0) {
      this.contenedor.innerHTML = estadoVacio(
        conFiltros ? "No encontramos platos con esos filtros" : "No hay platos disponibles",
      );
    } else {
      this.contenedor.innerHTML = platos.map((plato) => tarjetaPlato(plato)).join("");
    }
    this.alRecibirPlatos(platos);
  }
}
