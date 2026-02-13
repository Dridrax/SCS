# core/recompensas/ui_preparacion.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import pedir_int
from .tipos import RECURSOS_REGISTRADOS, registrar_recurso

# ─────────────────────────────────────────────
# VALIDACIÓN DE SOPORTE DE RECOMPENSAS
# ─────────────────────────────────────────────

def sistema_soporta_recompensa(sistema, tipo):
    """
    Comprueba si el sistema soporta un tipo de recompensa.
    Incluye soporte para recursos dinámicos.
    """

    # Recursos dinámicos siempre son válidos
    if tipo == "recursos":
        return True

    if tipo == "stats":
        return "stats" in sistema

    if tipo == "progress_stats":
        return "progress_stats" in sistema

    if tipo == "objetos":
        return sistema.get("plugins_activos", {}).get("inventario", False)

    if tipo == "puntos_stats":
        return "puntos_stats" in sistema

    if tipo == "puntos_habilidad":
        return "puntos_habilidad" in sistema

    if tipo == "dinero":
        return "dinero" in sistema

    if tipo == "nivel":
        return sistema.get("plugins_activos", {}).get("niveles", False)

    if tipo == "tiradas":
        return "tiradas" in sistema

    return False


# ─────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────

def _preguntar_creacion(texto):
    resp = input(f"❗ {texto} ¿Deseas crearlo? (s/n): ").lower()
    return resp == "s"


def _convertir_a_dinero_si_posible(sistema, recomp, cantidad):
    if cantidad <= 0:
        return

    if "dinero" not in sistema:
        crear = _preguntar_creacion("El sistema no usa dinero.")
        if not crear:
            return
        sistema["dinero"] = {}

    recomp.setdefault("dinero", {})
    recomp["dinero"]["oro"] = recomp["dinero"].get("oro", 0) + cantidad


# ─────────────────────────────────────────────
# PREPARAR RECOMPENSA
# ─────────────────────────────────────────────

def preparar_recompensa_para_aplicar(sistema, recompensas: dict):
    """
    Valida y prepara recompensas antes de aplicarlas.
    Ahora soporta recursos dinámicos.
    """

    recomp = recompensas.copy()

    # ───────────────
    # Recursos dinámicos
    # ───────────────
    if "recursos" in recomp:
        sistema.setdefault("recursos_definidos", {})
        sistema.setdefault("recursos", {})

        for nombre, cantidad in list(recomp["recursos"].items()):
            if nombre not in sistema["recursos_definidos"]:
                print(f"⚠ El recurso '{nombre}' no está definido en el sistema.")

                if _preguntar_creacion(f"¿Crear recurso '{nombre}'?"):
                    sistema["recursos_definidos"][nombre] = {
                        "descripcion": "",
                        "requiere_plugin": None
                    }
                    print(f"Recurso '{nombre}' creado.")
                else:
                    print(f"Recurso '{nombre}' descartado.")
                    recomp["recursos"].pop(nombre)

        if not recomp["recursos"]:
            recomp.pop("recursos")

    # ───────────────
    # PUNTOS DE STATS
    # ───────────────
    if "puntos_stats" in recomp and "puntos_stats" not in sistema:
        if _preguntar_creacion("Este sistema no tiene puntos de stats."):
            sistema["puntos_stats"] = 0
        else:
            cantidad = recomp.pop("puntos_stats")
            _convertir_a_dinero_si_posible(sistema, recomp, cantidad)

    # ───────────────
    # STATS
    # ───────────────
    if "stats" in recomp and "stats" not in sistema:
        if _preguntar_creacion("Este sistema no tiene stats simples."):
            sistema["stats"] = {}
        else:
            total = sum(recomp.pop("stats").values())
            _convertir_a_dinero_si_posible(sistema, recomp, total)

    # ───────────────
    # PROGRESS STATS
    # ───────────────
    if "progress_stats" in recomp and "progress_stats" not in sistema:
        if _preguntar_creacion("Este sistema no tiene progress stats."):
            sistema["progress_stats"] = {}
        else:
            total = sum(
                v.get("actual", 0)
                for v in recomp.pop("progress_stats").values()
            )
            _convertir_a_dinero_si_posible(sistema, recomp, total)

    # ───────────────
    # DINERO
    # ───────────────
    if "dinero" in recomp and "dinero" not in sistema:
        if _preguntar_creacion("Este sistema no tiene dinero."):
            sistema["dinero"] = {}
        else:
            recomp.pop("dinero")

    # ───────────────
    # OBJETOS
    # ───────────────
    if "objetos" in recomp:
        if not sistema.get("plugins_activos", {}).get("inventario", False):
            total_objetos = len(recomp["objetos"])
            print(f"➡ Inventario desactivado. {total_objetos} objetos descartados.")
            recomp.pop("objetos")
            _convertir_a_dinero_si_posible(sistema, recomp, total_objetos)

    return recomp


# ─────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────
def destinos_disponibles(plugin):
    """
    Devuelve la lista de destinos válidos según el plugin requerido.
    
    Parámetros:
        plugin (str | None): Nombre del plugin que requiere el recurso.
                             Si es None, se devuelven los destinos generales.
    
    Retorna:
        list[str]: Lista de nombres de destinos válidos.
    
    NOTAS PARA FUTUROS DESTINOS:
        1. Agrega el nuevo destino en el diccionario 'plugins_destinos'.
        2. La clave es el plugin que lo permite, o None si es general.
        3. Los valores son listas con los nombres de los destinos válidos.
    
    Ejemplo:
        plugins_destinos = {
            None: ["recursos", "stats_extra", "objetos"],
            "inventario": ["objetos", "equipamiento"],
            "combate": ["stats_extra", "habilidades"],
        }
        Para agregar un nuevo destino llamado "magia" que solo use el plugin "hechizos":
            plugins_destinos["hechizos"] = ["magia"]
    """
    plugins_destinos = {
        None: ["stats", "progress_stats"],  # Destinos generales
        "niveles": ["nivel", "xp_actual", "xp_para_siguiente"],
        # Agregar nuevos plugins aquí como claves y sus destinos como lista
    }
    return plugins_destinos.get(plugin, plugins_destinos[None])

def seleccionar_destino(plugin, destino_actual=None):
    """
    Permite al usuario elegir un destino válido mostrando opciones numeradas.

    Parámetros:
        plugin (str | None): Plugin requerido para filtrar destinos.
        destino_actual (str | None): Para mostrar el valor actual como predeterminado.

    Retorna:
        str: Destino elegido.
    """
    destinos_validos = destinos_disponibles(plugin)
    while True:
        print("\nDestinos válidos:")
        for i, d in enumerate(destinos_validos, 1):
            if d == destino_actual:
                print(f"{i}. {d} (actual)")
            else:
                print(f"{i}. {d}")
        try:
            eleccion = input("Selecciona el destino por número (Enter para mantener actual): ").strip()
            if eleccion == "" and destino_actual:
                return destino_actual
            indice = int(eleccion) - 1
            if 0 <= indice < len(destinos_validos):
                return destinos_validos[indice]
            else:
                print("Número inválido. Intenta de nuevo.")
        except ValueError:
            print("Entrada inválida. Ingresa un número.")


# ─────────────────────────────
# MENÚ CONFIGURAR RECURSOS
# ─────────────────────────────
def menu_configurar_recursos():
    sistema = estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    sistema.setdefault("recursos_definidos", {})

    while True:
        print("\n=== CONFIGURACIÓN DE RECURSOS ===")
        print("1. Ver recursos")
        print("2. Crear recurso")
        print("3. Editar recurso")
        print("4. Eliminar recurso")
        print("0. Volver")

        opcion = input("Selecciona opción: ").strip()

        # ───────────────
        # VER
        # ───────────────
        if opcion == "1":
            if not sistema["recursos_definidos"]:
                print("No hay recursos definidos.")
            else:
                for nombre, config in sistema["recursos_definidos"].items():
                    print(f"\n• {nombre}")
                    print(f"  Descripción: {config.get('descripcion', '')}")
                    print(f"  Requiere plugin: {config.get('requiere_plugin')}")
                    print(f"  Destino: {config.get('destino')}")

        # ───────────────
        # CREAR
        # ───────────────
        elif opcion == "2":
            nombre = input("Nombre del recurso: ").strip()
            if not nombre:
                print("Nombre inválido.")
                continue
            if nombre in sistema["recursos_definidos"]:
                print("Ese recurso ya existe.")
                continue

            descripcion = input("Descripción (opcional): ").strip()
            requiere_plugin = input("Requiere plugin (opcional): ").strip() or None

            destino = seleccionar_destino(requiere_plugin)

            sistema["recursos_definidos"][nombre] = {
                "descripcion": descripcion,
                "requiere_plugin": requiere_plugin,
                "destino": destino
            }

            registrar_recurso(nombre, descripcion, requiere_plugin, destino)

            estado.cambios_no_guardados = True
            print("Recurso creado correctamente.")

        # ───────────────
        # EDITAR
        # ───────────────
        elif opcion == "3":
            nombre = input("Nombre del recurso a editar: ").strip()
            if nombre not in sistema["recursos_definidos"]:
                print("No existe ese recurso.")
                continue

            descripcion = input("Nueva descripción (vacío para mantener): ").strip()
            requiere_plugin = input("Nuevo plugin requerido (vacío para mantener): ").strip() or sistema["recursos_definidos"][nombre]["requiere_plugin"]
            destino = seleccionar_destino(requiere_plugin, sistema["recursos_definidos"][nombre]["destino"])

            if descripcion:
                sistema["recursos_definidos"][nombre]["descripcion"] = descripcion
            sistema["recursos_definidos"][nombre]["requiere_plugin"] = requiere_plugin
            sistema["recursos_definidos"][nombre]["destino"] = destino

            registrar_recurso(
                nombre,
                sistema["recursos_definidos"][nombre].get("descripcion", ""),
                sistema["recursos_definidos"][nombre].get("requiere_plugin"),
                sistema["recursos_definidos"][nombre].get("destino", "recursos")
            )

            estado.cambios_no_guardados = True
            print("Recurso actualizado.")

        # ───────────────
        # ELIMINAR
        # ───────────────
        elif opcion == "4":
            nombre = input("Nombre del recurso a eliminar: ").strip()
            if nombre not in sistema["recursos_definidos"]:
                print("No existe ese recurso.")
                continue

            confirm = input("¿Seguro? (s/n): ").lower()
            if confirm == "s":
                sistema["recursos_definidos"].pop(nombre)
                RECURSOS_REGISTRADOS.pop(nombre, None)
                estado.cambios_no_guardados = True
                print("Recurso eliminado.")

        elif opcion == "0":
            guardar_sistema(print_msg=False)
            break
        else:
            print("Opción inválida.")