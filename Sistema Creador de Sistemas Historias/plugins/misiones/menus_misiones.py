#plugins/misiones/menus_misiones.py
from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import pedir_int
from core.recompensas.bloques import menu_editar_bloque
from core.recompensas.tipos import RECURSOS_REGISTRADOS


from plugins.misiones.helpers_misiones import (
    crear_mision,
    obtener_mision,
    editar_datos_basicos,
    procesar_recompensas_objetivo,
    eliminar_mision_helper,
    completar_mision,
    fallar_mision,

)

from plugins.misiones.modelos import crear_modelo_objetivo


# --------------------------
# Selección de misión
# --------------------------
def seleccionar_mision(sistema, accion="modificar"):
    misiones = sistema.get("misiones", {}).get("activas", {})
    if not misiones:
        print(f"❌ No hay misiones para {accion}.")
        return None

    lista = list(misiones.values())
    print(f"\n=== MISIÓN A {accion.upper()} ===")
    for i, m in enumerate(lista, 1):
        print(f"{i}. {m.get('nombre', 'Sin nombre')}")

    seleccion = input("Elige misión por número o nombre (Enter para cancelar): ").strip()
    if not seleccion:
        return None

    if seleccion.isdigit():
        idx = int(seleccion) - 1
        if 0 <= idx < len(lista):
            return lista[idx]
    else:
        for m in lista:
            if m.get("nombre","").lower() == seleccion.lower():
                return m

    print("❌ Misión no encontrada.")
    return None

# --------------------------
# Menú crear misión
# --------------------------
def menu_crear_mision(sistema):
    print("\n" + "="*40)
    print("        CREAR NUEVA MISIÓN")
    print("="*40)

    id = input("🆔 ID única: ").strip()
    if not id:
        print("❌ ID obligatoria.")
        return

    nombre = input("📛 Nombre de la misión: ").strip()
    descripcion = input("📝 Descripción: ").strip()

    objetivos = []

    while True:
        print("\n" + "-"*30)
        print("➕ NUEVO OBJETIVO")
        print("-"*30)

        if input("¿Añadir objetivo? (s/n): ").lower() != "s":
            break

        desc = input("📌 Descripción del objetivo: ").strip()
        interno = input("¿Es interno? (s/n): ").lower() == "s"
        cantidad = pedir_int("🎯 Cantidad necesaria: ", default=1)

        obj = crear_modelo_objetivo(descripcion=desc, interno=interno)

        obj["estado_objetivo"] = "pendiente"
        obj["cantidad_base"] = cantidad
        obj["progreso"] = 0
        obj.setdefault("recompensas", {})
        obj.setdefault("penalizaciones", {})

        print("\n🎁 Configuración de recompensas:")
        if input("¿Añadir recompensas ahora? (s/n): ").lower() == "s":
            menu_editar_bloque(obj, "recompensas")

        print("\n⚠ Configuración de penalizaciones:")
        if input("¿Añadir penalizaciones ahora? (s/n): ").lower() == "s":
            menu_editar_bloque(obj, "penalizaciones")

        objetivos.append(obj)
        print("✅ Objetivo añadido correctamente.")

    m = crear_mision(
        sistema,
        id=id,
        nombre=nombre,
        descripcion=descripcion,
        objetivos=objetivos
    )

    if m:
        print(f"\n🎉 Misión '{nombre}' creada correctamente.")
    else:
        print(f"\n❌ Ya existe una misión con ID '{id}'.")

# --------------------------
# Menú modificar misión
# --------------------------
def modificar_mision(sistema, mision_id):
    mision = obtener_mision(sistema, mision_id)
    if not mision:
        print("❌ Misión no encontrada.")
        return

    while True:
        print(f"\n--- MODIFICAR MISIÓN {mision['nombre']} ---")
        print("1. Editar datos básicos")
        print("2. Editar objetivos")
        print("3. Volver")
        opcion = pedir_int("Elige opción: ", default=3)

        if opcion == 1:
            nombre = input(f"Nombre ({mision['nombre']}): ").strip() or mision['nombre']
            descripcion = input(f"Descripción ({mision['descripcion']}): ").strip() or mision['descripcion']
            editar_datos_basicos(mision, nombre=nombre, descripcion=descripcion)
            print("✅ Datos básicos actualizados.")

        elif opcion == 2:
            menu_editar_objetivos(mision)
        else:
            break

# --------------------------
# Menú objetivos
# --------------------------
def menu_editar_objetivos(mision):
    while True:
        print("\nObjetivos:")
        for idx, obj in enumerate(mision["objetivos"], 1):
            tipo = "Interno" if obj["interno"] else "Normal"
            print(f"{idx}. {obj['descripcion']} [{tipo}]")

        seleccion = input("Elige objetivo por número para editar (Enter para salir): ").strip()
        if not seleccion:
            break
        if not seleccion.isdigit() or int(seleccion)-1 >= len(mision["objetivos"]):
            print("❌ Objetivo no encontrado.")
            continue

        obj = mision["objetivos"][int(seleccion)-1]

        obj.setdefault("recompensas", {"objetos":[]})
        obj.setdefault("penalizaciones", {"objetos":[]})

        print(f"--- Editando objetivo: {obj['descripcion']} ---")
        nueva_desc = input(f"Descripción ({obj['descripcion']}): ").strip() or obj['descripcion']
        obj['descripcion'] = nueva_desc
        obj['cantidad_base'] = pedir_int(f"Cantidad necesaria ({obj['cantidad_base']}): ", default=obj['cantidad_base'])

        obj['interno'] = input(f"Interno? (s/n) [{ 's' if obj['interno'] else 'n'}]: ").lower() == "s"

        while True:
            print("1. Editar recompensas")
            print("2. Editar penalizaciones")
            print("3. Volver")
            opt = pedir_int("Opción: ", default=3)
            if opt == 1:
                menu_editar_bloque(obj, "recompensas")
            elif opt == 2:
                menu_editar_bloque(obj, "penalizaciones")
            else:
                break


def menu_modificar_progreso(mision):
    """
    Permite al usuario cambiar progreso de objetivos manualmente y gestionar recompensas.
    Gestiona estados: 'pendiente', 'pendiente_entrega', 'entregado'
    """
    print(f"\n=== Modificar progreso de {mision['nombre']} ===")

    for idx, obj in enumerate(mision['objetivos'], 1):
        prog = obj.get("progreso", 0)
        base = obj.get("cantidad_base", 1)
        estado_obj = obj.get("estado_objetivo", "pendiente")

        # Ignorar objetivos ya entregados
        if estado_obj == "entregado":
            print(f"{idx}. {obj['descripcion']} | Progreso actual: {prog}/{base} | Estado: entregado ✅ (no modificable)")
            continue  # saltar al siguiente objetivo
        
        print(f"{idx}. {obj['descripcion']} | Progreso actual: {prog}/{base} | Estado: {estado_obj}")

        nuevo = input("Nuevo progreso (Enter = mantener actual): ").strip()

        if nuevo:
            try:
                obj["progreso"] = max(0, int(nuevo))
            except ValueError:
                print("Valor no válido, se mantiene progreso actual.")
                continue  # pasa al siguiente objetivo

        prog = obj.get("progreso", 0)  # actualizar después de cambio

        # Detectar objetivo completado
        if prog >= base and estado != "entregado":
            print(f"\n🎯 Objetivo '{obj['descripcion']}' completado!")
            while True:
                print("¿Qué deseas hacer con este objetivo?")
                print("1. Entregar recompensas ahora")
                print("2. Dejar como pendiente de entrega")
                print("3. Modificar progreso manualmente")
                opcion = input("Elige opción (1/2/3): ").strip()
                
                if opcion == "1":
                    # Entregar recompensas y marcar como entregado
                    procesar_recompensas_objetivo(estado.sistema_actual, obj)
                    obj["estado_objetivo"] = "entregado"
                    print("✅ Recompensas entregadas.")
                    guardar_sistema(print_msg=False)
                    break
                elif opcion == "2":
                    obj["estado_objetivo"] = "pendiente_entrega"
                    print("⏳ Objetivo dejado pendiente de entrega.")
                    guardar_sistema(print_msg=False)
                    break
                elif opcion == "3":
                    # Permite modificar progreso de nuevo, deja estado pendiente
                    obj["estado_objetivo"] = "pendiente"
                    print("✏ Puedes seguir modificando el progreso de este objetivo.")
                    break
                else:
                    print("❌ Opción no válida, elige 1, 2 o 3.")

    estado.cambios_no_guardados = True
    print("✅ Progreso actualizado.")

# --------------------------
# Menú administración
# --------------------------
def menu_administrar_misiones(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    while True:
        print("\n=== ADMINISTRAR MISIONES ===")
        print("1. Crear nueva misión")
        print("2. Modificar misión")
        print("3. Eliminar misión")
        print("4. Volver")
        opcion = pedir_int("Opción: ", default=4)

        if opcion == 1:
            menu_crear_mision(sistema)
        elif opcion == 2:
            m = seleccionar_mision(sistema, "modificar")
            if m:
                modificar_mision(sistema, m["id"])
        elif opcion == 3:
            m = seleccionar_mision(sistema, "eliminar")
            if m:
                confirmar = input(f"¿Seguro que quieres eliminar {m['nombre']}? (s/n): ").lower()
                if confirmar == "s":
                    eliminar_mision_helper(sistema, m["id"])
                    print("✅ Eliminado.")
        else:
            break

# --------------------------
# Mostrar misiones y gestionar
# --------------------------
def mostrar_misiones(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    activas = sistema.get("misiones", {}).get("activas", {})
    misiones_list = list(activas.values())
    if not misiones_list:
        print("❌ No hay misiones activas.")
        return

    while True:
        print("\n=== MISIONES ===")
        for idx, m in enumerate(misiones_list, 1):
            print(f"{idx}. {m['nombre']}")

        seleccion = input("\nElige misión por número o nombre (Enter para salir): ").strip()
        if not seleccion:
            break

        mision = None
        if seleccion.isdigit():
            index = int(seleccion)-1
            if 0<=index<len(misiones_list):
                mision = misiones_list[index]
        else:
            for m in misiones_list:
                if m["nombre"].lower()==seleccion.lower():
                    mision = m
                    break

        if not mision:
            print("❌ Misión no encontrada.")
            continue

        gestion_mision(sistema, mision, misiones_list)

# --------------------------
# Gestión de una misión
# --------------------------
def gestion_mision(sistema, mision, misiones_list):
    while True:
        print(f"\n--- DETALLES DE {mision['nombre']} ---")
        print(f"ID: {mision['id']}")
        print(f"Descripción: {mision['descripcion']}")

        # Mostrar objetivos normales e internos
        normales = [o for o in mision["objetivos"] if not o["interno"]]
        internos = [o for o in mision["objetivos"] if o["interno"]]

        def imprimir_bloque(titulo, bloque):
            if not bloque:
                print(f"{titulo}: (vacío)")
                return
            print(f"{titulo}:")
            for tipo, items in bloque.items():
                # items puede ser dict o lista
                if isinstance(items, dict):
                    for nombre, valor in items.items():
                        destino = ""
                        if nombre in RECURSOS_REGISTRADOS:
                            destino = f" (destino: {RECURSOS_REGISTRADOS[nombre].get('destino')})"
                        # Para objetos guardamos cantidad dentro de dict
                        if isinstance(valor, dict) and "cantidad" in valor:
                            val_disp = valor["cantidad"]
                        elif isinstance(valor, dict) and "valor" in valor:
                            val_disp = valor.get("valor", 0)
                        else:
                            val_disp = valor
                        print(f"  - {tipo} | {nombre}: {val_disp}{destino}")
                elif isinstance(items, list):
                    for idx, item in enumerate(items):
                        print(f"  - {tipo} [{idx}]: {item}")
                else:
                    print(f"  - {tipo}: {items}")

        if normales:
            print("\nObjetivos normales:")
            for o in normales:
                print(f"  - {o['descripcion']} | Progreso: {o['progreso']}/{o['cantidad_base']} | Estado: {o.get('estado_objetivo','pendiente')}")
                imprimir_bloque("    Recompensas", o.get("recompensas", {}))
                imprimir_bloque("    Penalizaciones", o.get("penalizaciones", {}))

        if internos:
            print("\nObjetivos internos:")
            for o in internos:
                print(f"  - {o['descripcion']} | Progreso: {o['progreso']}/{o['cantidad_base']} | Estado: {o.get('estado_objetivo','pendiente')}")
                imprimir_bloque("    Recompensas", o.get("recompensas", {}))
                imprimir_bloque("    Penalizaciones", o.get("penalizaciones", {}))

        print("\n[P] Modificar Progreso   [C] Completar   [F] Fallar   [D] Eliminar   [Enter] Volver")
        accion = input("> ").strip().lower()


        if accion == "p":
            menu_modificar_progreso(mision)
        
        elif accion == "c":
            exito = completar_mision(sistema, mision["id"], forzar=True)
            if exito:
                misiones_list.remove(mision)
            else:
                print("🔹 La misión no se completó todavía.")
            break

        elif accion == "f":
            fallar_mision(sistema, mision["id"])
            misiones_list.remove(mision)
            print("❌ Fallada.")
            break

        elif accion == "d":
            confirmar = input("Confirmar eliminación (s/n): ").lower()
            if confirmar == "s":
                eliminar_mision_helper(sistema, mision["id"])
                misiones_list.remove(mision)
                print("✅ Eliminada.")
                break

        else:
            guardar_sistema(print_msg=False)
            break





