from pathlib import Path
import json
import sys

settings_path = Path("~/AppData/Roaming/myMusic").expanduser() if sys.platform.startswith("win") else Path("~/.config/myMusic").expanduser()
settings_json_path = settings_path / "settings.json"

fallback_folder = Path.home() / "Downloads"

def load_download_folder():
    settings_path.mkdir(parents=True, exist_ok=True)

    if not settings_json_path.exists():
        selected_output_folder = fallback_folder
    else:
        try:
            saved_folder = json.loads(settings_json_path.read_text()).get("download_dir")
            if not isinstance(saved_folder, str):
                selected_output_folder = fallback_folder
            elif saved_folder == "":
                selected_output_folder = fallback_folder
            else:
                saved_folder = Path(saved_folder)
                if saved_folder.is_dir():
                    selected_output_folder = saved_folder
                else:
                    selected_output_folder = fallback_folder

        except Exception:
            selected_output_folder = fallback_folder

    return selected_output_folder

def save_download_folder(folder):
    settings_path.mkdir(parents=True, exist_ok=True)

    download_folder = Path(folder)

    settings = {
        "download_dir": str(download_folder)
    }

    settings_json = json.dumps(settings, indent=4)
    settings_json_path.write_text(settings_json)
