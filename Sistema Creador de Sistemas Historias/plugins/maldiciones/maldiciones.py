from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
import uuid


# ---------- MOSTRAR ----------
def mostrar_maldiciones(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n💀 MALDICIONES DEL PERSONAJE\n")
    if not sistema.get("maldiciones"):
        print("No hay maldiciones.")
        return

    for m in sistema["maldiciones"]:
        print(
            f"- {m['nombre']} ({m['tipo']}): {m['descripcion']} | "
            f"Origen: {m.get('origen', '')} | "
            f"Efectos: {m.get('efectos', {})}"
        )


# ---------- AÑADIR ----------
def añadir_maldicion(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n➕ AÑADIR MALDICIÓN\n")

    maldicion = {
        "id": str(uuid.uuid4()),
        "nombre": input("Nombre de la maldición: "),
        "descripcion": input("Descripción: "),
        "origen": input("Origen de la maldición: "),
        "tipo": input("Tipo de maldición: "),
        "efectos": {}
    }

    efectos_input = input("Efectos (ej: Ataque:-3,Vida:-10): ")
    for parte in efectos_input.split(","):
        if ":" in parte:
            stat, valor = parte.split(":")
            try:
                maldicion["efectos"][stat.strip()] = int(valor.strip())
            except ValueError:
                print(f"⚠️ Ignorado efecto inválido: {parte}")

    sistema.setdefault("maldiciones", []).append(maldicion)
    estado.cambios_no_guardados = True

    # Enciclopedia
    enciclopedia = sistema.setdefault("enciclopedias", {}).setdefault("maldiciones", [])
    enciclopedia.append({**maldicion, "activo": True})

    print(f"✅ Maldición '{maldicion['nombre']}' añadida correctamente.")


# ---------- MODIFICAR ----------
def modificar_maldicion(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema.get("maldiciones"):
        print("❌ No hay maldiciones para modificar.")
        return

    for i, m in enumerate(sistema["maldiciones"], 1):
        print(f"{i}. {m['nombre']} ({m['tipo']})")

    try:
        indice = int(input("Número a modificar: ")) - 1
        m = sistema["maldiciones"][indice]
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return

    print(f"\nMaldición seleccionada: {m['nombre']}")

    m["nombre"] = input("Nuevo nombre (enter para mantener): ") or m["nombre"]
    m["descripcion"] = input("Nueva descripción (enter): ") or m["descripcion"]
    m["origen"] = input("Nuevo origen (enter): ") or m["origen"]
    m["tipo"] = input("Nuevo tipo (enter): ") or m["tipo"]

    nuevos_efectos = input("Nuevos efectos (enter para mantener): ")
    if nuevos_efectos:
        m["efectos"] = {}
        for parte in nuevos_efectos.split(","):
            if ":" in parte:
                stat, valor = parte.split(":")
                try:
                    m["efectos"][stat.strip()] = int(valor.strip())
                except ValueError:
                    print(f"⚠️ Ignorado efecto inválido: {parte}")

    # Actualizar enciclopedia por ID
    enciclopedia = sistema.setdefault("enciclopedias", {}).setdefault("maldiciones", [])
    for e in enciclopedia:
        if e["id"] == m["id"]:
            e.update(m)
            e["activo"] = True

    estado.cambios_no_guardados = True
    print("✅ Maldición modificada correctamente.")


# ---------- ELIMINAR ----------
def eliminar_maldicion(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema.get("maldiciones"):
        print("❌ No hay maldiciones para eliminar.")
        return

    for i, m in enumerate(sistema["maldiciones"], 1):
        print(f"{i}. {m['nombre']} ({m['tipo']})")

    try:
        indice = int(input("Número a eliminar: ")) - 1
        m = sistema["maldiciones"].pop(indice)
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return

    # Desactivar en enciclopedia
    enciclopedia = sistema.setdefault("enciclopedias", {}).setdefault("maldiciones", [])
    for e in enciclopedia:
        if e["id"] == m["id"]:
            e["activo"] = False

    estado.cambios_no_guardados = True
    print(f"🗑️ Maldición eliminada: {m['nombre']}")


# ---------- MENÚ ----------
def menu_maldiciones(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    while True:
        print("\n=== MENÚ DE MALDICIONES ===")
        print("1. Ver maldiciones")
        print("2. Añadir maldición")
        print("3. Modificar maldición")
        print("4. Eliminar maldición")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_maldiciones(sistema)
        elif opcion == "2":
            añadir_maldicion(sistema)
        elif opcion == "3":
            modificar_maldicion(sistema)
        elif opcion == "4":
            eliminar_maldicion(sistema)
        elif opcion == "5":
            guardar_sistema(sistema)
            break
        else:
            print("❌ Opción no válida.")
