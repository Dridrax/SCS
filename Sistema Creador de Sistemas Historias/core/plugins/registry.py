# core/plugins/registry.py
from plugins.niveles import PLUGIN as PLUGIN_NIVELES
from plugins.misiones.config import inicializar_misiones
from plugins.misiones.rachas.helpers_rachas import inicializar_rachas

"""
Registro central de plugins para SCS.
Cada plugin se define con:
- "nombre": Nombre legible.
- "on_enable": Función opcional que se ejecuta al activar.
- "on_disable": Función opcional que se ejecuta al desactivar.
"""

PLUGINS = {
    "inventario": {
        "nombre": "Inventario",
        "on_enable": lambda sistema: sistema.setdefault("inventario", {}),
        "on_disable": None
    },

    "niveles": PLUGIN_NIVELES,

    "misiones": {
        "nombre": "Misiones",
        "on_enable": lambda sistema: inicializar_misiones(sistema),
        "on_disable": None
    },

    "rachas": {
        "nombre": "Rachas",
        "on_enable": lambda sistema: inicializar_rachas(sistema),
        "on_disable": None
    }

    # Aquí se pueden añadir más plugins en el futuro
}


"""    "puntos": {
        "nombre": "Puntos Distribuibles",
        "on_enable": lambda sistema: (
            sistema.setdefault("puntos_stats", 0),
            sistema.setdefault("puntos_habilidad", 0)
        ),
        "on_disable": None
    },"""