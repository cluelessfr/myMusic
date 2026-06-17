from src.gui.download_workflow import download_song_from_spotify_link


def main(spotify_link):
    result = download_song_from_spotify_link(spotify_link)

    if not result["ok"]:
        print(result["error"])
        return

    metadata = result["metadata"]

    print("Track Found: ")
    print("Title:      ", metadata["title"])
    print("Artist(s):  ", ", ".join(metadata["artists"]))
    print("Album:      ", metadata["album"])
    print("Spotify ID: ", metadata["spotify_id"])
    print(f"Downloaded To: {result['downloaded_path']}")


if __name__ == "__main__":
    user_text = input("Paste Spotify link: ")
    main(user_text)
