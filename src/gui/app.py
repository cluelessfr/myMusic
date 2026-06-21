import customtkinter as ctk
from src.gui.download_workflow import download_song_from_spotify_link, preview_metadata
from pathlib import Path
import json
from tkinter import filedialog
import threading


app = ctk.CTk()
app.title("myMusic")
app.geometry("500x540")

settings_path = Path("~/AppData/Roaming/myMusic").expanduser()
settings_json_path = settings_path / "settings.json"

settings_path.mkdir(parents=True, exist_ok=True)

fallback_folder = Path.home() / "Downloads"

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


def choose_download_folder():
    global selected_output_folder

    folder = filedialog.askdirectory(initialdir=str(selected_output_folder))

    if folder == "":
        return

    selected_output_folder = Path(folder)
    folder_label.configure(text=f"Save to: {selected_output_folder}")

    settings = {
        "download_dir": str(selected_output_folder)
    }
    settings_json = json.dumps(settings, indent=4)
    settings_json_path.write_text(settings_json)

link_entry = ctk.CTkEntry(app, placeholder_text="Paste Spotify Link")

choose_folder_button = ctk.CTkButton(app, text="Choose Folder", command=choose_download_folder)
folder_label = ctk.CTkLabel(app, text=f"Save to: {selected_output_folder}", wraplength=440)

status_label = ctk.CTkLabel(app, text="")
progress_bar = ctk.CTkProgressBar(app, orientation="horizontal", width=450, height=20, corner_radius=5)
progress_bar.set(0)

def progress_update(message, progress):
    def update_status():
        status_label.configure(text=message)
        progress_bar.set(progress)
    app.after(0, update_status)

title_label = ctk.CTkLabel(app, text="")
artist_label = ctk.CTkLabel(app, text="")
album_label = ctk.CTkLabel(app, text="")

path_label = ctk.CTkLabel(app, text="")

def preview(link):
    try:
        result = preview_metadata(link)

        def show_preview():
            if not result["ok"]:
                status_label.configure(text="Error")
                path_label.configure(text=result["error"], wraplength=440)
                return

            title_label.configure(text=f"Title: {result['title']}")
            artist_label.configure(text=f"Artist(s): {', '.join(result['artists'])}")
            album_label.configure(text=f"Album: {result['album']}")

        app.after(0, show_preview)

    except Exception as error:
        error_message = str(error)

        def show_error():
            status_label.configure(text="Error")
            path_label.configure(text=error_message, wraplength=440)

        app.after(0, show_error)

    finally:
        def enable_buttons():
            preview_button.configure(state="normal")
            download_button.configure(state="normal")

        app.after(0, enable_buttons)

def start_preview():
    link = link_entry.get()
    preview_button.configure(state="disabled")
    download_button.configure(state="disabled")
    status_label.configure(text="")
    path_label.configure(text="")
    title_label.configure(text="")
    artist_label.configure(text="")
    album_label.configure(text="")

    threading.Thread(target=preview, args=(link,), daemon=True).start()

preview_button = ctk.CTkButton(app, text="Preview Song Details", command=start_preview)

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

        app.after(0, check_ok)

    except Exception as error:
        error_message = str(error)

        def check_exception():
            status_label.configure(text="Error")
            path_label.configure(text=error_message, wraplength=440)
        app.after(0, check_exception)

    finally:
        def enable_buttons():
            download_button.configure(state="normal")
            preview_button.configure(state="normal")
            choose_folder_button.configure(state="normal")
        app.after(0, enable_buttons)

def start_download():
    link = link_entry.get()
    output_folder = selected_output_folder
    download_button.configure(state="disabled")
    preview_button.configure(state="disabled")
    choose_folder_button.configure(state="disabled")
    path_label.configure(text="")
    progress_bar.set(0)

    threading.Thread(target=run_download, args=(link, output_folder), daemon=True).start()

download_button = ctk.CTkButton(app, text="Download", command=start_download)

link_entry.pack(padx=20, pady=20, fill="x")
choose_folder_button.pack(pady=5)
folder_label.pack(pady=5)
preview_button.pack(pady=10)
title_label.pack(pady=10)
artist_label.pack(pady=10)
album_label.pack(pady=10)
path_label.pack(pady=10)
download_button.pack(pady=10)
status_label.pack(pady=10)
progress_bar.pack(pady=10)

app.mainloop()
