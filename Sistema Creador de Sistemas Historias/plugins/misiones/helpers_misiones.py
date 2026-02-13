# plugins/misiones/helpers_misiones.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.recompensas.aplicar import aplicar_recompensas
from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
from core.utils.funciones_utiles import sync_plugin_cache
from plugins.misiones.modelos import crear_modelo_mision


# --------------------------------------------------
# Infraestructura
# --------------------------------------------------
def asegurar_misiones(sistema):
    sistema.setdefault("misiones", {})
    sistema["misiones"].setdefault("activas", {})

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
    sync_plugin_cache(sistema, "misiones", ["activas"])
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
        sync_plugin_cache(sistema, "misiones", ["activas"])
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

