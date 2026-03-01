# core/recompensas/bloques.py

from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int, safe_int_input, safe_float_input
from core.recompensas.tipos import obtener_tipos_recompensa_validos, cargar_recursos_desde_sistema, RECURSOS_REGISTRADOS
from core.utils.selector_recursos_existentes import mostrar_recursos_existentes

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


# ─────────────────────────────
# MENÚ INTERACTIVO GENÉRICO
# ─────────────────────────────
def menu_editar_bloque_interactivo(bloque, nombre_bloque):
    """
    Editor dinámico de bloques (recompensas, penalizaciones, etc.)
    Ahora soporta recursos dinámicos cargados desde el sistema.
    """
    # ⚡ Cargar recursos dinámicos del sistema antes de mostrar el menú
    cargar_recursos_desde_sistema(estado.sistema_actual)

    while True:
        print(f"\n--- {nombre_bloque.upper()} ---")

        # Mostrar contenido actual
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
                        print(f"  [{idx}] {obj_item}")
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

        # ------------------------------
        # AGREGAR
        # ------------------------------
        if opcion == 1:
            tipos_validos = obtener_tipos_recompensa_validos()

            print("\nTipos disponibles:")
            for t in sorted(tipos_validos):
                print(f" - {t}")

            tipo = input("Tipo: ").strip()

            if tipo not in tipos_validos:
                print("❌ Tipo inválido.")
                continue

            # ─────────────────────────────
            # OBJETOS (lista)
            # ─────────────────────────────
            if tipo == "objetos":
                
                mostrar_recursos_existentes(estado.sistema_actual, "objetos")

                nombre = input("Nombre del objeto: ").strip()
                base = safe_int_input("Cantidad base: ", default=0)
                factor = safe_float_input("Factor de escalado (1.0 = fijo): ", default=1.0)

                # Calcular cantidad final
                cantidad_total = int(base * factor)

                item = {
                    "nombre": nombre,
                    "cantidad": cantidad_total,
                    "factor_escalado": factor,
                    "tipo": input("Tipo del objeto (opcional): ").strip(),
                    "rareza": input("Rareza (opcional): ").strip(),
                    "descripcion": "",
                    "efectos": {}
                }

                bloque.setdefault("objetos", []).append(item)

                


            else:
                mostrar_recursos_existentes(estado.sistema_actual, tipo)

                base = safe_int_input("Valor base: ", default=0)
                factor = safe_float_input("Factor de escalado (1.0 = fijo): ", default=1.0)
                tope = safe_int_input("Tope máximo (0 = sin tope): ", default=0)

                # 🔥 Detectar si es recurso dinámico
                if tipo in RECURSOS_REGISTRADOS:
                    config = RECURSOS_REGISTRADOS[tipo]
                    modo = config.get("modo", "contenedor")

                    if modo == "simple":
                        # 🔥 SIEMPRE usar estructura multinivel uniforme
                        bloque.setdefault(tipo, {})[tipo] = {
                            "valor_base": base,
                            "factor_escalado": factor,
                            "tope": tope
                        }

                    else:
                        # Contenedor (comportamiento clásico)
                        nombre = input("Subtipo / nombre interno: ").strip()
                        bloque.setdefault(tipo, {})[nombre] = {
                            "valor_base": base,
                            "factor_escalado": factor,
                            "tope": tope
                        }

                else:
                    # Tipos clásicos (stats, dinero, etc.)
                    nombre = input("Nombre del recurso/stat: ").strip()
                    bloque.setdefault(tipo, {})[nombre] = {
                        "valor_base": base,
                        "factor_escalado": factor,
                        "tope": tope
                    }



            estado.cambios_no_guardados = True
            print("✅ Agregado correctamente.")



        # ------------------------------
        # EDITAR
        # ------------------------------
        elif opcion == 2:
            tipo = input("Tipo a editar: ").strip()
            if tipo not in bloque:
                print("❌ Tipo no encontrado.")
                continue

            if tipo == "objetos":
                for idx, obj_item in enumerate(bloque["objetos"]):
                    print(f"[{idx}] {obj_item}")
                index = safe_int_input("Index del objeto a editar (Enter para cancelar): ", default=None)
                if index is None:
                    print("❌ Operación cancelada.")
                    continue
                if index < 0 or index >= len(bloque["objetos"]):
                    print("❌ Index inválido.")
                    continue
                obj_item = bloque["objetos"][index]


                obj_item["nombre"] = input(
                    f"Nombre ({obj_item.get('nombre','')}): "
                ).strip() or obj_item.get("nombre","")

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

                obj_item["tipo"] = input(
                    f"Tipo ({obj_item.get('tipo','')}): "
                ).strip() or obj_item.get("tipo","")

                obj_item["rareza"] = input(
                    f"Rareza ({obj_item.get('rareza','comun')}): "
                ).strip() or obj_item.get("rareza","comun")

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
                nuevo_base = safe_int_input(f"Valor / Cantidad ({base_actual}): ", default=base_actual)
                nuevo_factor = safe_float_input(f"Factor ({factor_actual}): ", default=factor_actual)
                item["valor_base"] = nuevo_base
                item["factor_escalado"] = nuevo_factor
                tope_actual = item.get("tope", None)
                item["tope"] = safe_int_input(f"Tope máximo ({tope_actual}): ", default=tope_actual)


            estado.cambios_no_guardados = True
            print("✅ Editado correctamente.")

        # ------------------------------
        # ELIMINAR
        # ------------------------------
        elif opcion == 3:
            tipo = input("Tipo: ").strip()
            if tipo not in bloque:
                print("❌ Tipo no encontrado.")
                continue

            if tipo == "objetos":
                for idx, obj_item in enumerate(bloque["objetos"]):
                    print(f"[{idx}] {obj_item}")
                index = safe_int_input("Index del objeto a eliminar (Enter para cancelar): ", default=None)
                if index is None:
                    print("❌ Operación cancelada.")
                    continue
                if index < 0 or index >= len(bloque["objetos"]):
                    print("❌ Index inválido.")
                    continue
                bloque["objetos"].pop(index)
                if not bloque["objetos"]:
                    del bloque["objetos"]


            else:
                nombre = input("Nombre a eliminar: ").strip()
                if nombre in bloque[tipo]:
                    del bloque[tipo][nombre]

            estado.cambios_no_guardados = True
            print("✅ Eliminado.")


# ─────────────────────────────
# MENÚ SIMPLE BASADO EN CLAVES
# ─────────────────────────────
def menu_editar_bloque(objeto, clave):
    """
    Menú simplificado para editar recompensas o penalizaciones en misiones.
    No usa escalado ni tope. Solo valores fijos.
    Compatible con aplicar_recompensas().
    """

    cargar_recursos_desde_sistema(estado.sistema_actual)
    bloque = objeto.setdefault(clave, {})

    while True:
        print(f"\n--- {clave.upper()} ---")
        tipos_validos = obtener_tipos_recompensa_validos()

        # ─────────────
        # MOSTRAR ACTUAL
        # ─────────────
        if bloque:
            for tipo, items in bloque.items():
                print(f" {tipo}:")
                if isinstance(items, dict):
                    for nombre, valor in items.items():
                        print(f"   {nombre}: {valor}")
                elif isinstance(items, list):
                    for idx, obj_item in enumerate(items):
                        print(f"   [{idx}] {obj_item}")
                else:
                    print(f"  {items}")
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
                mostrar_recursos_existentes(estado.sistema_actual, "objetos")
                base = pedir_int("Cantidad: ", default=1)
                factor = 1.0  # En este menú no hay escalado, pero lo dejamos por consistencia
            
                cantidad_total = max(int(base * factor), 1)
            
                datos = {
                    "nombre": input("Nombre del objeto: ").strip(),
                    "cantidad": cantidad_total,
                    "tipo": input("Tipo de objeto (opcional): ").strip()
                }
            
                bloque.setdefault("objetos", []).append(datos)

            else:
                # 🔥 Detectar si es recurso dinámico
                if tipo in RECURSOS_REGISTRADOS:
                    config = RECURSOS_REGISTRADOS[tipo]
                    modo = config.get("modo", "contenedor")
                    mostrar_recursos_existentes(estado.sistema_actual, tipo)
                    valor = pedir_int("Valor: ", default=0)

                    if modo == "simple":
                        # Guardar directamente sin subclave
                        bloque[tipo] = {
                            "valor_base": valor
                        }
                        #bloque.setdefault(tipo, {})[tipo] = {"valor_base": valor}

                    else:
                        # Contenedor (comportamiento antiguo)
                        nombre = input("Subtipo / nombre interno: ").strip()
                        bloque.setdefault(tipo, {})[nombre] = {
                            "valor_base": valor
                        }

                else:
                    # Tipos clásicos (stats, dinero, etc.)
                    nombre = input("Nombre del recurso/stat/dinero/puntos: ").strip()
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

                if "objetos" not in bloque or not bloque["objetos"]:
                    print("❌ No hay objetos para editar.")
                    continue

                for idx, obj_item in enumerate(bloque["objetos"]):
                    print(f"[{idx}] {obj_item}")


                index = safe_int_input("Index del objeto a editar (Enter para cancelar): ", default=None)
                if index is None:
                    print("❌ Operación cancelada.")
                    continue
                if index < 0 or index >= len(bloque["objetos"]):
                    print("❌ Index inválido.")
                    continue
                obj_item = bloque["objetos"][index]



                obj_item["nombre"] = input(
                    f"Nombre ({obj_item.get('nombre','')}): "
                ).strip() or obj_item.get("nombre", "")

                obj_item["cantidad"] = pedir_int(
                    f"Cantidad ({obj_item.get('cantidad',1)}): ",
                    default=obj_item.get("cantidad", 1)
                )

                obj_item["tipo"] = input(
                    f"Tipo ({obj_item.get('tipo','')}): "
                ).strip() or obj_item.get("tipo", "")

            else:

                if tipo not in bloque or not bloque[tipo]:
                    print("❌ No hay entradas para editar.")
                    continue

                claves = list(bloque[tipo].keys())

                for i, k in enumerate(claves, 1):
                    print(f"{i}. {k}: {bloque[tipo][k]}")

                nombre = input("Nombre a editar: ").strip()

                if nombre not in bloque[tipo]:
                    print("❌ Clave no encontrada.")
                    continue

                valor_actual = bloque[tipo][nombre].get("valor_base", 0)

                nuevo_valor = pedir_int(
                    f"Nuevo valor ({valor_actual}): ",
                    default=valor_actual
                )

                bloque[tipo][nombre]["valor_base"] = nuevo_valor

            estado.cambios_no_guardados = True
            print("✅ Editado correctamente.")

        # ─────────────────────────────
        # ELIMINAR
        # ─────────────────────────────
        elif opcion == 3:

            if tipo == "objetos":

                if "objetos" not in bloque or not bloque["objetos"]:
                    print("❌ No hay objetos para eliminar.")
                    continue

                for idx, obj_item in enumerate(bloque["objetos"]):
                    print(f"[{idx}] {obj_item}")

                index = safe_int_input("Index del objeto a eliminar (Enter para cancelar): ", default=None)
                if index is None:
                    print("❌ Operación cancelada.")
                    continue
                if index < 0 or index >= len(bloque["objetos"]):
                    print("❌ Index inválido.")
                    continue
                bloque["objetos"].pop(index)
                if not bloque["objetos"]:
                    del bloque["objetos"]

            else:

                if tipo not in bloque or not bloque[tipo]:
                    print("❌ No hay entradas para eliminar.")
                    continue

                nombre = input("Nombre a eliminar: ").strip()

                if nombre in bloque[tipo]:
                    del bloque[tipo][nombre]

                    if not bloque[tipo]:
                        del bloque[tipo]

            estado.cambios_no_guardados = True
            print("✅ Eliminado correctamente.")
