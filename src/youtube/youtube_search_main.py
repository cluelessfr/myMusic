from src.youtube.youtube_music_search_main import search_text_strings, build_search_url, search_youtube_music


def filter_youtube_candidates(search_results, limit=3):
    candidates = []

    for entry in search_results.get("entries", []):
        url = entry.get("url")

        if url is None:
            continue

        if "https://www.youtube.com/watch?v=" not in url:
            continue

        candidate = {
            "title": entry.get("title"),
            "url": entry.get("url"),
            "source": "youtube",
        }

        candidates.append(candidate)

        if len(candidates) >= limit:
            break

    return candidates

def get_youtube_candidates(metadata, limit=3):
    search_string = search_text_strings(metadata)
    search_url = build_search_url(search_string[0], base_url="https://www.youtube.com/search")
    results = search_youtube_music(search_url)
    candidates = filter_youtube_candidates(results, limit)

    return candidates
