"""CampusFoodHub: fachada de la lógica de negocio (RF1, RF2, RF4 a RF7, RF9, RF10).

Administra las colecciones de restaurantes, platos, estudiantes y pedidos, y los tres
motores. Valida las entradas y orquesta las operaciones; cada entidad modifica su
propia información.
"""

import re

from backend.dominio.pedido import Pedido
from backend.excepciones import EntidadNoEncontradaError, ReglaNegocioError, ValidacionError
from backend.logica.estimador_espera import EstimadorEspera
from backend.logica.motor_recomendacion import MotorRecomendacion
from backend.logica.optimizador_combos import OptimizadorCombos

LONGITUD_MAXIMA_TEXTO = 80
FORMATO_HORA = re.compile(r"([01][0-9]|2[0-3]):[0-5][0-9]")


class CampusFoodHub:
    """Fachada que ejecuta las operaciones de los requisitos."""

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
        """RF1: platos con inventario de restaurantes abiertos."""
        return [
            p for p in self._platos
            if p.tiene_stock() and p.get_restaurante().esta_abierto()
        ]

    def filtrar_menu(self, texto_busqueda=None, precio_maximo=None,
                     tiempo_maximo=None, solo_saludable=False, solo_excedente=False):
        """RF2: aplica con Y lógico solo los criterios informados (RF2.1 a RF2.5)."""
        texto = None
        if texto_busqueda is not None:
            if not isinstance(texto_busqueda, str):
                raise ValidacionError("El texto de búsqueda debe ser una cadena.")
            texto = texto_busqueda.strip().lower()
            if len(texto) > LONGITUD_MAXIMA_TEXTO:
                raise ValidacionError("El texto de búsqueda no puede superar 80 caracteres.")
        for nombre, valor in (("precio máximo", precio_maximo), ("tiempo máximo", tiempo_maximo)):
            if valor is not None and (isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0):
                raise ValidacionError(f"El {nombre} debe ser un número entero positivo.")

        resultado = self.obtener_menu_disponible()
        if texto:
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
        """RF4: lista ordenada de tuplas (plato, matchScore, razón)."""
        return self._motor_recomendacion.recomendar(
            self.obtener_menu_disponible(), estudiante, cantidad
        )

    def obtener_ofertas(self):
        """RF5: platos disponibles con descuento, de mayor a menor descuento."""
        ofertas = [p for p in self.obtener_menu_disponible() if p.es_excedente()]
        ofertas.sort(key=lambda p: p.get_descuento_excedente(), reverse=True)
        return ofertas

    def obtener_resumen_campus(self):
        """RF6: platos activos, restaurantes abiertos, ofertas vigentes y plato más rápido."""
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

    def crear_preorden(self, estudiante, items, nombre_cliente, hora_recogida, notas=""):
        """RF7: valida toda la preorden y solo entonces modifica el mundo del problema.

        items es una lista de tuplas (id_plato, cantidad). Se registra un único pedido
        en el historial del restaurante y en el del estudiante.
        """
        if not items:
            raise ValidacionError("La preorden debe incluir al menos un plato.")
        if not isinstance(nombre_cliente, str) or not nombre_cliente.strip():
            raise ValidacionError("El nombre del cliente es obligatorio.")
        if not isinstance(hora_recogida, str) or not FORMATO_HORA.fullmatch(hora_recogida):
            raise ValidacionError("La hora de recogida debe tener el formato HH:MM (00:00 a 23:59).")
        for item in items:
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                raise ValidacionError("Cada ítem debe indicar el plato y la cantidad.")
            id_plato, cantidad = item
            if isinstance(id_plato, bool) or not isinstance(id_plato, int):
                raise ValidacionError("El identificador del plato debe ser un número entero.")
            if isinstance(cantidad, bool) or not isinstance(cantidad, int) or not 1 <= cantidad <= 5:
                raise ValidacionError("La cantidad por plato debe ser un entero entre 1 y 5.")

        platos_por_id = {p.get_id(): p for p in self._platos}
        cantidad_por_plato = {}
        for id_plato, cantidad in items:
            plato = platos_por_id.get(id_plato)
            if plato is None:
                raise EntidadNoEncontradaError(f"No existe un plato con id {id_plato}.")
            cantidad_por_plato[plato] = cantidad_por_plato.get(plato, 0) + cantidad

        for plato, cantidad_total in cantidad_por_plato.items():
            if cantidad_total > 5:
                raise ValidacionError(
                    f"La cantidad total de '{plato.get_nombre()}' debe estar entre 1 y 5."
                )
        for plato in cantidad_por_plato:
            if not plato.get_restaurante().esta_abierto():
                raise ReglaNegocioError(
                    f"El restaurante '{plato.get_restaurante().get_nombre()}' está cerrado."
                )
        if len({plato.get_restaurante() for plato in cantidad_por_plato}) > 1:
            raise ReglaNegocioError("Todos los platos de una preorden deben ser del mismo restaurante.")
        for plato, cantidad_total in cantidad_por_plato.items():
            if cantidad_total > plato.get_inventario():
                raise ReglaNegocioError(f"Inventario insuficiente para '{plato.get_nombre()}'.")

        pedido = Pedido(estudiante, nombre_cliente.strip(), hora_recogida, notas)
        for plato, cantidad_total in cantidad_por_plato.items():
            pedido.agregar_item(plato, cantidad_total)
            plato.reducir_inventario(cantidad_total)
        pedido.get_restaurante().registrar_pedido()
        estudiante.registrar_pedido(pedido)
        for plato in cantidad_por_plato:
            estudiante.actualizar_perfil_segun_eleccion(plato)
        self._pedidos.append(pedido)
        return pedido

    def obtener_estado_restaurantes(self):
        """RF9: congestión y tiempo estimado promedio de cada restaurante abierto."""
        resultado = []
        for restaurante in self._restaurantes:
            if not restaurante.esta_abierto():
                continue
            platos_restaurante = [p for p in self._platos if p.get_restaurante() is restaurante]
            tiempo_prom = (
                round(sum(self._estimador_espera.tiempo_estimado(p) for p in platos_restaurante)
                      / len(platos_restaurante), 1)
                if platos_restaurante else 0
            )
            resultado.append({
                "restaurante": restaurante,
                "congestion": self._estimador_espera.estado_congestion(restaurante),
                "tiempo_estimado_min": tiempo_prom,
            })
        return resultado

    def obtener_combo_optimo(self, presupuesto):
        """RF10: tupla (platos, gasto total, ahorro); combo vacío si no hay solución."""
        return self._optimizador_combos.optimizar(self.obtener_menu_disponible(), presupuesto)
