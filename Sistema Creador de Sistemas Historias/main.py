#main.py
from core.estado_global import estado

#utils
from core.utils.salida import salir_programa
from core.utils.funciones_utiles import pedir_int

#menus
from core.menus.menus import (menu_crear_cargar, menu_mostrar,
                              menu_modificar, configuracion)


# ------------------- MENÚ PRINCIPAL -------------------
def menu_principal():
    while True:
        nombre_sistema = estado.sistema_actual.get("nombre_sistema") if estado.sistema_actual else "Sin sistema cargado"
        print(f"\n=== SISTEMA DOC (Sistema actual: {nombre_sistema}) ===\n")
        print("1. Crear/Cargar Sistema")
        print("2. Mostrar Sistema")
        print("3. Modificar Sistema")
        print("4. Configuracion")
        print("5. Salir\n")

        opcion = pedir_int("Elige una opción: ")
        #Crear/Cargar Sistema
        if opcion == 1:
            menu_crear_cargar()
    
        #Mostrar Sistema
        elif opcion == 2:
            menu_mostrar(estado.sistema_actual)

        #Modificar Sistema
        elif opcion == 3:
            menu_modificar(estado.sistema_actual)

        #Configuracion
        elif opcion == 4:
            configuracion(estado.sistema_actual)  

        #Salir
        elif opcion == 5:
            salir_programa()
            break

# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    menu_principal()




