# core/plugins/registry.py

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
        "on_enable": lambda sistema: sistema.setdefault("inventario", []),
        # Función que se ejecuta al desactivar el plugin (opcional)
        "on_disable": None
    },

    # Aquí puedes añadir más plugins en el futuro
    # "habilidades": {
    #     "nombre": "Habilidades",
    #     "on_enable": lambda sistema: sistema.setdefault("habilidades", []),
    #     "on_disable": None
    # },
}
