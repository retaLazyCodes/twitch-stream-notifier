import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QListWidget, QListWidgetItem, QLabel,
    QTextEdit, QGroupBox, QGridLayout, QMessageBox, QSpinBox,
    QCheckBox, QSplitter, QFrame
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap

from twitch_client import TwitchClient
from notifications import Notifier
from scheduler import TaskScheduler


class TwitchMonitorThread(QThread):
    """Hilo separado para monitorear los canales de Twitch."""
    
    channel_status_changed = pyqtSignal(str, str, bool)  # canal, estado, en_vivo
    log_message = pyqtSignal(str)
    
    def __init__(self, twitch_client, channels, interval_minutes):
        super().__init__()
        self.twitch_client = twitch_client
        self.channels = channels
        self.interval_minutes = interval_minutes
        self.running = False
        self.channels_state = {}
        self.channels_user_ids = {}
        
        # Init channel states
        for channel in channels:
            user_id = self.twitch_client.get_user_id(channel)
            if user_id:
                self.channels_user_ids[channel] = user_id
                self.channels_state[channel] = False
                self.log_message.emit(f"Canal '{channel}' configurado (ID: {user_id})")
            else:
                self.log_message.emit(f"Error: No se pudo obtener ID del canal '{channel}'")
    
    def run(self):
        """Ejecutar el monitoreo en bucle."""
        self.running = True
        while self.running:
            self.check_channels()
            self.sleep(self.interval_minutes * 60)
    
    def stop(self):
        """Detener el monitoreo."""
        self.running = False
    
    def check_channels(self):
        """Verificar el estado de todos los canales."""
        if not self.channels_user_ids:
            return
            
        for channel, user_id in self.channels_user_ids.items():
            try:
                is_live_now = self.twitch_client.is_channel_live(user_id)
                was_live_before = self.channels_state.get(channel, False)
                
                if is_live_now != was_live_before:
                    self.channels_state[channel] = is_live_now
                    status = "EN VIVO" if is_live_now else "OFFLINE"
                    self.channel_status_changed.emit(channel, status, is_live_now)
                    
                    if is_live_now:
                        self.log_message.emit(f"¡{channel} acaba de empezar a transmitir!")
                    else:
                        self.log_message.emit(f"{channel} ya no está en vivo.")
                        
            except Exception as e:
                self.log_message.emit(f"Error verificando {channel}: {str(e)}")
    
    def add_channel(self, channel):
        """Agregar un nuevo canal al monitoreo."""
        if channel in self.channels_user_ids:
            return False
            
        user_id = self.twitch_client.get_user_id(channel)
        if user_id:
            self.channels_user_ids[channel] = user_id
            self.channels_state[channel] = False
            self.channels.append(channel)
            self.log_message.emit(f"Canal '{channel}' agregado correctamente")
            return True
        else:
            self.log_message.emit(f"Error: No se pudo obtener ID del canal '{channel}'")
            return False
    
    def remove_channel(self, channel):
        """Remover un canal del monitoreo."""
        if channel in self.channels_user_ids:
            del self.channels_user_ids[channel]
            del self.channels_state[channel]
            self.channels.remove(channel)
            self.log_message.emit(f"Canal '{channel}' removido")
            return True
        return False


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Twitch Stream Notifier")
        self.setGeometry(100, 100, 800, 600)
        
        # Loads environment variables
        self.load_environment()
        
        # Init components
        self.init_ui()
        self.init_twitch_client()
        self.init_monitor_thread()
        
        # Set timer to update the interface
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)  # Update every second
    
    def load_environment(self):
        """Cargar variables de entorno."""
        from dotenv import load_dotenv
        load_dotenv()
        
        self.client_id = os.getenv("CLIENT_ID")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.interval_minutes = int(os.getenv("INTERVAL_MINUTES", "5"))
        
        channels_str = os.getenv("CHANNELS_TO_CHECK", "")
        self.initial_channels = [ch.strip() for ch in channels_str.split(",") if ch.strip()]
    
    def init_ui(self):
        """Inicializar la interfaz de usuario."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for channel management
        left_panel = self.create_channels_panel()
        
        # Right panel for logs and status
        right_panel = self.create_status_panel()
        
        # Splitter to resize panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])
        
        main_layout.addWidget(splitter)
    
    def create_channels_panel(self):
        """Crear el panel izquierdo para gestión de canales."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        title = QLabel("Canales Monitoreados")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.channels_list = QListWidget()
        self.channels_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.channels_list)
        
        controls_layout = QHBoxLayout()
        
        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("Nombre del canal")
        controls_layout.addWidget(self.channel_input)
        
        add_btn = QPushButton("Agregar")
        add_btn.clicked.connect(self.add_channel)
        controls_layout.addWidget(add_btn)
        
        layout.addLayout(controls_layout)
        
        remove_btn = QPushButton("Remover Canal")
        remove_btn.clicked.connect(self.remove_selected_channel)
        layout.addWidget(remove_btn)
        
        # Interval settings
        interval_group = QGroupBox("Configuración")
        interval_layout = QGridLayout(interval_group)
        
        interval_layout.addWidget(QLabel("Intervalo (minutos):"), 0, 0)
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 60)
        self.interval_spinbox.setValue(self.interval_minutes)
        self.interval_spinbox.valueChanged.connect(self.change_interval)
        interval_layout.addWidget(self.interval_spinbox, 0, 1)
        
        layout.addWidget(interval_group)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.start_stop_btn = QPushButton("Iniciar Monitoreo")
        self.start_stop_btn.clicked.connect(self.toggle_monitoring)
        buttons_layout.addWidget(self.start_stop_btn)
        
        layout.addLayout(buttons_layout)
        
        return panel
    
    def create_status_panel(self):
        """Crear el panel derecho para logs y estado."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        title = QLabel("Estado y Logs")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Monospace", 10))
        layout.addWidget(self.log_area)
        
        clear_btn = QPushButton("Limpiar Logs")
        clear_btn.clicked.connect(self.clear_logs)
        layout.addWidget(clear_btn)
        
        return panel
    
    def init_twitch_client(self):
        """Inicializar el cliente de Twitch."""
        if not self.client_id or not self.access_token:
            QMessageBox.warning(
                self, 
                "Error de Configuración",
                "CLIENT_ID o ACCESS_TOKEN no están configurados en el archivo .env"
            )
            return
        
        try:
            self.twitch_client = TwitchClient(self.client_id, self.access_token)
            self.log_message("Cliente de Twitch inicializado correctamente")
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error",
                f"No se pudo inicializar el cliente de Twitch: {str(e)}"
            )
    
    def init_monitor_thread(self):
        """Inicializar el hilo de monitoreo."""
        self.monitor_thread = TwitchMonitorThread(
            self.twitch_client, 
            self.initial_channels.copy(), 
            self.interval_minutes
        )
        
        # Conect signals
        self.monitor_thread.channel_status_changed.connect(self.on_channel_status_changed)
        self.monitor_thread.log_message.connect(self.log_message)
        
        # Load initial channels into the list
        for channel in self.initial_channels:
            self.add_channel_to_list(channel)
    
    def add_channel(self):
        """Agregar un canal desde la interfaz."""
        channel = self.channel_input.text().strip()
        if not channel:
            return
        
        if self.monitor_thread.add_channel(channel):
            self.add_channel_to_list(channel)
            self.channel_input.clear()
        else:
            QMessageBox.warning(self, "Error", f"No se pudo agregar el canal '{channel}'")
    
    def add_channel_to_list(self, channel):
        """Agregar un canal a la lista visual."""
        item = QListWidgetItem(channel)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Unchecked)
        self.channels_list.addItem(item)
    
    def remove_selected_channel(self):
        """Remover el canal seleccionado."""
        current_item = self.channels_list.currentItem()
        if not current_item:
            return
        
        channel = current_item.text()
        if self.monitor_thread.remove_channel(channel):
            self.channels_list.takeItem(self.channels_list.row(current_item))
    
    def toggle_monitoring(self):
        """Alternar entre iniciar y detener el monitoreo."""
        if self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            self.start_stop_btn.setText("Iniciar Monitoreo")
            self.log_message("Monitoreo detenido")
        else:
            self.monitor_thread.start()
            self.start_stop_btn.setText("Detener Monitoreo")
            self.log_message("Monitoreo iniciado")
    
    def change_interval(self, value):
        """Cambiar el intervalo de monitoreo."""
        self.interval_minutes = value
        if self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            self.monitor_thread.interval_minutes = value
            self.monitor_thread.start()
        self.log_message(f"Intervalo cambiado a {value} minutos")
    
    def on_channel_status_changed(self, channel, status, is_live):
        """Manejar cambios de estado de canales."""
        # Update the visual state in the list
        for i in range(self.channels_list.count()):
            item = self.channels_list.item(i)
            if item.text() == channel:
                if is_live:
                    item.setCheckState(Qt.CheckState.Checked)
                    item.setBackground(Qt.GlobalColor.green)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)
                    item.setBackground(Qt.GlobalColor.white)
                break
        
        # Send notification if live
        if is_live:
            try:
                script_dir = os.path.dirname(os.path.dirname(__file__))
                assets_dir = os.path.join(script_dir, "..", "assets")
                icon_path = os.path.join(assets_dir, "twitch.png")
                sound_path = os.path.join(assets_dir, "alert.wav")
                
                notifier = Notifier(icon_path, sound_path)
                notifier.notify_live(channel)
            except Exception as e:
                self.log_message(f"Error enviando notificación: {str(e)}")
    
    def log_message(self, message):
        """Agregar mensaje al área de logs."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
        
        # Auto-scroll at the end
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_logs(self):
        """Limpiar el área de logs."""
        self.log_area.clear()
    
    def update_ui(self):
        """Actualizar la interfaz de usuario."""
        pass
    
    def closeEvent(self, event):
        """Manejar el cierre de la ventana."""
        if hasattr(self, 'monitor_thread') and self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        event.accept()


def main():
    """Función principal para ejecutar la aplicación."""
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
