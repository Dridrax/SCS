from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.busqueda import buscar
import uuid


# ---------- MOSTRAR ----------
def mostrar_habilidades(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n🛡️ HABILIDADES DEL PERSONAJE\n")

    if not sistema.get("habilidades"):
        print("No hay habilidades aún.")
        return

    for i, h in enumerate(sistema["habilidades"], 1):
        print(f"{i}. {h['nombre']}")
        print(f"   Tipo: {h['tipo']}")
        print(f"   Descripción: {h.get('descripcion', '')}")
        print(f"   Efectos: {h.get('efectos','')}\n")


# ---------- BUSCAR ----------
def buscar_habilidades(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n🔍 BUSCAR HABILIDADES")

    nombre = input("Nombre (enter para omitir): ")
    tipo = input("Tipo (enter para omitir): ")
    efecto = input("Efecto (enter para omitir): ")

    resultados = buscar(
        sistema.get("habilidades", []),
        nombre=nombre or None,
        tipo=tipo or None,
        efectos=efecto or None
    )

    if not resultados:
        print("❌ No se encontraron habilidades.")
        return

    print(f"\n🛡️ RESULTADOS ({len(resultados)})\n")
    for h in resultados:
        print(f"- {h['nombre']} ({h['tipo']}) | {h.get('descripcion','')} | {h.get('efectos','')}")


# ---------- AÑADIR ----------
def añadir_habilidad(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n➕ AÑADIR HABILIDAD\n")

    habilidad = {
        "id": str(uuid.uuid4()),
        "nombre": input("Nombre de la habilidad: "),
        "tipo": input("Tipo de habilidad: "),
        "descripcion": input("Descripción: "),
        "efectos": input("Efectos: ")
    }

    sistema.setdefault("habilidades", []).append(habilidad)
    estado.cambios_no_guardados = True

    # Enciclopedia
    enciclopedia = sistema.setdefault("enciclopedias", {}).setdefault("habilidades", [])
    enciclopedia.append({**habilidad, "activo": True})

    print("✅ Habilidad añadida correctamente.")


# ---------- MODIFICAR ----------
def modificar_habilidad(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema.get("habilidades"):
        print("❌ No hay habilidades para modificar.")
        return

    mostrar_habilidades(sistema)

    try:
        indice = int(input("Número de la habilidad a modificar: ")) - 1
        h = sistema["habilidades"][indice]
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return

    print(f"\nHabilidad seleccionada: {h['nombre']}")

    h["nombre"] = input("Nuevo nombre (enter): ") or h["nombre"]
    h["tipo"] = input("Nuevo tipo (enter): ") or h["tipo"]
    h["descripcion"] = input("Nueva descripción (enter): ") or h["descripcion"]
    h["efectos"] = input("Nuevos efectos (enter): ") or h["efectos"]

    # Enciclopedia
    enciclopedia = sistema.setdefault("enciclopedias", {}).setdefault("habilidades", [])
    for e in enciclopedia:
        if e["id"] == h["id"]:
            e.update(h)
            e["activo"] = True

    estado.cambios_no_guardados = True
    print("✅ Habilidad modificada correctamente.")


# ---------- ELIMINAR ----------
def eliminar_habilidad(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema.get("habilidades"):
        print("❌ No hay habilidades para eliminar.")
        return

    mostrar_habilidades(sistema)

    try:
        indice = int(input("Número de la habilidad a eliminar: ")) - 1
        h = sistema["habilidades"].pop(indice)
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return

    # Enciclopedia
    enciclopedia = sistema.setdefault("enciclopedias", {}).setdefault("habilidades", [])
    for e in enciclopedia:
        if e["id"] == h["id"]:
            e["activo"] = False

    estado.cambios_no_guardados = True
    print(f"🗑️ Habilidad eliminada: {h['nombre']}")


# ---------- MENÚ ----------
def menu_habilidades(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    while True:
        print("\n=== MENÚ DE HABILIDADES ===")
        print("1. Ver habilidades")
        print("2. Buscar habilidad 🔍")
        print("3. Añadir habilidad")
        print("4. Modificar habilidad")
        print("5. Eliminar habilidad")
        print("6. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_habilidades(sistema)
        elif opcion == "2":
            buscar_habilidades(sistema)
        elif opcion == "3":
            añadir_habilidad(sistema)
        elif opcion == "4":
            modificar_habilidad(sistema)
        elif opcion == "5":
            eliminar_habilidad(sistema)
        elif opcion == "6":
            guardar_sistema(sistema)
            break
        else:
            print("❌ Opción no válida.")
