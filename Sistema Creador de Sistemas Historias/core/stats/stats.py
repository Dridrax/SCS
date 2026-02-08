from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import modificar_progreso, pedir_int, modificar_factor_escalado


"""======================================= DOCUMENTACIÓN DE STATS EN SCS =======================================

Tipos de Stats implementados:

1. Stats Simples
-----------------
- Son valores individuales, representados como enteros.
- Ejemplo:
    "Dinero": 111
- Se almacenan en:
    sistema["stats"]

- Se muestran con la función:
    mostrar_stats(sistema)
  Esta función itera sobre todas las claves de stats simples y las imprime.

- Se modifican directamente con helpers (pendiente de implementación):
    modificar_stat_simple(sistema, nombre_stat, delta)

2. Progress Stats (Stats de Progreso)
-------------------------------------
- Representan atributos que pueden subir de nivel y tienen progreso interno.
- Cada stat tiene la siguiente estructura:
    {
        "actual": int,   # Puntos actuales
        "max": int,      # Puntos necesarios para subir al siguiente nivel
        "nivel": int     # Nivel actual de la stat
    }
- Se almacenan en:
    sistema["progress_stats"]

- Funciones actuales relacionadas:

  a) sumar_progreso(stat, puntos)
     - Suma 'puntos' al stat de progreso.
     - Si 'actual' supera 'max', sube de nivel y recalcula el nuevo máximo.
     - Ejemplo de uso:
        sumar_progreso(sistema["progress_stats"]["Cabeza"], 50)

  b) mostrar_progress_stats_bar(progress_stats, ancho_barra=20)
     - Muestra los stats de progreso con barra visual tipo RPG.
     - Ejemplo de salida:
        Cabeza: [██████▒▒▒▒▒▒▒] 100/640 Nivel 1
     - Parámetros:
        progress_stats: diccionario de stats de progreso
        ancho_barra: cantidad de caracteres de la barra visual

- Seguridad:
    - La función verifica si los valores son diccionarios antes de intentar mostrar el stat,
      así no rompe aunque accidentalmente haya un valor incorrecto.

---------------------------------------
Buenas prácticas y futuras mejoras:
---------------------------------------
- Para agregar un nuevo tipo de stat, seguir la estructura modular:
    1) Definir dónde se guarda en 'sistema'.
    2) Crear funciones específicas para mostrar y modificar ese tipo.
    3) Integrar en mostrar_ficha y menus si corresponde.

- Nunca mezclar tipos de stats:
    - stats simples → valores enteros
    - progress_stats → dict con 'actual', 'max', 'nivel'
    - otros tipos futuros → dicts o estructuras propias

- Modificación de stats:
    - Se implementará más adelante con funciones dedicadas por tipo, 
      siguiendo la misma lógica que sumar_progreso para progress_stats.

- Integración con menú:
    - mostrar_stats(sistema) → imprime todos los stats simples y progress_stats
    - mostrar_progress_stats_bar(sistema["progress_stats"]) → imprime solo los progress_stats con barra

---------------------------------------
Fin de la documentación de stats
=======================================
"""


# =========================
# MOSTRAR STATS
# =========================
def mostrar_stats(sistema):
    """
    Muestra por pantalla los stats de un sistema.
    Diferencia entre stats simples y stats de progreso.
    """

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    print("\n=== STATS DEL SISTEMA ===")

    # Stats simples
    stats = sistema.get("stats", {})
    if stats:
        print("\n-- Stats Simples --")
        for nombre, valor in stats.items():
            print(f"{nombre}: {valor}")
    else:
        print("\n-- Stats Simples --\nNo hay stats simples")


def mostrar_progress_stats_bar(progress_stats, ancho_barra=20):
    """
    Muestra los stats de progreso con barra visual.
    
    Cada stat muestra:
        Nombre: [████▒▒▒▒▒▒] actual/max Nivel N
    
    Parámetros:
        progress_stats: dict con la estructura de progress_stats
        ancho_barra: cantidad de caracteres de la barra completa
    """

    if not progress_stats:
        print("\n-- Stats de Progreso --\nNo hay stats de progreso")
        return

    print("\n-- Stats de Progreso --")
    for nombre, datos in progress_stats.items():

        if not isinstance(datos, dict):
            print(f"{nombre}: ❌ Valor de stat inválido")
            continue
        
        actual = datos.get("actual", 0)
        maximo = datos.get("max", 1)  # evitar división por cero
        nivel = datos.get("nivel", 1)

        # calcular porcentaje y cantidad de bloques llenos
        porcentaje = actual / maximo
        bloques_llenos = int(porcentaje * ancho_barra)
        bloques_vacios = ancho_barra - bloques_llenos

        # crear barra
        barra = "█" * bloques_llenos + "▒" * bloques_vacios

        print(f"{nombre}: [{barra}] {actual}/{maximo} Nivel {nivel}")


# =========================
# MODIFICAR STAT SIMPLES
# =========================
def modificar_stat_simples(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema or not sistema.get("stats"):
        print("❌ No hay stats disponibles.")
        return

    print("\nMODIFICAR STAT\n")
    mostrar_stats(sistema)

    stat_input = input("\nNombre del stat a modificar: ").strip()
    stats = sistema["stats"]

    stat = next((s for s in stats if s.lower() == stat_input.lower()), None)
    if not stat:
        print("❌ Ese stat no existe.")
        return

    try:
        cambio = int(input("Cantidad a sumar/restar (ej: -10 o 5): "))
    except ValueError:
        print("❌ Debes introducir un número.")
        return

    antes = stats[stat]
    stats[stat] += cambio
    estado.cambios_no_guardados = True

    print(f"✅ {stat}: {antes} → {stats[stat]}")


# =========================
# MODIFICAR PROGRESS STATS
# =========================
def modificar_stat_progress(sistema=None):
    """
    Permite modificar completamente un progress stat:
    - Progreso actual
    - Nivel
    - Valor máximo
    - Factor de escalado
    """
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema or not sistema.get("progress_stats"):
        print("❌ No hay stats de progreso disponibles.")
        return

    progress_stats = sistema["progress_stats"]

    print("\nMODIFICAR STAT DE PROGRESO\n")
    mostrar_progress_stats_bar(progress_stats)

    stat_nombre = input("\nNombre del stat a modificar: ").strip()
    if stat_nombre not in progress_stats:
        print("❌ Ese stat no existe.")
        return

    stat = progress_stats[stat_nombre]

    # Asegurar campos base
    stat.setdefault("factor_escalado", 1.2)

    print(f"\nEditando '{stat_nombre}' (ENTER para mantener valor actual)\n")

    # --- MODIFICAR PROGRESO ---
    cambio_txt = input("\nSumar/restar progreso (ej: -10 o 50): ").strip()
    if cambio_txt:
        try:
            modificar_progreso(stat, int(cambio_txt))
        except ValueError:
            print("❌ Progreso inválido.")

    # --- MODIFICAR NIVEL ---
    nivel_txt = input(f"\nNivel actual ({stat['nivel']}): ").strip()
    if nivel_txt:
        try:
            stat["nivel"] = max(1, int(nivel_txt))
        except ValueError:
            print("❌ Nivel inválido.")

    # --- MODIFICAR MAX ---
    max_txt = input(f"\nValor máximo actual ({stat['max']}): ").strip()
    if max_txt:
        try:
            stat["max"] = max(1, int(max_txt))
        except ValueError:
            print("❌ Valor máximo inválido.")

    # --- MODIFICAR FACTOR ---
    factor_txt = input(f"\nFactor de escalado actual ({stat['factor_escalado']}): ").strip()
    if factor_txt:
        try:
            factor = float(factor_txt)
            if factor > 0:
                stat["factor_escalado"] = factor
            else:
                print("❌ El factor debe ser mayor que 0.")
        except ValueError:
            print("❌ Factor inválido.")

    estado.cambios_no_guardados = True
    print(f"\n✅ '{stat_nombre}' modificado correctamente.")




# =========================
# AÑADIR STAT SIMPLE
# =========================
def agregar_stat_simple(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    nombre = input("Nombre del nuevo stat simple: ").strip()
    if nombre in sistema.get("stats", {}):
        print("❌ Ese stat ya existe.")
        return

    valor = pedir_int("Valor inicial: ")
    
    sistema.setdefault("stats", {})[nombre] = valor
    estado.cambios_no_guardados = True
    print(f"✅ Stat simple '{nombre}' agregado con valor {valor}.")

# =========================
# AÑADIR PROGRESS STATS
# =========================
def agregar_progress_stat(sistema=None):
    """
    Agrega un nuevo progress stat a un sistema.
    Cada stat incluye actual, max, nivel y factor de escalado (editable).
    """
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema:
        print("❌ No hay sistema cargado.")
        return

    nombre = input("Nombre del nuevo stat de progreso: ").strip()
    if nombre in sistema.get("progress_stats", {}):
        print("❌ Ese stat ya existe.")
        return

    actual = pedir_int("Valor actual: ")
    maximo = pedir_int("Valor máximo: ")
    nivel = pedir_int("Nivel inicial: ")

    # Pedir factor de escalado, opcionalmente dejar 1.2 por defecto
    factor = input("Factor de escalado (por defecto 1.2): ").strip()
    try:
        factor = float(factor) if factor else 1.2
        if factor <= 0:
            print("❌ El factor debe ser mayor que 0. Usando 1.2 por defecto.")
            factor = 1.2
    except ValueError:
        print("❌ Valor inválido. Usando 1.2 por defecto.")
        factor = 1.2

    sistema.setdefault("progress_stats", {})[nombre] = {
        "actual": actual,
        "max": maximo,
        "nivel": nivel,
        "factor_escalado": factor
    }

    estado.cambios_no_guardados = True
    print(f"✅ Progress stat '{nombre}' agregado con {actual}/{maximo} Nivel {nivel}, factor de escalado {factor}.")




# =========================
# ELIMINAR STAT SIMPLES
# =========================
def eliminar_stat_simple(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema or not sistema.get("stats"):
        print("❌ No hay stats simples para eliminar.")
        return

    print("\nStats disponibles:")
    for stat in sistema["stats"]:
        print(f"- {stat}")

    nombre = input("Nombre del stat simple a eliminar: ").strip()

    if nombre not in sistema["stats"]:
        print("❌ Ese stat no existe.")
        return

    del sistema["stats"][nombre]
    estado.cambios_no_guardados = True
    print(f"✅ Stat simple '{nombre}' eliminado correctamente.")


# =========================
# ELIMINAR PROGRESS STAT
# =========================
def eliminar_progress_stat(sistema=None):
    if sistema is None:
        sistema = estado.sistema_actual

    if not sistema or not sistema.get("progress_stats"):
        print("❌ No hay stats de progreso para eliminar.")
        return

    print("\nProgress stats disponibles:")
    for stat in sistema["progress_stats"]:
        print(f"- {stat}")

    nombre = input("Nombre del progress stat a eliminar: ").strip()

    if nombre not in sistema["progress_stats"]:
        print("❌ Ese stat no existe.")
        return

    del sistema["progress_stats"][nombre]
    estado.cambios_no_guardados = True
    print(f"✅ Progress stat '{nombre}' eliminado correctamente.")

