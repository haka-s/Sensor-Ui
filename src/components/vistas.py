import flet as ft

# Assuming these components are correctly defined in your project
from components.navegacion import ResponsiveMenuLayout
from usuario import Login

def is_user_authenticated(page):
    return getattr(page, 'user_authenticated', False)

def show_login_screen(page):
    # Function to display the login screen
    login_screen = Login(page)
    
    def on_login_click(e):
        page.user_authenticated = True
        show_main_content(page)
        
    login_screen.submit_button.on_click = on_login_click

    page.controls.clear()
    page.add(login_screen)

def show_main_content(page):
    # Function to display the main content after login
    menu_button = ft.IconButton(ft.icons.MENU, on_click=lambda e: toggle_menu(page))

    page.appbar = ft.AppBar(
        leading=menu_button,
        leading_width=40,
        title=ft.Text("Dashboard maquinas"),
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    # Add main content here, e.g., using ResponsiveMenuLayout
    main_content = ResponsiveMenuLayout()
    page.controls.clear()
    page.add(main_content)

def toggle_menu(page):
    # Toggle the navigation menu or other elements
    pass

def main(page: ft.Page):
    page.title = "Basic Responsive Menu"

    if not is_user_authenticated(page):
        show_login_screen(page)
    else:
        show_main_content(page)

if __name__ == "__main__":
    ft.app(target=main)