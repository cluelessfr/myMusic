from src.metadata_providers.metadata_resolver import validate_link_get_metadata
from src.youtube.candidate_ranker import rank_candidates
from unittest.mock import patch

test_cases = [
    {"name": "valid_track", "input": "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC", "expected": "enriched"},
    {"name": "invalid_input", "input": "not spotify", "expected": "invalid"},
    {"name": "unsupported_album", "input": "https://open.spotify.com/album/6TJmQnO44YE5BtTxH8pop1", "expected": "unsupported"},
    {"name": "bad_track_id", "input": "https://open.spotify.com/track/0000000000000000000000", "expected": "failed"},
]

def run_case(case):
    result = validate_link_get_metadata(case["input"])
    status = result["status"]
    print(f"Expected result: {case['expected']}      Achieved result: {status}")


def test_spotify_oembed_fallback():
    fake_oembed_metadata = {
        "title": "Fallback Song",
        "thumbnail_url": "https://example.com/art.jpg",
    }

    with patch("src.metadata_providers.metadata_resolver.scrape_spotify_metadata", return_value=None), \
            patch("src.metadata_providers.metadata_resolver.fetch_spotify_oembed", return_value=fake_oembed_metadata):
        result = validate_link_get_metadata("https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC")

    metadata = result["metadata"]

    assert result["ok"] is True
    assert result["status"] == "enriched"
    assert metadata["source"] == "spotify_oembed"
    assert metadata["title"] == "Fallback Song"

    print(f"oEmbed fallback source: {metadata['source']}      Title: {metadata['title']}")


def test_candidate_ranking():
    fake_metadata = {
        "title": "Blinding Lights",
        "artists": ["The Weeknd"],
    }

    fake_candidates = [
        {"title": "Blinding Lights cover karaoke", "url": "bad"},
        {"title": "Blinding Lights The Weeknd Official Audio", "url": "good"},
    ]

    ranked_candidates = rank_candidates(fake_metadata, fake_candidates)

    print(f"Best Candidate: {ranked_candidates[0]['title']}")

def main():
    for case in test_cases:
        run_case(case)

    test_spotify_oembed_fallback()
    test_candidate_ranking()

if __name__ == "__main__":
    main()
