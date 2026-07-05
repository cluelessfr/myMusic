import requests
import sys
from typing import Any, Dict, Optional
from src.app_version import CURRENT_APP_VERSION

GITHUB_LATEST_RELEASE_URL = "https://api.github.com/repos/cluelessfr/myMusic/releases/latest"
if sys.platform.startswith("win"):
    INSTALLER_ASSET_SUFFIX = "windows-setup.exe"
elif sys.platform.startswith("linux"):
    INSTALLER_ASSET_SUFFIX = "linux-x64.tar.gz"
else:
    INSTALLER_ASSET_SUFFIX = None


def normalize_version(version_text):
    if version_text.startswith("v"):
        version_text = version_text[1:]

    return version_text

def version_to_tuple(version_text):
    normalized_version = normalize_version(version_text)

    return tuple(map(int, normalized_version.split(".")))

def is_newer_version(latest_version, current_version):
    return version_to_tuple(latest_version) > version_to_tuple(current_version)

def fetch_latest_release() -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(GITHUB_LATEST_RELEASE_URL, timeout=10)

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException:
        return None

def find_installer_asset(release_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if INSTALLER_ASSET_SUFFIX is None:
        return None

    assets = release_dict["assets"]

    for asset in assets:
        if asset["name"].endswith(INSTALLER_ASSET_SUFFIX):
            return asset
    return None

def check_for_update():
    latest_release_dict = fetch_latest_release()

    if not latest_release_dict:
        return {
            "status": "Failed",
            "update": False,
            "current_version": CURRENT_APP_VERSION,
            "latest_version": CURRENT_APP_VERSION,
            "message": "Failed to fetch latest release",
        }

    tag_name = latest_release_dict["tag_name"]
    normalized_tag_name = normalize_version(tag_name)
    is_update_available = is_newer_version(normalized_tag_name, CURRENT_APP_VERSION)

    if is_update_available:
        installer_asset = find_installer_asset(latest_release_dict)

        if installer_asset is None:
            return {
                "status": "Failed",
                "update": False,
                "current_version": CURRENT_APP_VERSION,
                "latest_version": normalized_tag_name,
                "message": "No installer asset found",
            }

        return {
            "status": "Success",
            "update": True,
            "current_version": CURRENT_APP_VERSION,
            "latest_version": normalized_tag_name,
            "message": "Updates available",
            "installer_asset": {
                "download_url": installer_asset["browser_download_url"],
                "asset_name": installer_asset["name"],
            },
        }

    return {
        "status": "Success",
        "update": False,
        "current_version": CURRENT_APP_VERSION,
        "latest_version": normalized_tag_name,
        "message": "The app is up to date",
    }
