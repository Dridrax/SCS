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
    Muestra la ficha completa del sistema incluyendo todos los plugins activos.
    """

    if not sistema:
        print("\n❌ No hay sistema cargado.")
        return

    # ------------------- BASE -------------------
    mostrar_ficha_simple(sistema)

    plugins = sistema.get("plugins_activos", {})

    # ------------------- RECURSOS -------------------
    print("\n-- RECURSOS --\n")

    print(f"    > Puntos Stats: {sistema.get('puntos_stats', 0)}")
    print(f"    > Puntos Habilidad: {sistema.get('puntos_habilidad', 0)}")

    dinero = sistema.get("dinero", {})
    if dinero:
        print("\n    > Dinero:")
        for tipo, cantidad in dinero.items():
            print(f"        - {tipo}: {cantidad}")

    tiradas = sistema.get("tiradas", {})
    if tiradas:
        print("\n    > Tiradas:")
        for tipo, cantidad in tiradas.items():
            print(f"        - {tipo}: {cantidad}")

    # ------------------- NIVELES -------------------
    if plugins.get("niveles", False):
        print("\n-- NIVELES --\n")
        niveles = sistema.get("niveles", {})

        print(f"    > Nivel: {niveles.get('nivel', 0)}")
        print(f"    > XP: {niveles.get('xp_actual', 0)} / {niveles.get('xp_para_siguiente', 0)}")

    # ------------------- INVENTARIO -------------------
    if plugins.get("inventario", False):
        print("\n-- INVENTARIO --\n")
        inventario = sistema.get("inventario", {})

        if not inventario:
            print("    (Inventario vacío)")
        else:
            for item in inventario.values():
                print(f"    > {item['nombre']} x{item['cantidad']} [{item['rareza']}]")

    # ------------------- MISIONES -------------------
    if plugins.get("misiones", False):
        print("\n-- MISIONES ACTIVAS --\n")
        misiones = sistema.get("misiones", {}).get("activas", {})

        if not misiones:
            print("    (No hay misiones activas)")
        else:
            for m in misiones.values():
                print(f"    > {m.get('nombre', 'Sin nombre')}")
                
                for obj in m.get("objetivos", []):
                    progreso = obj.get("progreso", 0)
                    total = obj.get("cantidad_base", 0)
                    print(f"        - {obj.get('descripcion', '')}: {progreso}/{total}")

    # ------------------- RACHAS -------------------
    if plugins.get("rachas", False):
        print("\n-- RACHAS ACTIVAS --\n")
        rachas = sistema.get("rachas", {}).get("activas", {})

        if not rachas:
            print("    (No hay rachas)")
        else:
            for r in rachas.values():
                print(f"    > {r.get('nombre')} (Completada: {r.get('veces_completada', 0)} veces)")
                
                for obj in r.get("objetivos", []):
                    print(f"        - {obj.get('descripcion')} ({obj.get('progreso', 0)})")

    # ------------------- RULETA -------------------
    if plugins.get("ruleta", False):
        print("\n-- RULETAS --\n")
        ruletas = sistema.get("ruleta", {}).get("activas", {})

        if not ruletas:
            print("    (No hay ruletas)")
        else:
            for r in ruletas.values():
                print(f"    > {r.get('nombre')}")
                print(f"        - Tiradas realizadas: {r.get('tiradas_realizadas', 0)}")
                print(f"        - Premios: {len(r.get('premios', {}))} tipos")

    print("\n=== FIN DE FICHA COMPLETA ===")