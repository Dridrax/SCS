# plugins/misiones/menus_rachas.py

from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int
from core.guardado.archivos import guardar_sistema
from plugins.misiones.rachas.helpers_rachas import (
    crear_racha, modificar_racha, eliminar_racha,
    gestion_racha, inicializar_rachas, safe_int_input,
    safe_float_input, seleccionar_racha, menu_editar_bloque_interactivo
)



# --------------------------------------------------
# Menú principal de administración de rachas
# --------------------------------------------------

def menu_administrar_rachas(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    while True:
        print("\n=== ADMINISTRAR RACHAS ===")
        print("1. Crear nueva racha")
        print("2. Modificar racha")
        print("3. Eliminar racha")
        
        print("4. Volver")

        opcion = pedir_int("Elige una opción: ", default=4)

        if opcion == 1:
            menu_crear_racha(sistema)
        elif opcion == 2:
            racha = seleccionar_racha(sistema, accion="modificar")
            if racha:
                modificar_racha(sistema, racha["id"])
        elif opcion == 3:
            racha = seleccionar_racha(sistema, accion="eliminar")
            if racha:
                eliminar_racha(sistema, racha["id"])
        
        else:
            guardar_sistema()
            break


# --------------------------------------------------
# Menú crear racha
# --------------------------------------------------

def menu_crear_racha(sistema):
    print("\n=== CREAR NUEVA RACHA ===")
    id = input("ID de la racha (único): ").strip()
    if not id:
        print("❌ ID inválido.")
        return

    nombre = input("Nombre: ").strip()
    if not nombre:
        print("❌ Nombre inválido.")
        return

    descripcion = input("Descripción: ").strip()

    # -----------------------
    # OBJETIVOS
    # -----------------------
    objetivos = []
    while True:
        agregar = input("Agregar objetivo? (s/n): ").strip().lower()
        if agregar != "s":
            break
        desc = input("Descripción del objetivo: ").strip()
        cantidad_base = safe_int_input("Cantidad base del objetivo: ", default=1)
        factor = safe_float_input("Factor de escalado (1.0 = sin cambio): ", default=1.0)
        tope = safe_int_input("Tope máximo (solo lineal_tope, Enter = sin tope): ", default=None)
        objetivos.append({
            "descripcion": desc,
            "cantidad_base": cantidad_base,
            "factor_escalado": factor,
            "tope": tope,
            "nivel": 0,
            "progreso": 0
        })

    # -----------------------
    # RECOMPENSAS
    # -----------------------
    recompensas = {}
    menu_editar_bloque_interactivo(recompensas, "recompensas")

    # -----------------------
    # PENALIZACIONES
    # -----------------------
    penalizaciones = {}
    menu_editar_bloque_interactivo(penalizaciones, "penalizaciones")

    # -----------------------
    # CREAR RACHA
    # -----------------------
    if crear_racha(
        sistema,
        id=id,
        nombre=nombre,
        descripcion=descripcion,
        objetivos=objetivos,
        recompensas=recompensas,
        penalizaciones=penalizaciones
    ):
        print("✅ Racha creada correctamente.")
    else:
        print("❌ Ya existe una racha con ese ID.")



# --------------------------------------------------
# Mostrar y gestionar rachas activas
# --------------------------------------------------

def mostrar_rachas(sistema=None):
    """
    Muestra todas las rachas activas y permite gestionarlas
    (completar, fallar, eliminar) de forma interactiva.
    """
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    inicializar_rachas(sistema)
    activas = sistema.get("rachas", {}).get("activas", {})
    rachas_list = [r for r in activas.values() if isinstance(r, dict) and "id" in r and "nombre" in r]

    if not rachas_list:
        print("❌ No hay rachas activas.")
        return

    while True:
        print("\n=== RACHAS ACTIVAS ===")
        for idx, r in enumerate(rachas_list, 1):
            print(f"{idx}. {r['nombre']} (Veces completada: {r['veces_completada']})")

        seleccion = input("\nElige una racha por número o nombre (Enter para salir): ").strip()
        if not seleccion:
            break

        racha = None
        if seleccion.isdigit():
            index = int(seleccion)-1
            if 0 <= index < len(rachas_list):
                racha = rachas_list[index]
        else:
            for r in rachas_list:
                if r["nombre"].lower() == seleccion.lower():
                    racha = r
                    break

        if not racha:
            print("❌ Racha no encontrada.")
            continue

        gestion_racha(sistema, racha, rachas_list)


