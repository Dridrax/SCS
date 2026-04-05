import uuid

def crear_modelo_objetivo(*, descripcion, cantidad_base=1, interno=False):
    return {
        "id": str(uuid.uuid4()),  # ID único para asignar recompensas/penalizaciones
        "descripcion": descripcion,
        "cantidad_base": cantidad_base,
        "progreso": 0,
        "interno": interno,
        "recompensas": {"objetos": []},
        "penalizaciones": {"objetos": []},
        "estado_objetivo": "pendiente"
    }

def crear_modelo_mision(
    *,
    id,
    nombre,
    descripcion="",
    objetivos=None
):
    return {
        "id": id,
        "nombre": nombre,
        "descripcion": descripcion,
        "objetivos": objetivos or [],  # Lista de objetivos, normales e internos
    }
