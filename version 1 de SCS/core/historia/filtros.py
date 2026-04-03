def filtrar_por_capitulo(sistema):
    try:
        num = int(input("Número de capítulo: "))
    except ValueError:
        print("❌ Número inválido.")
        return

    encontrados = [c for c in sistema["linea_temporal"] if c["id"] == num]

    if not encontrados:
        print("❌ No se encontró ese capítulo.")
        return

    for cap in encontrados:
        print(f"\n[Cap. {cap['id']}] {cap['titulo']} ({cap['arco']})")
        print(cap["resumen"])


def filtrar_por_rango(sistema):
    try:
        inicio = int(input("Desde capítulo: "))
        fin = int(input("Hasta capítulo: "))
    except ValueError:
        print("❌ Valores inválidos.")
        return

    encontrados = [
        c for c in sistema["linea_temporal"]
        if inicio <= c["id"] <= fin
    ]

    if not encontrados:
        print("❌ No hay capítulos en ese rango.")
        return

    for cap in encontrados:
        print(f"\n[Cap. {cap['id']}] {cap['titulo']} ({cap['arco']})")
        print(cap["resumen"])


def filtrar_por_arco(sistema):
    arcos = sorted(set(c["arco"] for c in sistema["linea_temporal"]))

    if not arcos:
        print("❌ No hay arcos definidos.")
        return

    print("\nArcos disponibles:")
    for i, arco in enumerate(arcos, 1):
        print(f"{i}. {arco}")

    try:
        opcion = int(input("Selecciona un arco: ")) - 1
        arco_seleccionado = arcos[opcion]
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return

    for cap in sistema["linea_temporal"]:
        if cap["arco"] == arco_seleccionado:
            print(f"\n[Cap. {cap['id']}] {cap['titulo']}")
            print(cap["resumen"])


def menu_filtros_linea_temporal(sistema):
    if not sistema.get("linea_temporal"):
        print("❌ No hay capítulos para filtrar.")
        return

    while True:
        print("\n=== FILTROS DE LÍNEA TEMPORAL ===")
        print("1. Por número de capítulo")
        print("2. Por rango de capítulos")
        print("3. Por arco / saga")
        print("4. Volver")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            filtrar_por_capitulo(sistema)
        elif opcion == "2":
            filtrar_por_rango(sistema)
        elif opcion == "3":
            filtrar_por_arco(sistema)
        elif opcion == "4":
            break
        else:
            print("❌ Opción no válida.")
