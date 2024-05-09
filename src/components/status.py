import flet as ft
import asyncio
import aiohttp

class MachineCards(ft.Row):
    def __init__(self, machines,access_token, update_interval=1):
        super().__init__()
        self.machines = machines
        self.update_interval = update_interval
        self.access_token = access_token
        print("MachineCards initialized")

    def did_mount(self):
        print("MachineCards did_mount")
        self.access_token = self.page.client_storage.get("access_token")
        self.page.run_task(self.update_machine_cards)

    async def update_machine_cards(self):
        print("Starting update_machine_cards loop")
        while True:
            print("Updating machine cards...")
            tasks = [self.fetch_and_create_card(machine_id) for machine_id in self.machines]
            cards = await asyncio.gather(*tasks)
            self.controls = cards
            self.update()
            print(f"Updated UI with {len(cards)} cards")
            await asyncio.sleep(self.update_interval)

    async def fetch_and_create_card(self, machine_id):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"http://localhost:8000/maquinas/{machine_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return self.create_machine_card(data)
                else:
                    return ft.Text(f"Error fetching data for machine {machine_id}")

    def create_machine_card(self, data):
        return ft.Card(
            content=ft.Column(
                controls=[
                    ft.Text(f"{data['nombre']}", size=20, weight='bold'),
                    *[ft.Text(f"Tipo: {sensor['tipo']} ({sensor['unidad']}) Valor: {sensor['valor']} Estado: {'Activo' if sensor['estado'] else 'Inactivo'}") for sensor in data['sensores']]
                ]
            )
        )