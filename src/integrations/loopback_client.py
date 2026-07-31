import requests
from time import monotonic, sleep
from src.integrations.loopback_api import HOST, PORT


def forward_secondary_launch(spotify_uri, retry_seconds=3.0) -> bool:
    deadline = monotonic() + retry_seconds
    base_url = f"http://{HOST}:{str(PORT)}"

    while True:
        try:
            if spotify_uri is None:
                response = requests.post(base_url + "/v1/window/show", timeout=0.5)
            else:
                response = requests.post(base_url + "/v1/downloads", json={"uri": spotify_uri}, timeout=0.5)

            if response.status_code == 202:
                return True
            return False

        except requests.RequestException:
            if monotonic() >= deadline:
                return False
            sleep(0.1)
