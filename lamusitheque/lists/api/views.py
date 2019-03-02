from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from lamusitheque.apiutils.permissions import IsUserOrReadOnly
from lamusitheque.apiutils.serializers import VoteSerializer
from lists.api.filters import ListFilter
from lists.api.permissions import IsListUserOrReadOnly
from lists.api.serializers import ListObjSerializer, ListItemSerializer, ListItemOrderSerializer, \
    ListItemWriteSerializer
from lists.models import ListObj, ListItem


class ListViewset(viewsets.ModelViewSet):
    """
    Viewset for lists. Only authenticated users can create a list, and only
    list user can change his list.
    """

    permission_classes = (IsUserOrReadOnly,)
    serializer_class = ListObjSerializer
    queryset = ListObj.objects.all()
    filter_class = ListFilter

    @action(detail=True, methods=["PUT"])
    def vote(self, request, pk=None):
        # votes
        # TODO : change default form in browsable API
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = serializer.validated_data.get('vote')
        listobj = self.get_object()
        if vote == "up":
            listobj.votes.up(request.user.pk)
        elif vote == "down":
            listobj.votes.down(request.user.pk)
        else:
            listobj.votes.delete(request.user.pk)
        # re-call get object to have the updated instance
        # (doesn't update by itself, don't know why)
        listobj = self.get_object()
        serializer = self.get_serializer(listobj)
        return Response(serializer.data)


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
    Viewset for lists/id/items . Only list users can create, edit or delete items.
    """

    permission_classes = (IsListUserOrReadOnly,)
    serializer_class = ListItemSerializer

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ListItemSerializer
        return ListItemWriteSerializer

    def get_queryset(self):
        listobj = get_object_or_404(ListObj, id=self.kwargs['lists_pk'])
        return ListItem.objects.filter(item_list=listobj)

    def create(self, request, *args, **kwargs):
        """
        Object permissions don't work with 'create', so with must rewrite the create method
        to ensure the list belongs to the user.
        """

        list_pk = self.kwargs['lists_pk']
        # forces to stop here if the user does not own the list
        list_obj = get_object_or_404(ListObj, id=list_pk)
        if list_obj.user != request.user:
            raise Http404("List not found")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        album = serializer.validated_data.get('album')
        if ListItem.objects.filter(album=album, item_list=list_obj):
            return Response({
                "message": "This album is already in the list"
            }, status=status.HTTP_400_BAD_REQUEST)

        item = serializer.save(item_list=list_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['PUT'], serializer_class=ListItemOrderSerializer)
    def position(self, request, lists_pk=None, pk=None):
        """
        Change an item's position
        """
        serializer = ListItemOrderSerializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
