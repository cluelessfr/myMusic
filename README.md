# myMusic

myMusic is a Windows desktop app that uses a Spotify track link to find a matching song and save it as a local MP3 file.

Paste a Spotify track link, click download, and myMusic saves a tagged MP3 to your computer.

## Download And Run

myMusic is distributed as a Windows zip file from the GitHub Releases page.

You do not need to install Python, project dependencies, FFmpeg, or developer tools. The zip includes the executable and the files the app needs to run.

1. Open the myMusic Releases page: https://github.com/cluelessfr/myMusic/releases
2. Download the latest Windows zip file.
3. Right-click the zip file.
4. Choose **Extract All**.
5. Open the extracted folder.
6. Double-click `myMusic.exe`.
7. Paste a Spotify track link.
8. Click **Download**.
9. Open the finished MP3 from your Downloads folder.

Do not run `myMusic.exe` from inside the zip file. Extract the zip first.

Do not move `myMusic.exe` out of the extracted folder by itself. Keep the extracted folder together so the app can find the files bundled with it.

## What The App Does

For a single Spotify track link, myMusic:

- Reads and cleans the Spotify link.
- Gets the track title, artists, album, and other metadata.
- Searches YouTube Music for a matching result.
- Downloads the selected audio.
- Converts it to MP3.
- Adds basic title, artist, and album tags.
- Saves the MP3 to your Downloads folder.

## Where The Processing Happens

myMusic runs on your computer.

The GitHub Release page only hosts the download. After you download and run `myMusic.exe`, the lookup, download, conversion, tagging, and file saving happen locally on your machine.

```text
GitHub Release page -> download zip -> extract folder -> run myMusic.exe -> MP3 saved locally
```

## Not Finished Yet

- Playlist downloads.
- Album downloads.
- Choosing between multiple YouTube Music matches.
- Choosing a custom download folder.
- Embedded cover artwork.
- Better progress messages while downloading.
