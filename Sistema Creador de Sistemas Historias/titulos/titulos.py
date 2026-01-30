from estado_global import estado
from guardado.archivos import guardar_sistema

def mostrar_titulos(sistema):
    print("\n🏆 TÍTULOS DEL PERSONAJE\n")
    if not sistema.get("titulos"):
        print("No hay títulos.")
        return
    for t in sistema["titulos"]:
        print(f"- {t['nombre']} ({t['tipo']}): {t['descripcion']}, Origen: {t.get('origen','')}, Efectos: {t.get('efectos',{})}")

def añadir_titulo():
    sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    print("\n➕ AÑADIR TÍTULO\n")

    titulo = {
        "nombre": input("Nombre del título: "),
        "descripcion": input("Descripción: "),
        "origen": input("Origen del título: "),
        "tipo": input("Tipo de título: "),
        "efectos": {}
    }

    efectos_input = input("Efectos sobre stats (ej: Ataque:7,Vida:10): ")
    for parte in efectos_input.split(","):
        if ":" in parte:
            stat, valor = parte.split(":")
            try:
                titulo["efectos"][stat.strip()] = int(valor.strip())
            except ValueError:
                print(f"⚠️ Ignorado efecto inválido: {parte}")

    sistema["titulos"].append(titulo)
    estado.cambios_no_guardados = True

    print(f"✅ Título '{titulo['nombre']}' añadido correctamente.")


def modificar_titulo():
    sistema = estado.sistema_actual
    if not sistema or not sistema["titulos"]:
        print("❌ No hay títulos para modificar.")
        return

    for i, t in enumerate(sistema["titulos"], 1):
        print(f"{i}. {t['nombre']} ({t['tipo']})")

    try:
        indice = int(input("Número del título a modificar: ")) - 1
        if 0 <= indice < len(sistema["titulos"]):
            t = sistema["titulos"][indice]

            print(f"\nTítulo seleccionado: {t['nombre']}")
            nuevo_nombre = input("Nuevo nombre (enter para mantener): ")
            nueva_descripcion = input("Nueva descripción (enter para mantener): ")
            nuevo_origen = input("Nuevo origen (enter para mantener): ")
            nuevo_tipo = input("Nuevo tipo (enter para mantener): ")
            nuevos_efectos = input("Nuevos efectos (ej: Ataque:7,Vida:10, enter para mantener): ")

            if nuevo_nombre:
                t["nombre"] = nuevo_nombre
            if nueva_descripcion:
                t["descripcion"] = nueva_descripcion
            if nuevo_origen:
                t["origen"] = nuevo_origen
            if nuevo_tipo:
                t["tipo"] = nuevo_tipo
            if nuevos_efectos:
                t["efectos"] = {}
                for parte in nuevos_efectos.split(","):
                    if ":" in parte:
                        stat, valor = parte.split(":")
                        try:
                            t["efectos"][stat.strip()] = int(valor.strip())
                        except ValueError:
                            print(f"⚠️ Ignorado efecto inválido: {parte}")

            estado.cambios_no_guardados = True
            print("✅ Título modificado correctamente.")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")


def eliminar_titulo():
    sistema = estado.sistema_actual
    if not sistema or not sistema["titulos"]:
        print("❌ No hay títulos para eliminar.")
        return

    for i, t in enumerate(sistema["titulos"], 1):
        print(f"{i}. {t['nombre']} ({t['tipo']})")

    try:
        indice = int(input("Número del título a eliminar: ")) - 1
        if 0 <= indice < len(sistema["titulos"]):
            t = sistema["titulos"].pop(indice)
            estado.cambios_no_guardados = True
            print(f"🗑️ Título eliminado: {t['nombre']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")



def menu_titulos(sistema):
    while True:
        print("\n=== MENÚ DE TÍTULOS ===")
        print("1. Ver títulos")
        print("2. Añadir título")
        print("3. Modificar título")
        print("4. Eliminar título")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_titulos(sistema)
        elif opcion == "2":
            añadir_titulo(sistema)
        elif opcion == "3":
            modificar_titulo(sistema)
        elif opcion == "4":
            eliminar_titulo(sistema)
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida.")