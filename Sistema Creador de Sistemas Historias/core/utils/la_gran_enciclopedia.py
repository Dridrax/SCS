from core.estado_global import estado

# ─────────────────────────────────────────────
# CONFIGURACIÓN CENTRAL
# ─────────────────────────────────────────────

MAPEO_SISTEMAS = {
    "inventario": "inventario",
    "habilidades": "habilidades",
    "titulos": "titulos",
    "bendiciones": "bendiciones",
    "maldiciones": "maldiciones",
    "notas": "notas",
    "bestiario": "bestiario",
}

# ─────────────────────────────────────────────
# FUNCIONES BASE
# ─────────────────────────────────────────────

def listar_enciclopedia(sistema):
    if not sistema:
        print("❌ No hay ningún sistema cargado.")
        return

    plugins = sistema.get("plugins_activos", {})
    enciclopedias = sistema.get("enciclopedias", {})

    tipos_disponibles = [
        tipo for tipo, activo in plugins.items()
        if activo and tipo in enciclopedias
    ]

    if not tipos_disponibles:
        print("⚠️ No hay enciclopedias activas.")
        return

    while True:
        print("\n=== LA GRAN ENCICLOPEDIA ===")
        for i, tipo in enumerate(tipos_disponibles, 1):
            print(f"{i}. {tipo.capitalize()}")
        print(f"{len(tipos_disponibles)+1}. Volver")

        try:
            opcion = int(input("Elige una sección: "))
        except ValueError:
            print("❌ Opción inválida.")
            continue

        if opcion == len(tipos_disponibles) + 1:
            break

        if 1 <= opcion <= len(tipos_disponibles):
            gestionar_enciclopedia_tipo(tipos_disponibles[opcion - 1])


# ─────────────────────────────────────────────
# GESTIÓN POR TIPO
# ─────────────────────────────────────────────

def gestionar_enciclopedia_tipo(tipo):
    sistema = estado.sistema_actual
    enciclopedia = sistema.get("enciclopedias", {}).get(tipo, [])

    if not enciclopedia:
        print("⚠️ No hay registros en esta enciclopedia.")
        return

    while True:
        print(f"\n=== ENCICLOPEDIA: {tipo.upper()} ===")

        for i, obj in enumerate(enciclopedia, 1):
            estado_str = "Activo ✅" if obj.get("activo", True) else "Inactivo ❌"
            clase = obj.get("clase", "")
            categoria = obj.get("categoria", "")
            extra = f" ({clase} | {categoria})" if clase or categoria else ""
            # Nombre visible según el tipo
            nombre_visible = (
                obj.get("nombre")
                or obj.get("titulo")
                or obj.get("id", "Sin nombre")
            )

            print(f"{i}. {nombre_visible}{extra} - {estado_str}")
            if tipo == "notas":
                extra = f" | {obj.get('contenido', '')[:30]}..."



        print(f"{len(enciclopedia)+1}. Volver")

        try:
            opcion = int(input("Selecciona un objeto para activar/desactivar: "))
        except ValueError:
            print("❌ Opción inválida.")
            continue

        if opcion == len(enciclopedia) + 1:
            break

        if 1 <= opcion <= len(enciclopedia):
            obj = enciclopedia[opcion - 1]

            if obj.get("activo", True):
                desactivar_objeto(sistema, tipo, obj["id"])
                print(f"❌ '{obj['nombre']}' desactivado.")
            else:
                reactivar_objeto(sistema, tipo, obj["id"])
                print(f"✅ '{obj['nombre']}' reactivado.")

            estado.cambios_no_guardados = True


# ─────────────────────────────────────────────
# ACTIVAR / DESACTIVAR
# ─────────────────────────────────────────────

def desactivar_objeto(sistema, tipo, id_objeto):
    enciclopedia = sistema["enciclopedias"].get(tipo, [])
    lista_activa_nombre = MAPEO_SISTEMAS.get(tipo)

    for obj in enciclopedia:
        if obj["id"] == id_objeto:
            obj["activo"] = False

            if lista_activa_nombre:
                sistema[lista_activa_nombre] = [
                    x for x in sistema.get(lista_activa_nombre, [])
                    if x["id"] != id_objeto
                ]
            return


def reactivar_objeto(sistema, tipo, id_objeto):
    enciclopedia = sistema["enciclopedias"].get(tipo, [])
    lista_activa_nombre = MAPEO_SISTEMAS.get(tipo)

    for obj in enciclopedia:
        if obj["id"] == id_objeto:
            obj["activo"] = True

            if lista_activa_nombre:
                sistema.setdefault(lista_activa_nombre, []).append(obj)
            return
        
# ─────────────────────────────────────────────
# REGISTRAR OBJETO
# ─────────────────────────────────────────────

def registrar_objeto(sistema, tipo, objeto):
    """
    Registra un objeto en la enciclopedia correspondiente.
    Si ya existe (por ID), no lo duplica.
    """

    sistema.setdefault("enciclopedias", {})
    sistema.setdefault("plugins_activos", {})

    # Inicializar enciclopedia si no existe
    sistema["enciclopedias"].setdefault(tipo, [])

    enciclopedia = sistema["enciclopedias"][tipo]

    # Evitar duplicados por ID
    if any(o["id"] == objeto["id"] for o in enciclopedia):
        return

    # Todo objeto registrado empieza activo
    objeto["activo"] = True

    enciclopedia.append(objeto)


"""📘 DOCUMENTACIÓN — LA GRAN ENCICLOPEDIA
===============================================================================

¿QUÉ ES LA GRAN ENCICLOPEDIA?
-----------------------------
LA GRAN ENCICLOPEDIA es el registro global de todos los objetos del sistema.
No gestiona lógica de juego ni efectos: solo EXISTENCIA, ESTADO y METADATOS.

Es una base de datos viva, centralizada y desacoplada del sistema activo.

La Enciclopedia permite:
- Registrar objetos creados por plugins
- Activarlos y desactivarlos
- Mantener historial y referencias seguras
- Evitar duplicados y bugs estructurales


PRINCIPIOS FUNDAMENTALES (REGLAS DE ORO)
----------------------------------------

1️⃣ LA ENCICLOPEDIA NO CREA OBJETOS
- Los objetos se crean SIEMPRE en sus plugins (inventario, notas, bestiario…)
- La Enciclopedia SOLO registra objetos ya creados

2️⃣ TODO OBJETO TIENE UN ID ÚNICO E INMUTABLE
- Campo obligatorio: "id"
- El ID jamás cambia
- El ID es la única referencia válida entre sistemas

3️⃣ EL SISTEMA ACTIVO SOLO GUARDA IDS
✔ Correcto:
    sistema["titulos"] = ["titulo_a1b2c3"]

❌ Incorrecto:
    sistema["titulos"] = [{objeto_completo}]

4️⃣ LA ENCICLOPEDIA GUARDA EL OBJETO COMPLETO
Ejemplo:
{
    "id": "nota_1bb9a3fd",
    "titulo": "Carta antigua",
    "contenido": "...",
    "activo": True
}

5️⃣ ACTIVAR / DESACTIVAR ≠ CREAR / BORRAR
- Crear: registrar + añadir ID al sistema
- Desactivar: activo = False
- Reactivar: activo = True
- Borrar definitivo: normalmente NO se hace


ESTRUCTURA DEL SISTEMA
---------------------
El sistema debe contener:

sistema["enciclopedias"] = {
    "titulos": [],
    "habilidades": [],
    "notas": [],
    "bestiario": [],
    ...
}

Cada clave contiene una LISTA DE OBJETOS COMPLETOS.


CONTRATO MÍNIMO DE UN OBJETO ENCICLOPÉDICO
-----------------------------------------
TODO objeto registrado debe tener:

{
    "id": str,        # obligatorio
    "activo": bool    # obligatorio
}

Además, debe tener AL MENOS un campo visible:
- "nombre" (preferido)
- o "titulo" (ej. notas)

Nunca se debe asumir que existe "nombre".


REGLA DE PRESENTACIÓN (MUY IMPORTANTE)
-------------------------------------
La Enciclopedia NO debe asumir campos específicos.

Siempre usar una función segura para mostrar nombres:

def obtener_nombre(obj):
    return (
        obj.get("nombre")
        or obj.get("titulo")
        or f"[{obj['id']}]"
    )


FUNCIONES PRINCIPALES DE LA ENCICLOPEDIA
----------------------------------------
- registrar_objeto
- desactivar_objeto
- reactivar_objeto
- listar_enciclopedia

Funciones planeadas:
- referencias cruzadas
- modo debug
- búsqueda global (futuro)


QUÉ NO DEBE HACER NUNCA LA ENCICLOPEDIA
--------------------------------------
🚫 No aplicar efectos
🚫 No modificar stats
🚫 No ejecutar lógica de juego
🚫 No crear objetos
🚫 No borrar referencias del sistema activo

La Enciclopedia OBSERVA y REGISTRA, no ejecuta.


OBJETIVO DEL DISEÑO
-------------------
- Separación total entre datos y lógica
- Evitar duplicaciones
- Permitir rollback e historial
- Escalabilidad sin miedo
- Plugins independientes y seguros

Este archivo es el NÚCLEO DOCUMENTAL del sistema.
Si algo rompe aquí, TODO el sistema lo notará.

===============================================================================
"""
