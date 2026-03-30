#core/recompensas/tipos.py
import random
from core.estado_global import estado

# ──────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────
# TODO DE LOS RECURSOS
# ──────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────

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
    modo: str = "contenedor"
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
        "modo": modo
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

def obtener_definicion_tipo(tipo: str) -> dict:
    """
    Devuelve la definición completa de un tipo de recompensa.
    Esto evita tener lógica duplicada en validadores y aplicadores.
    """

    # 1️⃣ Tipo base
    if tipo in TIPOS_RECOMPENSA:

        return {
            "tipo": tipo,
            "plugin": TIPOS_RECOMPENSA.get(tipo),
            "destino": tipo,
            "modo": "base"
        }

    # 2️⃣ Recurso dinámico
    if tipo in RECURSOS_REGISTRADOS:

        config = RECURSOS_REGISTRADOS[tipo]

        return {
            "tipo": tipo,
            "plugin": config.get("requiere_plugin"),
            "destino": config.get("destino"),
            "modo": config.get("modo", "contenedor")
        }

    # 3️⃣ Tipo desconocido
    return None

# ──────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────
# TODO DE LAS RAREZAS
# ──────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────

# ─────────────────────────────
# Tipos base de rarezas
# ─────────────────────────────
# Rarezas base con peso
RAREZAS_BASE = {
    "Muy Comun": {"descripcion": "Muy fácil de encontrar", "peso": 5.0},
    "Común": {"descripcion": "Frecuente", "peso": 4.0},
    "Poco Común": {"descripcion": "No tan frecuente", "peso": 3.0},
    "Raro": {"descripcion": "Difícil de encontrar", "peso": 2.0},
    "Muy Raro": {"descripcion": "Muy difícil de encontrar", "peso": 1.0},
    "Épico": {"descripcion": "Extraordinario", "peso": 0.5},
    "Legendario": {"descripcion": "Único y mítico", "peso": 0.1},
}

# ─────────────────────────────
# Inicialización de tipos base
# ─────────────────────────────
RAREZAS_BASE_ACTIVAS = { tipo: True for tipo in RAREZAS_BASE }

def inicializar_rarezas_base_activos():
    """
    Inicializa RAREZAS_BASE_ACTIVOS desde el sistema cargado,
    o deja todo activo por defecto.
    """
    sistema = estado.sistema_actual
    if sistema and "rarezas_base_activos" in sistema:
        for tipo, activo in sistema["rarezas_base_activos"].items():
            RAREZAS_BASE_ACTIVAS[tipo] = activo
    else:
        for tipo in RAREZAS_BASE:
            RAREZAS_BASE_ACTIVAS[tipo] = True

# ─────────────────────────────
# Rarezas dinámicas
# ─────────────────────────────
RAREZAS_REGISTRADAS = {}

def registrar_rareza(
    nombre: str,
    descripcion: str = "",
    peso: float = 1.0,
    requiere_plugin: str = None
):
    """
    Registra una rareza dinámica.
    """

    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("El nombre de la rareza debe ser un string válido")

    nombre = nombre.strip()

    RAREZAS_REGISTRADAS[nombre] = {
        "descripcion": descripcion,
        "peso": peso,
        "requiere_plugin": requiere_plugin
    }

def cargar_rarezas_desde_sistema(sistema: dict):
    RAREZAS_REGISTRADAS.clear()

    for nombre, config in sistema.get("rarezas_definidas", {}).items():
        registrar_rareza(
            nombre,
            config.get("descripcion", ""),
            config.get("peso", 1.0),
            config.get("requiere_plugin")
        )

# ─────────────────────────────
# API pública SCS
# ─────────────────────────────
def esta_rareza_base_activa(tipo: str) -> bool:
    sistema = estado.sistema_actual
    if sistema and "rarezas_base_activos" in sistema:
        return sistema["rarezas_base_activos"].get(tipo, True)
    return RAREZAS_BASE_ACTIVAS.get(tipo, True)

def obtener_rarezas_validas():
    sistema = estado.sistema_actual or {}
    plugins_activos = sistema.get("plugins_activos", {})

    rarezas_validas = set()

    # 1️⃣ Rarezas base (con activación)
    for tipo in RAREZAS_BASE:
        if not esta_rareza_base_activa(tipo):
            continue
        rarezas_validas.add(tipo)

    # 2️⃣ Rarezas dinámicas
    for nombre, config in RAREZAS_REGISTRADAS.items():
        plugin = config.get("requiere_plugin")
        if plugin is None or plugins_activos.get(plugin, False):
            rarezas_validas.add(nombre)

    return rarezas_validas

def es_rareza_valida(nombre: str) -> bool:
    return nombre in obtener_rarezas_validas()

def obtener_definicion_rareza(nombre: str) -> dict:
    if nombre in RAREZAS_REGISTRADAS:
        return RAREZAS_REGISTRADAS[nombre]
    return RAREZAS_BASE.get(nombre)

# ─────────────────────────────
# Función para elegir rareza aleatoria (bases + dinámicas)
# ─────────────────────────────
def elegir_rareza_aleatoria():
    sistema = estado.sistema_actual or {}
    plugins_activos = sistema.get("plugins_activos", {})

    rarezas = []

    # 1️⃣ Añadir rarezas base activas
    for nombre, config in RAREZAS_BASE.items():
        if esta_rareza_base_activa(nombre):
            rarezas.append((nombre, config))

    # 2️⃣ Añadir rarezas dinámicas válidas
    for nombre, config in RAREZAS_REGISTRADAS.items():
        plugin = config.get("requiere_plugin")
        if plugin is None or plugins_activos.get(plugin, False):
            rarezas.append((nombre, config))

    # 3️⃣ Calcular el peso total
    total_peso = sum(r[1]["peso"] for r in rarezas)

    if total_peso <= 0:
        return None

    # 4️⃣ Elegir una rareza aleatoriamente según el peso
    r = random.uniform(0, total_peso)
    acumulado = 0
    for nombre, config in rarezas:
        acumulado += config["peso"]
        if r <= acumulado:
            return nombre
# ─────────────────────────────
# Activar/Desactivar Rarezas Base (guardando en sistema)
# ─────────────────────────────
def activar_rareza_base(tipo: str):
    sistema = estado.sistema_actual
    if tipo not in RAREZAS_BASE:
        raise ValueError(f"'{tipo}' no es una rareza base válida")

    RAREZAS_BASE_ACTIVAS[tipo] = True

    if sistema is not None:
        sistema.setdefault("rarezas_base_activos", {})[tipo] = True
        estado.cambios_no_guardados = True

def desactivar_rareza_base(tipo: str):
    sistema = estado.sistema_actual
    if tipo not in RAREZAS_BASE:
        raise ValueError(f"'{tipo}' no es una rareza base válida")

    RAREZAS_BASE_ACTIVAS[tipo] = False

    if sistema is not None:
        sistema.setdefault("rarezas_base_activos", {})[tipo] = False
        estado.cambios_no_guardados = True


# ─────────────────────────────
# Asignar rareza a un objeto
# ─────────────────────────────
def asignar_rareza(objeto, preferida=None):
    """
    Asigna una rareza válida a un objeto.
    - Si 'preferida' es válida, se usa.
    - Si no tiene rareza definida, se asigna la más común de las disponibles.
    """
    if "rareza" not in objeto or not objeto["rareza"].strip():
        rarezas_validas = list(obtener_rarezas_validas())
        # Prioridad: rareza preferida si es válida
        if preferida and preferida in rarezas_validas:
            objeto["rareza"] = preferida
        elif rarezas_validas:
            # Usamos la primera (más común) disponible
            objeto["rareza"] = rarezas_validas[0]
        else:
            objeto["rareza"] = "Común"  # fallback seguro

    # Normalizamos: minúsculas y sin espacios extra
    objeto["rareza"] = objeto["rareza"].strip().lower()
    return objeto

# ─────────────────────────────
# Función auxiliar para elegir rareza con estética mejorada
# ─────────────────────────────
def seleccionar_rareza(default=None, prompt=None):
    rarezas_validas = sorted(obtener_rarezas_validas(), key=lambda x: x.lower())
    if not rarezas_validas:
        print("❌ No hay rarezas válidas disponibles, usando 'común'.")
        return "común"

    while True:
        print("\nRarezas disponibles:")
        for i, nombre in enumerate(rarezas_validas, 1):
            config = obtener_definicion_rareza(nombre)
            print(f"{nombre}:")
            if config and config.get("descripcion"):
                print(f"    - {config['descripcion']}")
            if config and "peso" in config:
                print(f"    - Peso: {config['peso']}")
            else:
                print(f"    - Peso: 1.0")  # fallback si no tiene peso

        msg = f"{prompt} [{default}]: " if prompt else f"Selecciona rareza [{default}]: "
        entrada = input(msg).strip()
        if not entrada and default:
            return default.lower()
        elif entrada.isdigit():
            idx = int(entrada) - 1
            if 0 <= idx < len(rarezas_validas):
                return rarezas_validas[idx].lower()
        elif entrada in rarezas_validas:
            return entrada.lower()

        print("❌ Entrada inválida. Intenta de nuevo.")