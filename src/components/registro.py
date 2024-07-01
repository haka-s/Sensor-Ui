import flet as ft
import requests
import re
URL_BASE_API = "https://localhost/api"
RUTA_CERTIFICADO = r"cert\fullchain.pem"

def es_correo_valido(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

def es_contraseña_valida(contraseña):
    patron = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(patron, contraseña) is not None

class Registro(ft.Container):
    def __init__(self, pagina, al_registrarse=None):
        super().__init__()
        self.pagina = pagina
        self.al_registrarse = al_registrarse
        
        self.campo_correo = ft.TextField(
            label="Correo electrónico",
            hint_text="Ingresa tu correo electrónico",
            prefix_icon=ft.icons.EMAIL,
        )
        self.campo_contraseña = ft.TextField(
            label="Contraseña",
            hint_text="Ingresa tu contraseña",
            password=True,
            prefix_icon=ft.icons.LOCK,
        )
        self.campo_confirmar_contraseña = ft.TextField(
            label="Confirmar Contraseña",
            hint_text="Confirma tu contraseña",
            password=True,
            prefix_icon=ft.icons.LOCK_CLOCK,
        )
        self.boton_registrar = ft.ElevatedButton(
            "Registrarse",
            on_click=self.clic_registrar,
            style=ft.ButtonStyle(
                color={ft.MaterialState.DEFAULT: ft.colors.WHITE},
                bgcolor={ft.MaterialState.DEFAULT: ft.colors.PRIMARY}
            ),
            width=200
        )

        self.content = ft.Column(
            controls=[
                ft.Text("Registrarse", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.campo_correo,
                self.campo_contraseña,
                self.campo_confirmar_contraseña,
                ft.Text(
                    "La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas, números y caracteres especiales.",
                    size=12,
                    color=ft.colors.GREY_700,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.boton_registrar
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

    def clic_registrar(self, e):
        correo = self.campo_correo.value
        contraseña = self.campo_contraseña.value
        confirmar_contraseña = self.campo_confirmar_contraseña.value

        if not es_correo_valido(correo):
            self.mostrar_error("Por favor, ingresa un correo electrónico válido.")
            return

        if not es_contraseña_valida(contraseña):
            self.mostrar_error("La contraseña no cumple con los requisitos de seguridad.")
            return

        if contraseña != confirmar_contraseña:
            self.mostrar_error("Las contraseñas no coinciden, inténtalo nuevamente")
            return

        try:
            respuesta = requests.post(
                f"{URL_BASE_API}/auth/register",
                json={"email": correo, "password": contraseña},
                verify=RUTA_CERTIFICADO
            )

            if respuesta.status_code == 201:
                self.mostrar_popup_verificacion(correo)
            elif respuesta.status_code == 400:
                detail = respuesta.json().get('detail', '')
                if "REGISTER_USER_ALREADY_EXISTS" in detail:
                    
                    verificacion_respuesta = requests.get(
                        f"{URL_BASE_API}/auth/check-verification/{correo}",
                        verify=RUTA_CERTIFICADO
                    )
                    if verificacion_respuesta.status_code == 200:
                        is_verified = verificacion_respuesta.json().get('is_verified', False)
                        if not is_verified:
                            self.manejar_usuario_no_verificado(correo, contraseña)
                        else:
                            self.manejar_usuario_existente(correo)
                    else:
                        self.mostrar_error("No se pudo verificar el estado del usuario.")
                else:
                    self.mostrar_error(f"Falló el registro: {detail}")
            else:
                self.mostrar_error(f"Falló el registro: {respuesta.json().get('detail', 'Error desconocido')}")
        except requests.RequestException as e:
            self.mostrar_error(f"Error en el registro: {str(e)}")
    def manejar_usuario_no_verificado(self, correo, contraseña):
        try:
            respuesta = requests.post(
                f"{URL_BASE_API}/auth/update-unverified",
                json={"email": correo, "password": contraseña},
                verify=RUTA_CERTIFICADO
            )
            if respuesta.status_code == 200:
                self.mostrar_popup_verificacion(correo, reenvio=True)
            else:
                self.mostrar_error("No se pudo actualizar la información. Por favor, intenta más tarde.")
        except requests.RequestException as e:
            self.mostrar_error(f"Error al actualizar la información: {str(e)}")

    def manejar_usuario_existente(self, correo):
        def cerrar_dialogo(_):
            self.pagina.dialog.open = False
            self.pagina.update()
        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Usuario ya registrado",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.PRIMARY
                    ),
                    ft.Text(
                        f"El correo {correo} ya está registrado y verificado. ¿Qué deseas hacer?",
                        size=14,
                        color=ft.colors.GREY_700
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Ir a inicio de sesión",
                                on_click=self.ir_a_inicio_sesion
                            ),
                            ft.OutlinedButton(
                                "Olvidé mi contraseña",
                                on_click=lambda _: self.solicitar_reseteo_contraseña(correo)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                spacing=20,
                width=400
            ),
            padding=20,
            border_radius=10,
            bgcolor=ft.colors.WHITE
        )

        self.pagina.dialog = ft.AlertDialog(
            modal=True,
            content=contenido,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
        
        self.pagina.dialog.open = True
        self.pagina.update()

    def solicitar_reseteo_contraseña(self, correo):
        # Implementa la lógica para solicitar el reseteo de contraseña
        pass

    def ir_a_inicio_sesion(self, e):
        self.pagina.dialog.open = False
        self.pagina.dialog.close()
    def mostrar_popup_verificacion(self, correo, reenvio=False):
        def cerrar_dialogo():
            self.pagina.dialog.open = False
            self.pagina.update()
        mensaje = "Hemos enviado un nuevo código de verificación a tu correo electrónico. " if reenvio else "Hemos enviado un código de verificación a tu correo electrónico. "
        mensaje += "Por favor, ingresa el código de 6 dígitos a continuación:"

        self.campo_codigo_verificacion = ft.TextField(
            label="Código de Verificación",
            hint_text="Ingresa el código de 6 dígitos",
            border=ft.InputBorder.OUTLINE,
            filled=True,
            prefix_icon=ft.icons.NUMBERS,
            width=200
        )

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Verificación de Correo Electrónico",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.PRIMARY
                    ),
                    ft.Text(mensaje, size=14, color=ft.colors.GREY_700, text_align=ft.TextAlign.CENTER),
                    self.campo_codigo_verificacion,
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Verificar",
                                on_click=lambda _: self.verificar_codigo(correo),
                                style=ft.ButtonStyle(
                                    color={ft.MaterialState.DEFAULT: ft.colors.WHITE},
                                    bgcolor={ft.MaterialState.DEFAULT: ft.colors.PRIMARY}
                                )
                            ),
                            ft.OutlinedButton(
                                "Cancelar",
                                on_click=lambda x: cerrar_dialogo()
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                spacing=20,
                width=300,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            border_radius=10,
            bgcolor=ft.colors.WHITE
        )

        self.pagina.dialog = ft.AlertDialog(
            modal=True,
            content=contenido,
            actions=[
                ft.TextButton("Cerrar", on_click=lambda x:cerrar_dialogo())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.pagina.dialog.open = True
        self.pagina.update()
    def verificar_codigo(self, correo):
        codigo = self.campo_codigo_verificacion.value
        try:
            respuesta = requests.post(
                f"{URL_BASE_API}/auth/verify",
                json={"email": correo, "code": codigo},
                verify=RUTA_CERTIFICADO
            )

            respuesta.raise_for_status()

            if respuesta.status_code == 200:
                # Primero, cerramos el diálogo de verificación
                self.pagina.dialog.open = False
                self.pagina.update()

                # Mostramos el mensaje de bienvenida
                self.pagina.snack_bar = ft.SnackBar(
                    ft.Text("Verificación completada, ¡bienvenido!"),
                    open=True,
                    action="OK",
                )
                self.pagina.snack_bar.open = True
                self.pagina.update()
                
                # Esperamos un momento para que el usuario pueda ver el mensaje
                self.redirigir_a_inicio_sesion
            else:
                self.mostrar_error(f"Error en la verificación: {respuesta.json().get('detail', 'Error desconocido')}")

        except requests.RequestException as e:
            self.mostrar_error(f"Error en la verificación: {str(e)}")

    def redirigir_a_inicio_sesion(self):
        from components.usuario import PantallaInicioSesion
        pantalla_inicio_sesion = PantallaInicioSesion(self.pagina)
        self.pagina.clean()
        self.pagina.add(pantalla_inicio_sesion)
        
        # Si hay alguna función adicional que deba ejecutarse después del registro
        if self.al_registrarse:
            self.al_registrarse()
    def mostrar_error(self, mensaje):
        self.pagina.snack_bar = ft.SnackBar(
            ft.Text(mensaje),
            open=True,
            action="OK",
        )
        self.pagina.snack_bar.open = True
        self.pagina.update()
