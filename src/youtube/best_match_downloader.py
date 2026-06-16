import os
from pathlib import Path
from typing import Any, cast
import yt_dlp


def download_audio(candidate, output_folder=None):
    song_url = candidate["url"]

    if output_folder is None:
        output_folder = Path.home() / "Downloads"

    os.makedirs(output_folder, exist_ok=True)

    ydl_opts = {
        "outtmpl": str(Path(output_folder) / "%(title)s.%(ext)s"),
        "format": "bestaudio/best",
    }

    with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
        ydl.download([song_url])
