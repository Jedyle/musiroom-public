from rest_framework import serializers


class SearchSerializer(serializers.Serializer):
    model = serializers.ChoiceField(choices=['album', 'artist'])
    method = serializers.ChoiceField(choices=['auto', 'advanced'])
    query = serializers.CharField()
    page = serializers.IntegerField(allow_null=True, required=False)
