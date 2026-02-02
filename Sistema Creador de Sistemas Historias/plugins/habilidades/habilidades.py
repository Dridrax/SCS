from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.busqueda import buscar
from core.utils.la_gran_enciclopedia import registrar_objeto, desactivar_objeto
import uuid

# ---------- UTILIDADES ----------
def asegurarse_lista(sistema=None):
    sistema = sistema or estado.sistema_actual
    sistema.setdefault("habilidades", [])
    sistema.setdefault("enciclopedias", {}).setdefault("habilidades", [])
    return sistema

def pedir_str(texto, actual=None):
    valor = input(f"{texto} [{actual}]: ")
    return actual if valor == "" else valor

# ---------- MOSTRAR ----------
def mostrar_habilidades(sistema=None):
    sistema = asegurarse_lista(sistema)
    if not sistema["habilidades"]:
        print("No hay habilidades aún.")
        return

    print("\n🛡️ HABILIDADES DEL PERSONAJE\n")
    for i, h in enumerate(sistema["habilidades"], 1):
        print(f"{i}. {h['nombre']} ({h['tipo']})")
        print(f"   Descripción: {h.get('descripcion','')}")
        print(f"   Efectos: {h.get('efectos',{})}\n")

# ---------- BUSCAR ----------
def buscar_habilidades(sistema=None):
    sistema = asegurarse_lista(sistema)
    print("\n🔍 BUSCAR HABILIDADES")

    nombre = input("Nombre (enter para omitir): ")
    tipo = input("Tipo (enter para omitir): ")
    efecto = input("Efecto (enter para omitir): ")

    resultados = buscar(
        sistema["habilidades"],
        nombre=nombre or None,
        tipo=tipo or None,
        efectos=efecto or None
    )

    if not resultados:
        print("❌ No se encontraron habilidades.")
        return

    print(f"\n🛡️ RESULTADOS ({len(resultados)})\n")
    for i, h in enumerate(resultados, 1):
        print(f"{i}. {h['nombre']} ({h['tipo']}) | {h.get('descripcion','')} | {h.get('efectos',{})}")

# ---------- AÑADIR ----------
def añadir_habilidad(sistema=None):
    sistema = asegurarse_lista(sistema)
    print("\n➕ AÑADIR HABILIDAD\n")

    habilidad = {
        "id": str(uuid.uuid4()),
        "nombre": input("Nombre de la habilidad: "),
        "tipo": input("Tipo de habilidad: "),
        "descripcion": input("Descripción: "),
        "efectos": {}
    }

    efectos_input = input("Efectos (ej: Ataque:5,Vida:10): ")
    for parte in efectos_input.split(","):
        if ":" in parte:
            stat, valor = parte.split(":")
            try:
                habilidad["efectos"][stat.strip()] = int(valor.strip())
            except ValueError:
                print(f"⚠️ Ignorado efecto inválido: {parte}")

    sistema["habilidades"].append(habilidad)
    registrar_objeto(sistema, "habilidades", habilidad)
    estado.cambios_no_guardados = True
    print("✅ Habilidad añadida correctamente.")

# ---------- MODIFICAR ----------
def modificar_habilidad(sistema=None):
    sistema = asegurarse_lista(sistema)
    if not sistema["habilidades"]:
        print("❌ No hay habilidades para modificar.")
        return

    mostrar_habilidades(sistema)
    try:
        indice = int(input("Número de la habilidad a modificar: ")) - 1
        h = sistema["habilidades"][indice]

        print(f"\nHabilidad seleccionada: {h['nombre']}")
        h["nombre"] = pedir_str("Nuevo nombre", h["nombre"])
        h["tipo"] = pedir_str("Nuevo tipo", h["tipo"])
        h["descripcion"] = pedir_str("Nueva descripción", h["descripcion"])

        nuevos_efectos = input("Nuevos efectos (ej: Ataque:5,Vida:10, enter para mantener): ")
        if nuevos_efectos:
            h["efectos"] = {}
            for parte in nuevos_efectos.split(","):
                if ":" in parte:
                    stat, valor = parte.split(":")
                    try:
                        h["efectos"][stat.strip()] = int(valor.strip())
                    except ValueError:
                        print(f"⚠️ Ignorado efecto inválido: {parte}")

        registrar_objeto(sistema, "habilidades", h, actualizar=True)
        estado.cambios_no_guardados = True
        print("✅ Habilidad modificada correctamente.")

    except (ValueError, IndexError):
        print("❌ Selección inválida.")

# ---------- ELIMINAR ----------
def eliminar_habilidad(sistema=None):
    sistema = asegurarse_lista(sistema)
    if not sistema["habilidades"]:
        print("❌ No hay habilidades para eliminar.")
        return

    mostrar_habilidades(sistema)
    try:
        indice = int(input("Número de la habilidad a eliminar: ")) - 1
        h = sistema["habilidades"].pop(indice)
        desactivar_objeto(sistema, "habilidades", h["id"])
        estado.cambios_no_guardados = True
        print(f"🗑️ Habilidad eliminada: {h['nombre']}")
    except (ValueError, IndexError):
        print("❌ Selección inválida.")

# ---------- MENÚ ----------
def menu_habilidades(sistema=None):
    sistema = asegurarse_lista(sistema)
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
