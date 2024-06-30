import flet as ft
import datetime
import requests
from collections import Counter
import pytz
RUTA_CERTIFICADO = r"cert\fullchain.pem"

class VisualizadorDatosSensor(ft.Container):
    def __init__(self, token_acceso):
        super().__init__()
        
        self.token_acceso = token_acceso
        self.maquina_seleccionada = None
        self.sensor_seleccionado = None
        self.fecha_inicio = None
        self.fecha_fin = None
        self.todos_los_datos = []
        self.tamano_pagina = 1000

        self.selector_maquina = ft.Dropdown(
            label="Seleccionar máquina",
            options=[],
            width=200,
            on_change=self.al_seleccionar_maquina,
        )

        self.selector_sensor = ft.Dropdown(
            label="Seleccionar sensor",
            options=[],
            width=200,
            on_change=self.al_seleccionar_sensor,
            disabled=True
        )

        self.selector_fecha_inicio = ft.DatePicker(
            on_change=self.al_cambiar_fecha,
            first_date=datetime.date(2023, 1, 1),
            last_date=datetime.date(2025, 12, 31),
        )
        self.selector_fecha_fin = ft.DatePicker(
            on_change=self.al_cambiar_fecha,
            first_date=datetime.date(2023, 1, 1),
            last_date=datetime.date(2025, 12, 31),
        )

        self.contenedor_grafico = ft.Container(
            content=ft.Text("No hay datos para mostrar", color="grey"),
            alignment=ft.alignment.center,
            width=800,
            height=400,
            border=ft.border.all(1, "grey"),
        )

        self.contenedor_grafico_circular = ft.Container(
            content=ft.Text("No hay datos para mostrar", color="grey"),
            alignment=ft.alignment.center,
            width=400,
            height=400,
            border=ft.border.all(1, "grey"),
        )

        self.texto_error = ft.Text("", color=ft.colors.RED, visible=False, text_align=ft.TextAlign.CENTER)
        self.boton_obtener_datos = ft.ElevatedButton("Obtener datos", on_click=self.obtener_datos_manual)
        self.texto_fecha_inicio_seleccionada = ft.Text("No se ha seleccionado la fecha de inicio")
        self.texto_fecha_fin_seleccionada = ft.Text("No se ha seleccionado la fecha de fin")
        self.boton_fecha_inicio = ft.ElevatedButton("Seleccionar fecha de inicio", on_click=lambda _: self.selector_fecha_inicio.pick_date())
        self.boton_fecha_fin = ft.ElevatedButton("Seleccionar fecha de fin", on_click=lambda _: self.selector_fecha_fin.pick_date())
        self.barra_progreso = ft.ProgressBar(visible=False, width=400, color="amber", bgcolor="#eeeeee")

        self.content = ft.Column([
            ft.Row([self.selector_maquina, self.selector_sensor], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.boton_fecha_inicio, self.boton_fecha_fin], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.selector_fecha_inicio, self.selector_fecha_fin], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.texto_fecha_inicio_seleccionada], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.texto_fecha_fin_seleccionada], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.texto_error], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.boton_obtener_datos], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.barra_progreso], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                self.contenedor_grafico], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.contenedor_grafico_circular], alignment=ft.MainAxisAlignment.CENTER),
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        self.padding = 20
        self.expand = True
    def did_mount(self):
        self.obtener_maquinas()

    def obtener_maquinas(self):
        cabeceras = {"Authorization": f"Bearer {self.token_acceso}"}
        url = "https://localhost/api/maquinas/lista"
        try:
            respuesta = requests.get(url, headers=cabeceras, verify=RUTA_CERTIFICADO)
            if respuesta.status_code == 200:
                maquinas = respuesta.json()
                self.selector_maquina.options = [
                    ft.dropdown.Option(key=str(maquina['id']), text=maquina['nombre'])
                    for maquina in maquinas
                ]
                self.update()
            else:
                self.texto_error.value = f"Error al obtener la lista de máquinas: {respuesta.status_code}"
                self.texto_error.visible = True
                self.update()
        except Exception as e:
            self.texto_error.value = f"Error al obtener la lista de máquinas: {str(e)}"
            self.texto_error.visible = True
            self.update()

    def al_seleccionar_maquina(self, e):
        self.maquina_seleccionada = e.control.value
        self.selector_sensor.disabled = False
        self.selector_sensor.options = []
        self.sensor_seleccionado = None
        self.obtener_sensores()
        self.update()

    def obtener_sensores(self):
        if not self.maquina_seleccionada:
            return

        cabeceras = {"Authorization": f"Bearer {self.token_acceso}"}
        url = f"https://localhost/api/maquinas/{self.maquina_seleccionada}"
        try:
            respuesta = requests.get(url, headers=cabeceras, verify=RUTA_CERTIFICADO)
            if respuesta.status_code == 200:
                datos_maquina = respuesta.json()
                self.selector_sensor.options = [
                    ft.dropdown.Option(key=sensor['nombre'], text=f"{sensor['nombre']} ({sensor['tipo']})")
                    for sensor in datos_maquina['sensores']
                ]
                self.update()
            else:
                self.texto_error.value = f"Error al obtener la lista de sensores: {respuesta.status_code}"
                self.texto_error.visible = True
                self.update()
        except Exception as e:
            self.texto_error.value = f"Error al obtener la lista de sensores: {str(e)}"
            self.texto_error.visible = True
            self.update()

    def al_seleccionar_sensor(self, e):
        self.sensor_seleccionado = e.control.value

    def al_cambiar_fecha(self, e):
        fecha_str = e.control.value.strftime('%Y-%m-%d')
        if e.control == self.selector_fecha_inicio:
            self.fecha_inicio = f"{fecha_str} 00:00:00"
            self.texto_fecha_inicio_seleccionada.value = f"Fecha de inicio seleccionada: {self.fecha_inicio}"
        elif e.control == self.selector_fecha_fin:
            self.fecha_fin = f"{fecha_str} 23:59:59"
            self.texto_fecha_fin_seleccionada.value = f"Fecha de fin seleccionada: {self.fecha_fin}"
        self.update()

    def obtener_datos_manual(self, e):
        if not self.maquina_seleccionada or not self.sensor_seleccionado:
            self.texto_error.value = "Por favor, seleccione una máquina y un sensor."
            self.texto_error.visible = True
            self.update()
            return

        self.todos_los_datos = []
        self.obtener_todos_los_datos()


    def mostrar_grafico(self):
        if not self.todos_los_datos:
            self.contenedor_grafico.content = ft.Text("No hay datos disponibles para mostrar.")
            self.contenedor_grafico_circular.content = ft.Text("No hay datos disponibles para mostrar.")
            self.barra_progreso.visible = False
            self.update()
            return

        try:
            utc = pytz.UTC
            fecha_inicio = datetime.datetime.strptime(self.fecha_inicio, "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)
            fecha_fin = datetime.datetime.strptime(self.fecha_fin, "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)

            # Filtrar los datos dentro del rango de fechas seleccionado
            datos_filtrados = [
                sensor for sensor in self.todos_los_datos
                if fecha_inicio <= datetime.datetime.fromisoformat(sensor['fecha_hora']).replace(tzinfo=utc) <= fecha_fin
            ]

            if not datos_filtrados:
                self.contenedor_grafico.content = ft.Text("No hay datos en el rango de fechas seleccionado.")
                self.contenedor_grafico_circular.content = ft.Text("No hay datos en el rango de fechas seleccionado.")
                self.barra_progreso.visible = False
                self.update()
                return

            # Convertir todos los puntos a tuplas (datetime, valor)
            puntos = [
                (datetime.datetime.fromisoformat(sensor['fecha_hora']).replace(tzinfo=utc), float(sensor['valor']))
                for sensor in datos_filtrados
            ]

            puntos.sort(key=lambda p: p[0])

            estados = Counter()
            for _, valor in puntos:
                estados['Activo' if valor >= 1 else 'Inactivo'] += 1

            min_y, max_y = min(p[1] for p in puntos), max(p[1] for p in puntos)
            rango_y = max_y - min_y

            if rango_y == 0:
                rango_y = 1
                max_y += 0.5
                min_y -= 0.5

            # Determinar el rango de fechas total
            rango_fechas = (fecha_fin.date() - fecha_inicio.date()).days + 1

            # Configurar etiquetas del eje X
            num_etiquetas = min(rango_fechas, 8)
            intervalo = max(1, rango_fechas // num_etiquetas)
            etiquetas_eje_x = [fecha_inicio.date() + datetime.timedelta(days=i*intervalo) for i in range(num_etiquetas)]

            labels_styled = [
                ft.ChartAxisLabel(
                    value=i * intervalo,
                    label=ft.Container(
                        ft.Text(
                            fecha.strftime("%Y-%m-%d"),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                        ),
                        margin=ft.margin.only(top=10),
                    ),
                ) for i, fecha in enumerate(etiquetas_eje_x)
            ]

            # Configurar etiquetas del eje Y
            num_etiquetas_y = 5
            intervalo_y = rango_y / (num_etiquetas_y - 1) if rango_y > 0 else 1
            etiquetas_eje_y = [min_y + i * intervalo_y for i in range(num_etiquetas_y)]
            
            labels_y_styled = [
                ft.ChartAxisLabel(
                    value=valor,
                    label=ft.Text(
                        f"{valor:.2f}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                    ),
                ) for valor in etiquetas_eje_y
            ]

            # Normalizar los puntos para el gráfico
            x_min = min(p[0] for p in puntos)
            x_max = max(p[0] for p in puntos)
            x_range = (x_max - x_min).total_seconds()
            
            normalized_points = [
                ft.LineChartDataPoint(
                    x=(p[0] - x_min).total_seconds() / x_range * (rango_fechas - 1),
                    y=p[1]
                ) for p in puntos
            ]

            grafico = ft.LineChart(
                tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.RED),
                expand=True,
                min_y=min_y - (rango_y * 0.1),
                max_y=max_y + (rango_y * 0.1),
                min_x=0,
                max_x=rango_fechas - 1,
                left_axis=ft.ChartAxis(
                    labels_size=40,
                    title=ft.Text("Valor"),
                    labels_interval=1,
                    labels=labels_y_styled,
                ),
                bottom_axis=ft.ChartAxis(
                    labels_size=40,
                    title=ft.Text("Fecha"),
                    labels=labels_styled,
                    labels_interval=1
                ),
                data_series=[
                    ft.LineChartData(
                        data_points=normalized_points,
                        stroke_width=2,
                        color=ft.colors.BLUE,
                        curved=True,
                        stroke_cap_round=True,
                    )
                ],
                border=ft.border.all(1, ft.colors.GREY),
                horizontal_grid_lines=ft.ChartGridLines(
                    interval=1,
                    color=ft.colors.GREY_300,
                    width=1,
                ),
                vertical_grid_lines=ft.ChartGridLines(
                    interval=1,
                    color=ft.colors.GREY_300,
                    width=1,
                ),
            )

            self.contenedor_grafico.content = grafico

            # Gráfico circular
            total = sum(estados.values())
            if total > 0:
                grafico_circular = ft.PieChart(
                    sections=[
                        ft.PieChartSection(
                            value=estados['Activo'],
                            title="Activo",
                            color=ft.colors.GREEN,
                            radius=100,
                        ),
                        ft.PieChartSection(
                            value=estados['Inactivo'],
                            title="Inactivo",
                            color=ft.colors.RED,
                            radius=100,
                        ),
                    ],
                    sections_space=0,
                    center_space_radius=60,
                    expand=True,
                )

                self.contenedor_grafico_circular.content = ft.Column([
                    grafico_circular,
                    ft.Text(f"Activo: {estados['Activo'] / total:.1%}"),
                    ft.Text(f"Inactivo: {estados['Inactivo'] / total:.1%}"),
                ], alignment=ft.MainAxisAlignment.CENTER)
            else:
                self.contenedor_grafico_circular.content = ft.Text("No hay datos suficientes para el gráfico circular")

        except Exception as e:
            self.texto_error.value = f"Error al procesar datos para el gráfico: {str(e)}"
            self.texto_error.visible = True

        finally:
            self.barra_progreso.visible = False
            self.update()
    def obtener_todos_los_datos(self, pagina=1):
        self.barra_progreso.visible = True
        self.update()

        cabeceras = {"Authorization": f"Bearer {self.token_acceso}"}
        url = (f"https://localhost/api/maquinas/{self.maquina_seleccionada}/sensores/historial"
               f"?nombre_sensor={self.sensor_seleccionado}"
               f"&fecha_inicio={self.fecha_inicio}&fecha_fin={self.fecha_fin}"
               f"&page={pagina}&page_size={self.tamano_pagina}")

        try:
            respuesta = requests.get(url, headers=cabeceras, verify=RUTA_CERTIFICADO)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                self.todos_los_datos.extend(datos['data'])
                
                if len(datos['data']) == self.tamano_pagina:
                    self.obtener_todos_los_datos(pagina + 1)
                else:
                    self.mostrar_grafico()
            else:
                self.texto_error.value = f"Error HTTP: {respuesta.status_code}"
                self.texto_error.visible = True
                self.barra_progreso.visible = False
                self.update()
        except Exception as e:
            self.texto_error.value = f"Error al obtener datos: {str(e)}"
            self.texto_error.visible = True
            self.barra_progreso.visible = False
            self.update()