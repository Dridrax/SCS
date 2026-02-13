# ─────────────────────────────
# Tipos base de recompensa
# ─────────────────────────────

TIPOS_RECOMPENSA = {
    "stats",
    "progress_stats",
    "objetos",
    "puntos_stats",
    "puntos_habilidad",
    "dinero",
    "nivel",
    "tiradas"
}


# ─────────────────────────────
# Recursos abstractos dinámicos
# ─────────────────────────────

RECURSOS_REGISTRADOS = {}

def registrar_recurso(nombre: str, descripcion: str = "", requiere_plugin: str = None, destino: str = "recursos"):
    """
    Registra un recurso dinámico y su destino dentro del sistema.

    Args:
        nombre: Nombre del recurso.
        descripcion: Descripción opcional.
        requiere_plugin: Si depende de un plugin.
        destino: Ruta dentro del sistema donde se guardará ("recursos", "stats_extra", etc.)
    """
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("El nombre del recurso debe ser un string válido")

    nombre = nombre.strip()

    if nombre in TIPOS_RECOMPENSA:
        raise ValueError(f"'{nombre}' ya es un tipo base de recompensa")

    RECURSOS_REGISTRADOS[nombre] = {
        "descripcion": descripcion,
        "requiere_plugin": requiere_plugin,
        "destino": destino  # <-- Aquí guardamos la ruta de destino
    }


def cargar_recursos_desde_sistema(sistema: dict):
    """
    Registra en memoria los recursos definidos en el sistema.
    """
    RECURSOS_REGISTRADOS.clear()

    for nombre, config in sistema.get("recursos_definidos", {}).items():
        registrar_recurso(
            nombre,
            config.get("descripcion", ""),
            config.get("requiere_plugin"),
            config.get("destino", "recursos")
        )


# ─────────────────────────────
# API pública SCS
# ─────────────────────────────

def obtener_tipos_recompensa_validos():
    return set(TIPOS_RECOMPENSA) | set(RECURSOS_REGISTRADOS.keys())

def es_tipo_recompensa_valido(tipo: str) -> bool:
    return tipo in obtener_tipos_recompensa_validos()
