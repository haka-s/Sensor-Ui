import flet as ft
from components.logon import Login
from components.register import Registry

class LoginRegisterScreen(ft.Column):
    def __init__(self, page, on_login_success=None):
        super().__init__(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        self.page = page
        self.login_form = Login(page, on_login_success=on_login_success)
        self.register_form = Registry(page)

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Iniciar Sesión",
                    icon=ft.icons.LOGIN,
                    content=ft.Container(
                        content=self.login_form,
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ),
                ft.Tab(
                    text="Registrarse",
                    icon=ft.icons.APP_REGISTRATION,
                    content=ft.Container(
                        content=self.register_form,
                        alignment=ft.alignment.center,
                        expand=True
                    )
                )
            ],
            expand=True
        )
        self.controls = [tabs]