import spotify_scraper as scraper
from src.spotify_link_cleaner import detect_input_type

def scrape_spotify_metadata(cleaned_link):

    if cleaned_link is None:
        return None

    link_type = detect_input_type(cleaned_link)

    try:
        with scraper.SpotifyClient() as client:
            if link_type == "track":
                track = client.get_track(cleaned_link)
            elif link_type == "playlist":
                track = client.get_playlist(cleaned_link)
            elif link_type == "album":
                track = client.get_album(cleaned_link)
            else:
                track = None

    except scraper.SpotifyScraperError:
        return None

    return track
