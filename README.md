# CampusFoodHub Inteligente

Sistema que centraliza el menú de los restaurantes de un campus universitario. Permite filtrar platos, elegir un perfil de usuario, recibir recomendaciones personalizadas, consultar ofertas de excedentes, conocer la congestión estimada de cada restaurante, obtener el combo óptimo de ofertas para un presupuesto y crear preórdenes con su comprobante.

Proyecto final de Programación Orientada a Objetos. Contiene el backend en Python, que expone una API HTTP/JSON, y la interfaz web que la consume.

## Requisitos

- Python 3.14 (versión verificada: 3.14.0).
- Dependencias: `pip install -r requirements.txt` (solo `numpy`).

## Ejecución

Desde la raíz del repositorio:

```bash
python main.py
```

La interfaz web queda disponible en `http://127.0.0.1:8000` (ábrala en el navegador). Las rutas que empiezan por `/api/` forman la API; las demás se sirven como archivos estáticos desde la carpeta `frontend/`. Para detener el servidor, use `Ctrl+C`.

Los datos se cargan en memoria al arrancar (4 restaurantes y 12 platos), y la sesión tiene un único estudiante, "Simón Valencia", sin perfil activo hasta que se elija uno. Al reiniciar el servidor, el estado vuelve al inicial.

## Pruebas

```bash
python -m unittest discover -s tests
```

## Estructura

| Ruta | Capa del UML | Contenido |
|---|---|---|
| `main.py` | Punto de entrada | Arma la fachada, siembra los datos, crea el estudiante de la sesión y lanza el servidor |
| `backend/excepciones/errores.py` | Excepciones | `CampusFoodHubError`, `ValidacionError`, `EntidadNoEncontradaError`, `ReglaNegocioError` |
| `backend/dominio/restaurante.py` | Dominio | `Restaurante` |
| `backend/dominio/plato.py` | Dominio | `Plato` |
| `backend/dominio/estudiante.py` | Dominio | `Estudiante` |
| `backend/dominio/item_pedido.py` | Dominio | `ItemPedido` |
| `backend/dominio/pedido.py` | Dominio | `Pedido` |
| `backend/logica/campus_food_hub.py` | Lógica de negocio | `CampusFoodHub` (fachada) |
| `backend/logica/motor_recomendacion.py` | Lógica de negocio | `MotorRecomendacion` |
| `backend/logica/estimador_espera.py` | Lógica de negocio | `EstimadorEspera` |
| `backend/logica/optimizador_combos.py` | Lógica de negocio | `OptimizadorCombos` |
| `backend/controlador/manejador_http.py` | Controlador | `ManejadorHTTP` |
| `backend/datos/datos_iniciales.py` | Datos iniciales | `sembrar_datos(hub)` |
| `tests/` | Pruebas | Pruebas `unittest` por requisito, por excepción y de la API HTTP |
| `frontend/index.html` | Interfaz web | Estructura de la página |
| `frontend/css/estilos.css` | Interfaz web | Estilos de la página |
| `frontend/js/main.js` | Interfaz web | Punto de entrada: crea `PaginaPrincipal` y llama `iniciar()` |
| `frontend/js/api.js` | Interfaz web | Cliente HTTP: única capa que llama a la API |
| `frontend/js/presentacion.js` | Interfaz web | Escape de HTML, formato de moneda y plantilla de tarjeta de plato |
| `frontend/js/componentes/` | Interfaz web | Una clase por archivo: `PaginaPrincipal`, `PanelFiltros`, `ListaMenu`, `SelectorPerfil`, `SeccionRecomendaciones`, `SeccionOfertas`, `ResumenCampus`, `PanelCongestion`, `FormularioPreorden`, `ModalComprobante`, `FormularioCombo` |

## Contrato JSON de la API

Todas las respuestas son JSON en UTF-8. Los errores tienen la forma `{"error": mensaje}`:

| Código | Excepción | Mensaje |
|---|---|---|
| 400 | `ValidacionError` | Motivo de la validación fallida |
| 404 | `EntidadNoEncontradaError` (perfil, plato o ruta `/api/...` inexistente) | Siempre `"no se encontró el elemento solicitado"` |
| 409 | `ReglaNegocioError` | Regla de negocio incumplida |

### Objetos

- **plato**: `id`, `nombre`, `restaurante` (nombre), `categoria`, `precio`, `precio_final`, `descuento_excedente`, `calorias`, `tiempo_preparacion`, `saludable`, `inventario`, `es_excedente`.
- **recomendación**: `{plato, matchScore, razon}`.
- **resumen**: `{platos_activos, restaurantes_abiertos, ofertas_vigentes, plato_mas_rapido}` (`plato_mas_rapido` es un plato o `null`).
- **congestión**: `{restaurante, congestion ("bajo" | "medio" | "alto"), tiempo_estimado_min}`.
- **combo**: `{platos, gasto_total, ahorro}`.
- **comprobante**: `{numero_pedido, cliente, restaurante, hora_recogida, lineas: [{plato, cantidad, subtotal}], notas, total}`.

### Endpoints

| Método | Ruta | Parámetros o cuerpo | Respuesta | RF |
|---|---|---|---|---|
| GET | `/api/menu` | Consulta opcional: `texto`, `precio_maximo`, `tiempo_maximo`, `solo_saludable`, `solo_excedente` (`true`/`false`) | 200, lista de platos | RF1, RF2 |
| POST | `/api/perfil` | `{"slug": "balance" \| "fit_rapido" \| "ahorro_total" \| "antojo_del_dia" \| "vegetariano"}` | 200, perfil del estudiante | RF3 |
| GET | `/api/recomendaciones` | Ninguno | 200, hasta 4 recomendaciones | RF4 |
| GET | `/api/ofertas` | Ninguno | 200, lista de platos de mayor a menor descuento | RF5 |
| GET | `/api/resumen` | Ninguno | 200, resumen | RF6 |
| POST | `/api/preorden` | `{"items": [{"id_plato": int, "cantidad": int}], "nombre_cliente": str, "hora_recogida": "HH:MM", "notas": str (opcional)}` | 201, comprobante | RF7, RF8 |
| GET | `/api/congestion` | Ninguno | 200, lista de congestión de los restaurantes abiertos | RF9 |
| GET | `/api/combo` | `presupuesto` (entero positivo) | 200, combo | RF10 |

Sin parámetros, `/api/menu` devuelve el menú disponible completo; así se resuelve "Limpiar filtros". Un texto vacío cuenta como criterio no informado.

### Ejemplos reales

Los ejemplos se capturaron del servidor en ejecución con los datos iniciales. En las listas largas se muestra solo el primer elemento.

`GET /api/menu` (200, 12 platos; se muestra el primero):

```json
[{"id": 1, "nombre": "Bandeja paisa", "restaurante": "Sazón Criollo", "categoria": "colombiana", "precio": 18000, "precio_final": 18000, "descuento_excedente": 0, "calorias": 950, "tiempo_preparacion": 20, "saludable": false, "inventario": 10, "es_excedente": false}]
```

`GET /api/menu?texto=arroz&solo_excedente=true` (200):

```json
[{"id": 5, "nombre": "Arroz con pollo (excedente)", "restaurante": "Sazón Criollo", "categoria": "colombiana", "precio": 15000, "precio_final": 9000, "descuento_excedente": 40, "calorias": 600, "tiempo_preparacion": 15, "saludable": false, "inventario": 4, "es_excedente": true}, {"id": 7, "nombre": "Arroz frito con verduras", "restaurante": "Wok Express", "categoria": "asiática", "precio": 13000, "precio_final": 9750, "descuento_excedente": 25, "calorias": 520, "tiempo_preparacion": 9, "saludable": false, "inventario": 3, "es_excedente": true}]
```

`GET /api/menu?precio_maximo=abc` (400):

```json
{"error": "El precio máximo debe ser un número entero positivo."}
```

`GET /api/menu?texto=` seguido de 81 caracteres (400):

```json
{"error": "El texto de búsqueda no puede superar 80 caracteres."}
```

`POST /api/perfil` con `{"slug": "fit_rapido"}` (200):

```json
{"nombre": "Simón Valencia", "perfil_activo": "fit_rapido", "presupuesto": 20000, "enfoque_salud": 0.8, "enfoque_velocidad": 0.8, "cocina_preferida": null}
```

`POST /api/perfil` con `{"slug": "keto"}` (404):

```json
{"error": "no se encontró el elemento solicitado"}
```

`POST /api/perfil` con un cuerpo que no es JSON (400):

```json
{"error": "El cuerpo de la solicitud no es un JSON válido."}
```

`GET /api/recomendaciones` con el perfil `fit_rapido` (200, 4 recomendaciones; se muestra la primera):

```json
[{"plato": {"id": 6, "nombre": "Jugo natural", "restaurante": "Green Bowl", "categoria": "vegetariana", "precio": 6000, "precio_final": 4800, "descuento_excedente": 20, "calorias": 120, "tiempo_preparacion": 5, "saludable": true, "inventario": 8, "es_excedente": true}, "matchScore": 0.7747, "razon": "Te lo recomendamos porque se ajusta a tu presupuesto, es una opción saludable, acorde a tu perfil, se prepara rápido, está en oferta por excedente."}]
```

`GET /api/ofertas` (200, 7 ofertas; se muestra la primera):

```json
[{"id": 12, "nombre": "Torta de chocolate", "restaurante": "Café Central", "categoria": "postres", "precio": 8000, "precio_final": 4000, "descuento_excedente": 50, "calorias": 520, "tiempo_preparacion": 3, "saludable": false, "inventario": 3, "es_excedente": true}]
```

`GET /api/resumen` (200):

```json
{"platos_activos": 12, "restaurantes_abiertos": 4, "ofertas_vigentes": 7, "plato_mas_rapido": {"id": 12, "nombre": "Torta de chocolate", "restaurante": "Café Central", "categoria": "postres", "precio": 8000, "precio_final": 4000, "descuento_excedente": 50, "calorias": 520, "tiempo_preparacion": 3, "saludable": false, "inventario": 3, "es_excedente": true}}
```

`POST /api/preorden` (201):

```json
{"items": [{"id_plato": 2, "cantidad": 2}, {"id_plato": 6, "cantidad": 1}], "nombre_cliente": "Simón Valencia", "hora_recogida": "12:30", "notas": "Sin crutones"}
```

```json
{"numero_pedido": 1, "cliente": "Simón Valencia", "restaurante": "Green Bowl", "hora_recogida": "12:30", "lineas": [{"plato": "Ensalada César", "cantidad": 2, "subtotal": 28000}, {"plato": "Jugo natural", "cantidad": 1, "subtotal": 4800}], "notas": "Sin crutones", "total": 32800}
```

Errores reales de `POST /api/preorden`:

| Caso | Código | Respuesta |
|---|---|---|
| `items` vacío | 400 | `{"error": "La preorden debe incluir al menos un plato."}` |
| `hora_recogida` = `"24:00"` | 400 | `{"error": "La hora de recogida debe tener el formato HH:MM (00:00 a 23:59)."}` |
| `id_plato` = 99 | 404 | `{"error": "no se encontró el elemento solicitado"}` |
| Platos 1 y 2 (restaurantes distintos) | 409 | `{"error": "Todos los platos de una preorden deben ser del mismo restaurante."}` |
| Plato 10, cantidad 2 (inventario 1) | 409 | `{"error": "Inventario insuficiente para 'Café con pandebono'."}` |

Otros mensajes 400 de la preorden: `"El nombre del cliente es obligatorio."`, `"La cantidad por plato debe ser un entero entre 1 y 5."`, `"El identificador del plato debe ser un número entero."`, `"La cantidad total de '<plato>' debe estar entre 1 y 5."`, `"Los ítems deben ser una lista de objetos con id_plato y cantidad."` y `"Las notas deben ser texto."`. Otro mensaje 409: `"El restaurante '<nombre>' está cerrado."`.

`GET /api/congestion` antes de la preorden anterior (200):

```json
[{"restaurante": "Sazón Criollo", "congestion": "bajo", "tiempo_estimado_min": 15.0}, {"restaurante": "Green Bowl", "congestion": "bajo", "tiempo_estimado_min": 8.3}, {"restaurante": "Wok Express", "congestion": "bajo", "tiempo_estimado_min": 12.7}, {"restaurante": "Café Central", "congestion": "bajo", "tiempo_estimado_min": 4.3}]
```

Después de la preorden, Green Bowl pasa a `"tiempo_estimado_min": 11.0` porque la preorden sumó un único pedido a su historial.

`GET /api/combo?presupuesto=20000` (200; se muestran solo el `id` y el `precio_final` de cada plato, que en la respuesta real viene completo):

```json
{"platos": [{"id": 5, "precio_final": 9000}, {"id": 11, "precio_final": 5850}, {"id": 12, "precio_final": 4000}], "gasto_total": 18850, "ahorro": 13150}
```

`GET /api/combo?presupuesto=1000` (200, sin combo posible):

```json
{"platos": [], "gasto_total": 0, "ahorro": 0}
```

`GET /api/combo?presupuesto=abc` (400; igual con `0`, un número negativo o sin parámetro):

```json
{"error": "El presupuesto debe ser un número entero positivo."}
```

`GET /api/inexistente` o `POST /api/inexistente` (404):

```json
{"error": "no se encontró el elemento solicitado"}
```

### Flujo de llamadas de la interfaz

- **Al cargar la página**: `GET /api/menu` (RF1), `GET /api/resumen` (RF6), `GET /api/recomendaciones` (RF4), `GET /api/ofertas` (RF5) y `GET /api/congestion` (RF9).
- **Al cambiar un filtro**: `GET /api/menu` con los cinco controles (RF2). "Limpiar filtros" vacía los controles y llama `GET /api/menu` sin parámetros. Ante un 400, la interfaz muestra el motivo y conserva la lista anterior.
- **Tras elegir un perfil**: `POST /api/perfil` (RF3) y luego `GET /api/recomendaciones` (RF4).
- **Tras crear una preorden**: `POST /api/preorden` (RF7). La respuesta 201 es el comprobante que muestra el modal (RF8). Luego conviene volver a pedir `GET /api/menu`, `GET /api/resumen`, `GET /api/ofertas`, `GET /api/recomendaciones` (el perfil se ajusta según la elección) y `GET /api/congestion`, porque cambiaron el inventario, el perfil y el historial del restaurante.
- **Combo**: `GET /api/combo?presupuesto=<entero>` (RF10). Una lista `platos` vacía significa que no se encontró combo.

## Flujo de trabajo en equipo

1. Hacer fork o clonar `https://github.com/MrmoonSOS/PROYECTO_FINAL_POO.git`.
2. Crear una rama por tarea a partir de la rama principal (`git checkout -b nombre-de-la-tarea`).
3. Hacer commits pequeños y descriptivos en español.
4. Ejecutar `python -m unittest discover -s tests` antes de subir cambios.
5. Abrir un pull request hacia la rama principal.

## Autoría

- Simón Valencia
- Tomás Henao
- Andrés Areiza
