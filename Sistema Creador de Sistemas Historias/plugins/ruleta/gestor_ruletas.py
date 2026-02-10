def inicializar_ruletas(sistema):
    if not hasattr(sistema, "ruletas"):
        sistema.ruletas = {}


def crear_ruleta(sistema, id_ruleta, nombre):
    from .modelo_ruleta import Ruleta
    inicializar_ruletas(sistema)

    if id_ruleta in sistema.ruletas:
        raise ValueError("Ya existe una ruleta con ese ID.")

    sistema.ruletas[id_ruleta] = Ruleta(id_ruleta, nombre)


def eliminar_ruleta(sistema, id_ruleta):
    inicializar_ruletas(sistema)
    sistema.ruletas.pop(id_ruleta, None)


def obtener_ruleta(sistema, id_ruleta):
    inicializar_ruletas(sistema)
    return sistema.ruletas.get(id_ruleta)
