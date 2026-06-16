from src.metadata_resolver import validate_link_get_metadata


def main(spotify_link):
    result = validate_link_get_metadata(spotify_link)

    if not result["ok"]:
        print(result["error"])
        return

    metadata = result["metadata"]

    print("Track Found: ")
    print("Title:      ", metadata["title"])
    print("Artist(s):  ", ", ".join(metadata["artists"]))
    print("Album:      ", metadata["album"])
    print("Spotify ID: ", metadata["spotify_id"])


if __name__ == "__main__":
    user_text = input("Paste Spotify link: ")
    main(user_text)
