# core/plugins/registry.py

"""
Registro central de plugins para SCS.
Cada plugin se define con:
- "nombre": Nombre legible.
- "on_enable": Función opcional que se ejecuta al activar.
- "on_disable": Función opcional que se ejecuta al desactivar.
"""

from core.utils.plugin_registry import inicializar_plugins_activos

from plugins.misiones import init_plugin_misiones

from plugins.niveles import PLUGIN as PLUGIN_NIVELES

from plugins.rachas import PLUGIN as PLUGIN_RACHAS

from plugins.ruleta import PLUGIN as PLUGIN_RULETA

PLUGINS = {
    "inventario": {
        "nombre": "Inventario",
        "on_enable": lambda sistema: sistema.setdefault("inventario", {}),
        "on_disable": None
    },
    
    "misiones": {
        "nombre": "Misiones",
        "on_enable": init_plugin_misiones,
        "on_disable": None
    },

    "niveles": PLUGIN_NIVELES,
    
    "rachas": PLUGIN_RACHAS,

    "ruleta": PLUGIN_RULETA
    
}

def inicializar_todos_los_plugins_activos(sistema):
    """
    Llamar esto al cargar un sistema.
    Inicializa automáticamente todos los plugins activos registrados.
    """
    inicializar_plugins_activos(sistema)
