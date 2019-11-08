from django.contrib.contenttypes.models import ContentType
from generic_relations.relations import GenericRelatedField
from rest_framework import serializers

from user_profile.api.serializers import ShortUserSerializer
from albums.api.serializers import ShortAlbumSerializer, ShortArtistSerializer
from albums.models import Album, Artist
from discussions.models import Discussion
from lamusitheque.apiutils.mixins import VoteSerializerMixin

ALLOWED_DISCUSSION_MODELS = [Album, Artist]
ALLOWED_DISCUSSION_CONTENT_TYPES = ContentType.objects.get_for_models(*ALLOWED_DISCUSSION_MODELS).values()


class DiscussionSerializer(serializers.ModelSerializer, VoteSerializerMixin):
    content_type = serializers.SlugRelatedField(slug_field="model", queryset=ContentType.objects.all(), allow_null=True)

    content_object = GenericRelatedField({
        Album: ShortAlbumSerializer(),
        Artist: ShortArtistSerializer()
    }, read_only=True)

    user = ShortUserSerializer()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Discussion
        fields = '__all__'
        read_only_fields = ('user', 'vote_score', 'num_vote_up', "num_vote_down", "content_object")

    def get_comment_count(self, discussion):
        return discussion.comments.count()

    def validate_content_type(self, data):
        if (data is not None) and (data not in ALLOWED_DISCUSSION_CONTENT_TYPES):
            raise serializers.ValidationError("You cannot create a discussion about this model")
        return data

