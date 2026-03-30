#core/menus
from core.estado_global import estado
from core.guardado.archivos import guardar_sistema, cargar_sistema, guardar_como

from core.administrar_puntos.menu_admin_puntos import menu_distribuir_puntos

from core.sistemas.crear_sistema import crear_nuevo_sistema
from core.utils.funciones_utiles import pedir_int
from core.sistemas.mostrar_sistema import que_ficha_queres
from core.plugins.registry import PLUGINS

from core.recompensas.ui_preparacion import (menu_configurar_recurso_dinamicos, menu_modificar_recursos_base, 
                                             menu_configurar_rarezas_dinamicas, menu_modificar_rarezas_base)

#Stats
from core.stats.stats import (mostrar_stats, mostrar_progress_stats_bar, 
                              modificar_stat_simples, modificar_stat_progress, 
                              agregar_stat_simple, agregar_progress_stat,
                              eliminar_stat_simple, eliminar_progress_stat)

#plugins
from plugins.inventario.menus_inv import (menu_agregar_item, mostrar_items,
                                          menu_modificar_item, menu_eliminar_item,
                                          seleccionar_item_inventario)

from plugins.misiones.menus_misiones import mostrar_misiones, menu_administrar_misiones

from plugins.niveles.menu_niveles import menu_configurar_niveles

from plugins.rachas.menus_rachas import mostrar_rachas, menu_administrar_rachas, configurar_rachas




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

# ------------------- MENÚS DE SISTEMA: MOSTRAR -------------------
def menu_mostrar(sistema):
    """
    Menú para mostrar información del sistema.
    Las opciones dependen de los plugins activos.
    """

    if not estado.sistema_actual:
        print("\n❌ No hay sistema cargado.")
        return

    plugins = sistema.get("plugins_activos", {})

    while True:
        print(f"\n=== SISTEMA DOC (Sistema actual: {sistema.get('nombre_sistema')}) ===")

        opciones = []

        # Stats y ficha base
        opciones.append(("Mostrar Stats", lambda: (
            mostrar_stats(sistema),
            mostrar_progress_stats_bar(sistema.get("progress_stats", {}))
        )))
        opciones.append(("Mostrar Ficha", lambda: que_ficha_queres(sistema)))

        # Inventario
        if plugins.get("inventario", False):
            opciones.append(("Mostrar Inventario", lambda: mostrar_items(sistema)))

        # Misiones activas
        if plugins.get("misiones", False):
            opciones.append(("Mostrar Misiones Activas", lambda: mostrar_misiones(sistema)))

        # Rachas
        if plugins.get("rachas", False):
            opciones.append(("Mostrar Rachas", lambda: mostrar_rachas(sistema)))

        # Menú numerado
        for i, (nombre, _) in enumerate(opciones, start=1):
            print(f"{i}. {nombre}")

        print(f"{len(opciones)+1}. Volver")

        opcion = pedir_int("\nElige una opción: ", default=len(opciones)+1)

        if 1 <= opcion <= len(opciones):
            _, funcion = opciones[opcion-1]
            funcion()
        else:
            break

# ------------------- MENÚS DE SISTEMA: MODIFICAR -------------------
def menu_modificar(sistema):
    """
    Menú para modificar elementos del sistema.
    Las opciones dependen de los plugins activos.
    """

    if not estado.sistema_actual:
        print("\n❌ No hay sistema cargado.")
        return

    plugins = sistema.get("plugins_activos", {})

    while True:
        print(f"\n=== SISTEMA DOC (Sistema actual: {sistema.get('nombre_sistema')}) ===")

        opciones = []

        # Stats base
        opciones.append(("Modificar Stats", lambda: menu_modificar_stats(sistema)))

        # Inventario
        if plugins.get("inventario", False):
            opciones.append(("Modificar Inventario", lambda: menu_modificar_items(sistema)))

        # Misiones
        if plugins.get("misiones", False):
            opciones.append(("Administrar Misiones", lambda: menu_administrar_misiones(sistema)))

        # Rachas
        if plugins.get("rachas", False):
            opciones.append(("Modificar Rachas", lambda: menu_administrar_rachas(sistema)))

        # Menú numerado
        for i, (nombre, _) in enumerate(opciones, start=1):
            print(f"{i}. {nombre}")

        print(f"{len(opciones)+1}. Volver")

        opcion = pedir_int("\nElige una opción: ", default=len(opciones)+1)

        if 1 <= opcion <= len(opciones):
            _, funcion = opciones[opcion-1]
            funcion()
            estado.cambios_no_guardados = True
        else:
            break

# ------------------- CONFIGURACION DEL SISTEMA -------------------
def configuracion(sistema):
    # Seguridad: no permitir entrar sin sistema cargado
    if not estado.sistema_actual:
        print("\n❌ No hay sistema cargado.")
        return

    while True:
        plugins = sistema.get("plugins_activos", {})

        print(f"\n=== SALIR/GUARDAR (Sistema actual: {sistema.get('nombre_sistema')}) ===")

        # Opciones del menú dinámico
        opciones = []

        opciones.append(("Guardar", guardar_sistema))

        opciones.append(("Configurar Sistema", lambda:configurar_sistema(sistema)))
        
        opciones.append(("Recursos", menu_configurar_recursos))

        opciones.append(("Rarezas", menu_configurar_rarezas))
        
        opciones.append(("Plugins", menu_plugins))

        if plugins.get("niveles", False):
            opciones.append(("Niveles", lambda: menu_configurar_niveles(sistema)))

        if plugins.get("rachas", False):
            opciones.append(("Configuración Rachas", lambda: configurar_rachas(sistema)))


        # Mostrar menú dinámico
        for i, (texto, _) in enumerate(opciones, start=1):
            print(f"{i}. {texto}")

        print(f"{len(opciones) + 1}. Salir\n")

        opcion = pedir_int("Elige una opción: ", default=len(opciones) + 1)

        if 1 <= opcion <= len(opciones):
            _, funcion = opciones[opcion - 1]
            funcion()
        else:
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
        print("4. Distribuir Puntos de Stats.")
        print("5. Volver.")

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

        elif opcion == 4:
            menu_distribuir_puntos(sistema)

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
            item_id = seleccionar_item_inventario(sistema)

            if not item_id:
                print("\nOperación cancelada.")
                continue

            cantidad = pedir_int("\nCantidad a eliminar:",
                                 default=0,
                                 minimo=0)
            if cantidad == 0:
                print("\nOperación cancelada.")
                continue

            menu_eliminar_item(sistema, item_id, cantidad)

        elif opcion == 4:
            mostrar_items()

        else:
            guardar_sistema()
            break

#------------------- ADMINISTRAR PLUGINS/MENU PLUGINS -------------------

def menu_plugins(autoguardar=True):
    sistema = estado.sistema_actual

    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    # Inicializar plugins activos en el sistema si no existen
    if "plugins_activos" not in sistema:
        sistema["plugins_activos"] = {}

    # Asegurarse de que todos los plugins de PLUGINS estén en plugins_activos
    for key in PLUGINS:
        if key not in sistema["plugins_activos"]:
            sistema["plugins_activos"][key] = False

    plugins = sistema["plugins_activos"]

    while True:
        print(f"\n=== ADMINISTRAR PLUGINS (Sistema actual: {sistema.get('nombre_sistema')}) ===")
        for i, key in enumerate(PLUGINS.keys(), 1):
            activo = plugins.get(key, False)
            estado_str = "✅ Activo" if activo else "❌ Inactivo"
            print(f"{i}. {PLUGINS[key]['nombre']}: {estado_str}")
        print(f"{len(PLUGINS)+1}. Continuar/Volver")

        try:
            opcion = int(input("\nElige un plugin para activar/desactivar: "))
        except ValueError:
            print("❌ Opción no válida.")
            continue

        if opcion == len(PLUGINS)+1:
            if autoguardar and estado.cambios_no_guardados:
                guardar_sistema()
            break
        elif 1 <= opcion <= len(PLUGINS):
            key = list(PLUGINS.keys())[opcion - 1]
            nuevo_estado = not plugins[key]

            plugin_obj = PLUGINS.get(key)
            if nuevo_estado:  # Activar plugin
                plugins[key] = True

                # Restaurar datos desde plugin_cache si existen
                if key in estado.plugin_cache.get("plugins", {}):
                    sistema[key] = estado.plugin_cache["plugins"][key].copy()
                elif plugin_obj and plugin_obj.get("on_enable"):
                    plugin_obj["on_enable"](sistema)

                print(f"🔄 {plugin_obj['nombre']} ahora Activo")

            else:  # Desactivar plugin
                if key in sistema:
                    conservar = input(f"¿Conservar los datos del plugin '{plugin_obj['nombre']}' para poder restaurarlos después? (s/n): ").lower() == "s"
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
                print(f"🔄 {plugin_obj['nombre']} ahora Inactivo")

            estado.cambios_no_guardados = True
        else:
            print("❌ Opción no válida.")

# ------------------- MODIFICAR Sistema(Nombre, Nombre del sistema, Original o fanfiction) -------------------

def configurar_sistema(sistema):
    """
    Permite modificar valores que normalmente solo se definen al crear el sistema:
    - Nombre del personaje
    - Edad del personaje
    - Nombre del sistema
    - Datos de la historia (tipo, sinopsis, personajes, parejas, fandom)
    """

    while True:
        print("\n=== CONFIGURAR SISTEMA ===")
        print(f"1. Nombre del personaje: {sistema['personaje'].get('nombre')}")
        print(f"2. Edad del personaje: {sistema['personaje'].get('edad')}")
        print(f"3. Nombre del sistema: {sistema.get('nombre_sistema')}")
        historia = sistema.get("historia", {})
        print(f"4. Tipo de historia: {historia.get('tipo')}")
        print("5. Modificar historia (sinopsis, personajes, parejas...)")
        print("6. Salir\n")

        opcion = input("Selecciona una opción (Enter para salir): ").strip()
        if opcion == "" or opcion == "6":
            guardar_sistema(print_msg=False)
            break

        if opcion == "1":
            nuevo_nombre = input(f"Nuevo nombre del personaje (Enter para mantener '{sistema['personaje']['nombre']}'): ").strip()
            if nuevo_nombre:
                sistema['personaje']['nombre'] = nuevo_nombre

        elif opcion == "2":
            nueva_edad = input(f"Nueva edad (Enter para mantener '{sistema['personaje']['edad']}'): ").strip()
            if nueva_edad:
                try:
                    sistema['personaje']['edad'] = int(nueva_edad)
                except ValueError:
                    print("❌ Edad inválida. No se modificó.")

        elif opcion == "3":
            nuevo_nombre_sistema = input(f"Nuevo nombre del sistema (Enter para mantener '{sistema.get('nombre_sistema')}'): ").strip()
            if nuevo_nombre_sistema:
                sistema['nombre_sistema'] = nuevo_nombre_sistema

        elif opcion == "4":
            while True:
                tipo = input("Nuevo tipo de historia: Original o Fanfiction (O/F, Enter para mantener): ").lower().strip()
                if tipo == "":
                    break
                if tipo in ("o", "f"):
                    historia.clear()
                    if tipo == "o":
                        historia["tipo"] = "original"
                        historia["sinopsis"] = input("Sinopsis: ")
                        historia["personajes_principales"] = input("Personajes principales: ")
                        historia["parejas"] = input("Parejas: ")
                    else:
                        historia["tipo"] = "fanfiction"
                        historia["fandom"] = input("Fandom: ")
                        historia["sinopsis"] = input("Sinopsis: ")
                        historia["personajes"] = input("Personajes: ")
                        historia["parejas"] = input("Parejas: ")
                    break
                else:
                    print("❌ Tipo inválido. Usa O o F.")

        elif opcion == "5":
            if historia.get("tipo") == "original":
                sinopsis = input(f"Sinopsis (Enter para mantener): ").strip()
                if sinopsis:
                    historia["sinopsis"] = sinopsis
                personajes = input(f"Personajes principales (Enter para mantener): ").strip()
                if personajes:
                    historia["personajes_principales"] = personajes
                parejas = input(f"Parejas (Enter para mantener): ").strip()
                if parejas:
                    historia["parejas"] = parejas

            elif historia.get("tipo") == "fanfiction":
                fandom = input(f"Fandom (Enter para mantener): ").strip()
                if fandom:
                    historia["fandom"] = fandom
                sinopsis = input(f"Sinopsis (Enter para mantener): ").strip()
                if sinopsis:
                    historia["sinopsis"] = sinopsis
                personajes = input(f"Personajes (Enter para mantener): ").strip()
                if personajes:
                    historia["personajes"] = personajes
                parejas = input(f"Parejas (Enter para mantener): ").strip()
                if parejas:
                    historia["parejas"] = parejas
            else:
                print("❌ Historia no definida.")

        else:
            print("❌ Opción inválida.")

    # Marcar cambios
    estado.cambios_no_guardados = True
    print("\n✅ Sistema configurado correctamente.\n")

# ------------------- MENU CONFIGURAR RECURSOS BASE/DINAMICOS -------------------

def menu_configurar_recursos():
    while True:
        print("\n=== CONFIGURACIÓN DE RECURSOS ===")
        print("1. Activar/Desactivar Recursos")
        print("2. Configurar recursos dinámicos")
        print("0. Volver")

        opcion = pedir_int("\nSelecciona opción:")

        if opcion == 1:
            menu_modificar_recursos_base()
        elif opcion == 2:
            menu_configurar_recurso_dinamicos()
        else:
            break

def menu_configurar_rarezas():
    while True:
        print("\n=== CONFIGURACIÓN DE RAREZAS ===")
        print("1. Activar/Desactivar Rarezas Base")
        print("2. Configurar rarezas dinámicas")
        print("0. Volver")

        opcion = pedir_int("\nSelecciona opción:")

        if opcion == 1:
            menu_modificar_rarezas_base()
        elif opcion == 2:
            menu_configurar_rarezas_dinamicas()
        else:
            break

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