import asyncio
import flet as ft
from components.navegacion import ResponsiveMenuLayout
from components.status import MachineCards
from components.test import test
from components.usuario import LoginRegisterScreen
from components.historical_analysis import SensorDataViewer
def main(page: ft.Page, title="Dashboard de maquinas"):
    page.title = title
    page.appbar = None
    page.snack_bar = None
    machine_ids = [1,2,3]  
    page.theme = ft.Theme(color_scheme_seed="Orange",use_material3=True)
    page.theme_mode = ft.ThemeMode.LIGHT
      
    def show_login_register_screen():
        page.title = "Inicio de sesión/registro"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        login_register_screen = LoginRegisterScreen(page, on_login_success=show_main_menu)
        page.clean()
        page.add(login_register_screen)

    def show_main_menu():
        menu_button = ft.IconButton(ft.icons.MENU)
        access_token = page.client_storage.get("access_token")
        machine_cards_component = MachineCards(machines=machine_ids,access_token=access_token)
        historical = SensorDataViewer(access_token=access_token)
        page.appbar = ft.AppBar(
            leading=menu_button,
            leading_width=40,
            title=ft.Text("Dashboard maquinas"),
            bgcolor=ft.colors.SURFACE_VARIANT,
        )

        pages = [
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
                            machine_cards_component
                        ],
                        expand=True,
                    ),
                ],
                expand=True,)
            ),
            (
                dict(
                    icon=ft.icons.LANDSCAPE_OUTLINED,
                    selected_icon=ft.icons.LANDSCAPE,
                    label="Datos Históricos",
                ),
                ft.Row(controls=[
                    ft.Column(
                        horizontal_alignment="stretch",
                        controls=[
                            ft.Card(content=ft.Container(ft.Text('Datos Históricos', weight="bold"), padding=8)),
                            historical
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
                create_page(
                    "Información sobre el programa:",
                    "Sistema "
                    "desarrollado por Santiago Motta\n",
                ),
            ),
        ]

        menu_layout = ResponsiveMenuLayout(page, pages)

        page.appbar.actions = [
            ft.TextButton(text="Cerrar sesión", on_click=lambda e: logout()),
            ft.TextButton(text="Cambiar contraseña", on_click=lambda e: change_password())
        ]

        page.clean()
        page.add(menu_layout)

        menu_button.on_click = lambda e: menu_layout.toggle_navigation()

    if not is_user_authenticated(page):
        show_login_register_screen()
    else:
        show_main_menu()

def is_user_authenticated(page):
    access_token = load_access_token(page)
    return access_token is not None

def load_access_token(page):
    return page.client_storage.get("access_token")

def create_page(title: str, body: str):
    return ft.Row(
        controls=[
            ft.Column(
                horizontal_alignment="stretch",
                controls=[
                    ft.Card(content=ft.Container(ft.Text(title, weight="bold"), padding=8)),
                    ft.Text(body),
                ],
                expand=True,
            ),
        ],
        expand=True,
    )

def logout():
    # Add the logic for logging out
    print("User logged out successfully")

def change_password():
    # Add the logic for changing password
    print("Change password dialog opened")



if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")