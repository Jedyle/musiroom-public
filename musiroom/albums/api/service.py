from albums.models import Album
from albums.api.serializers import AlbumSerializer

def add_album_details(discography, request):
    """
    Takes the result of ParseArtist.get_discography and add whatever album data we cannot getText from our database (rating, id, ...)
    """
    all_mbids = [item["mbid"] for release_type in discography for item in release_type["items"]]
    albums = Album.objects.filter(mbid__in=all_mbids)
    results = {}
    for album in albums:
        results[album.mbid] = album

    for release_type in discography:
        for item in release_type["items"]:
            item["details"] = AlbumSerializer(results[item["mbid"]], context={"request": request}).data if item["mbid"] in results else None
    return discography

