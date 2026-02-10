# core/recompensas/aplicar.py
from core.estado_global import estado
from plugins.inventario.inventario import agregar_item


def aplicar_recompensas(sistema: dict, recompensas: dict) -> dict:
    """
    Aplica recompensas al sistema.

    Reglas:
    - No pregunta ni imprime nada
    - No valida si el sistema debería soportar la recompensa
    - Aplica solo lo que exista o sea aplicable
    - Devuelve un resumen de lo ocurrido

    Return:
    {
        "aplicadas": {tipo: valor},
        "ignoradas": {tipo: motivo}
    }
    """

    resultado = {
        "aplicadas": {},
        "ignoradas": {}
    }

    if not sistema or not recompensas:
        return resultado

    # ───────────────
    # Stats simples
    # ───────────────
    if "stats" in recompensas:
        if "stats" not in sistema:
            resultado["ignoradas"]["stats"] = "El sistema no tiene stats"
        else:
            for stat, valor in recompensas["stats"].items():
                sistema["stats"][stat] = sistema["stats"].get(stat, 0) + valor
            resultado["aplicadas"]["stats"] = recompensas["stats"]

    # ───────────────
    # Progress stats
    # ───────────────
    if "progress_stats" in recompensas:
        if "progress_stats" not in sistema:
            resultado["ignoradas"]["progress_stats"] = "El sistema no tiene progress stats"
        else:
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

            resultado["aplicadas"]["progress_stats"] = recompensas["progress_stats"]

    # ───────────────
    # Puntos de stats
    # ───────────────
    if "puntos_stats" in recompensas:
        if "puntos_stats" not in sistema:
            resultado["ignoradas"]["puntos_stats"] = "El sistema no usa puntos de stats"
        else:
            sistema["puntos_stats"] += recompensas["puntos_stats"]
            resultado["aplicadas"]["puntos_stats"] = recompensas["puntos_stats"]

    # ───────────────
    # Dinero
    # ───────────────
    if "dinero" in recompensas:
        if "dinero" not in sistema:
            resultado["ignoradas"]["dinero"] = "El sistema no maneja dinero"
        else:
            for moneda, cantidad in recompensas["dinero"].items():
                sistema["dinero"][moneda] = sistema["dinero"].get(moneda, 0) + cantidad
            resultado["aplicadas"]["dinero"] = recompensas["dinero"]

    # ───────────────
    # Objetos (plugin inventario)
    # ───────────────
    if "objetos" in recompensas:
        if not sistema.get("plugins_activos", {}).get("inventario", False):
            resultado["ignoradas"]["objetos"] = "Plugin de inventario desactivado"
        else:
            for item_data in recompensas["objetos"]:
                agregar_item(sistema, item_data)
            resultado["aplicadas"]["objetos"] = len(recompensas["objetos"])

    # Marcar cambios solo si algo se aplicó
    if resultado["aplicadas"]:
        estado.cambios_no_guardados = True

    return resultado
