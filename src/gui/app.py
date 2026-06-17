import customtkinter as ctk
from src.gui.download_workflow import download_song_from_spotify_link
import threading


app = ctk.CTk()
app.title("myMusic")
app.geometry("500x280")

link_entry = ctk.CTkEntry(app, placeholder_text="Paste Spotify Link")
link_entry.pack(padx=20, pady=20, fill="x")

status_label = ctk.CTkLabel(app, text="")
status_label.pack(pady=10)

path_label = ctk.CTkLabel(app, text="")
path_label.pack(pady=10)

def run_download():
    download_button.configure(state="disabled")
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

def start_download():
    threading.Thread(target=run_download).start()

download_button = ctk.CTkButton(app, text="Download", command=start_download)
download_button.pack(pady=10)

app.mainloop()
