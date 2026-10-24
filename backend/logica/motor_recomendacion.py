"""MotorRecomendacion: puntúa y ordena los platos según el perfil del estudiante (RF4)."""

import numpy as np


class MotorRecomendacion:
    """Calcula el matchScore de cada plato; solo lee los datos del estudiante."""

    PESO_PRESUPUESTO = 0.35
    PESO_SALUD = 0.25
    PESO_VELOCIDAD = 0.25
    PESO_COCINA = 0.15
    TECHO_TIEMPO_MIN = 30

    def calcular_puntajes(self, lista_platos, estudiante):
        """Puntajes vectorizados de una lista de platos."""
        if not lista_platos:
            return np.array([])

        precios = np.array([p.precio_final() for p in lista_platos], dtype=float)
        tiempos = np.array([p.get_tiempo_preparacion() for p in lista_platos], dtype=float)
        es_saludable = np.array([p.es_saludable() for p in lista_platos], dtype=bool)
        es_cocina_favorita = np.array(
            [p.get_categoria() == estudiante.get_cocina_preferida() for p in lista_platos],
            dtype=bool,
        )

        presupuesto = estudiante.get_presupuesto()
        if presupuesto <= 0:
            afinidad_presupuesto = np.zeros(len(lista_platos))
        else:
            dentro = 1.0 - 0.5 * (precios / presupuesto)
            exceso = (precios - presupuesto) / presupuesto
            fuera = np.maximum(0.0, 0.5 - exceso)
            afinidad_presupuesto = np.where(precios <= presupuesto, dentro, fuera)

        enfoque_salud = estudiante.get_enfoque_salud()
        afinidad_salud = np.where(es_saludable, enfoque_salud, 1.0 - enfoque_salud)

        enfoque_velocidad = estudiante.get_enfoque_velocidad()
        rapidez = np.maximum(0.0, 1.0 - tiempos / self.TECHO_TIEMPO_MIN)
        afinidad_velocidad = enfoque_velocidad * rapidez + (1 - enfoque_velocidad) * 0.5

        afinidad_cocina = np.where(es_cocina_favorita, 1.0, 0.5)

        return (
            self.PESO_PRESUPUESTO * afinidad_presupuesto
            + self.PESO_SALUD * afinidad_salud
            + self.PESO_VELOCIDAD * afinidad_velocidad
            + self.PESO_COCINA * afinidad_cocina
        )

    def calcular_puntaje(self, plato, estudiante):
        return round(float(self.calcular_puntajes([plato], estudiante)[0]), 4)

    def generar_razon(self, plato, estudiante):
        razones = []
        if plato.precio_final() <= estudiante.get_presupuesto():
            razones.append("se ajusta a tu presupuesto")
        if plato.es_saludable() and estudiante.get_enfoque_salud() >= 0.5:
            razones.append("es una opción saludable, acorde a tu perfil")
        if plato.get_tiempo_preparacion() <= 10 and estudiante.get_enfoque_velocidad() >= 0.5:
            razones.append("se prepara rápido")
        if plato.get_categoria() == estudiante.get_cocina_preferida():
            razones.append(f"es de tu cocina preferida ({estudiante.get_cocina_preferida()})")
        if plato.es_excedente():
            razones.append("está en oferta por excedente")
        if not razones:
            return "Es la mejor opción disponible según tu perfil actual."
        return "Te lo recomendamos porque " + ", ".join(razones) + "."

    def recomendar(self, lista_platos, estudiante, cantidad=4):
        """Lista ordenada de tuplas (plato, matchScore, razón), de mayor a menor puntaje."""
        candidatos = [p for p in lista_platos if p.tiene_stock()]
        puntajes = self.calcular_puntajes(candidatos, estudiante)
        puntuados = [
            (plato, round(float(puntaje), 4), self.generar_razon(plato, estudiante))
            for plato, puntaje in zip(candidatos, puntajes)
        ]
        puntuados.sort(key=lambda t: t[1], reverse=True)
        return puntuados[:cantidad]
