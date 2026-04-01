#Core/sistemas/sistema_temporal.py

from core.recompensas.tipos import RECURSOS_BASE, RAREZAS_BASE
from core.utils.funciones_utiles import pedir_si_no

def crear_sistema_temporal_config(plugins_activos=None):
    """
    Crea un sistema temporal usado durante la creación del sistema.
    Permite configurar recursos y tipos base antes de crear el sistema real.
    """

    return {
        "plugins_activos": plugins_activos or {},
        "recursos_base_activos": {},
        "rarezas_base_activos": {},
        "recursos_definidos": {},
        "rarezas_definidas": {}, 
        "recursos": {}
    }

def configurar_tipos_base_interactivo():
    """
    Pregunta al usuario qué tipos base de recursos quiere activar
    al crear el sistema.
    """

    print("\n=== CONFIGURACIÓN DE RECURSOS BASE ===\n")

    tipos_config = {}

    for tipo, plugin in RECURSOS_BASE.items():

        # Texto más claro para el usuario
        if plugin:
            texto = f"¿Quieres activar '{tipo}'? (requiere plugin '{plugin}')"
        else:
            texto = f"¿Quieres activar '{tipo}'?"

        usar = pedir_si_no(texto + " (s/n): ")

        tipos_config[tipo] = usar

    return tipos_config

def configurar_rarezas_base_interactivo():
    """
    Pregunta al usuario qué rarezas base quiere activar
    al crear el sistema.
    """

    print("\n=== CONFIGURACIÓN DE RAREZAS BASE ===\n")

    rarezas_config = {}

    for tipo in RAREZAS_BASE:
        usar = pedir_si_no(f"¿Quieres activar '{tipo}'? (s/n): ")
        rarezas_config[tipo] = usar

    return rarezas_config