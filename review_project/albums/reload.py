from albums.models import Album
from albums.scraper import ParseAlbum, ParseCover
import time

def reload_tracks(mbid):
    album = Album.objects.get(mbid = mbid)
    parser = ParseAlbum(mbid)
    if not parser.load():
        return
    else:
        album.tracks = parser.get_track_list()
        album.save()
        return


def reload_all():
    start = time.time()
    albums = Album.objects.all()
    for album in albums:
        reload_tracks(album.mbid)
    end = time.time()
