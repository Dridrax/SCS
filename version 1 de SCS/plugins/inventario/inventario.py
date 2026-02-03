from core.estado_global import estado
from core.utils.busqueda import buscar
from core.guardado.archivos import guardar_sistema
from core.utils.la_gran_enciclopedia import registrar_objeto, desactivar_objeto, reactivar_objeto
import uuid

# =========================
# MOSTRAR INVENTARIO
# =========================
def mostrar_inventario(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n📦 INVENTARIO\n")

    if not sistema.get("inventario"):
        print("El inventario está vacío.")
        return

    for i, obj in enumerate(sistema["inventario"], 1):
        print(f"{i}. {obj['nombre']}")
        print(f"   Clase: {obj['clase']}")
        print(f"   Categoría: {obj['categoria']}")
        print(f"   Efectos: {obj['efectos']}")
        # 🔹 Indicar si está activo o desactivado según enciclopedia
        enc = buscar_objeto_enciclopedia(obj['id'], sistema, "inventario")
        estado_str = "Activo" if enc.get("activo") else "Desactivado"
        print(f"   Estado en Enciclopedia: {estado_str}\n")


# =========================
# BUSCAR EN INVENTARIO
# =========================
def buscar_inventario(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n🔍 BUSCAR EN INVENTARIO")
    nombre = input("Nombre (enter para omitir): ")
    clase = input("Clase (enter para omitir): ")
    categoria = input("Categoría (enter para omitir): ")
    efecto = input("Efecto (enter para omitir): ")

    resultados = buscar(
        sistema.get("inventario", []),
        nombre=nombre or None,
        clase=clase or None,
        categoria=categoria or None,
        efectos=efecto or None
    )

    if not resultados:
        print("❌ No se encontraron objetos.")
        return

    print(f"\n📦 RESULTADOS ({len(resultados)})\n")
    for obj in resultados:
        print(f"- {obj['nombre']} ({obj['clase']}) | {obj['categoria']} | {obj['efectos']}")


# =========================
# AÑADIR OBJETO
# =========================
def añadir_objeto(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n➕ AÑADIR OBJETO\n")

    # 🔹 Crear objeto con ID único
    inventario = {
        "id": str(uuid.uuid4()),
        "nombre": input("Nombre del objeto: "),
        "clase": input("Clase: "),
        "categoria": input("Categoría: "),
        "efectos": input("Efectos: ")
    }

    # 🔹 Añadir al inventario
    sistema.setdefault("inventario", []).append(inventario)

    # 🔹 Registrar en LA GRAN ENCICLOPEDIA
    registrar_objeto(sistema, "inventario", inventario)

    estado.cambios_no_guardados = True
    print("✅ Objeto añadido al inventario y registrado en la enciclopedia.")


# =========================
# MODIFICAR OBJETO
# =========================
def modificar_objeto(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema.get("inventario"):
        print("❌ No hay objetos para modificar.")
        return

    for i, obj in enumerate(sistema["inventario"], 1):
        print(f"{i}. {obj['nombre']}")

    try:
        indice = int(input("Número del objeto a modificar: ")) - 1
        obj = sistema["inventario"][indice]
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return

    print(f"\nObjeto seleccionado: {obj['nombre']}")

    # 🔹 Modificación de campos
    obj["nombre"] = input("Nuevo nombre (enter): ") or obj["nombre"]
    obj["clase"] = input("Nueva clase (enter): ") or obj["clase"]
    obj["categoria"] = input("Nueva categoría (enter): ") or obj["categoria"]
    obj["efectos"] = input("Nuevos efectos (enter): ") or obj["efectos"]

    # 🔹 Actualizar también en enciclopedia
    registrar_objeto(sistema, "inventario", obj, actualizar=True)

    estado.cambios_no_guardados = True
    print("✅ Objeto modificado correctamente en inventario y enciclopedia.")


# =========================
# ELIMINAR OBJETO
# =========================
def eliminar_objeto(sistema):
    inventario = sistema.get("inventario", [])
    if not inventario:
        print("❌ Inventario vacío.")
        return

    # Mostrar inventario
    for i, obj in enumerate(inventario, 1):
        print(f"{i}. {obj['nombre']}")

    try:
        index = int(input("Número del objeto a eliminar: ")) - 1
        obj = inventario[index]
    except (ValueError, IndexError):
        print("❌ Opción inválida.")
        return

    # Desactivar en enciclopedia usando ID
    desactivar_objeto(sistema, "inventario", obj["id"])

    # También lo quitamos del inventario
    inventario.pop(index)
    
    print(f"❌ Objeto '{obj['nombre']}' eliminado del inventario y desactivado en la enciclopedia.")



# =========================
# HELPER: Buscar objeto en enciclopedia
# =========================
def buscar_objeto_enciclopedia(obj_id, sistema, tipo):
    """Devuelve el objeto de la enciclopedia según su ID"""
    enc = sistema.get("enciclopedias", {}).get(tipo, [])
    for o in enc:
        if o["id"] == obj_id:
            return o
    return {}


# =========================
# MENÚ DE INVENTARIO
# =========================
def menu_inventario(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    while True:
        print("\n=== MENÚ DE INVENTARIO ===")
        print("1. Ver inventario")
        print("2. Buscar objeto 🔍")
        print("3. Añadir objeto")
        print("4. Modificar objeto")
        print("5. Eliminar objeto")
        print("6. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_inventario(sistema)
        elif opcion == "2":
            buscar_inventario(sistema)
        elif opcion == "3":
            añadir_objeto(sistema)
        elif opcion == "4":
            modificar_objeto(sistema)
        elif opcion == "5":
            eliminar_objeto(sistema)
        elif opcion == "6":
            guardar_sistema(sistema)
            break
        else:
            print("❌ Opción no válida.")

# 💡 COMENTARIOS PARA REPLICAR EN OTROS PLUGINS:
# 1. Cambiar todos los nombres de funciones y claves a la sección correspondiente.
#    Ejemplo: habilidades -> menu_habilidades, añadir_habilidad, etc.
# 2. Usar registrar_objeto/desactivar_objeto/reactivar_objeto para mantener todo en enciclopedia.
# 3. Para nuevas secciones como tienda, ruleta:
#    - Crear lista vacía en sistema y enciclopedia.
#    - Registrar objetos/elementos mediante registrar_objeto.
#    - Usar desactivar_objeto/reactivar_objeto para historial y log.
