from core.estado_global import estado
import uuid

# ---------- UTIL ----------

def generar_id():
    return f"titulo_{uuid.uuid4().hex[:8]}"

def buscar_titulo(enciclopedia, titulo_id):
    return next((t for t in enciclopedia if t["id"] == titulo_id), None)

# ---------- MOSTRAR ----------

def mostrar_titulos(sistema):
    print("\n🏆 TÍTULOS DEL PERSONAJE\n")

    ids = sistema.get("titulos", [])
    if not ids:
        print("No hay títulos.")
        return

    enciclopedia = sistema["enciclopedias"]["titulos"]

    for tid in ids:
        t = buscar_titulo(enciclopedia, tid)
        if t:
            print(f"- {t['nombre']} ({t['tipo']}): {t['descripcion']}, "
                  f"Origen: {t.get('origen','')}, Efectos: {t.get('efectos',{})}")

# ---------- AÑADIR ----------

def añadir_titulo(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    print("\n➕ AÑADIR TÍTULO\n")

    titulo = {
        "id": generar_id(),
        "nombre": input("Nombre del título: "),
        "descripcion": input("Descripción: "),
        "origen": input("Origen del título: "),
        "tipo": input("Tipo de título: "),
        "efectos": {}
    }

    efectos_input = input("Efectos sobre stats (ej: Ataque:7,Vida:10): ")
    for parte in efectos_input.split(","):
        if ":" in parte:
            stat, valor = parte.split(":")
            try:
                titulo["efectos"][stat.strip()] = int(valor.strip())
            except ValueError:
                print(f"⚠️ Ignorado efecto inválido: {parte}")

    # Registrar en enciclopedia
    enciclopedia = sistema.setdefault("enciclopedias", {}).setdefault("titulos", [])
    enciclopedia.append(titulo)

    # Activar en sistema (solo ID)
    sistema.setdefault("titulos", []).append(titulo["id"])

    estado.cambios_no_guardados = True
    print(f"✅ Título '{titulo['nombre']}' añadido correctamente.")

# ---------- MODIFICAR ----------

def modificar_titulo(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema.get("titulos"):
        print("❌ No hay títulos para modificar.")
        return

    enciclopedia = sistema["enciclopedias"]["titulos"]

    for i, tid in enumerate(sistema["titulos"], 1):
        t = buscar_titulo(enciclopedia, tid)
        print(f"{i}. {t['nombre']} ({t['tipo']})")

    try:
        indice = int(input("Número del título a modificar: ")) - 1
        tid = sistema["titulos"][indice]
        t = buscar_titulo(enciclopedia, tid)

        print(f"\nTítulo seleccionado: {t['nombre']}")

        t["nombre"] = input(f"Nuevo nombre [{t['nombre']}]: ") or t["nombre"]
        t["descripcion"] = input(f"Nueva descripción [{t['descripcion']}]: ") or t["descripcion"]
        t["origen"] = input(f"Nuevo origen [{t['origen']}]: ") or t["origen"]
        t["tipo"] = input(f"Nuevo tipo [{t['tipo']}]: ") or t["tipo"]

        nuevos_efectos = input("Nuevos efectos (ej: Ataque:7,Vida:10, enter para mantener): ")
        if nuevos_efectos:
            t["efectos"] = {}
            for parte in nuevos_efectos.split(","):
                if ":" in parte:
                    stat, valor = parte.split(":")
                    try:
                        t["efectos"][stat.strip()] = int(valor.strip())
                    except ValueError:
                        print(f"⚠️ Ignorado efecto inválido: {parte}")

        estado.cambios_no_guardados = True
        print("✅ Título modificado correctamente.")

    except (ValueError, IndexError):
        print("❌ Selección inválida.")

# ---------- ELIMINAR ----------

def eliminar_titulo(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual
    if not sistema.get("titulos"):
        print("❌ No hay títulos para eliminar.")
        return

    enciclopedia = sistema["enciclopedias"]["titulos"]

    for i, tid in enumerate(sistema["titulos"], 1):
        t = buscar_titulo(enciclopedia, tid)
        print(f"{i}. {t['nombre']} ({t['tipo']})")

    try:
        indice = int(input("Número del título a eliminar: ")) - 1
        tid = sistema["titulos"].pop(indice)

        estado.cambios_no_guardados = True
        print("🗑️ Título desasignado del personaje.")

    except (ValueError, IndexError):
        print("❌ Selección inválida.")

# ---------- MENÚ ----------

def menu_titulos(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    while True:
        print("\n=== MENÚ DE TÍTULOS ===")
        print("1. Ver títulos")
        print("2. Añadir título")
        print("3. Modificar título")
        print("4. Eliminar título")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_titulos(sistema)
        elif opcion == "2":
            añadir_titulo(sistema)
        elif opcion == "3":
            modificar_titulo(sistema)
        elif opcion == "4":
            eliminar_titulo(sistema)
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida.")
