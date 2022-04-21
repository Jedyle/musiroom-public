from django.contrib.contenttypes.models import ContentType
from generic_relations.relations import GenericRelatedField
from rest_framework import serializers

from user_profile.api.short_serializers import ShortUserSerializer
from albums.api.serializers import ShortAlbumSerializer, ShortArtistSerializer
from albums.models import Album, Artist
from discussions.models import Discussion
from lamusitheque.apiutils.mixins import VoteSerializerMixin


class DiscussionMixin(serializers.Serializer):
    content_object = GenericRelatedField(
        {Album: ShortAlbumSerializer(), Artist: ShortArtistSerializer()}, read_only=True
    )

    comment_count = serializers.SerializerMethodField()
    user = ShortUserSerializer(read_only=True)

    def get_comment_count(self, discussion):
        return discussion.comments.count()


class DiscussionSerializer(
    serializers.ModelSerializer, DiscussionMixin, VoteSerializerMixin
):
    content_type = serializers.SlugRelatedField(
        slug_field="model", queryset=ContentType.objects.all(), allow_null=True
    )

    object_id = serializers.IntegerField(min_value=0)

    class Meta:
        model = Discussion
        fields = "__all__"
        read_only_fields = (
            "user",
            "vote_score",
            "num_vote_up",
            "num_vote_down",
            "content_object",
        )

    def validate_content_type(self, data):
        ALLOWED_DISCUSSION_MODELS = [Album, Artist]
        ALLOWED_DISCUSSION_CONTENT_TYPES = ContentType.objects.get_for_models(
            *ALLOWED_DISCUSSION_MODELS
        ).values()
        if (data is not None) and (data not in ALLOWED_DISCUSSION_CONTENT_TYPES):
            raise serializers.ValidationError(
                "You cannot create a discussion about this model"
            )
        return data

    def validate(self, data):
        super().validate(data)

        if data.get("content_type") is not None:
            target = (
                data["content_type"].model_class().objects.filter(id=data["object_id"])
            )
            if not target.exists():
                raise serializers.ValidationError("The target object does not exist")
        return data


class DiscussionUpdateSerializer(
    serializers.ModelSerializer, DiscussionMixin, VoteSerializerMixin
):

    content_type = serializers.SlugRelatedField(slug_field="model", read_only=True)

    class Meta:
        model = Discussion
        fields = "__all__"
        read_only_fields = (
            "user",
            "vote_score",
            "num_vote_up",
            "num_vote_down",
            "content_object",
            "content_type",
            "object_id",
            "created",
            "modified",
        )
