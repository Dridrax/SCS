from core.estado_global import estado
from core.recompensas.aplicar import aplicar_recompensas

def revisar_y_subir_nivel(sistema):
    """
    Revisa si la XP actual es suficiente para subir de nivel.
    Si es así, aplica subir_nivel repetidamente hasta que la XP sea menor que la XP necesaria.
    """
    if not sistema:
        return

    config = sistema.get("niveles_config", {})
    factor_escalado = config.get("factor_escalado", 1.2)  # por defecto 120%

    while sistema.get("xp_actual", 0) >= sistema.get("xp_para_siguiente", 100):
        xp_sobrante = sistema["xp_actual"] - sistema["xp_para_siguiente"]
        sistema["xp_actual"] = xp_sobrante  # lo que sobra se mantiene

        subir_nivel(sistema)  # aplica stats/puntos y recompensas

        # Actualizar XP para siguiente nivel con factor de escalado
        xp_siguiente = int(sistema.get("xp_para_siguiente", 100) * factor_escalado)
        sistema["xp_para_siguiente"] = max(xp_siguiente, sistema.get("xp_para_siguiente", 100) + 1)

        print(f"✅ ¡Subiste al nivel {sistema['nivel']}!")


def subir_nivel(sistema):
    """
    Lógica para subir de nivel:
    - Incrementa nivel
    - Aplica stats automáticos y/o puntos de stats según modo de subida
    - Llama a aplicar_recompensas si corresponde
    """
    if not sistema:
        return

    sistema.setdefault("nivel", 1)

    sistema["nivel"] += 1

    config = sistema.get("niveles_config", {})
    modo = config.get("modo_subida", "auto_stats_y_puntos")
    puntos = config.get("puntos_por_nivel", 5)
    stats_auto = config.get("stats_automaticos", 0)

    # Stats automáticos
    if modo in ["auto_stats_y_puntos", "solo_stats"]:
        if "stats" in sistema:
            for key in sistema["stats"]:
                sistema["stats"][key] += stats_auto
        if "progress_stats" in sistema:
            for key in sistema["progress_stats"]:
                sistema["progress_stats"][key]["actual"] += stats_auto

    # Puntos de stats a distribuir
    if modo in ["auto_stats_y_puntos", "solo_puntos"]:
        sistema.setdefault("puntos_stats", 0)
        sistema["puntos_stats"] += puntos

    # Llamada a recompensas opcionales
    for recompensa in sistema.get("recompensas_por_nivel", []):
        aplicar_recompensas(sistema, recompensa)

    estado.cambios_no_guardados = True
