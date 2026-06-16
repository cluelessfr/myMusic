from src.spotify_link_cleaner import *
from src.metadata_providers.spotify_oembed_fallback import *


user_text = input("Paste Spotify link: ")

def main(spotify_link):
    input_type = detect_input_type(spotify_link)
    cleaned_url = clean_spotify_link(spotify_link)
    spotify_id = extract_spotify_id(spotify_link)

    print(input_type, cleaned_url, spotify_id)

    if cleaned_url is None:
        print("Invalid link")
        return None

    elif input_type != "track":
        print("Only track type is supported right now")
        return None

    else:
        metadata = fetch_spotify_oembed(cleaned_url)

    if metadata is not None:
        print(metadata)
        return None

    else:
        print("Failed to fetch metadata")
        return None


main(user_text)




