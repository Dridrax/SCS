#core/utils/funciones_utiles.py

from core.estado_global import estado



def pedir_int(mensaje, default=None, minimo=None, maximo=None):
    """
    Pide un número entero al usuario.
    - Si se presiona ENTER y se pasa default, devuelve default.
    - Si se pasa minimo, el valor ingresado no puede ser menor.
    - Si se pasa maximo, el valor ingresado no puede ser mayor.
    """
    while True:
        entrada = input(mensaje)
        if entrada == "" and default is not None:
            valor = default
        else:
            try:
                valor = int(entrada)
            except ValueError:
                print("❌ Debes introducir un número válido.")
                continue

        if minimo is not None and valor < minimo:
            print(f"❌ Debe ser al menos {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"❌ Debe ser como máximo {maximo}.")
            continue

        return valor





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


def safe_int_input(prompt, min_val=None, max_val=None, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            val = int(val)
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"❌ Debe estar entre {min_val} y {max_val}.")
                continue
            return val
        except ValueError:
            print("❌ Entrada no válida. Debe ser un número entero.")

def safe_float_input(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            return float(val)
        except ValueError:
            print("❌ Entrada no válida. Debe ser un número.")

def sync_plugin_cache(sistema, nombre_plugin, claves=None):
    """
    Sincroniza datos del sistema hacia estado.plugin_cache.

    sistema: dict principal del sistema cargado
    nombre_plugin: nombre del plugin (string)
    claves: lista de claves a copiar (ej: ["activas", "historial"])
            Si es None, copia todo el bloque del plugin.
    """

    estado.plugin_cache.setdefault("plugins", {})

    datos_plugin = sistema.get(nombre_plugin, {})

    if claves is None:
        # Copia todo el bloque del plugin
        estado.plugin_cache["plugins"][nombre_plugin] = datos_plugin
    else:
        # Copia solo las claves indicadas
        estado.plugin_cache["plugins"][nombre_plugin] = {
            clave: datos_plugin.get(clave, {})
            for clave in claves
        }