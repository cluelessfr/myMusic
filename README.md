# myMusic

myMusic is an early Windows-focused music utility for turning a Spotify track link into a local MP3 file.

The project is still in active development. The current version is no longer metadata-only: it now has a basic end-to-end single-track flow that resolves Spotify metadata, searches YouTube Music, downloads audio, converts it to MP3, and writes basic metadata tags.

## Current Status

Working today:

- Accepts Spotify track links.
- Cleans Spotify links and extracts the Spotify ID.
- Detects Spotify track, playlist, and album links.
- Resolves track metadata such as title, artists, album, duration, artwork URL, release date, and Spotify ID.
- Searches YouTube Music for matching results.
- Chooses the first YouTube Music candidate.
- Downloads the selected audio with `yt-dlp`.
- Converts the download to MP3 with FFmpeg.
- Adds basic ID3 metadata tags for title, artist, and album.
- Saves downloads to the user's Downloads folder.
- Provides both a command-line entry point and a simple CustomTkinter GUI.

Still in progress:

- Playlist downloads.
- Album downloads.
- Choosing between multiple YouTube Music matches.
- Choosing a custom download folder.
- Embedded artwork tagging.
- Better download progress in the GUI.
- Packaged app builds and public releases.
- More complete automated tests.

## How It Works

The current single-track flow is:

1. The user pastes a Spotify track link.
2. The program cleans the link and checks that it is a supported Spotify track.
3. The metadata resolver fetches normalized Spotify metadata.
4. The YouTube Music search step builds a search query from the track title and artists.
5. The downloader picks the first YouTube Music candidate.
6. `yt-dlp` downloads the best available audio.
7. FFmpeg converts the audio to MP3.
8. `mutagen` writes basic title, artist, and album tags.
9. The finished MP3 is saved in the user's Downloads folder.

## Project Structure

- `src/main.py` - command-line entry point.
- `src/gui/app.py` - simple CustomTkinter desktop window.
- `src/gui/download_workflow.py` - connects metadata lookup, YouTube Music search, download, and tagging.
- `src/spotify/spotify_link_cleaner.py` - Spotify link detection, cleaning, and ID extraction.
- `src/metadata_providers/metadata_resolver.py` - validates Spotify input and returns normalized track metadata.
- `src/youtube/youtube_music_search_main.py` - searches YouTube Music for candidate matches.
- `src/youtube/best_match_downloader.py` - downloads and converts the selected audio.
- `src/audio/metadata_tagger.py` - writes basic MP3 metadata.
- `tools/custom_tools/` - small helpers used by the downloader.

## Local Setup

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

If you are using the project virtual environment, activate it first:

```powershell
.\.venv\Scripts\Activate.ps1
```

FFmpeg is required for MP3 conversion. During local development, the code expects FFmpeg at:

```text
tools/ffmpeg/bin/ffmpeg.exe
```

The `tools/ffmpeg/` folder is intentionally ignored by git because it contains large local binaries.

## Running the App

Run the command-line version:

```powershell
python -m src.main
```

Run the GUI version:

```powershell
python -m src.gui.app
```

Paste a Spotify track link when prompted or into the GUI input field.

## Basic Test Script

There is a simple status-check script for the metadata resolver:

```powershell
python -m test.test
```

It currently checks:

- A valid Spotify track.
- Invalid non-Spotify input.
- An unsupported album link.
- A bad track ID.

## Next Milestones

The next useful improvements are:

1. Let the user review or choose the YouTube Music match before downloading.
2. Add better progress and error messages to the GUI.
3. Add custom output folder selection.
4. Add embedded cover artwork to downloaded MP3s.
5. Add playlist and album support after the single-track flow is more reliable.
