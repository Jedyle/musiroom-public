from django.urls import reverse
from django.conf import settings

from albums.scraper import ParseAlbum, ParseCover, ParseArtist


def compute_artists_links(album):
    all_artists = album.artists.all()
    artists = [{"name": artist.name, "mbid": artist.mbid} for artist in all_artists]
    artists_links = [
        "<a href='{}'>{}</a>".format(
            reverse("albums:artist", args=[artist["mbid"]]), artist["name"]
        )
        for artist in artists
    ]
    return ", ".join(artists_links)


# TODO : refactor and remove local imports


def load_album_if_not_exists(mbid):
    from albums.models import Album, Genre, AlbumGenre

    parser = ParseAlbum(mbid)
    if not parser.load():
        return None, None
    else:
        parse_cover = ParseCover(mbid)
        if parse_cover.load():
            cover_url = parse_cover.get_cover_small()
        else:
            cover_url = ""
        album = Album(mbid=mbid)
        album.title = parser.get_title()
        album.release_date = parser.get_release_date()
        album.cover = cover_url
        album.album_type = parser.get_type()
        album.tracks = parser.get_track_list()
        album.save()
        authors = get_artists_in_db(parser.get_artists())
        for author in authors:
            album.artists.add(author)
            tags = parser.get_tags()
            for tag in tags:
                genres = Genre.objects.filter(
                    name__iexact=tag.lower().replace("-", " ")
                )
                if genres.count() > 0:
                    genre = genres[0]
                    album_genre, created = AlbumGenre.objects.get_or_create(
                        album=album, genre=genre
                    )
                    if created:
                        album_genre.num_vote_up = 1
                        album_genre.save()

        album.save()
        artists = [{"name": author.name, "mbid": author.mbid} for author in authors]
        return album, artists


def create_artist_from_mbid(mbid, page, search):
    from albums.models import Artist

    parser = ParseArtist(mbid, page=page, name=search)
    if parser.load():
        artist = Artist.objects.create(mbid=mbid, name=parser.get_name())
        return artist
    return None


def get_artists_in_db(artist_dict):
    from albums.models import Artist

    artists = []
    for artist_elt in artist_dict:
        try:
            artist = Artist.objects.get(mbid=artist_elt["mbid"])
            artists.append(artist)
        except Artist.DoesNotExist:
            artist = Artist.objects.create(
                mbid=artist_elt["mbid"], name=artist_elt["name"]
            )
            artists.append(artist)
    return artists
