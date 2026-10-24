// Cliente HTTP de la interfaz: único punto de acceso a la API del backend.
// Solo traduce llamadas a fetch y respuestas JSON; no contiene lógica de negocio.

async function solicitar(ruta, opciones = {}) {
  let respuesta;
  try {
    respuesta = await fetch(ruta, opciones);
  } catch {
    throw new Error("No fue posible comunicarse con el servidor.");
  }
  let datos;
  try {
    datos = await respuesta.json();
  } catch {
    throw new Error("El servidor envió una respuesta que no se pudo leer.");
  }
  if (!respuesta.ok) {
    throw new Error(datos.error || "El servidor no pudo atender la solicitud.");
  }
  return datos;
}

function enviarJson(ruta, cuerpo) {
  return solicitar(ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  });
}

export function obtenerMenu(criterios = {}) {
  const consulta = new URLSearchParams(criterios).toString();
  return solicitar(consulta ? `/api/menu?${consulta}` : "/api/menu");
}

export function seleccionarPerfil(slug) {
  return enviarJson("/api/perfil", { slug });
}

export function obtenerRecomendaciones() {
  return solicitar("/api/recomendaciones");
}

export function obtenerOfertas() {
  return solicitar("/api/ofertas");
}

export function obtenerResumen() {
  return solicitar("/api/resumen");
}

export function crearPreorden(preorden) {
  return enviarJson("/api/preorden", preorden);
}

export function obtenerCongestion() {
  return solicitar("/api/congestion");
}

export function obtenerCombo(presupuesto) {
  return solicitar(`/api/combo?${new URLSearchParams({ presupuesto })}`);
}
