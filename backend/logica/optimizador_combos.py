"""OptimizadorCombos: combo de ofertas de mayor ahorro dentro de un presupuesto (RF10)."""

import numpy as np


class OptimizadorCombos:
    """Resuelve una mochila 0/1 sobre los platos en oferta con inventario."""

    def optimizar(self, lista_platos, presupuesto):
        """Devuelve la tupla (platos del combo, gasto total, ahorro)."""
        candidatos = [p for p in lista_platos if p.es_excedente() and p.tiene_stock()]
        if not candidatos or presupuesto <= 0:
            return [], 0, 0

        costos = np.array([p.precio_final() for p in candidatos], dtype=int)
        ahorros = np.array([p.get_precio() - p.precio_final() for p in candidatos], dtype=int)

        tope = int(min(presupuesto, costos.sum()))

        mejor_ahorro = np.zeros(tope + 1, dtype=int)
        tomado = np.zeros((len(candidatos), tope + 1), dtype=bool)

        for i in range(len(candidatos)):
            costo = int(costos[i])
            if costo > tope:
                continue
            con_plato = mejor_ahorro[:tope + 1 - costo] + int(ahorros[i])
            sin_plato = mejor_ahorro[costo:]
            mejora = con_plato > sin_plato
            mejor_ahorro[costo:] = np.where(mejora, con_plato, sin_plato)
            tomado[i, costo:] = mejora

        elegidos = []
        capacidad = tope
        for i in range(len(candidatos) - 1, -1, -1):
            if tomado[i, capacidad]:
                elegidos.append(candidatos[i])
                capacidad -= int(costos[i])
        elegidos.reverse()

        gasto = sum(p.precio_final() for p in elegidos)
        return elegidos, gasto, int(mejor_ahorro[tope])
