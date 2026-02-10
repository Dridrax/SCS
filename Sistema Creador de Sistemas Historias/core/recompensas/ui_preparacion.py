# core/recompensas/ui_preparacion.py


def sistema_soporta_recompensa(sistema, tipo):
    """
    Comprueba si el sistema soporta un tipo de recompensa.
    Devuelve True / False.
    """
    if tipo == "stats":
        return "stats" in sistema

    if tipo == "progress_stats":
        return "progress_stats" in sistema

    if tipo == "objetos":
        return sistema.get("plugins_activos", {}).get("inventario", False)

    if tipo == "puntos_stats":
        return "puntos_stats" in sistema

    if tipo == "puntos_habilidad":
        return "puntos_habilidad" in sistema

    if tipo == "dinero":
        return "dinero" in sistema

    if tipo == "nivel":
        return sistema.get("usa_niveles", False)

    if tipo == "tiradas":
        return "tiradas" in sistema

    return False


# --------------------------------------------------
# Helpers internos
# --------------------------------------------------

def _preguntar_creacion(campo, texto):
    resp = input(f"❗ {texto} ¿Deseas crearlo? (s/n): ").lower()
    return resp == "s"


def _convertir_a_dinero_si_posible(sistema, recomp, cantidad):
    """
    Intenta convertir una cantidad a dinero.
    Si el sistema no tiene dinero, pregunta si se crea.
    Si no se crea, la cantidad se pierde.
    """
    if cantidad <= 0:
        return

    if "dinero" not in sistema:
        crear = _preguntar_creacion(
            "dinero",
            "El sistema no usa dinero."
        )
        if not crear:
            return
        sistema["dinero"] = {}

    recomp.setdefault("dinero", {})
    recomp["dinero"]["oro"] = recomp["dinero"].get("oro", 0) + cantidad


# --------------------------------------------------
# Función principal
# --------------------------------------------------

def preparar_recompensa_para_aplicar(sistema, recompensas: dict):
    """
    Valida y prepara recompensas antes de aplicarlas.
    Puede:
    - Preguntar al usuario
    - Crear campos faltantes
    - Convertir recompensas (solo si es coherente)
    - Descartar recompensas incompatibles

    Devuelve una copia lista para aplicar.
    """
    recomp = recompensas.copy()

    # -----------------------------
    # PUNTOS DE STATS
    # -----------------------------
    if "puntos_stats" in recomp and "puntos_stats" not in sistema:
        if _preguntar_creacion("puntos_stats", "Este sistema no tiene puntos de stats."):
            sistema["puntos_stats"] = 0
        else:
            cantidad = recomp.pop("puntos_stats")
            _convertir_a_dinero_si_posible(sistema, recomp, cantidad)

    # -----------------------------
    # STATS SIMPLES
    # -----------------------------
    if "stats" in recomp and "stats" not in sistema:
        if _preguntar_creacion("stats", "Este sistema no tiene stats simples."):
            sistema["stats"] = {}
        else:
            total = sum(recomp.pop("stats").values())
            _convertir_a_dinero_si_posible(sistema, recomp, total)

    # -----------------------------
    # PROGRESS STATS
    # -----------------------------
    if "progress_stats" in recomp and "progress_stats" not in sistema:
        if _preguntar_creacion("progress_stats", "Este sistema no tiene progress stats."):
            sistema["progress_stats"] = {}
        else:
            total = sum(
                v.get("actual", 0)
                for v in recomp.pop("progress_stats").values()
            )
            _convertir_a_dinero_si_posible(sistema, recomp, total)

    # -----------------------------
    # DINERO DIRECTO
    # -----------------------------
    if "dinero" in recomp and "dinero" not in sistema:
        if _preguntar_creacion("dinero", "Este sistema no tiene dinero."):
            sistema["dinero"] = {}
        else:
            recomp.pop("dinero")

    # -----------------------------
    # OBJETOS / INVENTARIO
    # -----------------------------
    if "objetos" in recomp:
        inventario_activo = sistema.get("plugins_activos", {}).get("inventario", False)

        if not inventario_activo:
            total_objetos = len(recomp["objetos"])
            print(
                f"➡ El inventario está desactivado. "
                f"{total_objetos} objetos NO pueden entregarse."
            )

            recomp.pop("objetos")

            # Opcional: convertir a dinero solo si es coherente
            _convertir_a_dinero_si_posible(
                sistema,
                recomp,
                total_objetos
            )

    return recomp
