from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int
from .gestor_ruletas import (
    crear_ruleta,
    eliminar_ruleta,
    obtener_ruleta,
    inicializar_ruletas
)
from .modelo_ruleta import RecompensaRuleta
from .tiradas import tirar_ruleta


def menu_ruleta():
    sistema = estado.sistema_actual
    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    inicializar_ruletas(sistema)

    while True:
        print("\n🎰 MENÚ DE RULETAS")
        print("1. Crear ruleta")
        print("2. Eliminar ruleta")
        print("3. Añadir recompensa a ruleta")
        print("4. Tirar ruleta")
        print("0. Volver")

        opcion = input("> ")

        if opcion == "1":
            id_ruleta = input("ID de la ruleta: ")
            nombre = input("Nombre visible: ")
            crear_ruleta(sistema, id_ruleta, nombre)
            print("✅ Ruleta creada.")

        elif opcion == "2":
            id_ruleta = input("ID de la ruleta a eliminar: ")
            eliminar_ruleta(sistema, id_ruleta)
            print("🗑️ Ruleta eliminada.")

        elif opcion == "3":
            id_ruleta = input("ID de la ruleta: ")
            ruleta = obtener_ruleta(sistema, id_ruleta)

            if not ruleta:
                print("❌ Ruleta no encontrada.")
                continue

            print("Introduce la recompensa (formato dict de recompensas SCS)")
            print("Ejemplo: {'stats': {'fuerza': 10}}")
            recompensa = eval(input("> "))

            peso = pedir_int("Peso de salida (>=1): ", minimo=1)

            ruleta.agregar_recompensa(
                RecompensaRuleta(recompensa, peso)
            )
            print("🎁 Recompensa añadida.")

        elif opcion == "4":
            id_ruleta = input("ID de la ruleta: ")
            ruleta = obtener_ruleta(sistema, id_ruleta)

            if not ruleta:
                print("❌ Ruleta no encontrada.")
                continue

            # 🔥 DECISIÓN NARRATIVA DEL ADMIN
            print("\n¿Deseas consumir algo por esta tirada?")
            print("1. No")
            print("2. Sí (decidir manualmente)")

            consumir = input("> ")

            if consumir == "2":
                print("⚠️ Aplica aquí la lógica narrativa que quieras:")
                print("- dinero")
                print("- objeto")
                print("- boleto")
                print("- lo que decida la historia")
                input("Pulsa ENTER cuando lo hayas gestionado narrativamente.")

            recompensa = tirar_ruleta(sistema, ruleta)
            print("🎉 Recompensa obtenida:", recompensa)

        elif opcion == "0":
            break
