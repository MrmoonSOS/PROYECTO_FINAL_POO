"""Estudiante: perfil de preferencias e historial de pedidos (RF3, RF4, RF7)."""

from backend.excepciones import EntidadNoEncontradaError, ValidacionError


class Estudiante:
    """Mantiene y modifica el perfil y el historial del estudiante."""

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

    def set_presupuesto(self, valor):
        if valor < 0:
            raise ValidacionError("El presupuesto no puede ser negativo.")
        self._presupuesto = valor

    def set_cocina_preferida(self, valor):
        self._cocina_preferida = valor

    def set_enfoque_salud(self, valor):
        self._enfoque_salud = max(0.0, min(1.0, valor))

    def set_enfoque_velocidad(self, valor):
        self._enfoque_velocidad = max(0.0, min(1.0, valor))

    def aplicar_perfil(self, slug):
        """Configura presupuesto, enfoques y cocina preferida a partir de un perfil predefinido (RF3)."""
        slug = slug.lower().strip()
        if slug not in Estudiante.PERFILES_PREDEFINIDOS:
            raise EntidadNoEncontradaError(f"El perfil '{slug}' no existe.")
        datos = Estudiante.PERFILES_PREDEFINIDOS[slug]
        self.set_presupuesto(datos["presupuesto"])
        self.set_enfoque_salud(datos["enfoque_salud"])
        self.set_enfoque_velocidad(datos["enfoque_velocidad"])
        if datos["cocina_preferida"] is not None:
            self.set_cocina_preferida(datos["cocina_preferida"])
        self._perfil_activo = slug

    def registrar_pedido(self, pedido):
        """Agrega una preorden al historial del estudiante (RF7)."""
        self._historial_pedidos.append(pedido)

    def actualizar_perfil_segun_eleccion(self, plato_elegido):
        """Acerca los enfoques de salud y velocidad al plato elegido (RF7)."""
        objetivo_salud = 1.0 if plato_elegido.es_saludable() else 0.0
        self._enfoque_salud += Estudiante.TASA_APRENDIZAJE * (objetivo_salud - self._enfoque_salud)
        self._enfoque_salud = max(0.0, min(1.0, self._enfoque_salud))

        objetivo_velocidad = 1.0 if plato_elegido.get_tiempo_preparacion() <= 10 else 0.0
        self._enfoque_velocidad += Estudiante.TASA_APRENDIZAJE * (objetivo_velocidad - self._enfoque_velocidad)
        self._enfoque_velocidad = max(0.0, min(1.0, self._enfoque_velocidad))
