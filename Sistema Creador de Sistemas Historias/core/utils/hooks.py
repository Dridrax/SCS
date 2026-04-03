# core/utils/hooks.py

"""
Sistema de hooks de destinos SCS.

Permite que plugins registren funciones que se ejecutarán
automáticamente cuando un destino específico sea modificado.
"""

DESTINOS_HOOKS = {}


def registrar_hook_destino(nombre_destino: str, funcion):
    """
    Registra una función que se ejecutará cuando cambie un destino.
    Permite múltiples funciones por destino.
    """
    if nombre_destino not in DESTINOS_HOOKS:
        DESTINOS_HOOKS[nombre_destino] = []

    DESTINOS_HOOKS[nombre_destino].append(funcion)


def ejecutar_hook_si_existe(nombre_destino: str, sistema: dict):
    """
    Ejecuta todos los hooks asociados a un destino si existen.
    """
    funciones = DESTINOS_HOOKS.get(nombre_destino, [])

    for funcion in funciones:
        try:
            funcion(sistema, nombre_destino)
        except Exception as e:
            print(f"⚠️ Error en hook '{nombre_destino}': {e}")

