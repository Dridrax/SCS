from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int
from core.guardado.archivos import guardar_sistema
from plugins.misiones.helpers import (crear_mision, modificar_mision, eliminar_mision, 
                                      completar_mision, fallar_mision, menu_crear_mision,
                                      imprimir_resultados, sync_misiones_plugin_cache)


def seleccionar_mision(sistema, accion="modificar"):
    """
    Función para seleccionar una misión de forma interactiva.
    Retorna la misión seleccionada (dict) o None si se cancela/no encuentra.
    """
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

    mision = None
    if seleccion.isdigit():
        idx = int(seleccion) - 1
        if 0 <= idx < len(lista):
            mision = lista[idx]
    else:
        for m in lista:
            if m.get("nombre", "").lower() == seleccion.lower():
                mision = m
                break

    if not mision:
        print("❌ Misión no encontrada.")
        return None

    return mision


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

        opcion = pedir_int("Elige una opción: ", default=4)

        if opcion == 1:
            menu_crear_mision(sistema)

        elif opcion == 2:
            mision = seleccionar_mision(sistema, accion="modificar")
            if mision:
                modificar_mision(sistema, mision["id"])

        elif opcion == 3:
            mision = seleccionar_mision(sistema, accion="eliminar")
            if mision:
                eliminar_mision(sistema, mision["id"])

        else:
            break





def mostrar_misiones(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    # Obtener solo misiones activas
    activas = sistema.get("misiones", {}).get("activas", {})
    
    # Convertir a lista y filtrar solo misiones válidas
    misiones_list = [m for m in activas.values() if isinstance(m, dict) and "id" in m and "nombre" in m]
    
    if not misiones_list:
        print("❌ No hay misiones activas.")
        return

    while True:
        print("\n=== MISIONES ===")
        for idx, m in enumerate(misiones_list, 1):
            print(f"{idx}. {m['nombre']}")

        seleccion = input("\nElige una misión por número o nombre (Enter para salir): ").strip()
        if not seleccion:
            break  # Enter vacío → salir del menú

        # Buscar misión
        mision = None
        if seleccion.isdigit():
            index = int(seleccion) - 1
            if 0 <= index < len(misiones_list):
                mision = misiones_list[index]
        else:
            for m in misiones_list:
                if m["nombre"].lower() == seleccion.lower():
                    mision = m
                    break

        if not mision:
            print("❌ No se encontró esa misión.")
            continue

        # Entrar a los detalles de la misión
        while True:
            print("\n--- DETALLES DE LA MISIÓN ---")
            print(f"ID: {mision['id']}")
            print(f"Nombre: {mision['nombre']}")
            print(f"Descripción: {mision['descripcion']}")
            print(f"Objetivo: {mision['objetivo']}")

            recompensas = mision.get("recompensas", {})
            imprimir_resultados("Recompensas", recompensas)

            penalizaciones = mision.get("penalizaciones", {})
            imprimir_resultados("Penalizaciones", penalizaciones)

            print("\n[C] Completar misión   [F] Fallar Misión   [D] Eliminar misión   [Enter] Volver")
            accion = input("> ").strip().lower()

            if accion == "c":
                completar_mision(sistema, mision["id"])
                # Eliminar del sistema y de la lista temporal
                sistema["misiones"]["activas"].pop(mision["id"], None)
                misiones_list.remove(mision)
                # Guardar y sincronizar plugin cache
                estado.cambios_no_guardados = True
                guardar_sistema()
                sync_misiones_plugin_cache(sistema)
                print("\n✅ Misión completada y recompensas entregadas.")
                imprimir_resultados("Recompensas", recompensas)
                break

            elif accion == "f":
                fallar_mision(sistema, mision["id"])
                # Eliminar del sistema y de la lista temporal
                sistema["misiones"]["activas"].pop(mision["id"], None)
                misiones_list.remove(mision)
                # Guardar y sincronizar plugin cache
                estado.cambios_no_guardados = True
                guardar_sistema()
                sync_misiones_plugin_cache(sistema)
                print("\n❌ Misión fallada y penalizaciones aplicadas.")
                imprimir_resultados("Penalizaciones", penalizaciones)
                break

            elif accion == "d":
                confirmar = input("¿Seguro que quieres eliminar esta misión? (s/n): ").lower()
                if confirmar == "s":
                    eliminar_mision(sistema, mision["id"])
                    # Eliminar del sistema y de la lista temporal
                    sistema["misiones"]["activas"].pop(mision["id"], None)
                    misiones_list.remove(mision)
                    # Guardar y sincronizar plugin cache
                    sync_misiones_plugin_cache(sistema)
                    
                    break
            else:
                break


