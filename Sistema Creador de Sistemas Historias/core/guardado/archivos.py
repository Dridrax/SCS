import os
import json
import shutil
from core.estado_global import estado


# =========================
# GUARDAR SISTEMA (MODIFICADO)
# =========================
def guardar_sistema(nombre_archivo=None, print_msg=True):
    sistema = estado.sistema_actual
    if not sistema:
        if print_msg:
            print("❌ No hay sistema cargado.")
        return

    # Si no se pasa nombre de archivo, intentar usar nombre del sistema
    if nombre_archivo is None:
        if estado.archivo_actual:
            nombre_archivo = estado.archivo_actual.replace(".json", "")
        elif sistema.get("nombre_sistema"):
            nombre_archivo = sistema["nombre_sistema"]
        else:
            # Pedir al usuario si no hay nombre de sistema
            nombre_archivo = input("Introduce un nombre de archivo para guardar este sistema: ").strip()
            if not nombre_archivo:
                if print_msg:
                    print("❌ No se proporcionó nombre de archivo. Guardado cancelado.")
                return

    sistema_sin_plugins = sistema.copy()
    for plugin, activo in sistema.get("plugins_activos", {}).items():
        if not activo and plugin in sistema_sin_plugins:
            # Si el plugin está desactivado, borramos del JSON principal
            sistema_sin_plugins.pop(plugin, None)

    with open(f"{nombre_archivo}.json", "w", encoding="utf-8") as f:
        json.dump(sistema_sin_plugins, f, ensure_ascii=False, indent=4)

    # Guardar plugin_cache
    plugin_cache = estado.plugin_cache.copy()
    plugin_cache["stats"] = sistema.get("stats", {})
    plugin_cache["progress_stats"] = sistema.get("progress_stats", {})

    with open(f"{nombre_archivo}_plugin_cache.json", "w", encoding="utf-8") as f:
        json.dump(plugin_cache, f, ensure_ascii=False, indent=4)

    estado.cambios_no_guardados = False
    estado.archivo_actual = nombre_archivo

    if print_msg:
        print(f"\n✅ Sistema y plugin_cache guardados")
        #print(f"\n✅ Sistema y plugin_cache guardados en '{nombre_archivo}.json' y '{nombre_archivo}_plugin_cache.json'.")




# =========================
# GUARDAR COMO
# =========================
def guardar_como(sistema=None):
    
    

    if sistema is None:
        sistema = estado.sistema_actual

    if sistema is None:
        print("❌ No hay sistema cargado para guardar.")
        return

    print("\n=== GUARDAR COMO ===")
    print("1. Guardar con nuevo nombre (plugin_cache nuevo)")
    print("2. Guardar con nuevo nombre usando plugin_cache actual")
    print("3. Guardar con nuevo nombre usando otro plugin_cache")
    print("4. Cancelar")

    opcion = input("Elige una opción: ").strip()

    if opcion == "4":
        print("⚠️ Operación cancelada.")
        return

    nombre_base = input("\nNombre del nuevo archivo del sistema: ").strip()
    if not nombre_base:
        print("❌ Nombre inválido.")
        return

    nombre_json = f"{nombre_base}.json"
    nombre_cache = f"{nombre_base}_plugin_cache.json"

    if os.path.exists(nombre_json):
        print(f"\n❗ El archivo '{nombre_json}' ya existe.")
        sobrescribir = input("¿Sobrescribirlo? (s/n): ").lower() == "s"
        if not sobrescribir:
            print("⚠️ Operación cancelada.")
            return

    # ============================
    # OPCIÓN 1: plugin_cache NUEVO
    # ============================
    if opcion == "1":
        plugin_cache = {
            "plugins": {},
            "stats": sistema.get("stats", {}),
            "progress_stats": sistema.get("progress_stats", {})
        }

        with open(nombre_cache, "w", encoding="utf-8") as f:
            json.dump(plugin_cache, f, ensure_ascii=False, indent=4)

        estado.plugin_cache = plugin_cache

    # =================================
    # OPCIÓN 2: plugin_cache ACTUAL
    # =================================
    elif opcion == "2":
        plugin_cache = estado.plugin_cache

        with open(nombre_cache, "w", encoding="utf-8") as f:
            json.dump(plugin_cache, f, ensure_ascii=False, indent=4)

    # =====================================
    # OPCIÓN 3: usar OTRO plugin_cache
    # =====================================
    elif opcion == "3":
        ruta_cache = input("Ruta del plugin_cache a usar: ").strip()

        if not ruta_cache or not os.path.exists(ruta_cache):
            print("❌ Ruta inválida.")
            return

        shutil.copy(ruta_cache, nombre_cache)

        with open(nombre_cache, "r", encoding="utf-8") as f:
            estado.plugin_cache = json.load(f)

    else:
        print("❌ Opción no válida.")
        return

    # ============================
    # GUARDAR SISTEMA PRINCIPAL
    # ============================
    estado.archivo_actual = nombre_base
    guardar_sistema(nombre_base)

    print(f"\n✅ Sistema guardado como '{nombre_json}'")
    print(f"✅ Plugin cache asociado: '{nombre_cache}'")



# =========================
# CARGAR SISTEMA
# =========================
def cargar_sistema(nombre_archivo):
    if not os.path.exists(f"{nombre_archivo}.json"):
        print(f"❌ No se encontró '{nombre_archivo}.json'.")
        return None

    # =========================
    # 1️⃣ Cargar sistema principal
    # =========================
    with open(f"{nombre_archivo}.json", "r", encoding="utf-8") as f:
        sistema = json.load(f)

    estado.sistema_actual = sistema
    estado.archivo_actual = nombre_archivo

    # =========================
    # 2️⃣ Preparar plugin_cache
    # =========================
    cache_file_default = f"{nombre_archivo}_plugin_cache.json"
    plugin_cache = {
        "plugins": {},
        "stats": {},
        "progress_stats": {}
    }

    if os.path.exists(cache_file_default):
        print(f"Se encontró plugin_cache por defecto: '{cache_file_default}'")
        usar_cache = input("\n¿Deseas cargar este plugin_cache? (s/n): ").lower() == "s"

        if usar_cache:
            with open(cache_file_default, "r", encoding="utf-8") as f:
                plugin_cache = json.load(f)
        else:
            ruta_cache = input(
                "Indica la ruta del plugin_cache a cargar (o deja vacío para crear uno nuevo): "
            ).strip()

            if ruta_cache and os.path.exists(ruta_cache):
                with open(ruta_cache, "r", encoding="utf-8") as f:
                    plugin_cache = json.load(f)
            else:
                print("\n⚠️ No se cargó plugin_cache externo. Se creará uno nuevo.")
    else:
        print(f"❌ No se encontró plugin_cache. Se creará uno nuevo: '{cache_file_default}'")

    # =========================
    # 3️⃣ Sincronizar datos (NO sobreescribir)
    # =========================

    # Guardar stats siempre en cache
    plugin_cache["stats"] = sistema.get("stats", {})
    plugin_cache["progress_stats"] = sistema.get("progress_stats", {})

    # Copiar datos de plugins activos del sistema → cache (solo si no existen)
    for plugin, activo in sistema.get("plugins_activos", {}).items():
        if activo and plugin in sistema:
            if plugin not in plugin_cache["plugins"]:
                plugin_cache["plugins"][plugin] = sistema[plugin]

    # =========================
    # 4️⃣ Restaurar sistema desde cache
    # =========================
    sistema["stats"] = plugin_cache.get("stats", {})
    sistema["progress_stats"] = plugin_cache.get("progress_stats", {})

    for plugin, datos in plugin_cache.get("plugins", {}).items():
        if sistema.get("plugins_activos", {}).get(plugin):
            sistema[plugin] = datos

    # =========================
    # 5️⃣ Guardar plugin_cache asegurado
    # =========================
    with open(cache_file_default, "w", encoding="utf-8") as f:
        json.dump(plugin_cache, f, ensure_ascii=False, indent=4)

    estado.plugin_cache = plugin_cache
    estado.cambios_no_guardados = False

    # =========================
    # 6️⃣ 🔥 INICIALIZAR PLUGINS ACTIVOS (CLAVE)
    # =========================
    from core.plugins.registry import inicializar_todos_los_plugins_activos
    inicializar_todos_los_plugins_activos(sistema)

    print(f"\n✅ Sistema cargado correctamente desde '{nombre_archivo}.json'.")
    return sistema
