import flet as ft
from flet import Row, UserControl, VerticalDivider, View

from componetns.Navigation import Navigation
from views.HomeView import HomeView
from views.PaymentsView import PaymentsView
from views.SeparatorView import SeparatorView


class AppLayout(Row):
    def __init__(self, page: ft.Page, app: UserControl) -> None:
        super().__init__()
        # Data
        self.app = app
        self.page = page

        # Components
        self.navigation = Navigation(self.page)
        self.home_view = HomeView(self.page)
        self.separator_view = SeparatorView(self.page)
        # self.payments_view = PaymentsView(self.page)

        # Default active view
        self._active_view = self.home_view

        # Layout
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.expand = True
        self.padding = 10
        self.bgcolor = ft.colors.GREY_100
        self.controls = [
            self.navigation,
            VerticalDivider(width=1),
            self.active_view,
        ]

    @property
    def active_view(self) -> View:
        return self._active_view

    @active_view.setter
    def active_view(self, view: View) -> None:
        self._active_view = view
        self.controls[-1] = self._active_view
        self.update()

    def set_home_view(self) -> None:
        self.active_view = self.home_view
        self.navigation.navigation_rail.selected_index = 0
        self.navigation.update()
        self.page.update()

    def set_separator_view(self) -> None:
        self.active_view = self.separator_view
        self.navigation.navigation_rail.selected_index = 1
        self.navigation.update()
        self.page.update()

    # def set_payments_view(self) -> None:
    #    self.active_view = self.payments_view
    #    self.navigation.navigation_rail.selected_index = 2
    #    self.navigation.update()
    #    self.page.update()
