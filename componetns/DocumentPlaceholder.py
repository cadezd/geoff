from __future__ import annotations

import flet as ft
from flet import UserControl, Column, Row, TextField, Container, Draggable, DragTarget, Image, ControlEvent


class DocumentPlaceholder(UserControl):
    def __init__(self, page: ft.Page, document_name: str, image_paths: list[str]) -> None:
        super().__init__()

        # Data
        self.page = page
        self.document_name = document_name
        self.image_paths = image_paths

        self.selected_dragable_image_elements = []
        self.selected_image_paths = []

        # Components
        # We keep reference to the text field handle different events and change the document name
        self.text_field: TextField = TextField(
            label='Ime dokumenta:',
            value=self.document_name,
            border=ft.InputBorder.OUTLINE,
            tooltip='KLIKNI za urejanje imena dokumenta',
            bgcolor=ft.colors.RED_200 if self.is_in_error_state(self.document_name) else ft.colors.GREY_300,
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

        # We keep a reference to the dragable image elements so we can reorder them
        self.dragable_image_elements: list[DragTarget] = []
        # We keep a reference to the image elements so we can change their size
        self.image_elements: list[Image] = []
        for path in self.image_paths:
            image = Image(
                src=path,
                width=300,
                height=400,
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
            on_click=self.set_as_active_placeholder,
        )

    async def on_text_field_change(self, e: ControlEvent) -> None:
        """
        Highlight the text field if the value is empty or contains 'NEPREPOZNANO' or 'NOV DOKUMENT'
        It signals the user that the document name is not valid
        :param e:
        :return:
        """
        await self.set_as_active_placeholder(None)
        self.text_field.suffix_icon = 'error' if self.is_in_error_state(self.text_field.value) else 'edit'
        self.update()

    async def on_text_field_focus(self, e: ControlEvent) -> None:
        """
        Change the suffix icon to edit when the text field is focused
        :param e:
        :return:
        """
        await self.set_as_active_placeholder(None)
        self.text_field.suffix_icon = 'edit'
        self.update()

    def on_text_field_blur(self, e: ControlEvent) -> None:
        """
        Change the suffix icon to None when the text field is blurred
        :param e:
        :return:
        """
        self.text_field.suffix_icon = None
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
            # Swap the images in the list
            self.image_paths[i], self.image_paths[i + step] = self.image_paths[i + step], self.image_paths[i]

            # Swap the controls in the view
            self.images_row.controls[i], self.images_row.controls[i + step] = \
                self.images_row.controls[i + step], self.images_row.controls[i]

        self.update()

    async def set_as_active_placeholder(self, e: ControlEvent | None) -> None:
        """
        Set the active document placeholder in the parent component, so we can manipulate it
        :param e:
        :return:
        """

        # If there is an active document placeholder, change its background color back to normal
        if self.parent.parent.parent.parent.active_document_placeholder:
            # Based on the text field value, change the background color of text field to indicate the error state
            # if the document name is not valid
            self.parent.parent.parent.parent.active_document_placeholder.text_field.bgcolor = \
                ft.colors.RED_200 if self.parent.parent.parent.parent.active_document_placeholder.is_in_error_state(
                    self.parent.parent.parent.parent.active_document_placeholder.text_field.value
                ) else ft.colors.GREY_300
            # Set the background color of the images row container to normal and update the UI
            self.parent.parent.parent.parent.active_document_placeholder.images_row_container.bgcolor = ft.colors.GREY_300
            self.parent.parent.parent.parent.active_document_placeholder.update()

        # Change the color of current document placeholder to indicate that it is active
        self.text_field.bgcolor = ft.colors.RED_200 if self.is_in_error_state(
            self.text_field.value
        ) else ft.colors.BLUE_GREY_100
        self.images_row_container.bgcolor = ft.colors.BLUE_GREY_100
        # Set current document placeholder as active in the parent component and update the UI
        self.parent.parent.parent.parent.active_document_placeholder = self
        self.parent.parent.parent.parent.active_document_placeholder.update()

    def is_in_error_state(self, value) -> bool:
        """
        Check if the document name is in the error state
        :return: bool
        """
        return (
                not value or not value.strip() or 'NEPREPOZNANO' in value or 'NOV DOKUMENT' in value
        )

    async def zoom_in(self) -> None:
        """
        Increase the size of the images
        :return:
        """
        for image in self.image_elements:
            image.width = min(700, image.width + 50)
            image.height = min(800, image.height + 50)
            image.update()

    async def zoom_out(self) -> None:
        """
        Decrease the size of the images
        :return:
        """
        for image in self.image_elements:
            image.width = max(150, image.width - 50)
            image.height = max(200, image.height - 50)
            image.update()

    async def reset_zoom(self) -> None:
        """
        Reset the size of the images
        :return:
        """
        for image in self.image_elements:
            image.width = 300
            image.height = 400
            image.update()

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

            # Remove the image from the image paths list
            self.image_paths.pop(index)

            # Remove the image from the image elements
            self.image_elements.pop(index)

            # Remove the image from the UI
            self.images_row.controls.pop(index)

        # Clear the selected images
        self.selected_image_paths = []
        self.selected_dragable_image_elements = []

        # Update the UI
        self.images_row.update()

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
