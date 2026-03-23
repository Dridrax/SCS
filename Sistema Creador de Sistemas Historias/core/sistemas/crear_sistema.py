from core.estado_global import estado
from core.utils.funciones_utiles import pedir_int, pedir_si_no
from core.guardado.archivos import guardar_sistema
from .sistema_temporal import (
    crear_sistema_temporal_config,
    configurar_tipos_base_interactivo
)



def crear_nuevo_sistema(plugins_activos=None):


    # --- SELECCIÓN DE PLUGINS ---
    print("\n=== SELECCIÓN DE PLUGINS ===")
    print("Activa o desactiva los plugins que usará este sistema.\n")
    
    from core.menus.menus import menu_plugins
    
    PLUGINS_DISPONIBLES = ["inventario"]
    
    # 1️⃣ Guardamos el sistema actual real (si existe)
    sistema_anterior = estado.sistema_actual
    
    # 2️⃣ Creamos un sistema TEMPORAL solo para plugins
    estado.sistema_actual = {
        "plugins_activos": {plugin: False for plugin in PLUGINS_DISPONIBLES}
    }
    
    # 3️⃣ Abrimos el menú
    menu_plugins(autoguardar=False)
    
    # 4️⃣ Guardamos el resultado
    plugins_activos = estado.sistema_actual["plugins_activos"]
    
    # 5️⃣ Restauramos el sistema real
    estado.sistema_actual = sistema_anterior

    

    # --- SELECCIÓN DE RECURSOS ---
    print("\n=== SELECCIÓN DE RECURSOS ===")

    # 1️⃣ Preguntar recursos base
    tipos_recompensa = configurar_tipos_base_interactivo()

    # 2️⃣ Crear sistema temporal para recursos dinámicos
    sistema_temp = crear_sistema_temporal_config(plugins_activos)
    sistema_temp["tipos_recompensa_activos"] = tipos_recompensa

    # 3️⃣ Crear recursos personalizados si el usuario quiere
    from core.recompensas.ui_preparacion import menu_configurar_recurso_dinamicos

    if pedir_si_no("\n¿Quieres crear recursos personalizados? (s/n): "):

        sistema_anterior = estado.sistema_actual
        estado.sistema_actual = sistema_temp

        menu_configurar_recurso_dinamicos()

        estado.sistema_actual = sistema_anterior

    # Guardamos los recursos creados
    recursos_dinamicos = sistema_temp.get("recursos_definidos", {})

    


    print("\n=== CREAR NUEVO SISTEMA / PERSONAJE ===\n")

    # --- PERSONAJE ---
    personaje_nombre = input("Nombre del personaje: ")
    edad = pedir_int("Edad: ")

    # --- NOMBRE DEL SISTEMA ---
    if input("¿Tiene nombre el sistema? (s/n): ").lower() == "s":
        nombre_sistema = input("Nombre del sistema: ")
    else:
        nombre_sistema = None


    # --- STATS ---
    stats = {}
    progress_stats = {}
    
    # Stats simples (valor único)
    if pedir_si_no("¿El sistema tiene stats simples? (s/n): "):
        print("\n— Stats simples (enter para terminar) —")
        while True:
            nombre = input("Nombre del stat: ").strip()
            if nombre == "":
                break
            valor = pedir_int("Valor (+ o -): ")
            stats[nombre] = valor
    
    # Stats de progreso (valor actual / valor máximo)
    if pedir_si_no("¿El sistema tiene stats de progreso? (s/n): "):
        print("\n— Stats de progreso (enter para terminar) —")
        while True:
            nombre = input("Nombre del stat (ej: Cabeza, Pecho): ").strip()
            if nombre == "":
                break
            
            actual = pedir_int("Puntos actuales: ")
            maximo = pedir_int("Puntos para subir de nivel: ")
            nivel = pedir_int("Nivel Base: ")
    
            # Preguntar factor de escalado (opcional, por defecto 1.2)
            factor = input("Factor de escalado (por defecto 1.2): ").strip()
            try:
                factor = float(factor) if factor else 1.2
                if factor <= 0:
                    print("❌ El factor debe ser mayor que 0. Se usará 1.2 por defecto.")
                    factor = 1.2
            except ValueError:
                print("❌ Valor inválido. Se usará 1.2 por defecto.")
                factor = 1.2
    
            progress_stats[nombre] = {
                "actual": actual,
                "max": maximo,
                "nivel": nivel,
                "factor_escalado": factor
            }

    # --- HISTORIA ---
    historia = {}

    while True:
        tipo = input("\n¿Original o Fanfiction?\nO/F: ").lower()
        if tipo in ("o", "f"):
            break
        print("❌ Tipo inválido. Usa O o F.")

    if tipo == "o":
        historia["tipo"] = "original"
        historia["sinopsis"] = input("Sinopsis: ")
        historia["personajes_principales"] = input("Personajes principales: ")
        historia["parejas"] = input("Parejas: ")

    else:
        historia["tipo"] = "fanfiction"
        historia["fandom"] = input("Fandom: ")
        historia["sinopsis"] = input("Sinopsis: ")
        historia["personajes"] = input("Personajes: ")
        historia["parejas"] = input("Parejas: ")

    # --- SISTEMA FINAL ---
    sistema = {
        "personaje": {
            "nombre": personaje_nombre,
            "edad": edad,
        },
        "nombre_sistema": nombre_sistema,

        "stats": stats,
        "progress_stats": progress_stats,

        "historia": historia,

        "plugins_activos": plugins_activos or {},

        # 🔹 NUEVO
        "tipos_recompensa_activos": tipos_recompensa,

        # 🔹 NUEVO
        "recursos_definidos": recursos_dinamicos
    }

    # Si el plugin inventario está activo, inicializamos el inventario como diccionario vacío
    if sistema["plugins_activos"].get("inventario"):
        sistema["inventario"] = {}

    estado.sistema_actual = sistema

    # Inicializar plugin_cache para este sistema
    estado.plugin_cache = {
        "plugins": {},
        "stats": sistema.get("stats", {}),
        "progress_stats": sistema.get("progress_stats", {})
    }

    

    estado.cambios_no_guardados = True

    nombre_mostrar = nombre_sistema if nombre_sistema else "Sin nombre"
    print(f"\n✅ Sistema '{nombre_mostrar}' creado para '{personaje_nombre}'.\n")

    return sistema


"""======================== SCS - SISTEMA DE STATS ========================
        

        ========================
        SCS - SISTEMA DE STATS
        ========================

        SCS separa los stats por tipos para evitar mezclar lógicas distintas
        y permitir una expansión sencilla mediante core o plugins.

        --------------------------------------------------
        1) Stats simples
        --------------------------------------------------

        Estructura:
            "stats": {
                "Fuerza": 10,
                "Magia": 5
            }

        Características:
        - Valor único
        - Se modifican directamente
        - No tienen progreso ni niveles

        Ejemplo de uso:
            sistema["stats"]["Fuerza"] += 1

        --------------------------------------------------
        2) Stats de progreso
        --------------------------------------------------

        Estructura:
            "progress_stats": {
                "Cabeza": {
                    "actual": 100,
                    "max": 640,
                    "nivel": 1
                }
            }

        Características:
        - Representan progreso hacia un siguiente nivel
        - Suben de nivel al alcanzar 'max'
        - Pueden subir varios niveles de golpe
        - El valor sobrante se conserva

        --------------------------------------------------
        Función core: sumar_progreso
        --------------------------------------------------

        Uso:
            sumar_progreso(progress_stat, puntos)

        Ejemplo:
            sumar_progreso(sistema["progress_stats"]["Cabeza"], 120)

        Comportamiento:
        - Suma puntos al campo 'actual'
        - Mientras actual >= max:
            - resta max
            - incrementa nivel
            - recalcula el nuevo max

        El escalado de 'max' puede ajustarse según el sistema
        (porcentaje, fórmula fija, tablas, etc.).

        --------------------------------------------------
        DISEÑO FUTURO (stat_types)
        --------------------------------------------------

        Para escalar SCS, todos los tipos de stats pueden unificarse bajo:

            "stat_types": {
                "simple": {...},
                "progress": {...},
                "temporal": {...},
                "porcentaje": {...}
            }

        Cada tipo:
        - Tiene su propia estructura
        - Tiene su propia lógica
        - Puede vivir en core o en plugins

        --------------------------------------------------
        REGLA DE ORO
        --------------------------------------------------
        Nunca mezclar distintos tipos de stats en el mismo diccionario.
        Cada tipo tiene sus helpers y reglas propias.

        Esto mantiene SCS limpio, mantenible y escalable.
        """