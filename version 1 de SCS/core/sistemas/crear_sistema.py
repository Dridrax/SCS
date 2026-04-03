from core.estado_global import estado

def pedir_int(prompt):
    while True:
        valor = input(prompt)
        try:
            return int(valor)
        except ValueError:
            print("❌ Debes introducir un número entero válido.")


def crear_nuevo_sistema(plugins_activos=None):
    if plugins_activos is None:
        plugins_activos = {}

    print("\n=== CREAR NUEVO SISTEMA / PERSONAJE ===\n")
    personaje_nombre = input("Nombre del personaje: ")

    if input("¿Tiene nombre el sistema? (s/n): ").lower() == "s":
        nombre_sistema = input("Nombre del sistema: ")
    else:
        nombre_sistema = None

    # --- STATS BASE ---
    stats = {}
    stats["Edad"] = pedir_int("Edad: ")
    stats["Nivel"] = pedir_int("Nivel: ")
    stats["Vida"] = pedir_int("Vida: ")
    stats["Ataque"] = pedir_int("Ataque: ")

    while input("¿Hay más stats? (s/n): ").lower() == "s":
        nombre = input("Nombre del stat: ")
        valor = pedir_int("Valor (+ o -): ")
        stats[nombre] = valor

    # --- Inicialización según plugins ---
    # Las claves que usan listas
    inventario = [] if plugins_activos.get("inventario", False) else []
    habilidades = [] if plugins_activos.get("habilidades", False) else []
    titulos = [] if plugins_activos.get("titulos", False) else []
    bendiciones = [] if plugins_activos.get("bendiciones", False) else []
    maldiciones = [] if plugins_activos.get("maldiciones", False) else []
    linea_temporal = []

    # --- Enciclopedias ---
    # Siempre es diccionario, cada sección lista vacía
    enciclopedias = {}
    if plugins_activos.get("inventario"):
        enciclopedias["inventario"] = []
    if plugins_activos.get("habilidades"):
        enciclopedias["habilidades"] = []
    if plugins_activos.get("titulos"):
        enciclopedias["titulos"] = []
    if plugins_activos.get("bendiciones"):
        enciclopedias["bendiciones"] = []
    if plugins_activos.get("maldiciones"):
        enciclopedias["maldiciones"] = []

    # --- HISTORIA ---
    historia = {}
    tipo = input("\n¿Original o Fanfiction?: ").lower()
    historia["tipo"] = tipo
    if tipo == "original":
        historia["sinopsis"] = input("Sinopsis: ")
        historia["personajes_principales"] = input("Personajes principales: ")
    else:
        historia["fandom"] = input("Fandom: ")
        historia["sinopsis"] = input("Sinopsis: ")
        historia["personajes"] = input("Personajes: ")
        historia["parejas"] = input("Parejas: ")

    # Inicializar enciclopedias aunque el plugin no esté activo
    enciclopedias = {}
    for plugin in ["inventario", "habilidades", "titulos", "bendiciones", "maldiciones", "notas", "bestiario"]:
        enciclopedias[plugin] = []

    # Sistema final
    sistema = {
        "personaje": {"nombre": personaje_nombre},
        "nombre_sistema": nombre_sistema,
        "stats": stats,
        "inventario": [] ,  
        "habilidades": [],
        "titulos": [],
        "bendiciones": [],
        "maldiciones": [],
        "linea_temporal": [],
        "historia": historia,
        "enciclopedias": enciclopedias,
        "plugins_activos": plugins_activos  # <-- Añadir aquí
    }


    estado.sistema_actual = sistema
    estado.cambios_no_guardados = True
    print(f"\n✅ Sistema '{nombre_sistema}' creado para {personaje_nombre}.\n")
    return sistema

# 💡 COMENTARIOS:
# - Si agregas nuevas secciones/plugin como tienda, ruleta, minijuegos, etc.:
#   1. Añadir una lista vacía o diccionario en este bloque según su tipo.
#   2. Añadir clave correspondiente en 'enciclopedias' si necesita registro de objetos.
