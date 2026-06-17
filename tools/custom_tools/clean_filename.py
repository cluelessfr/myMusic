def clean_filename(filename):
    invalid_characters = ["?", ":", "/", "\\", "\"", "<", ">", "|", "*"]

    for character in invalid_characters:
        filename = filename.replace(character, "_")

    return filename
