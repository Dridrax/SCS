# core/sistemas/mostrar_sistema.py

def mostrar_stats_completos(sistema):
    """
    Muestra los stats base, los efectos de títulos, bendiciones y maldiciones,
    y el total final, respetando los plugins activos.
    """
    print("\n=== STATS COMPLETOS ===")

    base_stats = sistema.get("stats", {})
    efectos_totales = {}

    plugins = sistema.get("plugins_activos", {})

    # Sumamos efectos de títulos
    if plugins.get("titulos", False):
        for t in sistema.get("titulos", []):
            for stat, valor in t.get("efectos", {}).items():
                efectos_totales[stat] = efectos_totales.get(stat, 0) + valor

    # Sumamos efectos de bendiciones
    if plugins.get("bendiciones", False):
        for b in sistema.get("bendiciones", []):
            for stat, valor in b.get("efectos", {}).items():
                efectos_totales[stat] = efectos_totales.get(stat, 0) + valor

    # Sumamos efectos de maldiciones
    if plugins.get("maldiciones", False):
        for m in sistema.get("maldiciones", []):
            for stat, valor in m.get("efectos", {}).items():
                efectos_totales[stat] = efectos_totales.get(stat, 0) + valor

    # Mostramos stats con efectos
    for stat, base in base_stats.items():
        base_valor = int(base)
        efecto = efectos_totales.get(stat, 0)
        total = base_valor + efecto
        if efecto != 0:
            print(f"- {stat}: {base_valor} (base) + {efecto} (efecto) = {total}")
        else:
            print(f"- {stat}: {base_valor}")


def mostrar_ficha(sistema):
    """
    Muestra toda la ficha del sistema incluyendo stats completos y
    los plugins activos (titulos, bendiciones, maldiciones)
    """
    print("\n=== FICHA DEL SISTEMA ===")
    print(f"Personaje: {sistema['personaje']['nombre']}")
    print(f"Sistema: {sistema.get('nombre_sistema')}")

    # Stats completos
    mostrar_stats_completos(sistema)

    plugins = sistema.get("plugins_activos", {})

    # Inventario
    if plugins.get("inventario", False):
        print("\nINVENTARIO:")
        if sistema.get("inventario"):
            for obj in sistema.get("inventario", []):
                print(f"- {obj.get('nombre', 'Desconocido')} ({obj.get('categoria','')})")
        else:
            print("Vacío.")

    # Habilidades
    if plugins.get("habilidades", False):
        print("\nHABILIDADES:")
        if sistema.get("habilidades"):
            for h in sistema.get("habilidades", []):
                print(f"- {h.get('nombre','Desconocido')} ({h.get('tipo','')})")
        else:
            print("Vacío.")

    # Títulos
    if plugins.get("titulos", False):
        print("\nTÍTULOS:")
        if sistema.get("titulos"):
            for t in sistema.get("titulos", []):
                print(f"- {t.get('nombre','Desconocido')}: {t.get('descripcion','')}")
        else:
            print("Vacío.")

    # Bendiciones
    if plugins.get("bendiciones", False):
        print("\nBENDICIONES:")
        if sistema.get("bendiciones"):
            for b in sistema.get("bendiciones", []):
                print(f"- {b.get('nombre','Desconocido')}: {b.get('descripcion','')} (Efectos: {b.get('efectos', {})})")
        else:
            print("Vacío.")

    # Maldiciones
    if plugins.get("maldiciones", False):
        print("\nMALDICIONES:")
        if sistema.get("maldiciones"):
            for m in sistema.get("maldiciones", []):
                print(f"- {m.get('nombre','Desconocido')}: {m.get('descripcion','')} (Efectos: {m.get('efectos', {})})")
        else:
            print("Vacío.")
