from core.estado_global import estado
from core.stats.stats import mostrar_stats, mostrar_progress_stats_bar

def que_ficha_queres(sistema):
        
    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    opcion = input("\n¿Mostrar Ficha [S]imple o [C]ompleta?: ").lower()

    if opcion == "s":
        mostrar_ficha_simple(sistema)
    elif opcion == "c":
        mostrar_ficha_completo(sistema)
    else:
        print("n❌ Opcion no valida.")


def mostrar_ficha_simple(sistema):
    """
    Muestra la ficha simple de un sistema.
    Incluye:
    - Nombre del Personaje y Nombre del sistema
    - Nivel (Si esta activado Plugin: Niveles)
    - Stats simple
    - Stats Progress
    - Puntos de Stats
    - Historia
    """

    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    print("\n=== FICHA DEL SISTEMA ===")

    # --- PERSONAJE Y NOMBRE DEL SISTEMA ---
    personaje = sistema.get("personaje", {})
    nombre_personaje = personaje.get("nombre", "Sin nombre")
    nombre_sistema = sistema.get("nombre_sistema", "Sin nombre")
    puntos_stats = sistema.get("puntos_stats")

    print(f"    > Personaje: {nombre_personaje} | Sistema: {nombre_sistema}")

    # --- STATS SIMPLES ---
    mostrar_stats(sistema)  # muestra stats simples y de progreso juntos

    # --- PROGRESS STATS (opcional si quieres usar función modular) ---
    # mostrar_progress_stats(sistema.get("progress_stats", {}))
    mostrar_progress_stats_bar(sistema.get("progress_stats", {}))

    print(f"\nPuntos Stats: {puntos_stats}")
    
    # --- HISTORIA ---
    historia = sistema.get("historia", {})
    if historia:
        print("\n-- TIPO DE HISTORIA --\n")
        tipo = historia.get("tipo")
        if tipo == "original":  # original
            print(f"    > Tipo: Original")
            print(f"    > Protagonista: {historia.get('protagonista', 'N/A')}")
            print(f"    > Personajes principales: {historia.get('personajes_principales', 'N/A')}")
            print(f"    > Parejas: {historia.get('parejas', 'N/A')}")
            print(f"\n    > Sinopsis: {historia.get('sinopsis', 'N/A')}")

        elif tipo == "fanfiction":  # fanfiction
            print(f"    > Tipo: Fanfiction")
            print(f"    > Fandom: {historia.get('fandom', 'N/A')}")
            print(f"    > Protagonista: {historia.get('protagonista', 'N/A')}")
            print(f"    > Personajes principales: {historia.get('personajes_principales', 'N/A')}")
            print(f"    > Personajes: {historia.get('personajes', 'N/A')}")
            print(f"    > Parejas: {historia.get('parejas', 'N/A')}")
            print(f"\n    > Sinopsis: {historia.get('sinopsis', 'N/A')}")

        else:
            print("Tipo de historia no definido")
    else:
        print("\nNo hay historia registrada para este sistema.")

def mostrar_ficha_completo(sistema):
    """
    Muestra la ficha simple de un sistema.
    Incluye:
    - Nombre del Personaje y Nombre del sistema
    - Stats simple
    - Stats Progress
    - Puntos de Stats
    - Inventario (Si esta activado Plugin: Inventario)
    - Misiones (Si esta activado Plugin: Misiones)
    - Rachas (Si esta activado Plugin: Racha)
    - Nivel (Si esta activado Plugin: Niveles)
    - Historia
    """
    
    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    mostrar_ficha_simple(sistema)

    print("\n¡¡¡¡¡¡AUN EN CREACION!!!!!!!")


"""def mostrar_stats_completos(sistema):
 
    Muestra los stats base, los efectos de títulos, bendiciones y maldiciones,
    y el total final, respetando los plugins activos.
   
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
            print(f"- {stat}: {base_valor}")"""


"""def mostrar_ficha(sistema):

    Muestra toda la ficha del sistema incluyendo stats completos y
    los plugins activos (titulos, bendiciones, maldiciones)
    
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
            print("Vacío.")"""
