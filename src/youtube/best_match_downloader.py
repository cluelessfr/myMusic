import os
import sys
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
    ffmpeg_name = "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg"
    ffmpeg_path = app_root / "tools" / "ffmpeg" / "bin" / ffmpeg_name

    ydl_opts = {
        "outtmpl": str(Path(output_folder) / f"{filename}.%(ext)s"),
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    if ffmpeg_path.exists():
        ydl_opts["ffmpeg_location"] = str(ffmpeg_path.parent)

    deno_name = "deno.exe" if sys.platform.startswith("win") else "deno"
    deno_path = app_root / "tools" / "deno" / "bin" / deno_name

    if deno_path.exists():
        ydl_opts["js_runtimes"] = cast(
            Any,
            {
                "deno": {
                    "path": str(deno_path),
                },
            },
        )

    with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
        ydl.download([song_url])

    return final_path
