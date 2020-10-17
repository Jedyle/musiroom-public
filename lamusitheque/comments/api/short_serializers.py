from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from comments.models import Comment


class ShortCommentSerializer(serializers.ModelSerializer):

    content_type = serializers.SlugRelatedField(
        slug_field="model", queryset=ContentType.objects.all()
    )

    class Meta:
        model = Comment
        fields = ("id", "content_type", "object_pk", "comment")
