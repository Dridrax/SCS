from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.historia.filtros import menu_filtros_linea_temporal

# --------------------------------------------------
# UTILIDADES
# --------------------------------------------------
def normalizar_linea_temporal(sistema=None):
    """Asegura que todos los capítulos tengan id y arco"""
    sistema = sistema or estado.sistema_actual
    sistema.setdefault("linea_temporal", [])
    for i, cap in enumerate(sistema["linea_temporal"], 1):
        cap.setdefault("id", i)
        cap.setdefault("arco", "General")
    return sistema

def pedir_int(texto, actual=None):
    valor = input(f"{texto} [{actual}]: ")
    if valor == "":
        return actual
    try:
        return int(valor)
    except ValueError:
        print("⚠️ Valor inválido, se mantiene el anterior.")
        return actual

def pedir_str(texto, actual=None):
    valor = input(f"{texto} [{actual}]: ")
    return actual if valor == "" else valor

# --------------------------------------------------
# AÑADIR CAPÍTULO
# --------------------------------------------------
def añadir_capitulo(sistema=None):
    sistema = normalizar_linea_temporal(sistema)

    print("\n📖 NUEVO CAPÍTULO\n")

    capitulo = {
        "id": len(sistema["linea_temporal"]) + 1,
        "titulo": input("Título del capítulo: "),
        "resumen": input("Resumen / qué ocurrió: "),
        "arco": input("Arco / Saga (enter = General): ") or "General"
    }

    sistema["linea_temporal"].append(capitulo)
    estado.cambios_no_guardados = True
    print("✅ Capítulo añadido correctamente.")

    # Opcional: registrar en enciclopedia
    sistema.setdefault("enciclopedias", {}).setdefault("linea_temporal", []).append({**capitulo, "activo": True})

# --------------------------------------------------
# MODIFICAR CAPÍTULO
# --------------------------------------------------
def modificar_capitulo(sistema=None):
    sistema = normalizar_linea_temporal(sistema)

    if not sistema["linea_temporal"]:
        print("❌ No hay capítulos para modificar.")
        return

    mostrar_linea_temporal(sistema)

    try:
        indice = int(input("Número del capítulo a modificar: ")) - 1
    except ValueError:
        print("❌ Debes introducir un número válido.")
        return

    if not (0 <= indice < len(sistema["linea_temporal"])):
        print("❌ Número inválido.")
        return

    cap = sistema["linea_temporal"][indice]
    print(f"\n✏️ Capítulo seleccionado: {cap['titulo']}")

    cap["titulo"] = pedir_str("Nuevo título", cap["titulo"])
    cap["resumen"] = pedir_str("Nuevo resumen", cap["resumen"])
    cap["arco"] = pedir_str("Nuevo arco", cap["arco"])

    estado.cambios_no_guardados = True
    print("✅ Capítulo modificado.")

# --------------------------------------------------
# BORRAR CAPÍTULO
# --------------------------------------------------
def borrar_capitulo(sistema=None):
    sistema = normalizar_linea_temporal(sistema)

    if not sistema["linea_temporal"]:
        print("❌ No hay capítulos para borrar.")
        return

    mostrar_linea_temporal(sistema)

    try:
        indice = int(input("Número del capítulo a eliminar: ")) - 1
    except ValueError:
        print("❌ Debes introducir un número válido.")
        return

    if not (0 <= indice < len(sistema["linea_temporal"])):
        print("❌ Número inválido.")
        return

    cap = sistema["linea_temporal"].pop(indice)
    estado.cambios_no_guardados = True
    print(f"🗑️ Capítulo eliminado: {cap['titulo']}")

    # Desactivar en enciclopedia
    enc = sistema.setdefault("enciclopedias", {}).setdefault("linea_temporal", [])
    for e in enc:
        if e["id"] == cap["id"]:
            e["activo"] = False

# --------------------------------------------------
# MOSTRAR LÍNEA TEMPORAL
# --------------------------------------------------
def mostrar_linea_temporal(sistema=None):
    sistema = normalizar_linea_temporal(sistema)

    print("\n📚 LÍNEA TEMPORAL\n")

    if not sistema["linea_temporal"]:
        print("No hay capítulos todavía.")
        return

    for cap in sistema["linea_temporal"]:
        print(f"[Cap. {cap['id']}] {cap['titulo']}  ({cap['arco']})")
        print(f"   {cap['resumen']}\n")

# --------------------------------------------------
# MENÚ
# --------------------------------------------------
def menu_historia(sistema=None):
    sistema = normalizar_linea_temporal(sistema)

    while True:
        print("\n=== MENÚ DE HISTORIA / CAPÍTULOS ===")
        print("1. Añadir capítulo")
        print("2. Modificar capítulo")
        print("3. Borrar capítulo")
        print("4. Ver línea temporal")
        print("5. Filtros")
        print("6. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            añadir_capitulo(sistema)
        elif opcion == "2":
            modificar_capitulo(sistema)
        elif opcion == "3":
            borrar_capitulo(sistema)
        elif opcion == "4":
            mostrar_linea_temporal(sistema)
        elif opcion == "5":
            menu_filtros_linea_temporal(sistema)
        elif opcion == "6":
            guardar_sistema(sistema)
            break
        else:
            print("❌ Opción no válida.")
