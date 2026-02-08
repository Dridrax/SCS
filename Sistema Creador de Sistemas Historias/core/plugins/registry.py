# core/plugins/registry.py
from plugins.niveles import PLUGIN as PLUGIN_NIVELES
from plugins.misiones.config import inicializar_misiones
"""
Registro central de plugins para SCS.
Cada plugin se define con:
- "nombre": Nombre legible.
- "on_enable": Función opcional que se ejecuta al activar.
- "on_disable": Función opcional que se ejecuta al desactivar.
"""

  # Función para inicializar inventario

PLUGINS = {
    "inventario": {
        "nombre": "Inventario",
        # Función que se ejecuta al activar el plugin
        "on_enable": lambda sistema: sistema.setdefault("inventario", {}),
        # Función que se ejecuta al desactivar el plugin (opcional)
        "on_disable": None
    },

    "niveles": PLUGIN_NIVELES,
    
    "misiones": {
    "nombre": "Misiones",
    "on_enable": lambda sistema: inicializar_misiones(sistema),
    "on_disable": None
    }

    # Aquí puedes añadir más plugins en el futuro
    # "habilidades": {
    #     "nombre": "Habilidades",
    #     "on_enable": lambda sistema: sistema.setdefault("habilidades", {}),
    #     "on_disable": None
    # },
}

"""    "puntos": {
        "nombre": "Puntos Distribuibles",
        "on_enable": lambda sistema: (
            sistema.setdefault("puntos_stats", 0),
            sistema.setdefault("puntos_habilidad", 0)
        ),
        "on_disable": None
    },"""