from django.urls import reverse


def compute_artists_links(album):
    all_artists = album.artists.all()
    artists = [{'name': artist.name, 'mbid': artist.mbid} for artist in all_artists]
    artists_links = ["<a href='{}'>{}</a>".format(reverse('albums:artist', args=[artist['mbid']]), artist['name']) for
                     artist in artists]
    return ', '.join(artists_links)
