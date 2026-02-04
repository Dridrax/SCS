
def pedir_int(prompt):
    while True:
        valor = input(prompt)
        try:
            return int(valor)
        except ValueError:
            print("❌ Debes introducir un número entero válido.")


"""Mejorado def pedir_int(texto, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(texto))
            if minimo is not None and valor < minimo:
                print(f"❌ Debe ser ≥ {minimo}")
                continue
            if maximo is not None and valor > maximo:
                print(f"❌ Debe ser ≤ {maximo}")
                continue
            return valor
        except ValueError:
            print("❌ Introduce un número válido.")
"""

def pedir_si_no(texto):
    while True:
        respuesta = input(texto).strip().lower()
        if respuesta in ("s", "n"):
            return respuesta == "s"
        print("❌ Responde con 's' o 'n'")

def sumar_progreso(progress_stat, puntos): #funciona solamente para los progress_stats
    """
    Suma puntos a un stat de progreso.
    Si se alcanza o supera el máximo, sube de nivel automáticamente.
    """
    progress_stat["actual"] += puntos

    while progress_stat["actual"] >= progress_stat["max"]:
        progress_stat["actual"] -= progress_stat["max"]
        progress_stat["nivel"] += 1

        # Escalado del siguiente nivel (ajustable)
        progress_stat["max"] = int(progress_stat["max"] * 1.2)

def modificar_progreso(stat, cambio):
    """
    Modifica un progress stat sumando/restando puntos.
    Permite subir o bajar niveles y utiliza un factor de escalado editable.
    """
    if not all(k in stat for k in ("nivel", "actual", "max")):
        print("❌ Stat mal definido")
        return

    stat["actual"] += cambio
    factor = stat.get("factor_escalado", 1.2)

    # Subir niveles
    while stat["actual"] >= stat["max"]:
        stat["actual"] -= stat["max"]
        stat["nivel"] += 1
        stat["max"] = int(stat["max"] * factor)

    # Bajar niveles
    while stat["actual"] < 0 and stat["nivel"] > 1:
        stat["nivel"] -= 1
        stat["max"] = max(1, int(stat["max"] / factor))
        stat["actual"] += stat["max"]

    if stat["nivel"] == 1 and stat["actual"] < 0:
        stat["actual"] = 0


def modificar_factor_escalado(stat):
    """
    Permite al autor cambiar el factor de escalado de un progress stat.
    El cambio aplica a niveles futuros.
    """
    if "factor_escalado" not in stat:
        stat["factor_escalado"] = 1.2

    print(f"Factor actual: {stat['factor_escalado']}")
    nuevo_factor = float(input("\nNuevo factor de escalado (ej: 1.2): "))
    if nuevo_factor <= 0:
        print("❌ El factor debe ser mayor que 0.")
        return

    stat["factor_escalado"] = nuevo_factor
    print(f"\n✅ Factor de escalado actualizado a {nuevo_factor}")
