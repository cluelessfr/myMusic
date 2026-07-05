import sys
import subprocess
from pathlib import Path

def run_update_installer(installer_path):
    path = Path(installer_path)

    if not path.exists():
        return {
            "ok": False,
            "status": "Install failed",
            "message": "Path does not exist",
        }

    if sys.platform.startswith("linux"):
        return {
            "ok": False,
            "status": "Manual install required",
            "message": "Update archive downloaded. Install it manually.",
        }

    if path.suffix.lower() != ".exe":
        return {
            "ok": False,
            "status": "Install failed",
            "message": "Installer must be an .exe file",
        }

    try:
        subprocess.Popen([str(path), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"])
    except OSError:
        return {
            "ok": False,
            "status": "Install failed",
            "message": "Could not run installer",
        }

    return {
        "ok": True,
        "status": "Installer started",
        "message": "Installer started",
    }
