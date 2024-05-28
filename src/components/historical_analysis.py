import asyncio
import flet as ft
import datetime
import aiohttp
import traceback
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
            bgcolor=ft.colors.GREY_100,
            padding=20,
            border_radius=10,  # Rounded corners for a softer look
        )
        self.error_text = ft.Text(
            "", 
            color="red",  
            visible=False,  
            text_align=ft.TextAlign.CENTER
        )
        self.fetch_data_button = ft.ElevatedButton(
            "Fetch Data", 
            on_click=self.manual_fetch_data
        )
        self.selected_start_date_text = ft.Text("No start date selected")
        self.selected_end_date_text = ft.Text("No end date selected")
        self.s_date_button = ft.ElevatedButton("Select Start Date", on_click=lambda _: self.start_date_picker.pick_date())
        self.e_date_button = ft.ElevatedButton("Select End Date", on_click=lambda _: self.end_date_picker.pick_date())
        #self.graph_view = ft.Container(bgcolor=ft.colors.WHITE, padding=10)
        # UI Layout with improved arrangement and spacing
        self.loading = ft.ProgressBar(visible=False, width=400, color="amber", bgcolor="#eeeeee")
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
                    ft.Column(controls=[self.s_date_button], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column(controls=[self.start_date_picker], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column(controls=[self.e_date_button], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column(controls=[self.end_date_picker], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],
            
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            self.selected_start_date_text,
            self.selected_end_date_text,
            self.error_text,
            self.fetch_data_button,# Error message area
            ft.Row(controls=[ft.Divider()]),
            self.loading,
            self.graph_view
            ]
    def on_machine_selected(self, e):
        self.selected_machine = e.control.key

    def on_filter_change(self, e):
        setattr(self, e.control.tag, e.control.value)

    def on_date_change(self, e):
        date_str = e.control.value.strftime('%Y-%m-%d %H:%M:%S')
        if e.control == self.start_date_picker:
            self.start_date = date_str
            self.selected_start_date_text.value = f"Fecha de inicio: {self.start_date}"
        elif e.control == self.end_date_picker:
            self.end_date = date_str
            self.selected_end_date_text.value = f"Fecha fin: {self.end_date}"
        self.update()

    def manual_fetch_data(self, e):
        self.selected_machine = 3
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = (f"http://localhost:8000/maquinas/{self.selected_machine}/sensores/historial"
               f"?nombre_sensor={self.sensor_name}&tipo_sensor={self.sensor_type}"
               f"&fecha_inicio={self.start_date}&fecha_fin={self.end_date}")
        #print(url)
        
        asyncio.run(self.fetch_and_display_data(headers, url))      

    async def fetch_and_display_data(self, headers, url):
        self.loading.visible = True
        self.update()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.update_graph(data)
                    else:
                        self.error_text.value = f"HTTP Error: {response.status}"
                        self.error_text.visible = True
        except Exception as e:
            print(traceback.format_exc())
            self.error_text.value = f"Error fetching data: {str(e)}"
            self.error_text.visible = True
        finally:
            self.loading.visible = False
            self.update()



    def parse_datetime(self,date_str):
        # This function attempts to parse datetime with timezone and microseconds.
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z").astimezone(datetime.timezone.utc).date()
        except ValueError:
            # Fallback for any other formats you might encounter
            return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z").astimezone(datetime.timezone.utc).date()

    def update_graph(self, data):
        if data:
            energia_data = [sensor for sensor in data if sensor['tipo_sensor'] == 'energia']
            # Sampling data to reduce the number of points
            sample_rate = 10  # Adjust sample rate as needed
            sampled_energia_data = energia_data[::sample_rate]

            if sampled_energia_data:
                # Convert date strings to datetime objects in UTC and extract the date part only
                date_vals = [self.parse_datetime(sensor['fecha_hora']) for sensor in sampled_energia_data]
                unique_dates = sorted(set(date_vals))

                # Map each unique date to its corresponding values, filling gaps with None
                date_to_value_map = {date: None for date in unique_dates}
                for sensor, date in zip(sampled_energia_data, date_vals):
                    date_to_value_map[date] = float(sensor['valor'])
                
                line_data_points = [
                    ft.LineChartDataPoint(x=i, y=date_to_value_map[date], tooltip=f"Value: {date_to_value_map[date]} on {date}")
                    for i, date in enumerate(unique_dates)
                ]

                line_chart_data = ft.LineChartData(
                    data_points=line_data_points,
                    color=ft.colors.CYAN,
                    stroke_width=2,
                    curved=True,
                    stroke_cap_round=True
                )
                
                line_chart = ft.LineChart(
                    data_series=[line_chart_data],
                    expand=True,
                    min_y=0,
                    max_y=max(date_to_value_map.values(), default=0),
                    min_x=0,
                    max_x=len(unique_dates) - 1,
                    bottom_axis=ft.ChartAxis(
                        labels=[ft.ChartAxisLabel(value=i, label=ft.Text(date.strftime("%Y-%m-%d"), size=12))
                                for i, date in enumerate(unique_dates)],
                        labels_size=24
                    ),
                    left_axis=ft.ChartAxis(
                        labels=[ft.ChartAxisLabel(value=y, label=ft.Text(f"{y}", size=12))
                                for y in range(0, int(max(date_to_value_map.values(), default=0))+1, 10)],
                        labels_size=24
                    )
                )
                
                self.graph_view.content = ft.Row(controls=[line_chart], expand=True)
                self.error_text.visible = False
            else:
                self.error_text.value = "No 'energia' type sensor data available after sampling."
                self.error_text.visible = True
        else:
            self.error_text.value = "No data available or error fetching data."
            self.error_text.visible = True

        self.update()
