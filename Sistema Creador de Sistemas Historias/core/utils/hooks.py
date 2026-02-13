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

    Parámetros:
        nombre_destino (str): Nombre del destino (ej: "xp_actual")
        funcion (callable): Función que recibirá (sistema)
    """
    DESTINOS_HOOKS[nombre_destino] = funcion


def ejecutar_hook_si_existe(nombre_destino: str, sistema: dict):
    """
    Ejecuta el hook asociado a un destino si existe.
    """
    funcion = DESTINOS_HOOKS.get(nombre_destino)
    if funcion:
        funcion(sistema)
