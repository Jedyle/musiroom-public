from django.db.models.signals import post_save
from django.dispatch import receiver

from albums.models import AlbumGenre, Album, AlbumLinks


@receiver(post_save, sender=AlbumGenre)
def update_genres_handler(sender, instance, **kwargs):

    """
    When an AlbumGenre is updated, recompute the album's genres, i.e the 3 genres with the most likes.
    """

    album = instance.album
    genres = AlbumGenre.objects.filter(album=album, vote_score__gt=0).order_by('-vote_score')
    registered_genres = genres[:3]
    AlbumGenre.objects.filter(id__in=registered_genres).update(is_genre=True)
    AlbumGenre.objects.filter(album=album).exclude(id__in=registered_genres).update(is_genre=False)


@receiver(post_save, sender=Album)
def create_links(sender, instance=None, created=False, **kwargs):
    if created:
        links = AlbumLinks(album=instance)
        links.save()
