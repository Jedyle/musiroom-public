from rest_framework import serializers

from actstream.models import Action


class ActionSerializer(serializers.ModelSerializer):
    actor_content_type = serializers.SlugRelatedField(slug_field="model", read_only=True)
    actor = serializers.SerializerMethodField()

    target_content_type = serializers.SlugRelatedField(slug_field="model", read_only=True)
    target = serializers.SerializerMethodField()

    action_object_content_type = serializers.SlugRelatedField(slug_field="model", read_only=True)
    action_object = serializers.SerializerMethodField()

    def get_actor(self, obj):
        res = obj.actor
        if res is None:
            return None
        return {
            "name": str(res),
            "url": getattr(res, 'get_absolute_url', lambda: None)()
        }

    def get_target(self, obj):
        res = obj.target
        if res is None:
            return None
        return {
            "name": str(res),
            "url": getattr(res, 'get_absolute_url', lambda: None)()
        }

    def get_action_object(self, obj):
        res = obj.action_object
        if res is None:
            return None
        return {
            "name": str(res),
            "url": getattr(res, 'get_absolute_url', lambda: None)()
        }

    class Meta:
        model = Action
        exclude = ('actor_object_id', 'target_object_id', 'action_object_object_id')
