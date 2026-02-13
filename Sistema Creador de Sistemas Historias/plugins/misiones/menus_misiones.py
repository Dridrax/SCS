#plugins/misiones/menus_misiones.py
from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int
from plugins.misiones.helpers_misiones import (
    crear_mision,
    obtener_mision,
    editar_datos_basicos,
    imprimir_resultados,
    eliminar_mision_helper,
    completar_mision,
    fallar_mision
)

from core.recompensas.bloques import (
    menu_editar_bloque,
    menu_editar_bloque_interactivo,
    obtener_bloque
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



