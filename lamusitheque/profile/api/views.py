from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import views

from lamusitheque.viewsets import ListRetrieveViewset
from profile.api.filters import ProfileFilter
from profile.api.serializers import CreateUserSerializer, PasswordConfirmSerializer, PublicProfileSerializer
from profile.email import send_activation_email
from profile.models import Profile
from profile.tokens import account_activation_token


class RegisterUserView(generics.CreateAPIView):
    """
    Registers a user a sends him a confirmation email
    """
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        send_activation_email(request, user)
        return Response({
            "message": "A confirmation email has been sent.",
            **serializer.data
        }, status=status.HTTP_201_CREATED)


class ActivateAccountView(views.APIView):
    """
    Checks an account activation link sent by email after registration
    """

    def post(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({
                "message": "Registration completed"
            }, status=status.HTTP_202_ACCEPTED)
        return Response({
            "message": "Invalid token"
        }, status=status.HTTP_400_BAD_REQUEST)


class ResendConfirmationLinkView(views.APIView):
    """
    Resends an activation email
    """

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        if request.user.is_authenticated and request.user != user:
            return Response({
                "message": "Unauthorized"
            }, status=status.HTTP_403_FORBIDDEN)
        if user.is_active:
            return Response({
                "This user is already active !"
            }, status=status.HTTP_400_BAD_REQUEST)
        send_activation_email(request, user)
        return Response({
            "message": "A confirmation email has been sent.",
            **CreateUserSerializer(user).data
        }, status=status.HTTP_200_OK)


class DestroyAccountView(generics.CreateAPIView):

    serializer_class = PasswordConfirmSerializer

    # TODO : change API schema for this route

    def create(self, request):
        """
        This method actually DELETES the current user's account.
        We chose a post request to respect the convention that DELETE should not have a body.
        """
        user = request.user
        password_serializer = PasswordConfirmSerializer(data=request.data)
        password_serializer.is_valid(raise_exception=True)
        if user.check_password(password_serializer.data["password"]):
            # do not actually deletes an account, but sets its state to inactive
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            "message": "Invalid password"
        }, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewset(ListRetrieveViewset):

    """
    Consult user profiles.
    """

    serializer_class = PublicProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = 'user__username'
    filter_class = ProfileFilter
