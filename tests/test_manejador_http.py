"""Pruebas de extremo a extremo de ManejadorHTTP sobre un servidor real en un puerto libre."""

import json
import os
import tempfile
import threading
import unittest
from functools import partial
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.controlador import ManejadorHTTP
from backend.datos import sembrar_datos
from backend.dominio import Estudiante
from backend.logica import CampusFoodHub

CAMPOS_PLATO = {
    "id", "nombre", "restaurante", "categoria", "precio", "precio_final", "descuento_excedente",
    "calorias", "tiempo_preparacion", "saludable", "inventario", "es_excedente",
}


class ManejadorSilencioso(ManejadorHTTP):
    """Variante de prueba que no escribe el registro de accesos en la consola."""

    def log_message(self, formato, *args):
        pass


class PruebaManejadorHTTP(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.directorio = tempfile.TemporaryDirectory()
        inexistente = os.path.join(cls.directorio.name, "frontend")
        cls.servidor = HTTPServer(("127.0.0.1", 0), partial(ManejadorSilencioso, directory=inexistente))
        cls.base = f"http://127.0.0.1:{cls.servidor.server_address[1]}"
        cls.hilo = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.hilo.start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.directorio.cleanup()

    def setUp(self):
        hub = CampusFoodHub()
        sembrar_datos(hub)
        self.estudiante = Estudiante(1, "Simón Valencia", 15000)
        hub.agregar_estudiante(self.estudiante)
        ManejadorHTTP.hub = hub
        ManejadorHTTP.estudiante = self.estudiante

    def solicitar(self, ruta, cuerpo=None, crudo=None):
        datos = crudo if crudo is not None else (json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None)
        solicitud = Request(self.base + ruta, data=datos, method="POST" if datos is not None else "GET")
        solicitud.add_header("Content-Type", "application/json")
        try:
            with urlopen(solicitud) as respuesta:
                return respuesta.status, json.loads(respuesta.read().decode("utf-8"))
        except HTTPError as error:
            with error:
                contenido = error.read().decode("utf-8")
                tipo = error.headers.get("Content-Type", "")
            return error.code, json.loads(contenido) if tipo.startswith("application/json") else contenido

    def test_menu(self):
        codigo, platos = self.solicitar("/api/menu")
        self.assertEqual(codigo, 200)
        self.assertEqual(len(platos), 12)
        self.assertEqual(set(platos[0]), CAMPOS_PLATO)

    def test_menu_con_filtros(self):
        codigo, platos = self.solicitar("/api/menu?texto=ARROZ&precio_maximo=10000&solo_excedente=true")
        self.assertEqual(codigo, 200)
        self.assertEqual([p["id"] for p in platos], [5, 7])
        codigo, platos = self.solicitar("/api/menu?solo_saludable=true&tiempo_maximo=8")
        self.assertEqual([p["id"] for p in platos], [2, 6, 11])

    def test_menu_criterio_invalido(self):
        for consulta in ("precio_maximo=abc", "precio_maximo=0", "tiempo_maximo=-3",
                         "texto=" + "x" * 81, "solo_saludable=quizas"):
            with self.subTest(consulta=consulta):
                codigo, cuerpo = self.solicitar("/api/menu?" + consulta)
                self.assertEqual(codigo, 400)
                self.assertIn("error", cuerpo)

    def test_perfil(self):
        codigo, cuerpo = self.solicitar("/api/perfil", {"slug": "vegetariano"})
        self.assertEqual(codigo, 200)
        self.assertEqual(cuerpo["perfil_activo"], "vegetariano")
        self.assertEqual(self.estudiante.get_perfil_activo(), "vegetariano")

    def test_perfil_inexistente(self):
        codigo, cuerpo = self.solicitar("/api/perfil", {"slug": "keto"})
        self.assertEqual((codigo, cuerpo), (404, {"error": "no se encontró el elemento solicitado"}))

    def test_perfil_cuerpo_invalido(self):
        for crudo in (b"{no es json", b"[1, 2]", b"", json.dumps({"slug": 5}).encode()):
            with self.subTest(crudo=crudo):
                codigo, cuerpo = self.solicitar("/api/perfil", crudo=crudo)
                self.assertEqual(codigo, 400)
                self.assertIn("error", cuerpo)

    def test_recomendaciones(self):
        codigo, recomendaciones = self.solicitar("/api/recomendaciones")
        self.assertEqual(codigo, 200)
        self.assertEqual(len(recomendaciones), 4)
        self.assertEqual(set(recomendaciones[0]), {"plato", "matchScore", "razon"})

    def test_ofertas(self):
        codigo, ofertas = self.solicitar("/api/ofertas")
        self.assertEqual(codigo, 200)
        descuentos = [p["descuento_excedente"] for p in ofertas]
        self.assertEqual(descuentos, sorted(descuentos, reverse=True))

    def test_resumen(self):
        codigo, resumen = self.solicitar("/api/resumen")
        self.assertEqual(codigo, 200)
        self.assertEqual(resumen["platos_activos"], 12)
        self.assertEqual(resumen["restaurantes_abiertos"], 4)
        self.assertEqual(resumen["plato_mas_rapido"]["id"], 12)

    def test_preorden_y_congestion(self):
        cuerpo = {"items": [{"id_plato": 1, "cantidad": 2}, {"id_plato": 3, "cantidad": 1}],
                  "nombre_cliente": "Ana Pérez", "hora_recogida": "12:30", "notas": "Sin cebolla"}
        codigo, comprobante = self.solicitar("/api/preorden", cuerpo)
        self.assertEqual(codigo, 201)
        self.assertEqual(comprobante["cliente"], "Ana Pérez")
        self.assertEqual(comprobante["total"], 2 * 18000 + 8400)
        self.assertEqual(ManejadorHTTP.hub.obtener_menu_disponible()[0].get_restaurante().pedidos_ultima_hora(), 1)
        codigo, estados = self.solicitar("/api/congestion")
        self.assertEqual(codigo, 200)
        self.assertEqual(len(estados), 4)
        self.assertEqual(set(estados[0]), {"restaurante", "congestion", "tiempo_estimado_min"})

    def test_preorden_errores(self):
        casos = [
            ({"items": [], "nombre_cliente": "Ana", "hora_recogida": "12:00"}, 400),
            ({"items": [{"id_plato": 1, "cantidad": 1}], "nombre_cliente": "Ana", "hora_recogida": "24:00"}, 400),
            ({"items": [{"id_plato": 1, "cantidad": 6}], "nombre_cliente": "Ana", "hora_recogida": "12:00"}, 400),
            ({"items": "1", "nombre_cliente": "Ana", "hora_recogida": "12:00"}, 400),
            ({"items": [{"id_plato": 1, "cantidad": 1}], "nombre_cliente": "Ana", "hora_recogida": "12:00",
              "notas": 3}, 400),
            ({"items": [{"id_plato": 99, "cantidad": 1}], "nombre_cliente": "Ana", "hora_recogida": "12:00"}, 404),
            ({"items": [{"id_plato": 1, "cantidad": 1}, {"id_plato": 2, "cantidad": 1}],
              "nombre_cliente": "Ana", "hora_recogida": "12:00"}, 409),
            ({"items": [{"id_plato": 10, "cantidad": 2}], "nombre_cliente": "Ana", "hora_recogida": "12:00"}, 409),
        ]
        for cuerpo, esperado in casos:
            with self.subTest(cuerpo=cuerpo):
                codigo, respuesta = self.solicitar("/api/preorden", cuerpo)
                self.assertEqual(codigo, esperado)
                self.assertIn("error", respuesta)
        self.assertEqual(self.estudiante.get_historial(), [])

    def test_combo(self):
        codigo, combo = self.solicitar("/api/combo?presupuesto=20000")
        self.assertEqual(codigo, 200)
        self.assertEqual(set(combo), {"platos", "gasto_total", "ahorro"})
        self.assertLessEqual(combo["gasto_total"], 20000)
        self.assertGreater(combo["ahorro"], 0)

    def test_combo_sin_solucion(self):
        self.assertEqual(self.solicitar("/api/combo?presupuesto=100"),
                         (200, {"platos": [], "gasto_total": 0, "ahorro": 0}))

    def test_combo_presupuesto_invalido(self):
        for consulta in ("", "?presupuesto=abc", "?presupuesto=0", "?presupuesto=-5"):
            with self.subTest(consulta=consulta):
                self.assertEqual(self.solicitar("/api/combo" + consulta)[0], 400)

    def test_ruta_api_inexistente(self):
        esperado = (404, {"error": "no se encontró el elemento solicitado"})
        self.assertEqual(self.solicitar("/api/inexistente"), esperado)
        self.assertEqual(self.solicitar("/api/inexistente", {}), esperado)
        self.assertEqual(self.solicitar("/api/menu", {}), esperado)

    def test_estaticos_sin_directorio_frontend(self):
        self.assertEqual(self.solicitar("/")[0], 404)
        self.assertEqual(self.solicitar("/index.html")[0], 404)


if __name__ == "__main__":
    unittest.main()
