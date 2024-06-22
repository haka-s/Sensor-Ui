import asyncio
import flet as ft
import datetime
import aiohttp
import traceback
import matplotlib.pyplot as plt
import numpy as np
from flet.matplotlib_chart import MatplotlibChart
import dateutil.parser
import matplotlib
matplotlib.use("svg")

predefined_sensor_types = [
    {"tipo": "boolean", "unidad": "estado"},
    {"tipo": "distancia", "unidad": "metros"},
    {"tipo": "velocidad", "unidad": "metros/segundo"},
    {"tipo": "energia", "unidad": "kWh"},
    {"tipo": "presion", "unidad": "pascal"},
    {"tipo": "volumen", "unidad": "litros"},
    {"tipo": "temperatura", "unidad": "grados Celsius"}
]

class SensorDataViewer(ft.Column):
    def __init__(self, access_token):
        super().__init__()
        self.access_token = access_token
        self.selected_machine = None
        self.sensor_name = ""
        self.sensor_type = ""
        self.start_date = None
        self.end_date = None

        # Crear componentes de UI
        self.machine_selector = ft.Dropdown(
            label="Seleccionar máquina",
            options=[
                ft.dropdown.Option(text='Estación 1', key='1'),
                ft.dropdown.Option(text="Estación 2", key='2'),
            ],
            border_color=ft.colors.BLUE_GREY_100,
            on_change=self.on_machine_selected,
        )

        self.sensor_name_input = ft.TextField(
            label="Nombre del sensor", 
            on_change=self.on_filter_change, 
            border_color=ft.colors.BLUE_GREY_100
        )
        self.sensor_type_input = ft.TextField(
            label="Tipo de sensor", 
            on_change=self.on_filter_change, 
            border_color=ft.colors.BLUE_GREY_100
        )

        self.start_date_picker = ft.DatePicker(
            field_label_text="Fecha de inicio", 
            on_change=self.on_date_change,
        )
        self.end_date_picker = ft.DatePicker(
            field_label_text="Fecha de fin", 
            on_change=self.on_date_change,
        )

        self.graph_view = ft.Container(
            bgcolor=ft.colors.GREY_100,
            padding=20,
            border_radius=10,
        )
        self.error_text = ft.Text(
            "", 
            color="red",  
            visible=False,  
            text_align=ft.TextAlign.CENTER
        )
        self.fetch_data_button = ft.ElevatedButton(
            "Obtener datos", 
            on_click=self.manual_fetch_data
        )
        self.selected_start_date_text = ft.Text("No se ha seleccionado la fecha de inicio")
        self.selected_end_date_text = ft.Text("No se ha seleccionado la fecha de fin")
        self.s_date_button = ft.ElevatedButton("Seleccionar fecha de inicio", on_click=lambda _: self.start_date_picker.pick_date())
        self.e_date_button = ft.ElevatedButton("Seleccionar fecha de fin", on_click=lambda _: self.end_date_picker.pick_date())
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
            self.fetch_data_button,
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
            self.selected_start_date_text.value = f"Fecha de inicio seleccionada: {self.start_date}"
        elif e.control == self.end_date_picker:
            self.end_date = date_str
            self.selected_end_date_text.value = f"Fecha de fin seleccionada: {self.end_date}"
        self.update()

    def manual_fetch_data(self, e):
        self.selected_machine = 3
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = (f"https://localhost/api/maquinas/{self.selected_machine}/sensores/historial"
               f"?nombre_sensor={self.sensor_name}&tipo_sensor={self.sensor_type}"
               f"&fecha_inicio={self.start_date}&fecha_fin={self.end_date}")
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
                        self.error_text.value = f"Error HTTP: {response.status}"
                        self.error_text.visible = True
        except Exception as e:
            print(traceback.format_exc())
            self.error_text.value = f"Error al obtener datos: {str(e)}"
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
        if not data:
            self.error_text.value = "No data available or error fetching data."
            self.error_text.visible = True
            self.update()
            return

        charts = []
        # Loop through each sensor type defined in predefined_sensor_types
        for sensor_info in predefined_sensor_types:
            sensor_type_data = [sensor for sensor in data if sensor['tipo_sensor'] == sensor_info['tipo']]
            sample_rate = 10  # Adjust sample rate as needed
            sampled_data = sensor_type_data[::sample_rate]

            if sampled_data:
                x_values = [dateutil.parser.parse(sensor['fecha_hora']) for sensor in sampled_data]
                y_values = [float(sensor['valor']) for sensor in sampled_data]

                # Initialize the chart based on the type of sensor
                fig, ax = plt.subplots()
                if sensor_info['tipo'] == "boolean":
                    # Example: Pie chart for boolean data, assuming boolean values are 0 and 1
                    true_count = sum(y_values)
                    false_count = len(y_values) - true_count
                    ax.pie([true_count, false_count], labels=['True', 'False'], autopct='%1.1f%%')
                    ax.set_title(f"{sensor_info['tipo']} Distribution")
                elif sensor_info['tipo'] == "energia":
                    # Line chart for energia data
                    ax.plot(x_values, y_values, label=sensor_info['tipo'])
                    ax.set_title(f"{sensor_info['tipo']} over Time")
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Energy (kWh)")
                else:
                    # Scatter plot for other types as a default case
                    ax.scatter(x_values, y_values, label=sensor_info['tipo'])
                    ax.set_title(f"{sensor_info['tipo']} Measurement")
                    ax.set_xlabel("Time")
                    ax.set_ylabel(sensor_info['unidad'])

                ax.legend()
                ax.grid(True)
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()

                charts.append(MatplotlibChart(fig, expand=True))

        if charts:
            print(f"Generated {len(charts)} charts.")
            self.graph_view.content.append(ft.Row(controls=[chart for chart in charts], alignment=ft.MainAxisAlignment.SPACE_AROUND, expand=True))  # Directly set charts in the graph_view
            #self.graph_view.scroll = ft.ScrollMode.ALWAYS
            self.graph_view.update()  # Ensure graph_view is updated

            self.error_text.visible = False
        else:
            self.error_text.value = "No supported sensor types found in data."
            self.error_text.visible = True

        self.update()