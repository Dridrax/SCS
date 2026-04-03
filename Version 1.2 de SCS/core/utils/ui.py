# core/utils/ui.py

from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

# Instancia global de la consola
console = Console()

# ------------------- FUNCIONES DE INTERFAZ -------------------

def crear_layout() -> Layout:
    """
    Crea un layout base con dos áreas:
    - body: para mostrar la información principal
    - menu: para mostrar las opciones o botones
    """
    layout = Layout()
    layout.split_column(
        Layout(name="body", ratio=3),
        Layout(name="menu", ratio=1)
    )
    return layout

def ventana(titulo: str, contenido: str) -> RenderableType:
    """
    Crea un panel Rich para mostrar contenido.
    Nunca devuelve None.
    """
    if contenido is None:
        contenido = ""
    return Panel(Text(contenido), title=titulo, expand=True)

def menu_opciones(titulo: str, opciones: list[str]) -> RenderableType:
    """
    Crea un panel Rich con las opciones del menú.
    Nunca devuelve None.
    """
    if not opciones:
        opciones = ["Volver"]
    texto = "\n".join(f"{i+1}. {op}" for i, op in enumerate(opciones))
    return Panel(Text(texto), title=titulo, expand=True)

def mostrar(layout: Layout):
    """
    Limpia la consola y muestra el layout completo.
    """
    console.clear()
    console.print(layout)

def pausar(mensaje: str = "\nPresiona Enter para continuar..."):
    """
    Pausa la ejecución hasta que el usuario presione Enter.
    """
    input(mensaje)

def pedir_opcion(opciones: list[str], prompt_text: str = "> ") -> str:
    """
    Pide al usuario que seleccione una opción del menú usando Prompt de Rich.
    Devuelve el texto de la opción seleccionada.
    """
    if not opciones:
        return ""
    sel = Prompt.ask(prompt_text, choices=[str(i+1) for i in range(1, len(opciones)+1)])
    return opciones[int(sel) - 1]
