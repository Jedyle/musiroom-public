from star_ratings.models import UserRating
from django.contrib.auth.models import User
from django.db.models import Avg, Q

def rating_for_followees(user, album):
    return UserRating.objects.filter( Q(rating__albums = album) & Q(user__followers__follower = user)).aggregate(avg = Avg('score'))['avg'] or 0


def rating_for_followees_list(user, album_list):
    liste = UserRating.objects.filter(Q(rating__albums__in = album_list) & Q(user__followers__follower = user)).values('rating__albums__mbid').annotate(avg = Avg('score'))
    return dict((elt['rating__albums__mbid'], elt['avg']) for elt in liste)
