from django.db.models.signals import post_save
from django.dispatch import receiver

from actstream import action
from reviews.models import Review
from star_ratings.models import UserRating


RATE_LABEL = "rate"
REVIEW_LABEL = "review"


@receiver(post_save, sender=Review)
def save_review_handler(sender, instance, created, **kwargs):
    if created:
        action.send(
            instance.rating.user,
            verb="wrote a review",
            action_object=instance,
            label=REVIEW_LABEL,
        )


@receiver(post_save, sender=UserRating)
def save_rating_handler(sender, instance, created, **kwargs):
    if instance.score:
        action.send(
            instance.user,
            verb="gave " + str(instance.score) + " to",
            action_object=instance.rating.content_object,
            label=RATE_LABEL,
        )
    elif instance.is_in_collection:
        action.send(
            instance.user,
            verb="added an album to his collection : ",
            action_object=instance.rating.content_object,
            label=RATE_LABEL,
        )
    elif instance.is_interested:
        action.send(
            instance.user,
            verb="wants to listen to",
            action_object=instance.rating.content_object,
            label=RATE_LABEL,
        )
