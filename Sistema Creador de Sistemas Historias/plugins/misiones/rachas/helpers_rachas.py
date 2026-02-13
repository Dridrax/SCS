# plugins/misiones/helpers_rachas.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.recompensas.aplicar import aplicar_recompensas
from core.recompensas.tipos import obtener_tipos_recompensa_validos, cargar_recursos_desde_sistema
from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
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
    
    menu_editar_bloque_interactivo(racha.setdefault("recompensas", {}), "recompensas")

    # -----------------------
    # EDITAR PENALIZACIONES
    # -----------------------
    
    menu_editar_bloque_interactivo(racha.setdefault("penalizaciones", {}), "penalizaciones")

    estado.cambios_no_guardados = True
    guardar_sistema(print_msg=False)
    print("✅ Racha modificada correctamente.")
    return True



def menu_editar_bloque_interactivo(bloque, nombre_bloque):
    """
    Editor dinámico de recompensas/penalizaciones para SCS.
    Soporta todos los tipos base + recursos dinámicos.
    """
    
    while True:
        print(f"\n--- {nombre_bloque.upper()} ---")

        # Mostrar contenido actual
        if bloque:
            for tipo, items in bloque.items():
                print(f" {tipo}:")
                for nombre, info in items.items():
                    base = info.get("valor_base", info.get("valor",
                           info.get("cantidad_base", info.get("cantidad", 0))))
                    factor = info.get("factor_escalado", 1.0)
                    print(f"   {nombre}: {base} [Factor: {factor}]")

        print("\n1. Agregar")
        print("2. Editar")
        print("3. Eliminar")
        print("4. Volver")

        opcion = safe_int_input("Opción: ", default=4)

        # --------------------------------------------------
        # AGREGAR
        # --------------------------------------------------
        if opcion == 1:
            if sistema_actual := estado.sistema_actual:
                cargar_recursos_desde_sistema(estado.sistema_actual)  # actualiza RECURSOS_REGISTRADOS
            tipos_validos = obtener_tipos_recompensa_validos()
            print("\nTipos disponibles:")
            for t in tipos_validos:
                print(f" - {t}")

            tipo = input("Tipo: ").strip()
            if tipo not in tipos_validos:
                print("❌ Tipo inválido.")
                continue

            nombre = input("Nombre del recurso/stat/objeto: ").strip()
            base = safe_int_input("Valor / Cantidad base: ", default=0)
            factor = safe_float_input("Factor de escalado (1.0 = fijo): ", default=1.0)

            # AGREGAR ELEMENTO CORRECTAMENTE
            tope = None
            if tipo != "objetos":
                tope = safe_int_input("Tope máximo (solo lineal_tope, Enter = sin tope): ", default=None)

            item = {}
            if tipo == "objetos":
                item["cantidad"] = base
            else:
                item["valor_base"] = base
                item["tope"] = tope

            item["factor_escalado"] = factor

            bloque.setdefault(tipo, {})[nombre] = item



            print("✅ Agregado correctamente.")

        # --------------------------------------------------
        # EDITAR
        # --------------------------------------------------
        elif opcion == 2:
            tipo = input("Tipo a editar: ").strip()
            nombre = input("Nombre a editar: ").strip()

            if tipo not in bloque or nombre not in bloque[tipo]:
                print("❌ No encontrado.")
                continue

            item = bloque[tipo][nombre]

            base_actual = item.get("valor_base", item.get("cantidad", 0))
            factor_actual = item.get("factor_escalado", 1.0)

            nuevo_base = safe_int_input(f"Valor / Cantidad ({base_actual}): ", default=base_actual)
            nuevo_factor = safe_float_input(f"Factor ({factor_actual}): ", default=factor_actual)

            if tipo == "objetos":
                item["cantidad"] = nuevo_base
            else:
                item["valor_base"] = nuevo_base

            item["factor_escalado"] = nuevo_factor

            if tipo != "objetos":
                tope_actual = item.get("tope", None)
                nuevo_tope = safe_int_input(f"Tope máximo ({tope_actual}): ", default=tope_actual)
                item["tope"] = nuevo_tope


            print("✅ Editado correctamente.")

        # --------------------------------------------------
        # ELIMINAR
        # --------------------------------------------------
        elif opcion == 3:
            tipo = input("Tipo: ").strip()
            nombre = input("Nombre: ").strip()

            if tipo in bloque and nombre in bloque[tipo]:
                del bloque[tipo][nombre]
                print("✅ Eliminado.")
            else:
                print("❌ No encontrado.")

        elif opcion == 4:
            break

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
    Menú interactivo para configurar rachas:
    1 Reinicio de penalizaciones
    2 Tipo de escalado de recompensas (con ejemplos)
    """
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    sistema.setdefault("configuracion", {})
    config = sistema["configuracion"]

    while True:
        print("\n=== CONFIGURACIÓN DE RACHAS ===")
        print("1 Cambiar número de rachas completadas para reiniciar penalizaciones")
        print("2 Cambiar tipo de escalado de recompensas")
        print("0 Salir del menú")

        opcion = safe_int_input("Selecciona opción: ", min_val=0, max_val=2)

        if opcion == 0:
            break

        elif opcion == 1:
            valor_actual = config.get("racha_recuperacion_fallos", 3)
            print(f"\nNúmero actual: {valor_actual}")
            nuevo_valor = safe_int_input("Nuevo valor (Enter = mantener actual): ", min_val=1, default=valor_actual)
            config["racha_recuperacion_fallos"] = nuevo_valor
            print(f"✅ Reinicio de penalizaciones tras {nuevo_valor} rachas completadas.")

        elif opcion == 2:
            print("\nTipos de escalado disponibles:")
            print("1. Exponencial (valor_base * factor^n)")
            print("2. Lineal (valor_base + (factor-1)*valor_base * n)")
            print("3. Lineal + Tope (igual que lineal, pero con límite máximo)")
            print("4. Lineal por porcentaje (valor_base * (1 + (factor-1)*n))")
            print("5. Lineal suavizado (valor_base + incremento suavizado * n)")

            ejemplos = {}
            valor_base = 100
            factor = 1.5
            for tipo, nombre in enumerate(["exponencial", "lineal", "lineal_tope", "lineal_porcentaje", "lineal_suavizado"], start=1):
                valores = []
                for n in range(5):
                    if nombre == "exponencial":
                        valores.append(int(valor_base * (factor ** n)))
                    elif nombre == "lineal":
                        valores.append(int(valor_base + (factor-1)*valor_base * n))
                    elif nombre == "lineal_tope":
                        tope = 300
                        val = int(valor_base + (factor-1)*valor_base * n)
                        valores.append(min(val, tope))
                    elif nombre == "lineal_porcentaje":
                        valores.append(int(valor_base * (1 + (factor-1) * n)))
                    elif nombre == "lineal_suavizado":
                        incremento = (factor-1)*valor_base
                        valores.append(int(valor_base + incremento * (1 - 0.5**n)))
                ejemplos[nombre] = valores

            for k, v in ejemplos.items():
                print(f"{k}: {v}")

            opciones_map = {1: "exponencial", 2: "lineal", 3: "lineal_tope", 4: "lineal_porcentaje", 5: "lineal_suavizado"}
            tipo_actual = config.get("racha_tipo_escalado", "exponencial")
            print(f"\nTipo actual: {tipo_actual}")
            seleccion = safe_int_input("Selecciona opción (Enter = mantener actual): ", default=1, min_val=1, max_val=5)
            config["racha_tipo_escalado"] = opciones_map.get(seleccion, tipo_actual)
            print(f"✅ Tipo de escalado actualizado a: {config['racha_tipo_escalado']}")

        estado.cambios_no_guardados = True
        guardar_sistema(print_msg=False)

    print("🔹 Saliste del menú de configuración de rachas.")


