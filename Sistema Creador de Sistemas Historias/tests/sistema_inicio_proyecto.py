import json
import os

# ---------------- VARIABLES GLOBALES ----------------

# Nombre del archivo que estamos editando actualmente
archivo_actual = None

# Indica si el sistema ha sido modificado desde el último guardado
cambios_no_guardados = False

# ---------------- FIN DE VARIABLES GLOBALES ----------------

####################################################################

# ---------------- CREACION SISTEMAS NUEVOS ----------------

# Función principal para crear un nuevo sistema/personaje
"""def crear_nuevo_sistema():
    # Diccionario principal donde se guarda TODO
    sistema = {}

    print("\n=== CREAR NUEVO SISTEMA / PERSONAJE ===\n")

    # ---------------- PERSONAJE ----------------
    sistema["personaje"] = {}
    sistema["personaje"]["nombre"] = input("¿Cuál es el nombre del personaje?: ")

    # ---------------- SISTEMA ----------------
    if input("¿Tiene nombre el sistema? (s/n): ").lower() == "s":
        sistema["nombre_sistema"] = input("Nombre del sistema: ")
    else:
        sistema["nombre_sistema"] = None

    # ---------------- STATS BASE ----------------
    print("\n--- STATS BASE ---")

    sistema["stats"] = {}

    # Stats obligatorios
    sistema["stats"]["Edad"] = int(input("Edad: "))
    sistema["stats"]["Nivel"] = int(input("Nivel: "))
    sistema["stats"]["Vida"] = int(input("Vida: "))
    sistema["stats"]["Ataque"] = int(input("Ataque: "))

    # Stats extra
    while input("¿Hay más stats? (s/n): ").lower() == "s":
        nombre = input("Nombre del stat: ")
        valor = int(input("Valor del stat: "))
        sistema["stats"][nombre] = valor

    # ---------------- INVENTARIO ----------------
    sistema["inventario"] = []

    if input("\n¿Tiene objetos en el inventario? (s/n): ").lower() == "s":
        while True:
            objeto = {
                "nombre": input("Nombre del objeto: "),
                "clase": input("Clase: "),
                "categoria": input("Categoría: "),
                "efectos": input("Efectos (texto): ")
            }
            sistema["inventario"].append(objeto)

            if input("¿Añadir otro objeto? (s/n): ").lower() != "s":
                break

    # ---------------- HABILIDADES ----------------
    sistema["habilidades"] = []

    if input("\n¿Tiene habilidades? (s/n): ").lower() == "s":
        while True:
            habilidad = {
                "nombre": input("Nombre: "),
                "tipo": input("Tipo: "),
                "descripcion": input("Descripción: "),
                "efectos": input("Efectos (texto): ")
            }
            sistema["habilidades"].append(habilidad)

            if input("¿Añadir otra habilidad? (s/n): ").lower() != "s":
                break

    # ---------------- TÍTULOS ----------------
    sistema["titulos"] = []

    if input("\n¿Tiene títulos? (s/n): ").lower() == "s":
        while True:
            titulo = {
                "nombre": input("Nombre del título: "),
                "descripcion": input("Descripción: "),
                "origen": input("Origen: "),
                "tipo": input("Tipo (pasivo/activo/etc): "),
                "efectos": {}  # 👈 efectos reales sobre stats
            }

            # Añadir efectos del título
            while input("¿Añadir efecto al título? (s/n): ").lower() == "s":
                stat = input("Stat afectado: ")
                valor = int(input("Valor (+ o -): "))
                titulo["efectos"][stat] = valor

            sistema["titulos"].append(titulo)

            if input("¿Añadir otro título? (s/n): ").lower() != "s":
                break

    # ---------------- MALDICIONES ----------------
    sistema["maldiciones"] = []

    if input("\n¿Tiene maldiciones? (s/n): ").lower() == "s":
        while True:
            maldicion = {
                "nombre": input("Nombre de la maldición: "),
                "descripcion": input("Descripción: "),
                "origen": input("Origen: "),
                "tipo": input("Tipo: "),
                "efectos": {}  # 👈 efectos negativos normalmente
            }

            while input("¿Añadir efecto a la maldición? (s/n): ").lower() == "s":
                stat = input("Stat afectado: ")
                valor = int(input("Valor (+ o -): "))
                maldicion["efectos"][stat] = valor

            sistema["maldiciones"].append(maldicion)

            if input("¿Añadir otra maldición? (s/n): ").lower() != "s":
                break

    # ---------------- HISTORIA ----------------
    sistema["historia"] = {}

    tipo = input("\n¿Original o Fanfiction?: ").lower()
    sistema["historia"]["tipo"] = tipo

    if tipo == "original":
        sistema["historia"]["sinopsis"] = input("Sinopsis: ")
        sistema["historia"]["personajes_principales"] = input("Personajes principales: ")
    else:
        sistema["historia"]["fandom"] = input("Fandom: ")
        sistema["historia"]["sinopsis"] = input("Sinopsis: ")
        sistema["historia"]["personajes"] = input("Personajes: ")
        sistema["historia"]["parejas"] = input("Parejas: ")

    # ---------------- LINEA TEMPORAL ----------------
    sistema["linea_temporal"] = []

    return sistema"""

"""def mostrar_stats_completos(sistema):
    
    Muestra los stats base, los efectos de títulos y maldiciones, y el total.
    
    print("\n📊 STATS COMPLETOS\n")

    # Calculamos los efectos totales de títulos y maldiciones
    efectos_totales = {}  # diccionario con los efectos combinados

    # Sumamos efectos de títulos
    for t in sistema["titulos"]:
        for stat, valor in t.get("efectos", {}).items():
            efectos_totales[stat] = efectos_totales.get(stat, 0) + valor

    # Sumamos efectos de maldiciones
    for m in sistema["maldiciones"]:
        for stat, valor in m.get("efectos", {}).items():
            efectos_totales[stat] = efectos_totales.get(stat, 0) + valor

    # Mostramos stats
    for stat, base in sistema["stats"].items():
        base_valor = int(base)
        efecto = efectos_totales.get(stat, 0)
        total = base_valor + efecto
        if efecto != 0:
            print(f"- {stat}: {base_valor} + ({efecto}) = {total}")
        else:
            print(f"- {stat}: {base_valor}")"""

# Función para mostrar la ficha completa del sistema
"""def mostrar_ficha(sistema):

    print("\n\n===== FICHA DEL SISTEMA =====\n")

    # Mostramos nombre del personaje
    print(f"Personaje: {sistema['personaje']['nombre']}")

    # Mostramos el nombre del sistema solo si existe
    if sistema["nombre_sistema"]:
        print(f"Sistema: {sistema['nombre_sistema']}")

    # Mostramos los stats
    print("\nSTATS:")
    mostrar_stats_completos(sistema)

    # Mostramos el inventario
    print("\nINVENTARIO:")
    for obj in sistema["inventario"]:
        print(f"- {obj['nombre']} ({obj['categoria']})")

    # Mostramos las habilidades
    print("\nHABILIDADES:")
    for h in sistema["habilidades"]:
        print(f"- {h['nombre']} ({h['tipo']})")

    # Mostramos los títulos
    print("\nTÍTULOS:")
    for t in sistema["titulos"]:
        print(f"- {t['nombre']}")

    # Mostramos las maldiciones
    print("\nMALDICIONES:")
    for m in sistema["maldiciones"]:
        print(f"- {m['nombre']}")

    # Mostramos los datos de la historia
    print("\nHISTORIA:")
    for clave, valor in sistema["historia"].items():
        print(f"{clave}: {valor}")"""

# ---------------- FIN DE CREACION SISTEMAS NUEVOS ----------------

####################################################################

# ---------------- INVENTARIO EDITABLE ----------------

# Función para mostrar el inventario completo
"""def mostrar_inventario(sistema):
    print("\n📦 INVENTARIO\n")

    # Si no hay objetos
    if not sistema["inventario"]:
        print("El inventario está vacío.")
        return

    # Mostramos cada objeto con un número
    for i, obj in enumerate(sistema["inventario"], 1):
        print(f"{i}. {obj['nombre']}")
        print(f"   Clase: {obj['clase']}")
        print(f"   Categoría: {obj['categoria']}")
        print(f"   Efectos: {obj['efectos']}\n")"""

# Función para añadir un objeto nuevo al inventario
"""def añadir_objeto(sistema):
    print("\n➕ AÑADIR OBJETO\n")

    # Creamos el objeto como diccionario
    objeto = {
        "nombre": input("Nombre del objeto: "),
        "clase": input("Clase: "),
        "categoria": input("Categoría: "),
        "efectos": input("Efectos: ")
    }

    # Lo añadimos a la lista de inventario
    sistema["inventario"].append(objeto)
    global cambios_no_guardados
    cambios_no_guardados = True


    print("✅ Objeto añadido al inventario.")"""

# Función para eliminar un objeto del inventario
"""def eliminar_objeto(sistema):
    print("\n❌ ELIMINAR OBJETO\n")

    # Si no hay objetos, no hacemos nada
    if not sistema["inventario"]:
        print("El inventario está vacío.")
        return

    # Mostramos los objetos numerados
    for i, obj in enumerate(sistema["inventario"], 1):
        print(f"{i}. {obj['nombre']}")

    # Pedimos cuál quiere borrar
    try:
        indice = int(input("Número del objeto a eliminar: ")) - 1

        # Comprobamos que el número sea válido
        if 0 <= indice < len(sistema["inventario"]):
            eliminado = sistema["inventario"].pop(indice)
            global cambios_no_guardados
            cambios_no_guardados = True

            print(f"🗑️ Objeto eliminado: {eliminado['nombre']}")
        else:
            print("❌ Número inválido.")

    except ValueError:
        print("❌ Debes introducir un número.")"""

# Menú para gestionar el inventario
"""def menu_inventario(sistema):
    while True:
        print("\n=== MENÚ DE INVENTARIO ===")
        print("1. Ver inventario")
        print("2. Añadir objeto")
        print("3. Eliminar objeto")
        print("4. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_inventario(sistema)

        elif opcion == "2":
            añadir_objeto(sistema)

        elif opcion == "3":
            eliminar_objeto(sistema)

        elif opcion == "4":
            break

        else:
            print("❌ Opción no válida.")"""

# ---------------- FIN DE INVENTARIO EDITABLE ----------------

####################################################################

# ---------------- STATS EDITABLES ----------------

# Mostrar los stats actuales
"""def mostrar_stats(sistema):
    print("\n📊 STATS ACTUALES\n")
    for stat, valor in sistema["stats"].items():
        print(f"- {stat}: {valor}")"""

# Modificar un stat existente
"""def modificar_stat(sistema):
    print("\n✏️ MODIFICAR STAT\n")

    # Mostramos los stats disponibles
    mostrar_stats(sistema)

    stat = input("\nNombre del stat a modificar: ")

    # Comprobamos que el stat exista
    if stat not in sistema["stats"]:
        print("❌ Ese stat no existe.")
        return

    try:
        cambio = int(input("Cantidad a sumar/restar (ej: -10 o 5): "))
    except ValueError:
        print("❌ Debes introducir un número.")
        return

    # Modificamos el stat
    sistema["stats"][stat] = int(sistema["stats"][stat]) + cambio
    global cambios_no_guardados
    cambios_no_guardados = True

    print(f"✅ {stat} modificado correctamente.")"""

# Menú para gestionar stats
"""def menu_stats(sistema):
    while True:
        print("\n=== MENÚ DE STATS ===")
        print("1. Ver stats")
        print("2. Modificar stat")
        print("3. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_stats(sistema)

        elif opcion == "2":
            modificar_stat(sistema)

        elif opcion == "3":
            break

        else:
            print("❌ Opción no válida.")
"""
# ---------------- FIN DE STATS EDITABLES ----------------

####################################################################

# ---------------- LÍNEA TEMPORAL ----------------

# Añadir un capítulo a la línea temporal
"""def añadir_capitulo(sistema):

    # Seguridad: si no existe la línea temporal, la creamos
    if "linea_temporal" not in sistema:
        sistema["linea_temporal"] = []

    print("\n📖 NUEVO CAPÍTULO\n")

    titulo = input("Título del capítulo: ")
    resumen = input("Resumen / qué ocurrió: ")

    capitulo = {
        "titulo": titulo,
        "resumen": resumen
    }

    sistema["linea_temporal"].append(capitulo)
    global cambios_no_guardados
    cambios_no_guardados = True


    print("✅ Capítulo añadido a la línea temporal.")"""

# Modificar un capítulo
"""def modificar_capitulo(sistema):
    if not sistema["linea_temporal"]:
        print("❌ No hay capítulos para modificar.")
        return

    # Mostramos la lista de capítulos
    mostrar_linea_temporal(sistema)

    try:
        indice = int(input("Número del capítulo a modificar: ")) - 1
        if 0 <= indice < len(sistema["linea_temporal"]):
            capitulo = sistema["linea_temporal"][indice]

            print(f"\nCapítulo seleccionado: {capitulo['titulo']}")
            nuevo_titulo = input("Nuevo título (enter para mantener): ")
            nuevo_resumen = input("Nuevo resumen (enter para mantener): ")

            if nuevo_titulo:
                capitulo["titulo"] = nuevo_titulo
            if nuevo_resumen:
                capitulo["resumen"] = nuevo_resumen

            global cambios_no_guardados
            cambios_no_guardados = True

            print("✅ Capítulo modificado correctamente.")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")"""

# Borrar un capítulo
"""def borrar_capitulo(sistema):
    if not sistema["linea_temporal"]:
        print("❌ No hay capítulos para borrar.")
        return

    # Mostramos la lista de capítulos
    mostrar_linea_temporal(sistema)

    try:
        indice = int(input("Número del capítulo a eliminar: ")) - 1
        if 0 <= indice < len(sistema["linea_temporal"]):
            capitulo = sistema["linea_temporal"].pop(indice)

            global cambios_no_guardados
            cambios_no_guardados = True

            print(f"🗑️ Capítulo eliminado: {capitulo['titulo']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")"""

# Mostrar la línea temporal completa
"""def mostrar_linea_temporal(sistema):
    print("\n📚 LÍNEA TEMPORAL\n")

    if not sistema["linea_temporal"]:
        print("No hay capítulos todavía.")
        return

    for i, cap in enumerate(sistema["linea_temporal"], 1):
        print(f"{i}. {cap['titulo']}")
        print(f"   {cap['resumen']}\n")"""

# Menú de historia / capítulos
"""def menu_historia(sistema):
    while True:
        print("\n=== MENÚ DE HISTORIA / CAPÍTULOS ===")
        print("1. Añadir capítulo")
        print("2. Modificar capítulo")
        print("3. Borrar capítulo")
        print("4. Ver línea temporal")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            añadir_capitulo(sistema)
        elif opcion == "2":
            modificar_capitulo(sistema)
        elif opcion == "3":
            borrar_capitulo(sistema)
        elif opcion == "4":
            mostrar_linea_temporal(sistema)
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida.")"""

# ---------------- FIN DE LÍNEA TEMPORAL ----------------

####################################################################

# ---------------- TIPOS GUARDADOS  ----------------

# Función para guardar el sistema en un archivo
"""def guardar_sistema(sistema):
    global archivo_actual  # usamos la variable global

    if archivo_actual:
        # Si ya hay un archivo cargado, sobrescribimos directamente
        nombre_archivo = archivo_actual
    else:
        # Si es un sistema nuevo, pedimos nombre
        nombre_archivo = input("Nombre del archivo para guardar (ej: sistema.json): ")

    # Guardamos el sistema en JSON
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(sistema, archivo, indent=4, ensure_ascii=False)
        global cambios_no_guardados
        cambios_no_guardados = False
    archivo_actual = nombre_archivo  # actualizamos el puntero
    print(f"✅ Sistema guardado correctamente en '{nombre_archivo}'")"""

# Función para cargar un sistema desde un archivo
"""def cargar_sistema():
    global archivo_actual # usamos variable global
    nombre_archivo = input("Nombre del archivo a cargar: ")

    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        sistema = json.load(archivo)

    # --- COMPATIBILIDAD CON SISTEMAS ANTIGUOS ---
    # Si no existe la línea temporal, la creamos
    if "linea_temporal" not in sistema:
        sistema["linea_temporal"] = []
    
    archivo_actual = nombre_archivo # apuntamos al archivo cargado
    print(f"✅ Sistema cargado correctamente desde '{nombre_archivo}'")
    return sistema"""

# Función para guardar un sistema nuevo desde otro
"""def guardar_como(sistema):
    global archivo_actual
    global cambios_no_guardados
    nombre_archivo = input("Nombre del nuevo archivo para guardar este sistema: ")

    # Comprobamos si el archivo ya existe
    if os.path.exists(nombre_archivo):
        print(f"❗ El archivo '{nombre_archivo}' ya existe.")
        print("1. Sobrescribir")
        print("2. Cancelar / Volver")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            # Sobrescribimos
            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                json.dump(sistema, archivo, indent=4, ensure_ascii=False)
            archivo_actual = nombre_archivo
            print(f"✅ Archivo sobrescrito correctamente: '{nombre_archivo}'")
            global cambios_no_guardados
            cambios_no_guardados = False


        elif opcion == "2":
            print("⚠️ Operación cancelada. No se ha guardado.")
            return

        else:
            print("❌ Opción no válida. Operación cancelada.")
            return

    else:
        # Si no existe, simplemente guardamos
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(sistema, archivo, indent=4, ensure_ascii=False)
        archivo_actual = nombre_archivo
        print(f"✅ Sistema guardado como '{nombre_archivo}'")
        cambios_no_guardados = False"""

# ---------------- FIN DE TIPOS GUARDADOS  ----------------

####################################################################

# ---------------- HABILIDADES ----------------

"""def mostrar_habilidades(sistema):
    
    Muestra todas las habilidades del sistema con detalles.
    
    print("\n🛡️ HABILIDADES DEL PERSONAJE\n")

    # Si no hay habilidades, informamos
    if not sistema["habilidades"]:
        print("No hay habilidades aún.")
        return

    # Enumeramos todas las habilidades
    for i, h in enumerate(sistema["habilidades"], 1):
        print(f"{i}. {h['nombre']}")
        print(f"   Tipo: {h['tipo']}")
        print(f"   Descripción: {h.get('descripcion', '')}")
        print(f"   Efectos: {h['efectos']}\n")"""

"""def añadir_habilidad(sistema):
    
    Permite añadir una nueva habilidad al personaje.
    
    print("\n➕ AÑADIR HABILIDAD\n")

    # Creamos un diccionario con los datos de la habilidad
    habilidad = {
        "nombre": input("Nombre de la habilidad: "),       # Nombre
        "tipo": input("Tipo de habilidad: "),             # Tipo
        "descripcion": input("Descripción: "),            # Descripción detallada
        "efectos": input("Efectos: ")                     # Efectos sobre stats u otros
    }

    # Añadimos la habilidad a la lista de habilidades
    sistema["habilidades"].append(habilidad)

    # Marcamos el sistema como modificado
    global cambios_no_guardados
    cambios_no_guardados = True

    print("✅ Habilidad añadida correctamente.")"""

"""def modificar_habilidad(sistema):
    
    Permite modificar una habilidad existente.
    
    if not sistema["habilidades"]:
        print("❌ No hay habilidades para modificar.")
        return

    # Mostramos las habilidades actuales
    mostrar_habilidades(sistema)

    try:
        # Pedimos el número de la habilidad a modificar
        indice = int(input("Número de la habilidad a modificar: ")) - 1

        # Verificamos que el número sea válido
        if 0 <= indice < len(sistema["habilidades"]):
            h = sistema["habilidades"][indice]

            print(f"\nHabilidad seleccionada: {h['nombre']}")

            # Permitimos cambiar cada campo; si se deja vacío, se mantiene el valor actual
            nuevo_nombre = input("Nuevo nombre (enter para mantener): ")
            nuevo_tipo = input("Nuevo tipo (enter para mantener): ")
            nueva_descripcion = input("Nueva descripción (enter para mantener): ")
            nuevos_efectos = input("Nuevos efectos (enter para mantener): ")

            if nuevo_nombre:
                h["nombre"] = nuevo_nombre
            if nuevo_tipo:
                h["tipo"] = nuevo_tipo
            if nueva_descripcion:
                h["descripcion"] = nueva_descripcion
            if nuevos_efectos:
                h["efectos"] = nuevos_efectos

            # Marcamos cambios
            global cambios_no_guardados
            cambios_no_guardados = True

            print("✅ Habilidad modificada correctamente.")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")"""

"""def eliminar_habilidad(sistema):
    
    Permite eliminar una habilidad existente.
    
    if not sistema["habilidades"]:
        print("❌ No hay habilidades para eliminar.")
        return

    # Mostramos las habilidades actuales
    mostrar_habilidades(sistema)

    try:
        # Pedimos el número de la habilidad a eliminar
        indice = int(input("Número de la habilidad a eliminar: ")) - 1

        if 0 <= indice < len(sistema["habilidades"]):
            h = sistema["habilidades"].pop(indice)

            # Marcamos cambios
            global cambios_no_guardados
            cambios_no_guardados = True

            print(f"🗑️ Habilidad eliminada: {h['nombre']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")"""

"""def menu_habilidades(sistema):
    
    Menú interactivo para gestionar las habilidades del sistema.
    
    while True:
        print("\n=== MENÚ DE HABILIDADES ===")
        print("1. Ver habilidades")
        print("2. Añadir habilidad")
        print("3. Modificar habilidad")
        print("4. Eliminar habilidad")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_habilidades(sistema)
        elif opcion == "2":
            añadir_habilidad(sistema)
        elif opcion == "3":
            modificar_habilidad(sistema)
        elif opcion == "4":
            eliminar_habilidad(sistema)
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida.")"""

# ---------------- FIN DE HABILIDADES ----------------

####################################################################

# ---------------- TITULOS ----------------

"""def añadir_titulo(sistema):
    
    Permite añadir un nuevo título al personaje.
    
    print("\n➕ AÑADIR TÍTULO\n")

    # Creamos el diccionario con todos los campos
    titulo = {
        "nombre": input("Nombre del título: "),
        "descripcion": input("Descripción: "),
        "origen": input("Origen del título: "),
        "tipo": input("Tipo de título: "),
        # Pedimos efectos de forma sencilla: usuario puede escribir "Ataque:7,Vida:10"
        "efectos": {}
    }

    efectos_input = input("Efectos sobre stats (ej: Ataque:7,Vida:10): ")
    # Convertimos en diccionario
    for parte in efectos_input.split(","):
        if ":" in parte:
            stat, valor = parte.split(":")
            try:
                titulo["efectos"][stat.strip()] = int(valor.strip())
            except ValueError:
                print(f"⚠️ Ignorado efecto inválido: {parte}")

    # Añadimos el título
    sistema["titulos"].append(titulo)

    global cambios_no_guardados
    cambios_no_guardados = True

    print(f"✅ Título '{titulo['nombre']}' añadido correctamente.")"""

"""def modificar_titulo(sistema):
    
    Permite modificar un título existente.
    
    if not sistema["titulos"]:
        print("❌ No hay títulos para modificar.")
        return

    # Mostramos títulos numerados
    for i, t in enumerate(sistema["titulos"], 1):
        print(f"{i}. {t['nombre']} ({t['tipo']})")

    try:
        indice = int(input("Número del título a modificar: ")) - 1
        if 0 <= indice < len(sistema["titulos"]):
            t = sistema["titulos"][indice]

            print(f"\nTítulo seleccionado: {t['nombre']}")
            nuevo_nombre = input("Nuevo nombre (enter para mantener): ")
            nueva_descripcion = input("Nueva descripción (enter para mantener): ")
            nuevo_origen = input("Nuevo origen (enter para mantener): ")
            nuevo_tipo = input("Nuevo tipo (enter para mantener): ")
            nuevos_efectos = input("Nuevos efectos (ej: Ataque:7,Vida:10, enter para mantener): ")

            if nuevo_nombre:
                t["nombre"] = nuevo_nombre
            if nueva_descripcion:
                t["descripcion"] = nueva_descripcion
            if nuevo_origen:
                t["origen"] = nuevo_origen
            if nuevo_tipo:
                t["tipo"] = nuevo_tipo
            if nuevos_efectos:
                t["efectos"] = {}
                for parte in nuevos_efectos.split(","):
                    if ":" in parte:
                        stat, valor = parte.split(":")
                        try:
                            t["efectos"][stat.strip()] = int(valor.strip())
                        except ValueError:
                            print(f"⚠️ Ignorado efecto inválido: {parte}")

            global cambios_no_guardados
            cambios_no_guardados = True

            print("✅ Título modificado correctamente.")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")"""

"""def eliminar_titulo(sistema):
    
    Permite eliminar un título existente.
    
    if not sistema["titulos"]:
        print("❌ No hay títulos para eliminar.")
        return

    for i, t in enumerate(sistema["titulos"], 1):
        print(f"{i}. {t['nombre']} ({t['tipo']})")

    try:
        indice = int(input("Número del título a eliminar: ")) - 1
        if 0 <= indice < len(sistema["titulos"]):
            t = sistema["titulos"].pop(indice)

            global cambios_no_guardados
            cambios_no_guardados = True

            print(f"🗑️ Título eliminado: {t['nombre']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")"""

"""def menu_titulos(sistema):
    
    Menú interactivo para gestionar los títulos del sistema.
    
    while True:
        print("\n=== MENÚ DE TÍTULOS ===")
        print("1. Ver títulos")
        print("2. Añadir título")
        print("3. Modificar título")
        print("4. Eliminar título")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            # Mostramos títulos
            if not sistema["titulos"]:
                print("No hay títulos.")
            else:
                for t in sistema["titulos"]:
                    print(f"- {t['nombre']} ({t['tipo']}): {t['descripcion']}, Origen: {t['origen']}, Efectos: {t.get('efectos',{})}")
        elif opcion == "2":
            añadir_titulo(sistema)
        elif opcion == "3":
            modificar_titulo(sistema)
        elif opcion == "4":
            eliminar_titulo(sistema)
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida.")"""

# ---------------- FIN DE TITULOS ----------------

####################################################################

# ---------------- MALDICIONES ----------------

"""def añadir_maldicion(sistema):
    
    Permite añadir una nueva maldición al personaje.
    
    print("\n➕ AÑADIR MALDICIÓN\n")

    # Creamos el diccionario con todos los campos
    maldicion = {
        "nombre": input("Nombre de la maldición: "),
        "descripcion": input("Descripción: "),
        "origen": input("Origen de la maldición: "),
        "tipo": input("Tipo de maldición: "),
        # Pedimos efectos de forma sencilla: usuario puede escribir "Ataque:-3,Vida:-10"
        "efectos": {}
    }

    efectos_input = input("Efectos sobre stats (ej: Ataque:-3,Vida:-10): ")
    # Convertimos en diccionario
    for parte in efectos_input.split(","):
        if ":" in parte:
            stat, valor = parte.split(":")
            try:
                maldicion["efectos"][stat.strip()] = int(valor.strip())
            except ValueError:
                print(f"⚠️ Ignorado efecto inválido: {parte}")

    # Añadimos la maldición
    sistema["maldiciones"].append(maldicion)

    global cambios_no_guardados
    cambios_no_guardados = True

    print(f"✅ Maldición '{maldicion['nombre']}' añadida correctamente.")"""

"""def modificar_maldicion(sistema):
    
    Permite modificar una maldición existente.
    
    if not sistema["maldiciones"]:
        print("❌ No hay maldiciones para modificar.")
        return

    # Mostramos maldiciones numeradas
    for i, m in enumerate(sistema["maldiciones"], 1):
        print(f"{i}. {m['nombre']} ({m['tipo']})")

    try:
        indice = int(input("Número de la maldición a modificar: ")) - 1
        if 0 <= indice < len(sistema["maldiciones"]):
            m = sistema["maldiciones"][indice]

            print(f"\nMaldición seleccionada: {m['nombre']}")
            nuevo_nombre = input("Nuevo nombre (enter para mantener): ")
            nueva_descripcion = input("Nueva descripción (enter para mantener): ")
            nuevo_origen = input("Nuevo origen (enter para mantener): ")
            nuevo_tipo = input("Nuevo tipo (enter para mantener): ")
            nuevos_efectos = input("Nuevos efectos (ej: Ataque:-3,Vida:-10, enter para mantener): ")

            if nuevo_nombre:
                m["nombre"] = nuevo_nombre
            if nueva_descripcion:
                m["descripcion"] = nueva_descripcion
            if nuevo_origen:
                m["origen"] = nuevo_origen
            if nuevo_tipo:
                m["tipo"] = nuevo_tipo
            if nuevos_efectos:
                m["efectos"] = {}
                for parte in nuevos_efectos.split(","):
                    if ":" in parte:
                        stat, valor = parte.split(":")
                        try:
                            m["efectos"][stat.strip()] = int(valor.strip())
                        except ValueError:
                            print(f"⚠️ Ignorado efecto inválido: {parte}")

            global cambios_no_guardados
            cambios_no_guardados = True

            print("✅ Maldición modificada correctamente.")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")"""

"""def eliminar_maldicion(sistema):
    
    Permite eliminar una maldición existente.
    
    if not sistema["maldiciones"]:
        print("❌ No hay maldiciones para eliminar.")
        return

    for i, m in enumerate(sistema["maldiciones"], 1):
        print(f"{i}. {m['nombre']} ({m['tipo']})")

    try:
        indice = int(input("Número de la maldición a eliminar: ")) - 1
        if 0 <= indice < len(sistema["maldiciones"]):
            m = sistema["maldiciones"].pop(indice)

            global cambios_no_guardados
            cambios_no_guardados = True

            print(f"🗑️ Maldición eliminada: {m['nombre']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")"""

"""def menu_maldiciones(sistema):
    
    Menú interactivo para gestionar las maldiciones del sistema.
    
    while True:
        print("\n=== MENÚ DE MALDICIONES ===")
        print("1. Ver maldiciones")
        print("2. Añadir maldición")
        print("3. Modificar maldición")
        print("4. Eliminar maldición")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            if not sistema["maldiciones"]:
                print("No hay maldiciones.")
            else:
                for m in sistema["maldiciones"]:
                    print(f"- {m['nombre']} ({m['tipo']}): {m['descripcion']}, Origen: {m['origen']}, Efectos: {m.get('efectos',{})}")
        elif opcion == "2":
            añadir_maldicion(sistema)
        elif opcion == "3":
            modificar_maldicion(sistema)
        elif opcion == "4":
            eliminar_maldicion(sistema)
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida.")"""

# ---------------- FIN DE MALDICIONES ----------------

####################################################################

"""def salir_programa():
    
    if cambios_no_guardados:
        print("⚠️ Hay cambios no guardados.")
        print("1. Guardar y salir")
        print("2. Salir sin guardar")
        print("3. Cancelar")

        opcion_salir = input("Elige una opción: ")

        if opcion_salir == "1":
            try:
                guardar_sistema(sistema_actual)
            except NameError:
                print("❌ No hay sistema cargado para guardar.")
            return True  # salir

        elif opcion_salir == "2":
            print("Saliendo del sistema...")
            return True  # salir sin guardar

        elif opcion_salir == "3":
            return False  # cancelar salida

        else:
            print("❌ Opción no válida. Cancelando salida.")
            return False

    else:
        print("Saliendo del sistema...")
        return True"""

# ---------------- EJECUCIÓN DEL PROGRAMA ----------------
#     ---------------- MENÚ PRINCIPAL ----------------

# ---------------- MENÚ PRINCIPAL ----------------

"""while True:
    print("\n=== SISTEMA DOC ===")
    print("1. Crear Nuevo Sistema/Personaje")
    print("2. Cargar Sistema/Personaje")
    print("3. Guardar Sistema Actual")
    print("4. Guardar Como / Crear Nuevo Sistema Desde Este")
    print("5. Gestionar Inventario")
    print("6. Gestionar Stats")
    print("7. Historia / Capítulos")
    print("8. Gestionar Títulos")
    print("9. Gestionar Maldiciones")
    print("10. Salir")

    opcion = input("Elige una opción: ")

    # Opción 1: crear sistema nuevo
    if opcion == "1":
        sistema_actual = crear_nuevo_sistema()
        mostrar_ficha(sistema_actual)

        if input("\n¿Deseas guardar este sistema? (s/n): ").lower() == "s":
            guardar_sistema(sistema_actual)

    # Opción 2: cargar sistema existente
    elif opcion == "2":
        sistema_actual = cargar_sistema()
        mostrar_ficha(sistema_actual)
    
    # Opción 3: Guardar Sistema Cargado
    elif opcion == "3":
        try:
            guardar_sistema(sistema_actual)
        except NameError:
            print("❌ No hay ningún sistema cargado para guardar.")

    # Opción 4: Guardar Como / Crear Nuevo Sistema Desde Este
    elif opcion == "4":
        try:
            guardar_como(sistema_actual)
        except NameError:
            print("❌ No hay ningún sistema cargado para guardar.")

    # Opción 5: Gestion Inventario
    elif opcion == "5":
        try:
            menu_inventario(sistema_actual)
        except NameError:
            print("❌ No hay ningún sistema cargado.")

    # Opción 6: Gestion Stats
    elif opcion == "6":
        try:
            menu_stats(sistema_actual)
        except NameError:
            print("❌ No hay ningún sistema cargado.")

    # Opción 7: Historia / capitulos
    elif opcion == "7":
        try:
            menu_historia(sistema_actual)
        except NameError:
            print("❌ No hay ningún sistema cargado.")

    # Opción 8: Gestionar Títulos
    elif opcion == "8":
        try:
            menu_titulos(sistema_actual)
        except NameError:
            print("❌ No hay ningún sistema cargado.")

    # Opción 9: Gestionar Maldiciones
    elif opcion == "9":
        try:
            menu_maldiciones(sistema_actual)
        except NameError:
            print("❌ No hay ningún sistema cargado.")

    # Opción 10: Salir
    elif opcion == "10":
        if salir_programa():  # Suponiendo que esta función ya gestiona cambios no guardados
            break

    # Opción inválida
    else:
        print("❌ Opción no válida.")"""
