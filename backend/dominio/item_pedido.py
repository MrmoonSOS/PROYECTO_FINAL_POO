"""ItemPedido: línea de un pedido con un plato y su cantidad (RF7, RF8)."""


class ItemPedido:
    """Representa una línea del pedido."""

    def __init__(self, plato, cantidad):
        self._plato = plato
        self._cantidad = cantidad

    def get_plato(self):
        return self._plato

    def get_cantidad(self):
        return self._cantidad

    def subtotal(self):
        return self._plato.precio_final() * self._cantidad
