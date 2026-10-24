"""Pruebas de los requisitos funcionales RF1 a RF10 sobre la lógica y el dominio."""

import unittest

from backend.datos import sembrar_datos
from backend.dominio import Estudiante, Pedido
from backend.excepciones import EntidadNoEncontradaError, ReglaNegocioError, ValidacionError
from backend.logica import CampusFoodHub, MotorRecomendacion
from tests.escenario import capturar_estado, crear_escenario


def ids(platos):
    return [p.get_id() for p in platos]


class PruebaRF1MenuDisponible(unittest.TestCase):

    def setUp(self):
        self.e = crear_escenario()

    def test_solo_platos_con_inventario_de_restaurantes_abiertos(self):
        self.assertEqual(ids(self.e.hub.obtener_menu_disponible()), [1, 2, 3, 4, 5, 6])

    def test_cerrar_restaurante_retira_sus_platos(self):
        self.e.r1.set_abierto(False)
        self.assertEqual(ids(self.e.hub.obtener_menu_disponible()), [2, 4, 6])

    def test_menu_vacio(self):
        self.assertEqual(CampusFoodHub().obtener_menu_disponible(), [])


class PruebaRF2FiltrarMenu(unittest.TestCase):

    def setUp(self):
        self.hub = crear_escenario().hub

    def test_sin_criterios_devuelve_menu_completo(self):
        self.assertEqual(ids(self.hub.filtrar_menu()), ids(self.hub.obtener_menu_disponible()))

    def test_texto_vacio_o_solo_espacios_no_es_criterio(self):
        self.assertEqual(ids(self.hub.filtrar_menu(texto_busqueda="   ")), [1, 2, 3, 4, 5, 6])
        self.assertEqual(ids(self.hub.filtrar_menu(texto_busqueda="")), [1, 2, 3, 4, 5, 6])

    def test_rf2_1_texto_sin_distinguir_mayusculas_en_nombre_restaurante_y_categoria(self):
        self.assertEqual(ids(self.hub.filtrar_menu(texto_busqueda="WRAP")), [3])
        self.assertEqual(ids(self.hub.filtrar_menu(texto_busqueda="green bowl")), [2, 4, 6])
        self.assertEqual(ids(self.hub.filtrar_menu(texto_busqueda="Colombiana")), [1, 3, 5])

    def test_rf2_1_texto_de_80_caracteres_es_valido(self):
        self.assertEqual(self.hub.filtrar_menu(texto_busqueda="x" * 80), [])

    def test_rf2_1_texto_de_81_caracteres_es_invalido(self):
        with self.assertRaises(ValidacionError):
            self.hub.filtrar_menu(texto_busqueda="x" * 81)

    def test_rf2_2_precio_maximo_sobre_precio_final(self):
        self.assertEqual(ids(self.hub.filtrar_menu(precio_maximo=9000)), [3, 5, 6])

    def test_rf2_2_precio_cero_negativo_booleano_o_texto_es_invalido(self):
        for valor in (0, -100, True, "9000", 9000.5):
            with self.subTest(valor=valor), self.assertRaises(ValidacionError):
                self.hub.filtrar_menu(precio_maximo=valor)

    def test_rf2_3_tiempo_maximo(self):
        self.assertEqual(ids(self.hub.filtrar_menu(tiempo_maximo=8)), [2, 6])

    def test_rf2_3_tiempo_cero_negativo_o_booleano_es_invalido(self):
        for valor in (0, -5, False, "abc"):
            with self.subTest(valor=valor), self.assertRaises(ValidacionError):
                self.hub.filtrar_menu(tiempo_maximo=valor)

    def test_rf2_4_solo_saludables(self):
        self.assertEqual(ids(self.hub.filtrar_menu(solo_saludable=True)), [2, 3, 4, 6])

    def test_rf2_5_solo_ofertas_de_excedente(self):
        self.assertEqual(ids(self.hub.filtrar_menu(solo_excedente=True)), [3, 5, 6])

    def test_criterios_combinados_con_y_logico(self):
        resultado = self.hub.filtrar_menu(texto_busqueda="pollo", precio_maximo=9000,
                                          tiempo_maximo=12, solo_saludable=True, solo_excedente=True)
        self.assertEqual(ids(resultado), [3])

    def test_sin_coincidencias_devuelve_lista_vacia(self):
        self.assertEqual(self.hub.filtrar_menu(texto_busqueda="sushi"), [])

    def test_casillas_desmarcadas_no_filtran(self):
        completo = [1, 2, 3, 4, 5, 6]
        self.assertEqual(ids(self.hub.filtrar_menu(solo_saludable=False, solo_excedente=False)), completo)
        self.assertEqual(ids(self.hub.filtrar_menu(solo_saludable=None, solo_excedente=None)), completo)


class PruebaRF3SeleccionarPerfil(unittest.TestCase):

    def setUp(self):
        self.estudiante = Estudiante(1, "Simón Valencia", 15000)

    def test_aplicar_perfil_asigna_presupuesto_enfoques_cocina_y_perfil(self):
        self.estudiante.aplicar_perfil("vegetariano")
        self.assertEqual(self.estudiante.get_presupuesto(), 22000)
        self.assertEqual(self.estudiante.get_enfoque_salud(), 0.9)
        self.assertEqual(self.estudiante.get_enfoque_velocidad(), 0.5)
        self.assertEqual(self.estudiante.get_cocina_preferida(), "vegetariana")
        self.assertEqual(self.estudiante.get_perfil_activo(), "vegetariano")

    def test_perfil_sin_cocina_conserva_la_cocina_anterior(self):
        self.estudiante.aplicar_perfil("vegetariano")
        self.estudiante.aplicar_perfil("fit_rapido")
        self.assertEqual(self.estudiante.get_cocina_preferida(), "vegetariana")
        self.assertEqual(self.estudiante.get_perfil_activo(), "fit_rapido")

    def test_perfil_repetido_no_es_error(self):
        self.estudiante.aplicar_perfil("balance")
        self.estudiante.aplicar_perfil("balance")
        self.assertEqual(self.estudiante.get_perfil_activo(), "balance")

    def test_slug_sin_distinguir_mayusculas_ni_espacios(self):
        self.estudiante.aplicar_perfil("  Ahorro_Total ")
        self.assertEqual(self.estudiante.get_perfil_activo(), "ahorro_total")

    def test_existen_los_cinco_perfiles(self):
        self.assertEqual(set(Estudiante.PERFILES_PREDEFINIDOS),
                         {"balance", "fit_rapido", "ahorro_total", "antojo_del_dia", "vegetariano"})

    def test_slug_inexistente(self):
        with self.assertRaises(EntidadNoEncontradaError):
            self.estudiante.aplicar_perfil("keto")
        self.assertIsNone(self.estudiante.get_perfil_activo())


class PruebaRF4Recomendaciones(unittest.TestCase):

    def setUp(self):
        self.e = crear_escenario()

    def test_hasta_cuatro_tuplas_ordenadas_de_mayor_a_menor(self):
        self.e.estudiante.aplicar_perfil("fit_rapido")
        recomendaciones = self.e.hub.obtener_recomendaciones(self.e.estudiante)
        self.assertEqual(len(recomendaciones), 4)
        puntajes = [puntaje for _, puntaje, _ in recomendaciones]
        self.assertEqual(puntajes, sorted(puntajes, reverse=True))
        motor = MotorRecomendacion()
        for plato, puntaje, razon in recomendaciones:
            self.assertIn(plato, self.e.hub.obtener_menu_disponible())
            self.assertEqual(puntaje, motor.calcular_puntaje(plato, self.e.estudiante))
            self.assertEqual(razon, motor.generar_razon(plato, self.e.estudiante))

    def test_el_perfil_cambia_las_recomendaciones(self):
        self.e.estudiante.aplicar_perfil("fit_rapido")
        fit = [p.get_id() for p, _, _ in self.e.hub.obtener_recomendaciones(self.e.estudiante)]
        self.e.estudiante.aplicar_perfil("antojo_del_dia")
        antojo = [p.get_id() for p, _, _ in self.e.hub.obtener_recomendaciones(self.e.estudiante)]
        self.assertNotEqual(fit, antojo)

    def test_cantidad_personalizada(self):
        self.assertEqual(len(self.e.hub.obtener_recomendaciones(self.e.estudiante, cantidad=2)), 2)

    def test_menu_vacio_devuelve_lista_vacia(self):
        self.assertEqual(CampusFoodHub().obtener_recomendaciones(self.e.estudiante), [])


class PruebaRF5Ofertas(unittest.TestCase):

    def test_ofertas_disponibles_de_mayor_a_menor_descuento(self):
        hub = crear_escenario().hub
        self.assertEqual(ids(hub.obtener_ofertas()), [5, 3, 6])

    def test_sin_ofertas(self):
        self.assertEqual(CampusFoodHub().obtener_ofertas(), [])


class PruebaRF6Resumen(unittest.TestCase):

    def test_cuatro_estadisticas(self):
        e = crear_escenario()
        resumen = e.hub.obtener_resumen_campus()
        self.assertEqual(resumen["platos_activos"], 6)
        self.assertEqual(resumen["restaurantes_abiertos"], 2)
        self.assertEqual(resumen["ofertas_vigentes"], 3)
        self.assertIs(resumen["plato_mas_rapido"], e.platos[6])

    def test_sin_platos_ceros_y_sin_plato_mas_rapido(self):
        resumen = CampusFoodHub().obtener_resumen_campus()
        self.assertEqual(resumen, {"platos_activos": 0, "restaurantes_abiertos": 0,
                                   "ofertas_vigentes": 0, "plato_mas_rapido": None})


class PruebaRF7CrearPreorden(unittest.TestCase):

    def setUp(self):
        self.e = crear_escenario()

    def crear(self, items, nombre="Ana Pérez", hora="12:30", notas=""):
        return self.e.hub.crear_preorden(self.e.estudiante, items, nombre, hora, notas)

    def test_preorden_valida(self):
        pedido = self.crear([(2, 2), (6, 1)], nombre="  Ana Pérez  ", notas="Sin cebolla")
        self.assertIsInstance(pedido, Pedido)
        self.assertEqual(pedido.get_nombre_cliente(), "Ana Pérez")
        self.assertIs(pedido.get_estudiante(), self.e.estudiante)
        self.assertEqual(pedido.get_hora_recogida(), "12:30")
        self.assertEqual(pedido.get_notas(), "Sin cebolla")
        self.assertEqual(pedido.get_estado(), "confirmado")
        self.assertEqual(pedido.total(), 2 * 14000 + 4800)
        self.assertEqual(self.e.platos[2].get_inventario(), 3)
        self.assertEqual(self.e.platos[6].get_inventario(), 7)

    def test_n_items_registran_un_unico_pedido_en_restaurante_y_estudiante(self):
        self.crear([(2, 1), (4, 2), (6, 3), (2, 1)])
        self.assertEqual(self.e.r2.pedidos_ultima_hora(), 1)
        self.assertEqual(len(self.e.estudiante.get_historial()), 1)
        self.crear([(6, 1)])
        self.assertEqual(self.e.r2.pedidos_ultima_hora(), 2)
        self.assertEqual(len(self.e.estudiante.get_historial()), 2)

    def test_cantidad_acumulada_del_mismo_plato_forma_una_linea(self):
        pedido = self.crear([(2, 2), (2, 3)])
        self.assertEqual([(i.get_plato().get_id(), i.get_cantidad()) for i in pedido.get_items()], [(2, 5)])
        self.assertEqual(self.e.platos[2].get_inventario(), 0)

    def test_actualiza_el_perfil_una_vez_por_plato_distinto(self):
        referencia = Estudiante(2, "Referencia", 15000)
        referencia.actualizar_perfil_segun_eleccion(self.e.platos[2])
        referencia.actualizar_perfil_segun_eleccion(self.e.platos[6])
        self.crear([(2, 1), (6, 1), (2, 1)])
        self.assertAlmostEqual(self.e.estudiante.get_enfoque_salud(), referencia.get_enfoque_salud())
        self.assertAlmostEqual(self.e.estudiante.get_enfoque_velocidad(), referencia.get_enfoque_velocidad())

    def test_cantidad_cinco_e_inventario_justo(self):
        self.crear([(2, 5)])
        self.crear([(3, 2)])
        self.assertEqual(self.e.platos[2].get_inventario(), 0)
        self.assertEqual(self.e.platos[3].get_inventario(), 0)
        self.assertNotIn(self.e.platos[3], self.e.hub.obtener_menu_disponible())

    def assert_falla_sin_cambios(self, excepcion, **kwargs):
        antes = capturar_estado(self.e)
        with self.assertRaises(excepcion):
            self.crear(**kwargs)
        self.assertEqual(capturar_estado(self.e), antes)
        self.assertEqual(self.e.hub._pedidos, [])

    def test_validacion_items_vacios(self):
        self.assert_falla_sin_cambios(ValidacionError, items=[])

    def test_validacion_nombre_vacio(self):
        for nombre in ("", "   ", None):
            with self.subTest(nombre=nombre):
                self.assert_falla_sin_cambios(ValidacionError, items=[(2, 1)], nombre=nombre)

    def test_validacion_hora(self):
        for hora in ("24:00", "9:5", "", "12:60", "9:30", "12:30 ", None):
            with self.subTest(hora=hora):
                self.assert_falla_sin_cambios(ValidacionError, items=[(2, 1)], hora=hora)

    def test_horas_limite_validas(self):
        self.crear([(2, 1)], hora="00:00")
        self.crear([(2, 1)], hora="23:59")

    def test_validacion_cantidad_fuera_de_rango_o_no_entera(self):
        for cantidad in (0, 6, -1, True, "2", 2.0):
            with self.subTest(cantidad=cantidad):
                self.assert_falla_sin_cambios(ValidacionError, items=[(2, cantidad)])

    def test_validacion_id_no_entero(self):
        for id_plato in (True, "2", None):
            with self.subTest(id_plato=id_plato):
                self.assert_falla_sin_cambios(ValidacionError, items=[(id_plato, 1)])

    def test_validacion_cantidad_acumulada_mayor_a_cinco(self):
        self.assert_falla_sin_cambios(ValidacionError, items=[(2, 3), (2, 3)])

    def test_plato_inexistente(self):
        self.assert_falla_sin_cambios(EntidadNoEncontradaError, items=[(2, 1), (999, 1)])

    def test_restaurante_cerrado(self):
        self.assert_falla_sin_cambios(ReglaNegocioError, items=[(7, 1)])

    def test_platos_de_dos_restaurantes(self):
        self.assert_falla_sin_cambios(ReglaNegocioError, items=[(1, 1), (2, 1)])

    def test_inventario_insuficiente(self):
        self.assert_falla_sin_cambios(ReglaNegocioError, items=[(3, 3)])
        self.assert_falla_sin_cambios(ReglaNegocioError, items=[(1, 1), (8, 1)])

    def test_orden_de_validacion(self):
        with self.assertRaisesRegex(ValidacionError, "nombre"):
            self.crear([(2, 1)], nombre="", hora="99:99")
        with self.assertRaises(ValidacionError):
            self.crear([(999, 6)])
        with self.assertRaises(EntidadNoEncontradaError):
            self.crear([(999, 1), (7, 1)])


class PruebaRF8Comprobante(unittest.TestCase):

    def setUp(self):
        self.e = crear_escenario()

    def test_comprobante_completo_con_nombre_del_cliente(self):
        pedido = self.e.hub.crear_preorden(self.e.estudiante, [(3, 1), (5, 2)],
                                           "Ana Pérez", "13:15", "Para llevar")
        self.assertIs(pedido.get_restaurante(), self.e.r1)
        self.assertEqual(pedido.generar_comprobante(), {
            "numero_pedido": pedido.get_id(),
            "cliente": "Ana Pérez",
            "restaurante": "Sazón Criollo",
            "hora_recogida": "13:15",
            "lineas": [
                {"plato": "Wrap de pollo", "cantidad": 1, "subtotal": 8400},
                {"plato": "Arroz con pollo", "cantidad": 2, "subtotal": 18000},
            ],
            "notas": "Para llevar",
            "total": 26400,
        })

    def test_pedido_sin_items(self):
        pedido = Pedido(self.e.estudiante, "Ana Pérez", "12:00")
        with self.assertRaises(ReglaNegocioError):
            pedido.generar_comprobante()
        with self.assertRaises(ReglaNegocioError):
            pedido.get_restaurante()

    def test_agregar_item_no_tiene_efectos_secundarios(self):
        pedido = Pedido(self.e.estudiante, "Ana Pérez", "12:00")
        pedido.agregar_item(self.e.platos[2], 2)
        self.assertEqual(self.e.platos[2].get_inventario(), 5)
        self.assertEqual(self.e.r2.pedidos_ultima_hora(), 0)
        self.assertEqual(self.e.estudiante.get_historial(), [])


class PruebaRF9Congestion(unittest.TestCase):

    def setUp(self):
        self.e = crear_escenario()

    def estado(self, restaurante):
        return next(d for d in self.e.hub.obtener_estado_restaurantes() if d["restaurante"] is restaurante)

    def test_solo_restaurantes_abiertos_con_congestion_baja_inicial(self):
        estados = self.e.hub.obtener_estado_restaurantes()
        self.assertEqual([d["restaurante"] for d in estados], [self.e.r1, self.e.r2])
        self.assertEqual(self.estado(self.e.r2)["congestion"], "bajo")
        self.assertEqual(self.estado(self.e.r2)["tiempo_estimado_min"], round((8 + 12 + 5) / 3, 1))

    def test_niveles_segun_pedidos_de_la_ultima_hora(self):
        self.e.r2.registrar_pedido()
        self.assertEqual(self.estado(self.e.r2)["congestion"], "bajo")
        self.e.r2.registrar_pedido()
        self.assertEqual(self.estado(self.e.r2)["congestion"], "medio")
        for _ in range(6):
            self.e.r2.registrar_pedido()
        self.assertEqual(self.estado(self.e.r2)["congestion"], "alto")
        self.assertEqual(self.estado(self.e.r2)["tiempo_estimado_min"], round((16 + 24 + 10) / 3, 1))

    def test_una_preorden_de_varios_items_suma_un_solo_pedido(self):
        self.e.hub.crear_preorden(self.e.estudiante, [(2, 1), (4, 1), (6, 1)], "Ana", "12:00")
        self.assertEqual(self.e.r2.pedidos_ultima_hora(), 1)
        self.assertEqual(self.estado(self.e.r2)["congestion"], "bajo")

    def test_sin_restaurantes_abiertos(self):
        self.e.r1.set_abierto(False)
        self.e.r2.set_abierto(False)
        self.assertEqual(self.e.hub.obtener_estado_restaurantes(), [])


class PruebaRF10ComboOptimo(unittest.TestCase):

    def setUp(self):
        self.e = crear_escenario()

    def test_combo_de_mayor_ahorro_dentro_del_presupuesto(self):
        platos, gasto, ahorro = self.e.hub.obtener_combo_optimo(15000)
        self.assertEqual(ids(platos), [5, 6])
        self.assertEqual(gasto, 9000 + 4800)
        self.assertEqual(ahorro, 6000 + 1200)

    def test_presupuesto_amplio_toma_todas_las_ofertas(self):
        platos, gasto, ahorro = self.e.hub.obtener_combo_optimo(100000)
        self.assertEqual(ids(platos), [3, 5, 6])
        self.assertEqual((gasto, ahorro), (8400 + 9000 + 4800, 3600 + 6000 + 1200))

    def test_combo_sin_solucion(self):
        self.assertEqual(self.e.hub.obtener_combo_optimo(1000), ([], 0, 0))

    def test_presupuesto_cero(self):
        self.assertEqual(self.e.hub.obtener_combo_optimo(0), ([], 0, 0))

    def test_sin_ofertas(self):
        self.assertEqual(CampusFoodHub().obtener_combo_optimo(50000), ([], 0, 0))


class PruebaDatosIniciales(unittest.TestCase):

    def test_catalogo_inicial(self):
        hub = CampusFoodHub()
        sembrar_datos(hub)
        menu = hub.obtener_menu_disponible()
        self.assertEqual(len(menu), 12)
        self.assertEqual(hub.obtener_resumen_campus()["restaurantes_abiertos"], 4)
        self.assertIn("vegetariana", {p.get_categoria() for p in menu})
        self.assertGreaterEqual(len(hub.obtener_ofertas()), 3)
        self.assertGreaterEqual(len(hub.obtener_combo_optimo(20000)[0]), 2)


if __name__ == "__main__":
    unittest.main()
