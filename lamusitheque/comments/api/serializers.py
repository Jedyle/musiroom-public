from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from comments.models import Comment
from comments.settings import get_allowed_comment_targets
from user_profile.api.serializers import UserProfileSerializer


class ReadCommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    children = serializers.SlugRelatedField('id', many=True, read_only=True)
    comment = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'comment', 'submit_date', 'children', 'is_removed', 'content_type', 'object_pk',
                  'vote_score', 'num_vote_up', 'num_vote_down')

    def get_comment(self, obj):
        if obj.is_removed:
            return None
        return obj.comment


class WriteCommentSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), allow_null=True)
    content_type = serializers.SlugRelatedField(slug_field="model", queryset=ContentType.objects.all())

    class Meta:
        model = Comment
        fields = ('comment', 'submit_date', 'parent', 'content_type', 'object_pk',
                  'vote_score', 'num_vote_up', 'num_vote_down')
        read_only_fields = ('vote_score', 'num_vote_up', 'num_vote_down')

    def validate_content_type(self, value):
        model_class = value.model_class()
        allowed_classes = get_allowed_comment_targets()
        if model_class not in allowed_classes:
            raise serializers.ValidationError("Unauthorized content object for a comment")
        return value


class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'user', 'comment', 'submit_date', 'is_removed', 'content_type', 'object_pk',
                  'vote_score', 'num_vote_up', 'num_vote_down')
        read_only_fields = ('id', 'user', 'submit_date', 'is_removed', 'content_type', 'object_pk',
                            'vote_score', 'num_vote_up', 'num_vote_down')
