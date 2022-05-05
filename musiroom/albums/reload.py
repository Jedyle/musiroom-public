import time

from albums.models import Album
from albums.scraper import ParseAlbum, ParseCover


def reload_tracks(mbid):
    album = Album.objects.get(mbid=mbid)
    parser = ParseAlbum(mbid)
    if not parser.load():
        return
    else:
        album.tracks = parser.get_track_list()
        album.save()
        return


def reload_covers(mbid, override=False):
    album = Album.objects.get(mbid=mbid)
    if album.cover == "" or override:
        parse_cover = ParseCover(mbid)
        if parse_cover.load():
            album.cover = parse_cover.get_cover_small()
            album.media_cover = None
            album.save()

            
def reload_all(method=reload_tracks):
    start = time.time()
    albums = Album.objects.all()
    for album in albums:
        method(album.mbid)
    end = time.time()
    return end - start
