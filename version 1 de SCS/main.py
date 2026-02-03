from core.estado_global import estado
from core.sistemas.crear_sistema import crear_nuevo_sistema
from core.sistemas.mostrar_sistema import mostrar_ficha, mostrar_stats_completos
from core.guardado.archivos import guardar_sistema, cargar_sistema, guardar_como
from core.utils.salida import salir_programa
from core.stats.stats import menu_stats, mostrar_stats
from core.historia.linea_temporal import menu_historia, mostrar_linea_temporal
from core.utils.exportar_pdf import exportar_ficha_pdf
from core.utils.la_gran_enciclopedia import listar_enciclopedia

# Plugins
from plugins.inventario.inventario import menu_inventario, mostrar_inventario
from plugins.habilidades.habilidades import menu_habilidades, mostrar_habilidades
from plugins.titulos.titulos import menu_titulos, mostrar_titulos
from plugins.bendiciones.bendiciones import menu_bendiciones, mostrar_bendiciones
from plugins.maldiciones.maldiciones import menu_maldiciones, mostrar_maldiciones
from plugins.notas.gestor_notas import menu_notas
from plugins.bestiario.gestor_bestiario import menu_bestiario


# ------------------- MENÚ PRINCIPAL -------------------
def menu_principal():
    while True:
        nombre_sistema = estado.sistema_actual.get("nombre_sistema") if estado.sistema_actual else "Sin sistema cargado"
        print(f"\n=== SISTEMA DOC (Sistema actual: {nombre_sistema}) ===")
        print("1. Crear / Cargar Sistema")
        print("2. Guardar Sistema")
        print("3. Gestión del Sistema")
        print("4. Exportar Ficha a PDF")
        print("5. LA GRAN ENCICLOPEDIA")  # Ahora solo Enciclopedias
        print("6. Administrar Plugins")
        print("7. Ver Ficha del Sistema")
        print("8. Salir")

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
        elif opcion == "5":
            if estado.sistema_actual:
                listar_enciclopedia(estado.sistema_actual)
            else:
                print("❌ No hay ningún sistema cargado.")
        elif opcion == "6":
            if estado.sistema_actual:
                menu_plugins()
            else:
                print("❌ No hay ningún sistema cargado.")
        elif opcion == "7":
            if estado.sistema_actual:
                mostrar_ficha(estado.sistema_actual)
            else:
                print("❌ No hay ningún sistema cargado.")
        elif opcion == "8":
            if salir_programa():
                break
        else:
            print("❌ Opción no válida.")

# ------------------- ADMINISTRAR PLUGINS -------------------
def menu_plugins():
    sistema = estado.sistema_actual
    plugins = sistema.get("plugins_activos", {})

    while True:
        print("\n=== ADMINISTRAR PLUGINS ===")
        for i, plugin in enumerate(plugins, 1):
            estado_str = "✅ Activo" if plugins[plugin] else "❌ Inactivo"
            print(f"{i}. {plugin.capitalize()}: {estado_str}")
        print(f"{len(plugins)+1}. Volver")

        try:
            opcion = int(input("Elige un plugin para activar/desactivar: "))
        except ValueError:
            print("❌ Opción no válida.")
            continue

        if opcion == len(plugins)+1:
            break
        elif 1 <= opcion <= len(plugins):
            key = list(plugins.keys())[opcion-1]
            plugins[key] = not plugins[key]
            estado.cambios_no_guardados = True
            print(f"🔄 {key.capitalize()} ahora {'Activo' if plugins[key] else 'Inactivo'}")
        else:
            print("❌ Opción no válida.")

# ------------------- CREAR / CARGAR -------------------
# ======================================================
# CREAR / CARGAR SISTEMA
# ======================================================
def menu_crear_cargar():
    while True:
        print("\n=== CREAR / CARGAR ===")
        print("1. Crear Nuevo Sistema/Personaje")
        print("2. Cargar Sistema/Personaje")
        print("3. Volver")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            # --- Selección de plugins ---
            print("\n=== PLUGINS DISPONIBLES ===")
            plugins_activos = {}
            for plugin in ["inventario", "habilidades", "bendiciones", "maldiciones",
                           "titulos", "notas", "bestiario"]:
                respuesta = input(f"¿Activar plugin {plugin}? (s/n): ").lower()
                plugins_activos[plugin] = respuesta == "s"

            # --- Crear sistema nuevo ---
            sistema = crear_nuevo_sistema(plugins_activos)
            
            # ✅ Incluir plugins_activos dentro del sistema
            sistema["plugins_activos"] = plugins_activos

            estado.sistema_actual = sistema
            estado.archivo_actual = None

            mostrar_ficha(estado.sistema_actual)

            if input("\n¿Deseas guardar este sistema? (s/n): ").lower() == "s":
                guardar_sistema()

        elif opcion == "2":
            archivo = input("Nombre del archivo a cargar: ")
            sistema = cargar_sistema(archivo)

            # --- NORMALIZAR TITULOS ---
            titulos_norm = []
            for t in sistema.get("titulos", []):
                if isinstance(t, dict):
                    titulos_norm.append(t)
                elif isinstance(t, str):
                    # buscar en enciclopedia
                    for et in sistema.get("enciclopedias", {}).get("titulos", []):
                        if et.get("id") == t:
                            titulos_norm.append(et)
                            break
            sistema["titulos"] = titulos_norm


            if sistema:
                # --- NORMALIZAR CLAVES ---
                # Diccionarios
                for clave in ["enciclopedias", "historia"]:
                    if clave not in sistema or sistema[clave] is None or not isinstance(sistema[clave], dict):
                        sistema[clave] = {}
                # Listas
                for clave in ["inventario", "habilidades", "titulos", "bendiciones",
                              "maldiciones", "notas", "bestiario", "linea_temporal"]:
                    if clave not in sistema or sistema[clave] is None or not isinstance(sistema[clave], list):
                        sistema[clave] = []

                # Plugins activos
                plugins_defecto = ["inventario", "habilidades", "bendiciones", "maldiciones",
                                   "titulos", "notas", "enciclopedias", "bestiario"]
                if "plugins_activos" not in sistema or sistema["plugins_activos"] is None:
                    sistema["plugins_activos"] = {k: True for k in plugins_defecto}
                else:
                    for p in plugins_defecto:
                        sistema["plugins_activos"].setdefault(p, True)

                estado.sistema_actual = sistema
                estado.archivo_actual = archivo
                print(f"✅ Sistema cargado correctamente desde '{archivo}.json'")
                mostrar_ficha(estado.sistema_actual)

        elif opcion == "3":
            break
        else:
            print("❌ Opción no válida.")

# 💡 Comentarios:
# - Nuevos plugins deben agregarse a la lista de plugins_activos aquí y en plugins_defecto
# - Normalizar claves asegura que inventario, habilidades, enciclopedias, etc. siempre existan


# 💡 COMENTARIOS:
# - Nuevos plugins deben agregarse a la lista de plugins_activos.
# - Normalizar las claves en este bloque para evitar errores de tipo.
# - Si usan enciclopedias, asegurarse que 'enciclopedias' sea diccionario
#   y que cada sección sea una lista vacía al inicio.



# ======================================================
# GUARDADO
# ======================================================
def menu_guardado():
    if not estado.sistema_actual:
        print("❌ No hay sistema cargado.")
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


# ------------------- GESTIÓN DEL SISTEMA -------------------
def menu_gestion_sistema():
    sistema = estado.sistema_actual
    plugins = sistema.get("plugins_activos", {})
    if not isinstance(plugins, dict):
        plugins = {k: True for k in [
            "inventario", "habilidades", "bendiciones",
            "maldiciones", "titulos", "notas", "bestiario"
        ]}

    while True:
        print(f"\n=== GESTIÓN ({sistema.get('nombre_sistema', '')}) ===")
        opciones = []

        if plugins.get("inventario"):
            opciones.append("Inventario")
        if plugins.get("habilidades"):
            opciones.append("Habilidades")

        opciones.append("Stats")

        # ---------- HISTORIA / NOTAS / BESTIARIO (DINÁMICO) ----------
        label_historia = "Historia / Capítulos"

        extras = []
        if plugins.get("notas"):
            extras.append("Notas")
        if plugins.get("bestiario"):
            extras.append("Bestiario")

        if extras:
            label_historia += " / " + " / ".join(extras)

        opciones.append(label_historia)
        # ------------------------------------------------------------

        if any([plugins.get("titulos"), plugins.get("bendiciones"), plugins.get("maldiciones")]):
            opciones.append("Títulos / Bendiciones / Maldiciones")

        opciones.append("Modificar Sistema")
        opciones.append("Volver")

        for i, op in enumerate(opciones, 1):
            print(f"{i}. {op}")

        try:
            seleccion = opciones[int(input("> ")) - 1]
        except (ValueError, IndexError):
            print("❌ Opción inválida.")
            continue

        if seleccion == "Inventario":
            mostrar_inventario(sistema)
        elif seleccion == "Habilidades":
            mostrar_habilidades(sistema)
        elif seleccion == "Stats":
            mostrar_stats_completos(sistema)

        # 🔑 IMPORTANTE: startswith
        elif seleccion.startswith("Historia / Capítulos"):
            mostrar_linea_temporal(sistema)

        elif seleccion == "Títulos / Bendiciones / Maldiciones":
            if plugins.get("titulos"):
                mostrar_titulos(sistema)
            if plugins.get("bendiciones"):
                mostrar_bendiciones(sistema)
            if plugins.get("maldiciones"):
                mostrar_maldiciones(sistema)

        elif seleccion == "Modificar Sistema":
            menu_modificar_sistema()
        elif seleccion == "Volver":
            break


# 💡 Comentarios:
# - Aquí se agregan futuros plugins al menú principal de Gestión
#   Ejemplo: if plugins.get("tienda"): opciones.append("Tienda")


# ======================================================
# MODIFICAR SISTEMA
# ======================================================
def menu_modificar_sistema():
    sistema = estado.sistema_actual
    plugins = sistema.get("plugins_activos", {})
    if not isinstance(plugins, dict):
        plugins = {k: True for k in ["inventario", "habilidades", "bendiciones", "maldiciones",
                                     "titulos", "notas", "bestiario", "enciclopedias"]}

    while True:
        print("\n=== MODIFICAR SISTEMA ===")
        opciones = ["Stats"]

        plugins = sistema.get("plugins_activos", {})

        label_historia = "Historia / Capítulos"

        extras = []
        if plugins.get("notas"):
            extras.append("Notas")
        if plugins.get("bestiario"):
            extras.append("Bestiario")

        if extras:
            label_historia += " / " + " / ".join(extras)

        opciones.append(label_historia)


        if plugins.get("inventario"):
            opciones.append("Inventario")
        if plugins.get("habilidades"):
            opciones.append("Habilidades")
        if plugins.get("titulos") or plugins.get("bendiciones") or plugins.get("maldiciones"):
            opciones.append("Títulos / Bendiciones / Maldiciones")

        opciones.append("Volver")

        for i, op in enumerate(opciones, 1):
            print(f"{i}. {op}")

        try:
            seleccion = opciones[int(input("> ")) - 1]
        except (ValueError, IndexError):
            print("❌ Opción inválida.")
            continue

        if seleccion == "Stats":
            menu_stats(sistema)
        elif seleccion.startswith("Historia / Capítulos"):
            menu_modificar_historia_notas_bestiario()
        elif seleccion == "Inventario":
            menu_inventario(sistema)
        elif seleccion == "Habilidades":
            menu_habilidades(sistema)
        elif seleccion == "Títulos / Bendiciones / Maldiciones":
            menu_modificar_tbm()
        elif seleccion == "Volver":
            break

# 💡 Comentarios:
# - Aquí se agregan futuros plugins al menú de modificación de sistema
# - Si agregas, por ejemplo, 'tienda', se haría: if plugins.get("tienda"): opciones.append("Tienda")


# ======================================================
# SUBMENÚ: TÍTULOS / BENDICIONES / MALDICIONES
# ======================================================
def menu_modificar_tbm():
    sistema = estado.sistema_actual
    plugins = sistema.get("plugins_activos", {})

    while True:
        print("\n=== MODIFICAR T/B/M ===")
        opciones = []

        if plugins.get("titulos"):
            opciones.append("Títulos")
        if plugins.get("bendiciones"):
            opciones.append("Bendiciones")
        if plugins.get("maldiciones"):
            opciones.append("Maldiciones")

        opciones.append("Volver")

        for i, op in enumerate(opciones, 1):
            print(f"{i}. {op}")

        try:
            seleccion = opciones[int(input("> ")) - 1]
        except (ValueError, IndexError):
            print("❌ Opción inválida.")
            continue

        if seleccion == "Títulos":
            menu_titulos(sistema)
        elif seleccion == "Bendiciones":
            menu_bendiciones(sistema)
        elif seleccion == "Maldiciones":
            menu_maldiciones(sistema)
        elif seleccion == "Volver":
            break

# ======================================================
# SUBMENÚ: THISTORIA/CAPITULOS/NOTAS/BESTIARIO
# ======================================================


def menu_modificar_historia_notas_bestiario():
    sistema = estado.sistema_actual
    plugins = sistema.get("plugins_activos", {})

    while True:
        print("\n=== MODIFICAR HISTORIA / NOTAS / BESTIARIO ===")
        opciones = []

        # Historia SIEMPRE existe (core)
        opciones.append("Historia / Capítulos")

        if plugins.get("notas"):
            opciones.append("Notas")

        if plugins.get("bestiario"):
            opciones.append("Bestiario")

        opciones.append("Volver")

        for i, op in enumerate(opciones, 1):
            print(f"{i}. {op}")

        try:
            seleccion = opciones[int(input("> ")) - 1]
        except (ValueError, IndexError):
            print("❌ Opción inválida.")
            continue

        if seleccion == "Historia / Capítulos":
            menu_historia(sistema)
        elif seleccion == "Notas":
            menu_notas(sistema)
        elif seleccion == "Bestiario":
            menu_bestiario(sistema)
        elif seleccion == "Volver":
            break

# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    menu_principal()
