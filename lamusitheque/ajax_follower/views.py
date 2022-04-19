from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse, HttpResponseNotFound
from django.urls import reverse
from notifications.signals import notify

from user_profile.utils import notifications_alike
from friendship.models import Follow


# Create your views here.


def follow_notification(user):
    return (
        "<a href={}>{}</a> ".format(
            reverse("user_profile", args=[user.username]), user.username
        )
        + "vous suit"
    )


@login_required
def ajax_follow(request):
    if request.method == "POST":
        follow = request.POST["follow"]
        user_to_follow = User.objects.get(username=request.POST["user_to_follow"])
        user = request.user
        if follow == "true":
            if not Follow.objects.follows(user, user_to_follow):
                Follow.objects.add_follower(user, user_to_follow)
                notify.send(
                    sender=user,
                    recipient=user_to_follow,
                    verb="follows you",
                    to_str=follow_notification(request.user),
                )
        elif follow == "false":
            if Follow.objects.follows(user, user_to_follow):
                Follow.objects.remove_follower(user, user_to_follow)
                notifications_alike(
                    user_to_follow.notifications, actor=user, verb="follows you"
                ).delete()
        return JsonResponse({})
    return HttpResponseNotFound()


def make_json_contact_list(querydict, user=None):
    contact_list = []
    for f in querydict:
        contact = {}
        contact["username"] = f.username
        contact["profile_url"] = reverse("user_profile", args=[f.username])
        contact["avatar"] = f.profile.get_avatar()

        if (user is not None) and Follow.objects.follows(user, f):
            contact["follows"] = True
        elif user is not None:
            contact["follows"] = False
        else:
            contact["follows"] = None

        if user == f:
            contact["is_self"] = True
        else:
            contact["is_self"] = False

        contact_list.append(contact)

    return contact_list
