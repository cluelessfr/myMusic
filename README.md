# myMusic

myMusic is an early rebuild of a music utility for turning Spotify track links into offline music files.

The long-term goal is to let a user paste a Spotify link, resolve the correct track metadata, find the matching audio source, download it, tag it, and save it as a local file for offline listening.

## Current Status

This project is still in the early rebuild stage. The current code focuses on the first part of the pipeline: accepting Spotify links, cleaning them, identifying the Spotify item type, and resolving track metadata.

Working today:

- Detects Spotify track, playlist, and album links.
- Cleans normal Spotify URLs and Spotify URI-style inputs.
- Extracts the Spotify ID from a cleaned link.
- Supports metadata lookup for single tracks.
- Returns clear statuses for valid, invalid, unsupported, and failed metadata lookups.

Not built yet:

- Playlist downloads.
- Album downloads.
- YouTube matching.
- Audio downloading.
- MP3 conversion.
- Metadata tagging.
- Desktop app interface.

## How It Works

The planned full flow is:

1. The user pastes a Spotify track, playlist, or album link.
2. The program cleans the link and detects what kind of Spotify item it is.
3. The program resolves metadata such as title, artists, album, duration, artwork, and release date.
4. The program finds a matching audio source.
5. The program downloads the audio.
6. The program converts and tags the file.
7. The user can listen to the saved music offline.

Right now, only steps 1 through 3 are partly implemented, and only single-track metadata lookup is supported.

## Running Locally

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

Run the current command-line prototype:

```powershell
python src/main.py
```

Then paste a Spotify track link when prompted.

## Basic Test Script

There is a simple test script that checks the main metadata resolver statuses:

```powershell
python test/test.py
```

It currently checks:

- A valid Spotify track.
- Invalid non-Spotify input.
- An unsupported album link.
- A bad track ID.

## Project Direction

The next useful milestones are:

1. Keep improving Spotify link parsing and metadata resolution.
2. Add a reliable search step for finding matching audio.
3. Add download support with `yt-dlp`.
4. Add metadata tagging with `mutagen`.
5. Build the desktop interface once the core flow works.
