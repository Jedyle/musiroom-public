from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.db import transaction
from pinax.badges.models import BadgeAward
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views, mixins, generics, viewsets

from lamusitheque.apiutils.viewsets import ListRetrieveViewset
from user_profile.api.filters import ProfileFilter, NotificationFilter
from user_profile.api.serializers import (
    CreateUserSerializer,
    PasswordConfirmSerializer,
    PublicProfileSerializer,
    NotificationSerializer,
    BadgeSerializer,
    ProfileAvatarSerializer,
)
from django.contrib.sites.shortcuts import get_current_site
from user_profile.tasks import send_user_activation_email
from user_profile.models import Profile
from user_profile.tokens import profile_activation_token
from lists.api.serializers import ListItemSerializer


class RegisterUserView(generics.CreateAPIView):
    """
    Registers a user a sends him a confirmation email
    """

    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = CreateUserSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
            # mail must be sent only after user is successfully added in database
            transaction.on_commit(
                lambda: send_user_activation_email.delay(user.username)
            )
        return Response(
            {"message": "A confirmation email has been sent.", **serializer.data},
            status=status.HTTP_201_CREATED,
        )


class ActivateProfileView(views.APIView):
    """
    Checks an user_profile activation link sent by email after registration
    """

    def post(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and profile_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"message": "Registration completed"}, status=status.HTTP_202_ACCEPTED
            )
        return Response(
            {"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
        )


class ResendConfirmationLinkView(views.APIView):
    """
    Resends an activation email
    """

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        if request.user.is_authenticated and request.user != user:
            return Response(
                {"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN
            )
        if user.is_active:
            return Response(
                {"This user is already active !"}, status=status.HTTP_400_BAD_REQUEST
            )
        send_user_activation_email.delay(get_current_site(request).pk, user.username)
        return Response(
            {
                "message": "A confirmation email has been sent.",
                **CreateUserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class UpdateAvatarView(generics.UpdateAPIView):

    serializer_class = ProfileAvatarSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request):
        serializer = ProfileAvatarSerializer(request.user.profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DestroyProfileView(generics.CreateAPIView):

    serializer_class = PasswordConfirmSerializer

    def create(self, request):
        """
        This method actually DELETES the current user's user_profile.
        We chose a post request to respect the convention that DELETE should not have a body.
        """
        user = request.user
        password_serializer = PasswordConfirmSerializer(data=request.data)
        password_serializer.is_valid(raise_exception=True)
        if user.check_password(password_serializer.data["password"]):
            # do not actually deletes an user_profile, but sets its state to inactive
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
        )


class ProfileViewset(ListRetrieveViewset):

    """
    Consult user profiles.
    """

    serializer_class = PublicProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = "user__username"
    filter_class = ProfileFilter

    @action(detail=True, methods=["get"])
    def top(self, request, **kwargs):
        user = self.get_object()
        serializer = ListItemSerializer(user.top_albums.listitem_set, many=True)
        return Response(
            {"id": user.top_albums.id, "items": serializer.data},
            status=status.HTTP_200_OK,
        )


class NotificationViewset(viewsets.GenericViewSet, mixins.ListModelMixin):

    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = NotificationFilter

    def get_queryset(self):
        for el in self.request.user.notifications.all():
            print(el.actor, el.target)
        return self.request.user.notifications.all()

    @action(detail=False, methods=["get"])
    def unread_count(self, request, **kwargs):
        return Response({"unread": self.request.user.notifications.unread().count()})

    @action(detail=False, methods=["put"])
    def mark_all_as_read(self, request, **kwargs):
        request.user.notifications.unread().mark_all_as_read()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class BadgesViewset(viewsets.GenericViewSet, mixins.ListModelMixin):

    serializer_class = BadgeSerializer

    def get_queryset(self):
        username = self.kwargs["users_user__username"]
        return BadgeAward.objects.filter(user__username=username)
