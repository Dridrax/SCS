import flet as ft

def build_header(title):
    return ft.Container(
        padding=20,
        bgcolor=ft.Colors.BLUE_GREY_900,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls="#EE4B4B"
            )
    )
