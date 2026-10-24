"""Datos quemados en memoria con los que arranca el sistema.

El catálogo cubre todos los requisitos: categorías variadas (incluida la vegetariana del
perfil Vegetariano), platos saludables y no saludables, tiempos diversos, varias ofertas
de excedente para RF5 y RF10, e inventarios pequeños para probar el inventario insuficiente.
"""

from backend.dominio.plato import Plato
from backend.dominio.restaurante import Restaurante


def sembrar_datos(hub):
    """Registra en el hub los restaurantes y platos iniciales."""
    r1 = Restaurante(1, "Sazón Criollo", "colombiana", 4.5, "Bloque 12")
    r2 = Restaurante(2, "Green Bowl", "vegetariana", 4.7, "Bloque 20")
    r3 = Restaurante(3, "Wok Express", "asiática", 4.3, "Bloque 7")
    r4 = Restaurante(4, "Café Central", "cafetería", 4.6, "Bloque 33")
    for restaurante in (r1, r2, r3, r4):
        hub.agregar_restaurante(restaurante)

    platos = [
        Plato(1, "Bandeja paisa", r1, 18000, "colombiana", 950, 20, False, 10, 0),
        Plato(2, "Ensalada César", r2, 14000, "vegetariana", 350, 8, True, 5, 0),
        Plato(3, "Wrap de pollo", r1, 12000, "colombiana", 500, 10, True, 2, 30),
        Plato(4, "Bowl de quinua", r2, 16000, "vegetariana", 420, 12, True, 6, 0),
        Plato(5, "Arroz con pollo (excedente)", r1, 15000, "colombiana", 600, 15, False, 4, 40),
        Plato(6, "Jugo natural", r2, 6000, "vegetariana", 120, 5, True, 8, 20),
        Plato(7, "Arroz frito con verduras", r3, 13000, "asiática", 520, 9, False, 3, 25),
        Plato(8, "Ramen de cerdo", r3, 17000, "asiática", 700, 18, False, 6, 0),
        Plato(9, "Tofu salteado", r3, 15000, "vegetariana", 380, 11, True, 2, 15),
        Plato(10, "Café con pandebono", r4, 7000, "cafetería", 300, 4, False, 1, 0),
        Plato(11, "Sándwich integral", r4, 9000, "cafetería", 410, 6, True, 5, 35),
        Plato(12, "Torta de chocolate", r4, 8000, "postres", 520, 3, False, 3, 50),
    ]
    for plato in platos:
        hub.agregar_plato(plato)
