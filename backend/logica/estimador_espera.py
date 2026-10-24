"""EstimadorEspera: congestión y tiempo de espera de cada restaurante (RF9)."""

import numpy as np


class EstimadorEspera:
    """Estima la congestión a partir de los pedidos de la última hora del restaurante."""

    UMBRAL_ALTO = 8

    def factor_congestion(self, restaurante):
        pedidos = restaurante.pedidos_ultima_hora()
        factor = np.log1p(pedidos) / np.log1p(self.UMBRAL_ALTO)
        return float(np.clip(factor, 0.0, 1.5))

    def tiempo_estimado(self, plato):
        factor = self.factor_congestion(plato.get_restaurante())
        return round(plato.get_tiempo_preparacion() * (1 + factor), 1)

    def estado_congestion(self, restaurante):
        factor = self.factor_congestion(restaurante)
        if factor < 0.4:
            return "bajo"
        elif factor < 0.8:
            return "medio"
        else:
            return "alto"
