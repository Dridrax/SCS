import flet as ft

def sidebar(page: ft.Page):
    def nav(route: str):
        page.go(route)

    return ft.Container(
        width=220,
        padding=ft.padding.all(10),
        bgcolor=ft.Colors.SURFACE_VARIANT,
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Text("MENÚ", size=18, weight=ft.FontWeight.BOLD),

                ft.Divider(),

                ft.TextButton(
                    "👤 Personaje",
                    on_click=lambda e: nav("/personaje"),
                ),
                ft.TextButton(
                    "📊 Stats",
                    on_click=lambda e: nav("/stats"),
                ),
                ft.TextButton(
                    "🎒 Inventario",
                    on_click=lambda e: nav("/inventario"),
                ),
                ft.TextButton(
                    "✨ Habilidades",
                    on_click=lambda e: nav("/habilidades"),
                ),
                ft.TextButton(
                    "🕒 Timeline",
                    on_click=lambda e: nav("/timeline"),
                ),
            ],
        ),
    )
