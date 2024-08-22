import flet as ft
from flet import UserControl, NavigationRail, NavigationRailLabelType, NavigationRailDestination, Icon, ControlEvent, \
    Page


class Navigation(UserControl):
    def __init__(self, page: Page) -> None:
        super().__init__()

        self.page = page

        self.navigation_rail: NavigationRail = NavigationRail(
            selected_index=0,
            label_type=NavigationRailLabelType.ALL,
            expand=True,
            destinations=[
                NavigationRailDestination(
                    icon_content=Icon(ft.icons.HOME),
                    label="Domov",
                    padding=ft.padding.all(10),
                ),
                NavigationRailDestination(
                    icon_content=Icon(ft.icons.CUT),
                    label="Separator",
                    padding=ft.padding.all(10),
                ),
                # NavigationRailDestination(
                #    icon_content=Icon(ft.icons.EURO),
                #    label="Plačila",
                #    padding=ft.padding.all(10),
                # ),
            ],
            on_change=self.on_change,
        )

    def on_change(self, e: ControlEvent) -> None:
        selected_index: int = e if (type(e) == int) else e.control.selected_index
        self.navigation_rail.selected_index = selected_index

        if selected_index == 1:
            self.page.route = '/separator'
        # elif selected_index == 2:
        #    self.page.route = '/payments'
        else:
            self.page.route = '/'

        self.page.update()

    def build(self) -> NavigationRail:
        return self.navigation_rail
