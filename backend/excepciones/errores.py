"""Jerarquía de excepciones del backend.

ManejadorHTTP captura CampusFoodHubError y traduce cada subclase a un código HTTP:
ValidacionError -> 400, EntidadNoEncontradaError -> 404, ReglaNegocioError -> 409.
"""


class CampusFoodHubError(Exception):
    """Clase base de las excepciones del sistema."""


class ValidacionError(CampusFoodHubError):
    """Entrada inválida: criterio de filtro, ítems, cantidad, nombre u hora (RF2, RF7)."""


class EntidadNoEncontradaError(CampusFoodHubError):
    """Perfil o plato inexistente (RF3, RF7)."""


class ReglaNegocioError(CampusFoodHubError):
    """Regla incumplida: inventario, restaurante único, restaurante cerrado o pedido sin ítems (RF7, RF8)."""
