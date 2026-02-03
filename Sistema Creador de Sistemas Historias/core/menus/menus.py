from core.estado_global import estado
from core.guardado.archivos import guardar_sistema, cargar_sistema, guardar_como

from core.sistemas.crear_sistema import crear_nuevo_sistema
from core.utils.funciones_utiles import pedir_int
from core.sistemas.mostrar_sistema import mostrar_ficha

#Stats
from core.stats.stats import (mostrar_stats, mostrar_progress_stats_bar, 
                              modificar_stat_simples, modificar_stat_progress, 
                              agregar_stat_simple, agregar_progress_stat,
                              eliminar_stat_simple, eliminar_progress_stat)



# ------------------- CREAR / CARGAR -------------------
def menu_crear_cargar():
    while True:
        print("\n=== CREAR / CARGAR ===")
        print("1. Crear Nuevo Sistema/Personaje")
        print("2. Cargar Sistema/Personaje")
        print("3. Volver")
        opcion = pedir_int("Elige una opción: ")

        if opcion == 1:
            crear_nuevo_sistema()
            if input("\n¿Deseas guardar este sistema? (s/n): ").lower() == "s":
                guardar_sistema()

        elif opcion == 2:
            archivo = input("Nombre del archivo a cargar: ")
            sistema = cargar_sistema(archivo)
            estado.sistema_actual = sistema
            estado.archivo_actual = archivo

        elif opcion == 3:
            break
        else:
            print("❌ Opción no válida.")

# ------------------- GUARDAR -------------------
def menu_guardado():
    if not estado.sistema_actual:
        print("\n❌ No hay sistema cargado.")
        return

    while True:
        print("\n=== GUARDADO ===")
        print("1. Guardar")
        print("2. Guardar como")
        print("3. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            guardar_sistema()
        elif opcion == "2":
            guardar_como()
        elif opcion == "3":
            break
        else:
            print("❌ Opción no válida.")

# ------------------- MOSTRAR DATOS DEL SISTEMA CARGADO -------------------
def menu_mostrar(sistema):
    
    if not estado.sistema_actual:
        print("\n❌ No hay sistema cargado.")
        return
    
    while True:
        print(f"\n=== SISTEMA DOC (Sistema actual: {sistema.get("nombre_sistema")}) ===")
        print("1. Mostrar Stats")
        print("2. Mostrar Ficha")
        print("3. Mostrar Inventario")
        print("4. Volver")
        opcion = pedir_int("Elige una opción: ")

        if opcion == 1:
            # --- STATS SIMPLES ---
            mostrar_stats(sistema)  # muestra stats simples y de progreso juntos

            # --- PROGRESS STATS (opcional si quieres usar función modular) ---
            # mostrar_progress_stats(sistema.get("progress_stats", {}))
            mostrar_progress_stats_bar(sistema.get("progress_stats", {}))

        elif opcion == 2:
            mostrar_ficha(estado.sistema_actual)

        elif opcion == 3:
            print("\nImplementar mañana")
        elif opcion == 4:
            break

# ------------------- MODIFICAR DATOS DEL SISTEMA CARGADO -------------------
def menu_modificar(sistema):
    if not estado.sistema_actual:
        print("\n❌ No hay sistema cargado.")
        return
    
    while True:
        print(f"\n=== SISTEMA DOC (Sistema actual: {sistema.get("nombre_sistema")}) ===")
        print("1. Modificar Stats.")
        print("2. Modificar Inventario.")
        print("3. Volver.")

        opcion = pedir_int("\nElige una opción: ")
        if opcion == 1:
            modificar_stats(sistema)
        elif opcion == 2:
            print("\nImplementar mañana")
        else:
            estado.cambios_no_guardados = True
            break

# ------------------- MODIFICAR STATS MENUS Y SUBMENUS -------------------
def modificar_stats(sistema):
    if not estado.sistema_actual:
        print("\n❌ No hay sistema cargado.")
        return
    
    while True:
        print(f"\n=== MODIFICAR STATS (Sistema actual: {sistema.get("nombre_sistema")}) ===")

        print("1. Modificar Stats.")
        print("2. Agregar Stats.")
        print("3. Eliminar Stats.")
        print("4. Volver.")

        opcion = pedir_int("\nElige una opción: ")
        
        #Modificar Stats
        if opcion == 1:
            
            print("1. Modificar Stats Simples.")
            print("2. Modificar Stats Progress.")
            print("3. Volver.")

            opcion_2 = pedir_int("\nElige una opcíon: ")

            if opcion_2 == 1:
                modificar_stat_simples(sistema)
            elif opcion_2 == 2:
                modificar_stat_progress(sistema)
            else:
                estado.cambios_no_guardados = True
                break
        
        #Agregar Stats
        elif opcion == 2:

            print("1. Agregar Stats Simples.")
            print("2. Agregar Stats Progress.")
            print("3. Volver.")

            opcion_3 = pedir_int("\nElige una opcíon: ")

            if opcion_3 == 1:
                agregar_stat_simple(sistema)
            elif opcion_3 == 2:
                agregar_progress_stat(sistema)
            else:
                estado.cambios_no_guardados = True
                break

        #Eliminar Stats
        elif opcion == 3:
            print("1. Eliminar Stats Simples.")
            print("2. Eliminar Stats Progress.")
            print("3. Volver.")

            opcion_4 = pedir_int("\nElige una opcíon: ")

            if opcion_3 == 1:
                eliminar_stat_simple(sistema)
            elif opcion_3 == 2:
                eliminar_progress_stat(sistema)
            else:
                estado.cambios_no_guardados = True
                break

        else:
            guardar_sistema()
            break