import re
from urllib.parse import urlparse, parse_qs


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

    pattern = r"^spotify:(track|playlist|album):[a-zA-Z0-9]{22}$"
    spotify_uri = uri_values[0]

    if not re.fullmatch(pattern, spotify_uri):
        return None

    return spotify_uri


def parse_protocol_arguments(arguments):
    pass
