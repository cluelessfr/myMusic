def score_candidate(metadata, candidate):
    title = metadata['title']
    artists = metadata['artists']
    candidate_title = candidate['title']

    if candidate_title is None:
        candidate_title = ""

    score = 0
    lower_candidate_title = candidate_title.lower()
    lower_title = title.lower()
    metadata_text = lower_title

    for artist in artists:
        metadata_text += " " + artist.lower()

    bad_words = [
        "karaoke",
        "cover",
        "sped up",
        "nightcore",
        "google translate",
        "made popular by",
        "reaction",
        "react to",
        "podcast",
        "interview",
        "review",
        "deep dive",
        "video essay",
        "story behind",
        "documentary",
        "masked singer",
        "live performance",
        "live from",
        "live at",
        "parody",
    ]

    if lower_title in lower_candidate_title:
        score += 1

    if lower_candidate_title == lower_title:
        score += 2

    for artist in artists:
        lower_artist = artist.lower()
        if lower_artist in lower_candidate_title:
            score += 1

        if f"{lower_artist} - {lower_title}" in lower_candidate_title:
            score += 2

        if f"{lower_title} - {lower_artist}" in lower_candidate_title:
            score += 2

    if "official audio" in lower_candidate_title:
        score += 1

    for word in bad_words:
        if word in lower_candidate_title and word not in metadata_text:
            score -= 2

    return score


def rank_candidates(metadata, candidates):
    return sorted(candidates, key=lambda candidate: score_candidate(metadata, candidate), reverse=True)
