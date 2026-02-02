from core.estado_global import estado
from core.utils.la_gran_enciclopedia import registrar_objeto, desactivar_objeto
import uuid

# ---------- UTILIDADES ----------
def asegurarse_lista(sistema=None):
    sistema = sistema or estado.sistema_actual
    sistema.setdefault("notas", [])
    sistema.setdefault("enciclopedias", {}).setdefault("notas", [])
    return sistema

def pedir_str(texto, actual=None):
    valor = input(f"{texto} [{actual}]: ")
    return actual if valor == "" else valor

# ---------- CREAR ----------
def crear_nota(sistema=None):
    sistema = asegurarse_lista(sistema)

    print("\n📝 NUEVA NOTA\n")

    nota = {
        "id": f"nota_{uuid.uuid4().hex[:8]}",
        "titulo": input("Título de la nota: "),
        "contenido": input("Contenido: "),
        "archivada": False
    }

    # 1️⃣ Añadir al sistema activo
    sistema["notas"].append(nota)

    # 2️⃣ Registrar en enciclopedia
    registrar_objeto(sistema, "notas", nota)

    estado.cambios_no_guardados = True
    print("✅ Nota creada correctamente.")

# ---------- MOSTRAR ----------
def mostrar_notas(sistema=None, archivadas=False):
    sistema = asegurarse_lista(sistema)
    notas = [n for n in sistema["notas"] if n["archivada"] == archivadas]

    if not notas:
        print("📭 No hay notas para mostrar.")
        return

    for n in notas:
        estado_txt = "📦 ARCHIVADA" if n["archivada"] else ""
        print(f"\n[{n['id']}] {n['titulo']} {estado_txt}")
        print(n["contenido"])

# ---------- EDITAR ----------
def editar_nota(sistema=None):
    sistema = asegurarse_lista(sistema)
    mostrar_notas(sistema, archivadas=False)

    nota_id = input("\nID de la nota a editar: ").strip()
    nota = next((n for n in sistema["notas"] if n["id"] == nota_id), None)

    if not nota:
        print("❌ Nota no encontrada.")
        return

    nota["titulo"] = pedir_str("Nuevo título", nota["titulo"])
    nota["contenido"] = pedir_str("Nuevo contenido", nota["contenido"])

    # Actualizar enciclopedia
    registrar_objeto(sistema, "notas", nota, actualizar=True)
    estado.cambios_no_guardados = True
    print("✅ Nota editada.")

# ---------- ARCHIVAR ----------
def archivar_nota(sistema=None):
    sistema = asegurarse_lista(sistema)
    mostrar_notas(sistema, archivadas=False)

    nota_id = input("\nID de la nota a archivar: ").strip()
    nota = next((n for n in sistema["notas"] if n["id"] == nota_id), None)

    if not nota:
        print("❌ Nota no encontrada.")
        return

    nota["archivada"] = True
    estado.cambios_no_guardados = True
    print("📦 Nota archivada.")

# ---------- ELIMINAR ----------
def borrar_nota(sistema=None):
    sistema = asegurarse_lista(sistema)
    mostrar_notas(sistema, archivadas=True)

    nota_id = input("\nID de la nota a borrar definitivamente: ").strip()
    nota = next((n for n in sistema["notas"] if n["id"] == nota_id), None)

    if not nota or not nota["archivada"]:
        print("❌ Solo se pueden borrar notas archivadas.")
        return

    # 1️⃣ Desactivar en enciclopedia
    desactivar_objeto(sistema, "notas", nota["id"])

    # 2️⃣ Eliminar del sistema activo
    sistema["notas"].remove(nota)

    estado.cambios_no_guardados = True
    print(f"🗑️ Nota eliminada definitivamente: {nota['titulo']}")

# ---------- MENÚ ----------
def menu_notas(sistema=None):
    sistema = asegurarse_lista(sistema)

    while True:
        print("\n=== MENÚ DE NOTAS ===")
        print("1. Crear nota")
        print("2. Ver notas activas")
        print("3. Ver notas archivadas")
        print("4. Editar nota")
        print("5. Archivar nota")
        print("6. Borrar nota archivada")
        print("7. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            crear_nota(sistema)
        elif opcion == "2":
            mostrar_notas(sistema, archivadas=False)
        elif opcion == "3":
            mostrar_notas(sistema, archivadas=True)
        elif opcion == "4":
            editar_nota(sistema)
        elif opcion == "5":
            archivar_nota(sistema)
        elif opcion == "6":
            borrar_nota(sistema)
        elif opcion == "7":
            break
        else:
            print("❌ Opción no válida.")
