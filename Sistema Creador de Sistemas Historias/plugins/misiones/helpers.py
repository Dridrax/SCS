from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.recompensas.aplicar import aplicar_recompensas

from plugins.misiones.modelos import crear_modelo_mision

from plugins.misiones.helpers_recompensas import (
    agregar_recompensa_item,
    agregar_recompensa_stat,
    agregar_recompensa_progress_stat,
    agregar_recompensa_puntos_stats,
    agregar_recompensa_dinero,
    agregar_recompensa_nivel,
    agregar_recompensa_tirada
)
from core.utils.funciones_utiles import pedir_int
# --------------------------------------------------
# Inicialización
# --------------------------------------------------

def inicializar_misiones(sistema):
    sistema.setdefault("misiones", {})


# --------------------------------------------------
# Crear misión
# --------------------------------------------------

def crear_mision(
    sistema,
    *,
    id,
    nombre,
    descripcion="",
    objetivo="",
    recompensas=None,
    penalizaciones=None
):
    inicializar_misiones(sistema)

    if id in sistema["misiones"]:
        return False  # ya existe

    sistema["misiones"][id] = crear_modelo_mision(
        id=id,
        nombre=nombre,
        descripcion=descripcion,
        objetivo=objetivo,
        recompensas=recompensas,
        penalizaciones=penalizaciones
    )

    estado.cambios_no_guardados = True
    guardar_sistema()
    return True



def menu_crear_mision(sistema):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    print("\n=== CREAR NUEVA MISIÓN ===")
    mision_id = input("ID interno (único): ").strip()
    nombre = input("Nombre: ").strip()
    descripcion = input("Descripción: ").strip()
    objetivo = input("Objetivo narrativo: ").strip()

    crear_mision(
        sistema,
        id=mision_id,
        nombre=nombre,
        descripcion=descripcion,
        objetivo=objetivo,
        recompensas={},
        penalizaciones={}
    )

    print("✅ Misión creada.")

    mision = sistema["misiones"][mision_id]

    while True:
        print("\n--- AÑADIR RECOMPENSAS / PENALIZACIONES ---")
        print("1. Añadir")
        print("2. Editar")
        print("3. Eliminar")
        print("4. Terminar creación")

        opcion = pedir_int("Elige una opción: ", default=4)

        if opcion == 4:
            guardar_sistema()
            print("✅ Creación de misión finalizada.")
            break

        destino = elegir_destino()
        if destino is None:
            continue

        bloque = mision.setdefault(destino, {})

        if opcion == 1:
            añadir_recompensa(sistema, bloque)

        elif opcion == 2:
            editar_recompensa_existente(bloque)

        elif opcion == 3:
            eliminar_recompensa(bloque)

        else:
            print("❌ Opción inválida.")




# --------------------------------------------------
# Modificar misión
# --------------------------------------------------

def modificar_mision(sistema, mision_id):
    misiones = sistema.get("misiones", {})
    mision = misiones.get(mision_id)

    if not mision:
        print("❌ No existe esa misión.")
        return False

    while True:
        print("\n=== MODIFICAR MISIÓN ===")
        print(f"ID: {mision['id']}")
        print(f"Nombre: {mision['nombre']}")

        print("\n1. Editar datos básicos")
        print("2. Editar recompensas")
        print("3. Editar penalizaciones")
        print("4. Volver")

        opcion = pedir_int("Elige opción: ", default=4)

        if opcion == 1:
            editar_datos_basicos_mision(mision)

        elif opcion == 2:
            menu_editar_recompensas(sistema, mision, clave="recompensas")

        elif opcion == 3:
            menu_editar_recompensas(sistema, mision, clave="penalizaciones")

        else:
            break

    estado.cambios_no_guardados = True
    guardar_sistema()
    return True



def editar_datos_basicos_mision(mision):
    print("\n--- DATOS BÁSICOS ---")
    nombre = input(f"Nombre ({mision['nombre']}): ").strip()
    descripcion = input(f"Descripción ({mision['descripcion']}): ").strip()
    objetivo = input(f"Objetivo ({mision['objetivo']}): ").strip()

    if nombre:
        mision["nombre"] = nombre
    if descripcion:
        mision["descripcion"] = descripcion
    if objetivo:
        mision["objetivo"] = objetivo

    print("✅ Datos básicos actualizados.")


def menu_editar_recompensas(sistema, mision, clave="recompensas"):
    bloque = mision.setdefault(clave, {})

    while True:
        print(f"\n--- {clave.upper()} ---")

        if not bloque:
            print("No hay entradas.")
        else:
            for i, (tipo, valor) in enumerate(bloque.items(), 1):
                if tipo == "objetos":
                    print(f"{i}. objetos ({len(valor)})")
                else:
                    print(f"{i}. {tipo}: {valor}")

        print("\n1. Añadir")
        print("2. Editar")
        print("3. Eliminar")
        print("4. Volver")

        opcion = pedir_int("Elige opción: ", default=4)

        if opcion == 1:
            añadir_recompensa(sistema, bloque)

        elif opcion == 2:
            editar_recompensa_existente(bloque)

        elif opcion == 3:
            eliminar_recompensa(bloque)

        else:
            break

#####
def añadir_recompensa(sistema, bloque):
    tipo = input(
        "Tipo (objetos/stats/progress_stats/puntos_stats/dinero/nivel/tiradas): "
    ).strip()

    if tipo == "objetos":
        bloque.setdefault("objetos", []).append({
            "nombre": input("Nombre: "),
            "cantidad": pedir_int("Cantidad: ", default=1),
            "rareza": input("Rareza: ") or "común",
            "tipo": input("Tipo: ") or "misc",
            "descripcion": input("Descripción: "),
            "efectos": {}
        })

    elif tipo in {"puntos_stats", "nivel", "tiradas"}:
        bloque[tipo] = pedir_int("Valor: ")

    elif tipo in {"stats", "dinero"}:
        k = input("Nombre: ")
        v = pedir_int("Valor: ")
        bloque.setdefault(tipo, {})[k] = v

    elif tipo == "progress_stats":
        stat = input("Nombre stat: ")
        bloque.setdefault("progress_stats", {})[stat] = {
            "actual": pedir_int("Actual: ", default=0),
            "nivel": pedir_int("Nivel: ", default=1),
            "max": pedir_int("Máximo: ", default=100)
        }

    else:
        print("❌ Tipo inválido.")
        return

    print("✅ Añadido correctamente.")


def editar_recompensa_existente(bloque):
    if not bloque:
        print("No hay recompensas.")
        return

    tipos = list(bloque.keys())
    for i, t in enumerate(tipos, 1):
        print(f"{i}. {t}")

    idx = pedir_int("Editar cuál: ") - 1
    if not (0 <= idx < len(tipos)):
        return

    tipo = tipos[idx]

    if tipo == "objetos":
        objetos = bloque["objetos"]
        for i, obj in enumerate(objetos, 1):
            print(f"{i}. {obj['nombre']} x{obj['cantidad']}")

        j = pedir_int("Objeto: ") - 1
        if 0 <= j < len(objetos):
            obj = objetos[j]
            obj["nombre"] = input(f"Nombre ({obj['nombre']}): ") or obj["nombre"]
            obj["cantidad"] = pedir_int("Cantidad: ", default=obj["cantidad"])
            obj["rareza"] = input(f"Rareza ({obj['rareza']}): ") or obj["rareza"]
            obj["tipo"] = input(f"Tipo ({obj['tipo']}): ") or obj["tipo"]
            obj["descripcion"] = input("Descripción: ") or obj["descripcion"]

    elif isinstance(bloque[tipo], dict):
        for k in bloque[tipo]:
            print(f"- {k}: {bloque[tipo][k]}")
        clave = input("Qué clave editar: ")
        if clave in bloque[tipo]:
            bloque[tipo][clave] = pedir_int("Nuevo valor: ")

    else:
        bloque[tipo] = pedir_int("Nuevo valor: ")

    print("✅ Recompensa editada.")



def eliminar_recompensa(bloque):
    if not bloque:
        print("Nada que eliminar.")
        return

    tipos = list(bloque.keys())
    for i, t in enumerate(tipos, 1):
        print(f"{i}. {t}")

    idx = pedir_int("Eliminar cuál: ") - 1
    if 0 <= idx < len(tipos):
        del bloque[tipos[idx]]
        print("✅ Eliminada.")
####

def elegir_destino():
    while True:
        print("\n¿Dónde quieres añadir esto?")
        print("1. Recompensas")
        print("2. Penalizaciones")
        print("[Enter] Volver")

        opcion = input("> ").strip()
        if opcion == "1":
            return "recompensas"
        elif opcion == "2":
            return "penalizaciones"
        elif opcion == "":
            return None
        else:
            print("❌ Opción no válida.")


# --------------------------------------------------
# Eliminar misión
# --------------------------------------------------

def eliminar_mision(sistema, id):
    inicializar_misiones(sistema)
    if id not in sistema["misiones"]:
        print("❌ No existe esa misión.")
        return False

    confirmar = input(f"¿Seguro que quieres eliminar la misión '{sistema['misiones'][id]['nombre']}'? (s/n): ").strip().lower()
    if confirmar != "s":
        print("❌ Eliminación cancelada.")
        return False

    del sistema["misiones"][id]
    estado.cambios_no_guardados = True
    guardar_sistema()
    print("✅ Misión eliminada.")
    return True


# --------------------------------------------------
# Completar misión
# --------------------------------------------------


def completar_mision(sistema, mision_id):
    """
    Completa una misión aplicando las recompensas.
    Penalizaciones = recompensas con valores negativos.
    """
    misiones = sistema.get("misiones", {})

    if mision_id not in misiones:
        return False

    mision = misiones[mision_id]

    # Recompensas
    recompensas = mision.get("recompensas", {})
    if recompensas:
        aplicar_recompensas(sistema, recompensas)

    estado.cambios_no_guardados = True
    return True

def fallar_mision(sistema, mision_id):
    """
        Falla una misión aplicando las penalizaciones.
        Penalizaciones = recompensas con valores negativos.
        """
    misiones = sistema.get("misiones", {})

    if mision_id not in misiones:
        return False

    mision = misiones[mision_id]


    # Penalizaciones (mismo sistema)
    penalizaciones = mision.get("penalizaciones", {})
    if penalizaciones:
        aplicar_recompensas(sistema, penalizaciones)

    # Eliminar misión tras completarla
    del misiones[mision_id]

    estado.cambios_no_guardados = True
    return True





def imprimir_resultados(titulo, datos):
    print(f"{titulo}:")
    
    if not datos:
        print("  Ninguna")
        return

    if "objetos" in datos:
        print("  Objetos:")
        for o in datos["objetos"]:
            print(f"    - {o['nombre']} | Cantidad: {o['cantidad']} | Rareza: {o['rareza']} | Tipo: {o['tipo']}")

    if "stats" in datos:
        print("  Stats:")
        for k, v in datos["stats"].items():
            print(f"    - {k}: {v}")

    if "progress_stats" in datos:
        print("  Progress Stats:")
        for k, v in datos["progress_stats"].items():
            print(f"    - {k}: {v['actual']}/{v['max']} (Nivel {v['nivel']})")

    if "puntos_stats" in datos:
        print(f"  Puntos de Stats: {datos['puntos_stats']}")

    if "dinero" in datos:
        print("  Dinero:")
        for moneda, cantidad in datos["dinero"].items():
            print(f"    - {moneda}: {cantidad}")

    if "nivel" in datos:
        print(f"  Nivel: {datos['nivel']}")

    if "tiradas" in datos:
        print(f"  Tiradas: {datos['tiradas']}")



