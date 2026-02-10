import random
from core.recompensas.aplicar import aplicar_recompensas


def tirar_ruleta(sistema, ruleta):
    """
    Ejecuta una tirada:
    - NO cobra nada
    - NO decide reglas
    - SOLO selecciona recompensa y la aplica
    """
    if not ruleta.recompensas:
        print("❌ La ruleta no tiene recompensas.")
        return

    recompensas = ruleta.recompensas
    pesos = [r.peso for r in recompensas]

    seleccion = random.choices(recompensas, weights=pesos, k=1)[0]

    aplicar_recompensas(sistema, seleccion.recompensa)

    return seleccion.recompensa
