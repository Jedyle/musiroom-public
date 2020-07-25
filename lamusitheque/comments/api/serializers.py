from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from comments.models import Comment
from comments.settings import get_allowed_comment_targets
from user_profile.api.serializers import UserProfileSerializer
from lamusitheque.apiutils.mixins import VoteSerializerMixin

class ReadCommentSerializer(serializers.ModelSerializer, VoteSerializerMixin):
    user = UserProfileSerializer(read_only=True)
    children = serializers.ListField(child=RecursiveField())
    comment = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'comment', 'submit_date', 'children', 'is_removed', 'content_type', 'object_pk',
                  'vote_score', 'num_vote_up', 'num_vote_down', 'user_vote')

    def get_comment(self, obj):
        if obj.is_removed:
            return None
        return obj.comment


class WriteCommentSerializer(serializers.ModelSerializer, VoteSerializerMixin):
    user = UserProfileSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), allow_null=True)
    content_type = serializers.SlugRelatedField(slug_field="model", queryset=ContentType.objects.all())

    class Meta:
        model = Comment
        fields = ('id', 'comment', 'submit_date', 'parent', 'content_type', 'object_pk',
                  'vote_score', 'num_vote_up', 'num_vote_down', 'user', 'user_vote')
        read_only_fields = ('id', 'vote_score', 'num_vote_up', 'num_vote_down')

    def validate_content_type(self, value):
        model_class = value.model_class()
        allowed_classes = get_allowed_comment_targets()
        if model_class not in allowed_classes:
            raise serializers.ValidationError("Unauthorized content object for a comment")
        return value


class UpdateCommentSerializer(serializers.ModelSerializer, VoteSerializerMixin):

    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'user', 'comment', 'submit_date', 'is_removed', 'content_type', 'object_pk',
                  'vote_score', 'num_vote_up', 'num_vote_down', 'user_vote')
        read_only_fields = ('id', 'user', 'submit_date', 'is_removed', 'content_type', 'object_pk',
                            'vote_score', 'num_vote_up', 'num_vote_down')
