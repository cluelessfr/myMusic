import os
import yt_dlp
from pathlib import Path
from typing import Any, cast
from tools.custom_tools.get_app_root import get_app_root
from tools.custom_tools.clean_filename import clean_filename


def download_audio(candidate, metadata, output_folder=None):
    song_url = candidate["url"]

    if output_folder is None:
        output_folder = Path.home() / "Downloads"

    title = metadata["title"]
    filename = clean_filename(title)

    os.makedirs(output_folder, exist_ok=True)
    final_path = Path(output_folder) / f"{filename}.mp3"

    app_root = get_app_root()
    ffmpeg_folder = app_root / "tools" / "ffmpeg" / "bin"

    ydl_opts = {
        "outtmpl": str(Path(output_folder) / f"{filename}.%(ext)s"),
        "format": "bestaudio/best",
        "ffmpeg_location": str(ffmpeg_folder),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
        ydl.download([song_url])

    return final_path
