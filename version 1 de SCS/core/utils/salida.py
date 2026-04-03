from core.estado_global import estado
from core.guardado.archivos import guardar_sistema

def salir_programa():
    
    if estado.cambios_no_guardados:
        print("⚠️ Hay cambios no guardados.")
        print("1. Guardar y salir")
        print("2. Salir sin guardar")
        print("3. Cancelar")

        opcion_salir = input("Elige una opción: ")

        if opcion_salir == "1":
            try:
                guardar_sistema(estado.sistema_actual)
            except NameError:
                print("❌ No hay sistema cargado para guardar.")
            return True  # salir

        elif opcion_salir == "2":
            print("Saliendo del sistema...")
            return True  # salir sin guardar

        elif opcion_salir == "3":
            return False  # cancelar salida

        else:
            print("❌ Opción no válida. Cancelando salida.")
            return False

    else:
        print("Saliendo del sistema...")
        return True