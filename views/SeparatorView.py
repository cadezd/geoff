from __future__ import annotations

import os.path
import re

import flet as ft
from flet import MenuBar, SubmenuButton, Text, MenuItemButton, Column, Row, CupertinoSlidingSegmentedButton, ListView, \
    FloatingActionButton, ControlEvent, KeyboardEvent, GestureDetector, Container, TapEvent, Stack, Divider, FilePicker, \
    FilePickerFileType, FilePickerResultEvent, TextButton, Dropdown, TextField

from componetns.DocumentPlaceholder import DocumentPlaceholder
from controlers.FileSeparatorController import FileSeparatorController


class SeparatorView(Column):
    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        # Data
        self.page: ft.Page = page
        self.active_document_placeholder: DocumentPlaceholder | None = None
        self.controller: FileSeparatorController = FileSeparatorController()

        # Events
        self.page.on_keyboard_event = None
        self.page.on_keyboard_event = self.on_keyboard

        # Components
        # File picker for importing pdf files
        self.file_picker_import: FilePicker = FilePicker(
            on_result=self.on_import_files,
        )
        # File picker for saving pdf files
        self.file_picker_save: FilePicker = FilePicker(
            on_result=lambda e: print("JEEEJ2"),
        )
        self.page.overlay.append(self.file_picker_import)
        self.page.overlay.append(self.file_picker_save)

        # Settings alert dialog
        self.settings_inputs: dict[str, TextField | Dropdown] = {
            "MASKA": Dropdown(
                value=str(self.controller.settings["MASKA"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         self.controller.valid_settings_values["MASKA"]],
                expand=True,
            ),
            "ZOOM": Dropdown(
                value=str(self.controller.settings["ZOOM"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         self.controller.valid_settings_values["ZOOM"]],
                expand=True,
            ),
            "DPI_IN": Dropdown(
                value=str(self.controller.settings["DPI_IN"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         self.controller.valid_settings_values["DPI_IN"]],
                expand=True,
            ),
            "PODROCJE": Dropdown(
                value=str(self.controller.settings["PODROCJE"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         self.controller.valid_settings_values["PODROCJE"]],
                expand=True,
            ),
            "BELOST": Dropdown(
                value=str(self.controller.settings["BELOST"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         self.controller.valid_settings_values["BELOST"]],
                expand=True,
            ),
            "FILTER": TextField(
                value=self.controller.settings["FILTER"],
                expand=True,
                max_lines=2,
                multiline=True,
                on_change=self.check_regex,
            ),
        }

        self.settings_alert_dialog: ft.AlertDialog = ft.AlertDialog(
            modal=True,
            content=Column(
                width=500,
                height=400,
                controls=[
                    Row([ft.Text("Nastavitve", size=26, weight=ft.FontWeight.BOLD)],
                        alignment=ft.MainAxisAlignment.CENTER),
                    Row([
                        ft.Text(f"{'MASKA:':<10}", size=18),
                        self.settings_inputs["MASKA"],
                    ]),
                    Row([
                        ft.Text(f"{'ZOOM:':<10}", size=18),
                        self.settings_inputs["ZOOM"],
                    ]),
                    Row([
                        ft.Text(f"{'DPI_IN:':<10}", size=18),
                        self.settings_inputs["DPI_IN"],
                    ]),
                    Row([
                        ft.Text(f"{'PODROCJE:':<10}", size=18),
                        self.settings_inputs["PODROCJE"],
                    ]),
                    Row([
                        ft.Text(f"{'BELOST:':<10}", size=18),
                        self.settings_inputs["BELOST"],
                    ]),
                    Row([
                        ft.Text(f"{'FILTER:':<10}", size=18),
                        self.settings_inputs["FILTER"],
                    ]),
                ],
            ),
            actions=[
                TextButton(
                    text="Prekliči",
                    on_click=self.on_cancel_settings,
                ),
                TextButton(
                    text="Shrani",
                    on_click=lambda e: self.page.run_thread(self.on_save_settings),
                ),
            ],
        )

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
                            on_click=lambda e: self.file_picker_import.pick_files(
                                allow_multiple=True,
                                file_type=FilePickerFileType.CUSTOM,
                                allowed_extensions=["pdf"]
                            ),
                        ),
                        # Save button
                        MenuItemButton(
                            content=ft.Text("Shrani"),
                            tooltip="Shrani datoteke v mapo",
                            leading=ft.Icon(ft.icons.SAVE),
                            on_click=None
                        ),
                        Divider(height=2),
                        # Remove button
                        MenuItemButton(
                            content=ft.Text("Odstrani"),
                            tooltip="Odstrani vse datoteke",
                            leading=ft.Icon(ft.icons.DELETE),
                            on_click=None
                        )
                    ]
                ),

                # View submenu
                SubmenuButton(
                    content=Text("Pogled"),
                    leading=ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN_ROUNDED, size=20),
                    tooltip="Odpre nastavitve pogleda",
                    style=ft.ButtonStyle(
                        padding=15
                    ),
                    expand=True,
                    controls=[
                        # Zoom in all button
                        MenuItemButton(
                            content=ft.Text("Povečaj vse"),
                            leading=ft.Icon(ft.icons.ZOOM_IN),
                            tooltip="Poveča prikaz vseh dokumentov (CTRL +)",
                            close_on_click=False,
                            on_click=self.zoom_in_all,
                        ),
                        # Zoom out all button
                        MenuItemButton(
                            content=ft.Text("Pomanjšaj vse"),
                            leading=ft.Icon(ft.icons.ZOOM_OUT),
                            tooltip="Pomanjša prikaz vseh dokumentov (CTRL -)",
                            close_on_click=False,
                            on_click=self.zoom_out_all,
                        ),
                        Divider(height=2),
                        # Zoom in selected button
                        MenuItemButton(
                            content=ft.Text("Povečaj izbranega"),
                            leading=ft.Icon(ft.icons.ZOOM_IN),
                            tooltip="Poveča prikaz izbranega dokumenta (CTRL SHIFT +)",
                            close_on_click=False,
                            on_click=self.zoom_in_selected,
                        ),
                        # Zoom out selected button
                        MenuItemButton(
                            content=ft.Text("Pomanjšaj izbranega"),
                            leading=ft.Icon(ft.icons.ZOOM_OUT),
                            tooltip="Pomanjša prikaz izbranega dokumenta (CTRL SHIFT -)",
                            close_on_click=False,
                            on_click=self.zoom_out_selected,
                        ),
                        Divider(height=2),
                        # Reset zoom button
                        MenuItemButton(
                            content=ft.Text("Ponastavi pogled"),
                            leading=ft.Icon(ft.icons.REPLAY_ROUNDED),
                            tooltip="Ponastavi pogled vseh dokumentov (CRTL R)",
                            close_on_click=False,
                            on_click=self.reset_zoom,
                        ),
                    ]
                ),

                # Settings submenu
                SubmenuButton(
                    content=Text("Nastavitve"),
                    leading=ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN_ROUNDED, size=20),
                    tooltip="Odpre nastavitve",
                    expand=True,
                    style=ft.ButtonStyle(
                        padding=15
                    ),
                    controls=[
                        # Zoom in button
                        MenuItemButton(
                            content=ft.Text("Odpri nastavitve"),
                            leading=ft.Icon(ft.icons.SETTINGS_ROUNDED),
                            tooltip="Odpre nastavitve",
                            close_on_click=False,
                            on_click=lambda e: self.page.open(self.settings_alert_dialog),
                        )
                    ]
                ),

                # Split by
                CupertinoSlidingSegmentedButton(
                    selected_index=self.controller.settings["DEFAULT_SEPARATE"],
                    thumb_color=ft.colors.BLUE_400,
                    padding=4,
                    expand=True,
                    controls=[
                        ft.Text("QR koda"),
                        ft.Text("BAR koda"),
                    ],
                    height=40,
                    tooltip="Ločevanje datotek po BAR ali QR kodi",
                    on_change=lambda e: self.controller.set_setting("DEFAULT_SEPARATE", e.data),
                )
            ],
        )
        self.list_view: ListView = ListView(
            expand=True,
            spacing=60,
            padding=10,
        )

        # Action buttons for the bottom row (Left side)
        self.floating_action_button_import: FloatingActionButton = FloatingActionButton(
            icon=ft.icons.FILE_OPEN,
            tooltip="Uvozi izbrane datoteke",
            bgcolor=ft.colors.INDIGO_200,
            on_click=lambda e: self.file_picker_import.pick_files(
                allow_multiple=True,
                file_type=FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"]
            ),
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

        # Action buttons for the bottom row (Right side)
        self.floating_action_button_zoom_in: FloatingActionButton = FloatingActionButton(
            icon=ft.icons.ZOOM_IN,
            tooltip="Poveča prikaz vseh dokumentov (CTRL +)",
            on_click=self.zoom_in_all,
        )
        self.floating_action_button_zoom_out: FloatingActionButton = FloatingActionButton(
            icon=ft.icons.ZOOM_OUT,
            tooltip="Pomanjša prikaz vseh dokumentov (CTRL -)",
            on_click=self.zoom_out_all,
        )
        self.floating_action_button_reset_zoom: FloatingActionButton = FloatingActionButton(
            icon=ft.icons.REPLAY_ROUNDED,
            tooltip="Ponastavi pogled vseh dokumentov (CRTL R)",
            on_click=self.reset_zoom,
        )

        self.document_placeholders = []
        for i in range(15):
            document_placeholder = DocumentPlaceholder(
                page=self.page,
                document_name=f"Document {i}",
                image_paths=[
                    os.path.join("..", "assets", "image0.png"),
                    os.path.join("..", "assets", "image1.jpg"),
                    os.path.join("..", "assets", "image2.jpg"),
                ],
                set_as_active=self.set_active_document_placeholder,
            )

            self.document_placeholders.append(document_placeholder)
            self.list_view.controls.append(document_placeholder)

        self.context_menu: Container = Container(
            content=Container(
                visible=True,
                content=Column(
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("Ustvari nov dokument"),
                            tooltip="Ustvari nov dokument (CTRL + N)",
                            leading=ft.Icon(ft.icons.NOTE_ADD),
                            on_click=self.create_new_document,
                        ),
                        ft.MenuItemButton(
                            content=ft.Text("Izbriši izbrane strani"),
                            tooltip="Izbriši izbrane strani (Delete)",
                            leading=ft.Icon(ft.icons.DELETE),
                            on_click=self.delete_selected_images,
                        ),
                    ],
                ),
                width=200,
                height=100,
                bgcolor=ft.colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.GREY_500,
                    offset=ft.Offset(0, 2),
                    blur_style=ft.ShadowBlurStyle.NORMAL,
                ),
            ),
        )

        # Gesture detector that open the context menu on right click
        # and has list view as content
        self.gesture_detector: GestureDetector = GestureDetector(
            content=Stack(
                controls=[
                    self.list_view,
                    self.context_menu,
                ],
                expand=True,
            ),
            on_secondary_tap_down=self.open_context_menu,
            on_double_tap=self.hide_context_menu,
            expand=True,
        )
        # We hide the context menu, but if we do that in constructor it does not work properly
        self.context_menu.visible = False

        # Layout
        self.expand = True
        self.controls = [
            Row(controls=[self.menu]),
            self.gesture_detector,
            Row(
                controls=[
                    Container(
                        content=Row(
                            controls=[
                                self.floating_action_button_import,
                                self.floating_action_button_save,
                                self.floating_action_button_remove
                            ],
                        )
                    ),
                    Container(
                        content=Row(
                            controls=[
                                self.floating_action_button_reset_zoom,
                                self.floating_action_button_zoom_out,
                                self.floating_action_button_zoom_in
                            ],
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
        ]

    def on_cancel_settings(self, e: ControlEvent | None) -> None:
        """
        Close the settings alert dialog without saving the settings
        :param e:
        :return:
        """
        # Resets the settings inputs to the values from the controller
        # And removes error text and styles
        self.settings_inputs["MASKA"].value = str(self.controller.settings["MASKA"])
        self.settings_inputs["ZOOM"].value = str(self.controller.settings["ZOOM"])
        self.settings_inputs["DPI_IN"].value = str(self.controller.settings["DPI_IN"])
        self.settings_inputs["PODROCJE"].value = str(self.controller.settings["PODROCJE"])
        self.settings_inputs["BELOST"].value = str(self.controller.settings["BELOST"])
        self.settings_inputs["FILTER"].value = self.controller.settings["FILTER"]
        self.settings_inputs["FILTER"].error_text = None
        self.settings_inputs["FILTER"].suffix_icon = None
        self.settings_inputs["FILTER"].bgcolor = ft.colors.GREY_50

        self.page.close(self.settings_alert_dialog)

    def on_save_settings(self) -> None:
        """
        Save the settings to the file and close the settings alert dialog
        :param e:
        :return:
        """

        # Check if the filter is valid
        if self.settings_inputs["FILTER"].error_text:
            return

        # Set the settings from the inputs to the controller
        self.controller.set_setting("MASKA", int(self.settings_inputs["MASKA"].value))
        self.controller.set_setting("ZOOM", int(self.settings_inputs["ZOOM"].value))
        self.controller.set_setting("DPI_IN", int(self.settings_inputs["DPI_IN"].value))
        self.controller.set_setting("PODROCJE", float(self.settings_inputs["PODROCJE"].value))
        self.controller.set_setting("BELOST", int(self.settings_inputs["BELOST"].value))
        self.controller.set_setting("FILTER", self.settings_inputs["FILTER"].value)

        # Save the settings to the file
        self.controller.save_settings()

        # Close the settings alert dialog
        self.page.close(self.settings_alert_dialog)

    def check_regex(self, e: ControlEvent | None) -> None:
        """
        Check if the regex is valid
        :param e:
        :return:
        """
        try:
            re.compile(self.settings_inputs["FILTER"].value)
            self.settings_inputs["FILTER"].suffix_icon = None
            self.settings_inputs["FILTER"].error_text = None
            self.settings_inputs["FILTER"].bgcolor = ft.colors.GREY_100
        except Exception as e:
            self.settings_inputs["FILTER"].suffix_icon = 'error'
            self.settings_inputs["FILTER"].error_text = 'Napaka v regularnem izrazu'
            self.settings_inputs["FILTER"].bgcolor = ft.colors.RED_200

        self.settings_inputs["FILTER"].update()

    def set_active_document_placeholder(self, document_placeholder: DocumentPlaceholder) -> None:
        """
        Set the active document placeholder
        :param document_placeholder:
        :return:
        """
        if self.active_document_placeholder:
            self.active_document_placeholder.text_field.bgcolor = \
                ft.colors.RED_200 if self.active_document_placeholder.is_in_error_state(
                    self.active_document_placeholder.text_field.value
                ) else ft.colors.GREY_300
            self.active_document_placeholder.images_row_container.bgcolor = ft.colors.GREY_300
            self.active_document_placeholder.update()

        self.active_document_placeholder = document_placeholder
        self.active_document_placeholder.text_field.bgcolor = \
            ft.colors.RED_200 if self.active_document_placeholder.is_in_error_state(
                self.active_document_placeholder.text_field.value
            ) else ft.colors.BLUE_GREY_100
        self.active_document_placeholder.images_row_container.bgcolor = ft.colors.BLUE_GREY_100
        self.active_document_placeholder.update()

    async def delete_selected_images(self, e: ControlEvent | None) -> None:
        """
        Delete selected images from the document placeholders
        :param e:
        :return:
        """
        # Save empty document placeholders to remove them from the list view
        empty_document_placeholders: list[DocumentPlaceholder] = []
        for document_placeholder in self.document_placeholders:
            # Delete selected images from the document placeholder
            await document_placeholder.delete_selected_images()
            document_placeholder.update()

            # If there are no images in the document placeholder, save it as empty
            if len(document_placeholder.image_paths) == 0:
                empty_document_placeholders.append(document_placeholder)

        # Remove empty document placeholders from the list view
        for empty_document_placeholder in empty_document_placeholders:
            # If the empty document placeholder is active set active placeholder to None
            if self.active_document_placeholder == empty_document_placeholder:
                self.active_document_placeholder = None

            self.list_view.controls.remove(empty_document_placeholder)
            self.document_placeholders.remove(empty_document_placeholder)

        self.list_view.update()
        self.hide_context_menu(None)

    async def create_new_document(self, e: ControlEvent | None) -> None:
        """
        Create a new document
        :param e:
        :return:
        """

        # We get the selected images from all document placeholders that we want to move to the new document
        selected_image_paths = []
        # Save empty document placeholders to remove them from the list view
        empty_document_placeholders: list[DocumentPlaceholder] = []
        for document_placeholder in self.document_placeholders:
            selected_image_paths.extend(document_placeholder.selected_image_paths)
            await document_placeholder.delete_selected_images()

            # If there are no images in the document placeholder, save it as empty
            if len(document_placeholder.image_paths) == 0:
                empty_document_placeholders.append(document_placeholder)

        # Remove empty document placeholders from the list view
        for empty_document_placeholder in empty_document_placeholders:
            # If the empty document placeholder is active set active placeholder to None
            if self.active_document_placeholder == empty_document_placeholder:
                self.active_document_placeholder = None

            self.list_view.controls.remove(empty_document_placeholder)
            self.document_placeholders.remove(empty_document_placeholder)

        # If there are no selected images, do nothing
        if len(selected_image_paths) == 0:
            return

        # Create a new document placeholder
        new_document_placeholder = DocumentPlaceholder(
            page=self.page,
            document_name=f"NOV DOKUMENT",
            image_paths=selected_image_paths,
            set_as_active=self.set_active_document_placeholder,
        )

        # Add the new document placeholder at the end of the list
        self.document_placeholders.append(new_document_placeholder)
        self.list_view.controls.append(new_document_placeholder)

        # Update the list view
        self.list_view.update()
        self.page.update()

        # Scroll to the end of the list view
        self.list_view.scroll_to(offset=-1, duration=1000)

        # Set the new document placeholder as active this operation must be done last!!
        await new_document_placeholder.set_as_active_placeholder(None)
        new_document_placeholder.update()

        # Hide the context menu
        self.hide_context_menu(None)

    async def zoom_in_all(self, e: ControlEvent | None) -> None:
        """
        Increase the size of images in all document placeholders
        :param e:
        :return:
        """
        for document_placeholder in self.document_placeholders:
            await document_placeholder.zoom_in()
            document_placeholder.update()

        self.page.update()

    async def zoom_out_all(self, e: ControlEvent | None) -> None:
        """
        Decrease the size of images in all document placeholders
        :param e:
        :return:
        """
        for document_placeholder in self.document_placeholders:
            await document_placeholder.zoom_out()
            document_placeholder.update()

        self.page.update()

    async def zoom_in_selected(self, e: ControlEvent | None) -> None:
        """
        Increase the size of images in selected document placeholder
        :param e:
        :return:
        """
        if self.active_document_placeholder:
            await self.active_document_placeholder.zoom_in()
            self.active_document_placeholder.update()

            self.page.update()

    async def zoom_out_selected(self, e: ControlEvent | None) -> None:
        """
        Decrease the size of images in selected document placeholder
        :param e:
        :return:
        """
        if self.active_document_placeholder:
            await self.active_document_placeholder.zoom_out()
            self.active_document_placeholder.update()

            self.page.update()

    async def reset_zoom(self, e: ControlEvent | None) -> None:
        """
        Reset the zoom of all document placeholders
        :param e:
        :return:
        """
        for document_placeholder in self.document_placeholders:
            await document_placeholder.reset_zoom()
            document_placeholder.update()

        self.page.update()

    async def on_keyboard(self, e: KeyboardEvent) -> None:
        """
        CTRL + or CTRL = to zoom in all document placeholders
        CTRL - to zoom out all document placeholders
        CTRL SHIFT + to zoom in selected document placeholder
        CTRL SHIFT - to zoom out selected document placeholder
        CTRL R to reset zoom of all document placeholders
        CTRL N to create a new document
        Delete to delete selected images
        :param e:
        :return:
        """
        # Zoom in if CTRL and + are pressed
        if e.ctrl and not e.shift and (e.key == '+' or e.key == '='):
            await self.zoom_in_all(None)

        # Zoom out if CTRL and - are pressed
        if e.ctrl and not e.shift and e.key == '-':
            await self.zoom_out_all(None)

        # Zoom in selected document placeholder if CTRL SHIFT and + are pressed
        if e.ctrl and e.shift and (e.key == '+' or e.key == '='):
            await self.zoom_in_selected(None)

        # Zoom out selected document placeholder if CTRL SHIFT and - are pressed
        if e.ctrl and e.shift and e.key == '-':
            await self.zoom_out_selected(None)

        # Reset zoom if CTRL R is pressed
        if e.ctrl and (e.key == 'r' or e.key == 'R'):
            await self.reset_zoom(None)

        # Create new document if CTRL N is pressed
        if e.ctrl and (e.key == 'n' or e.key == 'N'):
            await self.create_new_document(None)

        # Delete selected images if Delete is pressed
        if e.key == 'Delete':
            await self.delete_selected_images(None)

        self.page.update()

    def on_import_files(self, e: FilePickerResultEvent) -> None:
        print(e.files)

    def hide_context_menu(self, e: ControlEvent | None) -> None:
        """
        Hide the context menu
        :param e:
        :return:
        """
        self.context_menu.visible = False
        self.context_menu.update()

    def open_context_menu(self, e: TapEvent) -> None:
        """
        Open the context menu and set its position based on the location of the tap event
        :param e:
        :return:
        """
        self.context_menu.visible = True
        self.context_menu.top = e.local_y - 10
        self.context_menu.left = e.local_x - 10
        self.context_menu.update()
