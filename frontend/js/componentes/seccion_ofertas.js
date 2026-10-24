import { obtenerOfertas } from "../api.js";
import { escapeHtml, estadoVacio, formatCOP } from "../presentacion.js";

// SeccionOfertas: ofertas de excedentes activas, en el orden que entrega el backend (RF5).
export class SeccionOfertas {
  constructor(pagina, contenedor, alRecibirPlatos) {
    this.pagina = pagina;
    this.contenedor = contenedor;
    this.alRecibirPlatos = alRecibirPlatos;
  }

  async cargar() {
    try {
      this.mostrar(await obtenerOfertas());
    } catch (error) {
      this.pagina.mostrarError(error.message);
    }
  }

  mostrar(ofertas) {
    if (ofertas.length === 0) {
      this.contenedor.innerHTML = estadoVacio("No hay ofertas activas");
    } else {
      this.contenedor.innerHTML = ofertas.map((plato) => this.tarjetaOferta(plato)).join("");
    }
    this.alRecibirPlatos(ofertas);
  }

  tarjetaOferta(plato) {
    return `
      <article class="offer-card">
        <div class="offer-discount-badge">-${plato.descuento_excedente}%</div>
        <h3>${escapeHtml(plato.nombre)}</h3>
        <p class="offer-restaurant">${escapeHtml(plato.restaurante)}</p>
        <div class="offer-pricing">
          <div class="offer-prices">
            <span class="offer-price-current">${formatCOP(plato.precio_final)}</span>
            <span class="offer-price-original">${formatCOP(plato.precio)}</span>
          </div>
          <div class="offer-stock">
            Disponibles<br>
            <strong>${plato.inventario}</strong>
          </div>
        </div>
        <button type="button" data-item-id="${plato.id}" class="pick-item">Reservar oferta</button>
      </article>
    `;
  }
}
