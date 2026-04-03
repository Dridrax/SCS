from core.estado_global import estado
from core.administrar_puntos.puntos import (consultar_puntos_stats, gastar_puntos_stats)

def menu_distribuir_puntos(sistema=None):
    """
    Menú para gastar puntos_stats en stats simples o progress stats.
    """
    if sistema is None:
        sistema = estado.sistema_actual
    if sistema is None:
        print("❌ No hay sistema cargado.")
        return

    if consultar_puntos_stats(sistema) <= 0:
        print("❌ No hay puntos para distribuir.")
        return

    while True:
        print("\n=== DISTRIBUIR PUNTOS ===")
        print(f"Puntos disponibles: {consultar_puntos_stats(sistema)}")
        print("1. Stats Simples")
        print("2. Progress Stats")
        print("0. Volver")

        opcion = input("\nElige una opción: ").strip()
        if opcion == "0":
            break
        elif opcion == "1":
            _distribuir_a_stat_simple(sistema)
        elif opcion == "2":
            _distribuir_a_progress_stat(sistema)
        else:
            print("❌ Opción inválida.")


def _distribuir_a_stat_simple(sistema):
    stats = sistema.get("stats", {})
    if not stats:
        print("❌ No hay stats simples.")
        return

    print("\nStats disponibles:")
    for stat in stats:
        print(f"- {stat} ({stats[stat]})")

    nombre = input("\nNombre del stat a mejorar: ").strip()
    if nombre not in stats:
        print("❌ Ese stat no existe.")
        return

    try:
        puntos = int(input(f"\nCantidad de puntos a gastar ({consultar_puntos_stats(sistema)}): "))
    except ValueError:
        print("❌ Debes introducir un número.")
        return

    if gastar_puntos_stats(puntos, sistema):
        stats[nombre] += puntos
        print(f"✅ {nombre} incrementado en {puntos} puntos.")
    else:
        print("❌ No hay suficientes puntos.")

def _distribuir_a_progress_stat(sistema):
    progress_stats = sistema.get("progress_stats", {})
    if not progress_stats:
        print("❌ No hay stats de progreso.")
        return

    print("\nProgress stats disponibles:")
    for stat, datos in progress_stats.items():
        print(f"- {stat}: {datos.get('actual',0)}/{datos.get('max',0)} Nivel {datos.get('nivel',1)}")

    nombre = input("\nNombre del stat a mejorar: ").strip()
    if nombre not in progress_stats:
        print("❌ Ese stat no existe.")
        return

    try:
        puntos = int(input(f"\nCantidad de puntos a gastar ({consultar_puntos_stats(sistema)}): "))
    except ValueError:
        print("❌ Debes introducir un número.")
        return

    if gastar_puntos_stats(puntos, sistema):
        from core.utils.funciones_utiles import modificar_progreso
        modificar_progreso(progress_stats[nombre], puntos)
        print(f"✅ {nombre} incrementado en {puntos} puntos de progreso.")
    else:
        print("❌ No hay suficientes puntos.")