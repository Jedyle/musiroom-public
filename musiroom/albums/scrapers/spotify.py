import spotipy
import musicbrainzngs
from spotipy.oauth2 import SpotifyClientCredentials


USER_AGENT = "mb-spotify-bindings", "1.0"


class MBToSpotify:
    def __init__(self):
        self.spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials()
        )
        musicbrainzngs.set_useragent(*USER_AGENT)

    def find_album(self, mbid):
        mb_search = musicbrainzngs.get_release_group_by_id(
            mbid, includes=["artists"]
        )
        mb_album = mb_search["release-group"]["title"]
        mb_artists = [
            el["artist"]["name"] for el in mb_search["release-group"]["artist-credit"] if "artist" in el
        ]
        spotify_search = self.spotify.search(
            f"{mb_album} {' '.join(mb_artists)}", type="album"
        )
        if len(spotify_search["albums"]["items"]) >= 1:
            return spotify_search["albums"]["items"][0]["external_urls"]["spotify"]
        # empty string will fill the column, so that API is not called again
        return ""
