import flet as ft
from components.inicio_sesion import InicioSesion
from components.registro import Registro

class PantallaInicioSesion(ft.Column):
    def __init__(self, pagina, al_iniciar_sesion=None):
        super().__init__(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        self.pagina = pagina
        self.formulario_inicio_sesion = InicioSesion(pagina, al_iniciar_sesion=al_iniciar_sesion)
        self.enlace_registro = ft.TextButton("¿No tienes cuenta? Regístrate", on_click=self.mostrar_registro)
        
        self.controls = [self.formulario_inicio_sesion, self.enlace_registro]

    def mostrar_registro(self, e):
        pantalla_registro = PantallaRegistro(self.pagina, al_registrarse=self.mostrar_inicio_sesion)
        self.pagina.clean()
        self.pagina.add(pantalla_registro)

    def mostrar_inicio_sesion(self):
        self.pagina.clean()
        self.pagina.add(self)

class PantallaRegistro(ft.Column):
    def __init__(self, pagina, al_registrarse=None):
        super().__init__(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        self.pagina = pagina
        self.formulario_registro = Registro(pagina, al_registrarse=al_registrarse)
        self.enlace_inicio_sesion = ft.TextButton("¿Ya tienes cuenta? Inicia sesión", on_click=self.mostrar_inicio_sesion)
        
        self.controls = [self.formulario_registro, self.enlace_inicio_sesion]

    def mostrar_inicio_sesion(self, e):
        pantalla_inicio_sesion = PantallaInicioSesion(self.pagina)
        self.pagina.clean()
        self.pagina.add(pantalla_inicio_sesion)