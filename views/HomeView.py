import os.path
from math import pi

import flet as ft
from flet import Column, Row, Container, Image, Text, TextSpan, ElevatedButton


class HomeView(Column):
    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        self.page = page
        self.alignment = ft.MainAxisAlignment.CENTER
        self.expand = True

        self.counter = 0

        # Geoff (the car) that will be animated
        self.geoff: Container = Container(
            content=Image(
                src=os.path.join("geoff.png"),
            ),
            offset=ft.transform.Offset(5, 0),
            animate_offset=ft.animation.Animation(1000),
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(1000, ft.AnimationCurve.BOUNCE_OUT),
        )

        # Controls of the HomeView
        self.controls = [
            # Welcome message
            Row(
                controls=[
                    Text("👋Dobrodošli nazaj!", size=36),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # Brief description of the app
            Row(
                controls=[
                    Text(spans=[
                        TextSpan("GEOFF", url="https://topgear.fandom.com/wiki/Geoff"),
                        TextSpan(" je namenska aplikacija za obdelavo dokumentov."),
                    ], size=24),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # Geoff (the car) image
            Row(
                controls=[
                    self.geoff,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # Button to animate Geoff
            Row(
                controls=[
                    ElevatedButton("Kje je Geoff?", on_click=self.animate, style=ft.ButtonStyle(
                        padding=20
                    )),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]

    def animate(self, e):
        """
        Animates Geoff (the car)
        :param e:
        :return:
        """
        if self.counter % 3 == 0:
            self.geoff.offset = ft.transform.Offset(0, 0)
        elif self.counter % 3 == 1:
            self.geoff.rotate.angle += pi * 2
        elif self.counter % 3 == 2:
            self.geoff.offset = ft.transform.Offset(5, 0)

        self.page.update()
        self.counter += 1
