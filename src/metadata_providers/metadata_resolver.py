from src.metadata_providers.spotify_scraper_main import scrape_spotify_metadata
from src.spotify.spotify_link_cleaner import detect_input_type, clean_spotify_link, extract_spotify_id


def normalize_track_metadata(raw_metadata, input_type, spotify_id, source):
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


def validate_link_get_metadata(link):
    input_type = detect_input_type(link)
    cleaned_url = clean_spotify_link(link)
    spotify_id = extract_spotify_id(link)

    source = "spotify_scraper"

    if (cleaned_url is None) or (spotify_id is None) or (input_type is None):
        ok = False
        status = "invalid"
        error = "Spotify link is invalid"
        return {'ok': ok, 'status': status, 'error': error, 'metadata': None}

    if input_type != "track":
        ok = False
        status = "unsupported"
        error = "Only single tracks are supported for now"
        return {'ok': ok, 'status': status, 'error': error, 'metadata': None}

    raw_metadata = scrape_spotify_metadata(cleaned_url)

    if raw_metadata is None:
        ok = False
        status = "failed"
        error = "Failed to fetch metadata"
        return {'ok': ok, 'status': status, 'error': error, 'metadata': None}

    normalized_metadata = normalize_track_metadata(raw_metadata, input_type, spotify_id, source)

    ok = True
    status = "enriched"
    error = None

    message = {'ok': ok, 'status': status, 'error': error, 'metadata': normalized_metadata}

    return message
