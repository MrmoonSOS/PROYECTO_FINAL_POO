// PanelFiltros: lee los cinco controles de filtrado y recarga ListaMenu (RF2).
// "Limpiar filtros" vacía los controles y vuelve a pedir el menú sin criterios.
export class PanelFiltros {
  static ESPERA_ESCRITURA_MS = 350;

  constructor(listaMenu, controles) {
    this.listaMenu = listaMenu;
    this.controles = controles;
    this.temporizador = null;

    [controles.texto, controles.precio, controles.tiempo].forEach((campo) => {
      campo.addEventListener("input", () => {
        clearTimeout(this.temporizador);
        this.temporizador = setTimeout(() => this.aplicar(), PanelFiltros.ESPERA_ESCRITURA_MS);
      });
    });
    [controles.saludable, controles.excedente].forEach((casilla) => {
      casilla.addEventListener("change", () => this.aplicar());
    });
    controles.limpiar.addEventListener("click", () => this.limpiar());
  }

  leerCriterios() {
    const { texto, precio, tiempo, saludable, excedente } = this.controles;
    const criterios = {};
    if (texto.value !== "") criterios.texto = texto.value;
    if (precio.value !== "") criterios.precio_maximo = precio.value;
    if (tiempo.value !== "") criterios.tiempo_maximo = tiempo.value;
    if (saludable.checked) criterios.solo_saludable = "true";
    if (excedente.checked) criterios.solo_excedente = "true";
    return criterios;
  }

  aplicar() {
    clearTimeout(this.temporizador);
    return this.listaMenu.cargarMenu(this.leerCriterios());
  }

  limpiar() {
    const { texto, precio, tiempo, saludable, excedente } = this.controles;
    texto.value = "";
    precio.value = "";
    tiempo.value = "";
    saludable.checked = false;
    excedente.checked = false;
    return this.aplicar();
  }
}
