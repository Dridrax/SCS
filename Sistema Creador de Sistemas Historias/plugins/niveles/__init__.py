# plugins/niveles/__init__.py

from core.utils.plugin_registry import registrar_plugin
from .helpers_niveles import revisar_y_subir_nivel_destino
from core.utils.hooks import registrar_hook_destino
from core.utils.funciones_utiles import sync_plugin_cache  # <--- Importamos la función


def init_plugin_niveles(sistema: dict):
    """
    Inicialización del plugin 'niveles'.
    Encapsula todos los datos dentro de sistema["niveles"] y migra datos antiguos.
    También sincroniza automáticamente con estado.plugin_cache.
    """

    # -------------------------
    # 🟡 MIGRACIÓN DE DATOS ANTIGUOS
    # -------------------------
    if "niveles" not in sistema:
        sistema["niveles"] = {
            "nivel": sistema.pop("nivel", 1),
            "xp_actual": sistema.pop("xp_actual", 0),
            "xp_para_siguiente": sistema.pop("xp_para_siguiente", 100),
            "niveles_config": sistema.pop("niveles_config", {
                "modo_subida": "auto_stats_y_puntos",
                "puntos_por_nivel": 5,
                "stats_automaticos": 5,
                "factor_escalado": 1.2
            }),
            "recompensas_por_nivel": sistema.pop("recompensas_por_nivel", [])
        }

    niveles = sistema["niveles"]

    # -------------------------
    # 🟢 ASEGURAR ESTRUCTURA
    # -------------------------
    niveles.setdefault("nivel", 1)
    niveles.setdefault("xp_actual", 0)
    niveles.setdefault("xp_para_siguiente", 100)
    niveles.setdefault("niveles_config", {
        "modo_subida": "auto_stats_y_puntos",
        "puntos_por_nivel": 5,
        "stats_automaticos": 5,
        "factor_escalado": 1.2
    })
    niveles.setdefault("recompensas_por_nivel", [])

    # -------------------------
    # 🔗 HOOKS
    # -------------------------
    registrar_hook_destino("xp_actual", revisar_y_subir_nivel_destino)

    # Revisar subida de nivel al cargar
    revisar_y_subir_nivel_destino(sistema)

    # -------------------------
    # 🔄 SINCRONIZAR PLUGIN CACHE
    # -------------------------
    sync_plugin_cache(sistema, "niveles")


# Registrar plugin en el sistema central
registrar_plugin("niveles", init_plugin_niveles)


# Diccionario de compatibilidad con el registry actual
PLUGIN = {
    "nombre": "Niveles",
    "on_enable": init_plugin_niveles,
    "on_disable": None
}