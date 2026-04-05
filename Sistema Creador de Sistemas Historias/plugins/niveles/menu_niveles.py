#plugins/niveles/menu_niveles

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import pedir_int
from plugins.niveles.helpers_niveles import revisar_y_subir_nivel_destino

def menu_configurar_niveles(sistema):
    """
    Menú principal de niveles.
    """

    sistema = estado.sistema_actual
    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    niveles = sistema.setdefault("niveles", {})
    config = niveles.setdefault("niveles_config", {})

    while True:
        print("\n--- CONFIGURACIÓN DE NIVELES ---")
        print("1. Configuración básica (Nivel, XP, XP siguiente + tipo recompensas)")
        print("2. Configuración de subida (Modo, puntos, stats, factor de escalado)")
        print("3. Configurar recompensas por nivel (bloques)")
        print("4. Volver")

        opcion = pedir_int("\nElige una opción: ", default=4)

        if opcion == 1:
            # -------------------------
            # 🔹 CONFIGURACIÓN BÁSICA
            # -------------------------
            print("\n---ACTUAL---")
            print(f"\nNivel: {niveles.get('nivel', 1)}")
            print(f"XP: {niveles.get('xp_actual', 0)}")
            print(f"XP para siguiente nivel: {niveles.get('xp_para_siguiente', 100)}\n")

            niveles["nivel"] = pedir_int(
                f"Nuevo nivel (actual: {niveles.get('nivel',1)}): ",
                default=niveles.get('nivel',1)
            )

            niveles["xp_actual"] = pedir_int(
                f"XP actual (actual: {niveles.get('xp_actual',0)}): ",
                default=niveles.get('xp_actual',0)
            )

            niveles["xp_para_siguiente"] = pedir_int(
                f"XP para siguiente nivel (actual: {niveles.get('xp_para_siguiente',100)}): ",
                default=niveles.get('xp_para_siguiente',100)
            )

            # -------------------------
            # 🎁 TIPO DE RECOMPENSA
            # -------------------------
            print("\n¿Deseas cambiar el Tipo de recompensa por nivel? (S/N)")
            print(f"                Tipo actual: {config.get('tipo_recompensas', 'sin_recompensa')}")
            opcion_tipo = input("\nSi/No: ").lower()

            # Valor por defecto si no se cambia
            tipo_actual = config.get("tipo_recompensas", "sin_recompensa")
            tipo_seleccionado = tipo_actual

            if opcion_tipo == "s":
                print("\n--- TIPO DE RECOMPENSAS POR NIVEL ---")
                print("\n1. Sin recompensa")
                print("2. Cada nivel")
                print("3. Cada X niveles")
                print("4. Nivel específico")
                print("5. Rango con nivel especial (ej: 1-9 normal, 10 especial)")

                mapa = {
                    "sin_recompensa": 1,
                    "cada_nivel": 2,
                    "cada_x": 3,
                    "nivel_especifico": 4,
                    "rango_con_especial": 5
                }
                default_tipo = mapa.get(tipo_actual, 1)
                t = pedir_int(
                    f"Elige tipo (actual: {tipo_actual}): ",
                    default=default_tipo
                )

                tipo_seleccionado = {
                    1: "sin_recompensa",
                    2: "cada_nivel",
                    3: "cada_x",
                    4: "nivel_especifico",
                    5: "rango_con_especial"
                }.get(t, tipo_actual)

                config["tipo_recompensas"] = tipo_seleccionado

                # -------------------------
                # ⚙️ CONFIGURACIÓN EXTRA SEGÚN TIPO
                # -------------------------
                if tipo_seleccionado == "cada_x":
                    config["cada"] = pedir_int(
                        f"Cada cuántos niveles (actual: {config.get('cada',5)}): ",
                        default=config.get("cada", 5)
                    )

                elif tipo_seleccionado == "nivel_especifico":
                    config["nivel_objetivo"] = pedir_int(
                        f"Nivel específico (actual: {config.get('nivel_objetivo',10)}): ",
                        default=config.get("nivel_objetivo", 10)
                    )

                elif tipo_seleccionado == "rango_con_especial":
                    config["cada"] = pedir_int(
                        f"Cada cuántos niveles ocurre el especial (actual: {config.get('cada',10)}): ",
                        default=config.get("cada", 10)
                    )

            # -------------------------
            # 🔄 REVISAR SUBIDA
            # -------------------------
            revisar_y_subir_nivel_destino(sistema, "xp_actual")
            guardar_sistema(print_msg=False)

            print("✅ Configuración básica actualizada.")

        elif opcion == 2:
            # --- Configuración de subida ---
            print("\nModo de subida:")
            print("1. Stats automáticos + Puntos a distribuir")
            print("2. Solo Stats automáticos")
            print("3. Solo Puntos a distribuir")

            modo_actual = config.get('modo_subida', 'auto_stats_y_puntos')
            modo_map = {"auto_stats_y_puntos":1, "solo_stats":2, "solo_puntos":3}
            default_modo = modo_map.get(modo_actual, 1)

            opcion_modo = pedir_int(
                f"Elige opción (actual: {modo_actual}): ",
                default=default_modo
            )

            config["modo_subida"] = {
                1:"auto_stats_y_puntos",
                2:"solo_stats",
                3:"solo_puntos"
            }.get(opcion_modo, modo_actual)

            # Puntos
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

            # Factor escalado
            config["factor_escalado"] = pedir_int(
                f"Factor de escalado de XP por nivel (actual: {int(config.get('factor_escalado',1)*100)}%): ",
                default=int(config.get('factor_escalado',1)*100)
            ) / 100

            guardar_sistema(print_msg=False)
            print("✅ Configuración de subida actualizada.")

        elif opcion == 3:
        
            from core.recompensas.bloques import menu_editar_bloque_interactivo

            lista = niveles.setdefault("recompensas_por_nivel", [])

            while True:
                print("\n--- RECOMPENSAS POR NIVEL ---")

                print("\n1. Añadir recompensa")
                print("2. Editar recompensa")
                print("3. Eliminar recompensa")
                print("4. Ver recompensas")
                print("5. Volver")

                op = pedir_int("Opción: ", default=5)

                # -------------------------
                # VOLVER
                # -------------------------
                if op == 5:
                    guardar_sistema(print_msg=False)
                    break
                
                # -------------------------
                # AÑADIR
                # -------------------------
                elif op == 1:
                    if config.get("tipo_recompensas") == "rango_con_especial":
                        print("\nTipo de bloque a crear:")
                        print("1. Normal (para niveles normales)")
                        print("2. Especial (para el nivel especial)")

                        bloque_tipo = pedir_int("Opción: ", default=1)
                        if bloque_tipo == 2:
                            nueva = {"bloque_especial": {}}
                            menu_editar_bloque_interactivo(
                                nueva["bloque_especial"],
                                "Recompensa Especial"
                            )
                        else:
                            nueva = {"bloque": {}}
                            menu_editar_bloque_interactivo(
                                nueva["bloque"],
                                "Recompensa Normal"
                            )
                    else:
                        # Para todos los otros tipos, usar bloque normal
                        nueva = {"bloque": {}}
                        menu_editar_bloque_interactivo(
                            nueva["bloque"],
                            "Recompensa"
                        )

                    lista.append(nueva)
                    estado.cambios_no_guardados = True
                    print("✅ Recompensa añadida.")

                # -------------------------
                # EDITAR
                # -------------------------
                elif op == 2:
                    if not lista:
                        continue
                    
                    for i, r in enumerate(lista, 1):
                        if config.get("tipo_recompensas") == "rango_con_especial":
                            if "bloque" in r:
                                print(f"{i}. Recompensa Normal")
                            elif "bloque_especial" in r:
                                print(f"{i}. Recompensa Especial")
                            else:
                                print(f"{i}. Recompensa (sin definir)")
                        else:
                            print(f"{i}. Recompensa")

                    idx = pedir_int("Índice: ", default=None)
                    if idx is None or idx < 1 or idx > len(lista):
                        continue
                    
                    recompensa = lista[idx-1]
                    # Detectar qué bloque editar según el tipo
                    if config.get("tipo_recompensas") == "rango_con_especial":
                        if "bloque" in recompensa:
                            menu_editar_bloque_interactivo(
                                recompensa["bloque"],
                                "Recompensa Normal"
                            )
                        elif "bloque_especial" in recompensa:
                            menu_editar_bloque_interactivo(
                                recompensa["bloque_especial"],
                                "Recompensa Especial"
                            )
                        else:
                            # Si no existiera ningún bloque definido, preguntar cuál crear
                            print("La recompensa no tiene bloque definido. ¿Cuál deseas crear?")
                            print("1. Normal")
                            print("2. Especial")
                            bloque_tipo = pedir_int("Opción: ", default=1)
                            if bloque_tipo == 2:
                                recompensa["bloque_especial"] = {}
                                menu_editar_bloque_interactivo(
                                    recompensa["bloque_especial"],
                                    "Recompensa Especial"
                                )
                            else:
                                recompensa["bloque"] = {}
                                menu_editar_bloque_interactivo(
                                    recompensa["bloque"],
                                    "Recompensa Normal"
                                )
                    else:
                        # Tipos normales
                        menu_editar_bloque_interactivo(
                            recompensa.setdefault("bloque", {}),
                            "Recompensa"
                        )

                # -------------------------
                # ELIMINAR
                # -------------------------
                elif op == 3:
                    if not lista:
                        continue
                    
                    for i, r in enumerate(lista, 1):
                        if config.get("tipo_recompensas") == "rango_con_especial":
                            if "bloque" in r:
                                print(f"{i}. Recompensa Normal")
                            elif "bloque_especial" in r:
                                print(f"{i}. Recompensa Especial")
                            else:
                                print(f"{i}. Recompensa (sin definir)")
                        else:
                            print(f"{i}. Recompensa")
                
                    idx = pedir_int("Índice a eliminar: ", default=None)
                
                    if idx and 1 <= idx <= len(lista):
                        lista.pop(idx-1)
                        estado.cambios_no_guardados = True
                        print("✅ Eliminado.")
                
                # -------------------------
                # VER
                # -------------------------
                elif op == 4:
                    if not lista:
                        print(" (sin recompensas)")
                        continue
                    
                    print("\n--- RECOMPENSAS CONFIGURADAS ---")
                
                    for i, r in enumerate(lista, 1):
                        print(f"\nRecompensa {i}:")
                
                        if config.get("tipo_recompensas") == "rango_con_especial":
                            if "bloque" in r:
                                print("  Tipo: Normal")
                                for tipo, contenido in r["bloque"].items():
                                    print(f"    {tipo}: {contenido}")
                            if "bloque_especial" in r:
                                print("  Tipo: Especial")
                                for tipo, contenido in r["bloque_especial"].items():
                                    print(f"    {tipo}: {contenido}")
                            if "bloque" not in r and "bloque_especial" not in r:
                                print("  (sin contenido definido)")
                        else:
                            # Para tipos normales solo hay bloque
                            for tipo, contenido in r.get("bloque", {}).items():
                                print(f"  {tipo}: {contenido}")

        else:
            guardar_sistema(print_msg=False)
            break