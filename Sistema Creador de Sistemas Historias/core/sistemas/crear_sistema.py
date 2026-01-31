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

    print("\n--- STATS BASE ---")
    stats = {}
    stats["Edad"] = pedir_int("Edad: ")
    stats["Nivel"] = pedir_int("Nivel: ")
    stats["Vida"] = pedir_int("Vida: ")
    stats["Ataque"] = pedir_int("Ataque: ")

    while input("¿Hay más stats? (s/n): ").lower() == "s":
        nombre = input("Nombre del stat: ")
        valor = pedir_int("Valor (+ o -): ")
        stats[nombre] = valor

    # Inicialización según plugins
    inventario = [] if plugins_activos.get("inventario", False) else None
    habilidades = [] if plugins_activos.get("habilidades", False) else None
    titulos = [] if plugins_activos.get("titulos", False) else None
    bendiciones = [] if plugins_activos.get("bendiciones", False) else None
    maldiciones = [] if plugins_activos.get("maldiciones", False) else None
    linea_temporal = []

    # Creación de contenido según plugin
    if inventario is not None:
        if input("\n¿Tiene objetos en el inventario? (s/n): ").lower() == "s":
            while True:
                objeto = {
                    "nombre": input("Nombre del objeto: "),
                    "clase": input("Clase: "),
                    "categoria": input("Categoría: "),
                    "efectos": input("Efectos (texto): ")
                }
                inventario.append(objeto)
                if input("¿Añadir otro objeto? (s/n): ").lower() != "s":
                    break

    if habilidades is not None:
        if input("\n¿Tiene habilidades? (s/n): ").lower() == "s":
            while True:
                habilidad = {
                    "nombre": input("Nombre de la habilidad: "),
                    "tipo": input("Tipo: "),
                    "descripcion": input("Descripción: "),
                    "efectos": input("Efectos (texto): ")
                }
                habilidades.append(habilidad)
                if input("¿Añadir otra habilidad? (s/n): ").lower() != "s":
                    break

    if titulos is not None:
        if input("\n¿Tiene títulos? (s/n): ").lower() == "s":
            while True:
                titulo = {
                    "nombre": input("Nombre del título: "),
                    "descripcion": input("Descripción: "),
                    "origen": input("Origen: "),
                    "tipo": input("Tipo (pasivo/activo/etc): "),
                    "efectos": {}
                }
                while input("¿Añadir efecto al título? (s/n): ").lower() == "s":
                    stat = input("Stat afectado: ")
                    valor = pedir_int("Valor (+ o -): ")
                    titulo["efectos"][stat] = valor
                titulos.append(titulo)
                if input("¿Añadir otro título? (s/n): ").lower() != "s":
                    break

    if bendiciones is not None:
        if input("\n¿Tiene bendiciones? (s/n): ").lower() == "s":
            while True:
                bendicion = {
                    "nombre": input("Nombre de la bendición: "),
                    "descripcion": input("Descripción: "),
                    "origen": input("Origen: "),
                    "tipo": input("Tipo (pasivo/activo/etc): "),
                    "efectos": {}
                }
                while input("¿Añadir efecto a la bendición? (s/n): ").lower() == "s":
                    stat = input("Stat afectado: ")
                    valor = pedir_int("Valor (+ o -): ")
                    bendicion["efectos"][stat] = valor
                bendiciones.append(bendicion)
                if input("¿Añadir otra bendición? (s/n): ").lower() != "s":
                    break

    if maldiciones is not None:
        if input("\n¿Tiene maldiciones? (s/n): ").lower() == "s":
            while True:
                maldicion = {
                    "nombre": input("Nombre de la maldición: "),
                    "descripcion": input("Descripción: "),
                    "origen": input("Origen: "),
                    "tipo": input("Tipo: "),
                    "efectos": {}
                }
                while input("¿Añadir efecto a la maldición? (s/n): ").lower() == "s":
                    stat = input("Stat afectado: ")
                    valor = pedir_int("Valor (+ o -): ")
                    maldicion["efectos"][stat] = valor
                maldiciones.append(maldicion)
                if input("¿Añadir otra maldición? (s/n): ").lower() != "s":
                    break

    # Historia
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

    # Sistema final
    sistema = {
        "personaje": {"nombre": personaje_nombre},
        "nombre_sistema": nombre_sistema,
        "stats": stats,
        "inventario": inventario,
        "habilidades": habilidades,
        "titulos": titulos,
        "bendiciones": bendiciones,
        "maldiciones": maldiciones,
        "linea_temporal": linea_temporal,
        "historia": historia
    }

    estado.sistema_actual = sistema
    estado.cambios_no_guardados = True
    print(f"\n✅ Sistema '{nombre_sistema}' creado para {personaje_nombre}.\n")
    return sistema
