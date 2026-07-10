import re

def title_normalizer(title):
    lower_title = title.lower()

    replace_text = r'!|"|\#|\$|%|\&|\'|\(|\)|\*|\+|,|\-|\.|\/|:|;|<|=|>|\?|@|\[|\\|\]|\^|_|`|\{|\|\}|\~'
    punc_replaced = re.sub(replace_text, " ", lower_title)

    normalized_title = " ".join(punc_replaced.split())

    return normalized_title


def spotify_base_title(input_title):
    parenthesis_remove = r"\s*\((?:feat\.?|ft\.?|featuring)\s+[^)]*\)"
    feat_titles = r"\s*(?:[;,-]\s*)?(?:feat\.?|ft\.?|featuring)\s+.*$"
    lower_input = input_title.lower()
    parenthesis_removed = re.sub(parenthesis_remove, "", lower_input)
    feat_removed = re.sub(feat_titles, "", parenthesis_removed)

    feat_removed_title = " ".join(feat_removed.split())

    normalized_title = title_normalizer(feat_removed_title)

    return normalized_title


def score_candidate(metadata, candidate):
    title = metadata['title']
    artists = metadata['artists']
    candidate_title = candidate['title']

    if candidate_title is None:
        candidate_title = ""

    score = 0
    lower_candidate_title = candidate_title.lower()
    normalized_candidate = title_normalizer(candidate_title)
    lower_title = title.lower()
    normalized_title = spotify_base_title(title)
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

    if normalized_title in normalized_candidate:
        score += 1

    if lower_candidate_title == lower_title:
        score += 1
        if candidate["source"] == "youtube_music":
            score += 2

    for artist in artists:
        lower_artist = artist.lower()
        if lower_artist in lower_candidate_title:
            score += 1

        if f"{lower_artist} - {lower_title}" in lower_candidate_title:
            score += 1

        if f"{lower_title} - {lower_artist}" in lower_candidate_title:
            score += 1

    if "official audio" in lower_candidate_title:
        score += 1

    for word in bad_words:
        if word in lower_candidate_title and word not in metadata_text:
            score -= 2

    return score


def rank_candidates(metadata, candidates):
    return sorted(candidates, key=lambda candidate: score_candidate(metadata, candidate), reverse=True)

def score_candidates(metadata, candidates):
    scored_candidates = []

    for candidate in candidates:
        score = score_candidate(metadata, candidate)
        candidate_group = [candidate, score]
        scored_candidates.append(candidate_group)

    sorted_list = sorted(scored_candidates, key=lambda candidate_in_list: candidate_in_list[1], reverse=True)

    return sorted_list
