import { obtenerRecomendaciones } from "../api.js";
import { estadoVacio, tarjetaPlato } from "../presentacion.js";

// SeccionRecomendaciones: platos recomendados para el perfil activo (RF4).
export class SeccionRecomendaciones {
  constructor(pagina, contenedor, alRecibirPlatos) {
    this.pagina = pagina;
    this.contenedor = contenedor;
    this.alRecibirPlatos = alRecibirPlatos;
  }

  async cargar() {
    try {
      this.mostrar(await obtenerRecomendaciones());
    } catch (error) {
      this.pagina.mostrarError(error.message);
    }
  }

  mostrar(recomendaciones) {
    if (recomendaciones.length === 0) {
      this.contenedor.innerHTML = estadoVacio("No hay recomendaciones disponibles");
    } else {
      this.contenedor.innerHTML = recomendaciones
        .map(({ plato, matchScore, razon }) =>
          tarjetaPlato(plato, { matchScore, razon, etiquetaAccion: "Quiero este" }))
        .join("");
    }
    this.alRecibirPlatos(recomendaciones.map(({ plato }) => plato));
  }
}
