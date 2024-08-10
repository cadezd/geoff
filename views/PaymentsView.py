import flet as ft
from flet import UserControl, RouteChangeEvent, View, Row, Column

class PaymentsView(Column):
    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        self.page = page
        self.controls = [
            ft.Text('Payments view')
        ]
