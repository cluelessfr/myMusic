from src.metadata_providers.metadata_resolver import validate_link_get_metadata_track, validate_link_get_metadata_playlist, validate_link_get_metadata_album
from src.youtube.youtube_music_search_main import get_youtube_music_candidates
from src.youtube.youtube_search_main import get_youtube_candidates
from src.spotify.spotify_link_cleaner import detect_input_type
from src.youtube.best_match_downloader import download_audio
from src.youtube.candidate_ranker import score_candidates
from src.audio.metadata_tagger import add_metadata


def format_download_error(error_message):
    if error_message is None:
        return "Download failed, but no detailed error was provided."

    lower_error = error_message.lower()

    if "not a bot" in lower_error or "sign in to confirm" in lower_error:
        return "YouTube blocked this download with a bot check. This is a YouTube-side limit, not an installation problem with myMusic. Try again later or from a different network."

    return error_message


def make_download_failure(status, error, metadata, technical_error=None):
    if technical_error:
        return {
            "ok": False,
            "status": status,
            "error": error,
            "technical_error": technical_error,
            "metadata": metadata,
            "downloaded_path": None,
        }

    return {
        "ok": False,
        "status": status,
        "error": error,
        "metadata": metadata,
        "downloaded_path": None,
    }


def make_download_success(metadata, candidate, downloaded_path):
    return {
        "ok": True,
        "status": "downloaded",
        "error": None,
        "metadata": metadata,
        "candidate": candidate,
        "downloaded_path": downloaded_path,
    }


def get_metadata_type(spotify_link):
    link_type = detect_input_type(spotify_link)

    if link_type == "track":
        result = validate_link_get_metadata_track(spotify_link)
    elif link_type == "playlist":
        result = validate_link_get_metadata_playlist(spotify_link)
    elif link_type == "album":
        result = validate_link_get_metadata_album(spotify_link)
    else:
        return [{
            "ok": False,
            "status": "invalid",
            "error": "Invalid Link",
            "metadata": None,
            "title": None,
            "artists": None,
            "album": None,
            "artwork_url": None,
        }]

    return result


def download_song_from_spotify_link(spotify_link, output_folder=None, progress_callback=None, track_status_callback=None):
    limit = 3
    results = []

    if progress_callback:
        progress_callback("Fetching Metadata...", 0)

    result = get_metadata_type(spotify_link)

    for i, track in enumerate(result, start=1):
        if track_status_callback:
            track_status_callback(i-1, "Downloading")

        if not track["ok"]:
            results.append(track)

            if track_status_callback:
                track_status_callback(i-1, "Failed")

            continue

        metadata = track["metadata"]

        if progress_callback:
            progress_callback("Searching for Candidates...", ((i - 1 + 0.25)/len(result)))

        ytm_candidates = get_youtube_music_candidates(metadata, limit)
        yt_candidates = get_youtube_candidates(metadata, limit)
        candidates = ytm_candidates + yt_candidates

        scored_candidates = score_candidates(metadata, candidates)

        if not scored_candidates:
            fail = make_download_failure(status="no_youtube_results", error="No YouTube candidates found", metadata=metadata)
            results.append(fail)

            if track_status_callback:
                track_status_callback(i-1, "Failed")

            continue

        downloaded_path = None
        candidate_error = None
        successful_candidate = None
        length_of_list = len(scored_candidates)
        minimum_score = 3

        for index, candidate in enumerate(scored_candidates, start=1):
            candidate_dict = candidate[0]
            candidate_score = candidate[1]

            if candidate_score >= minimum_score:
                if progress_callback:
                    progress_callback(f"Trying Match {index} of {length_of_list} for song {i}", ((i - 1 + 0.5)/len(result)))
                try:
                    downloaded_path = download_audio(candidate_dict, metadata, output_folder)

                    successful_candidate = candidate_dict

                    break

                except Exception as error:
                    candidate_error = str(error)
                    continue

            else:
                if candidate_error is None:
                    candidate_error = "No confident YouTube match found."
                break

        if not downloaded_path:
            fail = make_download_failure(status="no_valid_matches", error=format_download_error(candidate_error), metadata=metadata, technical_error=candidate_error)
            results.append(fail)

            if track_status_callback:
                track_status_callback(i-1, "Failed")

            continue

        if progress_callback:
            progress_callback("Adding Metadata...", ((i - 1 + 0.75)/len(result)))

        add_metadata(downloaded_path, metadata)

        if track_status_callback:
            track_status_callback(i-1, "Done")

        success = make_download_success(metadata=metadata, candidate=successful_candidate, downloaded_path=downloaded_path)
        results.append(success)

    if progress_callback:
        progress_callback("Done", 1)

    return results


def preview_metadata(link):
    tracks = []

    data = get_metadata_type(link)

    for track in data:
        if not track["ok"]:
            result = {
                "ok": track["ok"],
                "error": track["error"],
                "title": None,
                "artists": None,
                "album": None,
                "artwork_url": None,
            }

            tracks.append(result)

            continue

        title = track["metadata"]["title"]
        artists = track["metadata"]["artists"]
        album = track["metadata"]["album"]
        song_url = track["metadata"]["url"]
        artwork_url = track["metadata"]["artwork_url"]

        result = {
            "ok": track["ok"],
            "error": track["error"],
            "title": title,
            "artists": artists,
            "album": album,
            "url": song_url,
            "artwork_url": artwork_url,
        }

        tracks.append(result)

    return tracks
