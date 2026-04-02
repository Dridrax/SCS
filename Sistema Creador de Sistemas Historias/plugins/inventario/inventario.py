#plugins/inventario/inventario.py
from core.estado_global import estado
from core.utils.busqueda import buscar
from core.recompensas.tipos import asignar_rareza

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
# GENERAR FIRMA DEL OBJETO
# =========================
def generar_firma_objeto(item_data):
    """
    Genera una firma única del objeto (incluye valor).
    """
    nombre = item_data.get("nombre", "").strip().lower()
    rareza = item_data.get("rareza", "").strip().lower()
    tipo = item_data.get("tipo", "").strip().lower()
    descripcion = item_data.get("descripcion", "").strip().lower()

    efectos = item_data.get("efectos", {})
    efectos_firma = tuple(sorted((k.lower(), v) for k, v in efectos.items()))

    valor = item_data.get("valor")
    if isinstance(valor, dict):
        valor_firma = (valor.get("tipo", "").lower(), valor.get("cantidad", 0))
    else:
        valor_firma = None

    return (nombre, rareza, tipo, descripcion, efectos_firma, valor_firma)

# =========================
# AGREGAR ITEM REHECHO
# =========================
def agregar_item(sistema, item_data):
    """
    Agrega un item al inventario del sistema.
    Si un objeto idéntico ya existe, incrementa su cantidad en lugar de crear uno nuevo.
    La rareza se respeta desde item_data o se asigna automáticamente si no existe.
    """
    if "inventario" not in sistema or sistema["inventario"] is None:
        sistema["inventario"] = {}

    inventario = sistema["inventario"]
    cantidad_nueva = max(1, item_data.get("cantidad", 1))

    # Generar la firma del objeto (ignora cantidad)
    firma_nueva = generar_firma_objeto(item_data)

    # Buscar objeto idéntico
    for obj_id, obj in inventario.items():
        if generar_firma_objeto(obj) == firma_nueva:
            # Sumar cantidad
            obj["cantidad"] = obj.get("cantidad", 0) + cantidad_nueva

            # Solo aseguramos rareza válida (sin interacción)
            asignar_rareza(obj, item_data.get("rareza"))

            # Actualizar plugin_cache
            estado.plugin_cache.setdefault("plugins", {}).setdefault("inventario", {})[obj_id] = obj
            estado.cambios_no_guardados = True
            return obj_id

    # Crear nuevo objeto con cantidad correcta
    item_id = str(uuid.uuid4())
    item_nuevo = {
        "id": item_id,
        **item_data,
        "cantidad": cantidad_nueva
    }

    # Asignar rareza si no viene en item_data
    asignar_rareza(item_nuevo, item_data.get("rareza"))

    inventario[item_id] = item_nuevo
    estado.plugin_cache.setdefault("plugins", {}).setdefault("inventario", {})[item_id] = item_nuevo
    estado.cambios_no_guardados = True
    return item_id

# =========================
# MODIFICAR ITEM REHECHO
# =========================
def modificar_item(sistema, item_id, nuevos_datos):
    """
    Modifica un item existente en el inventario del sistema.
    - sistema: dict del sistema actual
    - item_id: id del item a modificar
    - nuevos_datos: dict con campos a actualizar

    Si la cantidad final es <= 0, elimina el item automáticamente.
    La rareza se respeta desde nuevos_datos o se mantiene la existente.
    """
    inventario = sistema.setdefault("inventario", {})

    if item_id not in inventario:
        print(f"❌ No se encontró el item con ID '{item_id}'.")
        return False

    item = inventario[item_id]

    # Comprobar cantidad antes de actualizar
    if "cantidad" in nuevos_datos and nuevos_datos["cantidad"] <= 0:
        return eliminar_item(sistema, item_id)

    # Actualizar campos
    item.update(nuevos_datos)

    # Asignar rareza solo para validar o completar si no existe
    asignar_rareza(item, nuevos_datos.get("rareza"))

    # Actualizar plugin_cache
    estado.plugin_cache.setdefault("plugins", {}).setdefault("inventario", {})[item_id] = item

    estado.cambios_no_guardados = True
    print(f"✅ Item '{item.get('nombre', item_id)}' modificado correctamente.")
    return True

# =========================
# ELIMINAR OBJETO
# =========================
def eliminar_item(sistema, item_id, cantidad=None):
    """
    Elimina un item o reduce su cantidad en el inventario.
    - sistema: dict del sistema actual
    - item_id: id del item a eliminar
    - cantidad: cantidad a eliminar (default None = eliminar todo)

    Si la cantidad es menor que la existente, se resta.
    Si la cantidad es mayor o igual, se elimina por completo.
    """
    inventario = sistema.get("inventario", {})

    if item_id not in inventario:
        print(f"❌ No se encontró el item con ID '{item_id}'.")
        return False

    item = inventario[item_id]

    if cantidad is None or cantidad >= item.get("cantidad", 1):
        # eliminar el item por completo
        del inventario[item_id]
        print(f"✅ Item '{item['nombre']}' eliminado del inventario.")
    else:
        # restar cantidad
        item["cantidad"] -= cantidad
        print(f"✅ Se eliminaron {cantidad} de '{item['nombre']}'. Quedan {item['cantidad']}.")

    # Actualizar plugin_cache si existe
    if "plugins" in estado.plugin_cache:
        plugin_inv = estado.plugin_cache.setdefault("plugins", {}).setdefault("inventario", {})
        if item_id in plugin_inv:
            if item_id in inventario:
                plugin_inv[item_id] = inventario[item_id]
            else:
                del plugin_inv[item_id]

    estado.cambios_no_guardados = True
    return True

# =========================
# VENDER ITEM
# =========================
def vender_item(sistema, item_id, cantidad=1):
    """
    Vende un item del inventario y otorga recompensa automáticamente,
    ahora manejando subtipos de dinero o tiradas.
    """
    inventario = sistema.get("inventario", {})

    if item_id not in inventario:
        print("❌ Item no encontrado.")
        return False

    item = inventario[item_id]

    if not puede_vender_item(item):
        print(f"❌ El item '{item['nombre']}' no se puede vender.")
        return False

    cantidad = max(1, cantidad)
    if item.get("cantidad", 1) < cantidad:
        print(f"❌ No tienes suficiente cantidad de '{item['nombre']}'.")
        return False

    valor = item["valor"]
    tipo = valor["tipo"]
    valor_unitario = valor["cantidad"]
    total = valor_unitario * cantidad

    # Eliminar item
    eliminar_item(sistema, item_id, cantidad)

    # Aplicar recompensa
    if tipo in ["dinero", "tiradas"]:
        sistema.setdefault(tipo, {})
        subtipo = valor.get("subtipo")  # usar el subtipo ya definido en el item
        if not subtipo:
            subtipo = "Común"  # fallback por si acaso
        sistema[tipo][subtipo] = sistema[tipo].get(subtipo, 0) + total

    elif tipo == "puntos_stats":
        sistema["puntos_stats"] = sistema.get("puntos_stats", 0) + total

    elif tipo == "puntos_habilidad":
        sistema["puntos_habilidad"] = sistema.get("puntos_habilidad", 0) + total

    else:
        sistema[tipo] = sistema.get(tipo, 0) + total

    #print(f"💰 Vendido '{item['nombre']}' x{cantidad} → +{total} {tipo}")
    estado.cambios_no_guardados = True
    return True

def puede_vender_item(item):
    """
    Comprueba si un item se puede vender.
    Requiere que tenga campo 'valor' válido.
    """
    if not isinstance(item, dict):
        return False

    valor = item.get("valor")
    if not valor or not isinstance(valor, dict):
        return False

    if "tipo" not in valor or "cantidad" not in valor:
        return False

    return True

def seleccionar_subtipo_recurso(sistema, tipo):
    """
    Permite seleccionar un subtipo existente de un recurso base o crear uno nuevo.
    Solo se permiten los recursos base: puntos_stats, puntos_habilidad, dinero, tiradas.
    Retorna el subtipo seleccionado, o None si se cancela.
    """
    RECURSOS_PERMITIDOS = {"puntos_stats", "puntos_habilidad", "dinero", "tiradas"}

    if tipo not in RECURSOS_PERMITIDOS:
        print(f"❌ El tipo '{tipo}' no está permitido para este menú.")
        return None

    # Detectar si el recurso tiene subtipos (dict) o es un valor directo
    recursos = sistema.get(tipo, {})
    tiene_subtipos = isinstance(recursos, dict)

    # Si no hay subtipos, simplemente devolver el tipo como subtipo
    if not tiene_subtipos:
        return tipo

    # Si hay subtipos, mostrar menú como antes
    if recursos:
        print(f"\nSubtipos existentes de {tipo}:")
        for i, key in enumerate(recursos.keys(), 1):
            print(f"{i}. {key} ({recursos[key]})")
    else:
        print(f"\nNo hay subtipos definidos para {tipo} aún.")

    print(f"{len(recursos)+1}. Crear nuevo subtipo")
    print("Presiona Enter para cancelar la selección.")

    opcion = input("Elige subtipo o crea uno nuevo: ").strip()

    if opcion == "":
        print("⚠️ Selección cancelada.")
        return None  # Cancelar selección si Enter

    if opcion.isdigit():
        opcion = int(opcion)
        if 1 <= opcion <= len(recursos):
            return list(recursos.keys())[opcion-1]
        elif opcion == len(recursos)+1:
            nuevo = input("Nombre del nuevo subtipo: ").strip()
            if nuevo:
                return nuevo
            else:
                return None
    else:
        return opcion  # nombre escrito manualmente

    return None

