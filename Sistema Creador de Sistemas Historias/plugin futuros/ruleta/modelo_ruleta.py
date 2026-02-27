class RecompensaRuleta:
    def __init__(self, recompensa, peso=1):
        """
        recompensa: dict compatible con aplicar_recompensas
        peso: probabilidad relativa
        """
        self.recompensa = recompensa
        self.peso = peso


class Ruleta:
    def __init__(self, id_ruleta, nombre):
        self.id = id_ruleta
        self.nombre = nombre
        self.recompensas = []

    def agregar_recompensa(self, recompensa_ruleta):
        self.recompensas.append(recompensa_ruleta)
