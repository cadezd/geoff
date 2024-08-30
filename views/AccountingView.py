import flet as ft
import numpy
import pandas as pd
from flet import MenuBar, SubmenuButton, Text, MenuItemButton, Row, Column, Divider, FloatingActionButton, ListView, \
    KeyboardEvent, FilePicker, FilePickerResultEvent, FilePickerFileType, TextField, Container
from flet_core import ControlEvent

from componetns.InvoicePlaceholder import InvoicePlaceholder
from controllers.AccounitngController import ReceiptRecord


class AccountingView(Column):
    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        # Data
        self.page = page
        self.invoice_placeholders: list[InvoicePlaceholder] = []
        self.receipt_records: list[ReceiptRecord] = []

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
                                dialog_title="Izberite eno ali več EXCEL (.xlsx) datotek",
                                allow_multiple=True,
                                file_type=FilePickerFileType.CUSTOM,
                                allowed_extensions=["xlsx"]
                            ),
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

        # SEARCH BUTTON #

        self.search: TextField = TextField(
            hint_text="Išči po DPR, NRA ali Št. zunanjega dokumenta...",
            on_change=self.on_search,
            bgcolor=ft.colors.GREY_100,
            border=ft.InputBorder.NONE,
            suffix_icon=ft.icons.SEARCH_ROUNDED,
        )

        # search container
        self.search_container: Container = Container(
            content=self.search,
            border_radius=5,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.GREY_500,
                offset=ft.Offset(0, 2),
                blur_style=ft.ShadowBlurStyle.NORMAL,
            ),
        )

        # LIST VIEW #

        # List view for displaying document placeholders
        self.list_view: ListView = ListView(
            expand=True,
            spacing=100,
            padding=10,
        )

        # FLOATING ACTION BUTTONS #

        # Action buttons for the bottom row (Left side)
        self.floating_action_button_import: FloatingActionButton = FloatingActionButton(
            icon=ft.icons.FILE_OPEN,
            tooltip="Uvozi izbrane datoteke",
            bgcolor=ft.colors.INDIGO_200,
            on_click=lambda e: self.file_picker_import.pick_files(
                dialog_title="Izberite eno ali več EXCEL (.xlsx) datotek",
                allow_multiple=True,
                file_type=FilePickerFileType.CUSTOM,
                allowed_extensions=["xlsx"]
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

        #
        # Layout
        #

        self.expand = True
        self.controls = [
            Row(controls=[self.menu]),
            self.search_container,
            self.list_view,
            Row(controls=[
                self.floating_action_button_import,
                self.floating_action_button_save,
                self.floating_action_button_remove
            ])
        ]

    def on_import_files(self, e: FilePickerResultEvent) -> None:
        """
        Display all the receipts from the selected Excel files
        :param e:
        :return:
        """
        # Get the paths of the selected files
        document_paths: list[str] = [file.path for file in e.files]

        for file_path in document_paths:
            # Read the excel file
            df_receipts: pd.core.frame.DataFrame = pd.read_excel(file_path)

            # Get all od the unique receipts IDs and filter out the ones that are not valid
            receipts: numpy.ndarray = df_receipts['Št. dokumenta'].unique()
            receipts = receipts[['NRA' in receipt or 'NDB' in receipt for receipt in receipts]]

            for i, receipt in enumerate(receipts):
                # Get the data for the current receipt
                receipt_data: pd.core.frame.DataFrame = df_receipts[df_receipts['Št. dokumenta'] == receipt]
                receipt_data = receipt_data.dropna(subset=['Splošna knjižna skupina izdelka'])

                # Create a new receipt record
                receipt_record: ReceiptRecord = ReceiptRecord(receipt_data)
                # Add the receipt record to the list of records
                self.receipt_records.append(receipt_record)

                # Create a new invoice placeholder
                invoice_placeholder: InvoicePlaceholder = InvoicePlaceholder(
                    self.page,
                    receipt_data,
                    receipt_record
                )
                # Add the invoice placeholder to the list of placeholders
                self.invoice_placeholders.append(invoice_placeholder)

                # Display the invoice placeholder on the list view
                self.list_view.controls.append(
                    invoice_placeholder
                )

        # Update the UI
        self.page.update()

    def on_search(self, e: ControlEvent) -> None:
        """
        Search for a specific receipt record and display it
        :param e:
        :return:
        """
        if self.search.value.strip() == '':
            self.list_view.controls = self.invoice_placeholders
        else:
            self.list_view.controls = list(filter(
                lambda placeholder: self.search.value.strip().lower() in placeholder.receipt_record.nra.lower() or \
                                    self.search.value.strip().lower() in placeholder.receipt_record.dpr.lower() or \
                                    self.search.value.strip().lower() in placeholder.receipt_record.szd.lower(),
                self.invoice_placeholders
            ))

        self.page.update()

    def on_save_files(self, e: FilePickerResultEvent) -> None:
        ...

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
