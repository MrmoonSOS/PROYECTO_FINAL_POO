"""Restaurante: datos del punto de venta, su estado y su historial de pedidos (RF1, RF7, RF9)."""

from datetime import datetime, timedelta


class Restaurante:
    """Mantiene los datos y el estado del restaurante y su historial de pedidos."""

    def __init__(self, id_restaurante, nombre, cocina, calificacion, ubicacion, abierto=True):
        self._id = id_restaurante
        self._nombre = nombre
        self._cocina = cocina
        self._calificacion = calificacion
        self._ubicacion = ubicacion
        self._abierto = abierto
        self._historial_pedidos = []

    def get_id(self):
        return self._id

    def get_nombre(self):
        return self._nombre

    def get_cocina(self):
        return self._cocina

    def get_calificacion(self):
        return self._calificacion

    def get_ubicacion(self):
        return self._ubicacion

    def esta_abierto(self):
        return self._abierto

    def set_abierto(self, valor):
        self._abierto = valor

    def registrar_pedido(self):
        """Agrega la marca de tiempo de una preorden; se invoca una sola vez por preorden (RF7)."""
        self._historial_pedidos.append(datetime.now())

    def pedidos_ultima_hora(self):
        """Cantidad de pedidos registrados en la última hora (RF9)."""
        limite = datetime.now() - timedelta(hours=1)
        return len([t for t in self._historial_pedidos if t >= limite])
