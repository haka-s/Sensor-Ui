import flet as ft
import requests

URL_BASE_API = "https://localhost/api"

class InicioSesion(ft.Column):
    def __init__(self, pagina, al_iniciar_sesion=None):
        super().__init__()
        self.pagina = pagina
        self.al_iniciar_sesion = al_iniciar_sesion
        self.campo_usuario = ft.TextField(
            label="Correo electrónico", hint_text="Ingresa tu correo electrónico"
        )
        self.campo_contraseña = ft.TextField(
            label="Contraseña", hint_text="Ingresa tu contraseña", password=True
        )
        self.boton_iniciar_sesion = ft.ElevatedButton("Iniciar Sesión", on_click=self.clic_iniciar_sesion)

        self.controls = [
            ft.Text("Inicio de Sesión", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.campo_usuario,
            self.campo_contraseña,
            self.boton_iniciar_sesion
        ]
        self.alignment = ft.MainAxisAlignment.CENTER
        self.width = 300

    def clic_iniciar_sesion(self, e):
        usuario = self.campo_usuario.value
        contraseña = self.campo_contraseña.value

        respuesta = requests.post(
            f"{URL_BASE_API}/auth/jwt/login",
            data={"username": usuario, "password": contraseña},
        )

        if respuesta.status_code == 200:
            token = respuesta.json()["access_token"]
            self.pagina.client_storage.set("access_token", token)
            self.pagina.snack_bar = ft.SnackBar(
                ft.Text("¡Inicio de sesión exitoso!"), open=True, action="OK"
            )
            if self.al_iniciar_sesion:
                self.al_iniciar_sesion()
        else:
            self.pagina.snack_bar = ft.SnackBar(
                ft.Text("Falló el inicio de sesión, verifica tus credenciales"),
                open=True,
                action="OK",
            )
        self.pagina.snack_bar.open = True
        self.pagina.update()