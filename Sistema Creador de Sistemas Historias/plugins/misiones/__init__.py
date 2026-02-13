# plugins/misiones/__init__.py
from plugins.misiones.config import inicializar_misiones
from plugins.misiones.rachas.helpers_rachas import inicializar_rachas

def init_plugin_misiones(sistema):
    """
    Inicializa el plugin de misiones y todos sus subcomponentes (como rachas).
    """
    # Inicializar estructura principal de misiones
    inicializar_misiones(sistema)
    
    # Inicializar rachas
    inicializar_rachas(sistema)
