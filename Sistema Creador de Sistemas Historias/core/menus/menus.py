from core.estado_global import estado
from core.guardado.archivos import guardar_sistema, cargar_sistema, guardar_como

from core.sistemas.crear_sistema import crear_nuevo_sistema
from core.utils.funciones_utiles import pedir_int, pedir_si_no
from core.sistemas.mostrar_sistema import mostrar_ficha
from core.plugins.registry import PLUGINS
#plugins

from plugins.inventario.menus_inv import (menu_agregar_item, mostrar_items,
                                          menu_modificar_item, menu_eliminar_item)

#Stats
from core.stats.stats import (mostrar_stats, mostrar_progress_stats_bar, 
                              modificar_stat_simples, modificar_stat_progress, 
                              agregar_stat_simple, agregar_progress_stat,
                              eliminar_stat_simple, eliminar_progress_stat)


"""MENUS.PY - Documentación y guía de uso

Este archivo contiene los menús principales y submenús del programa SCS.
Se encarga de manejar la interacción con el usuario para:
    - Crear, cargar y guardar sistemas/personajes
    - Mostrar información del sistema cargado
    - Modificar stats y otros datos del sistema
    - Gestionar submenús específicos (stats, inventario, etc.)

-------------------
Estructura de menús:

1. CREAR / CARGAR
-----------------
Función: menu_crear_cargar()
- Permite al usuario:
    1. Crear un nuevo sistema/personaje usando crear_nuevo_sistema().
       - Después de crear el sistema, pregunta si se desea guardar inmediatamente.
    2. Cargar un sistema desde un archivo existente usando cargar_sistema().
       - Actualiza estado.sistema_actual y estado.archivo_actual.
    3. Volver al menú anterior.
- Validaciones: opción inválida, sistema existente, confirmaciones de guardado.

2. GUARDADO
-----------
Función: menu_guardado()
- Permite al usuario:
    1. Guardar cambios en el sistema actual.
    2. Guardar el sistema con un nombre nuevo ("Guardar como").
    3. Volver al menú anterior.
- Validación: no permite guardar si no hay un sistema cargado.

3. MOSTRAR DATOS DEL SISTEMA
----------------------------
Función: menu_mostrar(sistema)
- Permite mostrar información del sistema cargado.
- Opciones:
    1. Mostrar Stats:
        - Llama a mostrar_stats() para stats simples y progress_stats.
        - Llama a mostrar_progress_stats_bar() específicamente para la barra visual de progress_stats.
    2. Mostrar Ficha:
        - Llama a mostrar_ficha() con el sistema actual.
    3. Mostrar Inventario:
        - Actualmente sin implementar, placeholder para futuro.
    4. Volver.
- Validaciones: verifica que exista un sistema cargado antes de mostrar.

4. MODIFICAR DATOS DEL SISTEMA
------------------------------
Función: menu_modificar(sistema)
- Permite al usuario modificar información del sistema cargado.
- Opciones:
    1. Modificar Stats:
        - Llama a modificar_stats(sistema)
        - Este submenú permite modificar, agregar o eliminar stats (simples o progress).
    2. Modificar Inventario:
        - Placeholder para implementación futura.
    3. Volver:
        - Marca cambios como no guardados si se sale sin modificar.
- Validaciones: verifica que haya sistema cargado.

5. MODIFICAR STATS
------------------
Función: modificar_stats(sistema)
- Submenú que maneja todas las operaciones sobre stats.
- Opciones principales:
    1. Modificar Stats:
        - Permite modificar stats simples o stats de progreso usando:
            - modificar_stat_simples(sistema)
            - modificar_stat_progress(sistema)
        - Las progress_stats usan modificar_progreso() para manejar niveles y factor de escalado dinámico.
    2. Agregar Stats:
        - Permite agregar stats simples o progress usando:
            - agregar_stat_simple(sistema)
            - agregar_progress_stat(sistema)
        - Los progress stats incluyen factor de escalado editable desde su creación.
    3. Eliminar Stats:
        - Permite eliminar stats simples o progress usando:
            - eliminar_stat_simple(sistema)
            - eliminar_progress_stat(sistema)
    4. Volver al menú anterior.

- Validaciones y detalles:
    - Se asegura de que exista un sistema cargado antes de cualquier operación.
    - Cada acción de stats marca cambios en estado.cambios_no_guardados = True.
    - Las progress_stats manejan niveles automáticamente y factor de escalado dinámico.
    - La organización de los submenús permite separar claramente:
        - Modificar (sumar/restar, subir/bajar nivel)
        - Agregar (definir actual, max, nivel y factor)
        - Eliminar (remover stat específico)
        
-------------------
Mejoras sugeridas / observaciones
---------------------------------
1. Consistencia de opciones:
    - En eliminar stats, actualmente se usan las variables "opcion_3" para las sub-opciones; revisar que no haya error de copy-paste en los if.
2. Inventario:
    - Aún no implementado; se recomienda mantener placeholders o integrarlo después.
3. Factor de escalado:
    - Ya implementado en agregar_progress_stat y modificar_stat_progress.
4. Validaciones de entrada:
    - Se usa pedir_int() para entradas numéricas.
    - Confirmaciones tipo sí/no usan pedir_si_no().
5. Modularidad:
    - Menús están separados en funciones claras, fáciles de llamar desde un menú principal.
    - Cada función hace una sola cosa: mostrar menú, ejecutar la acción seleccionada, validar entradas.

-------------------
Recomendación final
------------------
- Mantener este archivo exclusivamente para menús y navegación de usuario.
- Funciones de stats, creación de sistema, guardado y utils se mantienen en sus respectivos archivos.
- Cualquier cambio futuro en stats (ej: nuevos tipos de stats) solo requerirá actualizar las funciones de stats y llamar desde aquí.
"""

# ------------------- CREAR / CARGAR -------------------
def menu_crear_cargar():
    while True:
        print("\n=== CREAR / CARGAR ===")
        print("1. Crear Nuevo Sistema/Personaje")
        print("2. Cargar Sistema/Personaje")
        print("3. Volver")
        opcion = pedir_int("\nElige una opción: ")

        if opcion == 1:
            crear_nuevo_sistema()
            if input("\n¿Deseas guardar este sistema? (s/n): ").lower() == "s":
                guardar_sistema()

        elif opcion == 2:
            archivo = input("\nNombre del archivo a cargar: ")
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

        opcion = input("\nElige una opción: ")

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
        opcion = pedir_int("\nElige una opción: ")

        if opcion == 1:
            # --- STATS SIMPLES ---
            mostrar_stats(sistema)  # muestra stats simples y de progreso juntos

            # --- PROGRESS STATS (opcional si quieres usar función modular) ---
            # mostrar_progress_stats(sistema.get("progress_stats", {}))
            mostrar_progress_stats_bar(sistema.get("progress_stats", {}))

        elif opcion == 2:
            mostrar_ficha(estado.sistema_actual)

        elif opcion == 3:
            mostrar_items()
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
            menu_modificar_stats(sistema)
        elif opcion == 2:
            menu_modificar_items(sistema)
        else:
            estado.cambios_no_guardados = True
            break

# ------------------- MODIFICAR STATS MENUS Y SUBMENUS -------------------
def menu_modificar_stats(sistema):
    
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

            if opcion_4 == 1:
                eliminar_stat_simple(sistema)
            elif opcion_4 == 2:
                eliminar_progress_stat(sistema)
            else:
                estado.cambios_no_guardados = True
                break

        else:
            guardar_sistema()
            break

# ------------------- MODIFICAR ITEMS MENUS Y SUBMENUS -------------------
def menu_modificar_items(sistema):
    if not estado.sistema_actual:
        print("\n❌ No hay sistema cargado.")
        return
    
    
    while True:
        print(f"\n=== MODIFICAR ITEMS (Sistema actual: {sistema.get("nombre_sistema")}) ===")

        print("1. Agregar Items.")
        print("2. Modificar Item.")
        print("3. Eliminar Items.")
        print("4. Mostrar Items.")
        print("5. Volver.")

        opcion = pedir_int("\nElige una opción: ")
        
        #Modificar Items
        if opcion == 1:
            menu_agregar_item()
        
        #Agregar Items
        elif opcion == 2:
            menu_modificar_item()

        #Eliminar Items
        elif opcion == 3:
            menu_eliminar_item()

        elif opcion == 4:
            mostrar_items()

        else:
            guardar_sistema()
            break

#------------------- ADMINISTRAR PLUGINS/MENU PLUGINS -------------------

# Diccionario con todos los plugins disponibles y sus funciones on_enable (opcional)
"""PLUGINS = {
    "inventario": {
        "on_enable": lambda sistema: sistema.setdefault("inventario", {})
    },
    # "habilidades": {...}, "bendiciones": {...} etc.
}"""

def menu_plugins(autoguardar=True):
    sistema = estado.sistema_actual

    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    plugins = sistema.get("plugins_activos", {})
    if not plugins:
        print("\n❌ No hay plugins definidos para este sistema.")
        return

    while True:
        print(f"\n=== ADMINISTRAR PLUGINS (Sistema actual: {sistema.get('nombre_sistema')}) ===")
        for i, plugin in enumerate(plugins, 1):
            estado_str = "✅ Activo" if plugins[plugin] else "❌ Inactivo"
            print(f"{i}. {plugin.capitalize()}: {estado_str}")
        print(f"{len(plugins)+1}. Continuar/Volver")

        try:
            opcion = int(input("\nElige un plugin para activar/desactivar: "))
        except ValueError:
            print("❌ Opción no válida.")
            continue

        if opcion == len(plugins)+1:
            if autoguardar and estado.cambios_no_guardados:
                guardar_sistema()
            break
        elif 1 <= opcion <= len(plugins):
            key = list(plugins.keys())[opcion - 1]
            nuevo_estado = not plugins[key]

            plugin_obj = PLUGINS.get(key)
            if nuevo_estado:  # Activar plugin
                plugins[key] = True

                # Restaurar datos desde plugin_cache si existen
                if key in estado.plugin_cache.get("plugins", {}):
                    sistema[key] = estado.plugin_cache["plugins"][key]
                elif plugin_obj and "on_enable" in plugin_obj:
                    plugin_obj["on_enable"](sistema)

                
                print(f"🔄 {key.capitalize()} ahora Activo")

            else:  # Desactivar plugin
                if key in sistema:
                    conservar = input(f"¿Conservar los datos del plugin '{key}' para poder restaurarlos después? (s/n): ").lower() == "s"
                    if conservar:
                        # Guardar en plugin_cache
                        if "plugins" not in estado.plugin_cache:
                            estado.plugin_cache["plugins"] = {}
                        estado.plugin_cache["plugins"][key] = sistema[key]
                    else:
                        # Eliminar del cache
                        estado.plugin_cache.get("plugins", {}).pop(key, None)

                    # Eliminar datos del sistema mientras está desactivado
                    sistema.pop(key, None)

                plugins[key] = False
                
                print(f"🔄 {key.capitalize()} ahora Inactivo")

            estado.cambios_no_guardados = True
        else:
            print("❌ Opción no válida.")





"""def menu_plugins():
    sistema = estado.sistema_actual

    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    plugins = sistema.setdefault("plugins_activos", {})

    while True:
        print(f"\n=== ADMINISTRAR PLUGINS (Sistema actual: {sistema.get('nombre_sistema', 'Sin nombre')}) ===")
        for i, plugin in enumerate(plugins, 1):
            estado_str = "✅ Activo" if plugins[plugin] else "❌ Inactivo"
            print(f"{i}. {plugin.capitalize()}: {estado_str}")
        print(f"{len(plugins)+1}. Continuar/Volver")

        try:
            opcion = int(input("\nElige un plugin para activar/desactivar: "))
        except ValueError:
            print("❌ Opción no válida.")
            continue

        if opcion == len(plugins) + 1:
            break
        elif 1 <= opcion <= len(plugins):
            key = list(plugins.keys())[opcion - 1]
            nuevo_estado = not plugins[key]

            plugin_obj = PLUGINS.get(key) if "PLUGINS" in globals() else None
            if "plugin_cache" not in estado.__dict__:
                estado.plugin_cache = {}

            if nuevo_estado:  # Activar
                plugins[key] = True
                # Restaurar datos si estaban en cache
                if key in estado.plugin_cache:
                    sistema[key] = estado.plugin_cache[key]
                elif plugin_obj and hasattr(plugin_obj, "on_enable"):
                    plugin_obj["on_enable"](sistema)

            else:  # Desactivar
                if key in sistema:
                    conservar = input("¿Conservar los datos del plugin? (s/n): ").lower() == "s"
                    if conservar:
                        estado.plugin_cache[key] = sistema[key]
                    else:
                        estado.plugin_cache.pop(key, None)
                    # Eliminar datos del sistema mientras está desactivado
                    sistema.pop(key, None)
                plugins[key] = False

            estado.cambios_no_guardados = True
            print(f"🔄 {key.capitalize()} ahora {'Activo' if plugins[key] else 'Inactivo'}")
        else:
            print("❌ Opción no válida.")"""