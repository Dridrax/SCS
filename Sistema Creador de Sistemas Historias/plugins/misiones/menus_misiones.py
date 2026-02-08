from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int
from plugins.misiones.helpers import (crear_mision, modificar_mision, eliminar_mision, 
                                      completar_mision, fallar_mision, menu_crear_mision,
                                      imprimir_resultados)


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

        # ─────────────────────────────
        # CREAR NUEVA MISIÓN
        # ─────────────────────────────
        if opcion == 1:
            menu_crear_mision(estado.sistema_actual)

        elif opcion == 2:
            misiones = sistema.get("misiones", {})
            if not misiones:
                print("❌ No hay misiones para modificar.")
                continue
            
            print("\n=== MISIÓN A MODIFICAR ===")
            lista = list(misiones.values())
            for i, m in enumerate(lista, 1):
                print(f"{i}. {m['nombre']}")
        
            seleccion = input("Elige misión por número o nombre (Enter para cancelar): ").strip()
            if not seleccion:
                continue
            
            mision = None
            if seleccion.isdigit():
                idx = int(seleccion) - 1
                if 0 <= idx < len(lista):
                    mision = lista[idx]
            else:
                for m in lista:
                    if m["nombre"].lower() == seleccion.lower():
                        mision = m
                        break
                    
            if not mision:
                print("❌ Misión no encontrada.")
                continue
            
            modificar_mision(sistema, mision["id"])


        elif opcion == 3:
            eliminar_mision(sistema, mision["id"])

        else:
            break




def mostrar_misiones(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    misiones = sistema.get("misiones", {})
    if not misiones:
        print("❌ No hay misiones.")
        return

    misiones_list = list(misiones.values())

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

        # Entrar directamente a los detalles
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

            print("\n[C] Completar misión   [F]Fallar Mision   [D] Eliminar misión   [Enter] Volver")
            accion = input("> ").strip().lower()

            if accion == "c":
                completar_mision(sistema, mision["id"])
                misiones_list.remove(mision)
                print("\n✅ Misión completada y recompensas entregadas.")
                imprimir_resultados("Recompensas", recompensas)
                break

            elif accion == "f":
                fallar_mision(sistema, mision["id"])
                misiones_list.remove(mision)
                print("\n❌ Misión fallada y penalizaciones aplicadas.")
                imprimir_resultados("Penalizaciones", penalizaciones)
                break

            elif accion == "d":
                confirmar = input("¿Seguro que quieres eliminar esta misión? (s/n): ").lower()
                if confirmar == "s":
                    eliminar_mision(sistema, mision["id"])
                    misiones_list.remove(mision)
                    print("\n✅ Misión eliminada.")
                    break
            else:
                break  # Enter → volver a lista de misiones
        # Aquí ya no volvemos al principio si la misión fue encontrada; solo volvemos si el usuario quiere otra misión

