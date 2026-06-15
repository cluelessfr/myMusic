import re

# INPUT_TYPE = None

def detect_input_type(link):

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
    match = None

    if f"https://open.spotify.com/{detect_input_type(lowercase_link)}/" in lowercase_link:
        match = re.search(rf"https://open\.spotify\.com/{detect_input_type(link)}/([^/?\s]+)", link, re.IGNORECASE)
    elif f"spotify:{detect_input_type(lowercase_link)}" in lowercase_link:
        match = re.search(rf"spotify:{detect_input_type(link)}:([^\s)}}.,;:]+)", link, re.IGNORECASE)

    if match is None:
        return None

    link = match.group(0)
    return link.strip().replace("\u200b", "").rstrip(")}.,;:").strip()

def detect_spotify_link(link):
    detect_input_type(link)
    if detect_input_type(link) is None:
        return None
    cleaned_url = clean_spotify_link(link)
    if cleaned_url is None:
        return None

    return detect_input_type(link), cleaned_url
