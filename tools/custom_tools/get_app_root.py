import sys
from pathlib import Path


def get_app_root():
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))

    return Path(__file__).resolve().parents[2]
