def mostrar_stats_completos(sistema):
    """
    Muestra los stats base, los efectos de títulos, bendiciones y maldiciones, y el total.
    """
    print("\n📊 STATS COMPLETOS\n")

    # Efectos combinados
    efectos_totales = {}

    # Sumamos efectos de títulos
    for t in sistema.get("titulos", []):
        for stat, valor in t.get("efectos", {}).items():
            efectos_totales[stat] = efectos_totales.get(stat, 0) + valor

    # Sumamos efectos de bendiciones
    for b in sistema.get("bendiciones", []):
        for stat, valor in b.get("efectos", {}).items():
            efectos_totales[stat] = efectos_totales.get(stat, 0) + valor

    # Sumamos efectos de maldiciones
    for m in sistema.get("maldiciones", []):
        for stat, valor in m.get("efectos", {}).items():
            efectos_totales[stat] = efectos_totales.get(stat, 0) + valor

    # Mostramos stats
    for stat, base in sistema.get("stats", {}).items():
        base_valor = int(base)
        efecto = efectos_totales.get(stat, 0)
        total = base_valor + efecto
        if efecto != 0:
            print(f"- {stat}: {base_valor} + ({efecto}) = {total}")
        else:
            print(f"- {stat}: {base_valor}")


def mostrar_ficha(sistema):
    """Muestra toda la ficha del sistema"""

    # Aseguramos que las listas existan para evitar errores
    for clave in ["titulos", "bendiciones", "maldiciones", "inventario", "habilidades", "linea_temporal"]:
        if clave not in sistema:
            sistema[clave] = []

    print("\n\n===== FICHA DEL SISTEMA =====\n")

    # Personaje
    print(f"Personaje: {sistema.get('personaje', {}).get('nombre','Desconocido')}")

    # Nombre del sistema
    if sistema.get("nombre_sistema"):
        print(f"Sistema: {sistema['nombre_sistema']}")

    # Stats
    print("\nSTATS:")
    mostrar_stats_completos(sistema)

    # Inventario
    print("\nINVENTARIO:")
    if sistema["inventario"]:
        for obj in sistema["inventario"]:
            print(f"- {obj.get('nombre','Desconocido')} ({obj.get('categoria','')})")
    else:
        print("Vacío.")

    # Habilidades
    print("\nHABILIDADES:")
    if sistema["habilidades"]:
        for h in sistema["habilidades"]:
            print(f"- {h.get('nombre','Desconocido')} ({h.get('tipo','')})")
    else:
        print("Vacío.")

    # Títulos
    print("\nTÍTULOS:")
    if sistema["titulos"]:
        for t in sistema["titulos"]:
            print(f"- {t.get('nombre','Desconocido')}")
    else:
        print("Vacío.")

    # Bendiciones
    print("\nBENDICIONES:")
    if sistema["bendiciones"]:
        for b in sistema["bendiciones"]:
            print(f"- {b.get('nombre','Desconocido')}")
    else:
        print("Vacío.")

    # Maldiciones
    print("\nMALDICIONES:")
    if sistema["maldiciones"]:
        for m in sistema["maldiciones"]:
            print(f"- {m.get('nombre','Desconocido')}")
    else:
        print("Vacío.")

    # Historia
    print("\nHISTORIA:")
    if sistema["linea_temporal"]:
        for cap in sistema["linea_temporal"]:
            print(f"- {cap.get('titulo','Desconocido')}: {cap.get('resumen','')}")
    else:
        print("Vacío.")
