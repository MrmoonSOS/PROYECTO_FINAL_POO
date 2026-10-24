import { FormularioCombo } from "./formulario_combo.js";
import { FormularioPreorden } from "./formulario_preorden.js";
import { ListaMenu } from "./lista_menu.js";
import { ModalComprobante } from "./modal_comprobante.js";
import { PanelCongestion } from "./panel_congestion.js";
import { PanelFiltros } from "./panel_filtros.js";
import { ResumenCampus } from "./resumen_campus.js";
import { SeccionOfertas } from "./seccion_ofertas.js";
import { SeccionRecomendaciones } from "./seccion_recomendaciones.js";
import { SelectorPerfil } from "./selector_perfil.js";

const $ = (id) => document.getElementById(id);

// PaginaPrincipal: compone los componentes, coordina las recargas y muestra los errores generales.
export class PaginaPrincipal {
  static DURACION_AVISO_MS = 8000;

  constructor() {
    this.aviso = $("avisoGlobal");
    this.avisoTexto = $("avisoGlobalTexto");
    this.temporizadorAviso = null;

    this.modalComprobante = new ModalComprobante($("modalBackdrop"), $("modalDetails"), $("modalClose"));
    this.formularioPreorden = new FormularioPreorden(this, {
      formulario: $("preorderForm"),
      plato: $("menuItemSelect"),
      cantidad: $("quantity"),
      agregar: $("addItem"),
      lista: $("selectedItems"),
      nombre: $("customerName"),
      hora: $("pickupTime"),
      notas: $("notes"),
      enviar: $("preorderForm").querySelector(".submit-preorder"),
      mensaje: $("preorderMessage"),
    }, this.modalComprobante);

    const registrarPlatos = (platos) => this.formularioPreorden.registrarPlatos(platos);
    this.resumenCampus = new ResumenCampus(this, $("summaryCards"));
    this.listaMenu = new ListaMenu(this, $("menuGrid"), $("menuCount"),
      (platos) => this.formularioPreorden.actualizarOpciones(platos));
    this.panelFiltros = new PanelFiltros(this.listaMenu, {
      texto: $("searchInput"),
      precio: $("priceInput"),
      tiempo: $("timeInput"),
      saludable: $("healthyInput"),
      excedente: $("surplusInput"),
      limpiar: $("clearFilters"),
    });
    this.seccionRecomendaciones = new SeccionRecomendaciones(this, $("recommendations"), registrarPlatos);
    this.selectorPerfil = new SelectorPerfil(this, $("profileSelect"), $("profileHint"), this.seccionRecomendaciones);
    this.seccionOfertas = new SeccionOfertas(this, $("offers"), registrarPlatos);
    this.panelCongestion = new PanelCongestion(this, $("congestionGrid"));
    this.formularioCombo = new FormularioCombo($("comboForm"), $("comboBudget"), $("comboMessage"), $("comboResult"));
  }

  async iniciar() {
    document.addEventListener("click", (evento) => {
      const boton = evento.target.closest(".pick-item");
      if (!boton) return;
      this.formularioPreorden.agregarItem(Number(boton.dataset.itemId), 1);
      $("preorden").scrollIntoView({ behavior: "smooth", block: "start" });
    });
    document.addEventListener("keydown", (evento) => {
      if (evento.key === "Escape") this.modalComprobante.cerrar();
    });
    $("avisoGlobalCerrar").addEventListener("click", () => this.ocultarError());

    await Promise.all([
      this.listaMenu.cargarMenu(),
      this.resumenCampus.cargar(),
      this.seccionRecomendaciones.cargar(),
      this.seccionOfertas.cargar(),
      this.panelCongestion.cargar(),
    ]);
  }

  mostrarError(mensaje) {
    this.avisoTexto.textContent = mensaje;
    this.aviso.hidden = false;
    clearTimeout(this.temporizadorAviso);
    this.temporizadorAviso = setTimeout(() => this.ocultarError(), PaginaPrincipal.DURACION_AVISO_MS);
  }

  ocultarError() {
    clearTimeout(this.temporizadorAviso);
    this.aviso.hidden = true;
  }

  recargarTrasPreorden() {
    return Promise.all([
      this.panelFiltros.aplicar(),
      this.resumenCampus.cargar(),
      this.seccionOfertas.cargar(),
      this.seccionRecomendaciones.cargar(),
      this.panelCongestion.cargar(),
    ]);
  }
}
