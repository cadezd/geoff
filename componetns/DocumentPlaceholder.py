from __future__ import annotations

from collections.abc import Callable

import flet as ft
from flet import UserControl, Column, Row, TextField, Container, Draggable, DragTarget, Image, ControlEvent, IconButton, \
    ButtonStyle

from controlers.FileSeparatorController import file_separator_controller

MIN_IMAGE_WIDTH = 150
MIN_IMAGE_HEIGHT = 200
DEFAULT_IMAGE_WIDTH = 300
DEFAULT_IMAGE_HEIGHT = 400
MAX_IMAGE_WIDTH = 1400
MAX_IMAGE_HEIGHT = 1500


class DocumentPlaceholder(UserControl):
    def __init__(self, page: ft.Page, document_name: str, image_paths: list[str], set_as_active: Callable) -> None:
        super().__init__()

        # Data
        self.page = page
        self.document_name = document_name
        self.image_paths = image_paths
        self.set_as_active = set_as_active
        self.error = not document_name or \
                     not document_name.strip() or \
                     'NEPREPOZNANO' in document_name or \
                     'NOV DOKUMENT' in document_name

        self.selected_dragable_image_elements = []
        self.selected_image_paths = []

        # Components
        # We keep reference to the text field handle different events and change the document name
        self.text_field: TextField = TextField(
            label='Ime dokumenta:',
            value=self.document_name,
            border=ft.InputBorder.OUTLINE,
            tooltip='KLIKNI za urejanje imena dokumenta',
            bgcolor=ft.colors.RED_200 if self.is_in_error_state() else ft.colors.GREY_300,
            color=ft.colors.GREY_600,
            focused_color=ft.colors.GREY_900,
            filled=True,
            expand=True,
            multiline=False,
            border_width=0,
            on_change=self.on_text_field_change,
            on_focus=self.on_text_field_focus,
            on_blur=self.on_text_field_blur,
        )

        # Icon button for zooming in
        self.zoom_in_out_full_button = IconButton(
            icon=ft.icons.ZOOM_IN_ROUNDED,
            style=ButtonStyle(
                bgcolor=ft.colors.GREY_300,
                color=ft.colors.GREY_600,
                shape=ft.RoundedRectangleBorder(radius=5),
                padding=12,
            ),
            tooltip='Povečaj / pomanjšaj dokument',
            on_click=self.zoom_in_out_full,
        )

        # We keep a reference to the dragable image elements so we can reorder them
        self.dragable_image_elements: list[DragTarget] = []
        # We keep a reference to the image elements so we can change their size
        self.image_elements: list[Image] = []
        for path in self.image_paths:
            image = Image(
                src_base64=path,
                width=DEFAULT_IMAGE_WIDTH,
                height=DEFAULT_IMAGE_HEIGHT,
                tooltip='POVLECI IN SPUSTI za spreminjanje vrstnega reda\nLEVI KLIK za izbiro slike\nDESNI KLIK za izbiro možnosti',

            )
            self.image_elements.append(image)

            self.dragable_image_elements.append(
                DragTarget(
                    group=self.document_name,
                    on_accept=self.on_accept,
                    content=Draggable(
                        group=self.document_name,
                        content=Container(
                            content=image,
                            on_click=self.on_image_content_click
                        ),
                        data=path,
                    ),
                )
            )

        # We keep a reference to the row so we can manipulate the images (drag and drop)
        self.images_row: Row = Row(
            controls=self.dragable_image_elements,
            wrap=True,
            expand=True,
            spacing=30,
        )

        # We keep a reference to the images row container so we can manipulate its background color
        self.images_row_container: Container = Container(
            content=self.images_row,
            bgcolor=ft.colors.GREY_300,
            expand=True,
            padding=15,
            border_radius=5,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.GREY_500,
                offset=ft.Offset(0, 2),
                blur_style=ft.ShadowBlurStyle.NORMAL,
            ),
            on_click=lambda e: self.set_as_active(self),
        )

    def on_text_field_change(self, e: ControlEvent) -> None:
        """
        Highlight the text field when it is focused, remove the error text and change the suffix icon
        :param e:
        :return:
        """
        self.error = False
        self.set_as_active(self)
        self.text_field.suffix_icon = 'edit'
        self.text_field.error_text = None
        self.update()

    def on_text_field_focus(self, e: ControlEvent) -> None:
        """
        Highlight the text field when it is focused, remove the error text and change the suffix icon
        :param e:
        :return:
        """
        self.error = False
        self.set_as_active(self)
        self.text_field.suffix_icon = 'edit'
        self.text_field.error_text = None
        self.update()

    def on_text_field_blur(self, e: ControlEvent) -> None:
        """
        Check if the document name has changed and rename the document if the name is valid
        :param e:
        :return:
        """
        if self.text_field.value != self.document_name:
            try:
                file_separator_controller.rename_document(self.document_name, self.text_field.value)
                self.document_name = self.text_field.value
                self.text_field.suffix_icon = None
                self.error = False
            except ValueError as e:
                self.text_field.suffix_icon = 'error'
                self.text_field.bgcolor = ft.colors.RED_200
                self.text_field.error_text = str(e)
                self.error = True
        else:
            try:
                if "NOV DOKUMENT" in self.text_field.value or "NEPREPOZNANO" in self.text_field.value:
                    raise ValueError(f"Ime dokumenta {self.text_field.value} ni veljavno!")

                self.text_field.suffix_icon = None
                self.error = False
            except ValueError as e:
                self.text_field.error_text = str(e)
                self.error = True

        self.set_as_active(self)
        print("ON BLUR", self.document_name)
        self.update()

    def on_image_content_click(self, e: ControlEvent) -> None:
        """
        Selects the image and moves it to the selected images list so that we can manipulate it
        :param e:
        :return:
        """
        # get the selected image and draw a border around it
        container: Container = e.control
        container.border = ft.border.all(2, ft.colors.BLACK) if container.border is None else None

        # get the parent of the container
        parent: DragTarget = container.parent.parent

        # if the parent is not in the selected images list, add it
        if parent not in self.selected_dragable_image_elements:
            index = self.dragable_image_elements.index(parent)
            self.selected_dragable_image_elements.append(parent)
            self.selected_image_paths.append(self.image_paths[index])
        # if the parent is in the selected images list, remove it
        else:
            index = self.selected_dragable_image_elements.index(parent)
            self.selected_dragable_image_elements.pop(index)
            self.selected_image_paths.pop(index)

        # Set the document placeholder as active
        self.set_as_active(self)

        # Update the UI
        container.update()

    def on_accept(self, e: DragTarget) -> None:
        """
        Handle the drag and drop event to reorder the images
        :param e:
        :return:
        """
        # Get destination index
        destination_index = self.images_row.controls.index(e.control)
        # Get source index
        source_content = self.page.get_control(e.src_id)
        source_index = 0
        for i, control in enumerate(self.images_row.controls):
            if control.content == source_content:
                source_index = i
                break

        # Shift the controls
        step = 1 if source_index < destination_index else -1
        for i in range(source_index, destination_index, step):
            # Swap the controls in the view
            self.images_row.controls[i], self.images_row.controls[i + step] = \
                self.images_row.controls[i + step], self.images_row.controls[i]

        # Shift the selected images in controller
        file_separator_controller.rearrange_document_pages(self.document_name, source_index, destination_index)

        self.update()

    def is_in_error_state(self) -> bool:
        """
        Returns True if the document name is in error state else False
        :return: bool
        """
        return self.error

    async def zoom_in_out_full(self, e: ControlEvent) -> None:
        """
        Zoom in or out the images to full screen
        :return:
        """
        self.set_as_active(self)
        self.zoom_in_out_full_button.icon = ft.icons.ZOOM_IN_ROUNDED if \
            self.zoom_in_out_full_button.icon != ft.icons.ZOOM_IN_ROUNDED else ft.icons.REPLAY_ROUNDED
        for image in self.image_elements:
            image.width = MAX_IMAGE_WIDTH if self.zoom_in_out_full_button.icon != ft.icons.ZOOM_IN_ROUNDED else DEFAULT_IMAGE_WIDTH
            image.height = MAX_IMAGE_HEIGHT if self.zoom_in_out_full_button.icon != ft.icons.ZOOM_IN_ROUNDED else DEFAULT_IMAGE_HEIGHT
            image.update()

        self.update()

    async def zoom_in(self) -> None:
        """
        Increase the size of the images
        :return:
        """
        for image in self.image_elements:
            image.width = min(MAX_IMAGE_WIDTH, image.width + 50)
            image.height = min(MAX_IMAGE_HEIGHT, image.height + 50)
            image.update()

        self.update()

    async def zoom_out(self) -> None:
        """
        Decrease the size of the images
        :return:
        """
        for image in self.image_elements:
            image.width = max(MIN_IMAGE_WIDTH, image.width - 50)
            image.height = max(MIN_IMAGE_HEIGHT, image.height - 50)
            image.update()

        self.update()

    async def reset_zoom(self) -> None:
        """
        Reset the size of the images
        :return:
        """
        for image in self.image_elements:
            image.width = DEFAULT_IMAGE_WIDTH
            image.height = DEFAULT_IMAGE_HEIGHT
            image.update()

        self.update()

    async def delete_selected_images(self) -> None:
        """
        Delete the selected images from the document placeholder
        :return:
        """
        # If there are no selected images, do nothing
        if len(self.selected_image_paths) == 0 and len(self.selected_dragable_image_elements) == 0:
            return

        for selected_image_path, selected_dragable_image_element in zip(self.selected_image_paths,
                                                                        self.selected_dragable_image_elements):
            # Get the index of the selected image
            index = self.dragable_image_elements.index(selected_dragable_image_element)

            # Remove the image from the controller
            file_separator_controller.delete_document_page(self.document_name, index)

            # Remove the image from the image elements
            self.image_elements.pop(index)

            # Remove the image from the UI
            self.images_row.controls.pop(index)

        # Clear the selected images
        self.selected_image_paths = []
        self.selected_dragable_image_elements = []

        # Update the UI
        self.update()

    def build(self) -> Column:
        """
        Build the component and return it
        :return: Column
        """
        return Column(
            controls=[
                Row(
                    controls=[
                        Container(
                            content=Row(
                                controls=[
                                    self.text_field,
                                ],
                            ),
                            expand=True,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=5,
                                color=ft.colors.GREY_500,
                                offset=ft.Offset(0, 2),
                                blur_style=ft.ShadowBlurStyle.NORMAL,
                            ),
                        ),
                        Container(
                            content=Row(
                                controls=[
                                    self.zoom_in_out_full_button,
                                ],
                            ),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=5,
                                color=ft.colors.GREY_500,
                                offset=ft.Offset(0, 2),
                                blur_style=ft.ShadowBlurStyle.NORMAL,
                            ),
                        ),
                    ],
                ),
                Row(
                    controls=[
                        self.images_row_container
                    ],
                ),
            ],
            spacing=15,
        )
