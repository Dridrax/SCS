from core.recompensas.tipos import TIPOS_RECOMPENSA
from core.utils.funciones_utiles import pedir_si_no

def crear_sistema_temporal_config(plugins_activos=None):
    """
    Crea un sistema temporal usado durante la creación del sistema.
    Permite configurar recursos y tipos base antes de crear el sistema real.
    """

    return {
        "plugins_activos": plugins_activos or {},
        "tipos_recompensa_activos": {},
        "recursos_definidos": {},
        "recursos": {}
    }

def configurar_tipos_base_interactivo():
    """
    Pregunta al usuario qué tipos base de recursos quiere activar
    al crear el sistema.
    """

    print("\n=== CONFIGURACIÓN DE RECURSOS BASE ===\n")

    tipos_config = {}

    for tipo, plugin in TIPOS_RECOMPENSA.items():

        # Texto más claro para el usuario
        if plugin:
            texto = f"¿Quieres activar '{tipo}'? (requiere plugin '{plugin}')"
        else:
            texto = f"¿Quieres activar '{tipo}'?"

        usar = pedir_si_no(texto + " (s/n): ")

        tipos_config[tipo] = usar

    return tipos_config