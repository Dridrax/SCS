def crear_modelo_mision(
    *,
    id,
    nombre,
    descripcion="",
    objetivo="",
    recompensas=None,
    penalizaciones=None
):
    return {
        "id": id,
        "nombre": nombre,
        "descripcion": descripcion,
        "objetivo": objetivo,
        "recompensas": recompensas or {
            "objetos": []
        },
        "penalizaciones": penalizaciones or {
            "objetos": []
        }
    }



def crear_modelo_racha(
    *,
    id,
    nombre,
    descripcion="",
    recompensas=None
):
    """
    Modelo simple de racha.
    Recompensa repetible cuando el autor lo decide.
    """

    return {
        "id": id,
        "nombre": nombre,
        "descripcion": descripcion,
        "recompensas": recompensas or []
    }
