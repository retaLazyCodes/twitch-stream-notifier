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
CHANNELS_TO_CHECK = os.getenv("CHANNELS_TO_CHECK", "").split(",")
INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", default=5))

CHANNELS_TO_CHECK = [channel.strip() for channel in CHANNELS_TO_CHECK if channel.strip()]

SCRIPT_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets")
ICON_EXTENSION = "png" if platform.system() != "Windows" else "ico"

ICON_PATH = os.path.join(ASSETS_DIR, f"twitch.{ICON_EXTENSION}") 
SOUND_PATH = os.path.join(ASSETS_DIR, "alert.wav")

twitch_client = TwitchClient(CLIENT_ID, ACCESS_TOKEN)
notifier = Notifier(ICON_PATH, SOUND_PATH)

# saves the previous state of each channel
channels_state = {}
# saves the ID of each channel
channels_user_ids = {}

# Init channels data
for channel in CHANNELS_TO_CHECK:
    user_id = twitch_client.get_user_id(channel)
    if user_id:
        channels_user_ids[channel] = user_id
        channels_state[channel] = False  # Inicialmente offline
        print(f"Canal '{channel}' configurado correctamente (ID: {user_id})")
    else:
        print(f"Error: No se pudo obtener el ID del canal '{channel}'. Se omitirá.")


def check_channels_and_notify():
    """Función que se ejecutará en el programador de tareas."""
    global channels_state

    if not channels_user_ids:
        print("Error: No hay canales válidos configurados. Deteniendo...")
        return

    for channel, user_id in channels_user_ids.items():
        is_live_now = twitch_client.is_channel_live(user_id)
        was_live_before = channels_state.get(channel, False)

        if is_live_now and not was_live_before:
            print(f"¡{channel} acaba de empezar a transmitir!")
            notifier.notify_live(channel)
            channels_state[channel] = True

        elif not is_live_now and was_live_before:
            print(f"{channel} ya no está en vivo.")
            channels_state[channel] = False

        elif is_live_now:
            print(f"{channel} sigue en vivo.")

        else:
            print(f"{channel} sigue offline.")


def main():
    """Punto de entrada de la aplicación."""
    if not CHANNELS_TO_CHECK:
        print("Error: No se han especificado canales para monitorear.")
        print("Configura la variable de entorno CHANNELS_TO_CHECK con una lista separada por comas.")
        return
    
    if not channels_user_ids:
        print("Error: No se pudo obtener información de ningún canal. Verifica la configuración.")
        return
    
    print(f"Iniciando notificador para {len(channels_user_ids)} canal(es)...")
    scheduler = TaskScheduler(interval_minutes=INTERVAL_MINUTES)
    scheduler.schedule_task(check_channels_and_notify)
    print("Monitoreo iniciado. Presiona Ctrl+C para salir.")
    scheduler.run_pending_tasks()


if __name__ == "__main__":
    main()