# core/recompensas/ui_preparacion.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import pedir_int
from .tipos import (TIPOS_RECOMPENSA, RECURSOS_REGISTRADOS, TIPOS_RAREZAS, RAREZAS_REGISTRADAS, 
                    registrar_recurso, esta_tipo_base_activo, activar_tipo_base, desactivar_tipo_base,
                    registrar_rareza, esta_rareza_base_activa, activar_rareza_base, desactivar_rareza_base)

# ─────────────────────────────────────────────
# VALIDACIÓN DE SOPORTE DE RECOMPENSAS
# ─────────────────────────────────────────────
def sistema_soporta_recompensa(sistema, tipo):
    """
    Comprueba si el sistema soporta un tipo de recompensa.
    Incluye soporte para recursos dinámicos.
    """

    # Recursos dinámicos siempre son válidos
    if tipo == "recursos":
        return True

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
        return sistema.get("plugins_activos", {}).get("niveles", False)

    if tipo == "tiradas":
        return "tiradas" in sistema

    return False

# ─────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────
def _preguntar_creacion(texto):
    resp = input(f"❗ {texto} ¿Deseas crearlo? (s/n): ").lower()
    return resp == "s"

def _convertir_a_dinero_si_posible(sistema, recomp, cantidad):
    if cantidad <= 0:
        return

    if "dinero" not in sistema:
        crear = _preguntar_creacion("El sistema no usa dinero.")
        if not crear:
            return
        sistema["dinero"] = {}

    recomp.setdefault("dinero", {})
    recomp["dinero"]["oro"] = recomp["dinero"].get("oro", 0) + cantidad

# ─────────────────────────────────────────────
# PREPARAR RECOMPENSA
# ─────────────────────────────────────────────
def preparar_recompensa_para_aplicar(sistema, recompensas: dict):
    """
    Valida y prepara recompensas antes de aplicarlas.
    Ahora soporta recursos dinámicos.
    """

    recomp = recompensas.copy()

    # ───────────────
    # Recursos dinámicos
    # ───────────────
    if "recursos" in recomp:
        sistema.setdefault("recursos_definidos", {})
        sistema.setdefault("recursos", {})

        for nombre, cantidad in list(recomp["recursos"].items()):
            if nombre not in sistema["recursos_definidos"]:
                print(f"⚠ El recurso '{nombre}' no está definido en el sistema.")

                # 🔥 Validación anti-colisiones estructurales
                if nombre.lower() in sistema.get("dinero", {}):
                    print("❌ Conflicto: ya existe como moneda en 'dinero'. Recompensa descartada.")
                    recomp["recursos"].pop(nombre)
                    continue
                
                if nombre in sistema.get("stats", {}):
                    print("❌ Conflicto: ya existe como stat. Recompensa descartada.")
                    recomp["recursos"].pop(nombre)
                    continue
                
                if nombre in sistema.get("progress_stats", {}):
                    print("❌ Conflicto: ya existe como progress_stat. Recompensa descartada.")
                    recomp["recursos"].pop(nombre)
                    continue
                
                if _preguntar_creacion(f"¿Crear recurso '{nombre}'?"):
                    sistema["recursos_definidos"][nombre] = {
                        "descripcion": "",
                        "requiere_plugin": None,
                        "destino": "recursos"  # 🔥 Default limpio
                    }
                    print(f"Recurso '{nombre}' creado.")
                else:
                    print(f"Recurso '{nombre}' descartado.")
                    recomp["recursos"].pop(nombre)

        if not recomp["recursos"]:
            recomp.pop("recursos")

    # ───────────────
    # PUNTOS DE STATS
    # ───────────────
    if "puntos_stats" in recomp and "puntos_stats" not in sistema:
        if _preguntar_creacion("Este sistema no tiene puntos de stats."):
            sistema["puntos_stats"] = 0
        else:
            cantidad = recomp.pop("puntos_stats")
            _convertir_a_dinero_si_posible(sistema, recomp, cantidad)

    # ───────────────
    # STATS
    # ───────────────
    if "stats" in recomp and "stats" not in sistema:
        if _preguntar_creacion("Este sistema no tiene stats simples."):
            sistema["stats"] = {}
        else:
            total = sum(recomp.pop("stats").values())
            _convertir_a_dinero_si_posible(sistema, recomp, total)

    # ───────────────
    # PROGRESS STATS
    # ───────────────
    if "progress_stats" in recomp and "progress_stats" not in sistema:
        if _preguntar_creacion("Este sistema no tiene progress stats."):
            sistema["progress_stats"] = {}
        else:
            total = sum(
                v.get("actual", 0)
                for v in recomp.pop("progress_stats").values()
            )
            _convertir_a_dinero_si_posible(sistema, recomp, total)

    # ───────────────
    # DINERO
    # ───────────────
    if "dinero" in recomp and "dinero" not in sistema:
        if _preguntar_creacion("Este sistema no tiene dinero."):
            sistema["dinero"] = {}
        else:
            recomp.pop("dinero")

    # ───────────────
    # OBJETOS
    # ───────────────
    if "objetos" in recomp:
        if not sistema.get("plugins_activos", {}).get("inventario", False):
            total_objetos = len(recomp["objetos"])
            print(f"➡ Inventario desactivado. {total_objetos} objetos descartados.")
            recomp.pop("objetos")
            _convertir_a_dinero_si_posible(sistema, recomp, total_objetos)
        else:
            # ✅ Objetos activos: dejarlos tal como vienen (ya vienen con cantidad, tipo, rareza, etc.)
            pass  # nada que hacer



    return recomp

# ─────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────
def destinos_disponibles(plugin):
    """
    Devuelve la lista de destinos válidos según el plugin requerido.
    """

    plugins_destinos = {
        None: [
            "stats",
            "progress_stats",
            "dinero",      #  Nuevo destino válido
            "recursos",    #  Contenedor limpio de recursos dinámicos
        ],
        "niveles": [
            "nivel",
            "xp_actual",
            "xp_para_siguiente",
        ],
        # Añadir futuros plugins aquí
    }

    return plugins_destinos.get(plugin, plugins_destinos[None])

def seleccionar_destino(plugin, destino_actual=None):
    """
    Permite al usuario elegir un destino válido mostrando opciones numeradas.

    Parámetros:
        plugin (str | None): Plugin requerido para filtrar destinos.
        destino_actual (str | None): Para mostrar el valor actual como predeterminado.

    Retorna:
        str: Destino elegido.
    """
    destinos_validos = destinos_disponibles(plugin)
    while True:
        print("\nDestinos válidos:")
        for i, d in enumerate(destinos_validos, 1):
            if d == destino_actual:
                print(f"{i}. {d} (actual)")
            else:
                print(f"{i}. {d}")
        try:
            eleccion = input("Selecciona el destino por número (Enter para mantener actual): ").strip()
            if eleccion == "" and destino_actual:
                return destino_actual
            indice = int(eleccion) - 1
            if 0 <= indice < len(destinos_validos):
                return destinos_validos[indice]
            else:
                print("Número inválido. Intenta de nuevo.")
        except ValueError:
            print("Entrada inválida. Ingresa un número.")

def seleccionar_modo(modo_actual=None):
    while True:
        print("\nModo del recurso:")
        print("1. Simple (valor numérico directo)")
        print("2. Contenedor (subtipos internos)")

        opcion = input("Selecciona modo: ").strip()

        if opcion == "1":
            return "simple"
        elif opcion == "2":
            return "contenedor"
        elif not opcion and modo_actual:
            return modo_actual
        else:
            print("Opción inválida.")

# ─────────────────────────────
# MENÚ MODIFICAR TIPOS DINAMICOS
# ─────────────────────────────
def menu_configurar_recurso_dinamicos(sistema=None):
    sistema = sistema or estado.sistema_actual 

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    sistema.setdefault("recursos_definidos", {})

    while True:
        print("\n=== CONFIGURACIÓN DE RECURSOS DINAMICOS===")
        print("1. Ver recursos")
        print("2. Crear recurso")
        print("3. Editar recurso")
        print("4. Eliminar recurso")
        print("0. Volver")

        opcion = input("Selecciona opción: ").strip()

        # ───────────────
        # VER
        # ───────────────
        if opcion == "1":
            if not sistema["recursos_definidos"]:
                print("No hay recursos definidos.")
            else:
                for nombre, config in sistema["recursos_definidos"].items():
                    print(f"\n• {nombre}")
                    print(f"  Descripción: {config.get('descripcion', '')}")
                    print(f"  Requiere plugin: {config.get('requiere_plugin')}")
                    print(f"  Destino: {config.get('destino')}")
                    print(f"  Modo: {config.get('modo')}")

        # ───────────────
        # CREAR
        # ───────────────
        elif opcion == "2":
            nombre = input("Nombre del recurso: ").strip()
            
            if not nombre:
                print("Nombre inválido.")
                continue

            if nombre.lower() in sistema.get("dinero", {}):
                print("❌ Ya existe una moneda con ese nombre en 'dinero'.")
                continue

            if nombre in sistema.get("stats", {}):
                print("❌ Ya existe un stat con ese nombre.")
                continue

            if nombre in sistema.get("progress_stats", {}):
                print("❌ Ya existe un progress_stat con ese nombre.")
                continue

            if nombre in sistema["recursos_definidos"]:
                print("Ese recurso ya existe.")
                continue

            descripcion = input("Descripción (opcional): ").strip()
            requiere_plugin = input("Requiere plugin (opcional): ").strip() or None

            destino = seleccionar_destino(requiere_plugin)
            modo = seleccionar_modo()

            sistema["recursos_definidos"][nombre] = {
                "descripcion": descripcion,
                "requiere_plugin": requiere_plugin,
                "destino": destino,
                "modo": modo
            }

            if destino == "recursos":
            
                # 🔥 Asegurar que recursos sea SIEMPRE dict
                if not isinstance(sistema.get("recursos"), dict):
                    sistema["recursos"] = {}
            
                if modo == "simple":
                    sistema["recursos"].setdefault(nombre, 0)
                else:
                    sistema["recursos"].setdefault(nombre, {})
            
            else:
            
                if modo == "simple":
                    if not isinstance(sistema.get(destino), int):
                        sistema[destino] = 0
                else:
                    if not isinstance(sistema.get(destino), dict):
                        sistema[destino] = {}

            registrar_recurso(nombre, descripcion, requiere_plugin, destino, modo)

            estado.cambios_no_guardados = True
            print("Recurso creado correctamente.")

        # ───────────────
        # EDITAR
        # ───────────────
        elif opcion == "3":
            nombre = input("Nombre del recurso a editar: ").strip()
            if nombre not in sistema["recursos_definidos"]:
                print("No existe ese recurso.")
                continue

            recurso_actual = sistema["recursos_definidos"][nombre]

            descripcion = input("Nueva descripción (vacío para mantener): ").strip()
            requiere_plugin = input("Nuevo plugin requerido (vacío para mantener): ").strip() or recurso_actual.get("requiere_plugin")
            destino = seleccionar_destino(requiere_plugin, recurso_actual.get("destino"))
            modo = seleccionar_modo(recurso_actual.get("modo", "contenedor"))

            if descripcion:
                recurso_actual["descripcion"] = descripcion

            recurso_actual["requiere_plugin"] = requiere_plugin
            recurso_actual["destino"] = destino
            recurso_actual["modo"] = modo

            registrar_recurso(
                nombre,
                recurso_actual.get("descripcion", ""),
                recurso_actual.get("requiere_plugin"),
                recurso_actual.get("destino", "recursos"),
                recurso_actual.get("modo", "contenedor")
            )

            estado.cambios_no_guardados = True
            print("Recurso actualizado.")

        # ───────────────
        # ELIMINAR
        # ───────────────
        elif opcion == "4":
            nombre = input("Nombre del recurso a eliminar: ").strip()
            if nombre not in sistema["recursos_definidos"]:
                print("No existe ese recurso.")
                continue

            confirm = input("¿Seguro? (s/n): ").lower()
            if confirm == "s":
                sistema["recursos_definidos"].pop(nombre)
                RECURSOS_REGISTRADOS.pop(nombre, None)
                estado.cambios_no_guardados = True
                print("Recurso eliminado.")

        elif opcion == "0":
            #guardar_sistema(print_msg=False)
            break
        else:
            print("Opción inválida.")

# ─────────────────────────────
# MENÚ MODIFICAR TIPOS BASE
# ─────────────────────────────
def menu_modificar_recursos_base(sistema=None):
    sistema = sistema or estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    while True:
        print("\n=== ACTIVAR/DESACTOVAR RECURSOS ===")
        for i, (tipo, plugin) in enumerate(TIPOS_RECOMPENSA.items(), start=1):
            estado_activo = "✅ Activo" if esta_tipo_base_activo(tipo) else "❌ Desactivado"
            plugin_str = plugin if plugin else "Sin plugin"
            print(f"{i}. {tipo} ({estado_activo}) - Plugin: {plugin_str}")

        print("\nOpciones:")
        print("A. Activar un tipo")
        print("D. Desactivar un tipo")
        print("0. Volver")

        opcion = input("Selecciona opción: ").strip().upper()

        if opcion == "A":
            tipo_sel = input("Nombre del tipo a activar: ").strip()
            if tipo_sel not in TIPOS_RECOMPENSA:
                print("❌ Tipo no válido.")
                continue
            activar_tipo_base(tipo_sel)
            print(f"✅ {tipo_sel} activado.")

        elif opcion == "D":
            tipo_sel = input("Nombre del tipo a desactivar: ").strip()
            if tipo_sel not in TIPOS_RECOMPENSA:
                print("❌ Tipo no válido.")
                continue
            desactivar_tipo_base(tipo_sel)
            print(f"❌ {tipo_sel} desactivado.")

        elif opcion == "0":
            # 🔹 Guardado automático de cambios en sistema
            guardar_sistema(print_msg=False)
            break
        else:
            print("Opción inválida.")


# ─────────────────────────────
# MENÚ MODIFICAR RAREZAS BASE
# ─────────────────────────────
def menu_modificar_rarezas_base(sistema=None):
    sistema = sistema or estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    while True:
        print("\n=== ACTIVAR/DESACTIVAR RAREZAS ===")

        for i, tipo in enumerate(TIPOS_RAREZAS, start=1):
            estado_activo = "✅ Activo" if esta_rareza_base_activa(tipo) else "❌ Desactivado"
            print(f"{i}. {tipo} ({estado_activo})")

        print("\nOpciones:")
        print("A. Activar rareza")
        print("D. Desactivar rareza")
        print("0. Volver")

        opcion = input("Selecciona opción: ").strip().upper()

        # ───────────────
        # ACTIVAR
        # ───────────────
        if opcion == "A":
            tipo = input("Nombre de la rareza a activar: ").strip()

            if tipo not in TIPOS_RAREZAS:
                print("❌ Rareza no válida.")
                continue

            activar_rareza_base(tipo)
            print(f"✅ {tipo} activada.")

        # ───────────────
        # DESACTIVAR
        # ───────────────
        elif opcion == "D":
            tipo = input("Nombre de la rareza a desactivar: ").strip()

            if tipo not in TIPOS_RAREZAS:
                print("❌ Rareza no válida.")
                continue

            desactivar_rareza_base(tipo)
            print(f"❌ {tipo} desactivada.")

        # ───────────────
        # SALIR
        # ───────────────
        elif opcion == "0":
            guardar_sistema(print_msg=False)
            break

        else:
            print("Opción inválida.")


# ─────────────────────────────
# MENÚ MODIFICAR RAREZAS DINAMICOS
# ─────────────────────────────
def menu_configurar_rarezas_dinamicas(sistema=None):
    sistema = sistema or estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    sistema.setdefault("rarezas_definidas", {})

    while True:
        print("\n=== CONFIGURACIÓN DE RAREZAS DINÁMICAS ===")
        print("1. Ver rarezas")
        print("2. Crear rareza")
        print("3. Editar rareza")
        print("4. Eliminar rareza")
        print("0. Volver")

        opcion = input("Selecciona opción: ").strip()

        # ───────────────
        # VER
        # ───────────────
        if opcion == "1":
            if not sistema["rarezas_definidas"]:
                print("No hay rarezas definidas.")
            else:
                for nombre, config in sistema["rarezas_definidas"].items():
                    print(f"\n• {nombre}")
                    print(f"  Descripción: {config.get('descripcion', '')}")
                    print(f"  Color: {config.get('color')}")
                    print(f"  Icono: {config.get('icono')}")
                    print(f"  Peso: {config.get('peso')}")
                    print(f"  Requiere plugin: {config.get('requiere_plugin')}")

        # ───────────────
        # CREAR
        # ───────────────
        elif opcion == "2":
            nombre = input("Nombre de la rareza: ").strip()

            if not nombre:
                print("Nombre inválido.")
                continue

            if nombre in TIPOS_RAREZAS:
                print("❌ Ya existe como rareza base.")
                continue

            if nombre in sistema["rarezas_definidas"]:
                print("Esa rareza ya existe.")
                continue

            descripcion = input("Descripción (opcional): ").strip()
            color = input("Color (hex, opcional): ").strip() or "#ffffff"
            icono = input("Icono (opcional): ").strip()

            try:
                peso = float(input("Peso (default 1.0): ") or 1.0)
            except ValueError:
                print("Peso inválido.")
                continue

            requiere_plugin = input("Requiere plugin (opcional): ").strip() or None

            sistema["rarezas_definidas"][nombre] = {
                "descripcion": descripcion,
                "color": color,
                "icono": icono,
                "peso": peso,
                "requiere_plugin": requiere_plugin
            }

            registrar_rareza(
                nombre,
                descripcion,
                color,
                icono,
                peso,
                requiere_plugin
            )

            estado.cambios_no_guardados = True
            print("Rareza creada correctamente.")

        # ───────────────
        # EDITAR
        # ───────────────
        elif opcion == "3":
            nombre = input("Nombre de la rareza a editar: ").strip()

            if nombre not in sistema["rarezas_definidas"]:
                print("No existe esa rareza.")
                continue

            rareza_actual = sistema["rarezas_definidas"][nombre]

            descripcion = input("Nueva descripción (vacío para mantener): ").strip()
            color = input("Nuevo color (vacío para mantener): ").strip()
            icono = input("Nuevo icono (vacío para mantener): ").strip()

            peso_input = input("Nuevo peso (vacío para mantener): ").strip()
            requiere_plugin = input("Nuevo plugin requerido (vacío para mantener): ").strip()

            if descripcion:
                rareza_actual["descripcion"] = descripcion

            if color:
                rareza_actual["color"] = color

            if icono:
                rareza_actual["icono"] = icono

            if peso_input:
                try:
                    rareza_actual["peso"] = float(peso_input)
                except ValueError:
                    print("Peso inválido.")
                    continue

            if requiere_plugin:
                rareza_actual["requiere_plugin"] = requiere_plugin

            # 🔥 Re-registrar en memoria
            registrar_rareza(
                nombre,
                rareza_actual.get("descripcion", ""),
                rareza_actual.get("color", "#ffffff"),
                rareza_actual.get("icono", ""),
                rareza_actual.get("peso", 1.0),
                rareza_actual.get("requiere_plugin")
            )

            estado.cambios_no_guardados = True
            print("Rareza actualizada.")

        # ───────────────
        # ELIMINAR
        # ───────────────
        elif opcion == "4":
            nombre = input("Nombre de la rareza a eliminar: ").strip()

            if nombre not in sistema["rarezas_definidas"]:
                print("No existe esa rareza.")
                continue

            confirm = input("¿Seguro? (s/n): ").lower()
            if confirm == "s":
                sistema["rarezas_definidas"].pop(nombre)
                RAREZAS_REGISTRADAS.pop(nombre, None)

                estado.cambios_no_guardados = True
                print("Rareza eliminada.")

        # ───────────────
        # SALIR
        # ───────────────
        elif opcion == "0":
            #guardar_sistema(print_msg=False)
            break

        else:
            print("Opción inválida.")