from rest_framework import serializers

from export_ratings.models import ExportReport


class ExportReadSerializer(serializers.ModelSerializer):

    stats = serializers.JSONField()

    class Meta:
        model = ExportReport
        fields = "__all__"


class ExportDetailSerializer(serializers.ModelSerializer):

    stats = serializers.JSONField()
    new_ratings = serializers.JSONField()
    conflicts = serializers.JSONField()
    not_found = serializers.JSONField()

    class Meta:
        model = ExportReport
        fields = "__all__"

    def get_new_ratings(self, obj):
        return obj.get_new_ratings()


class ExportCreateSerializer(serializers.Serializer):

    sc_url = serializers.URLField(label="Senscritique URL", required=True)
    erase = serializers.BooleanField(label="Erase old notes if conflict", required=True)

    FIELDS = (
        ('LP', 'Albums'),
        ('EP', 'EPs'),
        ('Live', 'Live'),
        ('Compilation', 'Compilations'),
        ('OST', 'Bandes Originales'),
    )

    fields = serializers.MultipleChoiceField(label="Album types to export", choices=FIELDS, required=True)
