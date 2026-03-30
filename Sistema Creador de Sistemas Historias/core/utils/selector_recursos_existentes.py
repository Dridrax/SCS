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
def mostrar_recursos_existentes(sistema: dict, tipo: str, bloque_actual: dict = None):
    """
    Muestra en pantalla los recursos existentes según el tipo.
    Incluye recursos recién agregados en el bloque actual.
    ⚡ No muestra advertencia si el bloque está vacío recién creado.
    """
    existentes = obtener_recursos_existentes(sistema, tipo)

    # ⚡ Combinar con bloque_actual si existe
    if bloque_actual:
        bloque_tipo = bloque_actual.get(tipo)
        if bloque_tipo:
            if isinstance(existentes, dict) and isinstance(bloque_tipo, dict):
                existentes = {**existentes, **bloque_tipo}
            elif isinstance(existentes, dict) and isinstance(bloque_tipo, list):
                existentes = list(existentes.values()) + bloque_tipo
            elif isinstance(existentes, list) and isinstance(bloque_tipo, list):
                existentes = existentes + bloque_tipo

    # ⚡ Detectar si el bloque es nuevo y vacío
    bloque_vacio = bloque_actual is not None and not bool(bloque_actual)

    if not existentes:
        # Mostrar advertencia solo si NO es bloque recién creado
        if not bloque_vacio:
            print("\n⚠️ No existen recursos creados aún para este tipo.")
        return

    print("\n=== RECURSOS EXISTENTES ===")

    # ─────────────
    # OBJETOS
    # ─────────────
    if tipo == "objetos":
        lista_items = existentes if isinstance(existentes, list) else list(existentes.values())
        for i, item in enumerate(lista_items, 1):
            nombre = item.get("nombre", "???")
            cantidad = item.get("cantidad", item.get("cantidad_base", 0))
            rareza = item.get("rareza", "")
            print(f"{i}. {nombre} | Cantidad: {cantidad} | Rareza: {rareza}")
        return

    # ─────────────
    # RESTO DE TIPOS
    # ─────────────
    if isinstance(existentes, dict):
        for i, (clave, info) in enumerate(existentes.items(), 1):
            if isinstance(info, dict):
                valor = info.get("valor_base",
                         info.get("cantidad",
                         info.get("valor", "")))
                print(f"{i}. {clave} ({valor})")
            else:
                print(f"{i}. {clave}")
    elif isinstance(existentes, int):
        print(f"Cantidad: {existentes}")
    else:
        print(existentes)

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