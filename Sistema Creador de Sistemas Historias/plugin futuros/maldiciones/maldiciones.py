from core.estado_global import estado
from core.utils.la_gran_enciclopedia import registrar_objeto, desactivar_objeto, reactivar_objeto
import uuid

# --------------------------------------------------
# UTILIDADES
# --------------------------------------------------
def asegurarse_lista(sistema=None):
    sistema = sistema or estado.sistema_actual
    sistema.setdefault("maldiciones", [])
    sistema.setdefault("enciclopedias", {}).setdefault("maldiciones", [])
    return sistema

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

# --------------------------------------------------
# MOSTRAR MALDICIONES
# --------------------------------------------------
def mostrar_maldiciones(sistema=None):
    sistema = asegurarse_lista(sistema)

    print("\n💀 MALDICIONES DEL PERSONAJE\n")
    if not sistema["maldiciones"]:
        print("No hay maldiciones.")
        return

    for m in sistema["maldiciones"]:
        print(
            f"- {m['nombre']} ({m['tipo']})\n"
            f"  Descripción: {m['descripcion']}\n"
            f"  Origen: {m.get('origen', '')}\n"
            f"  Efectos: {m.get('efectos', {})}\n"
        )

# --------------------------------------------------
# AÑADIR MALDICIÓN
# --------------------------------------------------
def añadir_maldicion(sistema=None):
    sistema = asegurarse_lista(sistema)

    print("\n➕ AÑADIR MALDICIÓN\n")

    maldicion = {
        "id": str(uuid.uuid4()),
        "nombre": input("Nombre de la maldición: "),
        "descripcion": input("Descripción: "),
        "origen": input("Origen de la maldición: "),
        "tipo": input("Tipo de maldición: "),
        "efectos": {}
    }

    efectos_input = input("Efectos sobre stats (ej: Ataque:-5,Vida:-10): ")
    for parte in efectos_input.split(","):
        if ":" in parte:
            stat, valor = parte.split(":")
            try:
                maldicion["efectos"][stat.strip()] = int(valor.strip())
            except ValueError:
                print(f"⚠️ Ignorado efecto inválido: {parte}")

    # Añadir al sistema activo
    sistema.setdefault("maldiciones", []).append(maldicion)

    # Registrar en la Gran Enciclopedia
    registrar_objeto(sistema, "maldiciones", maldicion)

    estado.cambios_no_guardados = True
    print(f"✅ Maldición '{maldicion['nombre']}' añadida correctamente.")

# --------------------------------------------------
# MODIFICAR MALDICIÓN
# --------------------------------------------------
def modificar_maldicion(sistema=None):
    sistema = asegurarse_lista(sistema)

    if not sistema["maldiciones"]:
        print("❌ No hay maldiciones para modificar.")
        return

    for i, m in enumerate(sistema["maldiciones"], 1):
        print(f"{i}. {m['nombre']} ({m['tipo']})")

    try:
        indice = int(input("Número de la maldición a modificar: ")) - 1
    except ValueError:
        print("❌ Debes introducir un número válido.")
        return

    if not (0 <= indice < len(sistema["maldiciones"])):
        print("❌ Número inválido.")
        return

    m = sistema["maldiciones"][indice]
    print(f"\n✏️ Modificando: {m['nombre']} (ENTER para mantener)")

    m["nombre"] = pedir_str("Nombre", m["nombre"])
    m["descripcion"] = pedir_str("Descripción", m["descripcion"])
    m["origen"] = pedir_str("Origen", m["origen"])
    m["tipo"] = pedir_str("Tipo", m["tipo"])

    nuevos_efectos = input("Nuevos efectos (ej: Ataque:-5,Vida:-10, ENTER para mantener): ")
    if nuevos_efectos:
        m["efectos"] = {}
        for parte in nuevos_efectos.split(","):
            if ":" in parte:
                stat, valor = parte.split(":")
                try:
                    m["efectos"][stat.strip()] = int(valor.strip())
                except ValueError:
                    print(f"⚠️ Ignorado efecto inválido: {parte}")

    # Actualizar en la enciclopedia
    registrar_objeto(sistema, "maldiciones", m, actualizar=True)
    estado.cambios_no_guardados = True
    print("✅ Maldición modificada correctamente.")

# --------------------------------------------------
# ELIMINAR MALDICIÓN
# --------------------------------------------------
def eliminar_maldicion(sistema=None):
    sistema = asegurarse_lista(sistema)

    if not sistema["maldiciones"]:
        print("❌ No hay maldiciones para eliminar.")
        return

    # Mostrar maldiciones
    for i, m in enumerate(sistema["maldiciones"], 1):
        print(f"{i}. {m['nombre']} ({m['tipo']})")

    try:
        indice = int(input("Número de la maldición a eliminar: ")) - 1
    except ValueError:
        print("❌ Debes introducir un número válido.")
        return

    if not (0 <= indice < len(sistema["maldiciones"])):
        print("❌ Número inválido.")
        return

    # 1️⃣ Obtener maldición
    m = sistema["maldiciones"][indice]

    # 2️⃣ Desactivar en la enciclopedia usando su ID
    desactivar_objeto(sistema, "maldiciones", m["id"])

    # 3️⃣ Eliminar del sistema activo
    sistema["maldiciones"].pop(indice)

    # 4️⃣ Marcar cambios
    estado.cambios_no_guardados = True

    print(f"🗑️ Maldición eliminada: {m['nombre']}")


# --------------------------------------------------
# MENÚ
# --------------------------------------------------
def menu_maldiciones(sistema=None):
    sistema = asegurarse_lista(sistema)

    while True:
        print("\n=== MALDICIONES ===")
        print("1. Ver maldiciones")
        print("2. Añadir maldición")
        print("3. Modificar maldición")
        print("4. Eliminar maldición")
        print("5. Volver")

        opcion = input("> ")

        if opcion == "1":
            mostrar_maldiciones(sistema)
        elif opcion == "2":
            añadir_maldicion(sistema)
        elif opcion == "3":
            modificar_maldicion(sistema)
        elif opcion == "4":
            eliminar_maldicion(sistema)
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida.")
