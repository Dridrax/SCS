# plugins/niveles/__init__.py

from core.utils.plugin_registry import registrar_plugin
from .helpers_niveles import revisar_y_subir_nivel_destino

def init_plugin_niveles(sistema: dict):
    """
    Inicialización mínima del plugin 'niveles' para cualquier sistema.
    Esto se llama automáticamente cuando se activa el plugin.
    """
    # Valores básicos del sistema
    sistema.setdefault("nivel", 1)
    sistema.setdefault("xp_actual", 0)
    sistema.setdefault("xp_para_siguiente", 100)
    
    # Configuración de subida de niveles
    sistema.setdefault("niveles_config", {
        "modo_subida": "auto_stats_y_puntos",
        "puntos_por_nivel": 5,
        "stats_automaticos": 5,
        "factor_escalado": 1.2
    })
    
    # Inicializar recompensas por nivel si no existe
    sistema.setdefault("recompensas_por_nivel", [])

    # Hooks: Revisar automáticamente si hay suficiente XP al cargar
    revisar_y_subir_nivel_destino(sistema)


# Registrar plugin en el sistema central
registrar_plugin("niveles", init_plugin_niveles)


# Diccionario de compatibilidad con el registry actual
PLUGIN = {
    "nombre": "Niveles",
    "on_enable": init_plugin_niveles,
    "on_disable": None
}
