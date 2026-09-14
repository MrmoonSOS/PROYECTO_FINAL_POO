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

    def obtener_recomendaciones(self, estudiante, cantidad=4):
        return self._motor_recomendacion.recomendar(
            self.obtener_menu_disponible(), estudiante, cantidad
        )

    def crear_preorden(self, estudiante, items, hora_recogida, notas=""):
        if not items:
            raise ValueError("La preorden debe incluir al menos un plato")

        seleccion = []
        for id_plato, cantidad in items:
            plato = next((p for p in self._platos if p.get_id() == id_plato), None)
            if plato is None:
                raise ValueError(f"No existe un plato con id {id_plato}")
            seleccion.append((plato, cantidad))

        cantidad_por_plato = {}
        for plato, cantidad in seleccion:
            cantidad_por_plato[plato] = cantidad_por_plato.get(plato, 0) + cantidad
        for plato, cantidad_total in cantidad_por_plato.items():
            if cantidad_total < 1 or cantidad_total > 5:
                raise ValueError("La cantidad por plato debe estar entre 1 y 5")
            if cantidad_total > plato.get_inventario():
                raise ValueError(f"Inventario insuficiente para '{plato.get_nombre()}'")

        if len({p.get_restaurante().get_id() for p, _ in seleccion}) > 1:
            raise ValueError("Todos los platos de una preorden deben ser del mismo restaurante")

        pedido = Pedido(estudiante, hora_recogida, notas)
        for plato, cantidad in seleccion:
            pedido.agregar_item(plato, cantidad)
            estudiante.actualizar_perfil_segun_eleccion(plato)

        estudiante.registrar_pedido(pedido)
        self._pedidos.append(pedido)
        return pedido

    def obtener_combo_optimo(self, presupuesto):
        return self._optimizador_combos.optimizar(self.obtener_menu_disponible(), presupuesto)


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

    def obtener_estado_restaurantes(self):
        resultado = []
        for restaurante in self._restaurantes:
            if not restaurante.esta_abierto():
                continue
            platos_restaurante = [p for p in self._platos if p.get_restaurante() is restaurante]
            tiempo_prom = (
                round(sum(self._estimador_espera.tiempo_estimado(p) for p in platos_restaurante) / len(platos_restaurante), 1)
                if platos_restaurante else 0
            )
            resultado.append({
                "restaurante": restaurante,
                "congestion": self._estimador_espera.estado_congestion(restaurante),
                "tiempo_estimado_min": tiempo_prom,
            })
        return resultado

##MENU####


def sembrar_datos(hub):
    r1 = Restaurante(1, "Sazón Criollo", "colombiana", 4.5, "Bloque 12")
    r2 = Restaurante(2, "Green Bowl", "vegetariana", 4.7, "Bloque 20")
    hub.agregar_restaurante(r1)
    hub.agregar_restaurante(r2)

    platos = [
        Plato(1, "Bandeja paisa", r1, 18000, "colombiana", 950, 20, False, 10, 0),
        Plato(2, "Ensalada César", r2, 14000, "vegetariana", 350, 8, True, 5, 0),
        Plato(3, "Wrap de pollo", r1, 12000, "colombiana", 500, 10, True, 2, 30),
        Plato(4, "Bowl de quinua", r2, 16000, "vegetariana", 420, 12, True, 6, 0),
        Plato(5, "Arroz con pollo (excedente)", r1, 15000, "colombiana", 600, 15, False, 4, 40),
        Plato(6, "Jugo natural", r2, 6000, "vegetariana", 120, 5, True, 8, 20),
    ]
    for p in platos:
        hub.agregar_plato(p)


def registrar_estudiante(hub, nombre):
    """Crea un estudiante con presupuesto por defecto y lo agrega al hub."""
    nuevo = Estudiante(len(hub.obtener_estudiantes()) + 1, nombre, presupuesto=15000)
    hub.agregar_estudiante(nuevo)
    return nuevo


def elegir_estudiante(hub):
    print("\n--- Estudiantes registrados ---")
    for est in hub.obtener_estudiantes():
        print(f"  [{est.get_id()}] {est.get_nombre()}")
    print("  [0] Crear nuevo estudiante")
    opcion = input("Selecciona un estudiante por id: ").strip()

    if opcion == "0":
        nombre = input("Nombre: ").strip()
        nuevo = registrar_estudiante(hub, nombre)
        print(f"Estudiante '{nombre}' creado con id {nuevo.get_id()}.")
        return nuevo

    for est in hub.obtener_estudiantes():
        if str(est.get_id()) == opcion:
            return est
    print("Id no encontrado, se crea un estudiante temporal por defecto.")
    return registrar_estudiante(hub, "Invitado")


def leer_entero(mensaje):
    """Lee un entero positivo por consola; devuelve None si no es valido."""
    valor = input(mensaje).strip()
    return int(valor) if valor.isdigit() else None

# Menu principal y utilidades de impresion

def mostrar_menu_principal(estudiante):
    print("\n" + "=" * 60)
    print(f" CampusFoodHub Inteligente | Usuario: {estudiante.get_nombre()} "
          f"| Perfil: {estudiante.get_perfil_activo() or 'sin definir'}")
    print("=" * 60)
    print(" 1. Ver menu disponible")
    print(" 2. Buscar / filtrar platos")
    print(" 3. Limpiar filtros")
    print(" 4. Elegir perfil predefinido")
    print(" 5. Ver mis recomendaciones")
    print(" 6. Ver ofertas de excedentes")
    print(" 7. Consultar congestion de restaurantes")
    print(" 8. Obtener combo optimo por presupuesto")
    print(" 9. Crear preorden")
    print("10. Ver resumen del campus")
    print("11. Cambiar de estudiante")
    print(" 0. Salir")


def imprimir_platos(platos):
    if not platos:
        print("  (sin resultados)")
        return
    for p in platos:
        etiqueta = " [OFERTA]" if p.es_excedente() else ""
        print(f"  [{p.get_id()}] {p.get_nombre()} - {p.get_restaurante().get_nombre()} "
              f"- ${p.precio_final()} - {p.get_tiempo_preparacion()} min{etiqueta}")


# Filtros (RF02-RF07): el estado de los filtros vive solo en la consola,
# no en el modelo del mundo.

def submenu_filtros(filtros):
    print("\n--- Filtros ---")
    print(f" Filtros actuales: {filtros}")
    print(" a. Buscar por texto (RF02)")
    print(" b. Precio maximo (RF03)")
    print(" c. Tiempo maximo de preparacion (RF04)")
    print(" d. Solo saludables (RF05)")
    print(" e. Solo ofertas de excedente (RF06)")
    print(" f. Volver")
    opcion = input("Elige una opcion: ").strip().lower()
    if opcion == "a":
        texto = input("Texto a buscar (max 80 caracteres): ").strip()[:80]
        filtros["texto_busqueda"] = texto or None
    elif opcion == "b":
        filtros["precio_maximo"] = leer_entero("Precio maximo en COP: ")
    elif opcion == "c":
        filtros["tiempo_maximo"] = leer_entero("Tiempo maximo en minutos: ")
    elif opcion == "d":
        filtros["solo_saludable"] = not filtros["solo_saludable"]
    elif opcion == "e":
        filtros["solo_excedente"] = not filtros["solo_excedente"]


def filtros_por_defecto():
    """Estado vacio de los filtros de busqueda (RF07)."""
    return {
        "texto_busqueda": None, "precio_maximo": None,
        "tiempo_maximo": None, "solo_saludable": False, "solo_excedente": False,
    }


def limpiar_filtros(filtros):
    filtros.update(filtros_por_defecto())
    print("Filtros reiniciados.")

# Perfil, recomendaciones, ofertas, congestion, combo y resumen
# (RF08-RF11, RF14-RF15)

def submenu_perfil(estudiante):
    print("\n--- Perfiles disponibles ---")
    for slug in Estudiante.PERFILES_PREDEFINIDOS:
        print(f"  - {slug}")
    slug = input("Escribe el perfil que deseas activar: ").strip()
    try:
        estudiante.aplicar_perfil(slug)
        print(f"Perfil '{slug}' activado. Tus recomendaciones se recalcularan.")
    except ValueError as e:
        print(f"Error: {e}")


def mostrar_recomendaciones(hub, estudiante):
    print(f"\n--- Recomendaciones para {estudiante.get_nombre()} ---")
    resultados = hub.obtener_recomendaciones(estudiante)
    if not resultados:
        print("  No hay recomendaciones disponibles en este momento.")
    for plato, puntaje, razon in resultados:
        print(f"  [{plato.get_id()}] {plato.get_nombre()} | matchScore={puntaje} | {razon}")


def mostrar_ofertas(hub):
    print("\n--- Ofertas de excedente (mayor a menor descuento) ---")
    ofertas = hub.obtener_ofertas()
    if not ofertas:
        print("  No hay ofertas activas.")
    for p in ofertas:
        print(f"  [{p.get_id()}] {p.get_nombre()} | ${p.get_precio()} -> ${p.precio_final()} "
              f"(-{p.get_descuento_excedente()}%) | disponibles: {p.get_inventario()}")


def mostrar_congestion(hub):
    print("\n--- Congestion por restaurante ---")
    for estado in hub.obtener_estado_restaurantes():
        r = estado["restaurante"]
        print(f"  {r.get_nombre()}: congestion {estado['congestion']} "
              f"| tiempo estimado ~{estado['tiempo_estimado_min']} min")


def flujo_combo_optimo(hub):
    presupuesto = leer_entero("\nPresupuesto disponible en COP: ")
    if presupuesto is None:
        print("Presupuesto invalido.")
        return
    combo, gasto, ahorro = hub.obtener_combo_optimo(presupuesto)
    print("\n--- Combo optimo ---")
    if not combo:
        print("  No se encontro ningun combo dentro del presupuesto.")
        return
    for p in combo:
        print(f"  {p.get_nombre()} - ${p.precio_final()}")
    print(f"  Gasto total: ${gasto} | Ahorro total: ${ahorro}")


def mostrar_resumen(hub):
    resumen = hub.obtener_resumen_campus()
    print("\n--- Resumen del campus ---")
    print(f"  Platos activos: {resumen['platos_activos']}")
    print(f"  Restaurantes abiertos: {resumen['restaurantes_abiertos']}")
    print(f"  Ofertas vigentes: {resumen['ofertas_vigentes']}")
    if resumen["plato_mas_rapido"]:
        print(f"  Plato mas rapido: {resumen['plato_mas_rapido'].get_nombre()} "
              f"({resumen['plato_mas_rapido'].get_tiempo_preparacion()} min)")
    else:
        print("  No hay platos activos en este momento.")


# Preorden y comprobante (RF12-RF13)

def mostrar_comprobante(pedido):
    """RF13: funcion de consola que arma el comprobante a partir de Pedido."""
    print("\n" + "-" * 40)
    print("        COMPROBANTE DE PREORDEN")
    print("-" * 40)
    print(f" Pedido N.:     {pedido.get_id()}")
    print(f" Cliente:       {pedido.get_estudiante().get_nombre()}")
    restaurante = pedido.get_items()[0].get_plato().get_restaurante()
    print(f" Restaurante:   {restaurante.get_nombre()}")
    print(f" Hora recogida: {pedido.get_hora_recogida()}")
    print(" Platos:")
    for item in pedido.get_items():
        print(f"   - {item.get_cantidad()}x {item.get_plato().get_nombre()} = ${item.subtotal()}")
    if pedido.get_notas():
        print(f" Notas:         {pedido.get_notas()}")
    print(f" TOTAL:         ${pedido.total()}")
    print("-" * 40)


def flujo_crear_preorden(hub, estudiante):
    print("\n--- Crear preorden ---")
    print("Menu disponible:")
    imprimir_platos(hub.obtener_menu_disponible())

    items = []
    while True:
        id_plato = input("Id del plato a agregar (enter para terminar): ").strip()
        if id_plato == "":
            break
        if not id_plato.isdigit():
            print("Id invalido.")
            continue
        cantidad = leer_entero("Cantidad (1-5): ")
        if cantidad is None:
            print("Cantidad invalida.")
            continue
        items.append((int(id_plato), cantidad))

    if not items:
        print("No se agrego ningun plato, se cancela la preorden.")
        return

    hora_recogida = input("Hora de recogida (ej. 12:30): ").strip()
    notas = input("Notas (opcional): ").strip()

    try:
        pedido = hub.crear_preorden(estudiante, items, hora_recogida, notas)
        print(f"\nPreorden #{pedido.get_id()} creada con exito.")
        mostrar_comprobante(pedido)
    except ValueError as e:
        print(f"No se pudo crear la preorden: {e}")


# Bucle principal
def iniciar_consola():
    hub = CampusFoodHub()
    sembrar_datos(hub)
    estudiante = elegir_estudiante(hub)
    filtros = filtros_por_defecto()

    while True:
        mostrar_menu_principal(estudiante)
        opcion = input("Elige una opcion: ").strip()

        if opcion == "1":
            print("\n--- Menu disponible ---")
            imprimir_platos(hub.obtener_menu_disponible())
        elif opcion == "2":
            submenu_filtros(filtros)
            print("\n--- Resultado de la busqueda ---")
            imprimir_platos(hub.filtrar_menu(**filtros))
        elif opcion == "3":
            limpiar_filtros(filtros)
        elif opcion == "4":
            submenu_perfil(estudiante)
        elif opcion == "5":
            mostrar_recomendaciones(hub, estudiante)
        elif opcion == "6":
            mostrar_ofertas(hub)
        elif opcion == "7":
            mostrar_congestion(hub)
        elif opcion == "8":
            flujo_combo_optimo(hub)
        elif opcion == "9":
            flujo_crear_preorden(hub, estudiante)
        elif opcion == "10":
            mostrar_resumen(hub)
        elif opcion == "11":
            estudiante = elegir_estudiante(hub)
        elif opcion == "0":
            print("Hasta luego!")
            break
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    iniciar_consola()