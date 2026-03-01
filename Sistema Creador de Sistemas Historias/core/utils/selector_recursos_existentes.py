# core/utils/selector.py

from core.estado_global import estado


# ─────────────────────────────
# OBTENER RECURSOS EXISTENTES
# ─────────────────────────────
def obtener_recursos_existentes(sistema: dict, tipo: str):
    """
    Devuelve los recursos existentes según el tipo.
    Solo lectura. No crea ni modifica nada.
    """

    if not sistema:
        return {}

    # ─────────────
    # OBJETOS
    # ─────────────
    if tipo == "objetos":
        return sistema.get("inventario", {})

    # ─────────────
    # TIPOS CLÁSICOS
    # ─────────────
    mapa_clasicos = {
        "stats": "stats",
        "dinero": "dinero",
        "progress_stats": "progress_stats",
        "puntos_stats": "puntos_stats",
        "puntos_habilidad": "puntos_habilidad",
        "nivel": "niveles",
        "tiradas": "tiradas",
    }

    if tipo in mapa_clasicos:
        return sistema.get(mapa_clasicos[tipo], {})

    # ─────────────
    # RECURSOS DINÁMICOS DEFINIDOS POR USUARIO
    # ─────────────
    recursos_definidos = sistema.get("recursos_definidos", {})
    if tipo in recursos_definidos:
        destino = recursos_definidos[tipo].get("destino", tipo)
        return sistema.get(destino, {})

    return {}
    

# ─────────────────────────────
# MOSTRAR RECURSOS EXISTENTES
# ─────────────────────────────
def mostrar_recursos_existentes(sistema: dict, tipo: str):
    """
    Muestra en pantalla los recursos existentes según el tipo.
    No devuelve nada. Solo imprime.
    """

    existentes = obtener_recursos_existentes(sistema, tipo)

    if not existentes:
        print("\n⚠️ No existen recursos creados aún para este tipo.")
        return

    print("\n=== RECURSOS EXISTENTES ===")

    # ─────────────
    # OBJETOS
    # ─────────────
    if tipo == "objetos":
        for i, item in enumerate(existentes.values(), 1):
            print(
                f"{i}. {item.get('nombre')} | "
                f"Rareza: {item.get('rareza')} | "
                f"Cantidad: {item.get('cantidad')}"
            )
        return

    # ─────────────
    # RESTO DE TIPOS
    # ─────────────
    for i, (clave, info) in enumerate(existentes.items(), 1):

        if isinstance(info, dict):
            valor = info.get("valor_base",
                     info.get("cantidad",
                     info.get("valor", "")))
            print(f"{i}. {clave} ({valor})")
        else:
            print(f"{i}. {clave}")
            

# ─────────────────────────────
# SELECTOR INTERACTIVO
# ─────────────────────────────
def seleccionar_recurso_existente(
    sistema: dict,
    tipo: str,
    permitir_nuevo: bool = True
):
    """
    Permite seleccionar un recurso existente.

    Devuelve:
    - ID si es objeto
    - clave/nombre si es otro tipo
    - None si se quiere crear nuevo
    """

    existentes = obtener_recursos_existentes(sistema, tipo)

    if not existentes:
        return None

    print("\n=== SELECCIONAR RECURSO EXISTENTE ===")

    # ─────────────
    # OBJETOS
    # ─────────────
    if tipo == "objetos":
        objetos_lista = list(existentes.values())

        for i, obj in enumerate(objetos_lista, 1):
            print(
                f"{i}. {obj.get('nombre')} | "
                f"Rareza: {obj.get('rareza')} | "
                f"Cantidad: {obj.get('cantidad')}"
            )

        if permitir_nuevo:
            print("0. Crear nuevo objeto")

        opcion = input("Selecciona opción: ").strip()

        if permitir_nuevo and opcion == "0":
            return None

        if opcion.isdigit():
            idx = int(opcion) - 1
            if 0 <= idx < len(objetos_lista):
                return objetos_lista[idx].get("id")

        print("❌ Selección inválida.")
        return None

    # ─────────────
    # RESTO DE TIPOS
    # ─────────────
    claves = list(existentes.keys())

    for i, nombre in enumerate(claves, 1):
        print(f"{i}. {nombre}")

    if permitir_nuevo:
        print("0. Crear nuevo recurso")

    opcion = input("Selecciona opción: ").strip()

    if permitir_nuevo and opcion == "0":
        return None

    if opcion.isdigit():
        idx = int(opcion) - 1
        if 0 <= idx < len(claves):
            return claves[idx]

    print("❌ Selección inválida.")
    return None