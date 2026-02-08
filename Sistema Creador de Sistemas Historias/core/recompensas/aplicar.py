from core.estado_global import estado
from plugins.inventario.inventario import agregar_item

def aplicar_recompensas(sistema, recompensas: dict):
    """
    Aplica recompensas al sistema.
    Asume que todos los campos ya existen y que todo está autorizado.
    No hace prints ni inputs.
    """
    if not sistema or not recompensas:
        return

    # Stats simples
    if "stats" in recompensas:
        sistema.setdefault("stats", {})
        for stat, valor in recompensas["stats"].items():
            sistema["stats"][stat] = sistema["stats"].get(stat, 0) + valor

    # Progress stats
    if "progress_stats" in recompensas:
        sistema.setdefault("progress_stats", {})
        for stat, datos in recompensas["progress_stats"].items():
            prog = sistema["progress_stats"].setdefault(stat, {
                "actual": 0,
                "max": datos.get("max", 100),
                "nivel": datos.get("nivel", 1),
                "factor_escalado": datos.get("factor_escalado", 1.2)
            })
            prog["actual"] += datos.get("actual", 0)
            prog["nivel"] += datos.get("nivel", 0)
            prog["max"] = max(prog["max"], datos.get("max", prog["max"]))

    # Puntos de stats
    if "puntos_stats" in recompensas:
        sistema.setdefault("puntos_stats", 0)
        sistema["puntos_stats"] += recompensas["puntos_stats"]

    # Dinero
    if "dinero" in recompensas:
        sistema.setdefault("dinero", {})
        for moneda, cantidad in recompensas["dinero"].items():
            sistema["dinero"][moneda] = sistema["dinero"].get(moneda, 0) + cantidad

    # Objetos (inventario)
    if "objetos" in recompensas:
        sistema.setdefault("inventario", {})
        for item_data in recompensas["objetos"]:
            agregar_item(sistema, item_data)

    # Marcar cambios
    estado.cambios_no_guardados = True
