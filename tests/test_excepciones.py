"""Pruebas de la jerarquía de excepciones y de cada caso en que se lanzan."""

import unittest

from backend.dominio import Estudiante, Pedido
from backend.excepciones import (
    CampusFoodHubError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    ValidacionError,
)
from tests.escenario import crear_escenario


class PruebaJerarquia(unittest.TestCase):

    def test_subclases_de_campus_food_hub_error(self):
        for excepcion in (ValidacionError, EntidadNoEncontradaError, ReglaNegocioError):
            with self.subTest(excepcion=excepcion.__name__):
                self.assertTrue(issubclass(excepcion, CampusFoodHubError))
        self.assertTrue(issubclass(CampusFoodHubError, Exception))
        self.assertFalse(issubclass(CampusFoodHubError, ValueError))


class PruebaValidacionError(unittest.TestCase):

    def setUp(self):
        self.e = crear_escenario()

    def test_criterio_de_filtro_invalido(self):
        casos = [
            {"texto_busqueda": "a" * 81},
            {"precio_maximo": 0},
            {"precio_maximo": -1},
            {"precio_maximo": True},
            {"tiempo_maximo": 0},
            {"tiempo_maximo": "10"},
        ]
        for criterios in casos:
            with self.subTest(criterios=criterios), self.assertRaises(ValidacionError):
                self.e.hub.filtrar_menu(**criterios)

    def test_entradas_de_preorden_invalidas(self):
        casos = [
            ([], "Ana", "12:00"),
            ([(2, 1)], "", "12:00"),
            ([(2, 1)], "Ana", ""),
            ([(2, 1)], "Ana", "24:00"),
            ([(2, 1)], "Ana", "9:5"),
            ([(2, 0)], "Ana", "12:00"),
            ([(2, 6)], "Ana", "12:00"),
            ([(2, 3), (2, 3)], "Ana", "12:00"),
        ]
        for items, nombre, hora in casos:
            with self.subTest(items=items, nombre=nombre, hora=hora), self.assertRaises(ValidacionError):
                self.e.hub.crear_preorden(self.e.estudiante, items, nombre, hora)

    def test_pedido_agregar_item_fuera_de_rango(self):
        pedido = Pedido(self.e.estudiante, "Ana", "12:00")
        for cantidad in (0, 6, True):
            with self.subTest(cantidad=cantidad), self.assertRaises(ValidacionError):
                pedido.agregar_item(self.e.platos[2], cantidad)
        pedido.agregar_item(self.e.platos[2], 5)
        self.assertEqual(pedido.total(), 5 * 14000)

    def test_presupuesto_negativo(self):
        with self.assertRaises(ValidacionError):
            Estudiante(1, "Ana", 10000).set_presupuesto(-1)


class PruebaEntidadNoEncontradaError(unittest.TestCase):

    def test_perfil_inexistente(self):
        with self.assertRaises(EntidadNoEncontradaError):
            Estudiante(1, "Ana", 10000).aplicar_perfil("inexistente")

    def test_plato_inexistente(self):
        e = crear_escenario()
        with self.assertRaises(EntidadNoEncontradaError):
            e.hub.crear_preorden(e.estudiante, [(999, 1)], "Ana", "12:00")


class PruebaReglaNegocioError(unittest.TestCase):

    def setUp(self):
        self.e = crear_escenario()

    def test_inventario_insuficiente(self):
        with self.assertRaises(ReglaNegocioError):
            self.e.platos[3].reducir_inventario(3)
        self.assertEqual(self.e.platos[3].get_inventario(), 2)
        with self.assertRaises(ReglaNegocioError):
            self.e.hub.crear_preorden(self.e.estudiante, [(3, 3)], "Ana", "12:00")

    def test_platos_de_distintos_restaurantes(self):
        with self.assertRaises(ReglaNegocioError):
            self.e.hub.crear_preorden(self.e.estudiante, [(1, 1), (2, 1)], "Ana", "12:00")

    def test_restaurante_cerrado(self):
        with self.assertRaises(ReglaNegocioError):
            self.e.hub.crear_preorden(self.e.estudiante, [(7, 1)], "Ana", "12:00")

    def test_pedido_sin_items(self):
        with self.assertRaises(ReglaNegocioError):
            Pedido(self.e.estudiante, "Ana", "12:00").generar_comprobante()


if __name__ == "__main__":
    unittest.main()
