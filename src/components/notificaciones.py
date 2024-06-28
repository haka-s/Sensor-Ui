import flet as ft
import aiohttp
import asyncio

class NotificationsViewer(ft.Column):
    def __init__(self, access_token):
        super().__init__()
        self.access_token = access_token
        
        self.notifications_list = ft.ListView(spacing=10, padding=20, auto_scroll=True)
        self.refresh_button = ft.ElevatedButton("Actualizar notificaciones", on_click=self.refresh_notifications)
        
        self.controls = [
            ft.Text("Notificaciones", size=24, weight=ft.FontWeight.BOLD),
            self.refresh_button,
            self.notifications_list
        ]
        self.spacing = 20
        
    def did_mount(self):
        self.refresh_notifications(None)
        
    def refresh_notifications(self, e):
        asyncio.run(self.fetch_notifications())
        
    async def fetch_notifications(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = "https://localhost/api/notificaciones/"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        notifications = await response.json()
                        self.display_notifications(notifications)
                    else:
                        print(f"Error fetching notifications: {response.status}")
        except Exception as e:
            print(f"Error: {str(e)}")
            
    def display_notifications(self, notifications):
        self.notifications_list.controls.clear()
        for notification in notifications:
            self.notifications_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"Evento: {notification['event_id']}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Enviado a: {notification['sent_to']}"),
                            ft.Text(f"Estado: {notification['status']}"),
                            ft.Text(f"Fecha: {notification['sent_timestamp']}")
                        ]),
                        padding=10
                    )
                )
            )
        self.update()