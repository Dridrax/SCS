#plugins/misiones/menus_misiones.py
from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int
from plugins.misiones.helpers_misiones import (
    crear_mision,
    obtener_mision,
    editar_datos_basicos,
    imprimir_resultados,
    eliminar_mision_helper,
    sync_misiones_plugin_cache,
    completar_mision,
    fallar_mision,
    obtener_bloque,
    agregar_recompensa,
    editar_recompensa,
    eliminar_recompensa,
)

# --------------------------
# Selección de misión
# --------------------------
def seleccionar_mision(sistema, accion="modificar"):
    misiones = sistema.get("misiones", {}).get("activas", {})
    if not misiones:
        print(f"❌ No hay misiones para {accion}.")
        return None

    lista = list(misiones.values())
    print(f"\n=== MISIÓN A {accion.upper()} ===")
    for i, m in enumerate(lista, 1):
        print(f"{i}. {m.get('nombre', 'Sin nombre')}")

    seleccion = input("Elige misión por número o nombre (Enter para cancelar): ").strip()
    if not seleccion:
        return None

    if seleccion.isdigit():
        idx = int(seleccion) - 1
        if 0 <= idx < len(lista):
            return lista[idx]
    else:
        for m in lista:
            if m.get("nombre","").lower() == seleccion.lower():
                return m

    print("❌ Misión no encontrada.")
    return None

# --------------------------
# Menú crear misión
# --------------------------
def menu_crear_mision(sistema):
    print("\n=== CREAR NUEVA MISIÓN ===")
    id = input("ID única: ").strip()
    nombre = input("Nombre: ").strip()
    descripcion = input("Descripción: ").strip()
    objetivo = input("Objetivo: ").strip()

    m = crear_mision(sistema, id=id, nombre=nombre, descripcion=descripcion, objetivo=objetivo)
    if m:
        print(f"✅ Misión '{nombre}' creada.")
    else:
        print(f"❌ Error: ya existe misión con ID '{id}'.")

# --------------------------
# Menú modificar misión
# --------------------------
def modificar_mision(sistema, mision_id):
    mision = obtener_mision(sistema, mision_id)
    if not mision:
        print("❌ Misión no encontrada.")
        return

    while True:
        print(f"\n--- MODIFICAR MISIÓN {mision['nombre']} ---")
        print("1. Editar datos básicos")
        print("2. Editar recompensas")
        print("3. Editar penalizaciones")
        print("4. Volver")
        opcion = pedir_int("Elige opción: ", default=4)

        if opcion == 1:
            nombre = input(f"Nombre ({mision['nombre']}): ").strip() or mision['nombre']
            descripcion = input(f"Descripción ({mision['descripcion']}): ").strip() or mision['descripcion']
            objetivo = input(f"Objetivo ({mision['objetivo']}): ").strip() or mision['objetivo']
            editar_datos_basicos(mision, nombre=nombre, descripcion=descripcion, objetivo=objetivo)
            print("✅ Datos básicos actualizados.")

        elif opcion == 2:
            menu_editar_bloque(mision, "recompensas")
        elif opcion == 3:
            menu_editar_bloque(mision, "penalizaciones")
        else:
            break

def menu_editar_bloque(mision, clave):
    bloque = obtener_bloque(mision, clave)
    while True:
        print(f"\n--- {clave.upper()} ---")
        print("1. Agregar")
        print("2. Editar")
        print("3. Eliminar")
        print("4. Volver")
        opcion = pedir_int("Opción: ", default=4)
        if opcion == 1:
            tipo = input("Tipo (objetos/stats/dinero/progress_stats/puntos_stats/nivel/tiradas): ").strip()
            datos = {}
            if tipo == "objetos":
                datos["nombre"] = input("Nombre objeto: ")
                datos["cantidad"] = int(input("Cantidad: "))
                datos["rareza"] = input("Rareza: ")
                datos["tipo"] = input("Tipo: ")
            else:
                datos["nombre"] = input("Nombre: ")
                datos["valor"] = int(input("Valor: "))
            agregar_recompensa(bloque, tipo, datos)
            print("✅ Recompensa agregada.")
        elif opcion == 2:
            tipo = input("Tipo a editar: ").strip()
            clave_dato = input("Clave (nombre del stat/objeto): ").strip() or None
            valor = input("Valor/Actualizar (si es dict, ignorar por ahora): ").strip()
            try: valor = int(valor)
            except: pass
            editar_recompensa(bloque, tipo, clave=clave_dato, valor=valor)
            print("✅ Recompensa editada.")
        elif opcion == 3:
            tipo = input("Tipo a eliminar: ").strip()
            clave_dato = input("Clave a eliminar (opcional): ").strip() or None
            index = None
            if tipo == "objetos":
                index = int(input("Index objeto: "))
            eliminar_recompensa(bloque, tipo=tipo, clave=clave_dato, index=index)
            print("✅ Eliminado.")
        else:
            break

# --------------------------
# Menú administración
# --------------------------
def menu_administrar_misiones(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    while True:
        print("\n=== ADMINISTRAR MISIONES ===")
        print("1. Crear nueva misión")
        print("2. Modificar misión")
        print("3. Eliminar misión")
        print("4. Volver")
        opcion = pedir_int("Opción: ", default=4)

        if opcion == 1:
            menu_crear_mision(sistema)
        elif opcion == 2:
            m = seleccionar_mision(sistema, "modificar")
            if m:
                modificar_mision(sistema, m["id"])
        elif opcion == 3:
            m = seleccionar_mision(sistema, "eliminar")
            if m:
                confirmar = input(f"¿Seguro que quieres eliminar {m['nombre']}? (s/n): ").lower()
                if confirmar == "s":
                    eliminar_mision_helper(sistema, m["id"])
                    print("✅ Eliminado.")
        else:
            break

# --------------------------
# Mostrar misiones y gestionar
# --------------------------
def mostrar_misiones(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    activas = sistema.get("misiones", {}).get("activas", {})
    misiones_list = [m for m in activas.values() if isinstance(m, dict) and "id" in m and "nombre" in m]
    if not misiones_list:
        print("❌ No hay misiones activas.")
        return

    while True:
        print("\n=== MISIONES ===")
        for idx, m in enumerate(misiones_list, 1):
            print(f"{idx}. {m['nombre']}")

        seleccion = input("\nElige misión por número o nombre (Enter para salir): ").strip()
        if not seleccion:
            break

        mision = None
        if seleccion.isdigit():
            index = int(seleccion)-1
            if 0<=index<len(misiones_list):
                mision = misiones_list[index]
        else:
            for m in misiones_list:
                if m["nombre"].lower()==seleccion.lower():
                    mision = m
                    break

        if not mision:
            print("❌ Misión no encontrada.")
            continue

        gestion_mision(sistema, mision, misiones_list)

def gestion_mision(sistema, mision, misiones_list):
    while True:
        print(f"\n--- DETALLES DE {mision['nombre']} ---")
        print(f"ID: {mision['id']}")
        print(f"Descripción: {mision['descripcion']}")
        print(f"Objetivo: {mision['objetivo']}")
        imprimir_resultados("Recompensas", mision.get("recompensas", {}))
        imprimir_resultados("Penalizaciones", mision.get("penalizaciones", {}))

        print("\n[C] Completar   [F] Fallar   [D] Eliminar   [Enter] Volver")
        accion = input("> ").strip().lower()
        if accion=="c":
            completar_mision(sistema, mision["id"])
            misiones_list.remove(mision)
            print("✅ Completada.")
            break
        elif accion=="f":
            fallar_mision(sistema, mision["id"])
            misiones_list.remove(mision)
            print("❌ Fallada.")
            break
        elif accion=="d":
            confirmar = input("Confirmar eliminación (s/n): ").lower()
            if confirmar=="s":
                eliminar_mision_helper(sistema, mision["id"])
                misiones_list.remove(mision)
                print("✅ Eliminada.")
                break
        else:
            break



"""
DOCUMENTACIÓN DEL PLUGIN DE MISIONES

===========================
1️⃣ Estructura de archivos
===========================
plugins/misiones/
│
├─ helpers_misiones.py   # Funciones internas de gestión de misiones
├─ menus_misiones.py     # Menús interactivos de creación, edición y visualización
├─ modelos.py            # Modelos de datos para misiones
└─ __init__.py

Integración:
- Plugins activos: "misiones": True en sistema["plugins_activos"]
- Menús principales:
    - menu_mostrar → mostrar_misiones(sistema)
    - menu_modificar → menu_administrar_misiones(sistema)

===========================
2️⃣ helpers_misiones.py
===========================

Inicialización:
---------------
def inicializar_misiones(sistema)
- Crea estructura base sistema["misiones"] si no existe.
- Sincroniza plugin_cache para mantener versión rápida de misiones activas.

Crear misión:
-------------
def crear_mision(sistema, *, id, nombre, descripcion="", objetivo="", recompensas=None, penalizaciones=None) -> bool
- Crea una nueva misión en sistema["misiones"]["activas"].
- Retorna True si se creó, False si ya existía.
- Parámetros:
    - id: identificador único
    - nombre: nombre visible
    - descripcion: descripción narrativa
    - objetivo: objetivo de la misión
    - recompensas: dict inicial de recompensas
    - penalizaciones: dict inicial de penalizaciones

def menu_crear_mision(sistema)
- Menú interactivo para crear misión y agregar recompensas/penalizaciones.

Modificar misión:
-----------------
def modificar_mision(sistema, mision_id) -> bool
- Edita datos básicos, recompensas o penalizaciones.
- Retorna False si no existe la misión.

def editar_datos_basicos_mision(mision)
- Edita nombre, descripción y objetivo.

def menu_editar_recompensas(sistema, mision, clave="recompensas")
- Menú para agregar/editar/eliminar recompensas o penalizaciones.
- clave puede ser "recompensas" o "penalizaciones".

def añadir_recompensa(sistema, bloque)
- Añade un tipo de recompensa/penalización:
  - objetos → items para inventario
  - stats → stats básicos
  - progress_stats → stats de progreso con nivel y máximo
  - puntos_stats, nivel, tiradas
  - dinero

def editar_recompensa_existente(bloque)
- Edita item existente, stat o dinero.

def eliminar_recompensa(bloque)
- Elimina recompensas/penalizaciones existentes.

def elegir_destino() -> str|None
- Pregunta si la acción va en recompensas o penalizaciones.
- Retorna "recompensas", "penalizaciones" o None si se cancela.

Eliminar misión:
----------------
def eliminar_mision(sistema, id) -> bool
- Elimina misión activa del sistema.
- Pide confirmación interactiva.
- Retorna True si se eliminó, False si no.

Completar o fallar misión:
--------------------------
def completar_mision(sistema, mision_id) -> bool
- Aplica recompensas y elimina misión de activas.

def fallar_mision(sistema, mision_id) -> bool
- Aplica penalizaciones y elimina misión de activas.

def imprimir_resultados(titulo, datos)
- Imprime recompensas o penalizaciones de forma legible.
- Formatea objetos, stats, dinero, niveles y tiradas.

Sincronización de cache:
------------------------
def sync_misiones_plugin_cache(sistema)
- Mantiene estado.plugin_cache["plugins"]["misiones"]["activas"] actualizado.

===========================
3️⃣ menus_misiones.py
===========================

Selección de misión:
-------------------
def seleccionar_mision(sistema, accion="modificar") -> dict|None
- Lista todas las misiones activas.
- Permite seleccionar por número o nombre.
- Retorna misión seleccionada o None si se cancela/no encuentra.

Menú principal de administración:
---------------------------------
def menu_administrar_misiones(sistema=None)
- Menú interactivo:
    - Crear nueva misión
    - Modificar misión
    - Eliminar misión
- Llama a funciones de helpers_misiones.py
- Gestiona sincronización de cache y guardado automático.

Visualización de misiones:
--------------------------
def mostrar_misiones(sistema=None)
- Muestra todas las misiones activas de forma interactiva.
- Permite ver detalles, completar, fallar o eliminar misiones.
- Aplica recompensas y penalizaciones automáticamente.
"""
