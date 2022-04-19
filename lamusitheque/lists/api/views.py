from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from albums.models import Album
from lamusitheque.apiutils.mixins import VoteMixin
from lamusitheque.apiutils.permissions import IsUserOrReadOnly
from lists.api.filters import ListFilter
from lists.api.permissions import IsListUserOrReadOnly
from lists.api.serializers import (
    ListObjSerializer,
    ListItemWithListSerializer,
    ListItemSerializer,
    ListItemOrderSerializer,
    ListItemWriteSerializer,
    ShortListItemSerializer,
)
from lists.models import ListObj, ListItem


class ListViewset(viewsets.ModelViewSet, VoteMixin):
    """
    Viewset for lists. Only authenticated users can create a list, and only
    list user can change his list.
    """

    permission_classes = (IsUserOrReadOnly,)
    serializer_class = ListObjSerializer
    queryset = ListObj.objects.all()
    filter_class = ListFilter
    ordering_fields = ("vote_score", "modified", "created")


class UserListViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    Viewset to list a user's lists
    """

    serializer_class = ListObjSerializer
    filter_class = ListFilter

    def get_queryset(self):
        username = self.kwargs["users_user__username"]
        return ListObj.objects.filter(user__username=username)


class ListItemViewset(viewsets.ModelViewSet):
    """
    Viewset for lists/id/items .
    Only list users can create, edit or delete items.
    """

    permission_classes = (IsListUserOrReadOnly,)
    serializer_class = ListItemSerializer

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return ListItemSerializer
        return ListItemWriteSerializer

    def get_queryset(self):
        listobj = get_object_or_404(ListObj, id=self.kwargs["lists_pk"])
        return ListItem.objects.filter(item_list=listobj)

    def create(self, request, *args, **kwargs):
        """
        Object permissions don't work with 'create',
        so with must rewrite the create method
        to ensure the list belongs to the user.
        """

        list_pk = self.kwargs["lists_pk"]
        # forces to stop here if the user does not own the list
        list_obj = get_object_or_404(ListObj, id=list_pk)
        if list_obj.user != request.user:
            raise Http404("List not found")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        album = serializer.validated_data.get("album")
        if ListItem.objects.filter(album=album, item_list=list_obj):
            return Response(
                {"message": "This album is already in the list"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(item_list=list_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["GET"])
    def positions(self, request, lists_pk=None):
        serializer = ShortListItemSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT"], serializer_class=ListItemOrderSerializer)
    def position(self, request, lists_pk=None, pk=None):
        """
        Change an item's position
        """
        serializer = ListItemOrderSerializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_lists_with_album(request):
    mbid = request.GET.get("mbid")
    if not mbid:
        return Response({"message": "No mbid set"})
    get_object_or_404(Album, mbid=mbid)
    listItemsForAlbum = ListItem.objects.filter(
        item_list__user=request.user, album__mbid=mbid
    )
    serializer = ListItemWithListSerializer(
        listItemsForAlbum, many=True, context={"request": request}
    )
    return Response(serializer.data)
