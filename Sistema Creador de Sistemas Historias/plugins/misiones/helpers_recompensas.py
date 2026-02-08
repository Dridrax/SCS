from core.estado_global import estado


def agregar_recompensa_item(
    sistema,
    mision_id,
    nombre,
    cantidad=1,
    rareza="común",
    tipo="misc",
    descripcion=""
):
    misiones = sistema.get("misiones", {})

    if mision_id not in misiones:
        return False

    mision = misiones[mision_id]

    # --- BINDING EXTRA: asegurar que recompensas es dict y no lista ---
    mision.setdefault("recompensas", {})
    if isinstance(mision["recompensas"], list):
        mision["recompensas"] = {"objetos": []}

    # --- Asegurar que exista la lista de objetos ---
    mision["recompensas"].setdefault("objetos", [])

    # Crear el objeto de recompensa
    item = {
        "nombre": nombre,
        "cantidad": cantidad,
        "rareza": rareza,
        "tipo": tipo,
        "descripcion": descripcion,
        "efectos": {}
    }

    # Añadirlo a la misión
    mision["recompensas"]["objetos"].append(item)

    # Marcar cambios
    estado.cambios_no_guardados = True
    return True


def agregar_recompensa_puntos_stats(sistema, mision_id, cantidad):
    misiones = sistema.get("misiones", {})
    if mision_id not in misiones:
        return False

    mision = misiones[mision_id]
    if not isinstance(mision.get("recompensas"), dict):
        mision["recompensas"] = {}
    mision["recompensas"].setdefault("puntos_stats", 0)

    mision["recompensas"]["puntos_stats"] += cantidad
    estado.cambios_no_guardados = True
    return True



def agregar_recompensa_stat(sistema, mision_id, stat_nombre, cantidad):
    misiones = sistema.get("misiones", {})
    if mision_id not in misiones:
        return False

    mision = misiones[mision_id]
    if not isinstance(mision.get("recompensas"), dict):
        mision["recompensas"] = {}
    mision["recompensas"].setdefault("stats", {})

    mision["recompensas"]["stats"][stat_nombre] = \
        mision["recompensas"]["stats"].get(stat_nombre, 0) + cantidad

    estado.cambios_no_guardados = True
    return True


def agregar_recompensa_progress_stat(sistema, mision_id, stat_nombre, actual=0, nivel=0, maximo=100):
    misiones = sistema.get("misiones", {})
    if mision_id not in misiones:
        return False

    mision = misiones[mision_id]
    if not isinstance(mision.get("recompensas"), dict):
        mision["recompensas"] = {}
    mision["recompensas"].setdefault("progress_stats", {})

    prog = mision["recompensas"]["progress_stats"].setdefault(stat_nombre, {
        "actual": 0,
        "nivel": 1,
        "max": 100
    })
    prog["actual"] += actual
    prog["nivel"] += nivel
    prog["max"] = max(prog["max"], maximo)

    estado.cambios_no_guardados = True
    return True


def agregar_recompensa_dinero(sistema, mision_id, moneda, cantidad):
    misiones = sistema.get("misiones", {})
    if mision_id not in misiones:
        return False

    mision = misiones[mision_id]
    if not isinstance(mision.get("recompensas"), dict):
        mision["recompensas"] = {}
    mision["recompensas"].setdefault("dinero", {})

    mision["recompensas"]["dinero"][moneda] = \
        mision["recompensas"]["dinero"].get(moneda, 0) + cantidad

    estado.cambios_no_guardados = True
    return True

def agregar_recompensa_nivel(sistema, mision_id, cantidad_niveles):
    misiones = sistema.get("misiones", {})
    if mision_id not in misiones:
        return False

    mision = misiones[mision_id]
    if not isinstance(mision.get("recompensas"), dict):
        mision["recompensas"] = {}
    mision["recompensas"].setdefault("nivel", 0)

    mision["recompensas"]["nivel"] += cantidad_niveles
    estado.cambios_no_guardados = True
    return True

def agregar_recompensa_tirada(sistema, mision_id, cantidad_tiradas):
    misiones = sistema.get("misiones", {})
    if mision_id not in misiones:
        return False

    mision = misiones[mision_id]
    if not isinstance(mision.get("recompensas"), dict):
        mision["recompensas"] = {}
    mision["recompensas"].setdefault("tiradas", 0)

    mision["recompensas"]["tiradas"] += cantidad_tiradas
    estado.cambios_no_guardados = True
    return True