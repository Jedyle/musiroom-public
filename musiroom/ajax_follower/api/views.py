from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from notifications.signals import notify
from rest_framework import views, permissions, status, mixins, viewsets, generics
from rest_framework.response import Response

from ajax_follower.api.serializers import FollowSerializer
from friendship.models import Follow
from user_profile.api.serializers import PublicProfileSerializer
from user_profile.models import Profile
from user_profile.utils import notifications_alike


class FollowView(generics.CreateAPIView):

    """
    Updates a follower/following relationship
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FollowSerializer

    def post(self, request):

        """
        Toggles a following relationship between the logged in user and another user
        """

        serializer = self.get_serializer(data=request.data)
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
            notifications_alike(user.notifications, actor=request.user, verb="follows you").delete()
        else:
            # add follower
            Follow.objects.add_follower(request.user, user)
            notify.send(sender=request.user, recipient=user, verb="follows you")
        return Response({
            "user": user.username,
            "is_followed": Follow.objects.follows(request.user, user)
        })


class FollowersViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = PublicProfileSerializer
    pagination_class = None

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['users_user__username'])
        username_to_retrieve = self.request.query_params.get('username')
        queryset = Profile.objects.filter(user__in=Follow.objects.followers(user=user))
        if username_to_retrieve:
            queryset = queryset.filter(user__username = username_to_retrieve)
        return queryset


class FolloweesViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = PublicProfileSerializer
    pagination_class = None
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['users_user__username'])
        username_to_retrieve = self.request.query_params.get('username')        
        queryset = Profile.objects.filter(user__in=Follow.objects.following(user=user))
        if username_to_retrieve:
            queryset =  queryset.filter(user__username = username_to_retrieve)
        return queryset
