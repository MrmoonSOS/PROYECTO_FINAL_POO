"""Plato: datos del producto, su inventario y su precio final (RF1, RF2, RF5, RF7, RF10)."""

from backend.excepciones import ReglaNegocioError


class Plato:
    """Mantiene los datos del plato y su inventario, y calcula su precio final."""

    def __init__(self, id_plato, nombre, restaurante, precio, categoria,
                 calorias, tiempo_preparacion, saludable, inventario,
                 descuento_excedente=0):
        self._id = id_plato
        self._nombre = nombre
        self._restaurante = restaurante
        self._precio = precio
        self._categoria = categoria
        self._calorias = calorias
        self._tiempo_preparacion = tiempo_preparacion
        self._saludable = saludable
        self._inventario = inventario
        self._descuento_excedente = descuento_excedente

    def get_id(self):
        return self._id

    def get_nombre(self):
        return self._nombre

    def get_restaurante(self):
        return self._restaurante

    def get_precio(self):
        return self._precio

    def get_categoria(self):
        return self._categoria

    def get_calorias(self):
        return self._calorias

    def get_tiempo_preparacion(self):
        return self._tiempo_preparacion

    def es_saludable(self):
        return self._saludable

    def get_inventario(self):
        return self._inventario

    def get_descuento_excedente(self):
        return self._descuento_excedente

    def precio_final(self):
        """Precio con el descuento por excedente aplicado."""
        return round(self._precio * (1 - self._descuento_excedente / 100))

    def es_excedente(self):
        return self._descuento_excedente > 0 and self._inventario > 0

    def reducir_inventario(self, cantidad):
        """Descuenta unidades del inventario (RF7)."""
        if cantidad > self._inventario:
            raise ReglaNegocioError(f"Inventario insuficiente para '{self._nombre}'.")
        self._inventario -= cantidad

    def tiene_stock(self):
        return self._inventario > 0
