import mutagen.easyid3

def add_metadata(file_path, metadata):
    track = mutagen.easyid3.EasyID3(file_path)

    artists = ", ".join(metadata["artists"])

    track["artist"] = artists
    track["album"] = metadata["album"]
    track["title"] = metadata["title"]

    track.save()
