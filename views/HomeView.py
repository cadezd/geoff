import os.path

import flet as ft
from flet import Column, Image, Row


class HomeView(Column):
    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        self.page = page
        self.alignment = ft.MainAxisAlignment.CENTER
        self.expand = True
        self.page.on_keyboard_event = None
        self.controls = [
            Row(
                controls=[
                    Image(src=os.path.join("assets", "home_view_image.png"), width=500, height=500, ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        ]
