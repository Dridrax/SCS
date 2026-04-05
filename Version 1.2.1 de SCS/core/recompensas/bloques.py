# core/recompensas/bloques.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import pedir_int, safe_int_input, safe_float_input
from core.utils.selector_recursos_existentes import mostrar_recursos_existentes
from core.recompensas.tipos import (obtener_tipos_recursos_validos, cargar_recursos_desde_sistema, RECURSOS_BASE, 
                                    RECURSOS_REGISTRADOS, seleccionar_rareza, obtener_definicion_tipo)

def obtener_bloque(objeto, clave="recompensas"):
    """
    Obtiene un bloque dentro de un objeto (misión, racha, plugin, etc.)
    Si no existe, lo inicializa como dict vacío.
    """
    return objeto.setdefault(clave, {})


# ----------------------------------------
# FUNCIONES CRUD PARA BLOQUES
# ----------------------------------------
def agregar_recompensa(bloque, tipo, datos):
    """
    Agrega un elemento al bloque.
    - tipo: objetos, stats, dinero, progress_stats, puntos_stats, nivel, tiradas
    - datos: dict con la info del elemento a agregar
    """
    if tipo == "objetos":
        bloque.setdefault("objetos", []).append(datos)

        
    elif tipo in {"stats", "dinero"}:
        k = datos.get("nombre")
        v = datos.get("valor", 0)
        bloque.setdefault(tipo, {})[k] = v
    elif tipo == "progress_stats":
        nombre = datos.get("nombre")
        bloque.setdefault("progress_stats", {})[nombre] = {
            "actual": datos.get("actual", 0),
            "nivel": datos.get("nivel", 1),
            "max": datos.get("max", 100)
        }
    elif tipo in {"puntos_stats", "nivel", "tiradas"}:
        bloque[tipo] = datos.get("valor", 0)
    else:
        return False

    estado.cambios_no_guardados = True
    return True

def editar_recompensa(bloque, tipo, clave=None, valor=None, index=None):
    """
    Edita un elemento dentro del bloque.
    - tipo: igual que agregar
    - clave: nombre del stat/objeto
    - valor: nuevo valor o dict de actualización
    - index: para objetos dentro de lista
    """
    if tipo == "objetos":
        if index is None or index >= len(bloque.get("objetos", [])):
            return False
        bloque["objetos"][index].update(valor or {})
    elif tipo in {"stats", "dinero"}:
        if clave is None:
            return False
        bloque[tipo][clave] = valor
    elif tipo == "progress_stats":
        if clave is None:
            return False
        bloque["progress_stats"][clave].update(valor or {})
    elif tipo in {"puntos_stats", "nivel", "tiradas"}:
        bloque[tipo] = valor
    else:
        return False

    estado.cambios_no_guardados = True
    return True

def eliminar_recompensa(bloque, tipo=None, clave=None, index=None):
    """
    Elimina elementos del bloque:
    - tipo=None elimina todo
    - tipo=objetos y index dado elimina elemento en lista
    - tipo y clave elimina stat/valor específico
    """
    if tipo is None:
        bloque.clear()
    elif tipo == "objetos" and index is not None:
        bloque.get("objetos", []).pop(index)
    elif tipo in bloque and clave:
        del bloque[tipo][clave]

    estado.cambios_no_guardados = True
    return True

# ────────────── Funciones auxiliares ──────────────
def seleccionar_objeto_base(sistema: dict):
    """
    Selecciona o crea un objeto base SIMPLIFICADO.
    SOLO incluye: nombre, tipo y rareza.
    (Sin valor, sin cantidad, sin efectos complejos)
    """

    inventario = sistema.get("inventario", {})

    def normalizar(txt):
        return str(txt).strip().lower()

    # ─────────────────────────────
    # MOSTRAR INVENTARIO (LIMPIO)
    # ─────────────────────────────
    print("\n=== OBJETOS DISPONIBLES ===")

    lista_ids = list(inventario.keys())

    print("0. ➕ Crear nuevo objeto")

    for i, obj_id in enumerate(lista_ids, start=1):
        obj = inventario[obj_id]

        print(
            f"{i}. {obj.get('nombre','?')} "
            f"[{obj.get('rareza','-')}] | "
            f"{obj.get('tipo','-')}"
        )

    idx = pedir_int("Selecciona opción: ", default=-1)

    if idx < 0:
        print("❌ Cancelado.")
        return None

    # ─────────────────────────────
    # CREAR NUEVO OBJETO
    # ─────────────────────────────
    if idx == 0:
        print("\n--- CREAR OBJETO ---")

        nombre = normalizar(input("Nombre: "))
        tipo_obj = normalizar(input("Tipo (arma, consumible...): "))

        print("\nSeleccione la rareza:\n")
        rareza = normalizar(seleccionar_rareza(prompt="Rareza: "))

        return {
            "nombre": nombre,
            "tipo": tipo_obj,
            "rareza": rareza
        }

    # ─────────────────────────────
    # SELECCIONAR EXISTENTE
    # ─────────────────────────────
    idx_real = idx - 1

    if idx_real >= len(lista_ids):
        print("❌ Selección inválida.")
        return None

    obj = inventario[lista_ids[idx_real]].copy()
    obj.pop("id", None)

    print(f"\nSeleccionado: {obj['nombre']} [{obj.get('rareza','-')}]")

    # Permitir cambiar rareza (opcional)
    nueva_rareza = seleccionar_rareza(
        prompt=f"Rareza ({obj.get('rareza','-')}): ",
        default=obj.get("rareza")
    )

    obj["rareza"] = normalizar(nueva_rareza)

    # 🔥 IMPORTANTE: LIMPIAR CAMPOS NO USADOS
    obj.pop("valor", None)
    obj.pop("efectos", None)
    obj.pop("descripcion", None)
    obj.pop("cantidad", None)

    return {
        "nombre": normalizar(obj.get("nombre")),
        "tipo": normalizar(obj.get("tipo")),
        "rareza": normalizar(obj.get("rareza"))
    }

# ─────────────────────────────
# MENÚ INTERACTIVO GENÉRICO
# ─────────────────────────────
def menu_editar_bloque_interactivo(bloque, nombre_bloque):
    """
    Editor dinámico de bloques (recompensas, penalizaciones, etc.)
    Compatible con recursos dinámicos y objetos reales del inventario.
    """

    cargar_recursos_desde_sistema(estado.sistema_actual)

    while True:
        print(f"\n--- {nombre_bloque.upper()} ---")

        # ─────────────
        # MOSTRAR ACTUAL
        # ─────────────
        if bloque:
            for tipo, items in bloque.items():
                print(f" {tipo}:")

                if isinstance(items, dict):
                    for nombre, info in items.items():
                        base = info.get("valor_base", info.get("valor",
                               info.get("cantidad_base", info.get("cantidad", 0))))
                        factor = info.get("factor_escalado", 1.0)
                        print(f"   {nombre}: {base} [Factor: {factor}]")

                elif isinstance(items, list):
                    for idx, obj_item in enumerate(items):
                        nombre = obj_item.get("nombre", "?")
                        cantidad = obj_item.get("cantidad", 0)
                        rareza = obj_item.get("rareza", "-")
                        print(f"   [{idx}] {nombre} x{cantidad} [{rareza}]")

                else:
                    print(f"  {items}")
        else:
            print(" (vacío)")

        print("\n1. Agregar")
        print("2. Editar")
        print("3. Eliminar")
        print("4. Volver")

        opcion = safe_int_input("Opción: ", default=4)

        if opcion == 4:
            break

        # ─────────────────────────────
        # AGREGAR
        # ─────────────────────────────
        if opcion == 1:
            tipos_validos = obtener_tipos_recursos_validos()

            print("\nTipos disponibles:")
            for t in sorted(tipos_validos):
                print(f" - {t}")

            tipo = input("Tipo: ").strip()

            if tipo not in tipos_validos:
                print("❌ Tipo inválido.")
                continue

            # ───────── OBJETOS ─────────
            if tipo == "objetos":
                # Mostrar inventario + bloque actual
                mostrar_recursos_existentes(estado.sistema_actual, "objetos", bloque_actual=bloque)
            
                base_obj = seleccionar_objeto_base(estado.sistema_actual)
                if not base_obj:
                    continue
                
                cantidad_base = safe_int_input("Cantidad base: ", default=1)
                factor_escalado = safe_float_input("Factor de escalado (1.0 = fijo): ", default=1.0)
            
                item = base_obj.copy()
                item["cantidad_base"] = cantidad_base
                item["factor_escalado"] = factor_escalado
                item["cantidad"] = int(cantidad_base * factor_escalado)
            
                bloque.setdefault("objetos", []).append(item)

            # ───────── OTROS RECURSOS ─────────
            else:
                mostrar_recursos_existentes(estado.sistema_actual, tipo, bloque_actual=bloque)

                base = safe_int_input("Valor base: ", default=0)
                factor = safe_float_input("Factor de escalado (1.0 = fijo): ", default=1.0)
                tope = safe_int_input("Tope máximo (0 = sin tope): ", default=0)

                if tipo in RECURSOS_REGISTRADOS:
                    config = RECURSOS_REGISTRADOS[tipo]
                    modo = config.get("modo", "contenedor")

                    if modo == "simple":
                        bloque.setdefault(tipo, {})[tipo] = {
                            "valor_base": base,
                            "factor_escalado": factor,
                            "tope": tope
                        }
                    else:
                        nombre = input("Subtipo / nombre interno: ").strip()
                        bloque.setdefault(tipo, {})[nombre] = {
                            "valor_base": base,
                            "factor_escalado": factor,
                            "tope": tope
                        }

                else:
                    nombre = input("Nombre del recurso/stat: ").strip()
                    bloque.setdefault(tipo, {})[nombre] = {
                        "valor_base": base,
                        "factor_escalado": factor,
                        "tope": tope
                    }

            estado.cambios_no_guardados = True
            print("✅ Agregado correctamente.")

        # ─────────────────────────────
        # EDITAR
        # ─────────────────────────────
        elif opcion == 2:
            tipo = input("Tipo a editar: ").strip()

            if tipo not in bloque:
                print("❌ Tipo no encontrado.")
                continue

            if tipo == "objetos":
                objetos = bloque.get("objetos", [])

                if not objetos:
                    print("❌ No hay objetos.")
                    continue

                for idx, obj_item in enumerate(objetos):
                    print(f"[{idx}] {obj_item}")

                idx = safe_int_input("Índice: ", default=-1)

                if idx < 0 or idx >= len(objetos):
                    print("❌ Índice inválido.")
                    continue

                obj_item = objetos[idx]

                cantidad_actual = obj_item.get("cantidad", 1)
                obj_item["cantidad"] = safe_int_input(
                    f"Cantidad ({cantidad_actual}): ",
                    default=cantidad_actual
                )

                factor_actual = obj_item.get("factor_escalado", 1.0)
                obj_item["factor_escalado"] = safe_float_input(
                    f"Factor ({factor_actual}): ",
                    default=factor_actual
                )

            else:
                claves = list(bloque[tipo].keys())

                for i, k in enumerate(claves, 1):
                    print(f"{i}. {k}: {bloque[tipo][k]}")

                nombre = input("Nombre a editar: ").strip()

                if nombre not in bloque[tipo]:
                    print("❌ Clave no encontrada.")
                    continue

                item = bloque[tipo][nombre]

                base_actual = item.get("valor_base", item.get("cantidad", 0))
                factor_actual = item.get("factor_escalado", 1.0)

                item["valor_base"] = safe_int_input(
                    f"Valor ({base_actual}): ",
                    default=base_actual
                )

                item["factor_escalado"] = safe_float_input(
                    f"Factor ({factor_actual}): ",
                    default=factor_actual
                )

                item["tope"] = safe_int_input(
                    f"Tope ({item.get('tope', 0)}): ",
                    default=item.get("tope", 0)
                )

            estado.cambios_no_guardados = True
            print("✅ Editado correctamente.")

        # ─────────────────────────────
        # ELIMINAR
        # ─────────────────────────────
        elif opcion == 3:

            tipo = input("Tipo: ").strip()

            if tipo not in bloque:
                print("❌ Tipo no encontrado.")
                continue

            if tipo == "objetos":
                objetos = bloque.get("objetos", [])

                if not objetos:
                    print("❌ No hay objetos.")
                    continue

                for idx, obj_item in enumerate(objetos):
                    print(f"[{idx}] {obj_item}")

                idx = safe_int_input("Índice a eliminar: ", default=-1)

                if idx < 0 or idx >= len(objetos):
                    print("❌ Índice inválido.")
                    continue

                objetos.pop(idx)

                if not objetos:
                    del bloque["objetos"]

            else:
                nombre = input("Nombre a eliminar: ").strip()

                if nombre in bloque[tipo]:
                    del bloque[tipo][nombre]

                    if not bloque[tipo]:
                        del bloque[tipo]

            estado.cambios_no_guardados = True
            print("✅ Eliminado.")

# ─────────────────────────────
# MENÚ SIMPLE BASADO EN CLAVES
# ─────────────────────────────
def menu_editar_bloque(objeto, clave):
    """
    Menú simplificado para editar recompensas o penalizaciones en misiones.
    Usa objetos reales del inventario (sin crear basura).
    """

    cargar_recursos_desde_sistema(estado.sistema_actual)
    bloque = objeto.setdefault(clave, {})

    while True:
        print(f"\n--- {clave.upper()} ---")
        tipos_validos = obtener_tipos_recursos_validos()

        # ─────────────
        # MOSTRAR ACTUAL
        # ─────────────
        if bloque:
            for tipo, contenido in bloque.items():
                print(f" {tipo}:")

                if isinstance(contenido, dict):
                    for nombre, valor in contenido.items():
                        print(f"   {nombre}: {valor}")

                elif isinstance(contenido, list):

                    if tipo == "objetos":
                        for idx, obj in enumerate(contenido):
                            nombre = obj.get("nombre", "?")
                            cantidad = obj.get("cantidad", 0)
                            rareza = obj.get("rareza", "-")
                            print(f"   [{idx}] {nombre} x{cantidad} [{rareza}]")
                    else:
                        for idx, item in enumerate(contenido):
                            print(f"   [{idx}] {item}")

                else:
                    print(f"   {contenido}")
        else:
            print(" (vacío)")

        print("\n1. Agregar")
        print("2. Editar")
        print("3. Eliminar")
        print("4. Volver")

        opcion = pedir_int("Opción: ", default=4)

        if opcion == 4:
            break

        print("\nTipos disponibles:")
        for t in sorted(tipos_validos):
            print(f" - {t}")

        tipo = input("Tipo: ").strip()

        if tipo not in tipos_validos:
            print("❌ Tipo inválido.")
            continue

        # ─────────────────────────────
        # AGREGAR
        # ─────────────────────────────
        if opcion == 1:

            if tipo == "objetos":

                base_obj = seleccionar_objeto_base(estado.sistema_actual)
                if not base_obj:
                    continue

                cantidad = pedir_int("Cantidad: ", default=1)

                item = base_obj.copy()
                item["cantidad"] = cantidad

                bloque.setdefault("objetos", []).append(item)

            else:
                if tipo in RECURSOS_REGISTRADOS:
                    config = RECURSOS_REGISTRADOS[tipo]
                    modo = config.get("modo", "contenedor")

                    mostrar_recursos_existentes(estado.sistema_actual, tipo, bloque_actual=bloque)

                    valor = pedir_int("Valor: ", default=0)

                    if modo == "simple":
                        bloque[tipo] = {
                            "valor_base": valor
                        }
                    else:
                        nombre = input("Subtipo / nombre interno: ").strip()
                        bloque.setdefault(tipo, {})[nombre] = {
                            "valor_base": valor
                        }

                else:
                    nombre = input("Nombre del recurso: ").strip()
                    valor = pedir_int("Valor: ", default=0)

                    bloque.setdefault(tipo, {})[nombre] = {
                        "valor_base": valor
                    }

            estado.cambios_no_guardados = True
            print("✅ Agregado correctamente.")

        # ─────────────────────────────
        # EDITAR
        # ─────────────────────────────
        elif opcion == 2:

            if tipo == "objetos":

                objetos = bloque.get("objetos", [])

                if not objetos:
                    print("❌ No hay objetos.")
                    continue

                for idx, obj in enumerate(objetos):
                    print(f"[{idx}] {obj}")

                idx = pedir_int("Índice: ", default=-1)

                if idx < 0 or idx >= len(objetos):
                    print("❌ Índice inválido.")
                    continue

                obj_item = objetos[idx]

                cantidad_actual = obj_item.get("cantidad", 1)
                obj_item["cantidad"] = pedir_int(
                    f"Cantidad ({cantidad_actual}): ",
                    default=cantidad_actual
                )

            else:

                if tipo not in bloque or not bloque[tipo]:
                    print("❌ No hay entradas.")
                    continue

                claves = list(bloque[tipo].keys())

                for i, k in enumerate(claves, 1):
                    print(f"{i}. {k}: {bloque[tipo][k]}")

                nombre = input("Nombre a editar: ").strip()

                if nombre not in bloque[tipo]:
                    print("❌ Clave no encontrada.")
                    continue

                valor_actual = bloque[tipo][nombre].get("valor_base", 0)

                bloque[tipo][nombre]["valor_base"] = pedir_int(
                    f"Nuevo valor ({valor_actual}): ",
                    default=valor_actual
                )

            estado.cambios_no_guardados = True
            print("✅ Editado correctamente.")

        # ─────────────────────────────
        # ELIMINAR
        # ─────────────────────────────
        elif opcion == 3:

            if tipo == "objetos":

                objetos = bloque.get("objetos", [])

                if not objetos:
                    print("❌ No hay objetos.")
                    continue

                for idx, obj in enumerate(objetos):
                    print(f"[{idx}] {obj}")

                idx = pedir_int("Índice a eliminar: ", default=-1)

                if idx < 0 or idx >= len(objetos):
                    print("❌ Índice inválido.")
                    continue

                objetos.pop(idx)

                if not objetos:
                    del bloque["objetos"]

            else:

                if tipo not in bloque or not bloque[tipo]:
                    print("❌ No hay entradas.")
                    continue

                nombre = input("Nombre a eliminar: ").strip()

                if nombre in bloque[tipo]:
                    del bloque[tipo][nombre]

                    if not bloque[tipo]:
                        del bloque[tipo]

            estado.cambios_no_guardados = True
            print("✅ Eliminado correctamente.")

# ─────────────────────────────
# MENÚ SIMPLE PARA RULETA
# ─────────────────────────────
def menu_editar_bloque_ruleta(bloque, nombre_bloque="premios"):
    """
    Editor de bloques para RULETA (versión limpia y funcional)
    """
    cargar_recursos_desde_sistema(estado.sistema_actual)

    while True:
        print(f"\n--- {nombre_bloque.upper()} (RULETA) ---")

        # ─────────────
        # MOSTRAR BLOQUE ACTUAL
        # ─────────────
        if bloque:
            for tipo, lista in bloque.items():
                print(f" {tipo}:")
                for i, item in enumerate(lista):
                    nombre = item.get("nombre", "?")
                    valor = item.get("valor") or item.get("cantidad") or 1
                    tipo_valor = item.get("tipo", tipo)
                    rareza = item.get("rareza", "-")
                    print(f"   [{i}] {nombre} → {tipo_valor} {valor} [{rareza}]")
        else:
            print(" (vacío)")

        # ─────────────
        # MENÚ PRINCIPAL
        # ─────────────
        print("\n1. Agregar\n2. Editar\n3. Eliminar\n4. Volver")
        opcion = pedir_int("Opción: ", default=4)
        if opcion == 4:
            break

        # Mostrar tipos válidos antes de pedir tipo
        tipos_validos = obtener_tipos_recursos_validos()
        print("\nTipos disponibles:")
        for t in sorted(tipos_validos):
            print(f" - {t}")

        tipo = input("Tipo: ").strip()
        if tipo not in tipos_validos:
            print("❌ Tipo inválido.")
            continue

        bloque.setdefault(tipo, [])

        # ==================================================
        # ➕ AGREGAR
        # ==================================================
        if opcion == 1:
            if tipo == "objetos":
                base = seleccionar_objeto_base(estado.sistema_actual)
                if not base:
                    print("❌ Cancelado.")
                    continue
                cantidad = pedir_int("Cantidad: ", default=1)
                nuevo = base.copy()
                nuevo["cantidad"] = cantidad
            else:
                mostrar_recursos_existentes(estado.sistema_actual, tipo, bloque_actual=bloque)
                nombre = input("Nombre: ").strip()
                valor = pedir_int("Valor: ", default=1)
                nuevo = {"nombre": nombre, "valor": valor, "tipo": tipo}

            rareza = seleccionar_rareza(prompt="Rareza (opcional): ")
            if rareza:
                nuevo["rareza"] = rareza

            bloque[tipo].append(nuevo)
            estado.cambios_no_guardados = True
            print("✅ Agregado.")

        # ==================================================
        # ✏️ EDITAR
        # ==================================================
        elif opcion == 2:
            if not bloque[tipo]:
                print("❌ No hay elementos.")
                continue

            # Mostrar lista de items de forma limpia
            for i, item in enumerate(bloque[tipo]):
                nombre = item.get("nombre", "?")
                valor = item.get("valor") or item.get("cantidad") or 1
                rareza = item.get("rareza", "-")
                print(f"[{i}] {nombre} → {valor} [{rareza}]")

            idx = pedir_int("Índice a editar: ", default=-1)
            if idx < 0 or idx >= len(bloque[tipo]):
                print("❌ Índice inválido.")
                continue

            item = bloque[tipo][idx]

            # Editar nombre
            item["nombre"] = input(f"Nombre ({item.get('nombre')}): ").strip() or item.get("nombre")

            # Editar valor/cantidad
            actual = item.get("valor") or item.get("cantidad") or 1
            nuevo_valor = pedir_int(f"Valor ({actual}): ", default=actual)
            if tipo == "objetos":
                item["cantidad"] = nuevo_valor
            else:
                item["valor"] = nuevo_valor

            # Editar tipo y rareza
            item["tipo"] = input(f"Tipo valor ({item.get('tipo', tipo)}): ").strip() or item.get("tipo", tipo)
            item["rareza"] = seleccionar_rareza(prompt=f"Rareza ({item.get('rareza','-')}): ", default=item.get("rareza"))

            estado.cambios_no_guardados = True
            print("✅ Editado.")

        # ==================================================
        # ❌ ELIMINAR
        # ==================================================
        elif opcion == 3:
            if not bloque[tipo]:
                print("❌ No hay elementos.")
                continue

            for i, item in enumerate(bloque[tipo]):
                nombre = item.get("nombre", "?")
                valor = item.get("valor") or item.get("cantidad") or 1
                rareza = item.get("rareza", "-")
                print(f"[{i}] {nombre} → {valor} [{rareza}]")

            idx = pedir_int("Índice a eliminar: ", default=-1)
            if idx < 0 or idx >= len(bloque[tipo]):
                print("❌ Índice inválido.")
                continue

            bloque[tipo].pop(idx)
            if not bloque[tipo]:
                del bloque[tipo]

            estado.cambios_no_guardados = True
            print("✅ Eliminado.")