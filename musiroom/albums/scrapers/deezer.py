import deezer
import musicbrainzngs


USER_AGENT = "mb-spotify-bindings", "1.0"


class MBToDeezer:
    def __init__(self):
        self.deezer = deezer.Client()
        musicbrainzngs.set_useragent(*USER_AGENT)

    def find_album(self, mbid):
        mb_search = musicbrainzngs.get_release_group_by_id(mbid, includes=["artists"])
        mb_album = mb_search["release-group"]["title"]
        mb_artists = [
            el["artist"]["name"]
            for el in mb_search["release-group"]["artist-credit"]
            if "artist" in el
        ]

        deezer_search = self.deezer.search_albums(f"{mb_album} {' '.join(mb_artists)}")
        for album in deezer_search:
            check_album_similar = (album.title.lower() in mb_album.lower()) or (
                mb_album.lower() in album.title.lower()
            )
            check_artist_similar = any(
                [
                    (
                        (album.artist.name.lower() in artist.lower())
                        or (artist.lower() in album.artist.name.lower())
                    )
                    for artist in mb_artists
                ]
            )
            if check_album_similar and check_artist_similar:
                return album.link
        return ""
