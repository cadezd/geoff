import flet as ft

from App import App


async def main(page: ft.Page) -> None:
    page.title = 'Simpos app'
    page.window.width = 1000
    page.window.height = 700
    page.window.min_width = 1000
    page.window.min_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT

    app: App = App(page)
    page.add(app)
    page.update()
    app.initialize()


if __name__ == "__main__":
    ft.app(target=main)
