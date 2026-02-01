import uuid
# core/utils/la_gran_enciclopedia.py
from core.estado_global import estado
from core.guardado.archivos import guardar_sistema

# ---------- REGISTRAR OBJETO ----------

def registrar_objeto(sistema, tipo, objeto):
    """
    Registra un objeto en la enciclopedia.
    Crea un ID único si no existe.
    """
    if "enciclopedias" not in sistema:
        sistema["enciclopedias"] = {}
    if tipo not in sistema["enciclopedias"]:
        sistema["enciclopedias"][tipo] = []

    # Asignar ID único si no existe
    if "id" not in objeto:
        objeto["id"] = str(uuid.uuid4())

    objeto["activo"] = True  # siempre activo al registrar
    sistema["enciclopedias"][tipo].append(objeto)


# ---------- DESACTIVAR OBJETO ----------
def desactivar_objeto(sistema, tipo, id_objeto):
    """
    Desactiva un objeto en la enciclopedia según su tipo y id.
    """
    for obj in sistema.get("enciclopedias", {}).get(tipo, []):
        if obj.get("id") == id_objeto:
            obj["activo"] = False
            return True
    return False


# ---------- REACTIVAR OBJETO ----------

def reactivar_objeto(sistema, tipo, id_objeto):
    """
    Reactiva un objeto en la enciclopedia según su tipo y id.
    """
    for obj in sistema.get("enciclopedias", {}).get(tipo, []):
        if obj.get("id") == id_objeto:
            obj["activo"] = True
            return True
    return False


# ---------- LISTAR ENCICLOPEDIA ----------

def gestionar_enciclopedia_tipo(tipo):
    sistema = estado.sistema_actual
    enciclopedia = sistema.get("enciclopedias", {}).get(tipo, [])

    while True:
        print(f"\n=== ENCICLOPEDIA: {tipo.upper()} ===")

        for i, obj in enumerate(enciclopedia, 1):
            estado_str = "Activo ✅" if obj.get("activo", True) else "Inactivo ❌"
            print(
                f"{i}. {obj['nombre']} "
                f"({obj.get('clase', '')} | {obj.get('categoria', '')}) - {estado_str}"
            )

        print(f"{len(enciclopedia) + 1}. Volver")

        try:
            opcion = int(input("Selecciona un objeto para activar/desactivar: "))
        except ValueError:
            print("❌ Opción inválida.")
            continue

        if opcion == len(enciclopedia) + 1:
            break

        if not (1 <= opcion <= len(enciclopedia)):
            print("❌ Opción inválida.")
            continue

        obj = enciclopedia[opcion - 1]

        # ======================================================
        # DESACTIVAR OBJETO
        # ======================================================
        if obj.get("activo", True):
            desactivar_objeto(sistema, tipo, obj["id"])

            # ⚠️ AQUÍ va la lógica específica del sistema
            # Si el tipo tiene una lista activa (inventario, habilidades, etc.)
            # se elimina por ID (NUNCA por pop directo)
            if tipo == "inventario":
                sistema["inventario"] = [
                    i for i in sistema.get("inventario", [])
                    if i.get("id") != obj["id"]
                ]

            # 🔹 EJEMPLOS FUTUROS (NO IMPLEMENTADOS)
            # if tipo == "habilidades":
            #     sistema["habilidades"] = [...]
            #
            # if tipo == "tienda":
            #     sistema["tienda_activa"] = [...]

            estado.cambios_no_guardados = True
            print(f"❌ '{obj['nombre']}' desactivado.")

        # ======================================================
        # REACTIVAR OBJETO
        # ======================================================
        else:
            reactivar_objeto(sistema, tipo, obj["id"])

            # Volver a añadir al sistema activo si aplica
            if tipo == "inventario":
                sistema.setdefault("inventario", []).append(obj)

            # 🔹 EJEMPLOS FUTUROS
            # if tipo == "habilidades":
            #     sistema.setdefault("habilidades", []).append(obj)

            estado.cambios_no_guardados = True
            print(f"✅ '{obj['nombre']}' reactivado.")



def listar_enciclopedia(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    # Asegurarse que enciclopedias es un diccionario
    enciclopedias = sistema.get("enciclopedias")
    if not isinstance(enciclopedias, dict):
        print("❌ ERROR: La clave 'enciclopedias' no está correctamente inicializada.")
        sistema["enciclopedias"] = {}
        enciclopedias = sistema["enciclopedias"]

    while True:
        print("\n=== LA GRAN ENCICLOPEDIA ===")
        tipos = list(enciclopedias.keys())
        for i, t in enumerate(tipos, 1):
            print(f"{i}. {t.capitalize()}")
        print(f"{len(tipos)+1}. Volver")

        try:
            opcion = int(input("Elige una sección: "))
        except ValueError:
            print("❌ Opción inválida.")
            continue

        if opcion == len(tipos)+1:
            break
        elif 1 <= opcion <= len(tipos):
            gestionar_enciclopedia_tipo(tipos[opcion-1])
        else:
            print("❌ Opción inválida.")
