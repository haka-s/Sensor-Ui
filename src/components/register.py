import flet as ft
import requests

API_BASE_URL = "http://localhost:8000"

class Registry(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.username_textfield = ft.TextField(
            label="Email", hint_text="Ingresa tu email"
        )
        self.password_textfield = ft.TextField(
            label="Contraseña", hint_text="Ingresa tu contraseña", password=True
        )
        self.register_button = ft.ElevatedButton("Registrarse", on_click=self.register_click)

        self.controls = [
            ft.Text("Registrarse", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.username_textfield,
            self.password_textfield,
            self.register_button
        ]
        self.alignment = ft.MainAxisAlignment.CENTER
        self.width = 300

    def register_click(self, e):
        username = self.username_textfield.value
        password = self.password_textfield.value

        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"email": username, "password": password},
        )

        if response.status_code == 201:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Registration exitosa, ya podes iniciar sesión"),
                open=True,
                action="OK",
            )
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Fallo la registration, inténtalo nuevamente"),
                open=True,
                action="OK",
            )
        self.page.snack_bar.open = True
        self.page.update()