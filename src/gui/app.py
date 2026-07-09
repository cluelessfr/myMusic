import customtkinter as ctk
from src.workflows.download_workflow import download_song_from_spotify_link, preview_metadata
from src.gui.settings import load_download_folder, save_download_folder
from src.updater.update_checker import check_for_update
from src.updater.installer_downloader import download_update_installer
from src.updater.installer_runner import run_update_installer
from tkinter import filedialog
from typing import Any
from pathlib import Path
import threading


app = ctk.CTk()
app.title("myMusic")
app.geometry("500x590")

selected_output_folder = load_download_folder()
loaded_tracks = []
UPDATE_STATUS: dict[str, Any] | None = None
UPDATE_CANCEL_EVENT: threading.Event | None = None


def choose_download_folder():
    global selected_output_folder

    folder = filedialog.askdirectory(initialdir=str(selected_output_folder))

    if not folder:
        return

    selected_output_folder = Path(folder)
    folder_label.configure(text=f"Save to: {selected_output_folder}")
    save_download_folder(selected_output_folder)


def progress_update(message, progress):
    def update_status():
        status_label.configure(text=message)
        progress_bar.set(progress)
    # noinspection PyTypeChecker
    app.after(0, update_status)


def render_track_list():
    for widget in track_list_frame.winfo_children():
        widget.destroy()

    for track in loaded_tracks:
        row_frame = ctk.CTkFrame(track_list_frame, corner_radius=6, border_width=1)
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=0)
        title_label_row = ctk.CTkLabel(row_frame, text=track['title'], wraplength=280)
        artist_album_label_row = ctk.CTkLabel(row_frame, text=f"{', '.join(track['artists'])} - {track['album']}", wraplength=280)
        status_label_row = ctk.CTkLabel(row_frame, text=track['status'], width=70, corner_radius=5)

        row_frame.pack(padx=6, pady=4, fill="x")
        title_label_row.grid(column=0, row=0, sticky="w", padx=10, pady=4)
        artist_album_label_row.grid(column=0, row=1, sticky="w", padx=10, pady=4)
        status_label_row.grid(column=1, row=0, sticky="e", padx=10, pady=8)


def preview(link):
    try:
        result = preview_metadata(link)

        def show_preview():
            global loaded_tracks

            if not result["ok"]:
                status_label.configure(text="Error")
                path_label.configure(text=result["error"], wraplength=440)
                return

            title = result['title']
            artists = result['artists']
            album = result['album']

            track_dict = {
                "title": title,
                "artists": artists,
                "album": album,
                "status": "Ready",
                "metadata": result,
            }

            loaded_tracks.clear()
            loaded_tracks.append(track_dict)

            render_track_list()

        # noinspection PyTypeChecker
        app.after(0, show_preview)

    except Exception as error:
        error_message = str(error)

        def show_error():
            status_label.configure(text="Error")
            path_label.configure(text=error_message, wraplength=440)

        # noinspection PyTypeChecker
        app.after(0, show_error)

    finally:
        def enable_buttons():
            set_button_state("normal")

        # noinspection PyTypeChecker
        app.after(0, enable_buttons)


def set_button_state(state, include_folder_button=False):
    preview_button.configure(state=state)
    download_button.configure(state=state)
    update_button.configure(state=state)
    if include_folder_button:
        choose_folder_button.configure(state=state)


def start_preview():
    link = link_entry.get()
    set_button_state("disabled")
    status_label.configure(text="")
    path_label.configure(text="")

    threading.Thread(target=preview, args=(link,), daemon=True).start()


def update_download():
    global UPDATE_CANCEL_EVENT

    update_status = UPDATE_STATUS
    update_cancel_event = UPDATE_CANCEL_EVENT

    if update_status is None:
        return

    installer_asset = update_status["installer_asset"]
    download_url = installer_asset["download_url"]
    asset_name = installer_asset["asset_name"]

    result = download_update_installer(download_url, asset_name, progress_callback=progress_update, cancel_event=update_cancel_event)

    if result["ok"]:
        install_result = run_update_installer(result["download_path"])

    def update_ui():
        global UPDATE_CANCEL_EVENT

        if result["ok"]:
            path_label.configure(text=f"Downloaded to: {result['download_path']}", wraplength=440)
            if install_result["ok"]:
                status_label.configure(text=install_result["message"])
                update_button.configure(text="Check For App Updates", command=start_update_check)
                # noinspection PyTypeChecker
                app.after(1000, app.destroy)
            else:
                status_label.configure(text=install_result["message"])
                update_button.configure(text="Check For App Updates", command=start_update_check)
        elif result.get("canceled"):
            status_label.configure(text="Update canceled")
            path_label.configure(text="")
            update_button.configure(text="Check For App Updates", command=start_update_check)
            progress_bar.set(0)
        else:
            status_label.configure(text=result["message"])
            path_label.configure(text="")

        set_button_state("normal", include_folder_button=True)
        UPDATE_CANCEL_EVENT = None

    # noinspection PyTypeChecker
    app.after(0, update_ui)


def cancel_update_download():
    global UPDATE_CANCEL_EVENT

    if UPDATE_CANCEL_EVENT is not None:
        UPDATE_CANCEL_EVENT.set()

    status_label.configure(text="Canceling update...")
    update_button.configure(state="disabled", text="Canceling Update...")


def start_update_download():
    global UPDATE_CANCEL_EVENT

    if UPDATE_STATUS is None:
        status_label.configure(text="No Updates Available")
        return

    UPDATE_CANCEL_EVENT = threading.Event()
    update_button.configure(text="Cancel Update", command=cancel_update_download)

    set_button_state("disabled", include_folder_button=True)
    update_button.configure(state="normal")

    path_label.configure(text="")
    progress_bar.set(0)

    status_label.configure(text="Downloading update")

    threading.Thread(target=update_download, daemon=True).start()


def update_check_helper():
    global UPDATE_STATUS
    update_status = check_for_update()
    def update_ui():
        global UPDATE_STATUS

        if update_status["update"]:
            UPDATE_STATUS = update_status
            update_button.configure(text="Download And Install Update", command=start_update_download)
            status_label.configure(text="Updates Available")
            path_label.configure(text=f"Current Version: {update_status['current_version']}     Latest Version: {update_status['latest_version']}    Installer Name: {update_status['installer_asset']['asset_name']}")
        elif update_status["status"] == "Failed":
            UPDATE_STATUS = None
            update_button.configure(text="Check For App Updates", command=start_update_check)
            status_label.configure(text=update_status["message"])
        else:
            UPDATE_STATUS = None
            update_button.configure(text="Check For App Updates", command=start_update_check)
            status_label.configure(text=update_status["message"])

        set_button_state("normal", include_folder_button=True)

    # noinspection PyTypeChecker
    app.after(0, update_ui)


def start_update_check():
    set_button_state("disabled", include_folder_button=True)
    status_label.configure(text="Checking for updates...")
    path_label.configure(text="")

    threading.Thread(target=update_check_helper, daemon=True).start()


def run_download(link, output_folder):
    try:
        result = download_song_from_spotify_link(link, output_folder, progress_update)

        def check_ok():
            if not result["ok"]:
                status_label.configure(text="Error")
                path_label.configure(text=result["error"], wraplength=440)
            else:
                status_label.configure(text="Download Complete")
                path_label.configure(text=f"Downloaded to: {result['downloaded_path']}", wraplength=440)

        # noinspection PyTypeChecker
        app.after(0, check_ok)

    except Exception as error:
        error_message = str(error)

        def check_exception():
            status_label.configure(text="Error")
            path_label.configure(text=error_message, wraplength=440)
        # noinspection PyTypeChecker
        app.after(0, check_exception)

    finally:
        def enable_buttons():
            set_button_state("normal", include_folder_button=True)
        # noinspection PyTypeChecker
        app.after(0, enable_buttons)


def start_download():
    link = link_entry.get()
    output_folder = selected_output_folder
    set_button_state("disabled", include_folder_button=True)
    path_label.configure(text="")
    progress_bar.set(0)

    threading.Thread(target=run_download, args=(link, output_folder), daemon=True).start()


link_entry = ctk.CTkEntry(app, placeholder_text="Paste Spotify Link")
track_list_frame = ctk.CTkScrollableFrame(app, width=450, height=170)
choose_folder_button = ctk.CTkButton(app, text="Choose Folder", command=choose_download_folder)
folder_label = ctk.CTkLabel(app, text=f"Save to: {selected_output_folder}", wraplength=440)
status_label = ctk.CTkLabel(app, text="")
progress_bar = ctk.CTkProgressBar(app, orientation="horizontal", width=450, height=20, corner_radius=5)
progress_bar.set(0)
path_label = ctk.CTkLabel(app, text="", wraplength=440)
preview_button = ctk.CTkButton(app, text="Preview Song Details", command=start_preview)
update_button = ctk.CTkButton(app, text="Check For App Updates", command=start_update_check)
download_button = ctk.CTkButton(app, text="Download Song", command=start_download)

link_entry.pack(padx=20, pady=20, fill="x")
preview_button.pack(pady=10)
track_list_frame.pack(pady=10, padx=20, fill="x")
choose_folder_button.pack(pady=5)
folder_label.pack(pady=5)
download_button.pack(pady=10)
status_label.pack(pady=10)
progress_bar.pack(pady=10)
path_label.pack(pady=10)
update_button.pack(pady=10)

app.mainloop()
