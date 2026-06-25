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
        "cover",
        "karaoke",
        "sped up",
        "nightcore",
        "live",
        "instrumental",
        "remix",
        "tribute",
        "piano version",
        "google translate",
        "sings",
        "reaction",
        "deep dive",
        "podcast",
        "interview",
        "biography",
        "comparison",
        "episode",
        "analysis",
        "autobiography",
        "documentary",
        "react to",
        "performs",
        "performance",
        "stadium",
        "rock gala",
        "acoustic version",
        "discusses",
        "demo",
        "ending on a high note",
        "ep.",
        "made popular by",
        "vocal version",
        "masked singer",
        "panel sing",
        "actually sound",
        "students perform",
        "school of rock",
        "parody",
        "knockouts",
        "song of the week",
        "top 3 hits",
        "unplugged",
        "story behind",
        "maga edition",
        "discuss",
        "acappella",
        "mix lyrics",
        "highlights",
        "cult toy",
        "reveals",
        "avoided prison",
        "feels about",
        "collaborating",
        "reinvigorated",
        "sing-along",
        "netflix",
        "film version",
        "alternate mix",
        "acoustic blues",
        "audiophile quality",
        "extended mix",
        "lego",
        "(clean",
        "super clean",
        "vietsub",
        "metaphysics",
        "honest about",
        "review",
        "quiet on set",
        "lyrics (mix",
        "played this song",
        "fear stopped",
        "acoustic)",
        "live from",
        "fascinating world",
        "tomorrowland",
        "25 years of",
        "club mix",
        "tarot reading",
        "rock history",
        "unexpected connection",
        "famous single take",
        "motion picture soundtrack",
        "from love to legacy",
        "musiclegends",
        "pophistory",
        "timelessjoy",
        "internal war",
        "real drama",
        "full band history",
        "shirley bassey show",
        "response to",
        "we didn't care",
        "shocking truth",
        "real meaning behind",
        "true story",
        "premio",
        "vanguard",
        "biographie",
        "releasing",
        "solo album",
        "born on",
        "sonisphere",
        "proshot",
        "conspiraci",
        "retrospective",
        "discography drama",
        "background vocals",
        "goosebumps",
        "mind blowing facts",
        "take 9",
        "take 1",
        "full song video",
        "impersonator",
        "biopic",
        "grossed",
        "flop",
    ]

    if lower_title in lower_candidate_title:
        score += 1

    for artist in artists:
        lower_artist = artist.lower()
        if lower_artist in lower_candidate_title:
            score += 1

    if "official audio" in lower_candidate_title:
        score += 1

    for word in bad_words:
        if word in lower_candidate_title and word not in metadata_text:
            score -= 2

    return score


def rank_candidates(metadata, candidates):
    return sorted(candidates, key=lambda candidate: score_candidate(metadata, candidate), reverse=True)
