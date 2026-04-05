from core.estado_global import estado

# =========================
# PUNTOS STATS
# =========================

def agregar_puntos_stats(cantidad, sistema=None):
    """Agrega puntos al pool de puntos_stats del sistema."""
    if sistema is None:
        sistema = estado.sistema_actual
    if sistema is None:
        return False

    sistema.setdefault("puntos_stats", 0)
    sistema["puntos_stats"] += cantidad
    estado.cambios_no_guardados = True
    return True

def gastar_puntos_stats(cantidad, sistema=None):
    """Intenta gastar puntos del pool. Devuelve True si se pudo gastar."""
    if sistema is None:
        sistema = estado.sistema_actual
    if sistema is None:
        return False

    pool = sistema.setdefault("puntos_stats", 0)
    if pool >= cantidad:
        sistema["puntos_stats"] -= cantidad
        estado.cambios_no_guardados = True
        return True
    else:
        return False

def consultar_puntos_stats(sistema=None):
    """Devuelve la cantidad de puntos_stats disponibles."""
    if sistema is None:
        sistema = estado.sistema_actual
    if sistema is None:
        return 0
    return sistema.get("puntos_stats", 0)

