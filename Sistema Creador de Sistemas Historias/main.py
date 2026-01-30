from estado_global import estado

from sistemas.crear_sistema import crear_nuevo_sistema
from sistemas.mostrar_sistema import mostrar_ficha

from inventario.inventario import menu_inventario, mostrar_inventario
from stats.stats import menu_stats, mostrar_stats
from historia.linea_temporal import menu_historia, mostrar_linea_temporal
from titulos.titulos import menu_titulos, mostrar_titulos
from maldiciones.maldiciones import menu_maldiciones, mostrar_maldiciones
from bendiciones.bendiciones import menu_bendiciones, mostrar_bendiciones

from guardado.archivos import guardar_sistema, cargar_sistema, guardar_como
from utils.salida import salir_programa
from utils.exportar_pdf import exportar_ficha_pdf


# ------------------- MENÚ PRINCIPAL -------------------
def menu_principal():
    while True:
        nombre_sistema = estado.sistema_actual.get("nombre_sistema") if estado.sistema_actual else "Sin sistema cargado"
        print(f"\n=== SISTEMA DOC (Sistema actual: {nombre_sistema}) ===")
        print("1. Crear / Cargar Sistema")
        print("2. Guardar Sistema")
        print("3. Gestión del Sistema")
        print("4. Exportar Ficha a PDF")
        print("5. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            menu_crear_cargar()
        elif opcion == "2":
            menu_guardado()
        elif opcion == "3":
            if estado.sistema_actual:
                menu_gestion_sistema()
            else:
                print("❌ No hay ningún sistema cargado.")
        elif opcion == "4":
            if estado.sistema_actual:
                exportar_ficha_pdf(estado.sistema_actual)
            else:
                print("❌ No hay ningún sistema cargado.")
        elif opcion == "5":
            if salir_programa():
                break
        else:
            print("❌ Opción no válida.")


# ------------------- CREAR / CARGAR -------------------
def menu_crear_cargar():
    while True:
        print("\n=== CREAR / CARGAR ===")
        print("1. Crear Nuevo Sistema/Personaje")
        print("2. Cargar Sistema/Personaje")
        print("3. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            estado.sistema_actual = crear_nuevo_sistema()
            estado.archivo_actual = None
            mostrar_ficha(estado.sistema_actual)
            if input("\n¿Deseas guardar este sistema? (s/n): ").lower() == "s":
                guardar_sistema()
        elif opcion == "2":
            archivo = input("Nombre del archivo a cargar: ")
            sistema = cargar_sistema(archivo)
            if sistema:
                # Normalización de sistemas antiguos
                for clave in ["inventario", "habilidades", "titulos", "bendiciones", "maldiciones", "linea_temporal", "historia"]:
                    sistema.setdefault(clave, [] if clave != "historia" else {})
                estado.sistema_actual = sistema
                mostrar_ficha(estado.sistema_actual)
        elif opcion == "3":
            break
        else:
            print("❌ Opción no válida.")


# ------------------- GUARDADO -------------------
def menu_guardado():
    if not estado.sistema_actual:
        print("❌ No hay ningún sistema cargado.")
        return

    while True:
        print("\n=== GUARDAR SISTEMA ===")
        print("1. Guardar")
        print("2. Guardar Como")
        print("3. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            guardar_sistema()
        elif opcion == "2":
            guardar_como()
        elif opcion == "3":
            break
        else:
            print("❌ Opción no válida.")


# ------------------- GESTIÓN DEL SISTEMA -------------------
def menu_gestion_sistema():
    while True:
        nombre = estado.sistema_actual.get("nombre_sistema") if estado.sistema_actual else "Sin sistema"
        print(f"\n=== GESTIÓN DEL SISTEMA ({nombre}) ===")
        print("1. Inventario")
        print("2. Stats")
        print("3. Títulos / Bendiciones / Maldiciones")
        print("4. Historia / Capítulos")
        print("5. Cambiar Parámetros (modificar)")
        print("6. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mostrar_inventario(estado.sistema_actual)
        elif opcion == "2":
            mostrar_stats(estado.sistema_actual)
        elif opcion == "3":
            mostrar_titulos(estado.sistema_actual)
            mostrar_bendiciones(estado.sistema_actual)
            mostrar_maldiciones(estado.sistema_actual)
        elif opcion == "4":
            mostrar_linea_temporal(estado.sistema_actual)
        elif opcion == "5":
            menu_modificar_sistema()
        elif opcion == "6":
            break
        else:
            print("❌ Opción no válida.")


# ------------------- MODIFICAR SISTEMA -------------------
def menu_modificar_sistema():
    while True:
        print("\n=== MODIFICAR SISTEMA ===")
        print("1. Modificar Inventario")
        print("2. Modificar Stats")
        print("3. Modificar Títulos / Bendiciones / Maldiciones")
        print("4. Modificar Historia / Capítulos")
        print("5. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            menu_inventario(estado.sistema_actual)
        elif opcion == "2":
            menu_stats(estado.sistema_actual)
        elif opcion == "3":
            menu_modificar_tbm()
        elif opcion == "4":
            menu_historia(estado.sistema_actual)
        elif opcion == "5":
            break
        else:
            print("❌ Opción no válida.")


# ------------------- MODIFICAR T/B/M -------------------
def menu_modificar_tbm():
    while True:
        print("\n=== MODIFICAR T/B/M ===")
        print("1. Títulos")
        print("2. Bendiciones")
        print("3. Maldiciones")
        print("4. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            menu_titulos(estado.sistema_actual)
        elif opcion == "2":
            menu_bendiciones(estado.sistema_actual)
        elif opcion == "3":
            menu_maldiciones(estado.sistema_actual)
        elif opcion == "4":
            break
        else:
            print("❌ Opción no válida.")


# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    menu_principal()
