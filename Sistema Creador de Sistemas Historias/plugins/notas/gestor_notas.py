from core.estado_global import estado
import uuid

# ---------- UTIL ----------

def generar_id():
    return f"nota_{uuid.uuid4().hex[:8]}"

def obtener_enciclopedia(sistema):
    return sistema.setdefault("enciclopedias", {}).setdefault("notas", [])

def buscar_nota(enciclopedia, nota_id):
    return next((n for n in enciclopedia if n["id"] == nota_id), None)

# ---------- CREAR ----------

def crear_nota(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    print("\n📝 NUEVA NOTA\n")

    nota = {
        "id": generar_id(),
        "titulo": input("Título de la nota: "),
        "contenido": input("Contenido: "),
        "archivada": False
    }

    enciclopedia = obtener_enciclopedia(sistema)
    enciclopedia.append(nota)

    sistema.setdefault("notas", []).append(nota["id"])

    estado.cambios_no_guardados = True
    print("✅ Nota creada correctamente.")

# ---------- MOSTRAR ----------

def mostrar_notas(sistema=None, archivadas=False):
    if sistema is None:
        sistema = estado.sistema_actual

    ids = sistema.get("notas", [])
    enciclopedia = obtener_enciclopedia(sistema)

    notas = [
        buscar_nota(enciclopedia, nid)
        for nid in ids
        if buscar_nota(enciclopedia, nid)
        and buscar_nota(enciclopedia, nid)["archivada"] == archivadas
    ]

    if not notas:
        print("📭 No hay notas para mostrar.")
        return

    for n in notas:
        estado_txt = "📦 ARCHIVADA" if n["archivada"] else ""
        print(f"\n[{n['id']}] {n['titulo']} {estado_txt}")
        print(n["contenido"])

# ---------- EDITAR ----------

def editar_nota(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    mostrar_notas(sistema, archivadas=False)

    nota_id = input("\nID de la nota a editar: ").strip()
    enciclopedia = obtener_enciclopedia(sistema)
    nota = buscar_nota(enciclopedia, nota_id)

    if not nota:
        print("❌ Nota no encontrada.")
        return

    nota["titulo"] = input(f"Nuevo título [{nota['titulo']}]: ") or nota["titulo"]
    nota["contenido"] = input("Nuevo contenido (enter para mantener): ") or nota["contenido"]

    estado.cambios_no_guardados = True
    print("✅ Nota editada.")

# ---------- ARCHIVAR ----------

def archivar_nota(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    mostrar_notas(sistema, archivadas=False)

    nota_id = input("\nID de la nota a archivar: ").strip()
    nota = buscar_nota(obtener_enciclopedia(sistema), nota_id)

    if not nota:
        print("❌ Nota no encontrada.")
        return

    nota["archivada"] = True
    estado.cambios_no_guardados = True
    print("📦 Nota archivada.")

# ---------- BORRAR ----------

def borrar_nota(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    mostrar_notas(sistema, archivadas=True)

    nota_id = input("\nID de la nota a borrar definitivamente: ").strip()
    enciclopedia = obtener_enciclopedia(sistema)
    nota = buscar_nota(enciclopedia, nota_id)

    if not nota or not nota["archivada"]:
        print("❌ Solo se pueden borrar notas archivadas.")
        return

    enciclopedia.remove(nota)
    sistema["notas"].remove(nota_id)

    estado.cambios_no_guardados = True
    print("🗑️ Nota eliminada definitivamente.")

# ---------- MENÚ ----------

def menu_notas(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

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
