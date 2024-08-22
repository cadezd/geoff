from __future__ import annotations

import re

import flet as ft
from flet import MenuBar, SubmenuButton, Text, MenuItemButton, Column, Row, CupertinoSlidingSegmentedButton, ListView, \
    FloatingActionButton, ControlEvent, KeyboardEvent, GestureDetector, Container, TapEvent, Stack, Divider, FilePicker, \
    FilePickerFileType, FilePickerResultEvent, TextButton, Dropdown, TextField, ProgressBar

from componetns.DocumentPlaceholder import DocumentPlaceholder
from controllers.FileSeparatorController import file_separator_controller


class SeparatorView(Column):
    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        # Data
        self.page: ft.Page = page
        self.active_document_placeholder: DocumentPlaceholder | None = None
        self.document_placeholders = []

        #
        # Components
        #

        # FILE PICKERS #

        # File picker for importing pdf files
        self.file_picker_import: FilePicker = FilePicker(
            on_result=lambda e: self.page.run_thread(self.on_import_files, e),
        )
        # File picker for saving pdf files
        self.file_picker_save: FilePicker = FilePicker(
            on_result=lambda e: self.page.run_thread(self.on_save_files, e),
        )
        self.page.overlay.append(self.file_picker_import)
        self.page.overlay.append(self.file_picker_save)

        # ALTER DIALOGS #

        # Alert dialog for confirming the the deletion of documents
        self.delete_documents_alert_dialog: ft.AlertDialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Potrditev izbrisa dokumentov"),
            content=ft.Text("Ali ste prepričani, da želite izbrisati vse dokumente?", size=16),
            actions=[
                TextButton(
                    text="Prekliči",
                    on_click=lambda e: self.page.close(self.delete_documents_alert_dialog),
                ),
                TextButton(
                    text="Izbriši",
                    on_click=self.on_clear_documents,
                ),
            ]
        )

        # Alert dialog for notifying the user that the documents have been saved
        self.save_documents_alert_dialog: ft.AlertDialog = ft.AlertDialog(
            modal=True,
            actions=[
                TextButton(
                    text="V redu",
                    on_click=lambda e: self.page.close(self.save_documents_alert_dialog),
                ),
            ]
        )

        # Settings alert dialog
        self.settings_inputs: dict[str, TextField | Dropdown] = {
            "MASKA": Dropdown(
                value=str(file_separator_controller.settings["MASKA"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         file_separator_controller.valid_settings_values["MASKA"]],
                expand=True,
            ),
            "ZOOM": Dropdown(
                value=str(file_separator_controller.settings["ZOOM"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         file_separator_controller.valid_settings_values["ZOOM"]],
                expand=True,
            ),
            "DPI_IN": Dropdown(
                value=str(file_separator_controller.settings["DPI_IN"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         file_separator_controller.valid_settings_values["DPI_IN"]],
                expand=True,
            ),
            "PODROCJE": Dropdown(
                value=str(file_separator_controller.settings["PODROCJE"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         file_separator_controller.valid_settings_values["PODROCJE"]],
                expand=True,
            ),
            "BELOST": Dropdown(
                value=str(file_separator_controller.settings["BELOST"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         file_separator_controller.valid_settings_values["BELOST"]],
                expand=True,
            ),
            "DEFAULT_SEPARATE": Dropdown(
                value=str(file_separator_controller.settings["DEFAULT_SEPARATE"]),
                options=[ft.dropdown.Option(str(val)) for val in
                         file_separator_controller.valid_settings_values["DEFAULT_SEPARATE"]],
                expand=True,
            ),
            "FILTER": TextField(
                value=file_separator_controller.settings["FILTER"],
                expand=True,
                max_lines=2,
                multiline=True,
                on_change=self.check_regex,
            ),
        }
        self.settings_alert_dialog: ft.AlertDialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nastavitve", text_align=ft.TextAlign.CENTER),
            content=Column(
                width=500,
                height=450,
                controls=[
                    Row([
                        ft.Text(f"{'MASKA:':<10}", size=16),
                        self.settings_inputs["MASKA"],
                    ]),
                    Row([
                        ft.Text(f"{'ZOOM:':<10}", size=16),
                        self.settings_inputs["ZOOM"],
                    ]),
                    Row([
                        ft.Text(f"{'DPI_IN:':<10}", size=16),
                        self.settings_inputs["DPI_IN"],
                    ]),
                    Row([
                        ft.Text(f"{'PODROCJE:':<10}", size=16),
                        self.settings_inputs["PODROCJE"],
                    ]),
                    Row([
                        ft.Text(f"{'BELOST:':<10}", size=16),
                        self.settings_inputs["BELOST"],
                    ]),
                    Row([
                        ft.Text(f"{'DEFAULT_SEPARATE:':<10}", size=16),
                        self.settings_inputs["DEFAULT_SEPARATE"],
                    ]),
                    Row([
                        ft.Text(f"{'FILTER:':<10}", size=16),
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
                            on_click=lambda e: self.file_picker_import.pick_files(
                                dialog_title="Izberite eno ali več PDF datotek",
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
                            on_click=lambda e: self.file_picker_save.get_directory_path(
                                dialog_title="Izberite mapo za shranjevanje"
                            ),
                        ),
                        Divider(height=2),
                        # Remove button
                        MenuItemButton(
                            content=ft.Text("Odstrani"),
                            tooltip="Odstrani vse datoteke",
                            leading=ft.Icon(ft.icons.DELETE),
                            on_click=lambda e: self.page.open(self.delete_documents_alert_dialog),
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
                    selected_index=file_separator_controller.settings["DEFAULT_SEPARATE"],
                    thumb_color=ft.colors.BLUE_400,
                    padding=4,
                    expand=True,
                    controls=[
                        ft.Text("QR koda"),
                        ft.Text("BAR koda"),
                    ],
                    height=40,
                    tooltip="Ločevanje datotek po BAR ali QR kodi",
                    on_change=lambda e: file_separator_controller.set_setting("DEFAULT_SEPARATE", int(e.data)),
                )
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
            on_click=lambda e: self.file_picker_save.get_directory_path(
                dialog_title="Izberite mapo za shranjevanje"
            ),
        )
        self.floating_action_button_remove: FloatingActionButton = FloatingActionButton(
            icon=ft.icons.DELETE,
            tooltip="Odstrani vse datoteke",
            bgcolor=ft.colors.RED_200,
            on_click=lambda e: self.page.open(self.delete_documents_alert_dialog),
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

        # PROGRESS BAR #

        self.progress_text: Text = Text("Grupiram dokumente: 0% končano")
        self.progress_bar: ProgressBar = ProgressBar(
            value=file_separator_controller.progress,
            height=10,
            bgcolor=ft.colors.BLUE_200,
            border_radius=5,
        )
        self.progress_bar_container: Container = Container(
            content=Column(
                controls=[
                    self.progress_text,
                    self.progress_bar,
                ],
            ),
            alignment=ft.alignment.bottom_center,
        )

        # CONTEXT MENU #

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

        # GESTURE DETECTOR #

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

        #
        # Layout
        #
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
        self.settings_inputs["MASKA"].value = str(file_separator_controller.settings["MASKA"])
        self.settings_inputs["ZOOM"].value = str(file_separator_controller.settings["ZOOM"])
        self.settings_inputs["DPI_IN"].value = str(file_separator_controller.settings["DPI_IN"])
        self.settings_inputs["PODROCJE"].value = str(file_separator_controller.settings["PODROCJE"])
        self.settings_inputs["BELOST"].value = str(file_separator_controller.settings["BELOST"])
        self.settings_inputs["FILTER"].value = file_separator_controller.settings["FILTER"]
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
        file_separator_controller.set_setting("MASKA", int(self.settings_inputs["MASKA"].value))
        file_separator_controller.set_setting("ZOOM", int(self.settings_inputs["ZOOM"].value))
        file_separator_controller.set_setting("DPI_IN", int(self.settings_inputs["DPI_IN"].value))
        file_separator_controller.set_setting("PODROCJE", float(self.settings_inputs["PODROCJE"].value))
        file_separator_controller.set_setting("BELOST", int(self.settings_inputs["BELOST"].value))
        file_separator_controller.set_setting("DEFAULT_SEPARATE", int(self.settings_inputs["DEFAULT_SEPARATE"].value))
        file_separator_controller.set_setting("FILTER", self.settings_inputs["FILTER"].value)

        # Update the default separate setting on the main page
        self.menu.controls[-1].selected_index = file_separator_controller.settings["DEFAULT_SEPARATE"]
        self.page.update()

        # Save the settings to the file
        file_separator_controller.save_settings()

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

        self.page.update()

    def set_active_document_placeholder(self, document_placeholder: DocumentPlaceholder) -> None:
        """
        Set the active document placeholder
        :param document_placeholder:
        :return:
        """
        if self.active_document_placeholder:
            self.active_document_placeholder.text_field.bgcolor = \
                ft.colors.RED_200 if self.active_document_placeholder.is_in_error_state() else ft.colors.GREY_300
            self.active_document_placeholder.images_row_container.bgcolor = ft.colors.GREY_300
            self.active_document_placeholder.zoom_in_out_full_button.style.bgcolor = ft.colors.GREY_300
            self.page.update()

        self.active_document_placeholder = document_placeholder
        self.active_document_placeholder.text_field.bgcolor = \
            ft.colors.RED_200 if self.active_document_placeholder.is_in_error_state() else ft.colors.BLUE_GREY_100
        self.active_document_placeholder.images_row_container.bgcolor = ft.colors.BLUE_GREY_100
        self.active_document_placeholder.zoom_in_out_full_button.style.bgcolor = ft.colors.BLUE_GREY_100
        self.page.update()

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

            # If there are no images in the document placeholder, save it as empty
            if len(document_placeholder.image_paths) == 0:
                empty_document_placeholders.append(document_placeholder)

        # Remove empty document placeholders from the list view
        for empty_document_placeholder in empty_document_placeholders:
            # If the empty document placeholder is active set active placeholder to None
            if self.active_document_placeholder == empty_document_placeholder:
                self.active_document_placeholder = None

            file_separator_controller.delete_document(empty_document_placeholder.document_name)
            self.list_view.controls.remove(empty_document_placeholder)
            self.document_placeholders.remove(empty_document_placeholder)

        self.page.update()
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

            file_separator_controller.delete_document(empty_document_placeholder.document_name)
            self.list_view.controls.remove(empty_document_placeholder)
            self.document_placeholders.remove(empty_document_placeholder)

        # If there are no selected images, do nothing
        if len(selected_image_paths) == 0:
            return

        new_document_name, pages = file_separator_controller.create_new_document(selected_image_paths)
        # Create a new document placeholder
        new_document_placeholder = DocumentPlaceholder(
            page=self.page,
            document_name=new_document_name,
            image_paths=pages,
            set_as_active=self.set_active_document_placeholder,
        )

        # Add the new document placeholder at the end of the list
        self.document_placeholders.append(new_document_placeholder)
        self.list_view.controls.append(new_document_placeholder)

        # Scroll to the end of the list view
        self.list_view.scroll_to(offset=-1, duration=1000)

        # Set the new document placeholder as active this operation must be done last!!
        self.set_active_document_placeholder(new_document_placeholder)
        new_document_placeholder.update()

        # Hide the context menu
        self.hide_context_menu(None)

        # Update the list view
        self.page.update()

    async def zoom_in_all(self, e: ControlEvent | None) -> None:
        """
        Increase the size of images in all document placeholders
        :param e:
        :return:
        """
        for document_placeholder in self.document_placeholders:
            await document_placeholder.zoom_in()

    async def zoom_out_all(self, e: ControlEvent | None) -> None:
        """
        Decrease the size of images in all document placeholders
        :param e:
        :return:
        """
        for document_placeholder in self.document_placeholders:
            await document_placeholder.zoom_out()

    async def zoom_in_selected(self, e: ControlEvent | None) -> None:
        """
        Increase the size of images in selected document placeholder
        :param e:
        :return:
        """
        if self.active_document_placeholder:
            await self.active_document_placeholder.zoom_in()

    async def zoom_out_selected(self, e: ControlEvent | None) -> None:
        """
        Decrease the size of images in selected document placeholder
        :param e:
        :return:
        """
        if self.active_document_placeholder:
            await self.active_document_placeholder.zoom_out()

    async def reset_zoom(self, e: ControlEvent | None) -> None:
        """
        Reset the zoom of all document placeholders
        :param e:
        :return:
        """
        for document_placeholder in self.document_placeholders:
            await document_placeholder.reset_zoom()

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

    def on_clear_documents(self, e: ControlEvent | None) -> None:
        """
        Clear all grouped documents
        :param e:
        :return:
        """
        # Clear the grouped documents
        file_separator_controller.clear_grouped_documents()

        # Remove all document placeholders from the list view
        self.list_view.controls.clear()
        self.document_placeholders.clear()

        # Set the active document placeholder to None
        self.active_document_placeholder = None

        # Update the list view
        self.page.update()

        self.page.close(self.delete_documents_alert_dialog)

    def on_save_files(self, e: FilePickerResultEvent) -> None:
        """
        Save grouped documents to the selected directory
        :param e:
        :return:
        """

        if not e.path:
            return

        try:
            # Save the grouped documents to the selected directory
            file_separator_controller.save_documents(e.path)

            # Clear the grouped documents
            file_separator_controller.clear_grouped_documents()

            # Remove all document placeholders from the list view
            self.list_view.controls.clear()
            self.document_placeholders.clear()

            # Update the list view
            self.page.update()

            # Show the alert dialog that the documents have been saved
            self.save_documents_alert_dialog.title = ft.Text("Dokumenti so bili shranjeni")
            self.save_documents_alert_dialog.content = ft.Text("Dokumenti so bili uspešno shranjeni v izbrano mapo.",
                                                               size=16)
            self.page.open(self.save_documents_alert_dialog)

        except Exception as e:
            self.save_documents_alert_dialog.title = ft.Text(f"Napaka pri shranjevanju dokumentov!")
            self.save_documents_alert_dialog.content = ft.Text(f"Pri shranjevanju dokumentov je prišlo do napake:\n{e}",
                                                               size=16)
            self.page.open(self.save_documents_alert_dialog)

    def on_import_files(self, e: FilePickerResultEvent) -> None:
        """
        Import selected PDF files, group them and display grouped files in the list view
        :param e:
        :return:
        """
        # Get the paths of the selected files
        document_paths: list[str] = [file.path for file in e.files]

        # Bind the controller's report_progress method to update the progress bar
        file_separator_controller.report_progress = self.update_progress_bar

        # Show the progress bar
        self.controls.insert(-1, self.progress_bar_container)
        self.page.update()

        # Group the documents
        file_separator_controller.group_documents(document_paths)

        # Display the grouped documents in the list view
        for document_name, images in file_separator_controller.grouped_documents.items():
            document_placeholder = DocumentPlaceholder(
                page=self.page,
                document_name=document_name,
                image_paths=images,
                set_as_active=self.set_active_document_placeholder,
            )

            self.document_placeholders.append(document_placeholder)
            self.list_view.controls.append(document_placeholder)

        # Hide the progress bar
        self.controls.remove(self.progress_bar_container)
        self.page.update()

    def update_progress_bar(self) -> None:
        """
        Function to that updates the progress bar based on the controller's progress
        :return:
        """
        # Update progress text
        self.progress_text.value = f"Grupiram dokumente: {round(file_separator_controller.progress * 100, 2)}% končano"
        # Update the progress bar based on the current progress
        self.progress_bar.value = file_separator_controller.progress

        try:
            self.page.update()
        except Exception as e:
            print(e)

    def hide_context_menu(self, e: ControlEvent | None) -> None:
        """
        Hide the context menu
        :param e:
        :return:
        """
        self.context_menu.visible = False
        self.page.update()

    def open_context_menu(self, e: TapEvent) -> None:
        """
        Open the context menu and set its position based on the location of the tap event
        :param e:
        :return:
        """
        self.context_menu.visible = True
        self.context_menu.top = e.local_y - 10
        self.context_menu.left = e.local_x - 10
        self.page.update()

    def did_mount(self):
        """
        Allows the user to user shortcuts for file separator functions while separator view is active
        :return:
        """
        self.page.on_keyboard_event.subscribe(self.on_keyboard)

    def will_unmount(self):
        """
        When the user switches to another view, it removes shortcuts for file separator functions
        :return:
        """
        self.page.on_keyboard_event.unsubscribe(self.on_keyboard)
