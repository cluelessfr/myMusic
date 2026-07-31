import filecmp
import shutil
from shutil import which
from os import environ
from pathlib import Path
import subprocess
from subprocess import CompletedProcess
from tools.custom_tools.get_app_root import get_app_root


EXTENSION_FILENAME = "mymusic-integration.js"


def remove_extension_configuration(executable_path: Path) -> bool:
    extensions = get_configured_extensions(executable_path)

    if extensions is None:
        raise RuntimeError("Configuration could not be read")

    if EXTENSION_FILENAME not in extensions:
        return False

    process = run_spicetify(executable_path, "config", "extensions", f"{EXTENSION_FILENAME}-")

    if process.returncode != 0:
        raise RuntimeError(f"{process.stderr.strip() or process.stdout.strip() or "Failed to remove Spicetify extension configuration"}")

    return True


def uninstall_spicetify_integration() -> dict:
    file_changed = False
    config_changed = False
    applied = False
    destination = None

    spicetify_executable = find_spicetify_executable()

    if not spicetify_executable:
        return {
            "ok": True,
            "status": "spicetify_not_found",
            "error": None,
            "file_changed": file_changed,
            "config_changed": config_changed,
            "applied": applied,
            "destination": destination,
        }

    try:
        extension_directory = get_spicetify_extension_directory(spicetify_executable)

        if extension_directory is None:
            raise RuntimeError("Spicetify extension directory could not be found")

        destination = extension_directory / EXTENSION_FILENAME

        config_changed = remove_extension_configuration(spicetify_executable)

        if destination.is_file():
            destination.unlink()
            file_changed = True

        if file_changed or config_changed:
            apply_spicetify_configuration(spicetify_executable)
            applied = True
    except (OSError, subprocess.TimeoutExpired, RuntimeError) as error:
        return {
            "ok": False,
            "status": "failed",
            "error": str(error),
            "file_changed": file_changed,
            "config_changed": config_changed,
            "applied": applied,
            "destination": destination,
        }

    if file_changed or config_changed:
        status = "removed"
    else:
        status = "already_removed"

    error = None

    return {
        "ok": True,
        "status": status,
        "error": error,
        "file_changed": file_changed,
        "config_changed": config_changed,
        "applied": applied,
        "destination": destination,
    }


def find_spicetify_executable() -> Path | None:
    spicetify_path_str = which("spicetify")

    if spicetify_path_str is not None:
        spicetify_path = Path(spicetify_path_str)
    else:
        spicetify_path = None

    if spicetify_path is not None and spicetify_path.is_file():
        return spicetify_path

    app_data = environ.get("LOCALAPPDATA")

    if not app_data:
        return None

    fallback_path = Path(app_data) / "spicetify" / "spicetify.exe"

    if fallback_path.is_file():
        return fallback_path

    return None


def run_spicetify(executable_path: Path, *arguments: str):
    command_list = (str(executable_path), *arguments)
    creation_flag = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    process: CompletedProcess[str] = subprocess.run(command_list, capture_output=True, text=True, timeout=60, check=False, creationflags=creation_flag)

    return process


def get_spicetify_extension_directory(executable_path: Path) -> Path | None:
    process = run_spicetify(executable_path, "path", "-e", "root")

    code = process.returncode

    if code != 0:
        return None

    output = process.stdout.strip()

    if not output:
        return None

    path = Path(output)

    return path


def get_bundled_extension_path() -> Path | None:
    bundled_extension_path = get_app_root() / "integrations" / "spicetify" / EXTENSION_FILENAME

    if bundled_extension_path.is_file():
        return bundled_extension_path

    return None


def idempotent_file_copy(source_extension: Path, spicetify_extension: Path) -> tuple[Path, bool]:
    spicetify_extension.mkdir(parents=True, exist_ok=True)

    destination = spicetify_extension / EXTENSION_FILENAME

    if destination.is_file() and filecmp.cmp(source_extension, destination, shallow=False):
        return destination, False

    shutil.copy2(source_extension, destination)

    return destination, True


def get_configured_extensions(spicetify_executable: Path) -> set[str] | None:
    process = run_spicetify(spicetify_executable, "config", "extensions")

    if process.returncode != 0:
        return None

    output = process.stdout.strip()

    if not output:
        return set()

    normalized_output = output.replace('|', '\n')

    split_lines = normalized_output.splitlines()

    final_set: set[str] = set()

    for item in split_lines:
        clean_item = item.strip()

        if clean_item:
            final_set.add(clean_item)

    return final_set


def ensure_extension_configured(executable_path: Path) -> bool:
    configured_extensions = get_configured_extensions(executable_path)

    if configured_extensions is None:
        raise RuntimeError("Configuration command failed")

    if EXTENSION_FILENAME in configured_extensions:
        return False

    process = run_spicetify(executable_path, "config", "extensions", EXTENSION_FILENAME)

    if process.returncode != 0:
        raise RuntimeError(f"{process.stderr.strip() or process.stdout.strip() or "Failed to configure Spicetify extension"}")

    return True


def apply_spicetify_configuration(executable_path: Path) -> None:
    process = run_spicetify(executable_path, "apply")

    if process.returncode != 0:
        raise RuntimeError(f"{process.stderr.strip() or process.stdout.strip() or "Failed to apply Spicetify extension"}")


def install_spicetify_integration() -> dict:
    file_changed = False
    config_changed = False
    applied = False
    destination = None

    spicetify_executable = find_spicetify_executable()

    if spicetify_executable is None:
        return {
            "ok": False,
            "status": "spicetify_not_found",
            "error": "Spicetify executable could not be found",
            "file_changed": file_changed,
            "config_changed": config_changed,
            "applied": applied,
            "destination": destination,
        }

    extension_path = get_bundled_extension_path()

    if extension_path is None:
        return {
            "ok": False,
            "status": "packaging_error",
            "error": "Spicetify extensions could not be found",
            "file_changed": file_changed,
            "config_changed": config_changed,
            "applied": applied,
            "destination": destination,
        }

    try:
        extension_directory = get_spicetify_extension_directory(spicetify_executable)

        if extension_directory is None:
            return {
                "ok": False,
                "status": "extension_directory_not_found",
                "error": "Spicetify extension directory could not be found",
                "file_changed": file_changed,
                "config_changed": config_changed,
                "applied": applied,
                "destination": destination,
            }

        destination, file_changed = idempotent_file_copy(extension_path, extension_directory)

        config_changed = ensure_extension_configured(spicetify_executable)

        if file_changed or config_changed:
            apply_spicetify_configuration(spicetify_executable)

            applied = True

    except (OSError, subprocess.TimeoutExpired, RuntimeError) as error:
        return {
            "ok": False,
            "status": "failed",
            "error": str(error),
            "file_changed": file_changed,
            "config_changed": config_changed,
            "applied": applied,
            "destination": destination,
        }

    if file_changed or config_changed:
        status = "installed"
    else:
        status = "already_installed"

    error = None

    return {
            "ok": True,
            "status": status,
            "error": error,
            "file_changed": file_changed,
            "config_changed": config_changed,
            "applied": applied,
            "destination": destination,
        }
