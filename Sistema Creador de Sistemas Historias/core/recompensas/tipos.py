#core/recompensas/tipos.py
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
# Inicialización de tipos base
# ─────────────────────────────
TIPOS_RECOMPENSA_ACTIVOS = { tipo: True for tipo in TIPOS_RECOMPENSA }

def inicializar_tipos_recompensa_activos():
    """
    Inicializa TIPOS_RECOMPENSA_ACTIVOS desde el sistema cargado,
    o deja todo activo por defecto.
    """
    sistema = estado.sistema_actual
    if sistema and "tipos_recompensa_activos" in sistema:
        for tipo, activo in sistema["tipos_recompensa_activos"].items():
            TIPOS_RECOMPENSA_ACTIVOS[tipo] = activo
    else:
        for tipo in TIPOS_RECOMPENSA:
            TIPOS_RECOMPENSA_ACTIVOS[tipo] = True

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
# Activar/Desactivar Recursos Base (guardando en sistema)
# ─────────────────────────────
def activar_tipo_base(tipo: str):
    sistema = estado.sistema_actual
    if tipo not in TIPOS_RECOMPENSA:
        raise ValueError(f"'{tipo}' no es un tipo base válido")
    TIPOS_RECOMPENSA_ACTIVOS[tipo] = True
    if sistema is not None:
        sistema.setdefault("tipos_recompensa_activos", {})[tipo] = True
        estado.cambios_no_guardados = True

def desactivar_tipo_base(tipo: str):
    sistema = estado.sistema_actual
    if tipo not in TIPOS_RECOMPENSA:
        raise ValueError(f"'{tipo}' no es un tipo base válido")
    TIPOS_RECOMPENSA_ACTIVOS[tipo] = False
    if sistema is not None:
        sistema.setdefault("tipos_recompensa_activos", {})[tipo] = False
        estado.cambios_no_guardados = True

def esta_tipo_base_activo(tipo: str) -> bool:
    """Devuelve True si el tipo base está activo"""
    sistema = estado.sistema_actual
    if sistema and "tipos_recompensa_activos" in sistema:
        return sistema["tipos_recompensa_activos"].get(tipo, True)
    return TIPOS_RECOMPENSA_ACTIVOS.get(tipo, True)

# ─────────────────────────────
# API pública SCS
# ─────────────────────────────

def obtener_tipos_recompensa_validos():
    sistema = estado.sistema_actual or {}
    plugins_activos = sistema.get("plugins_activos", {})

    tipos_validos = set()

    # 1️⃣ Tipos base (considerando activación y plugin)
    for tipo, plugin_requerido in TIPOS_RECOMPENSA.items():
        if not esta_tipo_base_activo(tipo):
            continue  # Ignorar tipos desactivados
        if plugin_requerido is None or plugins_activos.get(plugin_requerido, False):
            tipos_validos.add(tipo)

    # 2️⃣ Recursos dinámicos (sin tocar su lógica)
    for nombre, config in RECURSOS_REGISTRADOS.items():
        plugin_requerido = config.get("requiere_plugin")
        if plugin_requerido is None or plugins_activos.get(plugin_requerido, False):
            tipos_validos.add(nombre)

    return tipos_validos

def es_tipo_recompensa_valido(tipo: str) -> bool:
    return tipo in obtener_tipos_recompensa_validos()
