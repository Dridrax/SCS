#plugins/inventario/menus_inv.py
from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import pedir_int
from plugins.inventario.inventario import agregar_item, modificar_item, eliminar_item


# _________________________
# MENU AGREGAR ITEM
# _________________________
def menu_agregar_item():
    sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    if not sistema.get("plugins_activos", {}).get("inventario"):
        print("❌ El plugin inventario no está activo.")
        return

    # Aseguramos que exista el inventario
    sistema.setdefault("inventario", {})

    print("\n=== AÑADIR ITEM ===")
    nombre = input("Nombre del item: ").strip()
    rareza = input("Rareza: ").strip()
    tipo = input("Tipo: ").strip()
    descripcion = input("Descripción: ").strip()
    cantidad = pedir_int("Cantidad: ")

    efectos = {}
    if input("¿Tiene efectos? (s/n): ").lower() == "s":
        while True:
            key = input("Efecto (enter para terminar): ").strip()
            if not key:
                break
            valor = pedir_int(f"Valor de {key}: ")
            efectos[key] = valor

    item_id = agregar_item(sistema, {
        "nombre": nombre,
        "rareza": rareza,
        "tipo": tipo,
        "descripcion": descripcion,
        "cantidad": cantidad,
        "efectos": efectos
    })

    print(f"\n✅ Item '{nombre}' añadido con ID {item_id}.\n")
    guardar_sistema()
    estado.cambios_no_guardados = True
    

# _________________________
# MENU MODIFICAR ITEM
# _________________________
def menu_modificar_item():
    sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    inventario = sistema.get("inventario", {})
    if not inventario:
        print("❌ No hay items en el inventario.")
        return

    while True:
        print("\n=== MODIFICAR ITEM ===")
        items = list(inventario.values())
        for i, item in enumerate(items, 1):
            print(f"{i}. {item['nombre']} | Rareza: {item['rareza']} | Cantidad: {item['cantidad']}")
        print(f"{len(items)+1}. Volver")

        entrada = input("\nSelecciona un item por número o nombre: ").strip()
        if entrada == str(len(items)+1) or entrada.lower() == "volver":
            break

        # Selección por número
        item_sel = None
        if entrada.isdigit():
            idx = int(entrada) - 1
            if 0 <= idx < len(items):
                item_sel = items[idx]
        # Selección por nombre
        else:
            for item in items:
                if item['nombre'].lower() == entrada.lower():
                    item_sel = item
                    break

        if not item_sel:
            print("❌ Item no encontrado.")
            continue

        # Pedir nuevos valores (enter para mantener valor actual)
        print(f"\nModificando '{item_sel['nombre']}' (enter para mantener el valor actual)")
        nombre = input(f"Nombre [{item_sel['nombre']}]: ").strip() or item_sel['nombre']
        rareza = input(f"Rareza [{item_sel['rareza']}]: ").strip() or item_sel['rareza']
        tipo = input(f"Tipo [{item_sel['tipo']}]: ").strip() or item_sel['tipo']
        descripcion = input(f"Descripción [{item_sel['descripcion']}]: ").strip() or item_sel['descripcion']

        # NUEVO: manejar cantidad como int y permitir eliminar si <=0
        cantidad_input = input(f"Cantidad [{item_sel['cantidad']}]: ").strip()
        cantidad = int(cantidad_input) if cantidad_input.isdigit() else item_sel['cantidad']

        # Modificar efectos
        efectos = item_sel.get("efectos", {}).copy()
        if input("¿Modificar efectos? (s/n): ").lower() == "s":
            efectos.clear()
            while True:
                k = input("Nombre del efecto (enter para terminar): ").strip()
                if not k:
                    break
                v = pedir_int("Valor del efecto: ")
                efectos[k] = v

        # Llamar a la función principal
        modificar_item(sistema, item_sel['id'], {
            "nombre": nombre,
            "rareza": rareza,
            "tipo": tipo,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "efectos": efectos
        })

        # Si la cantidad quedó ≤0, quitamos el item de la lista del menú
        if cantidad <= 0:
            print(f"\nItem '{item_sel['nombre']}' eliminado por tener cantidad 0.")
            items.remove(item_sel)
# _________________________
# MENU ELIMINAR ITEM
# _________________________
def menu_eliminar_item(sistema, item_id, cantidad=1):
    """
    Elimina un item del inventario.
    - sistema: dict del sistema actual
    - item_id: id del item a eliminar
    - cantidad: cantidad a eliminar (default 1)
    
    Si la cantidad es menor que la existente, se resta.
    Si la cantidad es mayor o igual, se elimina por completo.
    """
    inventario = sistema.get("inventario", {})

    if item_id not in inventario:
        print(f"❌ No se encontró el item con ID '{item_id}'.")
        return False

    item = inventario[item_id]
    if item.get("cantidad", 1) > cantidad:
        item["cantidad"] -= cantidad
        print(f"✅ Se eliminaron {cantidad} de '{item['nombre']}'. Quedan {item['cantidad']}.")
    else:
        del inventario[item_id]
        print(f"✅ Item '{item['nombre']}' eliminado del inventario.")

    # Actualizar plugin_cache
    if "plugins" in estado.plugin_cache:
        plugin_inv = estado.plugin_cache.setdefault("plugins", {}).setdefault("inventario", {})
        if item_id in plugin_inv:
            if item_id in inventario:
                plugin_inv[item_id] = inventario[item_id]
            else:
                del plugin_inv[item_id]

    estado.cambios_no_guardados = True
    return True

# _________________________
# MOSTRAR ITEM
# _________________________
def mostrar_items(sistema=None):
    """
    Muestra los items del inventario del sistema.
    Permite seleccionar un item por número o por nombre para ver sus detalles.
    Dentro del detalle del item, permite Modificar (M) o Eliminar (D) con confirmación.
    """
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    inventario = sistema.get("inventario", {})
    if not inventario:
        print("❌ No hay items en el inventario.")
        return

    # Lista ordenada de items
    items_list = list(inventario.values())

    while True:
        print("\n=== INVENTARIO ===")
        for idx, item in enumerate(items_list, 1):
            print(f"{idx}. {item['nombre']} | Rareza: {item['rareza']} | Cantidad: {item['cantidad']}")

        seleccion = input("\nElige un item por número o nombre (Enter para salir): ").strip()
        if not seleccion:
            break

        # Selección por número
        item_obj = None
        if seleccion.isdigit():
            index = int(seleccion) - 1
            if 0 <= index < len(items_list):
                item_obj = items_list[index]
            else:
                print("❌ Número inválido.")
                continue
        else:
            # Selección por nombre
            for item in items_list:
                if item['nombre'].lower() == seleccion.lower():
                    item_obj = item
                    break
            if item_obj is None:
                print("❌ No se encontró ningún item con ese nombre.")
                continue

        # Función interna para modificar item
        def editar_item_interactivo(item):
            nuevos_datos = {}
            nuevos_datos["nombre"] = input(f"Nuevo nombre ({item['nombre']}): ") or item['nombre']
            nuevos_datos["rareza"] = input(f"Nueva rareza ({item['rareza']}): ") or item['rareza']
            nuevos_datos["tipo"] = input(f"Nuevo tipo ({item['tipo']}): ") or item['tipo']
            nuevos_datos["descripcion"] = input(f"Nueva descripción ({item['descripcion']}): ") or item['descripcion']
            nuevos_datos["cantidad"] = pedir_int(f"Nueva cantidad ({item['cantidad']}): ") or item['cantidad']

            # Editar efectos
            efectos = item.get("efectos", {}).copy()
            if input("¿Modificar efectos? (s/n): ").lower() == "s":
                efectos.clear()
                while True:
                    k = input("Nombre del efecto (enter para terminar): ").strip()
                    if not k:
                        break
                    v = pedir_int(f"Valor del efecto {k}: ")
                    efectos[k] = v
            nuevos_datos["efectos"] = efectos

            modificar_item(sistema, item['id'], nuevos_datos)
            estado.cambios_no_guardados = True
            guardar_sistema()
            print(f"✅ Item '{nuevos_datos['nombre']}' modificado.")

        # Función interna para eliminar item
        def eliminar_item_interactivo(item):
            print(f"Cantidad actual de '{item['nombre']}': {item['cantidad']}")
            cantidad = pedir_int("Cantidad a eliminar: ")
            if cantidad <= 0:
                print("❌ Operación cancelada.")
                return
            confirmar = input(f"⚠️ ¿Eliminar {cantidad} de '{item['nombre']}'? (s/n): ").lower()
            if confirmar == "s":
                eliminar_item(sistema, item['id'], cantidad)
                if item.get("cantidad", 0) <= 0:
                    items_list.remove(item)
                estado.cambios_no_guardados = True
                guardar_sistema()
                print(f"✅ Item '{item['nombre']}' actualizado.")

        # Mostrar detalles del item
        while True:
            print("\n--- DETALLES DEL ITEM ---")
            print(f"ID: {item_obj['id']}")
            print(f"Nombre: {item_obj['nombre']}")
            print(f"Rareza: {item_obj['rareza']}")
            print(f"Tipo: {item_obj['tipo']}")
            print(f"Descripción: {item_obj['descripcion']}")
            print(f"Cantidad: {item_obj['cantidad']}")
            print("Efectos:")
            if item_obj.get("efectos"):
                for k, v in item_obj["efectos"].items():
                    print(f"  - {k}: {v}")
            else:
                print("  Ninguno")

            print("\n[M] Modificar objeto   [D] Eliminar objeto   [Enter] Volver")
            accion = input("> ").strip().lower()

            if accion == "m":
                editar_item_interactivo(item_obj)
            elif accion == "d":
                eliminar_item_interactivo(item_obj)
                break  # Volvemos al inventario después de eliminar
            else:
                break  # Volvemos al inventario
