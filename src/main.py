import flet as ft
import requests
from components.navegacion import ResponsiveMenuLayout
from components.status import MachineCards
from components.usuario import PantallaInicioSesion
from components.historical_analysis import VisualizadorDatosSensor
from components.eventos_criticos import CriticalEventsViewer
from components.notificaciones import NotificationsViewer

URL_BASE_API = "https://localhost/api"

def verificar_token(token_acceso):
    try:
        respuesta = requests.get(
            f"{URL_BASE_API}/auth/verify",
            headers={"Authorization": f"Bearer {token_acceso}"},
            verify=r"cert\fullchain.pem"
        )
        return respuesta.status_code == 200
    except requests.RequestException:
        return False

def esta_usuario_autenticado(page):
    token_acceso = page.client_storage.get("access_token")
    if token_acceso:
        return verificar_token(token_acceso)
    return False

def crear_pagina(titulo: str, cuerpo: str):
    return ft.Row(
        controls=[
            ft.Column(
                horizontal_alignment="stretch",
                controls=[
                    ft.Card(content=ft.Container(ft.Text(titulo, weight="bold"), padding=8)),
                    ft.Text(cuerpo),
                ],
                expand=True,
            ),
        ],
        expand=True,
    )

def main(page: ft.Page):
    page.title = "Dashboard de máquinas"
    page.theme = ft.Theme(color_scheme_seed="Orange", use_material3=True)
    page.theme_mode = ft.ThemeMode.LIGHT

    def mostrar_pantalla_inicio_sesion():
        page.title = "Inicio de sesión"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        pantalla_inicio_sesion = PantallaInicioSesion(page, al_iniciar_sesion=mostrar_menu_principal)
        page.clean()
        page.add(pantalla_inicio_sesion)

    def mostrar_menu_principal():
        def obtener_maquinas():
            token_acceso = page.client_storage.get("access_token")
            respuesta = requests.get(
                f"{URL_BASE_API}/maquinas/lista",
                headers={"Authorization": f"Bearer {token_acceso}"},
                verify=r"cert\fullchain.pem"
            )
            if respuesta.status_code == 200:
                return respuesta.json()
            return []

        boton_menu = ft.IconButton(ft.icons.MENU)
        token_acceso = page.client_storage.get("access_token")
        
        maquinas = obtener_maquinas()
        
        opciones_maquinas = [ft.dropdown.Option(text=maquina['nombre'], key=str(maquina['id'])) for maquina in maquinas]
        
        selector_maquinas = ft.Dropdown(
            label="Seleccionar máquina",
            options=opciones_maquinas,
            width=200,
        )

        token_acceso = page.client_storage.get("access_token")
        
        componente_tarjetas_maquinas = MachineCards(access_token=token_acceso)
        historico = VisualizadorDatosSensor(token_acceso=token_acceso)
        notificaciones = NotificationsViewer(access_token=token_acceso)
        eventos = CriticalEventsViewer(access_token=token_acceso)
        
        page.appbar = ft.AppBar(
            leading=boton_menu,
            leading_width=40,
            title=ft.Text("Dashboard máquinas"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="Cambiar contraseña", on_click=cambiar_contraseña),
                        ft.PopupMenuItem(text="Cerrar sesión", on_click=cerrar_sesion),
                    ]
                ),
            ],
        )
        
        paginas = [
            (
                dict(
                    icon=ft.icons.LANDSCAPE_OUTLINED,
                    selected_icon=ft.icons.LANDSCAPE,
                    label="Estado actual",
                ),
                ft.Row(controls=[
                    ft.Column(
                        horizontal_alignment="stretch",
                        controls=[
                            ft.Card(content=ft.Container(ft.Text('Estado actual', weight="bold"), padding=8)),
                            componente_tarjetas_maquinas
                        ],
                        expand=True,
                    ),
                ],
                expand=True,)
            ),
            (
                dict(
                    icon=ft.icons.BAR_CHART_OUTLINED,
                    selected_icon=ft.icons.BAR_CHART,
                    label="Datos Históricos",
                ),
                ft.Row(controls=[
                    ft.Column(
                        horizontal_alignment="stretch",
                        controls=[
                            ft.Card(content=ft.Container(ft.Text('Datos Históricos', weight="bold"), padding=8)),
                            historico
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
                )
            ),
            (
                dict(
                    icon=ft.icons.NOTIFICATIONS_OUTLINED,
                    selected_icon=ft.icons.NOTIFICATIONS,
                    label="Notificaciones",
                ),
                ft.Row(controls=[
                    ft.Column(
                        horizontal_alignment="stretch",
                        controls=[
                            ft.Card(content=ft.Container(ft.Text('Notificaciones', weight="bold"), padding=8)),
                            notificaciones
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
                )
            ),
            (
                dict(
                    icon=ft.icons.STOP_CIRCLE_OUTLINED,
                    selected_icon=ft.icons.STOP_CIRCLE,
                    label="Reportes",
                ),
                ft.Row(controls=[
                    ft.Column(
                        horizontal_alignment="stretch",
                        controls=[
                            ft.Card(content=ft.Container(ft.Text('Reportes', weight="bold"), padding=8)),
                            eventos
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
                )
            ),
            (
                dict(
                    icon=ft.icons.INFO_OUTLINE,
                    selected_icon=ft.icons.INFO,
                    label="Acerca del programa",
                ),
                crear_pagina(
                    "Información sobre el programa:",
                    "Sistema desarrollado por Santiago Motta\n",
                ),
            ),
        ]

        disposicion_menu = ResponsiveMenuLayout(page, paginas)
        page.clean()
        page.add(disposicion_menu)
        boton_menu.on_click = lambda e: disposicion_menu.toggle_navigation()

    def cerrar_sesion(_):
        page.client_storage.remove("access_token")
        mostrar_pantalla_inicio_sesion()

    def cambiar_contraseña(_):
        mostrar_dialogo_cambio_contraseña()

    def mostrar_dialogo_cambio_contraseña():
        campo_contraseña_actual = ft.TextField(label="Contraseña actual", password=True)
        campo_nueva_contraseña = ft.TextField(label="Nueva contraseña", password=True)
        campo_confirmar_contraseña = ft.TextField(label="Confirmar nueva contraseña", password=True)

        def confirmar_cambio_contraseña(e):
            if campo_nueva_contraseña.value != campo_confirmar_contraseña.value:
                page.snack_bar = ft.SnackBar(content=ft.Text("Las contraseñas no coinciden"))
                page.snack_bar.open = True
                page.update()
                return

            token_acceso = page.client_storage.get("access_token")
            respuesta = requests.post(
                f"{URL_BASE_API}/auth/change-password",
                headers={"Authorization": f"Bearer {token_acceso}"},
                json={
                    "current_password": campo_contraseña_actual.value,
                    "new_password": campo_nueva_contraseña.value
                },
                verify=r"cert\fullchain.pem"
            )

            if respuesta.status_code == 200:
                page.snack_bar = ft.SnackBar(content=ft.Text("Contraseña cambiada exitosamente"))
                page.dialog.open = False
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Error al cambiar la contraseña"))
            
            page.snack_bar.open = True
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Cambiar contraseña"),
            content=ft.Column([
                campo_contraseña_actual,
                campo_nueva_contraseña,
                campo_confirmar_contraseña
            ]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, 'open', False)),
                ft.TextButton("Confirmar", on_click=confirmar_cambio_contraseña)
            ]
        )
        page.dialog.open = True
        page.update()

    def verificar_autenticacion():
        if esta_usuario_autenticado(page):
            mostrar_menu_principal()
        else:
            mostrar_pantalla_inicio_sesion()
    #async await verificar_autenticacion()
    verificar_autenticacion()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")