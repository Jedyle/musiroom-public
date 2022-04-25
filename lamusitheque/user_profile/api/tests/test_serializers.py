from user_profile.tests.factories import UserFactory

from user_profile.api.serializers import PublicProfileSerializer, ProfileSerializer
from user_profile.api.short_serializers import ShortUserSerializer


class TestPublicProfileSerializer:
    def test_ok(self):
        user = UserFactory()
        serializer = PublicProfileSerializer(instance=user.profile)
        data = serializer.data
        assert data["avatar"] is not None


class TestProfileSerializer:
    def test_ok(self):
        user = UserFactory()
        serializer = ProfileSerializer(instance=user.profile)
        data = serializer.data
        assert data["avatar"] is not None


class TestShortUserSerializer:
    def test_ok(self):
        user = UserFactory()
        serializer = ShortUserSerializer(instance=user)
        data = serializer.data
        assert data["avatar"] is not None
        assert "description" in data
        assert "username" in data
