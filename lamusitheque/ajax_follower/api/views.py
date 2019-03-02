from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from notifications.signals import notify
from rest_framework import views, permissions, status, mixins, viewsets
from rest_framework.response import Response

from ajax_follower.api.serializers import FollowSerializer
from friendship.models import Follow
from user_profile.api.serializers import PublicProfileSerializer
from user_profile.models import Profile
from user_profile.utils import notifications_alike


class FollowView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        """
        Toggles a following relationship between request.user and a user
        """

        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("user")
        user = get_object_or_404(User, username=username)
        if user == request.user:
            return Response({
                "message": "Users cannot follow themselves"
            }, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.follows(request.user, user):
            # delete follower
            Follow.objects.remove_follower(request.user, user)
            # delete notifications like 'user x follows you'
            notifications_alike(user.notifications, actor=user, verb="follows you").delete()
        else:
            # add follower
            Follow.objects.add_follower(request.user, user)
            notify.send(sender=user, recipient=user, verb="follows you")
        return Response({
            "user": user.username,
            "is_followed": Follow.objects.follows(request.user, user)
        })


class FollowersViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = PublicProfileSerializer

    def get_queryset(self):
        username = self.kwargs['users_user__username']
        user = get_object_or_404(User, username=username)
        return Profile.objects.filter(user__in=Follow.objects.followers(user=user))


class FolloweesViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = PublicProfileSerializer

    def get_queryset(self):
        username = self.kwargs['users_user__username']
        user = get_object_or_404(User, username=username)
        return Profile.objects.filter(user__in=Follow.objects.following(user=user))
