import asyncio
import aiohttp
import flet as ft
import pytz
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzlocal
from datetime import datetime
class MachineCards(ft.Row):
    def __init__(self, machines, access_token, update_interval=1):
        super().__init__()
        self.machines = machines
        self.update_interval = update_interval
        self.access_token = access_token
    def format_timedelta(self,delta):
        if delta.days > 0:
            return f"last update {delta.days} days ago"
        elif delta.hours > 0:
            return f"last update {delta.hours} hours ago"
        elif delta.minutes > 0:
            return f"last update {delta.minutes} minutes ago"
        else:
            return "last update moments ago"
    def find_newest_update(self,data):
        # Extract the list of sensors
        sensors = data['sensores']
        
        # Find the sensor with the newest date
        newest_update = max(sensors, key=lambda x: datetime.fromisoformat(x['fecha_hora'][:-6]))
        return newest_update['fecha_hora']
    def last_update_time(self,utc_datetime_str):
        # Adjust the timezone string format to remove the colon
        adjusted_datetime_str = utc_datetime_str[:-3] + utc_datetime_str[-2:]
        
        # Parse the UTC datetime string
        utc_datetime = datetime.fromisoformat(adjusted_datetime_str)
        utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
        
        # Convert UTC datetime to local time
        local_datetime = utc_datetime.astimezone(tzlocal())
        
        # Calculate the time difference
        now = datetime.now(tzlocal())
        delta = relativedelta(now, local_datetime)
        
        # Format the last update string
        if delta.days > 0:
            return f"ultima actualización {delta.days} días atrás"
        elif delta.hours > 0:
            return f"ultima actualización  {delta.hours} horas atrás"
        elif delta.minutes > 0:
            return f"ultima actualización  {delta.minutes} minutos atrás"
        else:
            return "hace unos momentos"       

    def did_mount(self):
        
        # Access token can be updated from client storage if needed
        # self.access_token = self.page.client_storage.get("access_token")
        self.page.run_task(self.update_machine_cards)

    async def update_machine_cards(self):
        print("Starting update_machine_cards loop")
        while True:
            tasks = [self.fetch_and_create_card(machine_id) for machine_id in self.machines]
            cards = await asyncio.gather(*tasks)
            self.controls = cards
            self.update()
            print(f"Updated UI with {len(cards)} cards")
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
                        return ft.Text(f"Error {response.status}: No se puedo obtener datos sobre la maquina {machine_id}")
            except aiohttp.ClientError as e:
                return ft.Text(f"Error HTTP: {str(e)}")
            except Exception as e:
                return ft.Text(f"Algo Salio mal: {str(e)}")

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
            if sensor_unit == 'estado':
                sensor_description = f"{sensor_name}"
            else:
                sensor_description = f"{sensor_name}: {sensor_value} {sensor_unit}"

            sensor_row = ft.Row([
                ft.Icon(name=icon, color=color),
                ft.Text(sensor_description, color=color)
            ])
            sensor_controls.append(sensor_row)
        card = ft.Container(
            content=ft.Card(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Icon(ft.icons.ALBUM),
                            ft.Text(f"{data.get('nombre', 'Maquina Desconocida')}", size=25, weight='bold', font_family='Roboto',text_align=ft.TextAlign.CENTER),
                        ],tight=True, alignment=ft.MainAxisAlignment.CENTER),  # Center alignment for the title row
                        ft.Text(self.last_update_time(self.find_newest_update(data)), size=12, color='grey'),  # Center alignment for update time
                        *sensor_controls
                    ],alignment=ft.MainAxisAlignment.CENTER

                ),
                variant=ft.CardVariant.OUTLINED,
                margin=5,
                elevation=5,

                is_semantic_container=False,
                expand_loose=True
            ),
            padding=10,
            margin=15,
            alignment=ft.alignment.center,
            expand=True
# Padding around the Card
              # Take full width available
        )#width=ft.FULL,  # Take full width available
            
            
        return card
