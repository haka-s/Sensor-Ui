import flet as ft
from components.navegacion import ResponsiveMenuLayout
from components.test import test
from components.usuario import Login
if __name__ == "__main__":

    def main(page: ft.Page, title="Basic Responsive Menu"):

        page.title = title
        login_screen = Login(page)
        if not is_user_authenticated(page):
            
            page.add(login_screen)
        else:
            # Display the main app content

            #menu_button.on_click = lambda e: menu_layout.toggle_navigation()

            menu_button = ft.IconButton(ft.icons.MENU)

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
                        label="Menu in landscape",
                    ),
                    test(),
                ),
                (
                    dict(
                        icon=ft.icons.PORTRAIT_OUTLINED,
                        selected_icon=ft.icons.PORTRAIT,
                        label="Menu in portrait",
                    ),
                    create_page(
                        "Menu in portrait",
                        "Menu in portrait is mainly expected to be used on a smaller mobile device."
                        "\n\n"
                        "The menu is by default hidden, and when shown with the menu button it is placed on top of the main "
                        "content."
                        "\n\n"
                        "In addition to the menu button, menu can be dismissed by a tap/click on the main content area.",
                    ),
                ),
                (
                    dict(
                        icon=ft.icons.INSERT_EMOTICON_OUTLINED,
                        selected_icon=ft.icons.INSERT_EMOTICON,
                        label="Minimize to icons",
                    ),
                    create_page(
                        "Minimize to icons",
                        "ResponsiveMenuLayout has a parameter minimize_to_icons. "
                        "Set it to True and the menu is shown as icons only, when normally it would be hidden.\n"
                        "\n\n"
                        "Try this with the 'Minimize to icons' toggle in the top bar."
                        "\n\n"
                        "There are also landscape_minimize_to_icons and portrait_minimize_to_icons properties that you can "
                        "use to set this property differently in each orientation.",
                    ),
                ),
                (
                    dict(
                        icon=ft.icons.COMPARE_ARROWS_OUTLINED,
                        selected_icon=ft.icons.COMPARE_ARROWS,
                        label="Menu width",
                    ),
                    create_page(
                        "Menu width",
                        "ResponsiveMenuLayout has a parameter manu_extended. "
                        "Set it to False to place menu labels under the icons instead of beside them."
                        "\n\n"
                        "Try this with the 'Menu width' toggle in the top bar.",
                    ),
                ),
                (
                    dict(
                        icon=ft.icons.ROUTE_OUTLINED,
                        selected_icon=ft.icons.ROUTE,
                        label="Route support",
                        route="custom-route",
                    ),
                    create_page(
                        "Route support",
                        "ResponsiveMenuLayout has a parameter support_routes, which is True by default. "
                        "\n\n"
                        "Routes are useful only in the web, where the currently selected page is shown in the url, "
                        "and you can open the app directly on a specific page with the right url."
                        "\n\n"
                        "You can specify a route explicitly with a 'route' item in the menu dict (see this page in code). "
                        "If you do not specify the route, a slugified version of the page label is used "
                        "('Menu width' becomes 'menu-width').",
                    ),
                ),
                (
                    dict(
                        icon=ft.icons.PLUS_ONE_OUTLINED,
                        selected_icon=ft.icons.PLUS_ONE,
                        label="Fine control",
                    ),
                    create_page(
                        "Adjust navigation rail",
                        "NavigationRail is accessible via the navigation_rail attribute of the ResponsiveMenuLayout. "
                        "In this demo it is used to add the leading button control."
                        "\n\n"
                        "These NavigationRail attributes are used by the ResponsiveMenuLayout, and changing them directly "
                        "will probably break it:\n"
                        "- destinations\n"
                        "- extended\n"
                        "- label_type\n"
                        "- on_change\n",
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


            page.add(menu_layout)

            menu_button.on_click = lambda e: menu_layout.toggle_navigation()

    def is_user_authenticated(page):
        # Check if the user is authenticated (e.g., by retrieving the access token from persistent storage)
        access_token = load_access_token(page)
        return access_token is not None

    def load_access_token(page):
        token = page.client_storage.get("access_token")
        return token  # Replace with the actual implementation

    def navigate_to_main_app(page):
        page.update()
        pass
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

    ft.app(target=main)