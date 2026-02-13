# plugins/misiones/helpers_rachas.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.recompensas.aplicar import aplicar_recompensas
from core.recompensas.tipos import obtener_tipos_recompensa_validos
from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
from core.utils.funciones_utiles import safe_float_input, safe_int_input, sync_plugin_cache
from core.recompensas.bloques import menu_editar_bloque_interactivo


# --------------------------------------------------
# Inicialización y cache
# --------------------------------------------------

def inicializar_rachas(sistema):
    """
    Asegura que la estructura de rachas exista y sincroniza cache.
    """
    sistema.setdefault("rachas", {}).setdefault("activas", {})
    sync_plugin_cache(sistema, "rachas", ["activas", "historial"])


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

    # Normalizar recompensas/penalizaciones
    def normalizar_bloque(bloque):
        bloque_final = {}
        for tipo, items in (bloque or {}).items():
            bloque_final[tipo] = {}
            for nombre, info in items.items():
                nueva_info = info.copy()
                # Convertir "valor" o "cantidad" a base
                if "valor" in nueva_info:
                    nueva_info["valor_base"] = nueva_info.pop("valor")
                if "cantidad" in nueva_info:
                    nueva_info["cantidad_base"] = nueva_info.pop("cantidad")
                # Asegurar factor y tope
                nueva_info.setdefault("factor_escalado", 1.0)
                if tipo != "objetos":
                    nueva_info.setdefault("tope", None)
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
    sync_plugin_cache(sistema, "rachas", ["activas", "historial"])

    guardar_sistema(print_msg=False)

    return True


# --------------------------------------------------
# Modificar racha
# --------------------------------------------------

"""def menu_editar_bloque_racha(racha, clave):
    
    Permite usar menu_editar_bloque de misiones con rachas.
    
    # Creamos temporalmente un objeto con el mismo formato que una misión
    temp = {clave: racha.setdefault(clave, {})}
    menu_editar_bloque(temp, clave)
    # Guardamos los cambios de vuelta en la racha
    racha[clave] = temp[clave]"""


def modificar_racha(sistema, racha_id):
    """
    Modifica una racha existente:
    - Nombre y descripción
    - Objetivos
    - Recompensas
    - Penalizaciones
    """
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
        for i, obj in enumerate(racha.get("objetivos", []), 1):
            objetivo_actual = obj["cantidad_base"] * (obj["factor_escalado"] ** obj.get("nivel", 0))
            print(f"{i}. {obj['descripcion']} {obj.get('progreso', 0)}/{int(objetivo_actual)} [FE: {obj['factor_escalado']}]")

        print("[A] Añadir   [E] Editar   [D] Eliminar   [Enter] Volver")
        opcion = input("> ").strip().lower()

        if opcion == "a":
            desc = input("Descripción objetivo: ").strip()
            cantidad_base = safe_int_input("Cantidad base del objetivo: ", default=1)
            factor = safe_float_input("Factor de escalado (1.0 = sin cambio): ", default=1.0)
            racha.setdefault("objetivos", []).append({
                "descripcion": desc,
                "cantidad_base": cantidad_base,
                "factor_escalado": factor,
                "nivel": 0,
                "progreso": 0
            })

        elif opcion == "e":
            if not racha.get("objetivos"):
                print("❌ No hay objetivos para editar.")
                continue
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
            if not racha.get("objetivos"):
                print("❌ No hay objetivos para eliminar.")
                continue
            idx = safe_int_input("Número de objetivo a eliminar: ", min_val=1, max_val=len(racha["objetivos"])) - 1
            del racha["objetivos"][idx]

        else:
            break

    # -----------------------
    # EDITAR RECOMPENSAS
    # -----------------------
    tipos_validos = obtener_tipos_recompensa_validos()
    menu_editar_bloque_interactivo(
        racha.setdefault("recompensas", {}),
        "recompensas",
        tipos_validos=tipos_validos
    )

    # -----------------------
    # EDITAR PENALIZACIONES
    # -----------------------
    menu_editar_bloque_interactivo(
        racha.setdefault("penalizaciones", {}),
        "penalizaciones",
        tipos_validos=tipos_validos
    )

    # -----------------------
    # SINCRONIZAR Y GUARDAR
    # -----------------------
    sync_plugin_cache(sistema, "rachas", ["activas", "historial"])
    estado.cambios_no_guardados = True
    guardar_sistema(print_msg=False)
    print("✅ Racha modificada correctamente.")
    return True



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

            base = info.get("valor_base")
            if base is None:
                continue


            # Obtener tipo de escalado desde la configuración del sistema
            tipo_escalado = sistema.get("configuracion", {}).get("racha_tipo_escalado", "exponencial")
            factor = info.get("factor_escalado", 1.0)

            # Calcular nuevo valor según el tipo de escalado
            if tipo_escalado == "exponencial":
                nuevo_valor = int(base * (factor ** (multiplicador - 1)))

            elif tipo_escalado == "lineal":
                nuevo_valor = int(base + (factor - 1) * base * (multiplicador - 1))

            elif tipo_escalado == "lineal_tope":
                tope = info.get("tope", None)  # Opcional, permitir que cada racha tenga un máximo
                val = int(base + (factor - 1) * base * (multiplicador - 1))
                nuevo_valor = min(val, tope) if tope is not None else val

            elif tipo_escalado == "lineal_porcentaje":
                nuevo_valor = int(base * (1 + (factor - 1) * (multiplicador - 1)))

            elif tipo_escalado == "lineal_suavizado":
                incremento = (factor - 1) * base
                nuevo_valor = int(base + incremento * (1 - 0.5**(multiplicador - 1)))  # suavizado exponencial
            
            # 🔹 Aquí estaba la línea que faltaba:
            
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
    sync_plugin_cache(sistema, "rachas", ["activas", "historial"])

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
            tope = obj.get("tope", None)
            tope_str = f" | Tope: {tope}" if tope is not None else ""
            print(f"  {i}. {obj['descripcion']} {obj['progreso']}/{int(objetivo_actual)} [FE: {obj['factor_escalado']}{tope_str}]")

        # ----------------------------
        # Recompensas
        # ----------------------------
        print("Recompensa actual (escalada):")
        veces = racha.get("veces_completada", 0)
        tipo_escalado = sistema.get("configuracion", {}).get("racha_tipo_escalado", "exponencial")

        for t, items in racha.get("recompensas", {}).items():
            for k, v in items.items():
                base = v.get("valor_base", 0)
                factor = v.get("factor_escalado", 1.0)
                tope = v.get("tope", None)

                if tipo_escalado == "exponencial":
                    recompensa_actual = int(base * (factor ** veces))
                elif tipo_escalado == "lineal":
                    recompensa_actual = int(base + (factor - 1) * base * veces)
                elif tipo_escalado == "lineal_tope":
                    val = int(base + (factor - 1) * base * veces)
                    recompensa_actual = min(val, tope) if tope is not None else val
                elif tipo_escalado == "lineal_porcentaje":
                    recompensa_actual = int(base * (1 + (factor - 1) * veces))
                elif tipo_escalado == "lineal_suavizado":
                    incremento = (factor - 1) * base
                    recompensa_actual = int(base + incremento * (1 - 0.5 ** veces))

                tope_str = f" | Tope: {tope}" if tope is not None else ""
                print(f"  {k} ({t}): {recompensa_actual}  [Base: {base} | Factor: {factor}{tope_str}]")

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
                base = v.get("valor_base", 0)
                factor = v.get("factor_escalado", 1.0)
                tope = v.get("tope", None)

                # Aplicar mismo tipo de escalado que recompensas para mostrar correctamente
                if tipo_escalado == "exponencial":
                    penal_actual = int(base * (factor ** fallos))
                elif tipo_escalado == "lineal":
                    penal_actual = int(base + (factor - 1) * base * fallos)
                elif tipo_escalado == "lineal_tope":
                    val = int(base + (factor - 1) * base * fallos)
                    penal_actual = min(val, tope) if tope is not None else val
                elif tipo_escalado == "lineal_porcentaje":
                    penal_actual = int(base * (1 + (factor - 1) * fallos))
                elif tipo_escalado == "lineal_suavizado":
                    incremento = (factor - 1) * base
                    penal_actual = int(base + incremento * (1 - 0.5 ** fallos))

                tope_str = f" | Tope: {tope}" if tope is not None else ""
                print(f"  {k} ({t}): {penal_actual} [Base: {base} | Factor: {factor}{tope_str}]")


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

