Front End del Sistema de Monitoreo
----------------------------------

### Interfaz de Usuario (UI)

El front end se desarrolla usando Python Flet, proporcionando una interfaz gráfica de usuario (GUI) que es accesible desde navegadores web y otros dispositivos compatibles con Python.

#### Dashboard

-   Visualización de Datos: Indicadores clave de rendimiento (KPIs) como temperatura, velocidad de soldadura, y consumo de energía se muestran en el dashboard principal.
-   Gráficos en Tiempo Real: Integración de Plotly para la visualización de datos dinámicos y actualizaciones en tiempo real.

#### Logs de Eventos

-   Registros Históricos: Sección dedicada para visualizar los registros históricos de eventos y operaciones de la máquina.

#### Control de Acceso

-   Autenticación: Interfaces para iniciar y cerrar sesión, con gestión de usuarios que permite diferentes niveles de acceso y control.

### Funcionalidad

-   Monitoreo en Tiempo Real: Recepción continua de datos del backend, utilizando técnicas como WebSockets para mantener la UI actualizada.
-   Alertas y Notificaciones: Funcionalidad para configurar alertas basadas en umbrales predefinidos que, al excederse, notifican al usuario o al equipo técnico.
-   Control de la Máquina: Capacidades para interactuar con la máquina directamente desde la interfaz, como pausar o ajustar parámetros operativos.

### Tecnologías Utilizadas

-   Flet: Para la creación de interfaces de usuario que funcionan tanto en navegadores web como en aplicaciones de escritorio.
-   Plotly: Para gráficos avanzados y visualizaciones de datos.

### Responsividad

-   Diseño Adaptable: Asegurando que la aplicación sea usable en diferentes dispositivos ajustando la interfaz automáticamente según el tamaño del dispositivo.

### Seguridad

-   Comunicación Segura: Uso de técnicas seguras para la comunicación entre el cliente y el servidor.
-   Validación y Manejo de Errores: Validaciones robustas tanto en el cliente como en el servidor para prevenir errores y posibles vulnerabilidades de seguridad.