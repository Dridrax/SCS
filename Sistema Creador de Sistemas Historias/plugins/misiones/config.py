def inicializar_misiones(sistema):
    """
    Inicializa las estructuras básicas de misiones y rachas
    dentro del sistema si no existen.
    """

    if not sistema:
        return

    sistema.setdefault("misiones", {})
    sistema.setdefault("misiones_completadas", {})
    sistema.setdefault("rachas", {})
