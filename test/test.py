from src.metadata_resolver import *

valid_track = "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
invalid_input = "not spotify"
unsupported_album = "https://open.spotify.com/album/6TJmQnO44YE5BtTxH8pop1"
bad_track_id = "https://open.spotify.com/track/0000000000000000000000"

valid_result = validate_link_get_metadata(valid_track)
invalid_result = validate_link_get_metadata(invalid_input)
unsupported_album_result = validate_link_get_metadata(unsupported_album)
bad_track_result = validate_link_get_metadata(bad_track_id)

print("Expected result: enriched      Achieved result: ", valid_result["status"])
print("Expected result: invalid       Achieved result: ", invalid_result["status"])
print("Expected result: unsupported   Achieved result: ", unsupported_album_result["status"])
print("Expected result: failed        Achieved result: ", bad_track_result["status"])

