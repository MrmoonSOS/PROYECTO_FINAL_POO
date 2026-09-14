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

    
class Restaurante:

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
        self._historial_pedidos.append(datetime.now())

    def pedidos_ultima_hora(self):
        limite = datetime.now() - timedelta(hours=1)
        return len([t for t in self._historial_pedidos if t >= limite])


class EstimadorEspera:

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

class Plato:
    
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
        return round(self._precio * (1 - self._descuento_excedente / 100))

    def es_excedente(self):
        return self._descuento_excedente > 0 and self._inventario > 0

    def reducir_inventario(self, cantidad):
        if cantidad > self._inventario:
            raise ValueError(f"Inventario insuficiente para '{self._nombre}'")
        self._inventario -= cantidad

    def tiene_stock(self):
        return self._inventario > 0


class ItemPedido:

    def __init__(self, plato, cantidad):
        self._plato = plato
        self._cantidad = cantidad

    def get_plato(self):
        return self._plato

    def get_cantidad(self):
        return self._cantidad

    def subtotal(self):
        return self._plato.precio_final() * self._cantidad


class Pedido:

    _contador_id = 0

    def __init__(self, estudiante, hora_recogida, notas=""):
        Pedido._contador_id += 1
        self._id = Pedido._contador_id
        self._estudiante = estudiante
        self._items = []
        self._hora_recogida = hora_recogida
        self._notas = notas
        self._estado = "confirmado"

    def get_id(self):
        return self._id

    def get_estudiante(self):
        return self._estudiante

    def get_items(self):
        return self._items

    def get_hora_recogida(self):
        return self._hora_recogida

    def get_notas(self):
        return self._notas

    def get_estado(self):
        return self._estado

    def agregar_item(self, plato, cantidad):
        if cantidad < 1 or cantidad > 5:
            raise ValueError("La cantidad por plato debe estar entre 1 y 5")
        plato.reducir_inventario(cantidad)
        plato.get_restaurante().registrar_pedido()
        self._items.append(ItemPedido(plato, cantidad))

    def total(self):
        return sum(item.subtotal() for item in self._items)


class OptimizadorCombos:

    def optimizar(self, lista_platos, presupuesto):
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

class CampusFoodHub:

    def __init__(self):
        self._restaurantes = []
        self._platos = []
        self._estudiantes = []
        self._pedidos = []
        self._motor_recomendacion = MotorRecomendacion()
        self._estimador_espera = EstimadorEspera()
        self._optimizador_combos = OptimizadorCombos()

    def agregar_restaurante(self, restaurante):
        self._restaurantes.append(restaurante)

    def agregar_plato(self, plato):
        self._platos.append(plato)

    def agregar_estudiante(self, estudiante):
        self._estudiantes.append(estudiante)

    def obtener_estudiantes(self):
        return self._estudiantes

    def obtener_menu_disponible(self):
        return [
            p for p in self._platos
            if p.tiene_stock() and p.get_restaurante().esta_abierto()
        ]
    def filtrar_menu(self, texto_busqueda=None, precio_maximo=None,
                      tiempo_maximo=None, solo_saludable=False, solo_excedente=False):
        resultado = self.obtener_menu_disponible()

        if texto_busqueda:
            texto = texto_busqueda.lower().strip()
            resultado = [
                p for p in resultado
                if texto in p.get_nombre().lower()
                or texto in p.get_restaurante().get_nombre().lower()
                or texto in p.get_categoria().lower()
            ]
        if precio_maximo is not None:
            resultado = [p for p in resultado if p.precio_final() <= precio_maximo]
        if tiempo_maximo is not None:
            resultado = [p for p in resultado if p.get_tiempo_preparacion() <= tiempo_maximo]
        if solo_saludable:
            resultado = [p for p in resultado if p.es_saludable()]
        if solo_excedente:
            resultado = [p for p in resultado if p.es_excedente()]

        return resultado

    def obtener_recomendaciones(self, estudiante, cantidad=4):
        return self._motor_recomendacion.recomendar(
            self.obtener_menu_disponible(), estudiante, cantidad
        )

    def obtener_ofertas(self):
        ofertas = [p for p in self.obtener_menu_disponible() if p.es_excedente()]
        ofertas.sort(key=lambda p: p.get_descuento_excedente(), reverse=True)
        return ofertas

    def obtener_resumen_campus(self):
        activos = self.obtener_menu_disponible()
        restaurantes_abiertos = [r for r in self._restaurantes if r.esta_abierto()]
        ofertas = [p for p in activos if p.es_excedente()]
        plato_mas_rapido = min(activos, key=lambda p: p.get_tiempo_preparacion()) if activos else None
        return {
            "platos_activos": len(activos),
            "restaurantes_abiertos": len(restaurantes_abiertos),
            "ofertas_vigentes": len(ofertas),
            "plato_mas_rapido": plato_mas_rapido,
        }

