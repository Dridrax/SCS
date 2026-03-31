# plugins/ruleta/helpers_ruleta.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import sync_plugin_cache
from core.recompensas.aplicar import aplicar_recompensas
from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
from core.recompensas.tipos import obtener_definicion_rareza
from core.recompensas.bloques import menu_editar_bloque_interactivo
from core.recompensas.tipos import es_rareza_valida
import random
from copy import deepcopy


def inicializar_ruletas(sistema):
    """
    Asegura la estructura principal de ruletas en el sistema.
    """
    sistema.setdefault("ruleta", {}).setdefault("activas", {})
    sistema["ruleta"].setdefault("historial", [])
    sync_plugin_cache(sistema, "ruleta", ["activas", "historial"])

# ----------------------------
# NORMALIZAR PREMIOS (RECURSOS)
# ----------------------------
def normalizar_premios(bloque):
    """
    Normaliza un bloque de premios:
    - Convierte listas/diccionarios según tipo.
    - Valida rareza solo si existe.
    """
    bloque_final = {}

    for tipo, items in (bloque or {}).items():

        # 🔹 OBJETOS → LISTA
        if tipo == "objetos":
            bloque_final[tipo] = []

            for obj in items or []:
                nuevo = obj.copy()

                rareza = nuevo.get("rareza")
                if rareza:
                    if es_rareza_valida(rareza):
                        # rareza válida → mantener
                        pass
                    else:
                        print(f"⚠ Rareza inválida en objeto '{nuevo.get('nombre','?')}', eliminada.")
                        nuevo.pop("rareza", None)
                else:
                    nuevo.pop("rareza", None)

                bloque_final[tipo].append(nuevo)
            continue

        # 🔹 RESTO DE TIPOS → dict normal
        bloque_final[tipo] = {}
        for nombre, info in (items or {}).items():
            bloque_final[tipo][nombre] = info.copy()

    return bloque_final

# ----------------------------
# NORMALIZAR EVENTOS NARRATIVOS
# ----------------------------
def normalizar_eventos(eventos):
    lista = []

    for ev in eventos or []:
        if not isinstance(ev, dict):
            continue

        nuevo = {
            "titulo": ev.get("titulo", "Evento"),
            "descripcion": ev.get("descripcion", "")
        }

        rareza = ev.get("rareza")

        # 🔥 Solo validar si existe
        if rareza:
            if es_rareza_valida(rareza):
                nuevo["rareza"] = rareza
            else:
                print(f"⚠ Rareza inválida en evento '{nuevo['titulo']}', ignorada.")

        lista.append(nuevo)

    return lista
    
def crear_ruleta(
    sistema,
    *,
    id,
    nombre,
    descripcion="",
    premios=None,
    eventos_narrativos=None
):
    """
    Crea una ruleta con:
    - Premios de recursos (bloques de recompensas)
    - Eventos narrativos (para escritura creativa)
    """

    inicializar_ruletas(sistema)
    activas = sistema["ruleta"]["activas"]

    if id in activas:
        print("❌ Ya existe una ruleta con ese ID.")
        return False

    # ----------------------------
    # CREAR RULETA
    # ----------------------------
    activas[id] = {
        "id": id,
        "nombre": nombre,
        "descripcion": descripcion,

        # 🔹 Normalizar antes de guardar
        "premios": normalizar_premios(premios),
        "eventos_narrativos": normalizar_eventos(eventos_narrativos),

        "tiradas_realizadas": 0
    }

    estado.cambios_no_guardados = True
    sync_plugin_cache(sistema, "ruleta", ["activas", "historial"])
    guardar_sistema(print_msg=False)

    print(f"✅ Ruleta '{nombre}' creada correctamente.")
    return True

def modificar_ruleta(
    sistema,
    ruleta_id,
    *,
    nombre=None,
    descripcion=None,
    premios=None,
    eventos_narrativos=None
):
    """
    Modifica una ruleta existente.

    ⚠️ NO modifica el ID.

    Parámetros opcionales:
    - nombre
    - descripcion
    - premios (bloque completo)
    - eventos_narrativos (lista completa)
    """

    inicializar_ruletas(sistema)
    ruleta = sistema["ruleta"]["activas"].get(ruleta_id)

    if not ruleta:
        print("❌ No existe esa ruleta.")
        return False

    # -------------------------
    # 🟢 ACTUALIZAR DATOS BÁSICOS
    # -------------------------
    if nombre is not None:
        ruleta["nombre"] = nombre

    if descripcion is not None:
        ruleta["descripcion"] = descripcion

    # -------------------------
    # 🎁 PREMIOS (REEMPLAZO COMPLETO)
    # -------------------------
    if premios is not None:
        ruleta["premios"] = normalizar_premios(premios)

    # -------------------------
    # 📖 EVENTOS NARRATIVOS
    # -------------------------
    if eventos_narrativos is not None:
        ruleta["eventos_narrativos"] = eventos_narrativos

    # -------------------------
    # 💾 GUARDADO
    # -------------------------
    estado.cambios_no_guardados = True
    sync_plugin_cache(sistema, "ruleta", ["activas", "historial"])
    guardar_sistema(print_msg=False)

    print("✅ Ruleta modificada correctamente.")
    return True

def eliminar_ruleta(sistema, ruleta_id):
    """
    Elimina una ruleta del sistema con doble confirmación de seguridad.
    """
    inicializar_ruletas(sistema)
    activas = sistema["ruleta"]["activas"]

    if ruleta_id not in activas:
        print("❌ No existe esa ruleta.")
        return False

    ruleta = activas[ruleta_id]

    # -------------------------
    # 🔎 MOSTRAR INFO
    # -------------------------
    print("\n⚠️ Estás a punto de eliminar la siguiente ruleta:")
    print(f"Nombre: {ruleta['nombre']}")
    print(f"Descripción: {ruleta.get('descripcion', '')}")

    total_premios = 0

    # Premios sistema
    for tipo, items in ruleta.get("premios", {}).items():
        if isinstance(items, dict):
            total_premios += len(items)
        elif isinstance(items, list):
            total_premios += len(items)

    # Eventos narrativos
    total_premios += len(ruleta.get("eventos_narrativos", []))

    print(f"Total de premios/eventos: {total_premios}")

    # -------------------------
    # ⚠️ PRIMERA CONFIRMACIÓN
    # -------------------------
    confirmar = input("\n¿Seguro que quieres eliminar esta ruleta? (s/n): ").strip().lower()
    if confirmar != "s":
        print("❌ Eliminación cancelada.")
        return False

    # -------------------------
    # 🔐 SEGUNDA CONFIRMACIÓN (ANTI ERRORES)
    # -------------------------
    confirmacion_final = input(
        f"Escribe el ID de la ruleta para confirmar ('{ruleta_id}'): "
    ).strip()

    if confirmacion_final != ruleta_id:
        print("❌ ID incorrecto. Eliminación cancelada.")
        return False

    # -------------------------
    # 🗑 ELIMINAR
    # -------------------------
    del activas[ruleta_id]

    # -------------------------
    # 🔄 SINCRONIZAR Y GUARDAR
    # -------------------------
    sync_plugin_cache(sistema, "ruleta", ["activas", "historial"])
    estado.cambios_no_guardados = True
    guardar_sistema(print_msg=False)

    print("✅ Ruleta eliminada correctamente.")
    return True

def tirar_ruleta(sistema, ruleta_id):
    """
    Tirar la ruleta usando probabilidades basadas en rareza.
    Puede devolver:
    - Premio de sistema (se aplica)
    - Evento narrativo (solo se muestra)
    """
    import random

    inicializar_ruletas(sistema)

    ruleta = sistema["ruleta"]["activas"].get(ruleta_id)
    if not ruleta:
        print("❌ Ruleta no encontrada.")
        return None

    opciones = []

    # -------------------------
    # 🎁 PREMIOS SISTEMA
    # -------------------------
    premios = ruleta.get("premios", {})
    premios = normalizar_premios(premios)

    for tipo, items in premios.items():

        # OBJETOS (lista)
        if isinstance(items, list):
            for obj in items:
                rareza = obj.get("rareza")
                peso = 1.0
                if rareza:
                    definicion = obtener_definicion_rareza(rareza.capitalize())
                    if definicion:
                        peso = definicion.get("peso", 1.0)
                opciones.append({
                    "tipo": "sistema",
                    "subtipo": tipo,
                    "data": obj,
                    "peso": peso
                })

        # RECURSOS (dict)
        elif isinstance(items, dict):
            for nombre, info in items.items():
                rareza = info.get("rareza")
                peso = 1.0
                if rareza:
                    definicion = obtener_definicion_rareza(rareza.capitalize())
                    if definicion:
                        peso = definicion.get("peso", 1.0)
                opciones.append({
                    "tipo": "sistema",
                    "subtipo": tipo,
                    "data": {"nombre": nombre, **info},
                    "peso": peso
                })

    # -------------------------
    # 📖 EVENTOS NARRATIVOS
    # -------------------------
    eventos = ruleta.get("eventos_narrativos", [])

    for ev in eventos:
        rareza = ev.get("rareza")
        peso = 1.0
        if rareza:
            definicion = obtener_definicion_rareza(rareza.capitalize())
            if definicion:
                peso = definicion.get("peso", 1.0)
        opciones.append({
            "tipo": "narrativo",
            "data": ev,
            "peso": peso
        })

    # -------------------------
    # ❌ SIN OPCIONES
    # -------------------------
    if not opciones:
        print("⚠ No hay premios disponibles en la ruleta.")
        return None

    # -------------------------
    # 🎲 ELECCIÓN POR PESO
    # -------------------------
    total_peso = sum(op["peso"] for op in opciones)
    r = random.uniform(0, total_peso)
    acumulado = 0
    premio_ganado = None

    for op in opciones:
        acumulado += op["peso"]
        if r <= acumulado:
            premio_ganado = op
            break

    if not premio_ganado:
        return None

    # -------------------------
    # 🎁 APLICAR PREMIO SISTEMA
    # -------------------------
    if premio_ganado["tipo"] == "sistema":
        subtipo = premio_ganado["subtipo"]
        data = premio_ganado["data"]

        recompensa = {subtipo: {}}

        if isinstance(premios.get(subtipo), list):
            # Copiar solo campos relevantes para aplicar recompensa
            copia_obj = data.copy()
            cantidad = copia_obj.pop("cantidad_base", copia_obj.pop("cantidad", 1))
            copia_obj["cantidad"] = cantidad
            recompensa[subtipo] = {copia_obj.get("nombre", "objeto"): copia_obj}
        else:
            # Recursos tipo dict
            valor = data.get("valor", data.get("cantidad", 1))
            copia_info = data.copy()
            copia_info["valor"] = valor
            recompensa[subtipo] = {data.get("nombre", "recurso"): copia_info}

        aplicar_recompensas(
            sistema,
            preparar_recompensa_para_aplicar(sistema, recompensa)
        )

        nombre = data.get("nombre", "recurso")
        desc = data.get("descripcion", "")
        rareza = data.get("rareza", "sin rareza")
        cantidad = data.get("valor_base", "sin cantidad")

        print("\n🎉 PREMIO OBTENIDO")
        print(f"Tipo: {subtipo}")
        print(f"Rareza: {rareza}")
        if desc:
            print(f"Descripción: {desc}")
        print(f"Nombre: {nombre}")
        print(f"Cantidad: {cantidad}")

    # -------------------------
    # 📖 EVENTO NARRATIVO
    # -------------------------
    else:
        ev = premio_ganado["data"]
        tipo_ev = ev.get("tipo", "evento")
        rareza = ev.get("rareza", "sin rareza")
        titulo = ev.get("titulo", "Evento")
        descripcion = ev.get("descripcion", "")

        print("\n📖 EVENTO NARRATIVO")
        print(f"Tipo: {tipo_ev}")
        print(f"Rareza: {rareza}")
        print(f"Titulo: {titulo}")
        if descripcion:
            print(f"Descripción: {descripcion}")

    # -------------------------
    # 📊 ACTUALIZAR ESTADO
    # -------------------------
    ruleta["tiradas_realizadas"] = ruleta.get("tiradas_realizadas", 0) + 1
    estado.cambios_no_guardados = True
    guardar_sistema(print_msg=False)

    return premio_ganado

def contar_premios_ruleta(ruleta):
    total = 0
    premios = ruleta.get("premios", {})
    eventos = ruleta.get("eventos_narrativos", [])

    for items in premios.values():
        if isinstance(items, list):
            total += len(items)
        elif isinstance(items, dict):
            total += len(items)

    total += len(eventos)
    return total

def gestion_ruleta(sistema, ruleta, ruletas_list):
    """
    Menú interno para administrar una ruleta:
    - Tirar ruleta
    - Ver detalles
    - Eliminar
    - Volver
    """

    while True:
        print(f"\n--- RULETA: {ruleta['nombre']} ---")
        print(f"ID: {ruleta['id']}")
        print(f"Descripción: {ruleta.get('descripcion', '')}")
        print(f"Tiradas realizadas: {ruleta.get('tiradas_realizadas', 0)}")

        premios = ruleta.get("premios", {})
        eventos = ruleta.get("eventos_narrativos", [])

        total_premios = contar_premios_ruleta(ruleta)
        print(f"Total premios: {total_premios}")

        # ==================================================
        # 🎁 PREMIOS SISTEMA (DETALLADOS)
        # ==================================================
        total_sistema = 0
        for items in premios.values():
            if isinstance(items, list):
                total_sistema += len(items)
            elif isinstance(items, dict):
                total_sistema += len(items)

        print(f"\n🎁 Premios sistema: {total_sistema}")

        if total_sistema == 0:
            print("    (sin premios)")
        else:
            for tipo, items in premios.items():

                # LISTAS
                if isinstance(items, list):
                    for obj in items:
                        nombre = obj.get("nombre", "Premio")
                        desc = obj.get("descripcion", "")
                        rareza = obj.get("rareza")

                        linea = f"    - {nombre}"
                        if desc:
                            linea += f" ({desc})"
                        if rareza:
                            linea += f" [{rareza}]"

                        print(linea)

                # DICCIONARIOS
                elif isinstance(items, dict):
                    for k, v in items.items():
                        valor = v.get("valor", v.get("cantidad", ""))
                        rareza = v.get("rareza")

                        linea = f"    - {k}: {valor}"
                        if rareza:
                            linea += f" [{rareza}]"

                        print(linea)

        # ==================================================
        # 📖 EVENTOS NARRATIVOS (DETALLADOS)
        # ==================================================
        print(f"\n📖 Eventos narrativos: {len(eventos)}")

        if not eventos:
            print("    (sin eventos)")
        else:
            for e in eventos:
                texto = e.get("texto", "Evento")
                rareza = e.get("rareza", "-")

                print(f"    - {texto} ({rareza})")

        # ==================================================
        # MENÚ
        # ==================================================
        print("\n[T] Tirar ruleta   [D] Eliminar   [Enter] Volver")
        accion = input("> ").strip().lower()

        # 🎡 TIRAR
        if accion == "t":
            resultado = tirar_ruleta(sistema, ruleta["id"])

            if resultado:
                # Mostrar mejor resultado (preparando para siguiente mejora)
                nombre = resultado.get("nombre") or resultado.get("texto") or "Premio"
                #print(f"\n🎉 Resultado: {nombre}")

            break

        # ❌ ELIMINAR
        elif accion == "d":
            confirmar = input("⚠ Confirmar eliminación (s/n): ").lower()
            if confirmar == "s":
                confirmar2 = input("⚠⚠ Escribe 'ELIMINAR' para confirmar: ").strip()
                if confirmar2 == "ELIMINAR":
                    eliminar_ruleta(sistema, ruleta["id"])
                    ruletas_list.remove(ruleta)
                    print("✅ Ruleta eliminada.")
                else:
                    print("❌ Cancelado.")
            break

        else:
            break

def duplicar_ruleta(
    sistema: dict,
    ruleta_id_origen: str,
    nueva_id: str,
    nuevo_nombre: str,
    nueva_descripcion: str,
    premios_seleccion: str = "todos",  # "todos", "ninguno" o lista de nombres de premios
    eventos_seleccion: str = "todos"   # "todos", "ninguno" o lista de ids de eventos
) -> bool:
    """
    Duplica una ruleta existente dentro del sistema, permitiendo seleccionar
    qué premios y qué eventos narrativos se quieren copiar.

    Args:
        sistema (dict): Diccionario principal con todas las ruletas.
        ruleta_id_origen (str): ID de la ruleta que quieres duplicar.
        nueva_id (str): Nueva ID única para la ruleta duplicada.
        nuevo_nombre (str): Nombre de la nueva ruleta.
        nueva_descripcion (str): Descripción de la nueva ruleta.
        premios_seleccion (str|list): "todos", "ninguno" o lista de nombres de premios.
        eventos_seleccion (str|list): "todos", "ninguno" o lista de IDs de eventos narrativos.

    Returns:
        bool: True si se duplicó correctamente, False si falló.
    """

    # Validaciones básicas
    ruletas = sistema.get("ruleta", {}).get("activas", {})

    if  not ruletas:
        return False

    if ruleta_id_origen not in ruletas:
        return False  # Ruleta original no existe

    if nueva_id in ruletas:
        return False  # Nueva ID ya existe

    if not nueva_id.strip() or not nueva_descripcion.strip():
        return False  # ID y descripción obligatorios

    # Hacer copia profunda de la ruleta original
    ruleta_original = ruletas[ruleta_id_origen]
    ruleta_copia = deepcopy(ruleta_original)

    # Filtrar premios
    if premios_seleccion == "ninguno":
        ruleta_copia["premios"] = {}
    elif isinstance(premios_seleccion, list):
        ruleta_copia["premios"] = {
            k: v for k, v in ruleta_copia.get("premios", {}).items() if k in premios_seleccion
        }

    # Filtrar eventos narrativos

    if eventos_seleccion == "ninguno":
        ruleta_copia["eventos_narrativos"] = []

    elif isinstance(eventos_seleccion, list):
        eventos_originales = ruleta_copia.get("eventos_narrativos", [])
        ruleta_copia["eventos_narrativos"] = [
            eventos_originales[i] for i in eventos_seleccion
            if 0 <= i < len(eventos_originales)
        ]

    # Asignar nuevos valores obligatorios
    ruleta_copia["id"] = nueva_id
    ruleta_copia["nombre"] = nuevo_nombre
    ruleta_copia["descripcion"] = nueva_descripcion

    # Añadir la copia al sistema
    ruletas[nueva_id] = ruleta_copia

    # Marcar cambios no guardados
    estado.cambios_no_guardados = True

    return True