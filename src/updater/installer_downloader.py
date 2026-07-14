from tools.custom_tools.clean_filename import clean_filename
from pathlib import Path
import requests


def download_update_installer(download_url, asset_name, download_folder=None, progress_callback=None, cancel_event=None):
    if download_folder is None:
        download_folder = Path.home() / "Downloads"

    cleaned_asset_name = clean_filename(asset_name)
    path_folder = Path(download_folder)
    final_path = Path(path_folder / cleaned_asset_name)
    temp_path = final_path.with_suffix(final_path.suffix + ".download")

    try:
        path_folder.mkdir(parents=True, exist_ok=True)
        download = requests.get(download_url, stream=True, timeout=10)
        download.raise_for_status()

        response_size = download.headers.get("content-length")

        if response_size is not None:
            size = int(response_size)
        else:
            size = 0

        bytes_downloaded = 0
        canceled = False

        with open(temp_path, "wb") as file:
            for chunk in download.iter_content(chunk_size=1048576):
                if chunk:
                    if cancel_event is not None and cancel_event.is_set():
                        canceled = True
                        break
                    else:
                        file.write(chunk)
                        bytes_downloaded += len(chunk)
                        if progress_callback:
                            if size != 0:
                                progress_callback("Downloading update", min((bytes_downloaded / size), 1.0))
                            else:
                                progress_callback("Downloading update", 0)

        if canceled:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            return {
                "ok": False,
                "download_path": None,
                "canceled": True,
                "message": "Update canceled",
            }

        temp_path.replace(final_path)

        if progress_callback:
            progress_callback("Download complete", 1.0)

        return {
            "ok": True,
            "download_path": str(final_path),
            "message": "Download successful",
        }

    except (requests.exceptions.RequestException, OSError):
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)

        return {
            "ok": False,
            "download_path": None,
            "message": "Could not download update installer",
        }
