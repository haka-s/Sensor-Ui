import flet as ft
from datetime import datetime
import aiohttp
class SensorDataViewer(ft.Column):
    def __init__(self, access_token):
        super().__init__()
        self.access_token = access_token
        self.selected_machine = None
        self.sensor_name = ""
        self.sensor_type = ""
        self.start_date = None
        self.end_date = None

        # Create UI components
        self.machine_selector = ft.Dropdown(
            label="Select Machine",
            on_change=self.on_machine_selected,
            options=[
                ft.dropdown.Option(text="Estacion 1", data="1"),
                ft.dropdown.Option(text="Estacion 2", data="2")
            ]
        )

        self.sensor_name_input = ft.TextField(label="Sensor Name", on_change=self.on_filter_change)
        self.sensor_type_input = ft.TextField(label="Sensor Type", on_change=self.on_filter_change)

        self.start_date_picker = ft.DatePicker(on_change=self.on_date_change)
        self.end_date_picker = ft.DatePicker(on_change=self.on_date_change)

        self.s_date_button = ft.ElevatedButton(
            text="Select Start Date",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.start_date_picker.pick_date()
        )
        self.e_date_button = ft.ElevatedButton(
            text="Select End Date",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.end_date_picker.pick_date()
        )

        self.graph_view = ft.Container()

        # Assemble the UI
        self.controls.extend([
            self.machine_selector,
            self.sensor_name_input,
            self.sensor_type_input,
            ft.Row(controls=[self.s_date_button, self.e_date_button]),
            self.graph_view
        ])

    def on_machine_selected(self, e):
        self.selected_machine = e.control.value
        self.fetch_and_display_data()

    def on_filter_change(self, e):
        setattr(self, e.control.tag, e.control.value)
        self.fetch_and_display_data()

    def on_date_change(self, e):
        setattr(self, e.control.tag, e.control.value.strftime('%Y-%m-%d'))  # Format the date as string
        self.fetch_and_display_data()

    async def fetch_and_display_data(self):
        if not self.selected_machine:
            return  # No machine selected, do nothing
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = (f"http://localhost:8000/machines/{self.selected_machine}/sensors/history"
               f"?sensor_name={self.sensor_name}&sensor_type={self.sensor_type}"
               f"&start_date={self.start_date}&end_date={self.end_date}")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.update_graph(data)
                    else:
                        self.update_graph(None)  # Clear the graph if error or no data
            except Exception as e:
                self.update_graph(None)
                print(f"An error occurred: {str(e)}")  # Consider displaying this in the UI

    def update_graph(self, data):
        if not data:
            self.graph_view.controls = [ft.Text("No data available or error fetching data.")]
        else:
            # Update your graph or data visualization here
            self.graph_view.controls = [
                ft.Text(f"{sensor['sensor_name']} - {sensor['value']} on {sensor['datetime']}", wrap=None)
                for sensor in data
            ]
        self.update()

