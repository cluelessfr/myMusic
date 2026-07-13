from src.metadata_providers.spotify_scraper_main import scrape_spotify_metadata
from src.metadata_providers.spotify_oembed_fallback import fetch_spotify_oembed
from src.spotify.spotify_link_cleaner import detect_input_type, clean_spotify_link, extract_spotify_id


def normalize_track_metadata(raw_metadata, input_type, spotify_id, source):
    if input_type == "track":
        if raw_metadata.release_date is not None:
            release_date = str(raw_metadata.release_date.date())
        else:
            release_date = None

        artists = []

        for artist in raw_metadata.artists:
            artists.append(artist.name)

        return {
            'title': raw_metadata.name,
            'artists': artists,
            'album': raw_metadata.album.name,
            'duration_ms': raw_metadata.duration_ms,
            'explicit': raw_metadata.explicit,
            'artwork_url': raw_metadata.images[0].url,
            'url': raw_metadata.url,
            'id': raw_metadata.id,
            'release_date': release_date,
            'preview_url': raw_metadata.preview_url,
            'input_type': input_type,
            'spotify_id': spotify_id,
            'source': source,
        }

    return None


def validate_link_get_metadata_track(link):
    input_type = detect_input_type(link)
    cleaned_url = clean_spotify_link(link)
    spotify_id = extract_spotify_id(link)

    source = "spotify_scraper"

    if (cleaned_url is None) or (spotify_id is None) or (input_type is None):
        ok = False
        status = "invalid"
        error = "Spotify link is invalid"
        return [{'ok': ok, 'status': status, 'error': error, 'metadata': None}]

    if input_type != "track":
        ok = False
        status = "unsupported"
        error = "Only single tracks are supported for now"
        return [{'ok': ok, 'status': status, 'error': error, 'metadata': None}]

    raw_metadata = scrape_spotify_metadata(cleaned_url)

    if raw_metadata is None:
        source = "spotify_oembed"
        oembed_metadata = fetch_spotify_oembed(cleaned_url)
        if oembed_metadata is None:
            ok = False
            status = "failed"
            error = "Failed to fetch metadata"
            return [{'ok': ok, 'status': status, 'error': error, 'metadata': None}]

        title = oembed_metadata.get("title")

        if not title or title is None:
            ok = False
            status = "failed"
            error = "Failed to fetch metadata"
            return [{'ok': ok, 'status': status, 'error': error, 'metadata': None}]

        title = title.strip().replace("\u200b", "").strip()

        if title == "":
            ok = False
            status = "failed"
            error = "Failed to fetch metadata"
            return [{'ok': ok, 'status': status, 'error': error, 'metadata': None}]

        fallback_metadata = {
            "title": title,
            "artists": [],
            "album": "",
            "duration_ms": None,
            "explicit": None,
            "artwork_url": oembed_metadata.get("thumbnail_url"),
            "url": cleaned_url,
            "id": spotify_id,
            "release_date": None,
            "preview_url": None,
            "input_type": input_type,
            "spotify_id": spotify_id,
            "source": source,
        }

        ok = True
        status = "enriched"
        error = None

        return [{'ok': ok, 'status': status, 'error': error, 'metadata': fallback_metadata}]

    normalized_metadata = normalize_track_metadata(raw_metadata, input_type, spotify_id, source)

    ok = True
    status = "enriched"
    error = None

    message = {'ok': ok, 'status': status, 'error': error, 'metadata': normalized_metadata}

    return [message]


def validate_link_get_metadata_playlist(link):
    input_type = detect_input_type(link)
    cleaned_url = clean_spotify_link(link)
    spotify_id = extract_spotify_id(link)

    if (cleaned_url is None) or (spotify_id is None) or (input_type is None):
        ok = False
        status = "invalid"
        error = "Spotify link is invalid"
        return [{'ok': ok, 'status': status, 'error': error, 'metadata': None}]

    if input_type != "playlist":
        return [{
            "ok": False,
            "status": "unsupported",
            "error": "Expected a Spotify playlist link",
            "metadata": None,
        }]

    playlist = []

    raw_metadata = scrape_spotify_metadata(cleaned_url)

    if raw_metadata is None:
        return [{
            "ok": False,
            "status": "failed",
            "error": "Failed to fetch metadata",
            "metadata": None,
        }]

    for entry in raw_metadata.tracks:
        raw_track = entry.track
        normalized_result = normalize_track_metadata(raw_track, "track", raw_track.id, "spotify_scraper")

        result = {
            "ok": True,
            "status": "enriched",
            "error": None,
            "metadata": normalized_result,
        }

        playlist.append(result)

    return playlist


def normalize_album_metadata(raw_track, raw_album):
    release_date = (
        str(raw_album.release_date.date())
        if raw_album.release_date is not None
        else None
    )

    return {
        "title": raw_track.name,
        "artists": [artist.name for artist in raw_track.artists],
        "album": raw_album.name,
        "duration_ms": raw_track.duration_ms,
        "explicit": raw_track.explicit,
        "artwork_url": raw_album.images[0].url,
        "url": raw_track.url,
        "id": raw_track.id,
        "release_date": release_date,
        "preview_url": raw_track.preview_url,
        "input_type": "track",
        "spotify_id": raw_track.id,
        "source": "spotify_scraper",
    }


def validate_link_get_metadata_album(link):
    input_type = detect_input_type(link)
    cleaned_url = clean_spotify_link(link)
    spotify_id = extract_spotify_id(link)

    if (cleaned_url is None) or (spotify_id is None) or (input_type is None):
        ok = False
        status = "invalid"
        error = "Spotify link is invalid"
        return [{'ok': ok, 'status': status, 'error': error, 'metadata': None}]

    if input_type != "album":
        return [{
            "ok": False,
            "status": "unsupported",
            "error": "Expected a Spotify album link",
            "metadata": None,
        }]

    album = []

    raw_metadata = scrape_spotify_metadata(cleaned_url)

    if raw_metadata is None:
        return [{
            "ok": False,
            "status": "failed",
            "error": "Failed to fetch metadata",
            "metadata": None,
        }]

    for entry in raw_metadata.tracks:
        normalized_metadata = normalize_album_metadata(entry, raw_metadata)

        result = {
            "ok": True,
            "status": "enriched",
            "error": None,
            "metadata": normalized_metadata,
        }

        album.append(result)

    return album
