import flet as ft

def personaje_view(page: ft.Page):
    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Text("Vista Personaje", size=30),
    )
