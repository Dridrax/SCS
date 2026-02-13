# core/recompensas/bloques.py

from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int, safe_int_input, safe_float_input

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


# ----------------------------------------
# MENÚ INTERACTIVO GENÉRICO
# ----------------------------------------

def menu_editar_bloque_interactivo(bloque, nombre_bloque, tipos_validos=None):
    """
    Editor dinámico de bloques (recompensas, penalizaciones, etc.)
    - bloque: dict con la info a editar
    - nombre_bloque: nombre para mostrar
    - tipos_validos: opcional, lista de tipos permitidos (objetos, stats, dinero, etc.)
    """
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
                else:
                    print(f"  {items}")

        print("\n1. Agregar")
        print("2. Editar")
        print("3. Eliminar")
        print("4. Volver")

        opcion = safe_int_input("Opción: ", default=4)

        # --------------------------------------------------
        # SALIR
        # --------------------------------------------------
        if opcion == 4:
            break

        # --------------------------------------------------
        # AGREGAR
        # --------------------------------------------------
        if opcion == 1:
            tipo = input("Tipo: ").strip()
            if tipos_validos and tipo not in tipos_validos:
                print("❌ Tipo inválido.")
                continue

            nombre = input("Nombre del recurso/stat/objeto: ").strip()
            base = safe_int_input("Valor / Cantidad base: ", default=0)
            factor = safe_float_input("Factor de escalado (1.0 = fijo): ", default=1.0)

            # AGREGAR ELEMENTO
            item = {}
            if tipo == "objetos":
                item["cantidad"] = base
            else:
                item["valor_base"] = base
                tope = safe_int_input("Tope máximo (Enter = sin tope): ", default=None)
                item["tope"] = tope

            item["factor_escalado"] = factor

            bloque.setdefault(tipo, {})[nombre] = item
            estado.cambios_no_guardados = True
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
                tope_actual = item.get("tope", None)
                item["tope"] = safe_int_input(f"Tope máximo ({tope_actual}): ", default=tope_actual)

            item["factor_escalado"] = nuevo_factor
            estado.cambios_no_guardados = True
            print("✅ Editado correctamente.")

        # --------------------------------------------------
        # ELIMINAR
        # --------------------------------------------------
        elif opcion == 3:
            tipo = input("Tipo: ").strip()
            nombre = input("Nombre: ").strip()
            if tipo in bloque and nombre in bloque[tipo]:
                del bloque[tipo][nombre]
                estado.cambios_no_guardados = True
                print("✅ Eliminado.")
            else:
                print("❌ No encontrado.")


# ----------------------------------------
# MENÚ SIMPLE BASADO EN CLAVES
# ----------------------------------------

def menu_editar_bloque(objeto, clave):
    """
    Menú clásico basado en claves. Internamente usa obtener_bloque y las funciones CRUD.
    """
    bloque = obtener_bloque(objeto, clave)
    while True:
        print(f"\n--- {clave.upper()} ---")
        print("1. Agregar")
        print("2. Editar")
        print("3. Eliminar")
        print("4. Volver")
        opcion = pedir_int("Opción: ", default=4)

        if opcion == 1:
            tipo = input("Tipo: ").strip()
            datos = {}
            if tipo == "objetos":
                datos["nombre"] = input("Nombre objeto: ")
                datos["cantidad"] = int(input("Cantidad: "))
                datos["rareza"] = input("Rareza: ")
                datos["tipo"] = input("Tipo: ")
            else:
                datos["nombre"] = input("Nombre: ")
                datos["valor"] = int(input("Valor: "))
            agregar_recompensa(bloque, tipo, datos)
            print("✅ Agregado.")

        elif opcion == 2:
            tipo = input("Tipo a editar: ").strip()
            clave_dato = input("Clave (nombre del stat/objeto): ").strip() or None
            valor = input("Valor/Actualizar: ").strip()
            try: valor = int(valor)
            except: pass
            editar_recompensa(bloque, tipo, clave=clave_dato, valor=valor)
            print("✅ Editado.")

        elif opcion == 3:
            tipo = input("Tipo a eliminar: ").strip()
            clave_dato = input("Clave a eliminar (opcional): ").strip() or None
            index = None
            if tipo == "objetos":
                index = int(input("Index objeto: "))
            eliminar_recompensa(bloque, tipo=tipo, clave=clave_dato, index=index)
            print("✅ Eliminado.")
        else:
            break
