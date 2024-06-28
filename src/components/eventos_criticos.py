import flet as ft
import aiohttp
import asyncio

class CriticalEventsViewer(ft.Container):
    def __init__(self, access_token):
        super().__init__()
        self.access_token = access_token
        
        self.events_list = ft.ListView(spacing=10, padding=20, auto_scroll=True)
        self.refresh_button = ft.ElevatedButton("Actualizar eventos críticos", on_click=self.refresh_events)
        
        self.content = ft.Column([
            ft.Text("Eventos Críticos", size=24, weight=ft.FontWeight.BOLD),
            self.refresh_button,
            self.events_list
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        self.padding = 20
        self.expand = True
        
    def did_mount(self):
        self.refresh_events(None)
        
    def refresh_events(self, e):
        asyncio.run(self.fetch_events())
        
    async def fetch_events(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = "https://localhost/api/eventos-criticos/"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        events = await response.json()
                        self.display_events(events)
                    else:
                        print(f"Error fetching critical events: {response.status}")
        except Exception as e:
            print(f"Error: {str(e)}")
            
    def display_events(self, events):
        self.events_list.controls.clear()
        for event in events:
            self.events_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"ID: {event['id']}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Sensor: {event['sensor_id']}"),
                            ft.Text(f"Valor: {event['value']}"),
                            ft.Text(f"Descripción: {event['description']}"),
                            ft.Text(f"Fecha: {event['timestamp']}")
                        ]),
                        padding=10
                    ),
                    elevation=2
                )
            )
        self.update()