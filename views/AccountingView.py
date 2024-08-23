import flet as ft
from flet import MenuBar, SubmenuButton, Text, MenuItemButton, Row, Column, Divider, FloatingActionButton, ListView, \
    KeyboardEvent


class AccountingView(Column):
    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        # Data
        self.page = page

        # MENU AND SUBMENUS #

        # Top menu bar and all its submenus
        self.menu: MenuBar = MenuBar(
            expand=True,
            style=ft.MenuStyle(
                alignment=ft.alignment.top_left,
                mouse_cursor={
                    ft.ControlState.HOVERED: ft.MouseCursor.WAIT,
                    ft.ControlState.DEFAULT: ft.MouseCursor.ZOOM_OUT,
                },
                padding=0,
            ),
            controls=[
                # Files submenu
                SubmenuButton(
                    content=Text("Datoteka"),
                    leading=ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN_ROUNDED, size=20),
                    tooltip="Odpre možnosti datoteke",
                    style=ft.ButtonStyle(
                        padding=15
                    ),
                    expand=True,
                    controls=[
                        # Import button
                        MenuItemButton(
                            content=ft.Text("Uvozi"),
                            tooltip="Uvozi izbrane datoteke",
                            leading=ft.Icon(ft.icons.FILE_OPEN),
                            on_click=None,
                        ),
                        # Save button
                        MenuItemButton(
                            content=ft.Text("Shrani"),
                            tooltip="Shrani datoteke v mapo",
                            leading=ft.Icon(ft.icons.SAVE),
                            on_click=None,
                        ),
                        Divider(height=2),
                        # Remove button
                        MenuItemButton(
                            content=ft.Text("Odstrani"),
                            tooltip="Odstrani vse datoteke",
                            leading=ft.Icon(ft.icons.DELETE),
                            on_click=None,
                        )
                    ]
                ),
            ],
        )

        # LIST VIEW #

        # List view for displaying document placeholders
        self.list_view: ListView = ListView(
            expand=True,
            spacing=60,
            padding=10,
        )

        # FLOATING ACTION BUTTONS #

        # Action buttons for the bottom row (Left side)
        self.floating_action_button_import: FloatingActionButton = FloatingActionButton(
            icon=ft.icons.FILE_OPEN,
            tooltip="Uvozi izbrane datoteke",
            bgcolor=ft.colors.INDIGO_200,
            on_click=None
        )
        self.floating_action_button_save: FloatingActionButton = FloatingActionButton(
            icon=ft.icons.SAVE,
            tooltip="Shrani datoteke v mapo",
            bgcolor=ft.colors.INDIGO_200,
            on_click=None
        )
        self.floating_action_button_remove: FloatingActionButton = FloatingActionButton(
            icon=ft.icons.DELETE,
            tooltip="Odstrani vse datoteke",
            bgcolor=ft.colors.RED_200,
            on_click=None
        )

        #
        # Layout
        #

        self.expand = True
        self.controls = [
            Row(controls=[self.menu]),
            self.list_view,
            Row(controls=[
                self.floating_action_button_import,
                self.floating_action_button_save,
                self.floating_action_button_remove
            ])
        ]

    async def on_keyboard(self, e: KeyboardEvent) -> None:
        ...

    def did_mount(self):
        """
        Allows the user to user shortcuts for accounting functions while accounting view is active
        :return:
        """
        self.page.on_keyboard_event.subscribe(self.on_keyboard)

    def will_unmount(self):
        """
        When the user switches to another view, it removes shortcuts for accounting functions
        :return:
        """
        self.page.on_keyboard_event.unsubscribe(self.on_keyboard)
