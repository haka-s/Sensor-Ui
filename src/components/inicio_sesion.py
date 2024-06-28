import asyncio
import flet as ft
import requests

URL_BASE_API = "https://localhost/api"

class InicioSesion(ft.Container):
    def __init__(self, pagina, al_iniciar_sesion=None):
        super().__init__()
        self.pagina = pagina
        self.al_iniciar_sesion = al_iniciar_sesion
        self.campo_usuario = ft.TextField(
            label="Correo electrónico",
            hint_text="Ingresa tu correo electrónico",
            prefix_icon=ft.icons.EMAIL
        )
        self.campo_contraseña = ft.TextField(
            label="Contraseña",
            hint_text="Ingresa tu contraseña",
            password=True,
            prefix_icon=ft.icons.LOCK
        )
        
        self.boton_iniciar_sesion = ft.ElevatedButton(
            "Iniciar Sesión",
            on_click=self.clic_iniciar_sesion,
            style=ft.ButtonStyle(
                color={ft.MaterialState.DEFAULT: ft.colors.WHITE},
                bgcolor={ft.MaterialState.DEFAULT: ft.colors.PRIMARY}
            ),
            width=200
        )

        self.content = ft.Column(
            controls=[
                ft.Text("Inicio de Sesión", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.campo_usuario,
                self.campo_contraseña,
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.boton_iniciar_sesion
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            width=400
        )
        self.padding = ft.padding.all(20)
        self.bgcolor = ft.colors.WHITE
        self.border_radius = ft.border_radius.all(10)
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.colors.GREY_300,
            offset=ft.Offset(0, 0),
        )

    def clic_iniciar_sesion(self, e):
        usuario = self.campo_usuario.value
        contraseña = self.campo_contraseña.value

        try:
            respuesta = requests.post(
                f"{URL_BASE_API}/auth/jwt/login",
                data={"username": usuario, "password": contraseña},
                verify=r"cert\fullchain.pem",
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
        except requests.RequestException as e:
            self.pagina.snack_bar = ft.SnackBar(
                ft.Text(f"Error de conexión: {str(e)}"),
                open=True,
                action="OK",
            )
        
        self.pagina.snack_bar.open = True
        self.pagina.update()