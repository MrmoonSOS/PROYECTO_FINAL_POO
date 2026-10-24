import { escapeHtml, formatCOP } from "../presentacion.js";

// ModalComprobante: modal de confirmación con el comprobante de la preorden (RF8).
export class ModalComprobante {
  constructor(fondo, detalles, botonCerrar) {
    this.fondo = fondo;
    this.detalles = detalles;
    this.botonCerrar = botonCerrar;

    botonCerrar.addEventListener("click", () => this.cerrar());
    fondo.addEventListener("click", (evento) => {
      if (evento.target === fondo) this.cerrar();
    });
  }

  mostrar(comprobante) {
    const lineas = comprobante.lineas.map((linea) => `
      <div class="row">
        <span>${linea.cantidad} x ${escapeHtml(linea.plato)}</span>
        <span>${formatCOP(linea.subtotal)}</span>
      </div>
    `).join("");
    const notas = comprobante.notas
      ? `<div class="row"><span>Notas</span><span>${escapeHtml(comprobante.notas)}</span></div>`
      : "";

    this.detalles.innerHTML = `
      <div class="row"><span>Pedido N.</span><span>#${comprobante.numero_pedido}</span></div>
      <div class="row"><span>Cliente</span><span>${escapeHtml(comprobante.cliente)}</span></div>
      <div class="row"><span>Restaurante</span><span>${escapeHtml(comprobante.restaurante)}</span></div>
      <div class="row"><span>Recoger a las</span><span>${escapeHtml(comprobante.hora_recogida)}</span></div>
      ${lineas}
      ${notas}
      <div class="row total"><span>Total a pagar</span><span>${formatCOP(comprobante.total)}</span></div>
    `;
    this.fondo.classList.add("open");
    this.botonCerrar.focus();
  }

  cerrar() {
    this.fondo.classList.remove("open");
  }
}
