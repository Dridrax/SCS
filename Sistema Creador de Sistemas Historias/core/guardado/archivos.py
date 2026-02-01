import json
import os
from core.estado_global import estado

# ===============================
# GUARDAR SISTEMA
# ===============================
def guardar_sistema(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if sistema is None:
        print("❌ No hay sistema cargado para guardar.")
        return

    if estado.archivo_actual:
        nombre_archivo = estado.archivo_actual
    else:
        nombre_archivo = input("Nombre del archivo para guardar (ej: Sistema Yue.json): ")

    # Asegurarnos de que tenga extensión .json
    if not nombre_archivo.endswith(".json"):
        nombre_archivo += ".json"

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(sistema, archivo, indent=4, ensure_ascii=False)

    estado.archivo_actual = nombre_archivo
    estado.cambios_no_guardados = False
    print(f"✅ Sistema guardado correctamente en '{nombre_archivo}'")


# ===============================
# CARGAR SISTEMA
# ===============================
def cargar_sistema(nombre_archivo=None):
    if nombre_archivo is None:
        nombre_archivo = input("Nombre del archivo a cargar: ")

    if not nombre_archivo.endswith(".json"):
        nombre_archivo += ".json"

    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            sistema = json.load(f)

        # Validar estructura mínima
        claves_minimas = ["personaje", "nombre_sistema", "stats"]
        for clave in claves_minimas:
            if clave not in sistema:
                print(f"❌ El archivo '{nombre_archivo}' no es compatible (falta {clave}).")
                return None

        # Normalizar listas que podrían faltar
        for clave in ["inventario", "habilidades", "titulos", "bendiciones", "maldiciones", "linea_temporal", "historia"]:
            if clave not in sistema:
                if clave == "historia":
                    sistema[clave] = {}
                else:
                    sistema[clave] = []

        estado.sistema_actual = sistema
        estado.archivo_actual = nombre_archivo
        estado.cambios_no_guardados = False
        print(f"✅ Sistema cargado correctamente desde '{nombre_archivo}'")
        return sistema

    except FileNotFoundError:
        print(f"❌ Archivo '{nombre_archivo}' no encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"❌ El archivo '{nombre_archivo}' no es un sistema válido.")
        return None


# ===============================
# GUARDAR COMO
# ===============================
def guardar_como(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if sistema is None:
        print("❌ No hay sistema cargado para guardar.")
        return

    nombre_archivo = input("Nombre del nuevo archivo para guardar este sistema: ")
    if not nombre_archivo.endswith(".json"):
        nombre_archivo += ".json"

    if os.path.exists(nombre_archivo):
        print(f"❗ El archivo '{nombre_archivo}' ya existe.")
        print("1. Sobrescribir")
        print("2. Cancelar")
        opcion = input("Elige una opción: ")
        if opcion != "1":
            print("⚠️ Operación cancelada.")
            return

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(sistema, archivo, indent=4, ensure_ascii=False)

    estado.archivo_actual = nombre_archivo
    estado.cambios_no_guardados = False
    print(f"✅ Sistema guardado como '{nombre_archivo}'")
