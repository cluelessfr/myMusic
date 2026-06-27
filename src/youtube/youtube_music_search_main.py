from typing import Any, cast
import urllib.parse
import yt_dlp


def search_text_strings(metadata):
    title = metadata["title"]
    artists = " ".join(metadata["artists"])
    if metadata and metadata["artists"] is not None:
        first_artist = metadata["artists"][0] if metadata["artists"] else ""
    else:
        first_artist = ""

    search_text0 = title + " " + artists
    search_text1 = title + " " + first_artist + " official audio"
    search_text2 = title

    if first_artist == "":
        return [search_text2]
    else:
        return [search_text0, search_text1, search_text2]

def build_search_url(search_text_string, base_url="https://music.youtube.com/search"):
    search_query = urllib.parse.urlencode({'q': search_text_string})
    search_url = urllib.parse.urljoin(base_url, f"?{search_query}")

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


def filter_youtube_music_candidates(search_results, limit=3):
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


def get_youtube_music_candidates(metadata, limit=3):
    search_text = search_text_strings(metadata)
    search_url = build_search_url(search_text[0])
    search_results = search_youtube_music(search_url)
    candidates = filter_youtube_music_candidates(search_results, limit)

    return candidates
