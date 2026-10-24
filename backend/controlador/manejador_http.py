"""ManejadorHTTP: traduce las solicitudes HTTP de la interfaz en llamadas al backend (RF1 a RF10).

Convierte los parámetros de texto a tipos básicos, delega en CampusFoodHub o en el
estudiante de la sesión y responde en JSON. Las rutas que no empiezan por /api/ se sirven
como archivos estáticos desde el directorio configurado al crear el servidor.
"""

import json
from http.server import SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit

from backend.excepciones import (
    CampusFoodHubError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    ValidacionError,
)

MENSAJE_NO_ENCONTRADO = "no se encontró el elemento solicitado"


class ManejadorHTTP(SimpleHTTPRequestHandler):
    """Controlador HTTP; hub y estudiante los asigna main.py al arrancar."""

    hub = None
    estudiante = None

    def do_GET(self):
        url = urlsplit(self.path)
        if not url.path.startswith("/api/"):
            super().do_GET()
            return
        consulta = parse_qs(url.query)
        try:
            if url.path == "/api/menu":
                self.responder_menu(consulta)
            elif url.path == "/api/recomendaciones":
                self.responder_recomendaciones()
            elif url.path == "/api/ofertas":
                self.responder_ofertas()
            elif url.path == "/api/resumen":
                self.responder_resumen()
            elif url.path == "/api/congestion":
                self.responder_congestion()
            elif url.path == "/api/combo":
                self.responder_combo(consulta)
            else:
                raise EntidadNoEncontradaError(f"Ruta inexistente: {url.path}")
        except CampusFoodHubError as error:
            self.enviar_error(error)

    def do_POST(self):
        ruta = urlsplit(self.path).path
        try:
            if ruta not in ("/api/perfil", "/api/preorden"):
                raise EntidadNoEncontradaError(f"Ruta inexistente: {ruta}")
            try:
                longitud = int(self.headers.get("Content-Length", "0"))
                cuerpo = json.loads(self.rfile.read(max(longitud, 0)).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                raise ValidacionError("El cuerpo de la solicitud no es un JSON válido.") from None
            if not isinstance(cuerpo, dict):
                raise ValidacionError("El cuerpo de la solicitud debe ser un objeto JSON.")
            if ruta == "/api/perfil":
                self.responder_perfil(cuerpo)
            else:
                self.responder_preorden(cuerpo)
        except CampusFoodHubError as error:
            self.enviar_error(error)

    def responder_menu(self, consulta):
        """RF1 y RF2: menú filtrado; sin parámetros devuelve el menú disponible completo."""
        def valor(nombre):
            valores = consulta.get(nombre)
            return valores[0] if valores else None

        def a_entero(texto):
            if texto is None:
                return None
            try:
                return int(texto)
            except ValueError:
                return texto

        def a_booleano(texto):
            if texto is None or texto.lower() == "false":
                return False
            if texto.lower() == "true":
                return True
            return texto

        platos = self.hub.filtrar_menu(
            texto_busqueda=valor("texto"),
            precio_maximo=a_entero(valor("precio_maximo")),
            tiempo_maximo=a_entero(valor("tiempo_maximo")),
            solo_saludable=a_booleano(valor("solo_saludable")),
            solo_excedente=a_booleano(valor("solo_excedente")),
        )
        self.enviar_json(200, [self.serializar_plato(p) for p in platos])

    def responder_perfil(self, cuerpo):
        """RF3: aplica el perfil elegido al estudiante de la sesión."""
        slug = cuerpo.get("slug")
        if not isinstance(slug, str):
            raise ValidacionError("Debe indicar el slug del perfil.")
        self.estudiante.aplicar_perfil(slug)
        self.enviar_json(200, {
            "nombre": self.estudiante.get_nombre(),
            "perfil_activo": self.estudiante.get_perfil_activo(),
            "presupuesto": self.estudiante.get_presupuesto(),
            "enfoque_salud": self.estudiante.get_enfoque_salud(),
            "enfoque_velocidad": self.estudiante.get_enfoque_velocidad(),
            "cocina_preferida": self.estudiante.get_cocina_preferida(),
        })

    def responder_recomendaciones(self):
        """RF4: recomendaciones para el estudiante de la sesión."""
        recomendaciones = self.hub.obtener_recomendaciones(self.estudiante)
        self.enviar_json(200, [
            {"plato": self.serializar_plato(plato), "matchScore": puntaje, "razon": razon}
            for plato, puntaje, razon in recomendaciones
        ])

    def responder_ofertas(self):
        """RF5: ofertas de excedente activas."""
        self.enviar_json(200, [self.serializar_plato(p) for p in self.hub.obtener_ofertas()])

    def responder_resumen(self):
        """RF6: resumen general del campus."""
        resumen = self.hub.obtener_resumen_campus()
        plato_mas_rapido = resumen["plato_mas_rapido"]
        self.enviar_json(200, {
            "platos_activos": resumen["platos_activos"],
            "restaurantes_abiertos": resumen["restaurantes_abiertos"],
            "ofertas_vigentes": resumen["ofertas_vigentes"],
            "plato_mas_rapido": self.serializar_plato(plato_mas_rapido) if plato_mas_rapido else None,
        })

    def responder_preorden(self, cuerpo):
        """RF7 y RF8: crea la preorden y responde 201 con su comprobante."""
        items = cuerpo.get("items")
        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            raise ValidacionError("Los ítems deben ser una lista de objetos con id_plato y cantidad.")
        notas = cuerpo.get("notas", "")
        if not isinstance(notas, str):
            raise ValidacionError("Las notas deben ser texto.")
        pedido = self.hub.crear_preorden(
            self.estudiante,
            [(item.get("id_plato"), item.get("cantidad")) for item in items],
            cuerpo.get("nombre_cliente"),
            cuerpo.get("hora_recogida"),
            notas,
        )
        self.enviar_json(201, pedido.generar_comprobante())

    def responder_congestion(self):
        """RF9: congestión y tiempo estimado de los restaurantes abiertos."""
        self.enviar_json(200, [
            {
                "restaurante": estado["restaurante"].get_nombre(),
                "congestion": estado["congestion"],
                "tiempo_estimado_min": estado["tiempo_estimado_min"],
            }
            for estado in self.hub.obtener_estado_restaurantes()
        ])

    def responder_combo(self, consulta):
        """RF10: combo óptimo de ofertas para el presupuesto indicado."""
        valores = consulta.get("presupuesto")
        try:
            presupuesto = int(valores[0]) if valores else 0
        except ValueError:
            presupuesto = 0
        if presupuesto <= 0:
            raise ValidacionError("El presupuesto debe ser un número entero positivo.")
        platos, gasto_total, ahorro = self.hub.obtener_combo_optimo(presupuesto)
        self.enviar_json(200, {
            "platos": [self.serializar_plato(p) for p in platos],
            "gasto_total": gasto_total,
            "ahorro": ahorro,
        })

    def serializar_plato(self, plato):
        return {
            "id": plato.get_id(),
            "nombre": plato.get_nombre(),
            "restaurante": plato.get_restaurante().get_nombre(),
            "categoria": plato.get_categoria(),
            "precio": plato.get_precio(),
            "precio_final": plato.precio_final(),
            "descuento_excedente": plato.get_descuento_excedente(),
            "calorias": plato.get_calorias(),
            "tiempo_preparacion": plato.get_tiempo_preparacion(),
            "saludable": plato.es_saludable(),
            "inventario": plato.get_inventario(),
            "es_excedente": plato.es_excedente(),
        }

    def enviar_json(self, codigo, datos):
        contenido = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)

    def enviar_error(self, error):
        """Traduce una CampusFoodHubError a 400, 404 o 409 con un mensaje sin detalles técnicos."""
        if isinstance(error, EntidadNoEncontradaError):
            self.enviar_json(404, {"error": MENSAJE_NO_ENCONTRADO})
        elif isinstance(error, ReglaNegocioError):
            self.enviar_json(409, {"error": str(error)})
        else:
            self.enviar_json(400, {"error": str(error)})
