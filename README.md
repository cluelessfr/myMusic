# myMusic

myMusic is a Windows desktop app that uses a Spotify track link to find a matching song and save it as a local MP3 file.

![myMusic desktop app screenshot](docs/screenshots/myMusic-gui.png)

Paste a Spotify track link, preview the song details, then download the matched track as an MP3.

## Platform Support

| Platform | Status | Download |
| --- | --- | --- |
| Windows | Supported | `myMusic-v1.0.2-windows-setup.exe` from GitHub Releases |
| macOS | Not supported yet | N/A |
| Linux | Not supported yet | N/A |

## Download And Install

The recommended Windows download is the installer from the GitHub Releases page.

You do not need to install Python, project dependencies, FFmpeg, or developer tools. The installer includes the executable and the files the app needs to run.

1. Open the myMusic Releases page: https://github.com/cluelessfr/myMusic/releases
2. Download `myMusic-v1.0.2-windows-setup.exe`.
3. Open the downloaded installer.
4. Follow the setup steps.
5. Launch myMusic from the installer, Start Menu, or desktop shortcut if you selected one.

The release may also include a Windows zip file. Use the installer unless you specifically want the portable zip version. If you use the zip, extract it first and keep the extracted folder together.

## Windows SmartScreen

Windows may show a SmartScreen warning because myMusic is a new unsigned app from an independent developer. This does not automatically mean the app is unsafe. It means Windows does not recognize the app yet because it is not code-signed with a trusted certificate and has not built a download reputation.

Only bypass SmartScreen if you downloaded myMusic from the official GitHub Releases page.

To continue:

1. Click **More info**.
2. Check that the app name is `myMusic`.
3. Click **Run anyway**.

## How To Use myMusic

1. Open myMusic.
2. Paste a Spotify track link into the text box.
3. Click **Preview Song Details**.
4. Check that the title, artist, and album look right.
5. Click **Download**.
6. Open the finished MP3 from your selected output folder.

## Known Issue: YouTube Bot Check

myMusic uses YouTube Music through yt-dlp to find and download matching audio. Sometimes YouTube blocks automated requests and shows a "Sign in to confirm you're not a bot" error.

This is a YouTube-side anti-bot check, not an installation problem with myMusic. If it happens, try again later or from a different network. This version does not ask for your YouTube account or browser cookies.

## Uninstall

The Windows installer includes an uninstaller.

You can uninstall myMusic from:

- Windows Settings > Apps > Installed apps.
- The Start Menu entry named **Uninstall myMusic**.

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

The GitHub Release page only hosts the download. After you download and run myMusic, the lookup, download, conversion, tagging, and file saving happen locally on your machine.

```text
GitHub Release page -> download installer -> install myMusic -> run myMusic -> MP3 saved locally
```

## Not Finished Yet

- Playlist downloads.
- Album downloads.
- Choosing between multiple YouTube Music matches.
- Choosing a custom download folder.
- Embedded cover artwork.
- Better progress messages while downloading.
