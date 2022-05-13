from rest_framework import serializers
from feedback.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    
    class Meta:
        model = Feedback
        fields = "__all__"
        read_only_fields = ('user', )
