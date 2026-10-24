// Utilidades de presentación compartidas por los componentes: escape de HTML,
// formato de moneda y plantillas de tarjetas. No realizan cálculos de negocio.

export function escapeHtml(valor) {
  return String(valor ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function formatCOP(valor) {
  return "$" + Number(valor).toLocaleString("es-CO");
}

export function estadoVacio(mensaje) {
  return `<div class="empty-state">${escapeHtml(mensaje)}</div>`;
}

export function tarjetaPlato(plato, { matchScore = null, razon = "", etiquetaAccion = "Preordenar" } = {}) {
  const bloquePrecio = plato.es_excedente
    ? `<div class="price-row">
         <span class="price-current">${formatCOP(plato.precio_final)}</span>
         <span class="price-original">${formatCOP(plato.precio)}</span>
       </div>`
    : `<div class="price-row">
         <span class="price-current">${formatCOP(plato.precio_final)}</span>
       </div>`;

  const insigniaPuntaje = matchScore !== null
    ? `<div class="match-score">${Math.round(matchScore * 100)}%</div>`
    : "";

  const textoRazon = razon
    ? `<p class="recommendation-reason">${escapeHtml(razon)}</p>`
    : "";

  const etiquetas = `
    ${plato.saludable ? '<span class="tag-badge tag-healthy">Saludable</span>' : ""}
    ${plato.es_excedente ? `<span class="tag-badge tag-surplus">-${plato.descuento_excedente}% oferta</span>` : ""}
  `;

  return `
    <article class="card${matchScore !== null ? " card--recomendacion" : ""}">
      ${insigniaPuntaje}
      <div class="card-header">
        <div class="card-title-block">
          <h3>${escapeHtml(plato.nombre)}</h3>
          <p class="restaurant-name">${escapeHtml(plato.restaurante)}</p>
        </div>
        <span class="card-category">${escapeHtml(plato.categoria)}</span>
      </div>
      <div class="meta-row">
        <span class="tag">${plato.tiempo_preparacion} min</span>
        <span class="tag">${plato.calorias} kcal</span>
        <span class="tag">Disponibles: ${plato.inventario}</span>
      </div>
      <div class="tags-row">${etiquetas}</div>
      ${bloquePrecio}
      ${textoRazon}
      <button type="button" data-item-id="${plato.id}" class="pick-item">${escapeHtml(etiquetaAccion)}</button>
    </article>
  `;
}
