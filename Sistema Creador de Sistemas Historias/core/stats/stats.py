from core.estado_global import estado
from core.guardado.archivos import guardar_sistema

# =========================
# MOSTRAR STATS
# =========================
def mostrar_stats(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema or not sistema.get("stats"):
        print("❌ No hay stats disponibles.")
        return

    print("\n📊 STATS ACTUALES\n")
    for stat, valor in sistema["stats"].items():
        print(f"- {stat}: {valor}")

# =========================
# MODIFICAR STAT
# =========================
def modificar_stat(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema or not sistema.get("stats"):
        print("❌ No hay stats disponibles.")
        return

    print("\n✏️ MODIFICAR STAT\n")
    mostrar_stats(sistema)

    stat = input("\nNombre del stat a modificar: ")

    if stat not in sistema["stats"]:
        print("❌ Ese stat no existe.")
        return

    try:
        cambio = int(input("Cantidad a sumar/restar (ej: -10 o 5): "))
    except ValueError:
        print("❌ Debes introducir un número.")
        return

    sistema["stats"][stat] += cambio
    estado.cambios_no_guardados = True

    print(f"✅ {stat} modificado correctamente.")

# =========================
# AÑADIR STAT
# =========================
def añadir_stat(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema:
        print("❌ No hay un sistema cargado.")
        return

    sistema.setdefault("stats", {})

    print("\n➕ AÑADIR NUEVO STAT\n")
    stat = input("Nombre del nuevo stat: ").strip()

    if not stat:
        print("❌ El nombre no puede estar vacío.")
        return

    if stat in sistema["stats"]:
        print("❌ Ese stat ya existe.")
        return

    try:
        valor = int(input("Valor inicial del stat: "))
    except ValueError:
        print("❌ Debes introducir un número.")
        return

    sistema["stats"][stat] = valor
    estado.cambios_no_guardados = True

    print(f"✅ Stat '{stat}' añadido con valor {valor}.")

# =========================
# ELIMINAR STAT
# =========================
def eliminar_stat(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema or not sistema.get("stats"):
        print("❌ No hay stats disponibles.")
        return

    print("\n🗑️ ELIMINAR STAT\n")
    mostrar_stats(sistema)

    stat = input("\nNombre del stat a eliminar: ")

    if stat not in sistema["stats"]:
        print("❌ Ese stat no existe.")
        return

    confirm = input(f"¿Seguro que quieres eliminar '{stat}'? (s/n): ").lower()
    if confirm != "s":
        print("❌ Eliminación cancelada.")
        return

    del sistema["stats"][stat]
    estado.cambios_no_guardados = True

    print(f"✅ Stat '{stat}' eliminado correctamente.")

# =========================
# MENÚ DE STATS
# =========================
def menu_stats(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    while True:
        print("\n=== MENÚ DE STATS ===")
        print("1. Ver stats")
        print("2. Modificar stat")
        print("3. Añadir stat")
        print("4. Eliminar stat")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_stats(sistema)

        elif opcion == "2":
            modificar_stat(sistema)

        elif opcion == "3":
            añadir_stat(sistema)

        elif opcion == "4":
            eliminar_stat(sistema)

        elif opcion == "5":
            guardar_sistema()
            break

        else:
            print("❌ Opción no válida.")
