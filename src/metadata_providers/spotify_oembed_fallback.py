import requests


def fetch_spotify_oembed(cleaned_url):

    url = "https://open.spotify.com/oembed"

    if cleaned_url is None:
        return None

    params = {
        "url": cleaned_url
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        return response.json()
    except ValueError:
        return None
