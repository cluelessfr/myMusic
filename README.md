# myMusic

A music utility for saving songs as MP3 files and listening to them offline.

## Current status

This project is just being started, so there are no new features yet. This README will update, along with a changelog, as I update this project and new features get added. 

## How the project Works

1. The user pastes in a link to a Spotify track or playlist
2. The program uses the Spotify API to get the song details (Song name, Artist, etc.)
3. The program then uses the YouTube API to find videos of the song(s)
4. YT-DLP then downloads the video onto the user's computer to the directory they select
5. Then FFMPEG adds the metadata onto the song file, and converts it into the proper file type
6. The user can now listen to their music offline 
