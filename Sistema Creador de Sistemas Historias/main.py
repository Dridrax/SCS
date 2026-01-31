from core.estado_global import estado
from core.sistemas.crear_sistema import crear_nuevo_sistema
from core.sistemas.mostrar_sistema import mostrar_ficha, mostrar_stats_completos
from core.guardado.archivos import guardar_sistema, cargar_sistema, guardar_como
from core.utils.salida import salir_programa
from core.stats.stats import menu_stats, mostrar_stats
from core.historia.linea_temporal import menu_historia, mostrar_linea_temporal
from core.utils.exportar_pdf import exportar_ficha_pdf

# Plugins
from plugins.inventario.inventario import menu_inventario, mostrar_inventario
from plugins.titulos.titulos import menu_titulos, mostrar_titulos
from plugins.bendiciones.bendiciones import menu_bendiciones, mostrar_bendiciones
from plugins.maldiciones.maldiciones import menu_maldiciones, mostrar_maldiciones

# ------------------- MENÚ PRINCIPAL -------------------
def menu_principal():
    while True:
        nombre_sistema = estado.sistema_actual.get("nombre_sistema") if estado.sistema_actual else "Sin sistema cargado"
        print(f"\n=== SISTEMA DOC (Sistema actual: {nombre_sistema}) ===")
        print("1. Crear / Cargar Sistema")
        print("2. Guardar Sistema")
        print("3. Gestión del Sistema")
        print("4. Exportar Ficha a PDF")
        print("5. Ver Ficha del Sistema")  # Nueva opción
        print("6. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            menu_crear_cargar()
        elif opcion == "2":
            menu_guardado()
        elif opcion == "3":
            if estado.sistema_actual:
                menu_gestion_sistema()
            else:
                print("❌ No hay ningún sistema cargado.")
        elif opcion == "4":
            if estado.sistema_actual:
                exportar_ficha_pdf(estado.sistema_actual)
            else:
                print("❌ No hay ningún sistema cargado.")
        elif opcion == "5":  # Nueva opción
            if estado.sistema_actual:
                mostrar_ficha(estado.sistema_actual)
            else:
                print("❌ No hay ningún sistema cargado.")
        elif opcion == "6":
            if salir_programa():
                break
        else:
            print("❌ Opción no válida.")


# ------------------- CREAR / CARGAR -------------------
def menu_crear_cargar():
    while True:
        print("\n=== CREAR / CARGAR ===")
        print("1. Crear Nuevo Sistema/Personaje")
        print("2. Cargar Sistema/Personaje")
        print("3. Volver")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            # Plugins disponibles
            print("\n=== PLUGINS DISPONIBLES ===")
            plugins_activos = {}
            for plugin in ["inventario", "habilidades", "bendiciones", "maldiciones", "titulos"]:
                respuesta = input(f"¿Activar plugin {plugin}? (s/n): ").lower()
                plugins_activos[plugin] = respuesta == "s"

            # Crear sistema
            sistema = crear_nuevo_sistema(plugins_activos)
            sistema["plugins_activos"] = plugins_activos
            estado.sistema_actual = sistema
            estado.archivo_actual = None
            mostrar_ficha(estado.sistema_actual)

            if input("\n¿Deseas guardar este sistema? (s/n): ").lower() == "s":
                guardar_sistema()

        elif opcion == "2":
            archivo = input("Nombre del archivo a cargar: ")
            sistema = cargar_sistema(archivo)
            if sistema:
                # Normalización de sistemas antiguos
                for clave in ["inventario", "habilidades", "titulos", "bendiciones", "maldiciones", "linea_temporal", "historia"]:
                    sistema.setdefault(clave, [] if clave != "historia" else {})
                sistema.setdefault("plugins_activos", {k: True for k in ["inventario", "habilidades", "bendiciones", "maldiciones", "titulos"]})
                estado.sistema_actual = sistema
                mostrar_ficha(estado.sistema_actual)
        elif opcion == "3":
            break
        else:
            print("❌ Opción no válida.")

# ------------------- GUARDADO -------------------
def menu_guardado():
    if not estado.sistema_actual:
        print("❌ No hay ningún sistema cargado.")
        return
    while True:
        print("\n=== GUARDAR SISTEMA ===")
        print("1. Guardar")
        print("2. Guardar Como")
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

# ------------------- GESTIÓN DEL SISTEMA -------------------
def menu_gestion_sistema():
    sistema = estado.sistema_actual
    plugins = sistema.get("plugins_activos", {})

    while True:
        nombre = sistema.get("nombre_sistema", "Sin sistema")
        print(f"\n=== GESTIÓN DEL SISTEMA ({nombre}) ===")
        opciones = []

        if plugins.get("inventario", False):
            opciones.append("Inventario")
        opciones.append("Stats")
        if any([plugins.get("titulos", False), plugins.get("bendiciones", False), plugins.get("maldiciones", False)]):
            opciones.append("Títulos / Bendiciones / Maldiciones")
        opciones.append("Historia / Capítulos")
        opciones.append("Cambiar Parámetros (modificar)")
        opciones.append("Volver")

        for i, op in enumerate(opciones, start=1):
            print(f"{i}. {op}")

        try:
            opcion_num = int(input("Elige una opción: "))
        except ValueError:
            print("❌ Opción no válida.")
            continue

        if opcion_num < 1 or opcion_num > len(opciones):
            print("❌ Opción no válida.")
            continue

        seleccion = opciones[opcion_num-1]

        if seleccion == "Inventario":
            mostrar_inventario(sistema)
        elif seleccion == "Stats":
            mostrar_stats_completos(sistema)
        elif seleccion == "Títulos / Bendiciones / Maldiciones":
            if plugins.get("titulos", False):
                mostrar_titulos(sistema)
            if plugins.get("bendiciones", False):
                mostrar_bendiciones(sistema)
            if plugins.get("maldiciones", False):
                mostrar_maldiciones(sistema)
        elif seleccion == "Historia / Capítulos":
            mostrar_linea_temporal(sistema)
        elif seleccion == "Cambiar Parámetros (modificar)":
            menu_modificar_sistema()
        elif seleccion == "Volver":
            break

# ------------------- MODIFICAR SISTEMA -------------------
def menu_modificar_sistema():
    sistema = estado.sistema_actual
    plugins = sistema.get("plugins_activos", {})

    while True:
        opciones = []
        if plugins.get("stats", True):
            opciones.append("Stats")
        if plugins.get("historia", True):
            opciones.append("Historia / Capítulos")
        if plugins.get("inventario", False):
            opciones.append("Inventario")
        if plugins.get("maldiciones", False):
            opciones.append("Maldiciones")
        if any([plugins.get("titulos", False), plugins.get("bendiciones", False)]):
            opciones.append("T/B/M")  # Títulos / Bendiciones / Maldiciones
        opciones.append("Volver")

        print("\n=== MODIFICAR SISTEMA ===")
        for i, op in enumerate(opciones, start=1):
            print(f"{i}. Modificar {op}")

        try:
            opcion_num = int(input("Elige una opción: "))
        except ValueError:
            print("❌ Opción no válida.")
            continue

        if opcion_num < 1 or opcion_num > len(opciones):
            print("❌ Opción no válida.")
            continue

        seleccion = opciones[opcion_num-1]

        if seleccion == "Stats":
            menu_stats(sistema)
        elif seleccion == "Historia / Capítulos":
            menu_historia(sistema)
        elif seleccion == "Inventario":
            menu_inventario(sistema)
        elif seleccion == "Maldiciones":
            menu_maldiciones(sistema)
        elif seleccion == "T/B/M":
            menu_modificar_tbm()
        elif seleccion == "Volver":
            break

# ------------------- MODIFICAR T/B/M -------------------
def menu_modificar_tbm():
    sistema = estado.sistema_actual
    plugins = sistema.get("plugins_activos", {})

    opciones = []
    if plugins.get("titulos", False):
        opciones.append("Títulos")
    if plugins.get("bendiciones", False):
        opciones.append("Bendiciones")
    if plugins.get("maldiciones", False):
        opciones.append("Maldiciones")
    opciones.append("Volver")

    while True:
        print("\n=== MODIFICAR T/B/M ===")
        for i, op in enumerate(opciones, start=1):
            print(f"{i}. {op}")

        try:
            opcion_num = int(input("Elige una opción: "))
        except ValueError:
            print("❌ Opción no válida.")
            continue

        if opcion_num < 1 or opcion_num > len(opciones):
            print("❌ Opción no válida.")
            continue

        seleccion = opciones[opcion_num-1]

        if seleccion == "Títulos":
            menu_titulos(estado.sistema_actual)
        elif seleccion == "Bendiciones":
            menu_bendiciones(estado.sistema_actual)
        elif seleccion == "Maldiciones":
            menu_maldiciones(estado.sistema_actual)
        elif seleccion == "Volver":
            break

# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    menu_principal()
