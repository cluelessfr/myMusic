from spotify import *

user_text = input("Paste Spotify link: ")

print(f"Link Type: {detect_input_type(user_text)}, URL: {clean_spotify_link(user_text)}")
