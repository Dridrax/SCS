# core/utils/plugin_registry.py

PLUGIN_REGISTRY = {}

def registrar_plugin(nombre: str, funcion_inicializacion):
    """
    Registra un plugin y su función de inicialización.
    nombre: clave única del plugin (ej: "niveles")
    funcion_inicializacion: función(sistema) -> None
    """
    PLUGIN_REGISTRY[nombre] = funcion_inicializacion

def inicializar_plugin(nombre: str, sistema: dict):
    """
    Inicializa un plugin si está registrado.
    """
    if nombre in PLUGIN_REGISTRY:
        PLUGIN_REGISTRY[nombre](sistema)

def inicializar_plugins_activos(sistema: dict):
    """
    Recorre plugins activos del sistema y los inicializa si están registrados.
    """
    for plugin, activo in sistema.get("plugins_activos", {}).items():
        if activo:
            inicializar_plugin(plugin, sistema)
