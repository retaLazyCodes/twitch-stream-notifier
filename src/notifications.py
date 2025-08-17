import os
from notifypy import Notify


class Notifier:
    def __init__(self, icon_path, sound_path):
        self.icon_path = icon_path
        self.sound_path = sound_path

    def notify_live(self, channel_name):
        """Envía una notificación de que un canal está en vivo."""
        notification = Notify()
        notification.title = "Twitch"
        notification.message = f"¡{channel_name} está en vivo!"
        notification.application_name = "Twitch Stream Notifier"

        if os.path.exists(self.icon_path):
            notification.icon = self.icon_path
        
        if os.path.exists(self.sound_path):
            notification.audio = self.sound_path

        notification.send()
