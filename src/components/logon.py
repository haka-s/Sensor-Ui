import flet as ft
import requests

API_BASE_URL = "http://localhost:8000"

class Login(ft.Column):
    def __init__(self, page, on_login_success=None):
        super().__init__()
        self.page = page
        self.on_login_success = on_login_success
        self.username_textfield = ft.TextField(
            label="Email", hint_text="Ingresa tu email"
        )
        self.password_textfield = ft.TextField(
            label="Contraseña", hint_text="Ingresa tu contraseña", password=True
        )
        self.login_button = ft.ElevatedButton("Iniciar Sesión", on_click=self.login_click)

        self.controls = [
            ft.Text("Inicio de Sesión", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.username_textfield,
            self.password_textfield,
            self.login_button
        ]
        self.alignment = ft.MainAxisAlignment.CENTER
        self.width = 300

    def login_click(self, e):
        username = self.username_textfield.value
        password = self.password_textfield.value

        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={"username": username, "password": password},
        )

        if response.status_code == 200:
            token = response.json()["access_token"]
            self.page.client_storage.set("access_token", token)
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Inicio de Sesión exitoso!"), open=True, action="OK"
            )
            if self.on_login_success:
                self.on_login_success()
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Fallo el inicio de sesión, verifica tus credenciales"),
                open=True,
                action="OK",
            )
        self.page.snack_bar.open = True
        self.page.update()