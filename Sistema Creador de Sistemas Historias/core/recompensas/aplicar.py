# core/recompensas/aplicar.py

from core.estado_global import estado
from core.utils.funciones_utiles import modificar_progreso
from .tipos import cargar_recursos_desde_sistema
from core.utils.hooks import ejecutar_hook_si_existe
from core.recompensas.tipos import (
    RECURSOS_REGISTRADOS,
    es_tipo_recompensa_valido
)

from plugins.inventario.inventario import agregar_item
from plugins.niveles.helpers_niveles import revisar_y_subir_nivel_destino


# ⚠️ Import opcional (solo si el plugin está activo realmente)
try:
    from plugins.inventario.inventario import agregar_item
except ImportError:
    agregar_item = None


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

            for stat, cantidad in valor.items():
                sistema["stats"][stat] = sistema["stats"].get(stat, 0) + int(cantidad)

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
                
                cantidad = datos.get("cantidad", 0)
                factor = datos.get("factor_escalado", 1.0)
        
                total = int(cantidad * factor)
        
                # 🔥 AQUÍ ocurre la magia real
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

            sistema["puntos_stats"] += int(valor)
            resultado["aplicadas"][tipo] = valor
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

            for moneda, cantidad in valor.items():
                sistema["dinero"][moneda] = sistema["dinero"].get(moneda, 0) + int(cantidad)

            resultado["aplicadas"][tipo] = valor
            continue

        # ─────────────────────────────
        # OBJETOS (PLUGIN)
        # ─────────────────────────────
        if tipo == "objetos":
        
            if not isinstance(valor, dict):
                resultado["ignoradas"][tipo] = "Formato inválido para objetos"
                continue
            
            for nombre_objeto, datos in valor.items():
            
                cantidad = datos.get("cantidad", 1)
                factor = datos.get("factor_escalado", 1.0)

                total = int(cantidad * factor)

                for _ in range(total):
                    item_data = {
                        "nombre": nombre_objeto,
                        "rareza": datos.get("rareza", "comun"),
                        "tipo": datos.get("tipo", "general"),
                        "descripcion": datos.get("descripcion", ""),
                        "efectos": datos.get("efectos", {}),
                        "cantidad": 1
                    }

                    agregar_item(sistema, item_data)

                resultado["aplicadas"].setdefault(tipo, {})
                resultado["aplicadas"][tipo][nombre_objeto] = total



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
        
            if plugin_requerido and not sistema.get("plugins_activos", {}).get(plugin_requerido, False):
                resultado["ignoradas"][tipo] = f"Requiere plugin '{plugin_requerido}'"
                continue
            
            # ───────────────
            # DESTINO DIRECTO (atributo simple del sistema)
            # ───────────────
            if destino in sistema and not isinstance(sistema.get(destino), dict):
            
                if isinstance(valor, dict):
                    # Extraer valor numérico
                    total = 0
                    for sub, info in valor.items():
                        if isinstance(info, dict):
                            v = info.get("valor_base") or info.get("valor") or info.get("cantidad") or 0
                        else:
                            v = info
                        total += int(v)
                else:
                    total = int(valor)
        
                sistema[destino] += total

                # 🔔 Ejecutar hook si existe para este destino
                ejecutar_hook_si_existe(destino, sistema)
                # 🔹 Subida de nivel automática para recursos que sean XP de niveles
                if revisar_y_subir_nivel_destino:
                    # 🔹 Pasar configuración real de niveles para este recurso
                    revisar_y_subir_nivel_destino(
                        sistema,
                        destino=config.get("destino", "xp_actual")  # siempre el destino real
                    )


                
                resultado["aplicadas"][tipo] = total
                continue

            
            # ───────────────
            # DESTINO CONTENEDOR (diccionario)
            # ───────────────
            if destino not in sistema:
                sistema[destino] = {}
        
            if isinstance(valor, dict):
                for subnombre, info in valor.items():
                    if isinstance(info, dict):
                        v = info.get("valor_base") or info.get("valor") or info.get("cantidad") or 0
                    else:
                        v = info
        
                    sistema[destino].setdefault(tipo, {})
                    sistema[destino][tipo][subnombre] = sistema[destino][tipo].get(subnombre, 0) + int(v)
            else:
                sistema[destino][tipo] = sistema[destino].get(tipo, 0) + int(valor)
        
            resultado["aplicadas"][tipo] = valor
            continue




    # ─────────────────────────────
    # Marcar cambios
    # ─────────────────────────────
    if resultado["aplicadas"]:
        estado.cambios_no_guardados = True

    return resultado
