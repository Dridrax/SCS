# plugins/misiones/helpers_rachas.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.recompensas.aplicar import aplicar_recompensas
from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
from plugins.misiones.helpers_misiones import agregar_recompensa, editar_recompensa, eliminar_recompensa
from plugins.misiones.menus_misiones import menu_editar_bloque

# --------------------------------------------------
# Inicialización y cache
# --------------------------------------------------

def inicializar_rachas(sistema):
    """
    Asegura que la estructura de rachas exista y sincroniza cache.
    """
    sistema.setdefault("rachas", {}).setdefault("activas", {})
    sync_rachas_plugin_cache(sistema)

def sync_rachas_plugin_cache(sistema):
    """
    Sincroniza las rachas activas en el plugin cache.
    No borra otros posibles datos del plugin.
    """
    estado.plugin_cache.setdefault("plugins", {})
    estado.plugin_cache["plugins"].setdefault("rachas", {})
    estado.plugin_cache["plugins"]["rachas"]["activas"] = sistema.get("rachas", {}).get("activas", {})

# --------------------------------------------------
# Crear racha
# --------------------------------------------------

def crear_racha(
    sistema,
    *,
    id,
    nombre,
    descripcion="",
    objetivos=None,
    recompensas=None,
    penalizaciones=None
):
    inicializar_rachas(sistema)
    activas = sistema["rachas"]["activas"]

    if id in activas:
        return False

    # Asegurar estructura base fija en recompensas
    def normalizar_bloque(bloque):
        bloque_final = {}

        for tipo, items in (bloque or {}).items():
            bloque_final[tipo] = {}

            for nombre, info in items.items():
                nueva_info = info.copy()

                # Convertir "valor" → "valor_base"
                if "valor" in nueva_info:
                    nueva_info["valor_base"] = nueva_info.pop("valor")

                if "cantidad" in nueva_info:
                    nueva_info["cantidad_base"] = nueva_info.pop("cantidad")

                bloque_final[tipo][nombre] = nueva_info

        return bloque_final

    activas[id] = {
        "id": id,
        "nombre": nombre,
        "descripcion": descripcion,
        "objetivos": objetivos or [],
        "recompensas": normalizar_bloque(recompensas),
        "penalizaciones": normalizar_bloque(penalizaciones),
        "veces_completada": 0,
        "fallos_consecutivos": 0
    }

    estado.cambios_no_guardados = True
    sync_rachas_plugin_cache(sistema)
    guardar_sistema(print_msg=False)

    return True


# --------------------------------------------------
# Modificar racha
# --------------------------------------------------

def menu_editar_bloque_racha(racha, clave):
    """
    Permite usar menu_editar_bloque de misiones con rachas.
    """
    # Creamos temporalmente un objeto con el mismo formato que una misión
    temp = {clave: racha.setdefault(clave, {})}
    menu_editar_bloque(temp, clave)
    # Guardamos los cambios de vuelta en la racha
    racha[clave] = temp[clave]


def modificar_racha(sistema, racha_id):
    inicializar_rachas(sistema)
    racha = sistema["rachas"]["activas"].get(racha_id)
    if not racha:
        print("❌ No existe esa racha.")
        return False

    # -----------------------
    # EDITAR DATOS BÁSICOS
    # -----------------------
    nombre = input(f"Nombre ({racha['nombre']}): ").strip() or racha['nombre']
    descripcion = input(f"Descripción ({racha['descripcion']}): ").strip() or racha['descripcion']
    racha['nombre'] = nombre
    racha['descripcion'] = descripcion

    # -----------------------
    # EDITAR OBJETIVOS
    # -----------------------
    while True:
        print("\n--- OBJETIVOS ---")
        for i, obj in enumerate(racha["objetivos"], 1):
            objetivo_actual = obj["cantidad_base"] * (obj["factor_escalado"] ** obj["nivel"])
            print(f"{i}. {obj['descripcion']} {obj['progreso']}/{int(objetivo_actual)} [FE: {obj['factor_escalado']}]")

        print("[A] Añadir   [E] Editar   [D] Eliminar   [Enter] Volver")

        opcion = input("> ").strip().lower()

        if opcion == "a":
            desc = input("Descripción objetivo: ").strip()
            cantidad_base = safe_int_input("Cantidad base del objetivo: ", default=1)
            factor = safe_float_input("Factor de escalado (1.0 = sin cambio): ", default=1.0)
            racha["objetivos"].append({
                "descripcion": desc,
                "cantidad_base": cantidad_base,
                "factor_escalado": factor,
                "nivel": 0,
                "progreso": 0
            })

        elif opcion == "e":
            idx = safe_int_input("Número de objetivo a editar: ", min_val=1, max_val=len(racha["objetivos"])) - 1
            obj = racha["objetivos"][idx]
            desc = input(f"Descripción ({obj['descripcion']}): ").strip() or obj['descripcion']
            cantidad_base = safe_int_input(f"Cantidad base ({obj['cantidad_base']}): ", default=obj['cantidad_base'])
            factor = safe_float_input(f"Factor de escalado ({obj['factor_escalado']}): ", default=obj['factor_escalado'])
            obj.update({
                "descripcion": desc,
                "cantidad_base": cantidad_base,
                "factor_escalado": factor
            })

        elif opcion == "d":
            idx = safe_int_input("Número de objetivo a eliminar: ", min_val=1, max_val=len(racha["objetivos"])) - 1
            del racha["objetivos"][idx]

        else:
            break

    # -----------------------
    # EDITAR RECOMPENSAS / PENALIZACIONES
    # -----------------------
    while True:
        print("\n--- RECOMPENSAS / PENALIZACIONES ---")
        print("1. Editar recompensas")
        print("2. Editar penalizaciones")
        print("3. Salir")
        opcion = input("> ").strip()
        if opcion == "1":
            menu_editar_bloque_interactivo(racha.setdefault("recompensas", {}), "recompensas")
        elif opcion == "2":
            menu_editar_bloque_interactivo(racha.setdefault("penalizaciones", {}), "penalizaciones")
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida.")

        estado.cambios_no_guardados = True
        guardar_sistema()
        return True

    # -----------------------
    # EDITAR RECOMPENSAS / PENALIZACIONES
    # -----------------------
    while True:
        print("\n--- RECOMPENSAS / PENALIZACIONES ---")
        print("1. Editar recompensas")
        print("2. Editar penalizaciones")
        print("3. Salir")
        opcion = input("> ").strip()
        if opcion == "1":
            menu_editar_bloque_interactivo(racha.setdefault("recompensas", {}), "recompensas")
        elif opcion == "2":
            menu_editar_bloque_interactivo(racha.setdefault("penalizaciones", {}), "penalizaciones")
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida.")

        estado.cambios_no_guardados = True
        guardar_sistema()
        return True


def menu_editar_bloque_interactivo(bloque, nombre_bloque):
    """
    Permite agregar, editar y eliminar recompensas/penalizaciones.
    Cada ítem se guarda como {nombre: {"valor"/"cantidad": x, "factor_escalado": y}}.
    """
    while True:
        print(f"\n--- {nombre_bloque.upper()} ---")
        if bloque:
            print("Contenido actual:")
            for t, items in bloque.items():
                print(f" {t}:")
                for k, v in (items.items() if isinstance(items, dict) else enumerate(items)):
                    if isinstance(v, dict):
                        val = v.get("valor", v.get("cantidad", 0))
                        factor = v.get("factor_escalado", 1.0)
                        print(f"   {k}: {val} [Factor: {factor}]")
                    else:
                        print(f"   {k}: {v}")
        print("1. Agregar")
        print("2. Editar")
        print("3. Eliminar")
        print("4. Volver")
        opcion = safe_int_input("Opción: ", default=4)

        if opcion == 1:
            tipo = input("Tipo (objetos/stats/dinero/progress_stats/puntos_stats/nivel/tiradas): ").strip()
            nombre = input("Nombre: ").strip()
            factor = safe_float_input("Factor de escalado (1.0 = sin cambio): ", default=1.0)

            if tipo == "objetos":
                cantidad = safe_int_input("Cantidad: ", default=1)
                rareza = input("Rareza: ").strip()
                tipo_obj = input("Tipo: ").strip()
                bloque.setdefault(tipo, {})[nombre] = {
                    "cantidad": cantidad,
                    "rareza": rareza,
                    "tipo": tipo_obj,
                    "factor_escalado": factor
                }
            else:
                valor = safe_int_input("Valor: ", default=0)
                bloque.setdefault(tipo, {})[nombre] = {
                    "valor": valor,
                    "factor_escalado": factor
                }
            print("✅ Agregado.")

        elif opcion == 2:
            tipo = input("Tipo a editar: ").strip()
            clave_dato = input("Nombre del ítem a editar: ").strip()
            if tipo not in bloque or clave_dato not in bloque[tipo]:
                print("❌ Ítem no encontrado.")
                continue

            item = bloque[tipo][clave_dato]
            if "valor" in item:
                nuevo_valor = safe_int_input(f"Valor ({item['valor']}): ", default=item['valor'])
                item["valor"] = nuevo_valor
            elif "cantidad" in item:
                nueva_cantidad = safe_int_input(f"Cantidad ({item['cantidad']}): ", default=item['cantidad'])
                item["cantidad"] = nueva_cantidad

            nuevo_factor = safe_float_input(f"Factor de escalado ({item.get('factor_escalado', 1.0)}): ", default=item.get('factor_escalado', 1.0))
            item["factor_escalado"] = nuevo_factor
            print("✅ Editado.")

        elif opcion == 3:
            tipo = input("Tipo a eliminar: ").strip()
            clave_dato = input("Nombre del ítem a eliminar: ").strip()
            if tipo in bloque and clave_dato in bloque[tipo]:
                del bloque[tipo][clave_dato]
                print("✅ Eliminado.")
            else:
                print("❌ Ítem no encontrado.")

        elif opcion == 4:
            break
        else:
            print("❌ Opción inválida.")


# --------------------------------------------------
# PROCESAR RACHA (OPCIÓN A - BASE FIJA)
# --------------------------------------------------

def procesar_racha(sistema, racha_id, clave="recompensas", forzar=False):
    inicializar_rachas(sistema)

    racha = sistema["rachas"]["activas"].get(racha_id)
    if not racha:
        return False

    # ----------------------
    # Verificación (solo recompensas)
    # ----------------------
    if clave == "recompensas" and not forzar:
        objetivos = racha.get("objetivos", [])
        todos_completos = all(
            obj.get("progreso", 0) >=
            obj.get("cantidad_base", 1) *
            (obj.get("factor_escalado", 1.0) ** obj.get("nivel", 0))
            for obj in objetivos
        )
        if not todos_completos:
            return None

    datos = racha.get(clave, {})
    if not datos:
        return False

    entregado = {}

    # 🔹 Escalado correcto
    if clave == "recompensas":
        multiplicador = racha.get("veces_completada", 0) + 1
    else:
        multiplicador = racha.get("fallos_consecutivos", 0) + 1

    for tipo, items in datos.items():
        if not isinstance(items, dict):
            continue

        entregado[tipo] = {}

        for nombre, info in items.items():
            if not isinstance(info, dict):
                continue

            campo = "valor" if "valor" in info else "cantidad" if "cantidad" in info else None
            if not campo:
                continue

            base = info[campo]
            factor = info.get("factor_escalado", 1.0)

            # 🔥 CALCULO LIMPIO (NO modifica base)
            nuevo_valor = int(base * (factor ** (multiplicador - 1)))

            entregado[tipo][nombre] = nuevo_valor

    # Limpiar tipos vacíos
    entregado = {k: v for k, v in entregado.items() if v}

    if entregado:
        aplicar_recompensas(
            sistema,
            preparar_recompensa_para_aplicar(sistema, entregado)
        )

    # ----------------------
    # Actualizar contadores
    # ----------------------
    if clave == "recompensas":
        racha["veces_completada"] = racha.get("veces_completada", 0) + 1
        racha["fallos_consecutivos"] = 0

    elif clave == "penalizaciones":
        racha["fallos_consecutivos"] = racha.get("fallos_consecutivos", 0) + 1
        racha["veces_completada"] = 0

        # Reiniciar progresión completa
        for obj in racha.get("objetivos", []):
            obj["nivel"] = 0
            obj["progreso"] = 0

    estado.cambios_no_guardados = True
    guardar_sistema(print_msg=False)

    return entregado



# --------------------------------------------------
# COMPLETAR RACHA
# --------------------------------------------------

def completar_racha(sistema, racha_id, forzar=False):
    inicializar_rachas(sistema)

    racha = sistema["rachas"]["activas"].get(racha_id)
    if not racha:
        return False

    # ----------------------
    # FORZADO
    # ----------------------
    if forzar:
        for obj in racha.get("objetivos", []):
            obj["progreso"] = 0
            obj["nivel"] = obj.get("nivel", 0) + 1

        return procesar_racha(sistema, racha_id, "recompensas", forzar=True)

    # ----------------------
    # PROGRESO NORMAL
    # ----------------------
    todos_completados = True

    for obj in racha.get("objetivos", []):
        objetivo_actual = obj["cantidad_base"] * (
            obj["factor_escalado"] ** obj.get("nivel", 0)
        )
        progreso_actual = obj.get("progreso", 0)

        print(f"\nObjetivo: {obj['descripcion']} {progreso_actual}/{int(objetivo_actual)}")

        cantidad = safe_int_input(
            f"Ingrese avance desde {progreso_actual}: ", default=0
        )
        cantidad = max(0, cantidad)

        completado = marcar_progreso_objetivo(obj, cantidad)
        if not completado:
            todos_completados = False

    estado.cambios_no_guardados = True
    guardar_sistema(print_msg=False)

    if todos_completados:
        return procesar_racha(sistema, racha_id, "recompensas", forzar=True)

    return None


# --------------------------------------------------
# FALLAR RACHA
# --------------------------------------------------

def fallar_racha(sistema, racha_id):
    """
    Falla una racha.
    - Aplica penalizaciones.
    - Reinicia completamente la progresión (lo hace procesar_racha).
    """

    inicializar_rachas(sistema)

    racha = sistema["rachas"]["activas"].get(racha_id)
    if not racha:
        print("❌ Racha no encontrada.")
        return False

    penalizaciones = procesar_racha(sistema, racha_id, "penalizaciones")

    print("\n❌ Racha fallada. Penalizaciones aplicadas:")
    print(penalizaciones)
    print("🔄 La racha ha sido reiniciada a su estado base.")

    return penalizaciones







# --------------------------------------------------
# Eliminar racha
# --------------------------------------------------

def eliminar_racha(sistema, racha_id):
    inicializar_rachas(sistema)
    activas = sistema["rachas"]["activas"]
    if racha_id not in activas:
        print("❌ No existe esa racha.")
        return False

    confirmar = input(f"¿Seguro que quieres eliminar la racha '{activas[racha_id]['nombre']}'? (s/n): ").strip().lower()
    if confirmar != "s":
        print("❌ Eliminación cancelada.")
        return False

    del activas[racha_id]
    sync_rachas_plugin_cache(sistema)
    estado.cambios_no_guardados = True
    guardar_sistema()
    print("✅ Racha eliminada.")
    return True

# --------------------------------------------------
# Gestion racha
# --------------------------------------------------

def gestion_racha(sistema, racha, rachas_list):
    """
    Menu interno para administrar una racha:
    - Completar por progreso
    - Forzar completado
    - Fallar (penalizaciones escaladas)
    - Eliminar
    - Muestra número de fallos consecutivos y cuánto falta para reinicio
    """
    while True:
        print(f"\n--- DETALLES DE {racha['nombre']} ---")
        print(f"ID: {racha['id']}")
        print(f"Descripción: {racha['descripcion']}")

        # ----------------------------
        # Objetivos
        # ----------------------------
        print("\nObjetivos:")
        for i, obj in enumerate(racha.get("objetivos", []), 1):
            objetivo_actual = obj["cantidad_base"] * (obj["factor_escalado"] ** obj["nivel"])
            print(f"  {i}. {obj['descripcion']} {obj['progreso']}/{int(objetivo_actual)} [FE: {obj['factor_escalado']}]")

        # ----------------------------
        # Recompensas
        # ----------------------------
        print(f"\nVeces completada: {racha.get('veces_completada',0)}")
        print("Recompensas base:")
        for t, items in racha.get("recompensas", {}).items():
            for k, v in items.items():
                val = v.get("valor", v.get("cantidad", 0))
                factor = v.get("factor_escalado", 1.0)
                print(f"  {k} ({t}): {val} [Factor: {factor}]")

        # ----------------------------
        # Penalizaciones
        # ----------------------------
        fallos = racha.get("fallos_consecutivos", 0)
        max_fallos = sistema.get("configuracion", {}).get("racha_recuperacion_fallos", 3)
        faltan_para_reiniciar = max_fallos - fallos if max_fallos > fallos else 0

        print(f"\nFallos consecutivos: {fallos} (Faltan {faltan_para_reiniciar} rachas completadas para reinicio)")
        print("Penalizaciones actuales:")
        for t, items in racha.get("penalizaciones", {}).items():
            for k, v in items.items():
                base = v.get("valor", v.get("cantidad", 0))
                factor = v.get("factor_escalado", 1.0)
                # Penalización escalada
                penal_actual = int(base * (factor ** fallos)) if factor != 1.0 else base
                print(f"  {k} ({t}): {penal_actual} [Factor: {factor}]")

        # ----------------------------
        # Menú de acciones
        # ----------------------------
        print("\n[P] Completar por progreso   [F] Forzar completado   [E] Fallar   [D] Eliminar   [Enter] Volver")
        accion = input("> ").strip().lower()

        if accion == "p":
            recompensas = completar_racha(sistema, racha["id"], forzar=False)
            if recompensas:
                print("\n✅ Racha completada. Recompensas entregadas:")
                print(recompensas)
            else:
                print("\n⚠ Racha no completada. Algunos objetivos aún no alcanzaron su meta.")
            break

        elif accion == "f":
            recompensas = completar_racha(sistema, racha["id"], forzar=True)
            print("\n✅ Racha completada forzadamente. Recompensas entregadas:")
            print(recompensas)
            break

        elif accion == "e":
            penalizaciones = fallar_racha(sistema, racha["id"])
            print("\n❌ Racha fallada. Penalizaciones aplicadas:")
            print(penalizaciones)
            break

        elif accion == "d":
            confirmar = input("Confirmar eliminación (s/n): ").lower()
            if confirmar == "s":
                eliminar_racha(sistema, racha["id"])
                rachas_list.remove(racha)
                print("✅ Racha eliminada.")
                break

        else:
            break




# --------------------------------------------------
# Funciones de ayuda para inputs seguros
# --------------------------------------------------

def safe_int_input(prompt, min_val=None, max_val=None, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            val = int(val)
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"❌ Debe estar entre {min_val} y {max_val}.")
                continue
            return val
        except ValueError:
            print("❌ Entrada no válida. Debe ser un número entero.")

def safe_float_input(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            return float(val)
        except ValueError:
            print("❌ Entrada no válida. Debe ser un número.")




# --------------------------------------------------
# Seleccionar racha
# --------------------------------------------------

def seleccionar_racha(sistema, accion="modificar"):
    """
    Permite seleccionar una racha por número o nombre.
    Retorna la racha (dict) o None si se cancela.
    """
    inicializar_rachas(sistema)
    rachas = list(sistema.get("rachas", {}).get("activas", {}).values())
    if not rachas:
        print(f"❌ No hay rachas para {accion}.")
        return None

    print(f"\n=== RACHA A {accion.upper()} ===")
    for i, r in enumerate(rachas, 1):
        print(f"{i}. {r['nombre']}")

    seleccion = input("Elige racha por número o nombre (Enter para cancelar): ").strip()
    if not seleccion:
        return None

    # Buscar por índice
    if seleccion.isdigit():
        idx = int(seleccion) - 1
        if 0 <= idx < len(rachas):
            return rachas[idx]
    else:
        for r in rachas:
            if r["nombre"].lower() == seleccion.lower():
                return r

    print("❌ Racha no encontrada.")
    return None


def marcar_progreso_objetivo(objetivo, cantidad):
    """
    Incrementa progreso de un objetivo y marca nivel si se cumple.
    Retorna True si objetivo completado en este paso.
    Mantiene exceso de progreso acumulado para siguiente nivel.
    """
    objetivo["progreso"] += cantidad
    objetivo_actual = objetivo["cantidad_base"] * (objetivo["factor_escalado"] ** objetivo.get("nivel", 0))

    completado = False
    while objetivo["progreso"] >= objetivo_actual:
        objetivo["progreso"] -= objetivo_actual
        objetivo["nivel"] += 1
        objetivo_actual = objetivo["cantidad_base"] * (objetivo["factor_escalado"] ** objetivo["nivel"])
        completado = True

    return completado



def configurar_rachas(sistema):
    """
    Permite al administrador configurar parámetros generales de las rachas:
    - Número de rachas completadas consecutivas necesarias para reiniciar penalizaciones.
    """
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    # Asegurar que la sección de configuración exista
    sistema.setdefault("configuracion", {})
    config = sistema["configuracion"]

    print("\n=== CONFIGURACIÓN DE RACHAS ===")

    # Valor actual
    valor_actual = config.get("racha_recuperacion_fallos", 3)
    print(f"Número de rachas completadas consecutivas para reiniciar penalizaciones (actual: {valor_actual}): ")

    nuevo_valor = safe_int_input("Ingresa nuevo valor (Enter = mantener actual): ", min_val=1, default=valor_actual)
    config["racha_recuperacion_fallos"] = nuevo_valor

    print(f"✅ Configuración actualizada: reinicio de penalizaciones tras {nuevo_valor} rachas completadas consecutivas.")

    estado.cambios_no_guardados = True
    guardar_sistema()
