def normalizar_texto(valor):
    if not valor:
        return ""
    return str(valor).lower()


def buscar(elementos, *, nombre=None, tipo=None, categoria=None, efecto=None):
    resultados = []

    for elem in elementos:
        # Nombre
        if nombre:
            if nombre.lower() not in normalizar_texto(elem.get("nombre")):
                continue

        # Tipo / Clase
        if tipo:
            tipo_elem = elem.get("tipo") or elem.get("clase")
            if tipo.lower() not in normalizar_texto(tipo_elem):
                continue

        # Categoría
        if categoria:
            if categoria.lower() not in normalizar_texto(elem.get("categoria")):
                continue

        # Efectos
        if efecto:
            efectos = elem.get("efectos", "")
            if isinstance(efectos, list):
                efectos = " ".join(efectos)
            if efecto.lower() not in normalizar_texto(efectos):
                continue

        resultados.append(elem)

    return resultados
