from core.estado_global import estado

# --------------------------------------------------
# UTILIDADES
# --------------------------------------------------
def asegurarse_lista(sistema=None):
    sistema = sistema or estado.sistema_actual
    sistema.setdefault("bendiciones", [])
    sistema.setdefault("enciclopedias", {}).setdefault("bendiciones", [])
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
# MOSTRAR BENDICIONES
# --------------------------------------------------
def mostrar_bendiciones(sistema=None):
    sistema = asegurarse_lista(sistema)

    print("\n✨ BENDICIONES DEL PERSONAJE\n")
    if not sistema["bendiciones"]:
        print("No hay bendiciones.")
        return

    for b in sistema["bendiciones"]:
        print(
            f"- {b['nombre']} ({b['tipo']})\n"
            f"  Descripción: {b['descripcion']}\n"
            f"  Origen: {b.get('origen', '')}\n"
            f"  Efectos: {b.get('efectos', {})}\n"
        )

# --------------------------------------------------
# AÑADIR BENDICIÓN
# --------------------------------------------------
def añadir_bendicion(sistema=None):
    sistema = asegurarse_lista(sistema)

    print("\n➕ AÑADIR BENDICIÓN\n")

    bendicion = {
        "nombre": input("Nombre de la bendición: "),
        "descripcion": input("Descripción: "),
        "origen": input("Origen de la bendición: "),
        "tipo": input("Tipo de bendición: "),
        "efectos": {}
    }

    efectos_input = input("Efectos sobre stats (ej: Ataque:5,Vida:10): ")
    for parte in efectos_input.split(","):
        if ":" in parte:
            stat, valor = parte.split(":")
            try:
                bendicion["efectos"][stat.strip()] = int(valor.strip())
            except ValueError:
                print(f"⚠️ Ignorado efecto inválido: {parte}")

    sistema["bendiciones"].append(bendicion)
    estado.cambios_no_guardados = True

    print(f"✅ Bendición '{bendicion['nombre']}' añadida correctamente.")

    # -------- REGISTRO EN ENCICLOPEDIA --------
    enciclopedia = sistema["enciclopedias"]["bendiciones"]
    if not any(
        e["nombre"] == bendicion["nombre"] and e["tipo"] == bendicion["tipo"]
        for e in enciclopedia
    ):
        enciclopedia.append({**bendicion, "activo": True})

# --------------------------------------------------
# MODIFICAR BENDICIÓN
# --------------------------------------------------
def modificar_bendicion(sistema=None):
    sistema = asegurarse_lista(sistema)

    if not sistema["bendiciones"]:
        print("❌ No hay bendiciones para modificar.")
        return

    for i, b in enumerate(sistema["bendiciones"], 1):
        print(f"{i}. {b['nombre']} ({b['tipo']})")

    try:
        indice = int(input("Número de la bendición a modificar: ")) - 1
    except ValueError:
        print("❌ Debes introducir un número válido.")
        return

    if not (0 <= indice < len(sistema["bendiciones"])):
        print("❌ Número inválido.")
        return

    b = sistema["bendiciones"][indice]
    print(f"\n✏️ Modificando: {b['nombre']} (ENTER para mantener)")

    b["nombre"] = pedir_str("Nombre", b["nombre"])
    b["descripcion"] = pedir_str("Descripción", b["descripcion"])
    b["origen"] = pedir_str("Origen", b["origen"])
    b["tipo"] = pedir_str("Tipo", b["tipo"])

    nuevos_efectos = input("Nuevos efectos (ej: Ataque:5,Vida:10, ENTER para mantener): ")
    if nuevos_efectos:
        b["efectos"] = {}
        for parte in nuevos_efectos.split(","):
            if ":" in parte:
                stat, valor = parte.split(":")
                try:
                    b["efectos"][stat.strip()] = int(valor.strip())
                except ValueError:
                    print(f"⚠️ Ignorado efecto inválido: {parte}")

    estado.cambios_no_guardados = True
    print("✅ Bendición modificada correctamente.")

# --------------------------------------------------
# ELIMINAR BENDICIÓN
# --------------------------------------------------
def eliminar_bendicion(sistema=None):
    sistema = asegurarse_lista(sistema)

    if not sistema["bendiciones"]:
        print("❌ No hay bendiciones para eliminar.")
        return

    for i, b in enumerate(sistema["bendiciones"], 1):
        print(f"{i}. {b['nombre']} ({b['tipo']})")

    try:
        indice = int(input("Número de la bendición a eliminar: ")) - 1
    except ValueError:
        print("❌ Debes introducir un número válido.")
        return

    if not (0 <= indice < len(sistema["bendiciones"])):
        print("❌ Número inválido.")
        return

    b = sistema["bendiciones"].pop(indice)
    estado.cambios_no_guardados = True

    print(f"🗑️ Bendición eliminada: {b['nombre']}")

    # -------- DESACTIVAR EN ENCICLOPEDIA --------
    enciclopedia = sistema["enciclopedias"]["bendiciones"]
    for e in enciclopedia:
        if e["nombre"] == b["nombre"] and e["tipo"] == b["tipo"]:
            e["activo"] = False

# --------------------------------------------------
# MENÚ
# --------------------------------------------------
def menu_bendiciones(sistema=None):
    sistema = asegurarse_lista(sistema)

    while True:
        print("\n=== BENDICIONES ===")
        print("1. Ver bendiciones")
        print("2. Añadir bendición")
        print("3. Modificar bendición")
        print("4. Eliminar bendición")
        print("5. Volver")

        opcion = input("> ")

        if opcion == "1":
            mostrar_bendiciones(sistema)
        elif opcion == "2":
            añadir_bendicion(sistema)
        elif opcion == "3":
            modificar_bendicion(sistema)
        elif opcion == "4":
            eliminar_bendicion(sistema)
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida.")
