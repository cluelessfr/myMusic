from tools.custom_tools.clean_filename import clean_filename
from pathlib import Path
import requests


def download_update_installer(download_url, asset_name, download_folder=None):
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

        with open(temp_path, "wb") as file:
            for chunk in download.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        temp_path.replace(final_path)

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
