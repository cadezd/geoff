import flet as ft
from flet import UserControl, RouteChangeEvent, View, Row

from AppLayout import AppLayout


class App(UserControl):
    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        self.page = page
        self.page.on_route_change = self.on_route_change

    def build(self) -> UserControl:
        return self

    def on_route_change(self, e: RouteChangeEvent) -> None:
        if e.route == '/separator':
            self.layout.set_separator_view()
        # elif e.route == '/payments':
        #    self.layout.set_payments_view()
        else:
            self.layout.set_home_view()

        self.page.update()

    def initialize(self) -> None:
        self.page.views.append(
            View(
                "/",
                [self.layout],
                padding=10,
            )
        )
        self.page.update()
        self.page.go("/")

    def build(self) -> Row:
        self.layout = AppLayout(
            app=self,
            page=self.page,
        )

        return self.layout
