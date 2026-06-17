from src.metadata_providers.metadata_resolver import validate_link_get_metadata
from src.youtube.youtube_music_search_main import get_youtube_music_candidates
from src.youtube.best_match_downloader import download_audio


def main(spotify_link):
    result = validate_link_get_metadata(spotify_link)

    if not result["ok"]:
        print(result["error"])
        return

    metadata = result["metadata"]

    top_5_results = get_youtube_music_candidates(metadata)

    print("Track Found: ")
    print("Title:      ", metadata["title"])
    print("Artist(s):  ", ", ".join(metadata["artists"]))
    print("Album:      ", metadata["album"])
    print("Spotify ID: ", metadata["spotify_id"])
    print("Top 5 YouTube Music Candidates: ")

    for index, candidate in enumerate(top_5_results, start=1):
        print(f"\n{index}. {candidate['title']}")
        print("  ", candidate["url"])

    if not top_5_results:
        print("No YouTube Music candidates found")
        return

    best_candidate = top_5_results[0]
    downloaded_path = download_audio(best_candidate, metadata)
    print(f"Downloaded to: {downloaded_path}")


if __name__ == "__main__":
    user_text = input("Paste Spotify link: ")
    main(user_text)
