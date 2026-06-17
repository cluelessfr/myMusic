import customtkinter as ctk
from src.gui.download_workflow import download_song_from_spotify_link, preview_metadata
import threading


app = ctk.CTk()
app.title("myMusic")
app.geometry("500x420")

link_entry = ctk.CTkEntry(app, placeholder_text="Paste Spotify Link")

status_label = ctk.CTkLabel(app, text="")

title_label = ctk.CTkLabel(app, text="")
artist_label = ctk.CTkLabel(app, text="")
album_label = ctk.CTkLabel(app, text="")

path_label = ctk.CTkLabel(app, text="")

def preview():
    preview_button.configure(state="disabled")
    download_button.configure(state="disabled")

    try:
        status_label.configure(text="")
        path_label.configure(text="")
        title_label.configure(text="")
        artist_label.configure(text="")
        album_label.configure(text="")

        metadata = preview_metadata(link_entry.get())

        if not metadata["ok"]:
            status_label.configure(text="Error")
            path_label.configure(text=metadata["error"], wraplength=440)
            return

        title_label.configure(text=f"Title: {metadata['title']}")
        artist_label.configure(text=f"Artist(s): {', '.join(metadata['artists'])}")
        album_label.configure(text=f"Album: {metadata['album']}")

    except Exception as error:
        status_label.configure(text="Error")
        path_label.configure(text=str(error), wraplength=440)

    finally:
        preview_button.configure(state="normal")
        download_button.configure(state="normal")

def start_preview():
    threading.Thread(target=preview).start()

preview_button = ctk.CTkButton(app, text="Preview Song Details", command=start_preview)

def run_download():
    download_button.configure(state="disabled")
    preview_button.configure(state="disabled")

    try:
        link = link_entry.get()

        status_label.configure(text="Downloading...")
        path_label.configure(text="")

        result = download_song_from_spotify_link(link)

        if not result["ok"]:
            status_label.configure(text="Error")
            path_label.configure(text=result["error"], wraplength=440)
        else:
            status_label.configure(text="Download Complete")
            path_label.configure(text=f"Downloaded to: {result['downloaded_path']}", wraplength=440)

    except Exception as error:
        status_label.configure(text="Error")
        path_label.configure(text=str(error), wraplength=440)

    finally:
        download_button.configure(state="normal")
        preview_button.configure(state="normal")

def start_download():
    threading.Thread(target=run_download).start()

download_button = ctk.CTkButton(app, text="Download", command=start_download)

link_entry.pack(padx=20, pady=20, fill="x")
preview_button.pack(pady=10)
status_label.pack(pady=10)
title_label.pack(pady=10)
artist_label.pack(pady=10)
album_label.pack(pady=10)
path_label.pack(pady=10)
download_button.pack(pady=10)

app.mainloop()
