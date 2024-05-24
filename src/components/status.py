import asyncio
import aiohttp
import flet as ft

class MachineCards(ft.Row):
    def __init__(self, machines, access_token, update_interval=1):
        super().__init__()
        self.machines = machines
        self.update_interval = update_interval
        self.access_token = access_token
        

    def did_mount(self):
        
        # Access token can be updated from client storage if needed
        # self.access_token = self.page.client_storage.get("access_token")
        self.page.run_task(self.update_machine_cards)

    async def update_machine_cards(self):
        print("Starting update_machine_cards loop")
        while True:
            #print("Updating machine cards...")
            tasks = [self.fetch_and_create_card(machine_id) for machine_id in self.machines]
            cards = await asyncio.gather(*tasks)
            self.controls = cards
            self.update()
            #print(f"Updated UI with {len(cards)} cards")
            await asyncio.sleep(self.update_interval)

    async def fetch_and_create_card(self, machine_id):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with aiohttp.ClientSession() as session:
            url = f"http://localhost:8000/maquinas/{machine_id}"
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self.create_machine_card(data)
                    else:
                        return ft.Text(f"Error {response.status}: Unable to fetch data for machine {machine_id}")
            except aiohttp.ClientError as e:
                return ft.Text(f"HTTP error occurred: {str(e)}")
            except Exception as e:
                return ft.Text(f"An error occurred: {str(e)}")

    def create_machine_card(self, data):
        sensor_icons = {
            "boolean": "POWER_SETTINGS_NEW_ROUNDED",
            "distancia": "space_dashboard",
            "velocidad": "speed",
            "energia": "bolt",
            "presion": "compress",
            "volumen": "waves",
            "temperatura": "thermostat"
        }

        sensor_controls = []
        for sensor in data.get('sensores', []):  # Safe access to 'sensores'
            sensor_name = sensor.get('nombre', 'Sensor Desconocido')
            color = "green" if sensor.get('estado') else "red"
            icon = sensor_icons.get(sensor.get('tipo', 'unknown'), "device_unknown")
            sensor_type = sensor.get('tipo', 'unknown').capitalize()
            sensor_value = sensor.get('valor', 'N/A')
            sensor_unit = sensor.get('unidad', '')
            status = 'Activo' if sensor.get('estado') else 'Inactivo'
            sensor_description = f"{sensor_name} ({sensor_type}): {sensor_value} {sensor_unit} - {status}"

            sensor_row = ft.Row([
                ft.Icon(name=icon, color=color),
                ft.Text(sensor_description, color=color)
            ])
            sensor_controls.append(sensor_row)

        card = ft.Card(
            content=ft.Column(
                controls=[
                    ft.Text(f"{data.get('nombre', 'Unknown Machine')}", size=20, weight='bold'),
                    *sensor_controls
                ]
            ),
            elevation=5
        )
        
        return card
