from plugins.rachas.helpers_rachas import inicializar_rachas

PLUGIN = {
    "nombre": "Rachas",
    "on_enable": lambda sistema: inicializar_rachas(sistema),
    "on_disable": None
}
