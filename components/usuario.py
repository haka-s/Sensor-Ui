import flet as ft
import requests

API_BASE_URL = "http://localhost:8000"


class Login(ft.Row):
    def __init__(self,page):
        super().__init__()
        self.page = page
        #self.page.title = "Login/Register"
        
        self.login()

    def login(self):
            page = self.page
            page.title = "Login/Register"
            page.vertical_alignment = ft.MainAxisAlignment.CENTER
            page.horizontal_alignment = ft.MainAxisAlignment.CENTER
            self.username_textfield = ft.TextField(
                label="Username", hint_text="Enter your username"
            )
            self.password_textfield = ft.TextField(
                label="Password", hint_text="Enter your password", password=True
            )
            login_button = ft.ElevatedButton("Login", on_click=self.login_click)
            register_button = ft.ElevatedButton("Register", on_click=self.register_click)
            
            self.page.add(
                ft.Column(
                    [
                        ft.Text("Login/Register", size=24, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        self.username_textfield,
                        self.password_textfield,
                        login_button,
                        register_button,
                    ],
                    width=300,
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
    def login_click(self,e):
        print('login click')
        username = self.username_textfield.value
        password = self.password_textfield.value
        print(username,password)
        response = requests.post(
            f"{API_BASE_URL}/auth/jwt/login",
            data={"username": username, "password": password},
        )
        print(response)
        if response.status_code == 200:
            print('sucess!')
            token = response.json()["access_token"]
            self.page.client_storage.set("access_token", token)
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Login successful!"), open=True, action="OK"
            )
            # Navigate to the main app screen
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Login failed. Please check your credentials."),
                open=True,
                action="OK",
            )

    def register_click(self,e):
        username = self.username_textfield.value
        password = self.password_textfield.value

        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"email": username, "password": password},
        )

        if response.status_code == 201:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Registration successful! You can now log in."),
                open=True,
                action="OK",
            )
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Registration failed. Please try again."),
                open=True,
                action="OK",
            )