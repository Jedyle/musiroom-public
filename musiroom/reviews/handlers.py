from django.db.models.signals import post_save
from django.dispatch import receiver

from actstream import action
from reviews.models import Review
from star_ratings.models import UserRating


@receiver(post_save, sender=Review)
def save_review_handler(sender, instance, created, **kwargs):
    if created:
        action.send(instance.rating.user,
                    verb='wrote a review',
                    action_object=instance)


@receiver(post_save, sender=UserRating)
def save_rating_handler(sender, instance, created, **kwargs):
    action.send(instance.user, verb='gave ' + str(instance.score) + ' to',
                action_object=instance.rating.content_object)
