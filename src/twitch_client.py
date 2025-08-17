import requests
import os


class TwitchClient:
    def __init__(self, client_id, access_token):
        self.client_id = client_id
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Client-Id": self.client_id,
        }
        self.base_url = os.getenv("TWITCH_API_URL")

    def get_user_id(self, username):
        """Obtiene el ID de usuario a partir del nombre de usuario."""
        try:
            url = f"{self.base_url}users?login={username}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json().get("data")
            if data:
                return data[0]["id"]
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error en la API de Twitch (get_user_id): {e}")
            return None

    def is_channel_live(self, user_id):
        """Verifica si un canal está en vivo usando su ID de usuario."""
        try:
            url = f"{self.base_url}streams?user_id={user_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json().get("data")
            return bool(data)
        except requests.exceptions.RequestException as e:
            print(f"Error en la API de Twitch (is_channel_live): {e}")
            return False
