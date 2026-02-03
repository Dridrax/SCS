from core.estado_global import estado

from core.guardado.archivos import guardar_sistema, cargar_sistema, guardar_como

#utils
from core.utils.salida import salir_programa
from core.utils.funciones_utiles import pedir_int, pedir_si_no

#menus
from core.menus.menus import menu_crear_cargar, menu_guardado, menu_mostrar, menu_modificar


# ------------------- MENÚ PRINCIPAL -------------------
def menu_principal():
    while True:
        nombre_sistema = estado.sistema_actual.get("nombre_sistema") if estado.sistema_actual else "Sin sistema cargado"
        print(f"\n=== SISTEMA DOC (Sistema actual: {nombre_sistema}) ===\n")
        print("1. Crear/Cargar Sistema")
        print("2. Mostrar Sistema")
        print("3. Modificar Sistema")
        #print("Activar/Desactivar Plugins.)
        print("4. Salir/Guardar\n")

        opcion = pedir_int("Elige una opción: ")
        if opcion == 1:
            menu_crear_cargar()
        elif opcion == 2:
            menu_mostrar(estado.sistema_actual)

        elif opcion == 3:
            menu_modificar(estado.sistema_actual)

        elif opcion == 4:
            print(f"\n=== SALIR/GUARDAR (Sistema actual: {nombre_sistema}) ===")
            print("1. Guardar")
            print("2. Salir")

            opcion_2 = pedir_int("Elije una opcíon: ")
            if opcion_2 == 1:
                guardar_sistema()
            elif opcion_2 == 2:
                salir_programa()
                break







# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    menu_principal()





"""------------------- ADMINISTRAR PLUGINS -------------------
def menu_plugins():
    sistema = estado.sistema_actual
    plugins = sistema.get("plugins_activos", {})

    while True:
        print("\n=== ADMINISTRAR PLUGINS ===")
        for i, plugin in enumerate(plugins, 1):
            estado_str = "✅ Activo" if plugins[plugin] else "❌ Inactivo"
            print(f"{i}. {plugin.capitalize()}: {estado_str}")
        print(f"{len(plugins)+1}. Volver")

        try:
            opcion = int(input("Elige un plugin para activar/desactivar: "))
        except ValueError:
            print("❌ Opción no válida.")
            continue

        if opcion == len(plugins)+1:
            break
        elif 1 <= opcion <= len(plugins):
            key = list(plugins.keys())[opcion-1]
            plugins[key] = not plugins[key]
            estado.cambios_no_guardados = True
            print(f"🔄 {key.capitalize()} ahora {'Activo' if plugins[key] else 'Inactivo'}")
        else:
            print("❌ Opción no válida.")"""