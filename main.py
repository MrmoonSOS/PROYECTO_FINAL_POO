"""Punto de entrada de CampusFoodHub Inteligente.

Arma la fachada, siembra los datos iniciales, crea el estudiante de la sesión y lanza
el servidor HTTP que atiende la API y los archivos estáticos de la interfaz.
"""

import os
from functools import partial
from http.server import HTTPServer

from backend.controlador import ManejadorHTTP
from backend.datos import sembrar_datos
from backend.dominio import Estudiante
from backend.logica import CampusFoodHub

HOST = "127.0.0.1"
PUERTO = 8000
DIRECTORIO_ESTATICO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
PRESUPUESTO_POR_DEFECTO = 15000


def main():
    hub = CampusFoodHub()
    sembrar_datos(hub)
    estudiante = Estudiante(1, "Simón Valencia", PRESUPUESTO_POR_DEFECTO)
    hub.agregar_estudiante(estudiante)

    ManejadorHTTP.hub = hub
    ManejadorHTTP.estudiante = estudiante

    servidor = HTTPServer((HOST, PUERTO), partial(ManejadorHTTP, directory=DIRECTORIO_ESTATICO))
    print(f"CampusFoodHub Inteligente disponible en http://{HOST}:{PUERTO}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
