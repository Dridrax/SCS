# plugins/misiones/menus_rachas.py

from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int
from core.guardado.archivos import guardar_sistema
from plugins.rachas.helpers_rachas import (
    crear_racha, modificar_racha, eliminar_racha,
    gestion_racha, inicializar_rachas, safe_int_input,
    safe_float_input, seleccionar_racha, menu_editar_bloque_interactivo
)

# ----------------------------
# Función auxiliar para bloques
# ----------------------------
def menu_editar_recompensas_penalizaciones(racha_dict):
    """
    Menú genérico para editar recompensas y penalizaciones de rachas usando bloques.py
    """
    print("\n--- RECOMPENSAS ---")
    menu_editar_bloque_interactivo(racha_dict.setdefault("recompensas", {}), "recompensas")

    print("\n--- PENALIZACIONES ---")
    menu_editar_bloque_interactivo(racha_dict.setdefault("penalizaciones", {}), "penalizaciones")

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
    # RECOMPENSAS Y PENALIZACIONES
    # -----------------------
    recompensas = {}
    penalizaciones = {}
    menu_editar_recompensas_penalizaciones({"recompensas": recompensas, "penalizaciones": penalizaciones})


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
