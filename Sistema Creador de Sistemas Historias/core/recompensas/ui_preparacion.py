# core/recompensas/validacion.py

def sistema_soporta_recompensa(sistema, tipo):
    """
    Comprueba si el sistema soporta un tipo de recompensa.
    Devuelve True/False.
    """

    if tipo == "stats":
        return "stats" in sistema

    if tipo == "objetos":
        return sistema.get("plugins_activos", {}).get("inventario", False)

    if tipo == "puntos_stats":
        return "puntos_stats" in sistema

    if tipo == "puntos_habilidad":
        return "puntos_habilidad" in sistema

    if tipo == "dinero":
        return "dinero" in sistema  # se implementará en fase 6

    if tipo == "nivel":
        return sistema.get("usa_niveles", False)

    if tipo == "tiradas":
        return "tiradas" in sistema

    return False


def preparar_recompensa_para_aplicar(sistema, recompensas: dict):
    """
    Pregunta al usuario sobre creación de campos faltantes y conversión a oro.
    Devuelve una copia de la recompensa lista para aplicar.
    """
    recomp = recompensas.copy()

    # Puntos de stats
    if "puntos_stats" in recomp and "puntos_stats" not in sistema:
        crear = input("❗ Este sistema no tiene puntos de stats. ¿Deseas crearlos? (s/n): ").lower() == "s"
        if crear:
            sistema["puntos_stats"] = 0
        else:
            recomp.setdefault("dinero", {})
            recomp["dinero"]["oro"] = recomp["dinero"].get("oro", 0) + recomp.pop("puntos_stats")

    # Stats simples
    if "stats" in recomp and "stats" not in sistema:
        crear = input("❗ Este sistema no tiene stats simples. ¿Deseas crearlos? (s/n): ").lower() == "s"
        if crear:
            sistema["stats"] = {}
        else:
            total = sum(recomp.pop("stats").values())
            recomp.setdefault("dinero", {})
            recomp["dinero"]["oro"] = recomp["dinero"].get("oro", 0) + total

    # Progress stats
    if "progress_stats" in recomp and "progress_stats" not in sistema:
        crear = input("❗ Este sistema no tiene progress stats. ¿Deseas crearlos? (s/n): ").lower() == "s"
        if crear:
            sistema["progress_stats"] = {}
        else:
            total = sum([v.get("actual", 0) for v in recomp.pop("progress_stats").values()])
            recomp.setdefault("dinero", {})
            recomp["dinero"]["oro"] = recomp["dinero"].get("oro", 0) + total

    # Dinero
    if "dinero" in recomp and "dinero" not in sistema:
        crear = input("❗ Este sistema no tiene dinero. ¿Deseas crearlo? (s/n): ").lower() == "s"
        if crear:
            sistema["dinero"] = {}
        else:
            recomp.pop("dinero", None)

    # Objetos / plugins
    if "objetos" in recomp:
        inventario_activo = sistema.get("plugins_activos", {}).get("inventario", False)
        if not inventario_activo:
            total_objetos = len(recomp["objetos"])
            print(f"➡ El plugin de inventario está desactivado, {total_objetos} objetos se convierten en oro")
            recomp.setdefault("dinero", {})
            recomp["dinero"]["oro"] = recomp["dinero"].get("oro", 0) + total_objetos
            recomp.pop("objetos")

    return recomp
