import flet as ft
import asyncio
import aiohttp

async def machine_cards(page, machines, update_interval=10):
    access_token = page.client_storage.get("access_token")

    def sensor_card(sensor):
        return ft.Card(
            content=ft.Column([
                ft.Text(f"Tipo: {sensor['tipo']} ({sensor['unidad']})"),
                ft.Text(f"Valor: {sensor['valor']}"),
                ft.Text(f"Estado: {'Activo' if sensor['estado'] else 'Inactivo'}"),
            ])
        )

    async def fetch_and_create_card(machine_id):
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"http://localhost:8000/maquinas/{machine_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return ft.Card(
                        content=ft.Column(
                            horizontal_alignment="stretch",
                            controls=[
                                ft.Card(content=ft.Container(ft.Text('Machine Details', weight="bold"), padding=8)),
                                ft.Container(ft.Text(f"{data['nombre']}", weight="bold"), padding=8),
                                *(sensor_card(sensor) for sensor in data['sensores']),
                            ]
                        )
                    )
                else:
                    return ft.Text(f"Error fetching data for machine {machine_id}")

    while True:
        tasks = [fetch_and_create_card(machine_id) for machine_id in machines]
        cards = await asyncio.gather(*tasks)
        page.update(ft.Row(controls=cards, expand=True))
        await asyncio.sleep(update_interval)
