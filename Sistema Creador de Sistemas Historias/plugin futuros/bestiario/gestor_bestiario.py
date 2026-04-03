from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from plugins.bestiario.modelos import crear_monstruo_base
from core.utils.la_gran_enciclopedia import registrar_objeto, desactivar_objeto, reactivar_objeto

import uuid

# --------------------------------------------------
# UTILIDADES
# --------------------------------------------------
def asegurar_bestiario(sistema):
    sistema.setdefault("bestiario", [])
    sistema.setdefault("enciclopedias", {}).setdefault("bestiario", [])

def pedir_int(texto, actual=None):
    valor = input(f"{texto} [{actual}]: ")
    if valor == "":
        return actual
    try:
        return int(valor)
    except ValueError:
        print("⚠️ Valor inválido, se mantiene el anterior.")
        return actual

def pedir_str(texto, actual=None):
    valor = input(f"{texto} [{actual}]: ")
    return actual if valor == "" else valor

def pedir_bool(texto, actual=False):
    valor = input(f"{texto} (s/n) [{'s' if actual else 'n'}]: ").lower()
    if valor == "":
        return actual
    return valor == "s"

# --------------------------------------------------
# AÑADIR
# --------------------------------------------------
def añadir_monstruo(sistema=None):
    sistema = sistema or estado.sistema_actual
    asegurar_bestiario(sistema)

    monstruo = crear_monstruo_base()
    monstruo["id"] = str(uuid.uuid4())

    print("\n🐉 NUEVO MONSTRUO\n")
    monstruo["nombre"] = input("Nombre: ")
    monstruo["tipo"] = input("Tipo: ")
    monstruo["raza"] = input("Raza: ")
    monstruo["sexo"] = input("Sexo: ")
    monstruo["clase"] = input("Clase: ")
    monstruo["nivel"] = int(input("Nivel: ") or 1)
    monstruo["xp"] = int(input("XP otorgada: ") or 0)

    print("\n--- STATS BASE ---")
    for stat in monstruo["stats_base"]:
        monstruo["stats_base"][stat] = int(input(f"{stat.capitalize()}: ") or 0)

    monstruo["descripcion"] = input("Descripción: ")
    monstruo["origen"] = input("Origen: ")
    monstruo["lugar_origen"] = input("Lugar de origen: ")
    monstruo["nacimiento"] = input("Nacimiento: ")
    monstruo["metodo_invocacion"] = input("Método de invocación: ")
    monstruo["rango_aparicion"] = input("Rango de aparición: ")
    monstruo["rareza"] = input("Rareza: ")
    monstruo["domesticable"] = input("¿Domesticable? (s/n): ").lower() == "s"

    # 1️⃣ Añadir al sistema activo
    sistema.setdefault("bestiario", []).append(monstruo)

    # 2️⃣ Registrar en la Gran Enciclopedia (UNA sola línea)
    registrar_objeto(sistema, "bestiario", monstruo)

    estado.cambios_no_guardados = True
    print(f"✅ Monstruo '{monstruo['nombre']}' añadido.")


# --------------------------------------------------
# MOSTRAR
# --------------------------------------------------
def mostrar_bestiario(sistema=None):
    sistema = sistema or estado.sistema_actual
    asegurar_bestiario(sistema)

    if not sistema["bestiario"]:
        print("📭 Bestiario vacío.")
        return

    print("\n📘 BESTIARIO\n")
    for i, m in enumerate(sistema["bestiario"], 1):
        print(f"{i}. {m['nombre']} (Nv {m['nivel']})")
        print(f" Tipo: {m['tipo']} | Raza: {m['raza']} | Clase: {m['clase']}")
        print(f" Descripción: {m['descripcion']}")
        print(f" Origen: {m['origen']} | Rareza: {m['rareza']}")
        print(f" Domesticable: {m['domesticable']}")
        print()

# --------------------------------------------------
# MODIFICAR
# --------------------------------------------------
def modificar_monstruo(sistema=None):
    sistema = sistema or estado.sistema_actual
    asegurar_bestiario(sistema)

    mostrar_bestiario(sistema)

    try:
        indice = int(input("Número del monstruo a modificar: ")) - 1
        monstruo = sistema["bestiario"][indice]
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return

    print("\n✏️ MODIFICAR MONSTRUO\n")

    monstruo["nombre"] = pedir_str("Nombre", monstruo["nombre"])
    monstruo["tipo"] = pedir_str("Tipo", monstruo["tipo"])
    monstruo["raza"] = pedir_str("Raza", monstruo["raza"])
    monstruo["sexo"] = pedir_str("Sexo", monstruo["sexo"])
    monstruo["clase"] = pedir_str("Clase", monstruo["clase"])
    monstruo["nivel"] = pedir_int("Nivel", monstruo["nivel"])
    monstruo["xp"] = pedir_int("XP otorgada", monstruo["xp"])

    print("\n--- STATS BASE ---")
    for stat in monstruo["stats_base"]:
        monstruo["stats_base"][stat] = pedir_int(stat.capitalize(), monstruo["stats_base"][stat])

    monstruo["descripcion"] = pedir_str("Descripción", monstruo["descripcion"])
    monstruo["origen"] = pedir_str("Origen", monstruo["origen"])
    monstruo["lugar_origen"] = pedir_str("Lugar de origen", monstruo["lugar_origen"])
    monstruo["nacimiento"] = pedir_str("Nacimiento", monstruo["nacimiento"])
    monstruo["metodo_invocacion"] = pedir_str("Método de invocación", monstruo["metodo_invocacion"])
    monstruo["rango_aparicion"] = pedir_str("Rango de aparición", monstruo["rango_aparicion"])
    monstruo["rareza"] = pedir_str("Rareza", monstruo["rareza"])
    monstruo["domesticable"] = pedir_bool("¿Domesticable?", monstruo["domesticable"])

    # ---------- SINCRONIZAR ENCICLOPEDIA ----------
    registrar_objeto(sistema, "bestiario", monstruo, actualizar=True)


    estado.cambios_no_guardados = True
    print("✅ Monstruo actualizado.")

# --------------------------------------------------
# ELIMINAR
# --------------------------------------------------
def eliminar_monstruo(sistema=None):
    sistema = sistema or estado.sistema_actual
    asegurar_bestiario(sistema)

    mostrar_bestiario(sistema)

    try:
        indice = int(input("Número del monstruo a eliminar: ")) - 1
        monstruo = sistema["bestiario"].pop(indice)
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return

    desactivar_objeto(sistema, "bestiario", monstruo["id"])


    estado.cambios_no_guardados = True
    print(f"🗑️ Monstruo '{monstruo['nombre']}' eliminado.")

# --------------------------------------------------
# MENÚ
# --------------------------------------------------
def menu_bestiario(sistema=None):
    sistema = sistema or estado.sistema_actual

    while True:
        print("\n=== BESTIARIO ===")
        print("1. Añadir monstruo")
        print("2. Ver bestiario")
        print("3. Modificar monstruo")
        print("4. Eliminar monstruo")
        print("5. Volver")

        opcion = input("> ")

        if opcion == "1":
            añadir_monstruo(sistema)
        elif opcion == "2":
            mostrar_bestiario(sistema)
        elif opcion == "3":
            modificar_monstruo(sistema)
        elif opcion == "4":
            eliminar_monstruo(sistema)
        elif opcion == "5":
            guardar_sistema(sistema)
            break
        else:
            print("❌ Opción no válida.")
