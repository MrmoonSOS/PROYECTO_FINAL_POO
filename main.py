import numpy as np
from datetime import datetime, timedelta

class Estudiante:

    PERFILES_PREDEFINIDOS = {
        "balance": {
            "presupuesto": 25000, "enfoque_salud": 0.5,
            "enfoque_velocidad": 0.5, "cocina_preferida": None,
        },
        "fit_rapido": {
            "presupuesto": 20000, "enfoque_salud": 0.8,
            "enfoque_velocidad": 0.8, "cocina_preferida": None,
        },
        "ahorro_total": {
            "presupuesto": 12000, "enfoque_salud": 0.3,
            "enfoque_velocidad": 0.3, "cocina_preferida": None,
        },
        "antojo_del_dia": {
            "presupuesto": 30000, "enfoque_salud": 0.1,
            "enfoque_velocidad": 0.4, "cocina_preferida": None,
        },
        "vegetariano": {
            "presupuesto": 22000, "enfoque_salud": 0.9,
            "enfoque_velocidad": 0.5, "cocina_preferida": "vegetariana",
        },
    }

    TASA_APRENDIZAJE = 0.15

    def __init__(self, id_estudiante, nombre, presupuesto,
                 enfoque_salud=0.5, enfoque_velocidad=0.5, cocina_preferida=None):
        self._id = id_estudiante
        self._nombre = nombre
        self._presupuesto = presupuesto
        self._enfoque_salud = enfoque_salud
        self._enfoque_velocidad = enfoque_velocidad
        self._cocina_preferida = cocina_preferida
        self._perfil_activo = None
        self._historial_pedidos = []

    # --- Getters ---
    def get_id(self):
        return self._id

    def get_nombre(self):
        return self._nombre

    def get_presupuesto(self):
        return self._presupuesto

    def get_enfoque_salud(self):
        return self._enfoque_salud

    def get_enfoque_velocidad(self):
        return self._enfoque_velocidad

    def get_cocina_preferida(self):
        return self._cocina_preferida

    def get_perfil_activo(self):
        return self._perfil_activo

    def get_historial(self):
        return self._historial_pedidos

    # --- Setters ---
    def set_presupuesto(self, valor):
        if valor < 0:
            raise ValueError("El presupuesto no puede ser negativo")
        self._presupuesto = valor

    def set_cocina_preferida(self, valor):
        self._cocina_preferida = valor

    def set_enfoque_salud(self, valor):
        self._enfoque_salud = max(0.0, min(1.0, valor))

    def set_enfoque_velocidad(self, valor):
        self._enfoque_velocidad = max(0.0, min(1.0, valor))

    # --- Comportamiento (RF08) ---
    def aplicar_perfil(self, slug):
        """Configura presupuesto/enfoques a partir de un perfil predefinido."""
        slug = slug.lower().strip()
        if slug not in Estudiante.PERFILES_PREDEFINIDOS:
            opciones = ", ".join(Estudiante.PERFILES_PREDEFINIDOS.keys())
            raise ValueError(f"Perfil '{slug}' no existe. Opciones: {opciones}")
        datos = Estudiante.PERFILES_PREDEFINIDOS[slug]
        self.set_presupuesto(datos["presupuesto"])
        self.set_enfoque_salud(datos["enfoque_salud"])
        self.set_enfoque_velocidad(datos["enfoque_velocidad"])
        if datos["cocina_preferida"] is not None:
            self.set_cocina_preferida(datos["cocina_preferida"])
        self._perfil_activo = slug

    def registrar_pedido(self, pedido):
        self._historial_pedidos.append(pedido)

    def actualizar_perfil_segun_eleccion(self, plato_elegido):
        objetivo_salud = 1.0 if plato_elegido.es_saludable() else 0.0
        self._enfoque_salud += Estudiante.TASA_APRENDIZAJE * (objetivo_salud - self._enfoque_salud)
        self._enfoque_salud = max(0.0, min(1.0, self._enfoque_salud))

        objetivo_velocidad = 1.0 if plato_elegido.get_tiempo_preparacion() <= 10 else 0.0
        self._enfoque_velocidad += Estudiante.TASA_APRENDIZAJE * (objetivo_velocidad - self._enfoque_velocidad)
        self._enfoque_velocidad = max(0.0, min(1.0, self._enfoque_velocidad))


class MotorRecomendacion:

    PESO_PRESUPUESTO = 0.35
    PESO_SALUD = 0.25
    PESO_VELOCIDAD = 0.25
    PESO_COCINA = 0.15
    TECHO_TIEMPO_MIN = 30

    def calcular_puntajes(self, lista_platos, estudiante):

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
            razones.append("es una opcion saludable, acorde a tu perfil")
        if plato.get_tiempo_preparacion() <= 10 and estudiante.get_enfoque_velocidad() >= 0.5:
            razones.append("se prepara rapido")
        if plato.get_categoria() == estudiante.get_cocina_preferida():
            razones.append(f"es de tu cocina preferida ({estudiante.get_cocina_preferida()})")
        if plato.es_excedente():
            razones.append("esta en oferta por excedente")
        if not razones:
            return "Es la mejor opcion disponible segun tu perfil actual."
        return "Te lo recomendamos porque " + ", ".join(razones) + "."

    def recomendar(self, lista_platos, estudiante, cantidad=4):
        candidatos = [p for p in lista_platos if p.tiene_stock()]
        puntajes = self.calcular_puntajes(candidatos, estudiante)
        puntuados = [
            (plato, round(float(puntaje), 4), self.generar_razon(plato, estudiante))
            for plato, puntaje in zip(candidatos, puntajes)
        ]
        puntuados.sort(key=lambda t: t[1], reverse=True)
        return puntuados[:cantidad]