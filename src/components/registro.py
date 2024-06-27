import flet as ft
import requests

URL_BASE_API = "https://localhost/api"

class Registro(ft.Column):
    def __init__(self, pagina, al_registrarse=None):
        super().__init__()
        self.pagina = pagina
        self.al_registrarse = al_registrarse
        self.campo_correo = ft.TextField(
            label="Correo electrónico", hint_text="Ingresa tu correo electrónico"
        )
        self.campo_contraseña = ft.TextField(
            label="Contraseña", hint_text="Ingresa tu contraseña", password=True
        )
        self.campo_confirmar_contraseña = ft.TextField(
            label="Confirmar Contraseña", hint_text="Confirma tu contraseña", password=True
        )
        self.boton_registrar = ft.ElevatedButton("Registrarse", on_click=self.clic_registrar)

        self.controls = [
            ft.Text("Registrarse", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.campo_correo,
            self.campo_contraseña,
            self.campo_confirmar_contraseña,
            self.boton_registrar
        ]
        self.alignment = ft.MainAxisAlignment.CENTER
        self.width = 300

    def clic_registrar(self, e):
        correo = self.campo_correo.value
        contraseña = self.campo_contraseña.value
        confirmar_contraseña = self.campo_confirmar_contraseña.value

        if contraseña != confirmar_contraseña:
            self.pagina.snack_bar = ft.SnackBar(
                ft.Text("Las contraseñas no coinciden, inténtalo nuevamente"),
                open=True,
                action="OK",
            )
            self.pagina.snack_bar.open = True
            self.pagina.update()
            return

        respuesta = requests.post(
            f"{URL_BASE_API}/auth/register",
            json={"email": correo, "password": contraseña}
        )

        if respuesta.status_code == 201:
            self.mostrar_popup_verificacion()
        else:
            self.pagina.snack_bar = ft.SnackBar(
                ft.Text("Falló el registro, inténtalo nuevamente"),
                open=True,
                action="OK",
            )
            self.pagina.snack_bar.open = True
            self.pagina.update()

    def mostrar_popup_verificacion(self):
        self.campo_codigo_verificacion = ft.TextField(
            label="Código de Verificación", hint_text="Ingresa el código de 6 dígitos"
        )
        self.pagina.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Verificación de Registro"),
            content=ft.Column(
                controls=[
                    ft.Text("Por favor, ingresa el código de 6 dígitos que enviamos a tu correo electrónico."),
                    self.campo_codigo_verificacion,
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            actions=[
                ft.ElevatedButton("Verificar", on_click=self.verificar_codigo),
                ft.TextButton("Cancelar", on_click=lambda e: self.pagina.dialog.close())
            ]
        )
        
        self.pagina.dialog.open = True
        self.pagina.update()

    def verificar_codigo(self, e):
        codigo = self.campo_codigo_verificacion.value
        # Aquí deberías implementar la llamada real a tu API para verificar el código
        # Por ahora, asumiremos que la verificación es exitosa
        self.pagina.snack_bar = ft.SnackBar(
            ft.Text("Verificación completada, ¡bienvenido!"),
            open=True,
            action="OK",
        )
        self.pagina.dialog.open = False
        self.pagina.dialog.close()
        self.pagina.snack_bar.open = True
        self.pagina.update()
        
        # Después de una verificación exitosa, llama al callback al_registrarse
        if self.al_registrarse:
            self.al_registrarse()