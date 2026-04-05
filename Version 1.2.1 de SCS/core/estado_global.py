class EstadoApp:
    def __init__(self):
        self.archivo_actual = None
        self.cambios_no_guardados = False
        self.sistema_actual = None
        self.plugin_cache = {}

estado = EstadoApp()
