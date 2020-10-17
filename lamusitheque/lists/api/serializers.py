from rest_framework import serializers
from rest_framework.fields import IntegerField

from albums.api.serializers import ShortAlbumSerializer, AlbumSerializer
from user_profile.api.short_serializers import ShortUserSerializer
from albums.models import Album
from lists.models import ListObj, ListItem
from lamusitheque.apiutils.mixins import VoteSerializerMixin


class ShortListItemSerializer(serializers.ModelSerializer):
    album = ShortAlbumSerializer()

    class Meta:
        model = ListItem
        fields = ("id", "album", "order")


class ListItemSerializer(serializers.ModelSerializer):
    album = AlbumSerializer()

    class Meta:
        model = ListItem
        fields = ("id", "album", "comment", "order")
        read_only_fields = ("order",)


class ListItemWriteSerializer(serializers.ModelSerializer):
    album = serializers.SlugRelatedField(
        slug_field="mbid", queryset=Album.objects.all()
    )

    class Meta:
        model = ListItem
        fields = ("id", "album", "comment", "order")
        read_only_fields = ("id", "order")


class ListItemOrderSerializer(serializers.ModelSerializer):
    """
    Serializer to move an item
    """

    order = IntegerField(required=True)

    class Meta:
        model = ListItem
        fields = ("order", "id", "album", "comment")
        read_only_fields = ("id", "album", "comment")

    def update(self, instance, validated_data):

        """
        Move an item to another position
        """

        item_id = instance.order
        destination_id = validated_data.pop("order")
        items = ListItem.objects.filter(item_list=instance.item_list)
        nb_items = items.count()
        if nb_items >= destination_id >= 1 and nb_items >= item_id >= 1:
            if destination_id < item_id:
                for elt in items[destination_id-1:item_id-1]:
                    elt.order += 1
                    elt.save()
                instance.order = destination_id
                instance.save()
            elif destination_id > item_id:
                for elt in items[item_id:destination_id]:
                    elt.order -= 1
                    elt.save()
                instance.order = destination_id
                instance.save()
        return instance


class ListObjSerializer(serializers.ModelSerializer, VoteSerializerMixin):
    # albums are fetched in another route

    user = ShortUserSerializer(read_only=True)

    class Meta:
        model = ListObj
        fields = (
            "id",
            "user",
            "title",
            "description",
            "ordered",
            "num_vote_up",
            "num_vote_down",
            "vote_score",
            "user_vote"
        )
        read_only_fields = ("num_vote_up", "num_vote_down", "vote_score")

    def get_request_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def create(self, validated_data):
        listobj = ListObj(**validated_data, user=self.get_request_user())
        listobj.save()
        return listobj
