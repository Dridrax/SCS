import flet as ft

from ui.components.sidebar import sidebar
from ui.views.personaje_view import personaje_view
from ui.views.stats_view import stats_view
from ui.views.inventario_view import inventario_view
from ui.views.habilidades_view import habilidades_view
from ui.views.timeline_view import timeline_view

def main(page: ft.Page):
    page.title = "SCS"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    content = ft.Container(expand=True)

    def route_change(e):
        if page.route == "/personaje":
            content.content = personaje_view(page)
        elif page.route == "/stats":
            content.content = stats_view(page)
        elif page.route == "/inventario":
            content.content = inventario_view(page)
        elif page.route == "/habilidades":
            content.content = habilidades_view(page)
        elif page.route == "/timeline":
            content.content = timeline_view(page)
        else:
            content.content = personaje_view(page)

        page.update()

    page.on_route_change = route_change

    page.add(
        ft.Row(
            expand=True,
            controls=[
                sidebar(page),
                content,
            ],
        )
    )

    page.go("/personaje")

ft.app(target=main)
