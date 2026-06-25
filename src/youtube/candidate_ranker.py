def score_candidate(metadata, candidate):
    title = metadata['title']
    artists = metadata['artists']
    candidate_title = candidate['title']

    if candidate_title is None:
        candidate_title = ""

    score = 0
    lower_candidate_title = candidate_title.lower()
    lower_title = title.lower()
    bad_words = ["cover", "karaoke", "sped up", "nightcore", "live", "instrumental", "remix"]

    if lower_title in lower_candidate_title:
        score += 1

    for artist in artists:
        lower_artist = artist.lower()
        if lower_artist in lower_candidate_title:
            score += 1

    if "official audio" in lower_candidate_title:
        score += 1

    for word in bad_words:
        if word in lower_candidate_title:
            score -= 2

    return score


def rank_candidates(metadata, candidates):
    return sorted(candidates, key=lambda candidate: score_candidate(metadata, candidate), reverse=True)
