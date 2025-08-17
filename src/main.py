import os
import time
from dotenv import load_dotenv
import requests
import schedule
from notifypy import Notify

# loads environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
CHANNEL_TO_CHECK = os.getenv("CHANNEL_TO_CHECK")

SCRIPT_DIR = os.path.dirname(__file__)
ICON_PATH = os.path.join(SCRIPT_DIR, "..", "assets", "twitch.png")

# Variables to save the previous state of the channel
is_live_last_check = None
channel_user_id = None


def get_user_id(username):
    """Obtiene el ID de usuario a partir del nombre de usuario."""
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Client-Id": CLIENT_ID,
        }
        url = f"https://api.twitch.tv/helix/users?login={username}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get("data")
        if data:
            return data[0]["id"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el ID de usuario: {e}")
        return None


def check_channel_status():
    """
    Verifica si el canal está en vivo y notifica si cambia de estado.
    """
    global is_live_last_check
    global channel_user_id

    # Si aún no tenemos el ID del usuario, lo obtenemos
    if not channel_user_id:
        channel_user_id = get_user_id(CHANNEL_TO_CHECK)
        if not channel_user_id:
            print(
                f"No se pudo encontrar el ID para el usuario {CHANNEL_TO_CHECK}."
                "Reintentando en 1 minuto..."
            )
            return

    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Client-Id": CLIENT_ID,
        }
        url = f"https://api.twitch.tv/helix/streams?user_id={channel_user_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json().get("data")
        is_live_now = bool(data)

        if is_live_now and not is_live_last_check:
            print(f"¡{CHANNEL_TO_CHECK} acaba de empezar a transmitir!")
            
            notification = Notify()
            notification.title = "Twitch"
            notification.message = f"{CHANNEL_TO_CHECK} está en vivo!"
            notification.application_name = "Twitch Stream Notifier"
            notification.icon = ICON_PATH
            notification.send()

        elif not is_live_now and is_live_last_check:
            print(f"{CHANNEL_TO_CHECK} ya no está en vivo.")

        elif is_live_now:
            print(f"{CHANNEL_TO_CHECK} sigue en vivo.")

        else:
            print(f"{CHANNEL_TO_CHECK} sigue offline.")

        is_live_last_check = is_live_now

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")


def main():
    """Configura y ejecuta la tarea de monitoreo."""
    print("Iniciando el notificador de Twitch...")

    # Programa la tarea para que se ejecute cada 1 minuto
    schedule.every(1).minute.do(check_channel_status)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
