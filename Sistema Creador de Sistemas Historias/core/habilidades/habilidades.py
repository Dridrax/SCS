from core.estado_global import estado
from core.guardado.archivos import guardar_sistema

def mostrar_habilidades(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n🛡️ HABILIDADES DEL PERSONAJE\n")

    if not sistema.get("habilidades"):
        print("No hay habilidades aún.")
        return

    for i, h in enumerate(sistema["habilidades"], 1):
        print(f"{i}. {h['nombre']}")
        print(f"   Tipo: {h['tipo']}")
        print(f"   Descripción: {h.get('descripcion', '')}")
        print(f"   Efectos: {h.get('efectos',{})}\n")


def añadir_habilidad(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n➕ AÑADIR HABILIDAD\n")

    habilidad = {
        "nombre": input("Nombre de la habilidad: "),
        "tipo": input("Tipo de habilidad: "),
        "descripcion": input("Descripción: "),
        "efectos": input("Efectos: ")
    }

    sistema.setdefault("habilidades", []).append(habilidad)
    estado.cambios_no_guardados = True

    print("✅ Habilidad añadida correctamente.")


def modificar_habilidad(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema.get("habilidades"):
        print("❌ No hay habilidades para modificar.")
        return

    mostrar_habilidades(sistema)

    try:
        indice = int(input("Número de la habilidad a modificar: ")) - 1
        if 0 <= indice < len(sistema["habilidades"]):
            h = sistema["habilidades"][indice]

            print(f"\nHabilidad seleccionada: {h['nombre']}")

            nuevo_nombre = input("Nuevo nombre (enter para mantener): ")
            nuevo_tipo = input("Nuevo tipo (enter para mantener): ")
            nueva_descripcion = input("Nueva descripción (enter para mantener): ")
            nuevos_efectos = input("Nuevos efectos (enter para mantener): ")

            if nuevo_nombre:
                h["nombre"] = nuevo_nombre
            if nuevo_tipo:
                h["tipo"] = nuevo_tipo
            if nueva_descripcion:
                h["descripcion"] = nueva_descripcion
            if nuevos_efectos:
                h["efectos"] = nuevos_efectos

            estado.cambios_no_guardados = True
            print("✅ Habilidad modificada correctamente.")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")


def eliminar_habilidad(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema.get("habilidades"):
        print("❌ No hay habilidades para eliminar.")
        return

    mostrar_habilidades(sistema)

    try:
        indice = int(input("Número de la habilidad a eliminar: ")) - 1
        if 0 <= indice < len(sistema["habilidades"]):
            h = sistema["habilidades"].pop(indice)
            estado.cambios_no_guardados = True
            print(f"🗑️ Habilidad eliminada: {h['nombre']}")
        else:
            print("❌ Número inválido.")
    except ValueError:
        print("❌ Debes introducir un número válido.")


def menu_habilidades(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    while True:
        print("\n=== MENÚ DE HABILIDADES ===")
        print("1. Ver habilidades")
        print("2. Añadir habilidad")
        print("3. Modificar habilidad")
        print("4. Eliminar habilidad")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_habilidades(sistema)
        elif opcion == "2":
            añadir_habilidad(sistema)
        elif opcion == "3":
            modificar_habilidad(sistema)
        elif opcion == "4":
            eliminar_habilidad(sistema)
        elif opcion == "5":
            guardar_sistema(sistema)
            break
        else:
            print("❌ Opción no válida.")
