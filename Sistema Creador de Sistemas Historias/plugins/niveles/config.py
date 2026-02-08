def activar_plugin_niveles(sistema):
    """
    Inicializa todos los campos del plugin de niveles.
    Todos los valores son editables por el administrador.
    """
    sistema.setdefault("nivel", 1)
    sistema.setdefault("xp_actual", 0)
    sistema.setdefault("xp_para_siguiente", 100)

    # Configuración editable de la subida de nivel
    sistema.setdefault("niveles_config", {
        "modo_subida": "auto_stats_y_puntos",  # opciones: "auto_stats_y_puntos", "solo_stats", "solo_puntos"
        "puntos_por_nivel": 5,                 # puntos de stats a repartir
        "stats_automaticos": 5                 # cantidad que suben automáticamente las stats si corresponde
    })
