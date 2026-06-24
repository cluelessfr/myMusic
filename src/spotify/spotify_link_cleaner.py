import re


def detect_input_type(link):
    if link is None:
        return None

    lowercase_link = link.lower()

    if "spotify" in lowercase_link:
        if "/track/" in lowercase_link or ":track:" in lowercase_link:
            return "track"
        elif "/playlist/" in lowercase_link or ":playlist:" in lowercase_link:
            return "playlist"
        elif "/album/" in lowercase_link or ":album:" in lowercase_link:
            return "album"

    return None


def clean_spotify_link(link):

    lowercase_link = link.lower()
    input_type = detect_input_type(link)
    if input_type is None:
        return None
    match = None

    if f"https://open.spotify.com/{input_type}/" in lowercase_link:
        match = re.search(rf"https://open\.spotify\.com/{input_type}/([^/?\s]+)", link, re.IGNORECASE)
    elif f"spotify:{input_type}" in lowercase_link:
        match = re.search(rf"spotify:{input_type}:([^\s)}}.,;:]+)", link, re.IGNORECASE)

    if match is None:
        return None

    link = match.group(0)
    return link.strip().replace("\u200b", "").rstrip(")}.,;:").strip()


def extract_spotify_id(link):

    cleaned_url = clean_spotify_link(link)
    input_type = detect_input_type(cleaned_url)
    match = None

    if cleaned_url is None or input_type is None:
        return None

    if "https://open.spotify.com/" in cleaned_url:
        match = re.search(rf"https://open\.spotify\.com/{input_type}/([^/?\s]+)", cleaned_url, re.IGNORECASE)
    elif "spotify:" in cleaned_url:
        match = re.search(rf"spotify:{input_type}:([^\s)}}.,;:]+)", cleaned_url, re.IGNORECASE)

    if match is None:
        return None

    spotify_id = match.group(1)

    return spotify_id
