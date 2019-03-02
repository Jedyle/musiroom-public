from django.contrib.contenttypes.models import ContentType

from actstream.actions import follow
from friendship.models import Follow as FriendshipFollow


def notifications_alike(queryset, actor, verb, target=None):
    """
    Detects notifications in queryset with same actor, verb and target as provided.
    Used for instance when a notification is sent, to delete similar others (ex : 'user follows you').
    """
    if target is not None:
        return queryset.filter(actor_content_type=ContentType.objects.get_for_model(actor), actor_object_id=actor.id,
                               verb=verb, target_content_type=ContentType.objects.get_for_model(target),
                               target_object_id=target.id)
    else:
        return queryset.filter(actor_content_type=ContentType.objects.get_for_model(actor), actor_object_id=actor.id,
                               verb=verb, target_content_type=None, target_object_id=None)


def normalize_follow_friendship_activity():
    """
    Create one activity/follow instance for each friendship/follow instance
    """
    friendship_follows = FriendshipFollow.objects.all()
    for elt in friendship_follows:
        follower = elt.follower
        followee = elt.followee
        follow(follower, followee)
