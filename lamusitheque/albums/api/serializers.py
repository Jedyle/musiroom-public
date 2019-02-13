from rest_framework import serializers

from albums.models import Genre


class GenreSerializer(serializers.ModelSerializer):

    parent = serializers.SlugRelatedField(many=False, read_only=False, slug_field="slug",
                                          queryset=Genre.objects.all(), allow_null=True)

    class Meta:
        model = Genre
        fields = ("name", "description", "slug", "parent")
        lookup_field = 'slug'
