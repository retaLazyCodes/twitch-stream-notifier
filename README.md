# Twitch Stream Notifier

Una aplicación ligera y multiplataforma que te avisa cuando los streamers que sigues en Twitch empiezan a transmitir en vivo.

---

## 📝 Descripción

Esta app permite:

- Seguir una lista de streamers de Twitch.
- Recibir notificaciones en el escritorio cuando alguno empieza un stream.
- Configurar la frecuencia de chequeo de streams.
- Interfaz gráfica con PyQt6.

Ideal para quienes quieren estar al tanto de sus canales favoritos sin tener que abrir Twitch constantemente.

## 🚀 Características

### Modo Consola
- Monitoreo automático de múltiples canales
- Notificaciones de escritorio
- Configuración mediante variables de entorno

### Modo GUI (Nuevo)
- Interfaz gráfica moderna y responsive
- Gestión visual de canales
- Logs en tiempo real
- Control completo del monitoreo
- Diseño de dos paneles para mejor organización

## 🛠️ Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/retaLazyCodes/twitch-stream-notifier.git
cd twitch-stream-notifier
```

2. Instala las dependencias:
```bash
make install
# o
poetry install
```

3. Configura las variables de entorno en `.env`:
```env
CLIENT_ID=tu_client_id_de_twitch
ACCESS_TOKEN=tu_access_token_de_twitch
CHANNELS_TO_CHECK=canal1,canal2,canal3
INTERVAL_MINUTES=5
```

## 🎯 Uso

### Modo Consola
```bash
make run
# o
poetry run python -m src.main
```

### Modo GUI
```bash
make run-gui
# o
poetry run python src/gui_main.py
```

## 📁 Estructura del Proyecto

```
twitch-notifier/
├── src/
│   ├── ui/                 # Interfaz gráfica
│   │   ├── main_window.py  # Ventana principal
│   │   ├── app_config.py   # Configuración
│   │   └── resources.qrc   # Recursos de Qt
│   ├── main.py             # Aplicación de consola
│   ├── gui_main.py         # Punto de entrada GUI
│   ├── twitch_client.py    # Cliente de Twitch
│   ├── notifications.py    # Sistema de notificaciones
│   └── scheduler.py        # Programador de tareas
├── assets/                 # Recursos (iconos, sonidos)
└── Makefile               # Comandos útiles
```

## 🔧 Comandos Disponibles

### Aplicación
- `make install` - Instalar dependencias
- `make run` - Ejecutar modo consola
- `make run-gui` - Ejecutar interfaz gráfica

### Desarrollo
- `make lint` - Verificar código
- `make format` - Formatear código
- `make help` - Mostrar todos los comandos disponibles

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.