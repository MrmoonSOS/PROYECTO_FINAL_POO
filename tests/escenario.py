"""Escenario controlado y reutilizable para las pruebas del backend."""

from types import SimpleNamespace

from backend.dominio import Estudiante, Plato, Restaurante
from backend.logica import CampusFoodHub


def crear_escenario():
    """Hub con dos restaurantes abiertos, uno cerrado, un plato agotado y un estudiante."""
    hub = CampusFoodHub()
    r1 = Restaurante(1, "Sazón Criollo", "colombiana", 4.5, "Bloque 12")
    r2 = Restaurante(2, "Green Bowl", "vegetariana", 4.7, "Bloque 20")
    r3 = Restaurante(3, "Parrilla Norte", "parrilla", 4.0, "Bloque 1", abierto=False)
    for restaurante in (r1, r2, r3):
        hub.agregar_restaurante(restaurante)

    platos = {
        1: Plato(1, "Bandeja paisa", r1, 18000, "colombiana", 950, 20, False, 10, 0),
        2: Plato(2, "Ensalada César", r2, 14000, "vegetariana", 350, 8, True, 5, 0),
        3: Plato(3, "Wrap de pollo", r1, 12000, "colombiana", 500, 10, True, 2, 30),
        4: Plato(4, "Bowl de quinua", r2, 16000, "vegetariana", 420, 12, True, 6, 0),
        5: Plato(5, "Arroz con pollo", r1, 15000, "colombiana", 600, 15, False, 4, 40),
        6: Plato(6, "Jugo natural", r2, 6000, "vegetariana", 120, 5, True, 8, 20),
        7: Plato(7, "Churrasco", r3, 25000, "parrilla", 800, 25, False, 5, 10),
        8: Plato(8, "Empanadas", r1, 10000, "colombiana", 400, 7, False, 0, 50),
    }
    for plato in platos.values():
        hub.agregar_plato(plato)

    estudiante = Estudiante(1, "Simón Valencia", 15000)
    hub.agregar_estudiante(estudiante)
    return SimpleNamespace(hub=hub, r1=r1, r2=r2, r3=r3, platos=platos, estudiante=estudiante)


def capturar_estado(escenario):
    """Fotografía del estado modificable para comprobar que una preorden fallida no cambia nada."""
    estudiante = escenario.estudiante
    return {
        "inventarios": {i: p.get_inventario() for i, p in escenario.platos.items()},
        "pedidos_restaurantes": [r.pedidos_ultima_hora() for r in (escenario.r1, escenario.r2, escenario.r3)],
        "historial_estudiante": len(estudiante.get_historial()),
        "perfil": (
            estudiante.get_presupuesto(), estudiante.get_enfoque_salud(),
            estudiante.get_enfoque_velocidad(), estudiante.get_cocina_preferida(),
            estudiante.get_perfil_activo(),
        ),
    }
