from core.estado_global import estado
from core.guardado.archivos import guardar_sistema

def mostrar_maldiciones(sistema):
    print("\n💀 MALDICIONES DEL PERSONAJE\n")
    if not sistema.get("maldiciones"):
        print("No hay maldiciones.")
        return
    for m in sistema["maldiciones"]:
        print(f"- {m['nombre']} ({m['tipo']}): {m['descripcion']}, Origen: {m.get('origen','')}, Efectos: {m.get('efectos',{})}")

def añadir_maldicion(sistema=None):
    """
    Permite añadir una nueva maldición al personaje.
    """
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n➕ AÑADIR MALDICIÓN\n")

    maldicion = {
        "nombre": input("Nombre de la maldición: "),
        "descripcion": input("Descripción: "),
        "origen": input("Origen de la maldición: "),
        "tipo": input("Tipo de maldición: "),
        "efectos": {}
    }

    efectos_input = input("Efectos sobre stats (ej: Ataque:-3,Vida:-10): ")
    for parte in efectos_input.split(","):
        if ":" in parte:
            stat, valor = parte.split(":")
            try:
                maldicion["efectos"][stat.strip()] = int(valor.strip())
            except ValueError:
                print(f"⚠️ Ignorado efecto inválido: {parte}")

    sistema["maldiciones"].append(maldicion)
    estado.cambios_no_guardados = True

    print(f"✅ Maldición '{maldicion['nombre']}' añadida correctamente.")


def modificar_maldicion(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema["maldiciones"]:
        print("❌ No hay maldiciones para modificar.")
        return

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

            estado.cambios_no_guardados = True
            print("✅ Maldición modificada correctamente.")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")


def eliminar_maldicion(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema["maldiciones"]:
        print("❌ No hay maldiciones para eliminar.")
        return

    for i, m in enumerate(sistema["maldiciones"], 1):
        print(f"{i}. {m['nombre']} ({m['tipo']})")

    try:
        indice = int(input("Número de la maldición a eliminar: ")) - 1
        if 0 <= indice < len(sistema["maldiciones"]):
            m = sistema["maldiciones"].pop(indice)
            estado.cambios_no_guardados = True
            print(f"🗑️ Maldición eliminada: {m['nombre']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")


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
            guardar_sistema(sistema)
            break
        else:
            print("❌ Opción no válida.")
