# plugins/misiones/helpers_misiones.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.recompensas.aplicar import aplicar_recompensas
from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
from core.recompensas.tipos import RECURSOS_REGISTRADOS
from core.utils.funciones_utiles import sync_plugin_cache
from core.recompensas.validacion import manejar_conflictos_objetivo
from plugins.misiones.modelos import crear_modelo_mision

# -----------------------------
# Infraestructura
# -----------------------------
def asegurar_misiones(sistema):
    sistema.setdefault("misiones", {})
    sistema["misiones"].setdefault("activas", {})
    sistema["misiones"].setdefault("historial", {})

# -----------------------------
# Crear / Obtener / Eliminar
# -----------------------------
def crear_mision(sistema, *, id, nombre, descripcion="", objetivos=None):
    if not sistema:
        return None

    asegurar_misiones(sistema)
    if id in sistema["misiones"]["activas"]:
        return None

    mision = crear_modelo_mision(
        id=id,
        nombre=nombre,
        descripcion=descripcion,
        objetivos=objetivos
    )
    sistema["misiones"]["activas"][id] = mision
    estado.cambios_no_guardados = True
    sync_plugin_cache(sistema, "misiones", ["activas"])
    guardar_sistema()
    return mision

def obtener_mision(sistema, mision_id):
    asegurar_misiones(sistema)
    return sistema["misiones"]["activas"].get(mision_id)

def eliminar_mision_helper(sistema, mision_id):
    asegurar_misiones(sistema)
    if mision_id in sistema["misiones"]["activas"]:
        del sistema["misiones"]["activas"][mision_id]
        estado.cambios_no_guardados = True
        sync_plugin_cache(sistema, "misiones", ["activas"])
        guardar_sistema()
        return True
    return False

# -----------------------------
# Editar datos básicos
# -----------------------------
def editar_datos_basicos(mision, *, nombre=None, descripcion=None):
    if nombre: mision["nombre"] = nombre
    if descripcion: mision["descripcion"] = descripcion
    estado.cambios_no_guardados = True
    return mision

# -----------------------------
# Progreso / Completado
# -----------------------------
def marcar_progreso_objetivo(objetivo, cantidad):
    """
    Suma progreso de forma segura y gestiona niveles escalados.
    """
    if cantidad <= 0:
        return False

    objetivo.setdefault("nivel", 0)
    objetivo.setdefault("progreso", 0)

    objetivo["progreso"] += cantidad

    cantidad_requerida = int(objetivo["cantidad_base"] * (objetivo.get("factor_escalado", 1) ** objetivo["nivel"]))

    if objetivo["progreso"] >= cantidad_requerida:
        objetivo["progreso"] = cantidad_requerida
        return True

    return False

def procesar_recompensas_objetivo(sistema, objetivo, mision=None):

    recompensas = objetivo.get("recompensas")

    if not recompensas:
        print(f"⚠ Objetivo '{objetivo['descripcion']}' no tiene recompensas.")
        return "cancelado"

    accion = manejar_conflictos_objetivo(objetivo)

    if accion == "cancelar":
        print(f"🔹 Entrega de recompensas de '{objetivo['descripcion']}' cancelada.")
        return "cancelado"

    if accion == "eliminar_objetivo":

        if mision and objetivo in mision.get("objetivos", []):
            mision["objetivos"].remove(objetivo)

            print(f"✅ Objetivo eliminado de la misión '{mision['nombre']}'.")
            return "objetivo_eliminado"

        return "objetivo_eliminado"

    if accion == "activar_plugins":
        return procesar_recompensas_objetivo(sistema, objetivo, mision)

    from core.recompensas.validacion import filtrar_recompensas_validas_entidad

    objetivo_filtrado = filtrar_recompensas_validas_entidad(objetivo)

    recompensas_preparadas = {}

    for tipo, items in objetivo_filtrado.get("recompensas", {}).items():

        if isinstance(items, dict):

            recompensas_preparadas[tipo] = {}

            destino_principal = RECURSOS_REGISTRADOS.get(tipo, {}).get("destino")

            for nombre, valor in items.items():

                if isinstance(valor, dict):
                    val_disp = (
                        valor.get("valor_base")
                        or valor.get("valor")
                        or valor.get("cantidad")
                        or 0
                    )
                else:
                    val_disp = valor

                if destino_principal:

                    recompensas_preparadas[tipo][nombre] = {
                        "valor": val_disp,
                        "destino": destino_principal
                    }

                else:

                    recompensas_preparadas[tipo][nombre] = val_disp

        elif isinstance(items, list):

            lista_objetos = []

            for item in items:
                obj_copy = item.copy()
                obj_copy.setdefault("cantidad", 1)
                lista_objetos.append(obj_copy)

            recompensas_preparadas[tipo] = lista_objetos

        else:

            recompensas_preparadas[tipo] = items

    aplicar_recompensas(
        sistema,
        preparar_recompensa_para_aplicar(sistema, recompensas_preparadas)
    )

    print(f"\n✅ Recompensas del objetivo '{objetivo['descripcion']}' aplicadas correctamente.")

    return "aplicado"

def completar_mision(sistema, mision_id, forzar=False):
    """
    Completa una misión interactiva considerando los estados de los objetivos:
    - Pregunta por entrega de recompensas pendientes objetivo por objetivo.
    - Evita duplicar recompensas.
    - Maneja objetivos incompletos y entrega forzada si se desea.
    """

    mision = obtener_mision(sistema, mision_id)
    if not mision:
        print("❌ Misión no encontrada.")
        return False

    objetivos = mision["objetivos"]

    # 1️⃣ Revisar objetivos incompletos
    incompletos = [o for o in objetivos if o.get("progreso", 0) < o.get("cantidad_base", 1)]
    pendientes_entrega = [o for o in objetivos if o.get("estado_objetivo") == "pendiente_entrega"]

    # 2️⃣ Preguntar al usuario por objetivos incompletos si no se fuerza
    if incompletos and not forzar:
        print("⚠ Hay objetivos incompletos:")
        for o in incompletos:
            print(f"  - {o['descripcion']} | {o.get('progreso',0)}/{o.get('cantidad_base',1)}")

        confirmar = input("¿Quieres forzar la misión y decidir sobre los objetivos incompletos? (s/n): ").lower()
        if confirmar != "s":
            print("🔹 La misión no se completó.")
            return False

        forzar = True

    # 3️⃣ Entrega objetivos pendientes de manera individual
    for obj in list(objetivos):  # ⚠ iterar copia para evitar errores si se elimina
        if obj.get("estado_objetivo") in ["pendiente_entrega", "completado"]:

            if obj.get("progreso", 0) >= obj.get("cantidad_base", 1) or forzar:

                if obj.get("estado_objetivo") != "entregado":

                    print(f"\nObjetivo: {obj['descripcion']}")
                    respuesta = input("¿Deseas entregar esta recompensa ahora? (s/n): ").lower()

                    if respuesta == "s":

                        resultado = procesar_recompensas_objetivo(sistema, obj, mision)
                        print(f"[DEBUG] Procesando objetivo: {o['descripcion']}")

                        if resultado == "objetivo_eliminado":

                            incompletos_restantes = [
                                obj for obj in mision["objetivos"]
                                if obj.get("progreso", 0) < obj.get("cantidad_base", 1)
                            ]

                            continue

                        if resultado == "cancelado":
                            continue

                        obj["estado_objetivo"] = "entregado"

                        print(f"✅ Recompensas del objetivo '{obj['descripcion']}' entregadas.")

                    else:

                        obj["estado_objetivo"] = "pendiente_entrega"
                        print(f"🔹 Objetivo '{obj['descripcion']}' queda pendiente de entrega.")

    # 4️⃣ Revisar objetivos incompletos restantes
    incompletos_restantes = [
        o for o in list(objetivos)
        if o.get("progreso",0) < o.get("cantidad_base",1)
    ]

    if incompletos_restantes:

        print("\n⚠ Algunos objetivos siguen incompletos al finalizar la misión:")

        for o in list(incompletos_restantes):

            print(f"  - {o['descripcion']} | {o.get('progreso',0)}/{o.get('cantidad_base',1)}")

            respuesta = input(
                "¿Deseas entregar la recompensa de todas formas o perderla? (s = entregar / n = perder): "
            ).lower()

            if respuesta == "s":

                resultado = procesar_recompensas_objetivo(sistema, o, mision)

                if resultado == "objetivo_eliminado":
                    continue

                if resultado == "cancelado":
                    continue

                o["estado_objetivo"] = "entregado"

                print(f"✅ Recompensas del objetivo '{o['descripcion']}' entregadas aunque incompleto.")

            else:

                print(f"❌ Recompensas del objetivo '{o['descripcion']}' perdidas.")

    # 5️⃣ Marcar misión como completada y mover a historial
    sistema["misiones"]["historial"][mision_id] = {**mision, "estado": "completada"}

    if mision_id in sistema["misiones"]["activas"]:
        del sistema["misiones"]["activas"][mision_id]

    estado.cambios_no_guardados = True

    sync_plugin_cache(sistema, "misiones", ["activas", "historial"])

    guardar_sistema()

    print("\n🏆 Misión completada y recompensas procesadas según elección.")

    return True

def fallar_mision(sistema, mision_id):
    mision = obtener_mision(sistema, mision_id)
    if not mision:
        return False

    for obj in mision["objetivos"]:
        if obj.get("progreso", 0) < obj.get("cantidad_base", 1):
            if obj.get("penalizaciones"):
                penal = obj["penalizaciones"]
                if penal:
                    from core.recompensas.aplicar import aplicar_recompensas
                    from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
                    aplicar_recompensas(sistema, preparar_recompensa_para_aplicar(sistema, penal))
            obj["estado_objetivo"] = "fallado"
        else:
            obj["estado_objetivo"] = "completado"

    sistema.setdefault("misiones", {}).setdefault("historial", {})[mision_id] = {**mision, "estado": "fallada"}
    if mision_id in sistema.get("misiones", {}).get("activas", {}):
        del sistema["misiones"]["activas"][mision_id]

    estado.cambios_no_guardados = True
    from core.utils.funciones_utiles import sync_plugin_cache
    sync_plugin_cache(sistema, "misiones", ["activas", "historial"])
    from core.guardado.archivos import guardar_sistema
    guardar_sistema()
    return True

# -----------------------------
# Mostrar resultados
# -----------------------------
def imprimir_resultados(titulo, datos):
    print(f"{titulo}:")
    if not datos:
        print("  Ninguna")
        return
    for clave, valor in datos.items():
        if clave == "objetos":
            print("  Objetos:")
            for obj in valor:
                print(f"    - {obj.get('nombre','Desconocido')} | Cantidad: {obj.get('cantidad',0)} | Rareza: {obj.get('rareza','?')} | Tipo: {obj.get('tipo','?')}")
        else:
            print(f"  {clave}: {valor}")

"""def completar_mision(sistema, mision_id, objetivos_ids=None):
    
    Completa una misión interactiva:
    - Permite modificar progreso de objetivos.
    - Pregunta si se quiere completar la misión.
    - Permite forzar completado si hay objetivos incompletos, con entrega selectiva de recompensas.
    
    mision = obtener_mision(sistema, mision_id)
    if not mision:
        print("❌ Misión no encontrada.")
        return False

    objetivos = mision["objetivos"]
    # Filtrar si se pasan objetivos_ids
    if objetivos_ids:
        objetivos = [o for o in objetivos if o["id"] in objetivos_ids]

    # 1️⃣ Modificar progreso de objetivos
    print(f"\n=== Objetivos de {mision['nombre']} ===")
    for idx, obj in enumerate(objetivos, 1):
        actual = obj.get("progreso", 0)
        base = obj.get("cantidad_base", 1)
        print(f"{idx}. {obj['descripcion']} | Progreso: {actual}/{base} | Nivel: {obj.get('nivel',0)}")
        # Permitir modificar progreso manualmente
        nuevo = input(f"   Nuevo progreso (Enter = mantener {actual}): ").strip()
        if nuevo:
            try:
                nuevo_val = int(nuevo)
                if nuevo_val < 0:
                    nuevo_val = 0
                obj["progreso"] = nuevo_val
            except ValueError:
                print("   ❌ Valor no válido, se mantiene el progreso actual.")

    estado.cambios_no_guardados = True

    # 2️⃣ Verificar si todos los objetivos están completos
    todos_completados = all(o.get("progreso",0) >= o.get("cantidad_base",1) for o in objetivos)

    # 3️⃣ Preguntar al usuario si quiere completar la misión
    if todos_completados:
        completar = input("\n✅ Todos los objetivos completos. ¿Deseas completar la misión y entregar recompensas? (s/n): ").lower()
        if completar != "s":
            print("🔹 La misión no se completará aún.")
            return False
    else:
        # Forzar completado de misión
        forzar = input("\n⚠ Algunos objetivos no están completos. ¿Deseas forzar la finalización de la misión? (s/n): ").lower()
        if forzar != "s":
            print("🔹 La misión no se completará aún.")
            return False
        # Opciones de entrega de recompensas
        entregar = input("¿Deseas entregar todas las recompensas ahora? (s = todas / n = solo las automáticas completadas): ").lower()
        entregar_todo = entregar == "s"

    # 4️⃣ Procesar recompensas de objetivos
    for obj in objetivos:
        prog = obj.get("progreso",0)
        base = obj.get("cantidad_base",1)
        # Entrega automática si está marcado
        if obj.get("entregar_al_completar") and prog >= base:
            procesar_recompensas_objetivo(sistema, obj)
        # Entregar todas si se fuerza
        elif not todos_completados and forzar and entregar_todo:
            procesar_recompensas_objetivo(sistema, obj)
        # Si ya estaban completados y no forzamos, opcionalmente podrían pedirse

    # 5️⃣ Guardar misión en historial y eliminar de activas
    sistema["misiones"]["historial"][mision_id] = {**mision, "estado":"completada"}
    del sistema["misiones"]["activas"][mision_id]

    estado.cambios_no_guardados = True
    sync_plugin_cache(sistema, "misiones", ["activas","historial"])
    guardar_sistema()
    print("🏆 Misión completada y recompensas aplicadas según elección.")
    return True"""