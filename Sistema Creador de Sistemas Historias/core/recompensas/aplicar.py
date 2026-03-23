# core/recompensas/aplicar.py

from core.estado_global import estado
from core.utils.funciones_utiles import modificar_progreso
from .tipos import cargar_recursos_desde_sistema
from core.utils.hooks import ejecutar_hook_si_existe
from core.recompensas.tipos import (RECURSOS_REGISTRADOS,
                                    es_tipo_recompensa_valido)
from core.recompensas.validacion import (validar_recompensas_entidad,
                                         manejar_conflictos,
                                         filtrar_recompensas_validas_entidad)

from plugins.inventario.inventario import agregar_item, eliminar_item
from plugins.niveles.helpers_niveles import revisar_y_subir_nivel_destino




def aplicar_recompensas(sistema: dict, recompensas: dict) -> dict:
    """
    Aplica recompensas al sistema.

    Reglas:
    - No imprime nada
    - No pregunta nada
    - Solo aplica lo posible
    - Valida tipos usando API oficial
    - Devuelve resumen estructurado

    Return:
    {
        "aplicadas": {...},
        "ignoradas": {...}
    }
    """

    cargar_recursos_desde_sistema(sistema)

    # ─────────────────────────────
    # VALIDAR RECOMPENSAS / PENALIZACIONES
    # ─────────────────────────────
    entidad_dummy = {"recompensas": recompensas, "penalizaciones": {}}  # si la entidad tiene penalizaciones, pásalas aquí
    resultado_validacion = validar_recompensas_entidad(entidad_dummy)
    
    if resultado_validacion["invalidas"]:
        accion = manejar_conflictos("Recompensas actuales", resultado_validacion)
    
        if accion == "cancelar":
            return {"aplicadas": {}, "ignoradas": {}}
        elif accion == "eliminar_recompensas":
            entidad_dummy = filtrar_recompensas_validas_entidad(entidad_dummy)
            recompensas = entidad_dummy["recompensas"]
        elif accion == "eliminar_entidad":
            # aquí si quieres eliminar toda la misión/racha/entidad en otro nivel, habría que llamarlo desde el sistema principal
            return {"aplicadas": {}, "ignoradas": {}}
        elif accion == "activar_plugins":
            pass  # los plugins ya se activaron dentro del menú

    resultado = {
        "aplicadas": {},
        "ignoradas": {}
    }

    if not isinstance(sistema, dict) or not isinstance(recompensas, dict):
        return resultado

    for tipo, valor in recompensas.items():

        # ─────────────────────────────
        # Validación oficial SCS
        # ─────────────────────────────
        if not es_tipo_recompensa_valido(tipo):
            resultado["ignoradas"][tipo] = "Tipo de recompensa no válido"
            continue

        # ─────────────────────────────
        # STATS
        # ─────────────────────────────
        if tipo == "stats":
            if "stats" not in sistema or not isinstance(valor, dict):
                resultado["ignoradas"][tipo] = "Sistema no soporta stats"
                continue

            for stat, datos in valor.items():
                if isinstance(datos, dict):
                    cantidad = datos.get("valor_base", 0)
                    factor = datos.get("factor_escalado", 1.0)
                    total = int(cantidad * factor)
                else:
                    total = int(datos)

                sistema["stats"][stat] = sistema["stats"].get(stat, 0) + total

            resultado["aplicadas"][tipo] = valor
            continue

        # ─────────────────────────────
        # PROGRESS STATS
        # ─────────────────────────────
        if tipo == "progress_stats":
        
            if not isinstance(valor, dict):
                resultado["ignoradas"][tipo] = "Formato inválido para progress_stats"
                continue
            
            for nombre_stat, datos in valor.items():
            
                stat = sistema.get("progress_stats", {}).get(nombre_stat)

                if not stat:
                    resultado["ignoradas"].setdefault(tipo, {})
                    resultado["ignoradas"][tipo] = f"{nombre_stat} no existe"
                    continue
                
                if isinstance(datos, dict):
                    cantidad = datos.get("valor_base", 0)
                    factor = datos.get("factor_escalado", 1.0)
                    total = int(cantidad * factor)
                else:
                    # Si viene un int directo
                    total = int(datos)

                # 🔥 Aplicar progreso
                modificar_progreso(stat, total)

                resultado["aplicadas"].setdefault(tipo, {})
                resultado["aplicadas"][tipo][nombre_stat] = total



        # ─────────────────────────────
        # PUNTOS STATS
        # ─────────────────────────────
        if tipo == "puntos_stats":
        
            if "puntos_stats" not in sistema:
                resultado["ignoradas"][tipo] = "Sistema no usa puntos_stats"
                continue
            
            # valor es un dict con subclaves de puntos
            if not isinstance(valor, dict):
                resultado["ignoradas"][tipo] = "Formato inválido para puntos_stats"
                continue
            
            for subclave, datos in valor.items():
            
                if isinstance(datos, dict):
                    # Tomamos el valor_base y factor_escalado
                    cantidad = datos.get("valor_base", 0)
                    factor = datos.get("factor_escalado", 1.0)
                    total = int(cantidad * factor)
        
                    sistema["puntos_stats"] += total
        
                    resultado["aplicadas"].setdefault(tipo, {})
                    resultado["aplicadas"][tipo][subclave] = total
        
                else:
                    # por compatibilidad, si viene un int directo
                    sistema["puntos_stats"] += int(datos)
                    resultado["aplicadas"].setdefault(tipo, {})
                    resultado["aplicadas"][tipo][subclave] = int(datos)
        
            continue

        # ─────────────────────────────
        # PUNTOS HABILIDAD
        # ─────────────────────────────
        if tipo == "puntos_habilidad":
            if "puntos_habilidad" not in sistema:
                resultado["ignoradas"][tipo] = "Sistema no usa puntos_habilidad"
                continue

            sistema["puntos_habilidad"] += int(valor)
            resultado["aplicadas"][tipo] = valor
            continue

        # ─────────────────────────────
        # DINERO
        # ─────────────────────────────
        if tipo == "dinero":
            if "dinero" not in sistema or not isinstance(valor, dict):
                resultado["ignoradas"][tipo] = "Sistema no maneja dinero"
                continue

            for moneda, datos in valor.items():
                if isinstance(datos, dict):
                    cantidad = datos.get("valor_base", 0)
                    factor = datos.get("factor_escalado", 1.0)
                    total = int(cantidad * factor)
                else:
                    total = int(datos)

                sistema["dinero"][moneda] = sistema["dinero"].get(moneda, 0) + total

            resultado["aplicadas"][tipo] = valor
            continue

        # ─────────────────────────────
        # OBJETOS (PLUGIN)
        # ─────────────────────────────
        if tipo == "objetos":

            if not isinstance(valor, (list, dict)):
                resultado["ignoradas"][tipo] = "Formato inválido para objetos"
                continue

            resultado["aplicadas"].setdefault(tipo, {})

            # ─────────────────────────
            # FUNCIÓN INTERNA SEGURA
            # ─────────────────────────
            def calcular_total(datos: dict) -> int:
                cantidad = (
                    datos.get("cantidad_base")
                    if datos.get("cantidad_base") is not None
                    else datos.get("cantidad")
                )

                if cantidad is None:
                    cantidad = 1

                factor = datos.get("factor_escalado", 1.0)
                return int(cantidad * factor)

            # ─────────────────────────
            # FORMATO NUEVO (DICT)
            # ─────────────────────────
            if isinstance(valor, dict):
                for nombre_objeto, datos in valor.items():
                    if not isinstance(datos, dict):
                        continue

                    total = calcular_total(datos)

                    item_data = {
                        "nombre": nombre_objeto,
                        "rareza": datos.get("rareza", ""),
                        "tipo": datos.get("tipo", ""),
                        "descripcion": datos.get("descripcion", ""),
                        "efectos": datos.get("efectos", {}),
                        "cantidad": total
                    }

                    if total > 0:
                        agregar_item(sistema, item_data)

                    elif total < 0:
                        # Buscar objeto existente por firma
                        inventario = sistema.get("inventario", {})
                        for obj_id, obj in inventario.items():
                            if (
                                obj.get("nombre") == item_data["nombre"]
                                and obj.get("tipo") == item_data["tipo"]
                                and obj.get("rareza") == item_data["rareza"]
                                and obj.get("descripcion") == item_data["descripcion"]
                                and obj.get("efectos") == item_data["efectos"]
                            ):
                                eliminar_item(sistema, obj_id, cantidad=abs(total))
                                break

                    resultado["aplicadas"][tipo][nombre_objeto] = {
                        "cantidad": total,
                        "tipo": item_data["tipo"],
                        "rareza": item_data["rareza"],
                        "descripcion": item_data["descripcion"],
                        "efectos": item_data["efectos"]
                    }

            # ─────────────────────────
            # FORMATO LISTA (ANTIGUO)
            # ─────────────────────────
            else:
                for datos in valor:
                    if not isinstance(datos, dict):
                        continue

                    nombre_objeto = datos.get("nombre", "objeto")
                    total = calcular_total(datos)

                    item_data = {
                        "nombre": nombre_objeto,
                        "rareza": datos.get("rareza", "comun"),
                        "tipo": datos.get("tipo", "general"),
                        "descripcion": datos.get("descripcion", ""),
                        "efectos": datos.get("efectos", {}),
                        "cantidad": total
                    }

                    if total > 0:
                        agregar_item(sistema, item_data)
                    
                    elif total < 0:
                        # Buscar objeto existente por firma
                        inventario = sistema.get("inventario", {})
                        for obj_id, obj in inventario.items():
                            if (
                                obj.get("nombre") == item_data["nombre"]
                                and obj.get("tipo") == item_data["tipo"]
                                and obj.get("rareza") == item_data["rareza"]
                                and obj.get("descripcion") == item_data["descripcion"]
                                and obj.get("efectos") == item_data["efectos"]
                            ):
                                eliminar_item(sistema, obj_id, cantidad=abs(total))
                                break

                    resultado["aplicadas"][tipo][nombre_objeto] = {
                        "cantidad": total,
                        "tipo": item_data["tipo"],
                        "rareza": item_data["rareza"],
                        "descripcion": item_data["descripcion"],
                        "efectos": item_data["efectos"]
                    }

            continue


        # ─────────────────────────────
        # NIVEL
        # ─────────────────────────────
        if tipo == "nivel":
            if not sistema.get("usa_niveles", False):
                resultado["ignoradas"][tipo] = "Sistema no usa niveles"
                continue

            sistema["nivel"] = sistema.get("nivel", 1) + int(valor)
            resultado["aplicadas"][tipo] = valor
            continue

        # ─────────────────────────────
        # TIRADAS
        # ─────────────────────────────
        if tipo == "tiradas":
            if "tiradas" not in sistema:
                resultado["ignoradas"][tipo] = "Sistema no usa tiradas"
                continue

            sistema["tiradas"] += int(valor)
            resultado["aplicadas"][tipo] = valor
            continue


        # ─────────────────────────────
        # RECURSOS DINÁMICOS
        # ─────────────────────────────
        if tipo in RECURSOS_REGISTRADOS:

            config = RECURSOS_REGISTRADOS[tipo]
            plugin_requerido = config.get("requiere_plugin")
            destino = config.get("destino", "recursos")
            modo = config.get("modo", "contenedor")

            # Plugin requerido
            if plugin_requerido and not sistema.get("plugins_activos", {}).get(plugin_requerido, False):
                resultado["ignoradas"][tipo] = f"Requiere plugin '{plugin_requerido}'"
                continue

            # 🔥 Calcular total real (valor_base * factor_escalado si existe)
            total = 0

            if isinstance(valor, dict):
                for _, info in valor.items():
                    if isinstance(info, dict):
                        base = (
                            info.get("valor_base")
                            or info.get("valor")
                            or info.get("cantidad")
                            or 0
                        )
                        factor = info.get("factor_escalado", 1.0)
                        total += int(base * factor)
                    else:
                        total += int(info)
            else:
                total = int(valor)

            # ==========================================================
            # 🔥 BLINDAJE ABSOLUTO PARA XP
            # ==========================================================
            if destino == "xp_actual":

                # Asegurar que xp_actual sea SIEMPRE int
                if not isinstance(sistema.get("xp_actual"), int):
                    sistema["xp_actual"] = 0

                sistema["xp_actual"] += total

                # Ejecutar subida de nivel automática
                revisar_y_subir_nivel_destino(sistema, destino="xp_actual")

                resultado["aplicadas"][tipo] = total
                continue

            # ==========================================================
            # 🔹 MODO SIMPLE (valor numérico directo)
            # ==========================================================
            if modo == "simple":
            
                # 🔹 Caso A: destino es contenedor global "recursos"
                if destino == "recursos":
                
                    if "recursos" not in sistema or not isinstance(sistema["recursos"], dict):
                        sistema["recursos"] = {}

                    if not isinstance(sistema["recursos"].get(tipo), int):
                        sistema["recursos"][tipo] = 0

                    sistema["recursos"][tipo] += total

                # 🔹 Caso B: destino es campo numérico directo (xp, puntos, etc)
                else:
                
                    if not isinstance(sistema.get(destino), int):
                        sistema[destino] = 0

                    sistema[destino] += total

                ejecutar_hook_si_existe(destino, sistema)

                resultado["aplicadas"][tipo] = total
                continue

            # ==========================================================
            # 🔹 MODO CONTENEDOR (estructura multinivel)
            # ==========================================================
            if modo == "contenedor":

                if destino not in sistema or not isinstance(sistema.get(destino), dict):
                    sistema[destino] = {}

                if tipo not in sistema[destino] or not isinstance(sistema[destino].get(tipo), dict):
                    sistema[destino][tipo] = {}

                if isinstance(valor, dict):
                    for subnombre, info in valor.items():

                        if isinstance(info, dict):
                            base = (
                                info.get("valor_base")
                                or info.get("valor")
                                or info.get("cantidad")
                                or 0
                            )
                            factor = info.get("factor_escalado", 1.0)
                            v = int(base * factor)
                        else:
                            v = int(info)

                        sistema[destino][tipo][subnombre] = (
                            sistema[destino][tipo].get(subnombre, 0) + v
                        )

                resultado["aplicadas"][tipo] = total
                continue



    # ─────────────────────────────
    # Marcar cambios
    # ─────────────────────────────
    if resultado["aplicadas"]:
        estado.cambios_no_guardados = True

    return resultado
