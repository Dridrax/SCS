from estado_global import estado
from guardado.archivos import guardar_sistema

# Añadir un capítulo a la línea temporal
def añadir_capitulo(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

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
    estado.cambios_no_guardados = True

    print("✅ Capítulo añadido a la línea temporal.")


# Modificar un capítulo
def modificar_capitulo(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema.get("linea_temporal"):
        print("❌ No hay capítulos para modificar.")
        return

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

            estado.cambios_no_guardados = True
            print("✅ Capítulo modificado correctamente.")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")


# Borrar un capítulo
def borrar_capitulo(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema.get("linea_temporal"):
        print("❌ No hay capítulos para borrar.")
        return

    mostrar_linea_temporal(sistema)

    try:
        indice = int(input("Número del capítulo a eliminar: ")) - 1
        if 0 <= indice < len(sistema["linea_temporal"]):
            capitulo = sistema["linea_temporal"].pop(indice)
            estado.cambios_no_guardados = True
            print(f"🗑️ Capítulo eliminado: {capitulo['titulo']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")


# Mostrar la línea temporal completa
def mostrar_linea_temporal(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n📚 LÍNEA TEMPORAL\n")

    if not sistema.get("linea_temporal"):
        print("No hay capítulos todavía.")
        return

    for i, cap in enumerate(sistema["linea_temporal"], 1):
        print(f"{i}. {cap['titulo']}")
        print(f"   {cap['resumen']}\n")


# Menú de historia / capítulos
def menu_historia(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

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
            guardar_sistema(sistema)
            break
        else:
            print("❌ Opción no válida.")
