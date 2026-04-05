#plugins/niveles/helpers_niveles.py
from core.estado_global import estado
from core.utils.funciones_utiles import modificar_progreso  
from core.recompensas.tipos import obtener_tipos_recursos_validos

def revisar_y_subir_nivel_destino(sistema, destino=None):
    """
    Hook que revisa si un recurso tipo XP ha alcanzado el límite para subir nivel.
    """
    if not sistema:
        return

    niveles = sistema.get("niveles", {})
    if not niveles:
        return

    niveles_config = niveles.get("niveles_config", {})

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

def mostrar_recompensas_por_nivel(sistema, nivel_inicial, nivel_final):
    """
    Muestra las recompensas acumuladas de forma simple:
    base × niveles_subidos
    SOLO visual, sin lógica real.
    """
    if not sistema:
        print("❌ Sistema vacío")
        return

    niveles = sistema.get("niveles", {})
    if not niveles:
        print("❌ No hay información de niveles")
        return

    recompensas = niveles.get("recompensas_por_nivel", [])
    if not recompensas:
        print(" (sin recompensas configuradas)")
        return

    tipos_validos = obtener_tipos_recursos_validos()

    niveles_subidos = nivel_final - nivel_inicial

    if niveles_subidos <= 0:
        return

    print("\n--- RECOMPENSAS ACUMULADAS ---\n")
    print(f"(Subida de +{niveles_subidos} niveles)\n")

    for idx, rec in enumerate(recompensas, 1):
        print(f"Recompensa {idx}:")
        bloque = rec.get("bloque", {})

        for tipo, detalle in bloque.items():
            if tipo not in tipos_validos:
                continue

            # Tipos con subclaves (dinero, puntos, etc.)
            if isinstance(detalle, dict) and all(isinstance(v, dict) for v in detalle.values()):
                for subclave, subdetalle in detalle.items():
                    base = subdetalle.get("valor_base", 0)
                    total = base * niveles_subidos
                    print(f"  {subclave}: {base} x (Lv: +{niveles_subidos}) = {total}")
            else:
                # Otros tipos simples
                if isinstance(detalle, dict):
                    base = detalle.get("valor_base", 0)
                    total = base * niveles_subidos
                    print(f"  {tipo}: {base} x (Lv: +{niveles_subidos}) = {total}")
                else:
                    print(f"  {tipo}: {detalle}")

def subir_nivel_desde_config(sistema, config_nivel):
    """
    Maneja subida de nivel usando sistema["niveles"]
    """
    niveles = sistema.get("niveles", {})
    if not niveles:
        return

    nivel_key = config_nivel.get("nivel_key", "nivel")
    xp_key = config_nivel.get("xp_key", "xp_actual")
    xp_siguiente_key = config_nivel.get("xp_para_siguiente_key", "xp_para_siguiente")
    factor_escalado = config_nivel.get("factor_escalado", 1.2)
    modo = config_nivel.get("modo_subida", "auto_stats_y_puntos")
    puntos = config_nivel.get("puntos_por_nivel", 5)
    stats_auto = config_nivel.get("stats_automaticos", 0)

    # Asegurar estructura dentro de niveles
    niveles.setdefault(nivel_key, 1)
    niveles.setdefault(xp_key, 0)
    niveles.setdefault(xp_siguiente_key, 100)

    # Guardar nivel inicial para mostrar salto final
    nivel_inicial = niveles[nivel_key]

    while niveles[xp_key] >= niveles[xp_siguiente_key]:
        xp_necesaria = niveles[xp_siguiente_key]
        niveles[xp_key] -= xp_necesaria

        # Subir nivel
        niveles[nivel_key] += 1

        # -------------------------
        # 📊 Stats automáticos (ROOT)
        # -------------------------
        if modo in ["auto_stats_y_puntos", "solo_stats"]:
            for cont in ["stats", "progress_stats"]:
                if cont in sistema and isinstance(sistema[cont], dict):
                    for k in sistema[cont]:
                        if cont == "stats":
                            sistema[cont][k] += stats_auto
                        else:
                            modificar_progreso(sistema[cont][k], stats_auto)

        # -------------------------
        # 🎯 Puntos de stats (ROOT)
        # -------------------------
        if modo in ["auto_stats_y_puntos", "solo_puntos"]:
            sistema.setdefault("puntos_stats", 0)
            sistema["puntos_stats"] += puntos

        # -------------------------
        # 🎁 Recompensas por nivel (desde niveles)
        # -------------------------
        from core.recompensas.aplicar import aplicar_recompensas
        from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar

        nivel_actual = niveles[nivel_key]
        niveles_config = niveles.get("niveles_config", {})

        tipo = niveles_config.get("tipo_recompensas", "sin_recompensa")
        cada = niveles_config.get("cada", 1)
        nivel_objetivo = niveles_config.get("nivel_objetivo", 1)

        lista = niveles.get("recompensas_por_nivel", [])

        # ⚫ Sin recompensa
        if tipo == "sin_recompensa":
            pass
        
        # 🟢 Cada nivel
        elif tipo == "cada_nivel":
            for recompensa in lista:
                aplicar_recompensas(sistema, preparar_recompensa_para_aplicar(sistema, recompensa.get("bloque", {})))

        # 🔵 Cada X niveles
        elif tipo == "cada_x":
            if cada > 0 and nivel_actual % cada == 0:
                for recompensa in lista:
                    aplicar_recompensas(sistema, preparar_recompensa_para_aplicar(sistema, recompensa.get("bloque", {})))

        # 🟣 Nivel específico
        elif tipo == "nivel_especifico":
            if nivel_actual == nivel_objetivo:
                for recompensa in lista:
                    aplicar_recompensas(sistema, preparar_recompensa_para_aplicar(sistema, recompensa.get("bloque", {})))

        # 🟡 Rango con nivel especial
        elif tipo == "rango_con_especial":
            if cada > 0:
                if nivel_actual % cada == 0:
                    # 🎉 ESPECIAL
                    for recompensa in lista:
                        aplicar_recompensas(
                            sistema,
                            preparar_recompensa_para_aplicar(sistema, recompensa.get("bloque_especial", {}))
                        )
                else:
                    # 🔁 NORMAL
                    for recompensa in lista:
                        aplicar_recompensas(
                            sistema,
                            preparar_recompensa_para_aplicar(sistema, recompensa.get("bloque", {}))
                        )

        # ⚠️ fallback (por seguridad)
        else:
            for recompensa in lista:
                aplicar_recompensas(sistema, preparar_recompensa_para_aplicar(sistema, recompensa.get("bloque", {})))
            

        # -------------------------
        # 📈 Escalado de XP
        # -------------------------
        nueva_xp = max(int(xp_necesaria * factor_escalado), xp_necesaria + 1)
        niveles[xp_siguiente_key] = nueva_xp

    # Mostrar solo el salto final de nivel
    if nivel_inicial != niveles[nivel_key]:
        print(f"✅ Nivel {nivel_inicial} -> {niveles[nivel_key]}!")
        mostrar_recompensas_por_nivel(sistema, nivel_inicial, niveles[nivel_key])

    estado.cambios_no_guardados = True