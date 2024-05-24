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
            label="Station",
            options=[
                ft.dropdown.Option(text='estacion 2',key='1'),
                ft.dropdown.Option(text= "Station 2",key='2'),
            ],
            border_color=ft.colors.BLUE_GREY_100,
            on_change=self.on_machine_selected,
        )

        self.sensor_name_input = ft.TextField(
            label="Sensor Name", 
            on_change=self.on_filter_change, 
            border_color=ft.colors.BLUE_GREY_100
        )
        self.sensor_type_input = ft.TextField(
            label="Sensor Type", 
            on_change=self.on_filter_change, 
            border_color=ft.colors.BLUE_GREY_100
        )

        self.start_date_picker = ft.DatePicker(
            field_label_text="Start Date", 
            on_change=self.on_date_change,
        )
        self.end_date_picker = ft.DatePicker(
            field_label_text="End Date", 
            on_change=self.on_date_change,
        )

        self.graph_view = ft.Container(
            bgcolor=ft.colors.WHITE,
            padding=20,
            border_radius=10,  # Rounded corners for a softer look
        )
        self.error_text = ft.Text(
            "", 
            color="red",  
            visible=False,  
            text_align=ft.TextAlign.CENTER
        )
        self.s_date_button = ft.ElevatedButton("Select Start Date", on_click=lambda _: self.start_date_picker.pick_date())
        self.e_date_button = ft.ElevatedButton("Select End Date", on_click=lambda _: self.end_date_picker.pick_date())
        #self.graph_view = ft.Container(bgcolor=ft.colors.WHITE, padding=10)
        # UI Layout with improved arrangement and spacing
        self.controls = [
            ft.Row(
                controls=[
                    ft.Column(controls=[self.machine_selector], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column(controls=[self.sensor_name_input], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column(controls=[self.sensor_type_input], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            ft.Row(
                controls=[
                    ft.Column(controls=[self.start_date_picker], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column(controls=[self.end_date_picker], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column(controls=[self.s_date_button], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column(controls=[self.e_date_button], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
  # Add background color and padding to the graph area

                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            self.error_text,  # Error message area
            ft.Divider(),  # Visual separation
            self.graph_view,
        ]
    def on_machine_selected(self, e):
        self.selected_machine = e.control.key
        self.page.on_connect = self.fetch_and_display_data  # Trigger data fetch

    def on_filter_change(self, e):
        setattr(self, e.control.tag, e.control.value)
        self.page.on_connect = self.fetch_and_display_data 

    def on_date_change(self, e):
        if e.control == self.start_date_picker:
            self.start_date = e.control.value.strftime('%Y-%m-%d')
            self.start_date = f'{self.start_date} 00:00:00'
        elif e.control == self.end_date_picker:
            self.end_date = e.control.value.strftime('%Y-%m-%d')
            self.end_date = f'{self.end_date} 23:59:59'
        self.page.on_connect = self.fetch_and_display_data  # Trigger data fetch

    async def fetch_and_display_data(self):
        if not self.selected_machine:
            self.update_graph(None)
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
                        print(response)
                        self.update_graph(data)
                    else:
                        print(response)
                        self.update_graph(None)  # Clear the graph if error or no data
            except aiohttp.ClientError as e:
                self.update_graph(None)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Network error: {str(e)}"))  # Show error message
                self.page.snack_bar.open = True

            except Exception as e:
                self.update_graph(None)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error fetching data: {str(e)}"))  # Show error message
                self.page.snack_bar.open = True

    def update_graph(self, data):
        if not data:
            self.error_text.value = "No data available or error fetching data."
            self.error_text.visible = True
        else:
            self.graph_view.controls = [
                ft.Text(f"{sensor['sensor_name']} - {sensor['value']} on {sensor['datetime']}", wrap=None)
                for sensor in data
            ]

        self.update()

