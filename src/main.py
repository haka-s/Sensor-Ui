import asyncio
import flet as ft
from components.navegacion import ResponsiveMenuLayout
from components.status import MachineCards
from components.test import test
from components.usuario import LoginRegisterScreen

def main(page: ft.Page, title="Dashboard de maquinas"):
    page.title = title
    page.appbar = None
    page.snack_bar = None
    machine_ids = [1, 2,3]  
    
    
    
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
        print(machine_cards_component)
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
                            machine_cards_component
                        ],
                        expand=True,
                    ),
                ],
                expand=True,)
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
            ft.Row(
                [
                    ft.Text("Minimize\nto icons"),
                    ft.Switch(on_change=lambda e: toggle_icons_only(menu_layout)),
                    ft.Text("Menu\nwidth"),
                    ft.Switch(
                        value=True, on_change=lambda e: toggle_menu_width(menu_layout)
                    ),
                ]
            )
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

def toggle_icons_only(menu: ResponsiveMenuLayout):
    menu.minimize_to_icons = not menu.minimize_to_icons
    menu.page.update()

def toggle_menu_width(menu: ResponsiveMenuLayout):
    menu.menu_extended = not menu.menu_extended
    menu.page.update()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")