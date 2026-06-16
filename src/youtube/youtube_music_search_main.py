from typing import Any, cast
import urllib.parse
import yt_dlp


def build_youtube_music_search_url(metadata):
    title = metadata["title"]
    artists = " ".join(metadata["artists"])
    base_url = "https://music.youtube.com/search"

    search_text = title + " " + artists

    query_string = urllib.parse.urlencode({'q': search_text})

    search_url = urllib.parse.urljoin(base_url, f"?{query_string}")

    return search_url


def search_youtube_music(search_url):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }

    with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
        search_results = ydl.extract_info(search_url, download=False)

    return search_results


def filter_youtube_music_candidates(search_results, limit=5):
    candidates = []

    for entry in search_results.get("entries", []):
        url = entry.get("url")

        if url is None:
            continue

        if "music.youtube.com/watch?v=" not in url:
            continue

        candidate = {
            "title": entry.get("title"),
            "url": entry.get("url"),
            "source": "youtube_music",
        }

        candidates.append(candidate)

        if len(candidates) >= limit:
            break

    return candidates


def get_youtube_music_candidates(metadata, limit=5):
    search_url = build_youtube_music_search_url(metadata)
    search_results = search_youtube_music(search_url)
    candidates = filter_youtube_music_candidates(search_results, limit)

    return candidates
