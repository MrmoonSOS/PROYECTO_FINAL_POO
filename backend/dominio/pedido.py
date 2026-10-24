"""Pedido: datos de la preorden y generación de su comprobante (RF7, RF8)."""

from backend.dominio.item_pedido import ItemPedido
from backend.excepciones import ReglaNegocioError, ValidacionError


class Pedido:
    """Mantiene los datos de la preorden y genera su comprobante."""

    _contador_id = 0

    def __init__(self, estudiante, nombre_cliente, hora_recogida, notas=""):
        Pedido._contador_id += 1
        self._id = Pedido._contador_id
        self._estudiante = estudiante
        self._nombre_cliente = nombre_cliente
        self._items = []
        self._hora_recogida = hora_recogida
        self._notas = notas
        self._estado = "confirmado"

    def get_id(self):
        return self._id

    def get_estudiante(self):
        return self._estudiante

    def get_nombre_cliente(self):
        return self._nombre_cliente

    def get_items(self):
        return self._items

    def get_hora_recogida(self):
        return self._hora_recogida

    def get_notas(self):
        return self._notas

    def get_estado(self):
        return self._estado

    def agregar_item(self, plato, cantidad):
        """Agrega una línea al pedido; solo valida la cantidad (RF7)."""
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or not 1 <= cantidad <= 5:
            raise ValidacionError("La cantidad por plato debe ser un entero entre 1 y 5.")
        self._items.append(ItemPedido(plato, cantidad))

    def total(self):
        return sum(item.subtotal() for item in self._items)

    def get_restaurante(self):
        """Restaurante del pedido: el de su primer ítem (RF8)."""
        if not self._items:
            raise ReglaNegocioError("El pedido no tiene ítems.")
        return self._items[0].get_plato().get_restaurante()

    def generar_comprobante(self):
        """Comprobante de la preorden para el modal de confirmación (RF8)."""
        restaurante = self.get_restaurante()
        return {
            "numero_pedido": self._id,
            "cliente": self._nombre_cliente,
            "restaurante": restaurante.get_nombre(),
            "hora_recogida": self._hora_recogida,
            "lineas": [
                {
                    "plato": item.get_plato().get_nombre(),
                    "cantidad": item.get_cantidad(),
                    "subtotal": item.subtotal(),
                }
                for item in self._items
            ],
            "notas": self._notas,
            "total": self.total(),
        }
