from core.estado_global import estado
from core.utils.la_gran_enciclopedia import registrar_objeto, desactivar_objeto
import uuid

# ---------- UTILIDADES ----------
def asegurarse_lista(sistema=None):
    sistema = sistema or estado.sistema_actual
    sistema.setdefault("titulos", [])
    sistema.setdefault("enciclopedias", {}).setdefault("titulos", [])
    return sistema

def pedir_str(texto, actual=None):
    valor = input(f"{texto} [{actual}]: ")
    return actual if valor == "" else valor

# ---------- CREAR ----------
def añadir_titulo(sistema=None):
    sistema = asegurarse_lista(sistema)

    print("\n➕ AÑADIR TÍTULO\n")

    titulo = {
        "id": f"titulo_{uuid.uuid4().hex[:8]}",
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

    # 1️⃣ Añadir al sistema activo
    sistema["titulos"].append(titulo)

    # 2️⃣ Registrar en enciclopedia
    registrar_objeto(sistema, "titulos", titulo)

    estado.cambios_no_guardados = True
    print(f"✅ Título '{titulo['nombre']}' añadido correctamente.")

# ---------- MOSTRAR ----------
def mostrar_titulos(sistema=None):
    sistema = asegurarse_lista(sistema)
    if not sistema["titulos"]:
        print("📭 No hay títulos.")
        return

    print("\n🏆 TÍTULOS DEL PERSONAJE\n")
    for t in sistema["titulos"]:
        print(f"- {t['nombre']} ({t['tipo']}): {t['descripcion']}, "
              f"Origen: {t.get('origen','')}, Efectos: {t.get('efectos',{})}")

# ---------- MODIFICAR ----------
def modificar_titulo(sistema=None):
    sistema = asegurarse_lista(sistema)
    if not sistema["titulos"]:
        print("❌ No hay títulos para modificar.")
        return

    for i, t in enumerate(sistema["titulos"], 1):
        print(f"{i}. {t['nombre']} ({t['tipo']})")

    try:
        indice = int(input("Número del título a modificar: ")) - 1
        t = sistema["titulos"][indice]

        print(f"\nTítulo seleccionado: {t['nombre']}")

        t["nombre"] = pedir_str("Nuevo nombre", t["nombre"])
        t["descripcion"] = pedir_str("Nueva descripción", t["descripcion"])
        t["origen"] = pedir_str("Nuevo origen", t["origen"])
        t["tipo"] = pedir_str("Nuevo tipo", t["tipo"])

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

        # Actualizar enciclopedia
        registrar_objeto(sistema, "titulos", t, actualizar=True)

        estado.cambios_no_guardados = True
        print("✅ Título modificado correctamente.")

    except (ValueError, IndexError):
        print("❌ Selección inválida.")

# ---------- ELIMINAR ----------
def eliminar_titulo(sistema=None):
    sistema = asegurarse_lista(sistema)
    if not sistema["titulos"]:
        print("❌ No hay títulos para eliminar.")
        return

    for i, t in enumerate(sistema["titulos"], 1):
        print(f"{i}. {t['nombre']} ({t['tipo']})")

    try:
        indice = int(input("Número del título a eliminar: ")) - 1
        t = sistema["titulos"].pop(indice)

        # Desactivar en enciclopedia
        desactivar_objeto(sistema, "titulos", t["id"])

        estado.cambios_no_guardados = True
        print(f"🗑️ Título eliminado: {t['nombre']}")

    except (ValueError, IndexError):
        print("❌ Selección inválida.")

# ---------- MENÚ ----------
def menu_titulos(sistema=None):
    sistema = asegurarse_lista(sistema)

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
