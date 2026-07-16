import unittest
from src.integrations.parse_protocol_url import parse_protocol_url


class ProtocolUrlTests(unittest.TestCase):
    def test_parse_protocol_url(self):
        protocol_url = "mymusic://download?uri=spotify%3Atrack%3A4uLU6hMCjMI75M1A2tKUQC"
        expected_uri = "spotify:track:4uLU6hMCjMI75M1A2tKUQC"

        actual_uri = parse_protocol_url(protocol_url)

        self.assertEqual(expected_uri, actual_uri)

    def test_missing_uri_returns_none(self):
        protocol_url = "mymusic://download"

        actual_uri = parse_protocol_url(protocol_url)

        self.assertIsNone(actual_uri)

    def test_valid_playlist_url(self):
        protocol_url = "mymusic://download?uri=spotify%3Aplaylist%3A37i9dQZF1DXcBWIGoYBM5M"
        expected_uri = "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"

        actual_uri = parse_protocol_url(protocol_url)

        self.assertEqual(expected_uri, actual_uri)

    def test_valid_album_url(self):
        protocol_url = "mymusic://download?uri=spotify%3Aalbum%3A6TJmQnO44YE5BtTxH8pop1"
        expected_uri = "spotify:album:6TJmQnO44YE5BtTxH8pop1"

        actual_uri = parse_protocol_url(protocol_url)

        self.assertEqual(expected_uri, actual_uri)
