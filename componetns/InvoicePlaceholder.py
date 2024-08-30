from __future__ import annotations

import flet as ft
import pandas as pd
from flet import UserControl, DataTable, DataColumn, DataRow, DataCell, Text, Row, Column, Container, ControlEvent, \
    Markdown, ResponsiveRow, TextField, Divider

from controllers.AccounitngController import ReceiptRecord


class InvoicePlaceholder(UserControl):
    def __init__(self, page: ft.Page, receipt_data: pd.core.frame.DataFrame,
                 receipt_record: ReceiptRecord | None) -> None:
        super().__init__()

        # Data
        self.page: ft.Page = page
        self.receipt_data: pd.core.frame.DataFrame = receipt_data
        self.receipt_record: ReceiptRecord = receipt_record

        self.receipt_data['Datum DDV'] = self.receipt_data['Datum DDV'].dt.strftime('%m/%Y')
        self.receipt_data['Datum knjiženja'] = self.receipt_data['Datum knjiženja'].dt.strftime('%m/%Y')

        #
        # Components
        #

        # DATA TABLE that shows original receipt data #

        cols = ['Št. dokumenta', 'Vrsta dokumenta', 'Opis',
                'Št. zunanjega dokumenta', 'Datum DDV', 'Datum knjiženja',
                'Št. GK konta', 'Splošna knjižna skupina izdelka', 'Knjižna skupina izdelka za DDV',
                'Znesek v breme2', 'Znesek v dobro2', 'Znesek2']

        self.data_table: DataTable = DataTable(
            columns=[DataColumn(Text(value=col, selectable=True)) for col in cols],
            # add data from the receipt_data dataframe
            rows=[
                DataRow([
                    DataCell(
                        Text(value=str(row[col]),
                             selectable=True) if col in self.receipt_data.columns else Text(value=''))
                    for col in cols
                ])
                for index, row in self.receipt_data.iterrows()
            ],
            bgcolor=ft.colors.GREY_300,
            border_radius=5,
        )

        # INPUTS with default values from receipt_record #

        self.nra_input: TextField = TextField(
            value=self.receipt_record.nra,
            label="NRA",
            on_focus=self.clear_input_error_text,
            on_blur=self.handle_data_change,
            border_color=ft.colors.GREY_400,
            expand=True,
            multiline=False
        )
        self.st_zunanjega_dokumenta_input: TextField = TextField(
            value=self.receipt_record.szd,
            label="Št. zunanjega dokumenta",
            on_focus=self.clear_input_error_text,
            on_blur=self.handle_data_change,
            border_color=ft.colors.GREY_400,
            expand=True,
            multiline=False
        )
        self.dpr_input: TextField = TextField(
            value=self.receipt_record.dpr,
            label="DPR",
            on_focus=self.clear_input_error_text,
            on_blur=self.handle_data_change,
            border_color=ft.colors.GREY_400,
            expand=True,
            multiline=False
        )
        self.datum_ddv_input: TextField = TextField(
            value=self.receipt_record.datum_ddv.strftime('%m/%Y'),
            label="Datum DDV (mm/yyyy)",
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9/]"),
            on_focus=self.clear_input_error_text,
            on_blur=self.handle_data_change,
            border_color=ft.colors.GREY_400,
            suffix_icon=ft.icons.CALENDAR_MONTH,
            expand=True,
            multiline=False,
        )
        self.datum_knizenja_input: TextField = TextField(
            value=self.receipt_record.datum_obdobje.strftime('%m/%Y'),
            label="Datum knjiženja (mm/yyyy)",
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9/]"),
            on_focus=self.clear_input_error_text,
            on_blur=self.handle_data_change,
            border_color=ft.colors.GREY_400,
            suffix_icon=ft.icons.CALENDAR_MONTH,
            expand=True,
            multiline=False,
        )
        self.osnova_22_input: TextField = TextField(
            value=round(self.receipt_record.osnove_davki.get(22, 0.0), 2),
            label='Osnova 22% (€)',
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\.,-]"),
            on_focus=self.clear_input_error_text,
            on_blur=self.handle_data_change,
            border_color=ft.colors.GREY_400,
            expand=True,
            multiline=False,
        )
        self.osnova_95_input: TextField = TextField(
            value=round(self.receipt_record.osnove_davki.get(9.5, 0.0), 2),
            label='Osnova 9.5% (€)',
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\.,-]"),
            on_focus=self.clear_input_error_text,
            on_blur=self.handle_data_change,
            border_color=ft.colors.GREY_400,
            expand=True,
            multiline=False,
        )
        self.osnova_0_input: TextField = TextField(
            value=round(self.receipt_record.osnove_davki.get(0, 0.0), 2),
            label='Osnova 0% (€)',
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\.,-]"),
            on_focus=self.clear_input_error_text,
            on_blur=self.handle_data_change,
            border_color=ft.colors.GREY_400,
            expand=True,
            multiline=False,
        )
        self.konti_input: TextField = TextField(
            value=', '.join(self.receipt_record.konte),
            label="Konto",
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9,\s]"),
            on_focus=self.clear_input_error_text,
            on_blur=self.handle_data_change,
            border_color=ft.colors.GREY_400,
            expand=True,
            multiline=False
        )

        # MARKDOWN (sticker preview)#

        self.markdown: Markdown = Markdown(
            value=self.receipt_record.__str__(),
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            expand=True,
            selectable=True,
        )

    def clear_input_error_text(self, e: ControlEvent) -> None:
        """
        When the input is focused, clear the error text
        :param e:
        :return:
        """
        e.control.error_text = None
        e.control.update()

    def handle_data_change(self, e: ControlEvent) -> None:
        """
        Change the data in the receipt record and update the markdown (sticker preview)
        :param e:
        :return:
        """
        # Get the input control
        input_control: TextField = e.control

        try:
            # Set the appropriate value in the receipt record and UI
            # New value is the "clean" value that is set in the receipt record
            new_value: str = ''
            if input_control == self.nra_input:
                new_value = self.receipt_record.set_nra(input_control.value)

            elif input_control == self.st_zunanjega_dokumenta_input:
                new_value = self.receipt_record.set_szd(input_control.value)

            elif input_control == self.dpr_input:
                new_value = self.receipt_record.set_dpr(input_control.value)

            elif input_control == self.datum_ddv_input:
                new_value = self.receipt_record.set_datum_ddv(input_control.value)

            elif input_control == self.datum_knizenja_input:
                new_value = self.receipt_record.set_datum_obdobje(input_control.value)

            elif input_control == self.osnova_22_input:
                new_value = self.receipt_record.set_osnova(22, input_control.value)

            elif input_control == self.osnova_95_input:
                new_value = self.receipt_record.set_osnova(9.5, input_control.value)

            elif input_control == self.osnova_0_input:
                new_value = self.receipt_record.set_osnova(0, input_control.value)

            elif input_control == self.konti_input:
                new_value = self.receipt_record.set_konte(input_control.value)

            # Update the control with the new value
            input_control.value = new_value
        except ValueError as error:
            # Set the error text if the value is not valid
            input_control.error_text = str(error)
            input_control.value = ''

        # Update the markdown
        self.markdown.value = self.receipt_record.__str__()

        # Update the UI
        self.update()

    def did_mount(self) -> None:
        """
        While the component is mounted, keep track of the page resize event and resize the data table accordingly
        :return:
        """
        self.page.on_resized.subscribe(self.handle_resize)

    def will_unmount(self) -> None:
        """
        When the component is unmounted, unsubscribe from the page resize event
        :return:
        """
        self.page.on_resized.unsubscribe(self.handle_resize)

    def handle_resize(self, e: ControlEvent) -> None:
        """
        If the page width is less than 2300 make the data table scrollable, otherwise expand it
        :return:
        """
        if self.page.width < 2300:
            self.data_table.expand = False
            self.data_table.parent.scroll = ft.ScrollMode.AUTO
            self.data_table.parent.expand = False
        else:
            self.data_table.expand = True
            self.data_table.parent.scroll = None
            self.data_table.parent.expand = True

        self.update()

    def build(self) -> Column:
        """
        Build the component
        :return:
        """
        return Column(
            controls=[
                Container(
                    content=Row(controls=[self.data_table], scroll=ft.ScrollMode.AUTO),
                    bgcolor=ft.colors.GREY_300,
                    border_radius=5,
                    padding=10,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.colors.GREY_500,
                        offset=ft.Offset(0, 2),
                        blur_style=ft.ShadowBlurStyle.NORMAL,
                    ),
                ),

                Container(
                    content=ResponsiveRow(
                        controls=[
                            Container(
                                content=self.markdown,
                                bgcolor=ft.colors.WHITE,
                                expand=True,
                                padding=10,
                                border_radius=5,
                                col={"md": 6, "lg": 3, }
                            ),
                            Container(
                                content=Column(
                                    controls=[
                                        Row(
                                            controls=[
                                                self.nra_input,
                                                self.st_zunanjega_dokumenta_input,
                                            ],
                                        ),
                                        Row(
                                            controls=[
                                                self.dpr_input,
                                                Text(value='', expand=True),
                                            ]
                                        ),
                                        Row(
                                            controls=[
                                                self.datum_ddv_input,
                                                self.datum_knizenja_input,
                                            ]
                                        ),
                                        Divider(height=5, visible=False),
                                        Row(controls=[
                                            self.osnova_22_input,
                                            Text(value='', expand=True),
                                        ]),
                                        Row(controls=[
                                            self.osnova_95_input,
                                            Text(value='', expand=True),
                                        ]),
                                        Row(controls=[
                                            self.osnova_0_input,
                                            Text(value='', expand=True),
                                        ]),
                                        Divider(height=5, visible=False),
                                        Row(
                                            controls=[
                                                self.konti_input,
                                            ]
                                        )
                                    ]
                                ),
                                bgcolor=ft.colors.GREY_300,
                                expand=True,
                                padding=10,
                                border_radius=5,
                                col={"md": 6, "lg": 9, }
                            ),
                        ]
                    ),
                    bgcolor=ft.colors.GREY_300,
                    border_radius=5,
                    padding=10,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.colors.GREY_500,
                        offset=ft.Offset(0, 2),
                        blur_style=ft.ShadowBlurStyle.NORMAL,
                    ),
                ),
            ],
            expand=True,
            spacing=15,
        )
