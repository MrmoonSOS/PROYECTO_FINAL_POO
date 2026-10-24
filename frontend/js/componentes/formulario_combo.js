import { obtenerCombo } from "../api.js";
import { escapeHtml, estadoVacio, formatCOP } from "../presentacion.js";

// FormularioCombo: pide y muestra el combo óptimo de ofertas para un presupuesto (RF10).
export class FormularioCombo {
  constructor(formulario, campo, mensaje, resultado) {
    this.campo = campo;
    this.mensaje = mensaje;
    this.resultado = resultado;

    formulario.addEventListener("submit", (evento) => {
      evento.preventDefault();
      this.calcular(campo.value);
    });
  }

  async calcular(presupuesto) {
    this.mensaje.textContent = "";
    this.mensaje.className = "form-message";
    try {
      this.mostrar(await obtenerCombo(presupuesto));
    } catch (error) {
      this.mensaje.textContent = error.message;
      this.mensaje.className = "form-message error";
    }
  }

  mostrar(combo) {
    if (combo.platos.length === 0) {
      this.resultado.innerHTML = estadoVacio("No se encontró un combo");
      return;
    }
    const filas = combo.platos.map((plato) => `
      <li class="combo-row">
        <div>
          <strong>${escapeHtml(plato.nombre)}</strong>
          <span>${escapeHtml(plato.restaurante)}</span>
        </div>
        <span class="price-current">${formatCOP(plato.precio_final)}</span>
      </li>
    `).join("");
    this.resultado.innerHTML = `
      <ul class="combo-list">${filas}</ul>
      <div class="combo-totals">
        <div><span>Gasto total</span><strong>${formatCOP(combo.gasto_total)}</strong></div>
        <div class="combo-ahorro"><span>Ahorro</span><strong>${formatCOP(combo.ahorro)}</strong></div>
      </div>
    `;
  }
}
