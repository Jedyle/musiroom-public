import pytest

from albums.scraper import ParseArtistPhoto


@pytest.mark.api
class TestParseArtistPhoto:
    def test_ok(self):
        parser = ParseArtistPhoto("f27ec8db-af05-4f36-916e-3d57f91ecf5e")
        parser.load()
        assert (
            parser.get_thumb()
            == "https://commons.wikimedia.org/wiki/Special:Redirect/file/Michael_Jackson_in_1988.jpg"
        )

    def test_returns_empty(self):
        # this artist has no image
        parser = ParseArtistPhoto("16456fed-c9f2-4adf-b6ea-97b648c474d2")
        parser.load()
        assert parser.get_thumb() == ""
