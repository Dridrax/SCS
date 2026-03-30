# plugins/misiones/helpers_rachas.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.recompensas.aplicar import aplicar_recompensas
from core.recompensas.tipos import obtener_tipos_recompensa_validos
from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
from core.utils.funciones_utiles import safe_float_input, safe_int_input, sync_plugin_cache
from core.recompensas.bloques import menu_editar_bloque_interactivo
from core.recompensas.validacion import (
    validar_recompensas_entidad,
    manejar_conflictos,
    filtrar_recompensas_validas_entidad
)

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

    # ----------------------------
    # Normalizar recompensas/penalizaciones
    # ----------------------------
    def normalizar_bloque(bloque):
        bloque_final = {}

        for tipo, items in (bloque or {}).items():

            # 🔹 CASO OBJETOS → LISTA SIMPLE (SIN ESCALADO)
            if tipo == "objetos":
                bloque_final[tipo] = []

                for obj in items or []:
                    nuevo_obj = obj.copy()

                    # Convertir cantidad a cantidad_base si existe
                    if "cantidad" in nuevo_obj:
                        nuevo_obj["cantidad_base"] = nuevo_obj.pop("cantidad")

                    # Eliminar cosas que NO queremos en rachas
                    nuevo_obj.pop("factor_escalado", None)
                    nuevo_obj.pop("tope", None)

                    bloque_final[tipo].append(nuevo_obj)

                continue

            # 🔹 RESTO DE TIPOS → dict normal
            bloque_final[tipo] = {}

            for nombre, info in (items or {}).items():
                nueva_info = info.copy()

                # Convertir valor/cantidad a base
                if "valor" in nueva_info:
                    nueva_info["valor_base"] = nueva_info.pop("valor")

                if "cantidad" in nueva_info:
                    nueva_info["cantidad_base"] = nueva_info.pop("cantidad")

                # En rachas NO forzamos escalado
                nueva_info.setdefault("factor_escalado", 1.0)
                nueva_info.setdefault("tope", None)

                bloque_final[tipo][nombre] = nueva_info

        return bloque_final

    # ----------------------------
    # Crear racha
    # ----------------------------
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
# Calcular escalado
# --------------------------------------------------
def calcular_escalado(base, factor, nivel, modo="exponencial", tope=None):
    """
    Calcula un valor escalado según el tipo configurado.

    Args:
        base (float/int): Valor base.
        factor (float): Factor de escalado.
        nivel (int): Número de veces completadas / nivel actual (empezando desde 0).
        modo (str): Tipo de escalado: "exponencial", "lineal", "lineal_tope", 
                    "lineal_porcentaje", "lineal_suavizado".
        tope (float/int, opcional): Límite máximo para lineal_tope. Default None.

    Returns:
        int: Valor escalado.
    """
    if modo == "exponencial":
        valor = base * (factor ** nivel)

    elif modo == "lineal":
        valor = base + (factor - 1) * base * nivel

    elif modo == "lineal_tope":
        val = base + (factor - 1) * base * nivel
        valor = min(val, tope) if tope is not None else val

    elif modo == "lineal_porcentaje":
        valor = base * (1 + (factor - 1) * nivel)

    elif modo == "lineal_suavizado":
        incremento = (factor - 1) * base
        valor = base + incremento * (1 - 0.5 ** nivel)

    else:
        valor = base

    return int(valor)

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

        # 🔥 NUEVO: obtener tipo escalado
        tipo_escalado = sistema.get("configuracion", {}).get("racha_tipo_escalado", "exponencial")

        for i, obj in enumerate(racha.get("objetivos", []), 1):
            objetivo_actual = calcular_escalado(
                obj["cantidad_base"],
                obj["factor_escalado"],
                obj.get("nivel", 0),
                tipo_escalado,
                obj.get("tope")
            )

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
    menu_editar_bloque_interactivo(
        racha.setdefault("recompensas", {}),
        "recompensas"

    )

    # -----------------------
    # EDITAR PENALIZACIONES
    # -----------------------
    menu_editar_bloque_interactivo(
        racha.setdefault("penalizaciones", {}),
        "penalizaciones"

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
    """
    Procesa una racha, calculando recompensas o penalizaciones escaladas.
    - clave: "recompensas" o "penalizaciones"
    - forzar: omitir verificación de objetivos para recompensas
    """
    inicializar_rachas(sistema)

    racha = sistema["rachas"]["activas"].get(racha_id)
    if not racha:
        return False

    tipo_escalado = sistema.get("configuracion", {}).get("racha_tipo_escalado", "exponencial")

    # ----------------------------
    # Verificación solo para recompensas
    # ----------------------------
    if clave == "recompensas" and not forzar:
        todos_completos = all(
            obj.get("progreso", 0) >= calcular_escalado(
                obj.get("cantidad_base", 1),
                obj.get("factor_escalado", 1.0),
                obj.get("nivel", 0),
                tipo_escalado,
                obj.get("tope")
            )
            for obj in racha.get("objetivos", [])
        )
        if not todos_completos:
            return None

    datos = racha.get(clave, {})
    if not datos:
        return False

    entregado = {}
    multiplicador = (racha.get("veces_completada", 0) + 1) if clave == "recompensas" else (racha.get("fallos_consecutivos", 0) + 1)

    # ----------------------------
    # Calcular cantidades escaladas
    # ----------------------------
    for tipo, items in datos.items():
        if tipo == "objetos" and isinstance(items, list):
            objetos_dict = {}
            for obj in items:
                nombre = obj.get("nombre")
                if not nombre:
                    continue
                base = obj.get("cantidad", obj.get("cantidad_base", 1))
                factor = obj.get("factor_escalado", 1.0)
                tope = obj.get("tope")
                cantidad_total = calcular_escalado(base, factor, multiplicador - 1, tipo_escalado, tope)
                objetos_dict[nombre] = {
                    "cantidad": cantidad_total,
                    "tipo": obj.get("tipo", "general"),
                    "rareza": obj.get("rareza", "comun"),
                    "descripcion": obj.get("descripcion", ""),
                    "efectos": obj.get("efectos", {})
                }
            if objetos_dict:
                entregado[tipo] = objetos_dict

        elif isinstance(items, dict):
            recursos_dict = {}
            for nombre, info in items.items():
                if not isinstance(info, dict):
                    continue
                base = info.get("valor_base")
                if base is None:
                    continue
                factor = info.get("factor_escalado", 1.0)
                tope = info.get("tope")
                valor = calcular_escalado(base, factor, multiplicador - 1, tipo_escalado, tope)
                recursos_dict[nombre] = valor
            if recursos_dict:
                entregado[tipo] = recursos_dict

    # ----------------------------
    # Validaciones y conflictos
    # ----------------------------
    if entregado:
        entidad_temp = {
            "recompensas": entregado if clave == "recompensas" else {},
            "penalizaciones": entregado if clave == "penalizaciones" else {}
        }
        resultado_validacion = validar_recompensas_entidad(entidad_temp)

        if resultado_validacion["invalidas"]:
            accion = manejar_conflictos(
                racha["nombre"],
                resultado_validacion,
                sistema.get("plugins_activos", {}),
                estado.plugin_cache,
                id_racha=racha["id"]
            )

            if accion == "cancelar":
                return False
            elif accion == "eliminar_entidad":
                eliminar_racha(sistema, racha["id"])
                return False
            elif accion in ["eliminar_recompensas", "ignorar_recompensas"]:
                entidad_temp = filtrar_recompensas_validas_entidad(entidad_temp)
                entregado = entidad_temp.get(clave, {})

    # ----------------------------
    # Aplicar recompensas o penalizaciones
    # ----------------------------
    if entregado:
        aplicar_recompensas(sistema, preparar_recompensa_para_aplicar(sistema, entregado))

    # ----------------------------
    # Actualizar contadores y reinicios
    # ----------------------------
    if clave == "recompensas":
        racha["veces_completada"] = racha.get("veces_completada", 0) + 1
        racha["fallos_consecutivos"] = 0
    else:  # penalizaciones
        racha["fallos_consecutivos"] = racha.get("fallos_consecutivos", 0) + 1
        racha["veces_completada"] = 0
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
    """
    Completa una racha:
    - Si forzar=True: incrementa todos los niveles de los objetivos y aplica recompensas.
    - Si forzar=False: solicita progreso para cada objetivo y solo completa racha si todos los objetivos alcanzan su meta.
    """
    inicializar_rachas(sistema)
    racha = sistema["rachas"]["activas"].get(racha_id)
    if not racha:
        return False

    tipo_escalado = sistema.get("configuracion", {}).get("racha_tipo_escalado", "exponencial")
    todos_completados = True

    # ----------------------
    # FORZADO
    # ----------------------
    if forzar:
        for obj in racha.get("objetivos", []):
            obj["nivel"] = obj.get("nivel", 0) + 1
            obj["progreso"] = 0
        return procesar_racha(sistema, racha_id, "recompensas", forzar=True)

    # ----------------------
    # PROGRESO NORMAL
    # ----------------------
    for obj in racha.get("objetivos", []):
        meta_actual = calcular_escalado(
            obj["cantidad_base"],
            obj.get("factor_escalado", 1.0),
            obj.get("nivel", 0),
            tipo_escalado,
            obj.get("tope")
        )

        progreso_actual = obj.get("progreso", 0)
        tope = obj.get("tope")
        print(f"\nObjetivo: {obj['descripcion']} {progreso_actual}/{int(meta_actual)}")
        
        # Solicitar avance
        cantidad = safe_int_input(f"Ingrese avance desde {progreso_actual}: ", default=0)
        cantidad = max(0, cantidad)

        # Incrementar progreso sin pasarse del tope
        obj["progreso"] = min(progreso_actual + cantidad, meta_actual if tope in (None, 0) else tope)

        # Verificar si este objetivo alcanzó la meta para la racha
        if obj["progreso"] < meta_actual:
            todos_completados = False

    # Guardar cambios
    estado.cambios_no_guardados = True
    guardar_sistema(print_msg=False)

    # ----------------------
    # Si todos los objetivos completaron la meta, subir niveles y aplicar recompensas
    # ----------------------
    if todos_completados:
        for obj in racha.get("objetivos", []):
            obj["nivel"] = obj.get("nivel", 0) + 1
            obj["progreso"] = 0
        return procesar_racha(sistema, racha_id, "recompensas", forzar=True)

    return None

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
    tipo_escalado = sistema.get("configuracion", {}).get("racha_tipo_escalado", "exponencial")

    while True:
        print(f"\n--- DETALLES DE {racha['nombre']} ---")
        print(f"ID: {racha['id']}")
        print(f"Descripción: {racha['descripcion']}")
        print(f"Tipo escalado: {tipo_escalado}")

        # ----------------------------
        # Objetivos
        # ----------------------------
        print("\nObjetivos:")
        for i, obj in enumerate(racha.get("objetivos", []), 1):
            meta_actual = calcular_escalado(
                obj["cantidad_base"],
                obj.get("factor_escalado", 1.0),
                obj.get("nivel", 0),
                tipo_escalado,
                obj.get("tope")
            )
            tope_str = f" | Tope: {obj.get('tope')}" if obj.get("tope") is not None else ""
            print(f"  {i}. {obj['descripcion']} {obj.get('progreso',0)}/{int(meta_actual)} [Nivel: {obj.get('nivel',0)} | FE: {obj.get('factor_escalado',1.0)}{tope_str}]")

        # ----------------------------
        # Recompensas y penalizaciones (unificadas)
        # ----------------------------
        def mostrar_items(items, veces_o_fallos, titulo):
            print(f"\n{titulo}:")
            for t, elementos in items.items():
                if isinstance(elementos, list):
                    for obj in elementos:
                        nombre = obj.get("nombre", "objeto")
                        base = obj.get("cantidad_base", obj.get("cantidad", 0))
                        factor = obj.get("factor_escalado", 1.0)
                        tope = obj.get("tope", None)
                        valor = calcular_escalado(base, factor, veces_o_fallos, tipo_escalado, tope)
                        tope_str = f" | Tope: {tope}" if tope is not None else ""
                        print(f"  {nombre} ({t}): {valor}  [Base: {base} | Factor: {factor}{tope_str}]")
                elif isinstance(elementos, dict):
                    for k, v in elementos.items():
                        base = v.get("valor_base", 0)
                        factor = v.get("factor_escalado", 1.0)
                        tope = v.get("tope", None)
                        valor = calcular_escalado(base, factor, veces_o_fallos, tipo_escalado, tope)
                        tope_str = f" | Tope: {tope}" if tope is not None else ""
                        print(f"  {k} ({t}): {valor}  [Base: {base} | Factor: {factor}{tope_str}]")

        mostrar_items(racha.get("recompensas", {}), racha.get("veces_completada",0), "Recompensas actuales (escaladas)")
        mostrar_items(racha.get("penalizaciones", {}), racha.get("fallos_consecutivos",0), "Penalizaciones actuales")

        # ----------------------------
        # Menú
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

def marcar_progreso_objetivo(objetivo, cantidad, tipo_escalado="exponencial"):
    """
    Incrementa progreso de un objetivo respetando el tope.
    Retorna True si el objetivo alcanzó su meta (para este nivel).
    """
    objetivo_actual = calcular_escalado(
        base=objetivo["cantidad_base"],
        factor=objetivo.get("factor_escalado", 1.0),
        nivel=objetivo.get("nivel", 0),
        modo=tipo_escalado,
        tope=objetivo.get("tope")
    )

    progreso_actual = objetivo.get("progreso", 0)
    progreso_nuevo = progreso_actual + cantidad

    # Si hay tope, no permitir excederlo
    if objetivo.get("tope") is not None:
        max_objetivo = objetivo["tope"]
        if progreso_nuevo > max_objetivo:
            progreso_nuevo = max_objetivo

    objetivo["progreso"] = progreso_nuevo

    # Completado solo si llegó al objetivo actual
    completado = objetivo["progreso"] >= objetivo_actual

    return completado

