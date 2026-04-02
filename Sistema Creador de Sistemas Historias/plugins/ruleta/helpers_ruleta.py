# plugins/ruleta/helpers_ruleta.py

from core.estado_global import estado
from core.guardado.archivos import guardar_sistema
from core.utils.funciones_utiles import sync_plugin_cache
from core.recompensas.aplicar import aplicar_recompensas
from core.recompensas.ui_preparacion import preparar_recompensa_para_aplicar
from core.recompensas.tipos import obtener_definicion_rareza
from core.recompensas.bloques import menu_editar_bloque_interactivo
from core.recompensas.tipos import es_rareza_valida, normalizar_rareza_texto
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
# NORMALIZAR PREMIOS (RECURSOS)/EVENTOS NARRATIVOS
# ----------------------------
def normalizar_premios(bloque):
    """
    Normaliza un bloque de premios:
    - Asegura estructuras correctas (lista/dict)
    - Normaliza rarezas correctamente (capitalización consistente)
    - NO fuerza rareza por defecto innecesariamente
    - Evita mutaciones del original
    """

    bloque_final = {}

    if not isinstance(bloque, dict):
        return bloque_final

    for tipo, items in bloque.items():

        # ─────────────────────────────
        # 🔹 OBJETOS → LISTA
        # ─────────────────────────────
        if tipo == "objetos":

            bloque_final[tipo] = []

            if not isinstance(items, list):
                continue

            for obj in items:

                if not isinstance(obj, dict):
                    continue

                nuevo = obj.copy()

                # -------------------------
                # 🧬 NORMALIZAR RAREZA
                # -------------------------
                rareza = nuevo.get("rareza")

                if rareza:
                    rareza_norm = normalizar_rareza_texto(rareza)

                    if es_rareza_valida(rareza_norm):
                        nuevo["rareza"] = rareza_norm
                    else:
                        print(f"⚠ Rareza inválida en objeto '{nuevo.get('nombre','?')}', eliminada.")
                        nuevo.pop("rareza", None)

                # ⚠ IMPORTANTE: NO poner "común" automáticamente

                # -------------------------
                # 📦 NORMALIZAR CANTIDAD
                # -------------------------
                if "cantidad" not in nuevo and "cantidad_base" not in nuevo:
                    nuevo["cantidad"] = 1

                bloque_final[tipo].append(nuevo)

            continue

        # ─────────────────────────────
        # 🔹 RESTO DE TIPOS → DICT
        # ─────────────────────────────
        bloque_final[tipo] = {}

        if not isinstance(items, dict):
            continue

        for nombre, info in items.items():

            if not isinstance(info, dict):
                continue

            nuevo = info.copy()

            # -------------------------
            # 🧬 NORMALIZAR RAREZA
            # -------------------------
            rareza = nuevo.get("rareza")

            if rareza:
                rareza_norm = normalizar_rareza_texto(rareza)

                if es_rareza_valida(rareza_norm):
                    nuevo["rareza"] = rareza_norm
                else:
                    print(f"⚠ Rareza inválida en '{nombre}', eliminada.")
                    nuevo.pop("rareza", None)

            # ⚠ IMPORTANTE: NO poner "común" automáticamente

            # -------------------------
            # 🔢 NORMALIZAR VALOR
            # -------------------------
            if (
                "valor_base" not in nuevo and
                "valor" not in nuevo and
                "cantidad" not in nuevo
            ):
                nuevo["valor_base"] = 1

            bloque_final[tipo][nombre] = nuevo

    return bloque_final

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
    
# ----------------------------
# CREAR RULETA
# ----------------------------
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

# ----------------------------
# MODIFICAR/ELIMINAR/DUPLICAR RULETA
# ----------------------------
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

def duplicar_ruleta(
    sistema: dict,
    ruleta_id_origen: str,
    nueva_id: str,
    nuevo_nombre: str,
    nueva_descripcion: str,
    premios_seleccion: str = "todos",
    eventos_seleccion: str = "todos"
) -> bool:
    ruletas = sistema.get("ruleta", {}).get("activas", {})
    if not ruletas or ruleta_id_origen not in ruletas or nueva_id in ruletas:
        return False
    if not nueva_id.strip() or not nueva_descripcion.strip():
        return False

    ruleta_original = ruletas[ruleta_id_origen]
    ruleta_copia = deepcopy(ruleta_original)

    # Premios
    if premios_seleccion == "ninguno":
        ruleta_copia["premios"] = {}
    elif isinstance(premios_seleccion, list):
        ruleta_copia["premios"] = {k: v for k, v in ruleta_copia.get("premios", {}).items() if k in premios_seleccion}

    # Eventos
    if eventos_seleccion == "ninguno":
        ruleta_copia["eventos_narrativos"] = []
    elif isinstance(eventos_seleccion, list):
        ruleta_copia["eventos_narrativos"] = [ruleta_copia["eventos_narrativos"][i] for i in eventos_seleccion if 0 <= i < len(ruleta_copia["eventos_narrativos"])]

    ruleta_copia["id"] = nueva_id
    ruleta_copia["nombre"] = nuevo_nombre
    ruleta_copia["descripcion"] = nueva_descripcion

    # Normalizar antes de añadir
    ruleta_copia["premios"] = normalizar_premios(ruleta_copia.get("premios", {}))
    ruleta_copia["eventos_narrativos"] = normalizar_eventos(ruleta_copia.get("eventos_narrativos", []))

    ruletas[nueva_id] = ruleta_copia
    estado.cambios_no_guardados = True
    return True

# ----------------------------
# GESTION RULETA
# ----------------------------
def gestion_ruleta(sistema, ruleta, ruletas_list):
    """
    Menú interno para administrar una ruleta:
    - Tirar ruleta (1 vez)
    - Tiradas múltiples
    - Eliminar
    - Volver
    """
    while True:
        # -------------------------
        # INFORMACIÓN RULETA
        # -------------------------
        print(f"\n--- RULETA: {ruleta['nombre']} ---")
        print(f"ID: {ruleta['id']}")
        print(f"Descripción: {ruleta.get('descripcion', '')}")
        print(f"Tiradas realizadas: {ruleta.get('tiradas_realizadas', 0)}")

        premios = ruleta.get("premios", {})
        eventos = ruleta.get("eventos_narrativos", [])

        total_premios = contar_premios_ruleta(ruleta)
        print(f"Total premios: {total_premios}")

        # -------------------------
        # PREMIOS SISTEMA
        # -------------------------
        total_sistema = sum(len(items) if isinstance(items, list) else len(items.keys()) if isinstance(items, dict) else 0 for items in premios.values())
        print(f"\n🎁 Premios sistema: {total_sistema}")

        if total_sistema == 0:
            print("    (sin premios)")
        else:
            for tipo, items in premios.items():
                if isinstance(items, list):
                    for obj in items:
                        nombre = obj.get("nombre", "Premio")
                        desc = obj.get("descripcion", "")
                        rareza = obj.get("rareza", "-")
                        cantidad = obj.get("valor_base") or obj.get("cantidad") or 1

                        linea = f"    - {nombre} x{cantidad}"
                        if desc:
                            linea += f" ({desc})"
                        if rareza:
                            linea += f" [{rareza}]"

                        print(linea)

                elif isinstance(items, dict):
                    for k, v in items.items():
                        cantidad = v.get("valor_base") or v.get("cantidad") or 1
                        rareza = v.get("rareza", "-")

                        linea = f"    - {k} x{cantidad} [{rareza}]"
                        print(linea)

        # -------------------------
        # EVENTOS
        # -------------------------
        print(f"\n📖 Eventos narrativos: {len(eventos)}")
        if not eventos:
            print("    (sin eventos)")
        else:
            for e in eventos:
                texto = e.get("titulo", "Evento")
                rareza = e.get("rareza", "-")
                print(f"    - {texto} [{rareza}]")

        # -------------------------
        # MENÚ
        # -------------------------
        print("\n[T] Tirar 1 vez   [M] Tiradas múltiples   [D] Eliminar   [Enter] Volver")
        accion = input("> ").strip().lower()

        # -------------------------
        # TIRADA SIMPLE
        # -------------------------
        if accion == "t":
            tirar_ruleta_una_vez(sistema, ruleta["id"])
            continue

        # -------------------------
        # TIRADAS MÚLTIPLES
        # -------------------------
        elif accion == "m":
            tirar_ruleta_multiples_veces(sistema, ruleta["id"])
            continue

        # -------------------------
        # ELIMINAR
        # -------------------------
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

        # -------------------------
        # VOLVER
        # -------------------------
        else:
            break

# ----------------------------
# TIRADAS SIMPLES Y MULTIPLES
# ----------------------------
def tirar_ruleta_una_vez(sistema, ruleta_id):
    """
    Ejecuta UNA tirada de ruleta.
    - Pregunta qué recurso gastar.
    - Hace 1 sola tirada.
    """
    inicializar_ruletas(sistema)

    ruleta = sistema["ruleta"]["activas"].get(ruleta_id)
    if not ruleta:
        print("❌ Ruleta no encontrada.")
        return None

    # -------------------------
    # COSTE (solo 1 tirada)
    # -------------------------
    tipo = seleccionar_tipo_coste()
    if tipo is None:
        return None

    if tipo != "gratis":
        subtipo = seleccionar_subtipo_recurso(sistema, tipo)
        if not subtipo:
            return None

        # comprobar que tiene al menos 1 recurso
        if calcular_max_tiradas(sistema, tipo, subtipo) <= 0:
            print("❌ No tienes recursos.")
            return None

        # gastar SOLO 1
        if not gastar_recurso(sistema, tipo, subtipo, 1):
            return None
    else:
        subtipo = None

    # -------------------------
    # EJECUTAR 1 TIRADA
    # -------------------------
    r = obtener_resultado_ruleta(ruleta)
    if not r:
        print("❌ No hay resultados en la ruleta.")
        return None

    procesar_resultado(sistema, ruleta, r, mostrar=False)

    # -------------------------
    # MOSTRAR RESULTADO
    # -------------------------
    print("\n=== RESULTADO ===")

    data = r["data"]
    nombre = data.get("nombre") or data.get("titulo") or "evento"
    rareza = data.get("rareza", "-")
    cantidad_ganada = data.get("valor") or data.get("cantidad") or 1

    print(f"*** ¡Obtuviste {nombre} x{cantidad_ganada} [{rareza}]! ***")

    # -------------------------
    # GUARDAR
    # -------------------------
    estado.cambios_no_guardados = True
    guardar_sistema(print_msg=False)

    return [r]

def tirar_ruleta_multiples_veces(sistema, ruleta_id):
    """
    Ejecuta múltiples tiradas de ruleta de forma controlada.
    - Pregunta recurso
    - Pregunta cantidad
    - Limita por recursos disponibles
    """

    inicializar_ruletas(sistema)
    ruleta = sistema["ruleta"]["activas"].get(ruleta_id)
    if not ruleta:
        print("❌ Ruleta no encontrada.")
        return None

    # -------------------------
    # COSTE
    # -------------------------
    tipo = seleccionar_tipo_coste()
    if tipo is None:
        return None

    if tipo != "gratis":
        subtipo = seleccionar_subtipo_recurso(sistema, tipo)
        if not subtipo:
            return None

        max_tiradas = calcular_max_tiradas(sistema, tipo, subtipo)
        if max_tiradas <= 0:
            print("❌ No tienes recursos.")
            return None
    else:
        subtipo = None
        max_tiradas = 999999  # gratis limitado luego manualmente

    # -------------------------
    # CANTIDAD
    # -------------------------
    while True:
        try:
            cantidad = int(input(f"¿Cuántas tiradas? (max {max_tiradas}): ") or "1")
        except ValueError:
            print("❌ Número inválido.")
            continue

        if cantidad <= 0:
            print("❌ Cantidad inválida.")
            continue

        if cantidad > max_tiradas:
            print(f"❌ No tienes suficientes recursos. Máximo permitido: {max_tiradas}")
            continue

        break

    # 🔥 SEGURIDAD EXTRA
    LIMITE_DURO = 1000
    if cantidad > LIMITE_DURO:
        print(f"⚠ Límite máximo de seguridad: {LIMITE_DURO}")
        cantidad = LIMITE_DURO

    # -------------------------
    # GASTAR RECURSOS
    # -------------------------
    if tipo != "gratis":
        if not gastar_recurso(sistema, tipo, subtipo, cantidad):
            return None

    # -------------------------
    # EJECUTAR TIRADAS
    # -------------------------
    resultados = []
    for _ in range(cantidad):
        r = obtener_resultado_ruleta(ruleta)
        if not r:
            break
        resultados.append(r)
        procesar_resultado(sistema, ruleta, r, mostrar=(cantidad <= 5))

    # -------------------------
    # MOSTRAR RESUMEN
    # -------------------------
    if cantidad > 5:
        resumen = {}
        for r in resultados:
            data = r["data"]
            nombre = data.get("nombre") or data.get("titulo") or "evento"
            rareza = data.get("rareza", "-")
            cantidad_ganada = data.get("valor") or data.get("cantidad") or 1

            if nombre not in resumen:
                resumen[nombre] = {"cantidad": 0, "rareza": rareza}

            resumen[nombre]["cantidad"] += cantidad_ganada

        print("\n=== RESULTADOS ===")
        for nombre, info in resumen.items():
            print(f"*** ¡Obtuviste {nombre} x{info['cantidad']} [{info['rareza']}]! ***")

    # -------------------------
    # GUARDAR
    # -------------------------
    estado.cambios_no_guardados = True
    guardar_sistema(print_msg=False)

    return resultados

# ----------------------------
# OBTENER/PROCESAR RESULTADO
# ----------------------------
def obtener_resultado_ruleta(ruleta):
    opciones = []

    premios = normalizar_premios(ruleta.get("premios", {}))

    # 🎁 PREMIOS
    for tipo, items in premios.items():
        if isinstance(items, list):
            for obj in items:
                rareza = obj.get("rareza")
                peso = 1.0
                if rareza:
                    definicion = obtener_definicion_rareza(normalizar_rareza_texto(rareza))
                    if definicion:
                        peso = definicion.get("peso", 1.0)
                opciones.append({"tipo": "sistema", "subtipo": tipo, "data": obj, "peso": peso})
        elif isinstance(items, dict):
            for nombre, info in items.items():
                rareza = info.get("rareza")
                peso = 1.0
                if rareza:
                    definicion = obtener_definicion_rareza(normalizar_rareza_texto(rareza))
                    if definicion:
                        peso = definicion.get("peso", 1.0)
                data = {"nombre": nombre, **info}
                opciones.append({"tipo": "sistema", "subtipo": tipo, "data": data, "peso": peso})

    # 📖 EVENTOS
    for ev in ruleta.get("eventos_narrativos", []):
        rareza = ev.get("rareza")
        peso = 1.0
        if rareza:
            definicion = obtener_definicion_rareza(normalizar_rareza_texto(rareza))
            if definicion:
                peso = definicion.get("peso", 1.0)
        opciones.append({"tipo": "narrativo", "data": ev, "peso": peso})

    if not opciones:
        return None

    total_peso = sum(op["peso"] for op in opciones)
    if total_peso <= 0:
        total_peso = len(opciones)  # fallback para pesos inválidos

    r = random.uniform(0, total_peso)
    acumulado = 0
    for op in opciones:
        acumulado += op["peso"]
        if r <= acumulado:
            return op

    return opciones[-1]

def procesar_resultado(sistema, ruleta, resultado, mostrar=True):
    if not resultado:
        return

    tipo = resultado["tipo"]
    data = deepcopy(resultado["data"])  # Copia para no mutar original
    rareza = data.get("rareza", "-")

    if tipo == "sistema":
        subtipo = resultado["subtipo"]
        recompensa = {subtipo: {}}

        if isinstance(ruleta["premios"].get(subtipo), list):
            cantidad = data.pop("cantidad_base", data.pop("cantidad", 1))
            data["cantidad"] = cantidad
            recompensa[subtipo] = {data.get("nombre", "objeto"): data}
        else:
            valor = data.get("valor", data.get("cantidad", 1))
            data["valor"] = valor
            recompensa[subtipo] = {data.get("nombre", "recurso"): data}

        aplicar_recompensas(
            sistema,
            preparar_recompensa_para_aplicar(sistema, recompensa)
        )

        if mostrar:
            print(f"🎉 {data.get('nombre', 'recurso')} x{data.get('cantidad', data.get('valor',1))} [{rareza}]")

    else:  # narrativo
        if mostrar:
            print(f"📖 {data.get('titulo', 'Evento')} [{rareza}]")

    # actualizar contador
    ruleta["tiradas_realizadas"] = ruleta.get("tiradas_realizadas", 0) + 1

# ----------------------------
# CALCULAR COSTO/ GASTAR RECURSO
# ----------------------------
def calcular_max_tiradas(sistema, tipo, subtipo, coste=1):
    if tipo == "gratis":
        return float("inf")

    disponibles = sistema.get(tipo, {}).get(subtipo, 0)
    return disponibles // coste

def gastar_recurso(sistema, tipo, subtipo, cantidad=1):
    recursos = sistema.setdefault(tipo, {})

    actual = recursos.get(subtipo, 0)

    if actual < cantidad:
        print(f"❌ No tienes suficiente {subtipo}. ({actual}/{cantidad})")
        return False

    recursos[subtipo] -= cantidad
    return True

# ----------------------------
# SELECCIONAR TIPO Y SUBTIPO
# ----------------------------
def seleccionar_tipo_coste(auto=False):
    print("\n--- COSTE DE TIRADA ---")
    opciones = []

    if not auto:
        print("1. Gratis")
        opciones.append("gratis")

    print("2. Usar tiradas")
    opciones.append("tiradas")
    print("3. Usar dinero")
    opciones.append("dinero")

    op = input("> ").strip()

    if op == "1" and not auto:
        return "gratis"
    elif op == "2":
        return "tiradas"
    elif op == "3":
        return "dinero"

    print("❌ Selección inválida.")
    return None
    
def seleccionar_subtipo_recurso(sistema, tipo):
    recursos = sistema.setdefault(tipo, {})

    if not recursos:
        print(f"\n⚠ No hay subtipos de {tipo}. Vamos a crear uno.")
        nombre = input(f"Nombre del nuevo subtipo de {tipo}: ").strip()
        recursos[nombre] = 0
        return nombre

    print(f"\n--- {tipo.upper()} DISPONIBLES ---")
    lista = list(recursos.keys())

    for i, nombre in enumerate(lista, 1):
        print(f"{i}. {nombre} ({recursos[nombre]})")

    print(f"{len(lista)+1}. Crear nuevo")

    op = input("> ").strip()

    if op.isdigit():
        idx = int(op) - 1

        if 0 <= idx < len(lista):
            return lista[idx]

        elif idx == len(lista):
            nombre = input(f"Nuevo subtipo de {tipo}: ").strip()
            recursos[nombre] = 0
            return nombre

    print("❌ Selección inválida.")
    return None

# ----------------------------
# CONTAR PREMIOS TOTALES
# ----------------------------
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









