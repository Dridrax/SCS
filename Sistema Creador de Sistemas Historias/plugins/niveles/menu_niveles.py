from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int
from plugins.niveles.helpers import revisar_y_subir_nivel

def menu_configurar_niveles(sistema):
    """
    Menú principal de niveles. Permite separar la configuración básica de la configuración de subida.
    """
    sistema = estado.sistema_actual
    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    config = sistema.setdefault("niveles_config", {})

    while True:
        print("\n=== CONFIGURACIÓN DE NIVELES ===")
        print("1. Configuración básica (Nivel, XP, XP siguiente)")
        print("2. Configuración de subida (Modo, puntos, stats, factor de escalado)")
        print("3. Volver")
        opcion = pedir_int("Elige una opción: ", default=3)

        if opcion == 1:
            # --- Configuración básica ---
            print(f"\nNivel actual: {sistema.get('nivel', 1)}")
            print(f"XP actual: {sistema.get('xp_actual', 0)}")
            print(f"XP para siguiente nivel: {sistema.get('xp_para_siguiente', 100)}")

            sistema["nivel"] = pedir_int(f"Nuevo nivel (actual: {sistema.get('nivel',1)}): ", default=sistema.get('nivel',1))
            sistema["xp_actual"] = pedir_int(f"XP actual (actual: {sistema.get('xp_actual',0)}): ", default=sistema.get('xp_actual',0))
            sistema["xp_para_siguiente"] = pedir_int(f"XP para siguiente nivel (actual: {sistema.get('xp_para_siguiente',100)}): ", default=sistema.get('xp_para_siguiente',100))

            # Revisar si se debe subir de nivel automáticamente
            revisar_y_subir_nivel(sistema)
            print("✅ Configuración básica actualizada.")

        elif opcion == 2:
            # --- Configuración de subida ---
            print("\nModo de subida:")
            print("1. Stats automáticos + Puntos a distribuir")
            print("2. Solo Stats automáticos")
            print("3. Solo Puntos a distribuir")
        
            modo_actual = config.get('modo_subida','auto_stats_y_puntos')
            modo_map = {"auto_stats_y_puntos":1, "solo_stats":2, "solo_puntos":3}
            default_modo = modo_map.get(modo_actual, 1)
        
            opcion_modo = pedir_int(f"Elige opción (actual: {modo_actual}): ", default=default_modo)
            config["modo_subida"] = {1:"auto_stats_y_puntos", 2:"solo_stats", 3:"solo_puntos"}.get(opcion_modo, modo_actual)
        
            # Puntos a distribuir
            if config["modo_subida"] in ["auto_stats_y_puntos", "solo_puntos"]:
                config["puntos_por_nivel"] = pedir_int(
                    f"Puntos a distribuir por nivel (actual: {config.get('puntos_por_nivel',5)}): ",
                    default=config.get('puntos_por_nivel',5)
                )
            else:
                config["puntos_por_nivel"] = 0
        
            # Stats automáticos
            if config["modo_subida"] in ["auto_stats_y_puntos", "solo_stats"]:
                config["stats_automaticos"] = pedir_int(
                    f"Cantidad que suben automáticamente las stats (actual: {config.get('stats_automaticos',0)}): ",
                    default=config.get('stats_automaticos',0)
                )
            else:
                config["stats_automaticos"] = 0
        
            # Factor de escalado
            config["factor_escalado"] = pedir_int(
                f"Factor de escalado de XP por nivel (actual: {int(config.get('factor_escalado',1)*100)}%): ",
                default=int(config.get('factor_escalado',1)*100)
            ) / 100  # Convertimos a decimal interno
        
            estado.cambios_no_guardados = True
            print("✅ Configuración de subida actualizada.")


        else:
            break
