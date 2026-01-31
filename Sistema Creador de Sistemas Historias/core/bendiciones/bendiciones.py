from core.estado_global import estado

def asegurarse_lista(sistema):
    """Asegura que el sistema tenga la lista de bendiciones"""
    if "bendiciones" not in sistema:
        sistema["bendiciones"] = []

def mostrar_bendiciones(sistema):
    print("\n✨ BENDICIONES DEL PERSONAJE\n")
    if not sistema.get("bendiciones"):
        print("No hay bendiciones.")
        return
    for b in sistema["bendiciones"]:
        print(f"- {b['nombre']} ({b['tipo']}): {b['descripcion']}, Origen: {b.get('origen','')}, Efectos: {b.get('efectos',{})}")

def añadir_bendicion(sistema):
    asegurarse_lista(sistema)
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

def modificar_bendicion(sistema):
    asegurarse_lista(sistema)
    if not sistema["bendiciones"]:
        print("❌ No hay bendiciones para modificar.")
        return

    for i, b in enumerate(sistema["bendiciones"], 1):
        print(f"{i}. {b['nombre']} ({b['tipo']})")

    try:
        indice = int(input("Número de la bendición a modificar: ")) - 1
        if 0 <= indice < len(sistema["bendiciones"]):
            b = sistema["bendiciones"][indice]
            print(f"\nBendición seleccionada: {b['nombre']}")

            nuevo_nombre = input("Nuevo nombre (enter para mantener): ")
            nueva_descripcion = input("Nueva descripción (enter para mantener): ")
            nuevo_origen = input("Nuevo origen (enter para mantener): ")
            nuevo_tipo = input("Nuevo tipo (enter para mantener): ")
            nuevos_efectos = input("Nuevos efectos (ej: Ataque:5,Vida:10, enter para mantener): ")

            if nuevo_nombre:
                b["nombre"] = nuevo_nombre
            if nueva_descripcion:
                b["descripcion"] = nueva_descripcion
            if nuevo_origen:
                b["origen"] = nuevo_origen
            if nuevo_tipo:
                b["tipo"] = nuevo_tipo
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
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")

def eliminar_bendicion(sistema):
    asegurarse_lista(sistema)
    if not sistema["bendiciones"]:
        print("❌ No hay bendiciones para eliminar.")
        return

    for i, b in enumerate(sistema["bendiciones"], 1):
        print(f"{i}. {b['nombre']} ({b['tipo']})")

    try:
        indice = int(input("Número de la bendición a eliminar: ")) - 1
        if 0 <= indice < len(sistema["bendiciones"]):
            b = sistema["bendiciones"].pop(indice)
            estado.cambios_no_guardados = True
            print(f"🗑️ Bendición eliminada: {b['nombre']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")

def menu_bendiciones(sistema):
    asegurarse_lista(sistema)
    while True:
        print("\n=== MENÚ DE BENDICIONES ===")
        print("1. Ver bendiciones")
        print("2. Añadir bendición")
        print("3. Modificar bendición")
        print("4. Eliminar bendición")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            if not sistema["bendiciones"]:
                print("No hay bendiciones.")
            else:
                for b in sistema["bendiciones"]:
                    print(f"- {b['nombre']} ({b['tipo']}): {b['descripcion']}, Origen: {b.get('origen','')}, Efectos: {b.get('efectos',{})}")
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
