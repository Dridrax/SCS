# plugins/ruleta/__init__.py

from core.utils.plugin_registry import registrar_plugin
from .helpers_ruleta import inicializar_ruletas
from core.utils.hooks import registrar_hook_destino
from core.utils.funciones_utiles import sync_plugin_cache

def init_plugin_ruleta(sistema: dict):
    """
    Inicialización del plugin 'ruleta'.
    Encapsula todos los datos dentro de sistema["ruleta"] y migra datos antiguos.
    También sincroniza automáticamente con estado.plugin_cache.
    """

    # -------------------------
    # 🟡 MIGRACIÓN DE DATOS ANTIGUOS
    # -------------------------
    if "ruleta" not in sistema:
        sistema["ruleta"] = {
            "activas": {},
            "historial": []
        }

    # -------------------------
    # 🔧 ASEGURAR ESTRUCTURA
    # -------------------------
    ruletas = sistema["ruleta"]
    ruletas.setdefault("activas", {})
    ruletas.setdefault("historial", [])

    # -------------------------
    # 🔄 SINCRONIZAR PLUGIN CACHE
    # -------------------------
    sync_plugin_cache(sistema, "ruleta")

# Registrar plugin en el sistema central
registrar_plugin("ruleta", init_plugin_ruleta)

# Diccionario de compatibilidad con el registry actual
PLUGIN = {
    "nombre": "Ruleta",
    "on_enable": init_plugin_ruleta,
    "on_disable": None
}