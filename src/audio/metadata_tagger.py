import io
from mutagen.id3 import ID3, APIC
import mutagen.easyid3 as easyid3
import requests


def add_metadata(file_path, metadata):
    track = easyid3.EasyID3(file_path)

    artists = ", ".join(metadata["artists"])

    track["artist"] = artists
    track["album"] = metadata["album"]
    track["title"] = metadata["title"]

    track.save()

    add_cover_art(file_path, metadata.get("artwork_url"))

def add_cover_art(audio_path, artwork_url):
    if artwork_url is None:
        return

    try:
        response = requests.get(artwork_url, stream=True, timeout=10)
        tags = ID3(audio_path)
        image_bytes = io.BytesIO()

        if response.status_code != 200:
            return

        mime_type = response.headers.get("Content-Type", "image/jpeg")

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                image_bytes.write(chunk)

        tags.add(
            APIC(
                encoding=3,
                mime=mime_type,
                type=3,
                desc="Cover",
                data=image_bytes.getvalue(),
            )
        )

        tags.save(v2_version=3)

    except Exception:
        return

