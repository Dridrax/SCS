from core.estado_global import estado


def revisar_y_subir_nivel_destino(sistema, destino=None):
    """
    Hook que revisa si un recurso tipo XP ha alcanzado el límite para subir nivel.
    Si destino es None, usa valores por defecto de xp_actual / xp_para_siguiente / nivel.
    """
    if not sistema:
        return

    niveles_config = sistema.get("niveles_config", {})

    config_nivel = {
        "nivel_key": "nivel",
        "xp_key": destino or "xp_actual",
        "xp_para_siguiente_key": "xp_para_siguiente",
        "factor_escalado": niveles_config.get("factor_escalado", 1.2),
        "modo_subida": niveles_config.get("modo_subida", "auto_stats_y_puntos"),
        "puntos_por_nivel": niveles_config.get("puntos_por_nivel", 5),
        "stats_automaticos": niveles_config.get("stats_automaticos", 0)
    }

    subir_nivel_desde_config(sistema, config_nivel)


def subir_nivel_desde_config(sistema, config_nivel):
    """
    Función interna que maneja subida de nivel con cualquier configuración.
    """
    nivel_key = config_nivel.get("nivel_key", "nivel")
    xp_key = config_nivel.get("xp_key", "xp_actual")
    xp_siguiente_key = config_nivel.get("xp_para_siguiente_key", "xp_para_siguiente")
    factor_escalado = config_nivel.get("factor_escalado", 1.2)
    modo = config_nivel.get("modo_subida", "auto_stats_y_puntos")
    puntos = config_nivel.get("puntos_por_nivel", 5)
    stats_auto = config_nivel.get("stats_automaticos", 0)

    sistema.setdefault(nivel_key, 1)
    sistema.setdefault(xp_key, 0)
    sistema.setdefault(xp_siguiente_key, 100)

    while sistema[xp_key] >= sistema[xp_siguiente_key]:
        xp_necesaria = sistema[xp_siguiente_key]
        sistema[xp_key] -= xp_necesaria

        # Subir nivel
        sistema[nivel_key] += 1

        # Stats automáticos
        if modo in ["auto_stats_y_puntos", "solo_stats"]:
            for cont in ["stats", "progress_stats"]:
                if cont in sistema and isinstance(sistema[cont], dict):
                    for k in sistema[cont]:
                        if cont == "stats":
                            sistema[cont][k] += stats_auto
                        else:
                            sistema[cont][k]["actual"] += stats_auto

        # Puntos de stats
        if modo in ["auto_stats_y_puntos", "solo_puntos"]:
            sistema.setdefault("puntos_stats", 0)
            sistema["puntos_stats"] += puntos

        # Recompensas por nivel
        for recompensa in sistema.get("recompensas_por_nivel", []):
            from core.recompensas.aplicar import aplicar_recompensas
            aplicar_recompensas(sistema, recompensa)


        # Escalar XP para siguiente nivel
        nueva_xp = max(int(xp_necesaria * factor_escalado), xp_necesaria + 1)
        sistema[xp_siguiente_key] = nueva_xp

        print(f"✅ ¡Subiste {nivel_key} al nivel {sistema[nivel_key]}!")

    estado.cambios_no_guardados = True
