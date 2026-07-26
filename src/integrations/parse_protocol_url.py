import re
from urllib.parse import urlparse, parse_qs


SUPPORTED_SPOTIFY_URI_PATTERN = re.compile(r"^spotify:(track|playlist|album):[a-zA-Z0-9]{22}$")


def is_supported_spotify_uri(uri):
    if not isinstance(uri, str):
        return False

    if SUPPORTED_SPOTIFY_URI_PATTERN.fullmatch(uri) is None:
        return False

    return True


def parse_protocol_url(protocol_url):
    if not isinstance(protocol_url, str):
        return None

    url = urlparse(protocol_url)

    if url.scheme != "mymusic":
        return None

    if url.netloc != "download":
        return None

    query = parse_qs(url.query)

    uri_values = query.get("uri")

    if not uri_values or len(uri_values) != 1:
        return None

    spotify_uri = uri_values[0]

    if not is_supported_spotify_uri(spotify_uri):
        return None

    return spotify_uri


def parse_protocol_arguments(arguments):
    if not isinstance(arguments, (list, tuple)):
        return None

    for item in arguments[1:]:
        parsed_url = parse_protocol_url(item)

        if parsed_url is not None:
            return parsed_url

    return None
