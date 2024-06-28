import asyncio
import flet as ft
import datetime
import aiohttp
import traceback
import plotly.graph_objects as go
from flet.plotly_chart import PlotlyChart


class SensorDataViewer(ft.Container):
    def __init__(self, access_token, machine_selector):
        super().__init__()
        self.access_token = access_token
        self.machine_selector = machine_selector
        self.selected_machine = None
        self.sensor_name = ""
        self.sensor_type = ""
        self.start_date = None
        self.end_date = None

        self.machine_selector = ft.Dropdown(
            label="Seleccionar máquina",
            options=[
                ft.dropdown.Option(text='Estación 1', key='1'),
                ft.dropdown.Option(text="Estación 2", key='2'),
            ],
            width=200,
            on_change=self.on_machine_selected,
        )

        self.sensor_name_input = ft.TextField(
            label="Nombre del sensor", 
            on_change=self.on_filter_change, 
            width=200
        )
        self.sensor_type_input = ft.TextField(
            label="Tipo de sensor", 
            on_change=self.on_filter_change, 
            width=200
        )

        self.start_date_picker = ft.DatePicker(
            on_change=self.on_date_change,
            first_date=datetime.date(2023, 1, 1),
            last_date=datetime.date(2025, 12, 31),
        )
        self.end_date_picker = ft.DatePicker(
            on_change=self.on_date_change,
            first_date=datetime.date(2023, 1, 1),
            last_date=datetime.date(2025, 12, 31),
        )

        self.graph_view = ft.Container(
            bgcolor=ft.colors.BACKGROUND,
            padding=20,
            border_radius=10,
            content=ft.Column([], scroll=ft.ScrollMode.AUTO),
            expand=True
        )
        self.error_text = ft.Text("", color=ft.colors.RED, visible=False, text_align=ft.TextAlign.CENTER)
        self.fetch_data_button = ft.ElevatedButton("Obtener datos", on_click=self.manual_fetch_data)
        self.trend_analysis_button = ft.ElevatedButton("Análisis de tendencias", on_click=self.fetch_trend_analysis)
        self.selected_start_date_text = ft.Text("No se ha seleccionado la fecha de inicio")
        self.selected_end_date_text = ft.Text("No se ha seleccionado la fecha de fin")
        self.s_date_button = ft.ElevatedButton("Seleccionar fecha de inicio", on_click=lambda _: self.start_date_picker.pick_date())
        self.e_date_button = ft.ElevatedButton("Seleccionar fecha de fin", on_click=lambda _: self.end_date_picker.pick_date())
        self.loading = ft.ProgressBar(visible=False, width=400, color="amber", bgcolor="#eeeeee")
        
        self.content = ft.Column([
            ft.Row([self.machine_selector, self.sensor_name_input, self.sensor_type_input], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.s_date_button, self.e_date_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.start_date_picker, self.end_date_picker], alignment=ft.MainAxisAlignment.CENTER),
            self.selected_start_date_text,
            self.selected_end_date_text,
            self.error_text,
            ft.Row([self.fetch_data_button, self.trend_analysis_button], alignment=ft.MainAxisAlignment.CENTER),
            self.loading,
            self.graph_view
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        self.padding = 20
        self.expand = True
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
    def fetch_trend_analysis(self, e):
        if not self.selected_machine or not self.sensor_name:
            self.error_text.value = "Por favor, seleccione una máquina y un sensor."
            self.error_text.visible = True
            self.update()
            return

        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://localhost/api/analisis-tendencias/{self.selected_machine}/{self.sensor_name}"
        if self.start_date and self.end_date:
            url += f"?fecha_inicio={self.start_date}&fecha_fin={self.end_date}"
        
        asyncio.run(self.fetch_and_display_trend_analysis(headers, url))

    async def fetch_and_display_trend_analysis(self, headers, url):
        self.loading.visible = True
        self.update()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.display_trend_analysis(data)
                    else:
                        self.error_text.value = f"Error HTTP: {response.status}"
                        self.error_text.visible = True
        except Exception as e:
            print(traceback.format_exc())
            self.error_text.value = f"Error al obtener análisis de tendencias: {str(e)}"
            self.error_text.visible = True
        finally:
            self.loading.visible = False
            self.update()

    async def fetch_and_display_data(self, headers, url):
        self.loading.visible = True
        self.update()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.display_interactive_chart(data)
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

    def display_interactive_chart(self, data):
        if not data:
            self.error_text.value = "No hay datos disponibles para mostrar."
            self.error_text.visible = True
            self.update()
            return

        fig = go.Figure()

        for sensor in data:
            x = [datetime.fromisoformat(point['fecha_hora']) for point in sensor['datos']]
            y = [point['valor'] for point in sensor['datos']]
            
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                name=f"{sensor['nombre_sensor']} ({sensor['tipo_sensor']})"
            ))

        fig.update_layout(
            title="Datos históricos de sensores",
            xaxis_title="Fecha y Hora",
            yaxis_title="Valor",
            legend_title="Sensores",
            height=600
        )

        chart = PlotlyChart(fig, expand=True)
        self.graph_view.content.controls = [chart]
        self.graph_view.update()