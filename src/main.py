import os
import platform
from dotenv import load_dotenv

from .twitch_client import TwitchClient
from .notifications import Notifier
from .scheduler import TaskScheduler

# loads environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
CHANNEL_TO_CHECK = os.getenv("CHANNEL_TO_CHECK")
INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", default=5))

SCRIPT_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets")
ICON_EXTENSION = "png" if platform.system() != "Windows" else "ico"

ICON_PATH = os.path.join(ASSETS_DIR, f"twitch.{ICON_EXTENSION}") 
SOUND_PATH = os.path.join(ASSETS_DIR, "alert.wav")

twitch_client = TwitchClient(CLIENT_ID, ACCESS_TOKEN)
notifier = Notifier(ICON_PATH, SOUND_PATH)

# save the previous state of the channel
is_live_last_check = None
channel_user_id = twitch_client.get_user_id(CHANNEL_TO_CHECK)


def check_channel_and_notify():
    """Función que se ejecutará en el programador de tareas."""
    global is_live_last_check

    if not channel_user_id:
        print("Error: No se pudo obtener el ID del canal. Deteniendo...")
        return

    is_live_now = twitch_client.is_channel_live(channel_user_id)

    if is_live_now and not is_live_last_check:
        print(f"¡{CHANNEL_TO_CHECK} acaba de empezar a transmitir!")
        notifier.notify_live(CHANNEL_TO_CHECK)

    elif not is_live_now and is_live_last_check:
        print(f"{CHANNEL_TO_CHECK} ya no está en vivo.")

    elif is_live_now:
        print(f"{CHANNEL_TO_CHECK} sigue en vivo.")

    else:
        print(f"{CHANNEL_TO_CHECK} sigue offline.")

    is_live_last_check = is_live_now


def main():
    """Punto de entrada de la aplicación."""
    print("Iniciando notificador...")
    scheduler = TaskScheduler(interval_minutes=INTERVAL_MINUTES)
    scheduler.schedule_task(check_channel_and_notify)
    print("Monitoreo iniciado. Presiona Ctrl+C para salir.")
    scheduler.run_pending_tasks()


if __name__ == "__main__":
    main()