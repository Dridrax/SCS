from core.estado_global import estado
from core.recompensas.tipos import (
    RECURSOS_REGISTRADOS,
    RECURSOS_BASE,
    RECURSOS_BASE_ACTIVOS,
    es_tipo_recompensa_valido
)

# ─────────────────────────────
# Función interna para recorrer recompensas y penalizaciones
# ─────────────────────────────
def _recorrer_recompensas_dict(recompensas: dict):
    """
    Genera todos los elementos individuales de recompensas o penalizaciones,
    devolviendo dicts con 'tipo' y 'plugin' (si aplica).
    """
    for tipo, datos in recompensas.items():

        plugin_req = None

        # recursos dinámicos
        if tipo in RECURSOS_REGISTRADOS:
            plugin_req = RECURSOS_REGISTRADOS[tipo].get("requiere_plugin")

        # tipos base
        elif tipo in RECURSOS_BASE:
            plugin_req = RECURSOS_BASE.get(tipo)

        yield {"tipo": tipo, "plugin": plugin_req}

# ─────────────────────────────
# Validación principal
# ─────────────────────────────
def validar_recompensas_entidad(entidad: dict):
    """
    Valida todas las recompensas y penalizaciones de una entidad.
    """
    invalidas = []
    plugins_necesarios = set()
    tipos_necesarios = set()

    recompensas_todas = {}
    for campo in ["recompensas", "penalizaciones"]:
        if campo in entidad and isinstance(entidad[campo], dict):
            recompensas_todas.update(entidad[campo])

    for item in _recorrer_recompensas_dict(recompensas_todas):
        tipo = item["tipo"]
        plugin = item["plugin"]

        # Tipo base desactivado
        if tipo in RECURSOS_BASE and not RECURSOS_BASE_ACTIVOS.get(tipo, False):
            invalidas.append(item)
            tipos_necesarios.add(tipo)
            if plugin:
                plugins_necesarios.add(plugin)
            continue

        # Tipo desconocido
        if not es_tipo_recompensa_valido(tipo):
            invalidas.append(item)
            if plugin:
                plugins_necesarios.add(plugin)

    return {
        "invalidas": invalidas,
        "plugins_necesarios": plugins_necesarios,
        "tipos_necesarios": tipos_necesarios
    }

# ─────────────────────────────
# Manejo de conflictos actualizado
# ─────────────────────────────
def manejar_conflictos(entidad_name: str,
                        resultado_validacion: dict,
                        plugins_activos: dict,
                        plugin_cache: dict,
                        id_racha: str = None,
                        on_enable_callbacks: dict = None) -> str:
    """
    Menú interactivo para manejar recompensas/penalizaciones inválidas,
    con activación de plugins que restaura sus datos desde plugin_cache.

    Args:
        entidad_name: nombre de la entidad afectada
        resultado_validacion: resultado de validar_recompensas_entidad
        plugins_activos: dict de plugins activos del sistema
        plugin_cache: cache de datos de plugins
        on_enable_callbacks: dict opcional {plugin_name: callback} para ejecutar al activar
    """
    invalidas = resultado_validacion.get("invalidas", [])
    plugins = resultado_validacion.get("plugins_necesarios", set())
    tipos = resultado_validacion.get("tipos_necesarios", set())

    if not invalidas:
        return "continuar"

    print(f"\n❌ Se han detectado recompensas/penalizaciones inválidas en '{entidad_name}':")

    if plugins:
        print("  Plugins requeridos que no están activos:")
        for p in plugins:
            print(f"   - {p}")
    if tipos:
        print("  Tipos de recompensa desactivados:")
        for t in tipos:
            print(f"   - {t}")

    print("\nOpciones:")
    print("A. Activar plugins requeridos")
    print("R. Eliminar recompensas/penalizaciones afectadas")
    print("E. Eliminar entidad completa")
    print("S. Seguir de todas formas")
    print("Enter. Cancelar y volver")

    while True:
        opcion = input("Selecciona opción: ").strip().upper()
        if opcion == "A":
            plugins_cache = plugin_cache.get("plugins", {})

            for p in plugins:
                plugins_activos[p] = True

                # Restaurar datos desde plugin_cache
                if p in plugins_cache:
                    estado.sistema_actual[p] = plugins_cache[p].copy()

                # Si no hay cache, usar callback
                elif on_enable_callbacks and p in on_enable_callbacks:
                    on_enable_callbacks[p](estado.sistema_actual)

            estado.cambios_no_guardados = True
            print("Plugins activados correctamente y datos restaurados.")
            return "activar_plugins"

        elif opcion == "R":
            print("\nOpciones:")
            print("1. Eliminar definitivamente recompensas/penalizaciones inválidas")
            print("2. Ignorar solo esta vez (no se entregarán pero se mantienen)")
        
            sub_op = input("Selecciona opción: ").strip()
        
            if sub_op == "1":
                # eliminar definitivamente
                if id_racha is None:
                    # Buscar racha por nombre si no se pasó id_racha
                    for rid, r in estado.sistema_actual.get("rachas", {}).get("activas", {}).items():
                        if r.get("nombre") == entidad_name:
                            id_racha = rid
                            break
                        
                if id_racha not in estado.sistema_actual.get("rachas", {}).get("activas", {}):
                    print("❌ No se encontró la racha para eliminar recompensas.")
                    return "cancelar"
            
                racha = estado.sistema_actual["rachas"]["activas"][id_racha]
            
                # Función auxiliar para eliminar bloques inválidos
                def eliminar_bloques_invalidos(seccion: dict):
                    tipos_a_eliminar = {inval["tipo"] for inval in invalidas if inval["tipo"] in seccion}
                    for tipo in tipos_a_eliminar:
                        seccion.pop(tipo, None)
            
                # Aplicar a recompensas y penalizaciones
                if "recompensas" in racha:
                    eliminar_bloques_invalidos(racha["recompensas"])
                if "penalizaciones" in racha:
                    eliminar_bloques_invalidos(racha["penalizaciones"])
            
                estado.cambios_no_guardados = True
                print("❌ Bloques de recompensas/penalizaciones inválidas eliminados definitivamente.")
                return "eliminar_recompensas"
            
            elif sub_op == "2":
                # ignorar solo esta vez
                print("⚠ Recompensas/penalizaciones inválidas ignoradas esta vez (no se entregarán).")
                return "ignorar_recompensas"
        
            else:
                print("Opción inválida. Volviendo al menú principal.")

        elif opcion == "E":
            print(f"Entidad '{entidad_name}' eliminada.")
            estado.cambios_no_guardados = True
            return "eliminar_entidad"

        elif opcion == "":
            print("Acción cancelada, se vuelve al menú.")
            return "cancelar"

        elif opcion == "S":
            print("Continuando. Las recompensas inválidas no serán entregadas.")
            return "seguir"

        else:
            print("Opción inválida. Intenta de nuevo.")

# ─────────────────────────────
# Filtrado de recompensas válidas
# ─────────────────────────────
def filtrar_recompensas_validas_entidad(entidad: dict) -> dict:
    """
    Devuelve solo recompensas y penalizaciones válidas para la entidad
    """
    resultado = validar_recompensas_entidad(entidad)
    invalidas_tipos = {i["tipo"] for i in resultado["invalidas"]}

    def filtrar(d: dict):
        if not isinstance(d, dict):
            return d
        return {k: v for k, v in d.items() if k not in invalidas_tipos}

    nueva_entidad = dict(entidad)
    if "recompensas" in entidad:
        nueva_entidad["recompensas"] = filtrar(entidad["recompensas"])
    if "penalizaciones" in entidad:
        nueva_entidad["penalizaciones"] = filtrar(entidad["penalizaciones"])

    return nueva_entidad

# ─────────────────────────────
# Manejar conflictos por objetivo
# ─────────────────────────────
def manejar_conflictos_objetivo(objetivo):
    resultado = validar_recompensas_objetivo(objetivo)
    if not resultado["invalidas"]:
        return "continuar"

    descripcion = objetivo.get('descripcion', 'desconocido')
    print(f"\n⚠ Recompensas inválidas detectadas en '{descripcion}':")

    # 🔥 NUEVO: plugins por tipo (sin mezclar)
    if resultado["plugins_necesarios"]:
        print("  Plugins requeridos inactivos:")
        for tipo, plugins in resultado["plugins_necesarios"].items():
            for p in plugins:
                print(f"   - {p} (tipo: {tipo})")

    # 🔥 Mejora: tipos más claros
    if resultado["tipos_necesarios"]:
        print("  Tipos no reconocidos o desactivados:")
        for t in resultado["tipos_necesarios"]:
            print(f"   - {t}")

    # 🔥 EXTRA PRO (opcional pero MUY útil)
    if resultado["invalidas"]:
        print("  Detalles:")
        for inval in resultado["invalidas"]:
            tipo = inval.get("tipo", "?")
            item = inval.get("item", "")
            plugin = inval.get("plugin", "")

            if item and plugin:
                print(f"   → {tipo} → {item} requiere '{plugin}'")
            elif plugin:
                print(f"   → {tipo} requiere '{plugin}'")
            else:
                print(f"   → {tipo} ({inval.get('detalle', 'error')})")

    print("\nOpciones:")
    print("A. Activar plugins necesarios")
    print("R. Eliminar recompensas inválidas")
    print("E. Eliminar objetivo completo")
    print("S. Seguir de todas formas")
    print("Enter. Cancelar entrega")

    while True:
        opcion = input("Selecciona opción: ").strip().upper()
        if opcion == "A":
            for p in resultado["plugins_necesarios"]:
                estado.sistema_actual["plugins_activos"][p] = True
                # Restaurar datos desde plugin_cache si existen
                if "plugins" in estado.plugin_cache and p in estado.plugin_cache["plugins"]:
                    estado.sistema_actual[p] = estado.plugin_cache["plugins"][p].copy()
            estado.cambios_no_guardados = True
            print("Plugins activados y datos restaurados.")
            return "activar_plugins"

        elif opcion == "R":
            for inval in resultado["invalidas"]:
                tipo = inval["tipo"]
                if tipo in objetivo.get("recompensas", {}):
                    del objetivo["recompensas"][tipo]
            estado.cambios_no_guardados = True
            print("Recompensas inválidas eliminadas.")
            return "eliminar_recompensas"

        elif opcion == "E":
            print(f"Objetivo '{descripcion}' eliminado.")
            estado.cambios_no_guardados = True
            # Aquí deberías eliminarlo de la lista del sistema si aplica
            return "eliminar_objetivo"

        elif opcion == "S":
            return "seguir"

        elif opcion == "":
            return "cancelar"

        else:
            print("Opción inválida, intenta de nuevo.")
            
# ─────────────────────────────
# Validar recompensas por objetivo
# ─────────────────────────────
def validar_recompensas_objetivo(objetivo):
    """
    Validación REAL basada en el sistema actual:
    - Usa RECURSOS_BASE_activos del JSON
    - Ignora tipos vacíos
    - No mezcla plugins entre tipos
    """

    from core.recompensas.tipos import (
        RECURSOS_REGISTRADOS,
        RECURSOS_BASE,
        es_tipo_recompensa_valido
    )

    invalidas = []
    plugins_necesarios = {}
    tipos_necesarios = set()

    sistema = estado.sistema_actual or {}
    plugins_activos = sistema.get("plugins_activos", {})
    tipos_activos = sistema.get("recursos_base_activos", {})  # 🔥 CLAVE

    recompensas = objetivo.get("recompensas", {})

    for tipo, items in recompensas.items():

        # 🔥 1. IGNORAR TIPOS VACÍOS
        if not items:
            continue

        # 🔥 2. IGNORAR TIPOS DESACTIVADOS EN EL SISTEMA
        if not tipos_activos.get(tipo, False):
            continue

        # 🔥 3. VALIDAR EXISTENCIA DEL TIPO
        if not es_tipo_recompensa_valido(tipo):
            invalidas.append({
                "tipo": tipo,
                "detalle": "Tipo no válido"
            })
            tipos_necesarios.add(tipo)
            continue

        # 🔥 4. OBTENER PLUGIN CORRECTO
        if tipo in RECURSOS_REGISTRADOS:
            plugin_req = RECURSOS_REGISTRADOS[tipo].get("requiere_plugin")

        elif tipo in RECURSOS_BASE:
            plugin_req = RECURSOS_BASE.get(tipo)

        else:
            plugin_req = None

        # 🔥 5. VALIDAR ITEMS SOLO SI HAY PLUGIN
        def validar_item(nombre):

            if plugin_req is None:
                return

            if not plugins_activos.get(plugin_req, False):

                plugins_necesarios.setdefault(tipo, set()).add(plugin_req)

                invalidas.append({
                    "tipo": tipo,
                    "item": nombre,
                    "plugin": plugin_req
                })

        # 🔥 6. RECORRER SEGÚN ESTRUCTURA

        if isinstance(items, dict):

            for nombre in items.keys():
                validar_item(nombre)

        elif isinstance(items, list):

            for i, item in enumerate(items):

                if isinstance(item, dict):
                    nombre = item.get("nombre", f"item_{i}")
                else:
                    nombre = str(item)

                validar_item(nombre)

        else:

            validar_item(str(items))

    return {
        "invalidas": invalidas,
        "plugins_necesarios": plugins_necesarios,
        "tipos_necesarios": tipos_necesarios
    }