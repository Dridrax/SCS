from core.estado_global import estado
from core.utils.busqueda import buscar
from core.guardado.archivos import guardar_sistema

import uuid


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
# AÑADIR ITEM
# =========================
def agregar_item(sistema, item_data):
    """Agrega un item al inventario del sistema.
    - sistema: diccionario del sistema
    - item_data: dict con keys: nombre, rareza, tipo, descripcion, cantidad, efectos

    Parámetros obligatorios:
    - nombre (str)
    - rareza (str)
    - tipo (str)

    Parámetros opcionales:
    - descripcion (str)
    - efectos (dict)
    - cantidad (int)
    - metadata (dict) -> para expansión futura
    """

    if "inventario" not in sistema or sistema["inventario"] is None:
        sistema["inventario"] = {}

    inventario = sistema["inventario"]
    item_id = str(uuid.uuid4())  # ID único para cada item

    # Guardar en JSON principal
    inventario[item_id] = {
        "id": item_id,
        **item_data
    }

    # Guardar también en plugin_cache
    if "plugins" not in estado.plugin_cache:
        estado.plugin_cache["plugins"] = {}
    if "inventario" not in estado.plugin_cache["plugins"]:
        estado.plugin_cache["plugins"]["inventario"] = {}

    estado.plugin_cache["plugins"]["inventario"][item_id] = inventario[item_id]

    # Marcar cambios no guardados
    estado.cambios_no_guardados = True

    return item_id

# =========================
# MODIFICAR OBJETO
# =========================
def modificar_item(sistema, item_id, nuevos_datos):
    """
    Modifica un item existente en el inventario del sistema.
    - sistema: dict del sistema actual
    - item_id: id del item a modificar
    - nuevos_datos: dict con campos a actualizar
    """
    inventario = sistema.setdefault("inventario", {})
    
    if item_id not in inventario:
        print(f"❌ No se encontró el item con ID '{item_id}'.")
        return False

    # Actualizamos solo los campos que se pasen en nuevos_datos
    inventario[item_id].update(nuevos_datos)
    estado.cambios_no_guardados = True
    print(f"✅ Item '{inventario[item_id].get('nombre', item_id)}' modificado correctamente.")
    return True

# =========================
# ELIMINAR OBJETO
# =========================
def eliminar_item(sistema, item_id):
    """
    Elimina un item del inventario.
    - sistema: dict del sistema actual
    - item_id: id del item a eliminar
    """
    inventario = sistema.get("inventario", {})
    
    if item_id not in inventario:
        print(f"❌ No se encontró el item con ID '{item_id}'.")
        return False

    nombre = inventario[item_id].get("nombre", item_id)
    del inventario[item_id]
    estado.cambios_no_guardados = True
    print(f"✅ Item '{nombre}' eliminado del inventario.")
    return True


