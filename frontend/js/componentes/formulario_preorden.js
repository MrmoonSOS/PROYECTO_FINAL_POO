import { crearPreorden } from "../api.js";
import { escapeHtml } from "../presentacion.js";

// FormularioPreorden: arma una preorden de uno o más platos y muestra ModalComprobante (RF7 y RF8).
// No valida ni fusiona ítems: el backend decide y la interfaz muestra su respuesta.
export class FormularioPreorden {
  constructor(pagina, elementos, modalComprobante) {
    this.pagina = pagina;
    this.elementos = elementos;
    this.modalComprobante = modalComprobante;
    this.itemsSeleccionados = [];
    this.platosConocidos = new Map();

    elementos.agregar.addEventListener("click", () => {
      if (elementos.plato.value === "") {
        this.mostrarError("Selecciona un plato de la lista para agregarlo.");
        return;
      }
      this.agregarItem(Number(elementos.plato.value), elementos.cantidad.value);
    });
    elementos.lista.addEventListener("click", (evento) => {
      const boton = evento.target.closest(".remove-item");
      if (boton) this.quitarItem(Number(boton.dataset.itemId));
    });
    elementos.formulario.addEventListener("submit", (evento) => {
      evento.preventDefault();
      this.enviar();
    });
    this.mostrarItems();
  }

  registrarPlatos(platos) {
    platos.forEach((plato) => this.platosConocidos.set(plato.id, plato));
  }

  actualizarOpciones(platos) {
    this.registrarPlatos(platos);
    const selector = this.elementos.plato;
    const seleccionado = selector.value;
    selector.innerHTML =
      '<option value="">Selecciona un plato...</option>' +
      platos.map((plato) =>
        `<option value="${plato.id}">${escapeHtml(`${plato.nombre} · ${plato.restaurante}`)}</option>`,
      ).join("");
    if (platos.some((plato) => String(plato.id) === seleccionado)) {
      selector.value = seleccionado;
    }
  }

  agregarItem(idPlato, cantidad) {
    this.itemsSeleccionados.push({ idPlato, cantidad });
    this.mostrarItems();
    const plato = this.platosConocidos.get(idPlato);
    this.mostrarMensaje(`Se agregó ${plato ? plato.nombre : "el plato"} a la preorden.`, "success");
  }

  quitarItem(idPlato) {
    this.itemsSeleccionados = this.itemsSeleccionados.filter((item) => item.idPlato !== idPlato);
    this.mostrarItems();
  }

  async enviar() {
    const { nombre, hora, notas, enviar, formulario } = this.elementos;
    const preorden = {
      items: this.itemsSeleccionados.map(({ idPlato, cantidad }) => ({
        id_plato: idPlato,
        cantidad: Number(cantidad),
      })),
      nombre_cliente: nombre.value,
      hora_recogida: hora.value,
      notas: notas.value,
    };

    this.mostrarMensaje("Procesando tu preorden...", "processing");
    enviar.disabled = true;
    try {
      const comprobante = await crearPreorden(preorden);
      this.itemsSeleccionados = [];
      formulario.reset();
      this.mostrarItems();
      this.mostrarMensaje(`Preorden #${comprobante.numero_pedido} confirmada.`, "success");
      this.modalComprobante.mostrar(comprobante);
      await this.pagina.recargarTrasPreorden();
    } catch (error) {
      this.mostrarError(error.message);
    } finally {
      enviar.disabled = false;
    }
  }

  mostrarError(mensaje) {
    this.mostrarMensaje(mensaje, "error");
  }

  mostrarMensaje(texto, tipo) {
    this.elementos.mensaje.textContent = texto;
    this.elementos.mensaje.className = `form-message ${tipo}`;
  }

  mostrarItems() {
    if (this.itemsSeleccionados.length === 0) {
      this.elementos.lista.innerHTML =
        '<li class="selected-item-empty">Aún no has agregado platos.</li>';
      return;
    }
    this.elementos.lista.innerHTML = this.itemsSeleccionados.map(({ idPlato, cantidad }) => {
      const plato = this.platosConocidos.get(idPlato);
      const nombre = plato ? plato.nombre : `Plato ${idPlato}`;
      return `
        <li class="selected-item">
          <span>${escapeHtml(nombre)} · Cantidad: ${escapeHtml(cantidad)}</span>
          <button type="button" class="remove-item" data-item-id="${idPlato}">Quitar</button>
        </li>
      `;
    }).join("");
  }
}
