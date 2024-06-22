import flet as ft
import requests

API_BASE_URL = "https://localhost/api"

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
        self.confirm_password_textfield = ft.TextField(
            label="Confirmar Contraseña", hint_text="Confirma tu contraseña", password=True
        )
        self.register_button = ft.ElevatedButton("Registrarse", on_click=self.register_click)

        self.controls = [
            ft.Text("Registrarse", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.username_textfield,
            self.password_textfield,
            self.confirm_password_textfield,
            self.register_button
        ]
        self.alignment = ft.MainAxisAlignment.CENTER
        self.width = 300

    def register_click(self, e):
        username = self.username_textfield.value
        password = self.password_textfield.value
        confirm_password = self.confirm_password_textfield.value

        # Check if the passwords match
        if password != confirm_password:
            # If passwords do not match, show an error message
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Las contraseñas no coinciden, inténtalo nuevamente"),
                open=True,
                action="OK",
            )
            self.page.snack_bar.open = True
            self.page.update()
            return  # Exit the function early

        # If passwords match, proceed with making the registration API request
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"email": username, "password": password}, verify=False
        )

        if response.status_code == 201:
            self.show_verification_popup()
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Fallo el registro, inténtalo nuevamente"),
                open=True,
                action="OK",
            )
            self.page.snack_bar.open = True
            self.page.update()

    def show_verification_popup(self):
        self.verification_code_textfield = ft.TextField(
            label="Código de Verificación", hint_text="Ingresa el código de 6 dígitos"
        )
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Verificación de Registro"),
            content=ft.Column(
                controls=[
                    ft.Text("Por favor, ingresa el código de 6 dígitos que enviamos a tu email."),
                    self.verification_code_textfield,
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            actions=[
                ft.ElevatedButton("Verificar", on_click=self.verify_code),
                ft.TextButton("Cancelar", on_click=lambda e: self.page.dialog.close())
            ]
        )
        
        self.page.dialog.open = True
        self.page.update()

    def verify_code(self, e):
        code = self.verification_code_textfield.value
        # Assume we send the verification code to the server for checking
        # Here you'd have a server endpoint to verify the code
        # For now, just a placeholder for the functionality
        print(f"Verifying code: {code}")  # Implement actual verification call
        # Assume verification success
        self.page.snack_bar = ft.SnackBar(
            ft.Text("Verificación completada, bienvenido!"),
            open=True,
            action="OK",
        )
        self.page.dialog.open = False
        self.page.dialog.close()
        self.page.snack_bar.open = True
        self.page.update()