from core.estado_global import estado
from core.guardado.archivos import guardar_sistema

# Función para mostrar el inventario completo
def mostrar_inventario(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n📦 INVENTARIO\n")

    if not sistema["inventario"]:
        print("El inventario está vacío.")
        return

    for i, obj in enumerate(sistema["inventario"], 1):
        print(f"{i}. {obj['nombre']}")
        print(f"   Clase: {obj['clase']}")
        print(f"   Categoría: {obj['categoria']}")
        print(f"   Efectos: {obj['efectos']}\n")


# Función para añadir un objeto nuevo al inventario
def añadir_objeto(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n➕ AÑADIR OBJETO\n")

    objeto = {
        "nombre": input("Nombre del objeto: "),
        "clase": input("Clase: "),
        "categoria": input("Categoría: "),
        "efectos": input("Efectos: ")
    }

    sistema["inventario"].append(objeto)
    estado.cambios_no_guardados = True

    print("✅ Objeto añadido al inventario.")


# Función para eliminar un objeto del inventario
def eliminar_objeto(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n❌ ELIMINAR OBJETO\n")

    if not sistema["inventario"]:
        print("El inventario está vacío.")
        return

    for i, obj in enumerate(sistema["inventario"], 1):
        print(f"{i}. {obj['nombre']}")

    try:
        indice = int(input("Número del objeto a eliminar: ")) - 1
        if 0 <= indice < len(sistema["inventario"]):
            eliminado = sistema["inventario"].pop(indice)
            estado.cambios_no_guardados = True
            print(f"🗑️ Objeto eliminado: {eliminado['nombre']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número.")


# Menú para gestionar el inventario
def menu_inventario(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

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
            guardar_sistema(sistema)
            break
        else:
            print("❌ Opción no válida.")
