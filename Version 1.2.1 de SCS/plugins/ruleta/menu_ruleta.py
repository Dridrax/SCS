# plugins/ruleta/menu_ruleta.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import pedir_int, pedir_str, seleccionar_opcion
from core.recompensas.bloques import menu_editar_bloque_ruleta
from core.recompensas.tipos import seleccionar_rareza
from core.utils.funciones_utiles import safe_int_input
from .helpers_ruleta import (
    inicializar_ruletas, crear_ruleta, modificar_ruleta,
    gestion_ruleta, eliminar_ruleta, contar_premios_ruleta, 
    normalizar_premios, normalizar_eventos, duplicar_ruleta
)

def mostrar_ruletas(sistema):
    """
    Muestra todas las ruletas disponibles con:
    - Nombre
    - Descripción
    - Número total de premios (recursos + eventos narrativos)
    """

    inicializar_ruletas(sistema)
    activas = sistema["ruleta"]["activas"]

    if not activas:
        print("❌ No hay ruletas disponibles.")
        return

    print("\n=== RULETAS DISPONIBLES ===")

    for ruleta in activas.values():
        nombre = ruleta.get("nombre", "Sin nombre")
        descripcion = ruleta.get("descripcion", "")

        # -------------------------
        # 🎁 CONTAR PREMIOS SISTEMA
        # -------------------------
        total_premios = 0

        premios = ruleta.get("premios", {})

        for tipo, items in premios.items():
            if isinstance(items, list):  # objetos
                total_premios += len(items)
            elif isinstance(items, dict):  # stats, xp, etc
                total_premios += len(items)

        # -------------------------
        # 📖 CONTAR EVENTOS NARRATIVOS
        # -------------------------
        eventos = ruleta.get("eventos_narrativos", [])
        total_premios += len(eventos)

        # -------------------------
        # 🖨 MOSTRAR
        # -------------------------
        print(f"\n{nombre}:")
        print(f"  - {descripcion}")
        print(f"  - {total_premios} premios")

def menu_eventos_narrativos(ruleta):
    """
    Permite gestionar eventos narrativos:
    - Crear
    - Editar
    - Eliminar
    """

    eventos = ruleta.setdefault("eventos_narrativos", [])

    while True:
        print("\n--- EVENTOS NARRATIVOS ---")

        if not eventos:
            print(" (sin eventos)")
        else:
            for i, ev in enumerate(eventos, 1):
                rareza = ev.get("rareza", "sin rareza")
                print(f"{i}. {ev['titulo']} [{rareza}]")

        print("\n[A] Añadir   [E] Editar   [D] Eliminar   [Enter] Volver")
        op = input("> ").strip().lower()

        # -------------------------
        # AÑADIR
        # -------------------------
        if op == "a":
            titulo = input("Título: ").strip()
            descripcion = input("Descripción: ").strip()

            print("\n¿Quieres asignar rareza? (s/n)")
            if input("> ").lower() == "s":
                rareza = seleccionar_rareza(default=None)
            else:
                rareza = None

            nuevo = {
                "titulo": titulo,
                "descripcion": descripcion
            }

            if rareza:
                nuevo["rareza"] = rareza

            eventos.append(nuevo)
            print("✅ Evento añadido.")

        # -------------------------
        # EDITAR
        # -------------------------
        elif op == "e":
            if not eventos:
                continue

            idx = safe_int_input("Número: ", min_val=1, max_val=len(eventos)) - 1
            ev = eventos[idx]

            titulo = input(f"Título ({ev['titulo']}): ").strip() or ev["titulo"]
            descripcion = input(f"Descripción ({ev['descripcion']}): ").strip() or ev["descripcion"]

            print("\n¿Cambiar rareza? (s/n)")
            if input("> ").lower() == "s":
                rareza = seleccionar_rareza(default=ev.get("rareza"))
            else:
                rareza = ev.get("rareza")

            ev["titulo"] = titulo
            ev["descripcion"] = descripcion

            if rareza:
                ev["rareza"] = rareza
            else:
                ev.pop("rareza", None)

            print("✅ Evento editado.")

        # -------------------------
        # ELIMINAR
        # -------------------------
        elif op == "d":
            if not eventos:
                continue

            idx = safe_int_input("Número: ", min_val=1, max_val=len(eventos)) - 1
            eventos.pop(idx)
            print("✅ Evento eliminado.")

        else:
            break

def menu_modificar_ruletas(sistema):
    """
    Menú interactivo de ruletas.
    """
    sistema = estado.sistema_actual
    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    inicializar_ruletas(sistema)

    while True:
        print("\n--- GESTIÓN DE RULETAS ---")
        print("1. Crear ruleta")
        print("2. Modificar ruletas")
        print("3. Eliminar ruletas")  
        print("4. Duplicar ruletas")      
        print("5. Ver ruletas")
        print("6. Volver")

        opcion = pedir_int("Elige una opción: ", default=6)
        activas = sistema["ruleta"]["activas"]

        # =========================================================
        # 🎡 CREAR RULETA
        # =========================================================
        if opcion == 1:
            id = input("ID de la ruleta: ").strip()
            nombre = input("Nombre de la ruleta: ").strip()
            descripcion = input("Descripción: ").strip()

            # 🔹 PREMIOS
            premios_sistema = {}
            print("\n--- CONFIGURAR PREMIOS DE SISTEMA ---")

            # 🔥 NUEVO MENÚ
            menu_editar_bloque_ruleta(premios_sistema)

            # 🔹 NORMALIZAR
            premios_sistema = normalizar_premios(premios_sistema)

            # 🔹 RAREZA OPCIONAL
            for tipo, items in premios_sistema.items():

                if isinstance(items, list):
                    for obj in items:
                        nombre_obj = obj.get("nombre", "objeto")
                        rareza_actual = obj.get("rareza", "ninguna")

                        print(f"\nAsignar rareza para '{nombre_obj}'? (actual: {rareza_actual}) [s/n]")
                        if input("> ").lower() == "s":
                            obj["rareza"] = seleccionar_rareza(default=obj.get("rareza"))

                elif isinstance(items, dict):
                    for nombre_rec, info in items.items():
                        rareza_actual = info.get("rareza", "ninguna")

                        print(f"\nAsignar rareza para '{nombre_rec}'? (actual: {rareza_actual}) [s/n]")
                        if input("> ").lower() == "s":
                            info["rareza"] = seleccionar_rareza(default=info.get("rareza"))

            # 🔹 CREAR RULETA
            creada = crear_ruleta(
                sistema,
                id=id,
                nombre=nombre,
                descripcion=descripcion,
                premios=premios_sistema,
                eventos_narrativos=[]
            )

            if not creada:
                print("❌ No se pudo crear la ruleta.")
                continue

            # 🔹 EVENTOS
            print("\n--- CONFIGURAR EVENTOS NARRATIVOS ---")
            ruleta = sistema["ruleta"]["activas"][id]
            menu_eventos_narrativos(ruleta)

            print("✅ Ruleta configurada completamente.")

        # =========================================================
        # 🛠 MODIFICAR RULETA
        # =========================================================
        elif opcion == 2:
            if not activas:
                print("❌ No hay ruletas disponibles.")
                continue

            lista = list(activas.values())

            print("\n--- RULETAS DISPONIBLES ---")
            mostrar_ruletas(sistema)

            print("\n--- SELECCIÓN ---")
            for i, r in enumerate(lista, 1):
                print(f"{i}. {r['nombre']}")

            idx = pedir_int("Elige una ruleta: ", default=None)

            if idx is None or idx < 1 or idx > len(lista):
                print("❌ Selección inválida.")
                continue

            ruleta = lista[idx - 1]
            ruleta_id = ruleta["id"]

            # -------------------------
            # SUBMENÚ
            # -------------------------
            while True:
                print(f"\n--- MODIFICAR RULETA: {ruleta['nombre']} ---")
                print("1. Cambiar nombre")
                print("2. Cambiar descripción")
                print("3. Editar premios")
                print("4. Editar eventos narrativos")
                print("5. Volver")

                sub = pedir_int("Opción: ", default=5)

                # ✏️ NOMBRE
                if sub == 1:
                    nuevo = input(f"Nuevo nombre ({ruleta['nombre']}): ").strip()
                    if nuevo:
                        modificar_ruleta(sistema, ruleta_id, nombre=nuevo)

                # 📝 DESCRIPCIÓN
                elif sub == 2:
                    nueva = input(f"Nueva descripción ({ruleta['descripcion']}): ").strip()
                    if nueva:
                        modificar_ruleta(sistema, ruleta_id, descripcion=nueva)

                # 🎁 PREMIOS
                elif sub == 3:
                    print("\n--- EDITAR PREMIOS ---")

                    # 🔥 NUEVO MENÚ
                    menu_editar_bloque_ruleta(
                        ruleta.setdefault("premios", {}),
                        "Premios de la ruleta"
                    )

                    # 🔹 NORMALIZAR
                    ruleta["premios"] = normalizar_premios(ruleta["premios"])

                    # 🔹 RAREZA
                    for tipo, items in ruleta["premios"].items():

                        if isinstance(items, list):
                            for obj in items:
                                nombre_obj = obj.get("nombre", "objeto")
                                rareza_actual = obj.get("rareza", "ninguna")

                                print(f"\nAsignar rareza para '{nombre_obj}'? (actual: {rareza_actual}) [s/n]")
                                if input("> ").lower() == "s":
                                    obj["rareza"] = seleccionar_rareza(default=obj.get("rareza"))

                        elif isinstance(items, dict):
                            for nombre_rec, info in items.items():
                                rareza_actual = info.get("rareza", "ninguna")

                                print(f"\nAsignar rareza para '{nombre_rec}'? (actual: {rareza_actual}) [s/n]")
                                if input("> ").lower() == "s":
                                    info["rareza"] = seleccionar_rareza(default=info.get("rareza"))

                    modificar_ruleta(
                        sistema,
                        ruleta_id,
                        premios=ruleta["premios"]
                    )

                # 📖 EVENTOS
                elif sub == 4:
                    print("\n--- EDITAR EVENTOS NARRATIVOS ---")

                    menu_eventos_narrativos(ruleta)

                    modificar_ruleta(
                        sistema,
                        ruleta_id,
                        eventos_narrativos=ruleta["eventos_narrativos"]
                    )

                else:
                    break

        # -------------------------
        #  ELIMINAR RULETA
        # -------------------------
        elif opcion == 3:
            if not activas:
                print("❌ No hay ruletas disponibles.")
                continue
            lista = list(activas.values())
            print("\n--- RULETAS DISPONIBLES ---")
            mostrar_ruletas(sistema)
            print("\n--- SELECCIÓN ---")
            for i, r in enumerate(lista, 1):
                print(f"{i}. {r['nombre']}")
            idx = pedir_int("Elige una ruleta a eliminar: ", default=None)
            if idx is None or idx < 1 or idx > len(lista):
                print("❌ Selección inválida.")
                continue
            ruleta = lista[idx - 1]
            ruleta_id = ruleta["id"]
            # 🔥 LLAMADA A FUNCIÓN SEGURA
            eliminar_ruleta(sistema, ruleta_id)

        # -------------------------
        #  DUPLICAR RULETAS
        # -------------------------
        elif opcion == 4:
            menu_duplicar_ruleta(sistema)

        # -------------------------
        #  VER RULETAS
        # -------------------------
        elif opcion == 5:
            if not activas:
                print("❌ No hay ruletas activas.")
                continue

            print("\n=== 🎡 RULETAS DISPONIBLES ===")

            # 🔹 Vista general limpia
            mostrar_ruletas(sistema)

            # -------------------------
            # 🔎 VER DETALLE OPCIONAL
            # -------------------------
            print("\n¿Quieres ver detalles de alguna ruleta?")
            print("1. Sí")
            print("2. No")

            ver_detalle = pedir_int("Opción: ", default=2)

            if ver_detalle != 1:
                continue

            lista = list(activas.values())

            print("\n--- SELECCIÓN ---")
            for i, r in enumerate(lista, 1):
                print(f"{i}. {r['nombre']}")

            idx = pedir_int("Elige una ruleta: ", default=None)

            if idx is None or idx < 1 or idx > len(lista):
                print("❌ Selección inválida.")
                continue

            ruleta = lista[idx - 1]

            # -------------------------
            # 📊 DETALLE COMPLETO
            # -------------------------
            print(f"\n=== 🎡 {ruleta['nombre']} ===")
            print(f"Descripción: {ruleta.get('descripcion', '')}")
            print(f"Tiradas realizadas: {ruleta.get('tiradas_realizadas', 0)}")

            # 🎁 PREMIOS SISTEMA
            print("\n--- PREMIOS DE SISTEMA ---")
            premios = ruleta.get("premios", {})

            if not premios:
                print(" (sin premios)")
            else:
                for tipo, contenido in premios.items():
                    print(f"\n{tipo.upper()}:")
                    if isinstance(contenido, dict):
                        for k, v in contenido.items():
                            print(f"  {k}: {v}")
                    elif isinstance(contenido, list):
                        for obj in contenido:
                            nombre = obj.get("nombre", "objeto")
                            cantidad = obj.get("cantidad_base", obj.get("cantidad", 1))
                            rareza = obj.get("rareza", "sin rareza")
                            print(f"  {nombre} x{cantidad} [{rareza}]")

            # 📖 EVENTOS NARRATIVOS
            print("\n--- EVENTOS NARRATIVOS ---")
            eventos = ruleta.get("eventos_narrativos", [])

            if not eventos:
                print(" (sin eventos narrativos)")
            else:
                for i, e in enumerate(eventos, 1):
                    rareza = e.get("rareza") or "sin rareza"
                    print(f"{i}. [{rareza}] {e.get('texto', '')} ({e.get('tipo', 'evento')})")


        else:
            guardar_sistema(print_msg=False)
            break

def mostrar_ruletas_interactivo(sistema=None):
    """
    Muestra todas las ruletas activas y permite gestionarlas
    de forma interactiva.
    """
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    inicializar_ruletas(sistema)
    activas = sistema.get("ruleta", {}).get("activas", {})

    ruletas_list = [
        r for r in activas.values()
        if isinstance(r, dict) and "id" in r and "nombre" in r
    ]

    if not ruletas_list:
        print("❌ No hay ruletas activas.")
        return

    while True:
        print("\n=== RULETAS ACTIVAS ===")
        for idx, r in enumerate(ruletas_list, 1):
            total = contar_premios_ruleta(r)
            print(f"{idx}. {r['nombre']} ({total} premios)")

        seleccion = input("\nElige una ruleta por número o nombre (Enter para salir): ").strip()

        if not seleccion:
            break

        ruleta = None

        if seleccion.isdigit():
            index = int(seleccion) - 1
            if 0 <= index < len(ruletas_list):
                ruleta = ruletas_list[index]
        else:
            for r in ruletas_list:
                if r["nombre"].lower() == seleccion.lower():
                    ruleta = r
                    break

        if not ruleta:
            print("❌ Ruleta no encontrada.")
            continue

        gestion_ruleta(sistema, ruleta, ruletas_list)

def menu_duplicar_ruleta(sistema):
    """
    Menú interactivo para duplicar una ruleta existente, permitiendo seleccionar
    premios y eventos narrativos que se quieren copiar.
    """

    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    # 🔹 Acceder a las ruletas activas
    ruletas = sistema.get("ruleta", {}).get("activas", {})
    if not ruletas:
        print("No hay ruletas activas disponibles para duplicar.")
        return

    # ─────────────────────────────
    # Seleccionar ruleta origen
    # ─────────────────────────────
    print("Ruletas activas disponibles:\n")
    ruleta_ids = list(ruletas.keys())
    for i, ruleta_id in enumerate(ruleta_ids, 1):
        ruleta = ruletas[ruleta_id]
        print(f"{i}. {ruleta.get('nombre', 'Sin nombre')} (ID: {ruleta.get('id', 'N/A')})")

    indice_origen = pedir_int("\nSelecciona la ruleta a duplicar:", 1, len(ruleta_ids))
    ruleta_origen_id = ruleta_ids[indice_origen - 1]
    ruleta_origen = ruletas[ruleta_origen_id]


    # ─────────────────────────────
    # Pedir nuevos datos
    # ─────────────────────────────
    while True:
        nueva_id = pedir_str("Nueva ID para la ruleta (obligatorio):").strip()
        if nueva_id and nueva_id not in ruletas:
            break
        print("ID inválida o ya existe. Intenta otra.")

    nuevo_nombre = pedir_str("Nuevo nombre de la ruleta:").strip()
    nueva_descripcion = ""
    while True:
        nueva_descripcion = pedir_str("Nueva descripción (obligatoria):").strip()
        if nueva_descripcion:
            break
        print("La descripción es obligatoria.")

    # ─────────────────────────────
    # Selección de premios
    # ─────────────────────────────
    premios_opcion = seleccionar_opcion(
        ["Todos", "Ninguno", "Seleccionar"], "¿Qué premios deseas copiar?"
    ).lower()

    if premios_opcion == "seleccionar":
        premios_disponibles = list(ruleta_origen.get("premios", {}).keys())
        print("Premios disponibles:")
        for i, p in enumerate(premios_disponibles, 1):
            print(f"{i}. {p}")
        indices = pedir_str(
            "Ingresa los números de los premios a copiar separados por coma (ej: 1,3,4):"
        )
        try:
            indices = [int(x.strip()) - 1 for x in indices.split(",")]
            premios_seleccion = [premios_disponibles[i] for i in indices if 0 <= i < len(premios_disponibles)]
        except Exception:
            premios_seleccion = []
    elif premios_opcion == "todos":
        premios_seleccion = "todos"
    else:
        premios_seleccion = "ninguno"

    # ─────────────────────────────
    # Selección de eventos narrativos
    # ─────────────────────────────
    eventos_opcion = seleccionar_opcion(
        ["Todos", "Ninguno", "Seleccionar"], "¿Qué eventos narrativos deseas copiar?"
    ).lower()

    if eventos_opcion == "seleccionar":
        eventos_disponibles = list(ruleta_origen.get("eventos", {}).keys())
        print("Eventos disponibles:")
        for i, e in enumerate(eventos_disponibles, 1):
            print(f"{i}. {e}")
        indices = pedir_str(
            "Ingresa los números de los eventos a copiar separados por coma (ej: 1,2,4):"
        )
        try:
            indices = [int(x.strip()) - 1 for x in indices.split(",")]
            eventos_seleccion = [eventos_disponibles[i] for i in indices if 0 <= i < len(eventos_disponibles)]
        except Exception:
            eventos_seleccion = []
    elif eventos_opcion == "todos":
        eventos_seleccion = "todos"
    else:
        eventos_seleccion = "ninguno"

    # ─────────────────────────────
    # Llamar a helper para duplicar
    # ─────────────────────────────
    exito = duplicar_ruleta(
        sistema,
        ruleta_id_origen=ruleta_origen_id,
        nueva_id=nueva_id,
        nuevo_nombre=nuevo_nombre,
        nueva_descripcion=nueva_descripcion,
        premios_seleccion=premios_seleccion,
        eventos_seleccion=eventos_seleccion
    )

    if exito:
        print(f"Ruleta '{nuevo_nombre}' duplicada correctamente.")
        guardar_sistema(print_msg=False)
    else:
        print("Error al duplicar la ruleta. Revisa los datos e intenta de nuevo.")