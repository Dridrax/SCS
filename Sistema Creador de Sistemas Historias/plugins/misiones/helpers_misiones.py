# plugins/misiones/helpers_misiones.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.recompensas.aplicar import aplicar_recompensas
from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
from plugins.misiones.modelos import crear_modelo_mision

# --------------------------------------------------
# Infraestructura
# --------------------------------------------------
def asegurar_misiones(sistema):
    sistema.setdefault("misiones", {})
    sistema["misiones"].setdefault("activas", {})

def sync_misiones_plugin_cache(sistema):
    estado.plugin_cache.setdefault("plugins", {})
    estado.plugin_cache["plugins"]["misiones"] = {
        "activas": sistema.get("misiones", {}).get("activas", {})
    }

# --------------------------------------------------
# Crear / Obtener / Eliminar misiones
# --------------------------------------------------
def crear_mision(sistema, *, id, nombre, descripcion="", objetivo="", recompensas=None, penalizaciones=None):
    if not sistema:
        return None

    asegurar_misiones(sistema)
    if id in sistema["misiones"]["activas"]:
        return None

    mision = crear_modelo_mision(
        id=id,
        nombre=nombre,
        descripcion=descripcion,
        objetivo=objetivo,
        recompensas=recompensas or {},
        penalizaciones=penalizaciones or {}
    )

    sistema["misiones"]["activas"][id] = mision
    estado.cambios_no_guardados = True
    sync_misiones_plugin_cache(sistema)
    guardar_sistema()
    return mision

def obtener_mision(sistema, mision_id):
    asegurar_misiones(sistema)
    return sistema["misiones"]["activas"].get(mision_id)

def eliminar_mision_helper(sistema, mision_id):
    """Elimina sin confirmación, usado internamente"""
    asegurar_misiones(sistema)
    if mision_id in sistema["misiones"]["activas"]:
        del sistema["misiones"]["activas"][mision_id]
        estado.cambios_no_guardados = True
        sync_misiones_plugin_cache(sistema)
        guardar_sistema()
        return True
    return False

# --------------------------------------------------
# Modificar misión
# --------------------------------------------------
def editar_datos_basicos(mision, *, nombre=None, descripcion=None, objetivo=None):
    if nombre is not None:
        mision["nombre"] = nombre
    if descripcion is not None:
        mision["descripcion"] = descripcion
    if objetivo is not None:
        mision["objetivo"] = objetivo
    estado.cambios_no_guardados = True
    return mision

def obtener_bloque(mision, clave="recompensas"):
    return mision.setdefault(clave, {})

def agregar_recompensa(bloque, tipo, datos):
    if tipo == "objetos":
        bloque.setdefault("objetos", []).append(datos)
    elif tipo in {"stats", "dinero"}:
        k = datos.get("nombre")
        v = datos.get("valor", 0)
        bloque.setdefault(tipo, {})[k] = v
    elif tipo == "progress_stats":
        nombre = datos.get("nombre")
        bloque.setdefault("progress_stats", {})[nombre] = {
            "actual": datos.get("actual", 0),
            "nivel": datos.get("nivel", 1),
            "max": datos.get("max", 100)
        }
    elif tipo in {"puntos_stats", "nivel", "tiradas"}:
        bloque[tipo] = datos.get("valor", 0)
    else:
        return False
    estado.cambios_no_guardados = True
    return True

def editar_recompensa(bloque, tipo, clave=None, valor=None, index=None):
    if tipo == "objetos":
        if index is None or index >= len(bloque.get("objetos", [])):
            return False
        bloque["objetos"][index].update(valor or {})
    elif tipo in {"stats", "dinero"}:
        if clave is None:
            return False
        bloque[tipo][clave] = valor
    elif tipo == "progress_stats":
        if clave is None:
            return False
        bloque["progress_stats"][clave].update(valor or {})
    elif tipo in {"puntos_stats", "nivel", "tiradas"}:
        bloque[tipo] = valor
    else:
        return False
    estado.cambios_no_guardados = True
    return True

def eliminar_recompensa(bloque, tipo=None, clave=None, index=None):
    if tipo is None:
        bloque.clear()
    elif tipo == "objetos" and index is not None:
        bloque["objetos"].pop(index)
    elif tipo in bloque and clave:
        del bloque[tipo][clave]
    estado.cambios_no_guardados = True
    return True

# --------------------------------------------------
# Completar / Fallar misión
# --------------------------------------------------
def procesar_mision(sistema, mision_id, clave="recompensas"):
    misiones_activas = sistema.get("misiones", {}).get("activas", {})
    mision = misiones_activas.get(mision_id)
    if not mision:
        return False

    datos = mision.get(clave, {})
    if datos:
        datos_preparados = preparar_recompensa_para_aplicar(sistema, datos)
        aplicar_recompensas(sistema, datos_preparados)

    eliminar_mision_helper(sistema, mision_id)
    return True

def completar_mision(sistema, mision_id):
    return procesar_mision(sistema, mision_id, "recompensas")

def fallar_mision(sistema, mision_id):
    return procesar_mision(sistema, mision_id, "penalizaciones")

# --------------------------------------------------
# Menú interactivo helpers
# --------------------------------------------------
def imprimir_resultados(titulo, datos):
    print(f"{titulo}:")
    if not datos:
        print("  Ninguna")
        return
    for clave, valor in datos.items():
        if clave == "objetos":
            print("  Objetos:")
            for obj in valor:
                print(f"    - {obj.get('nombre','Desconocido')} | Cantidad: {obj.get('cantidad',0)} | Rareza: {obj.get('rareza','?')} | Tipo: {obj.get('tipo','?')}")
        elif isinstance(valor, dict):
            print(f"  {clave.capitalize()}:")
            for k, v in valor.items():
                if isinstance(v, dict) and "actual" in v:
                    print(f"    - {k}: {v['actual']}/{v['max']} (Nivel {v['nivel']})")
                else:
                    print(f"    - {k}: {v}")
        else:
            print(f"  {clave.capitalize()}: {valor}")



"""# Sistema de Misiones - Reglas Generales

## Principios básicos

- Las misiones NO crean sistemas nuevos.
- Todas las recompensas y penalizaciones solo se aplican
  sobre sistemas previamente existentes.
- Si un recurso no existe en el sistema, la recompensa se ignora.

Ejemplo:
Si una misión otorga `dinero`, pero el sistema no tiene el
parámetro `dinero`, dicha recompensa no se aplicará.

Esto garantiza:
- coherencia del sistema
- control total del administrador
- ausencia de efectos inesperados

## Recompensas y penalizaciones

- Las penalizaciones utilizan el mismo sistema que las recompensas,
  pero con valores negativos.
- Ambas pasan por el mismo proceso de validación.

## Eliminación de misiones

- Una misión se elimina tras completarse o fallarse.
- La eliminación ocurre después de aplicar recompensas o penalizaciones.
- Los cambios marcan el sistema como modificado.
"""