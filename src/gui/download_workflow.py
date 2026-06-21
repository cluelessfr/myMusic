from src.metadata_providers.metadata_resolver import validate_link_get_metadata
from src.youtube.youtube_music_search_main import get_youtube_music_candidates
from src.youtube.best_match_downloader import download_audio
from src.audio.metadata_tagger import add_metadata


def download_song_from_spotify_link(spotify_link, output_folder=None, progress_callback=None):
    if progress_callback:
        progress_callback("Fetching Metadata...", 0)
    result = validate_link_get_metadata(spotify_link)

    if not result["ok"]:
        return result

    metadata = result["metadata"]

    if progress_callback:
        progress_callback("Searching for Candidates...", 0.25)
    top_5_results = get_youtube_music_candidates(metadata)

    if not top_5_results:
        return {
            "ok": False,
            "status": "no_youtube_results",
            "error": "No YouTube Music candidates found",
            "metadata": metadata,
            "downloaded_path": None,
        }

    best_candidate = top_5_results[0]

    if progress_callback:
        progress_callback("Downloading Audio...", 0.5)
    downloaded_path = download_audio(best_candidate, metadata, output_folder)

    if progress_callback:
        progress_callback("Adding Metadata...", 0.75)
    add_metadata(downloaded_path, metadata)

    if progress_callback:
        progress_callback("Done", 1)

    return {
        "ok": True,
        "status": "downloaded",
        "error": None,
        "metadata": metadata,
        "candidate": best_candidate,
        "downloaded_path": downloaded_path,
    }

def preview_metadata(link):
    result = validate_link_get_metadata(link)

    if not result["ok"]:
        return {
            "ok": result["ok"],
            "error": result["error"],
            "title": None,
            "artists": None,
            "album": None,
            "artwork_url": None,
        }

    title = result["metadata"]["title"]
    artists = result["metadata"]["artists"]
    album = result["metadata"]["album"]
    artwork_url = result["metadata"]["artwork_url"]

    return {
        "ok": result["ok"],
        "error": result["error"],
        "title": title,
        "artists": artists,
        "album": album,
        "artwork_url": artwork_url,
    }
