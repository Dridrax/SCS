from core.estado_global import estado

# ─────────────────────────────
# Tipos base de recompensa
# ─────────────────────────────

TIPOS_RECOMPENSA = {
    "stats": None,
    "progress_stats": None,
    "objetos": "inventario",
    "puntos_stats": None,
    "puntos_habilidad": None,
    "dinero": None,
    "nivel": "niveles",
    "tiradas": None
}


# ─────────────────────────────
# Recursos abstractos dinámicos
# ─────────────────────────────

RECURSOS_REGISTRADOS = {}

def registrar_recurso(
    nombre: str,
    descripcion: str = "",
    requiere_plugin: str = None,
    destino: str = "recursos",
    modo: str = "contenedor"  # 👈 NUEVO
):
    """
    Registra un recurso dinámico y su destino dentro del sistema.

    Args:
        nombre: Nombre del recurso.
        descripcion: Descripción opcional.
        requiere_plugin: Si depende de un plugin.
        destino: Ruta dentro del sistema donde se guardará.
        modo: "simple" o "contenedor"
    """

    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("El nombre del recurso debe ser un string válido")

    nombre = nombre.strip()

    if nombre in TIPOS_RECOMPENSA:
        raise ValueError(f"'{nombre}' ya es un tipo base de recompensa")

    if modo not in ("simple", "contenedor"):
        raise ValueError("El modo debe ser 'simple' o 'contenedor'")

    RECURSOS_REGISTRADOS[nombre] = {
        "descripcion": descripcion,
        "requiere_plugin": requiere_plugin,
        "destino": destino,
        "modo": modo  # 👈 NUEVO
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
            config.get("destino", "recursos"),
            config.get("modo", "contenedor")
        )


# ─────────────────────────────
# API pública SCS
# ─────────────────────────────

def obtener_tipos_recompensa_validos():
    sistema = estado.sistema_actual or {}
    plugins_activos = sistema.get("plugins_activos", {})

    tipos_validos = set()

    # 1️⃣ Tipos base
    for tipo, plugin_requerido in TIPOS_RECOMPENSA.items():
        if plugin_requerido is None:
            tipos_validos.add(tipo)
        else:
            if plugins_activos.get(plugin_requerido, False):
                tipos_validos.add(tipo)

    # 2️⃣ Recursos dinámicos
    for nombre, config in RECURSOS_REGISTRADOS.items():
        plugin_requerido = config.get("requiere_plugin")
        if plugin_requerido is None:
            tipos_validos.add(nombre)
        else:
            if plugins_activos.get(plugin_requerido, False):
                tipos_validos.add(nombre)

    return tipos_validos


def es_tipo_recompensa_valido(tipo: str) -> bool:
    return tipo in obtener_tipos_recompensa_validos()
