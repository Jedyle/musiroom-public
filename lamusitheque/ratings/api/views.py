from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from lamusitheque.apiutils.serializers import VoteSerializer
from ratings.api.filters import ReviewFilter
from ratings.api.permissions import IsUserOrReadOnly
from ratings.api.serializers import ReviewSerializer, ReviewCreateSerializer
from ratings.models import Review


class ReviewViewset(viewsets.ModelViewSet):

    permission_classes = (IsUserOrReadOnly,)
    queryset = Review.objects.all()
    filter_class = ReviewFilter

    def get_queryset(self):

        """
        Adds custom filter for review list.
        content_type : filter with obj.rating.rating.content_type.model
        """

        queryset = Review.objects.all()

        content_type = self.request.query_params.get("content_type")
        if content_type is not None:
            queryset = queryset.filter(rating__rating__content_type__model=content_type)

        object_id = self.request.query_params.get("object_id")
        if object_id is not None:
            try:
                object_id = int(object_id)
            except ValueError:
                object_id = -1
            queryset = queryset.filter(rating__rating__object_id=object_id)

        return queryset

    def get_serializer_class(self):
        if self.request.method in ["POST"]:
            return ReviewCreateSerializer
        return ReviewSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.validated_data.get('rating')
        if rating.user != request.user:
            raise PermissionDenied({
                "message": "Users do not match"
            })
        review = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["PUT"])
    def vote(self, request, pk=None):
        # votes
        # TODO : change default form in browsable API
        # TODO : refactor with other votes
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = serializer.validated_data.get('vote')
        obj = self.get_object()
        if vote == "up":
            obj.votes.up(request.user.pk)
        elif vote == "down":
            obj.votes.down(request.user.pk)
        else:
            obj.votes.delete(request.user.pk)
        # re-call get object to have the updated instance
        # (doesn't update by itself, don't know why)
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class UserReviewViewset(viewsets.GenericViewSet, mixins.ListModelMixin):

    permission_classes = (IsUserOrReadOnly,)
    queryset = Review.objects.all()
    filter_class = ReviewFilter
    serializer_class = ReviewSerializer

    def get_queryset(self):
        username = self.kwargs["users_user__username"]
        return Review.objects.filter(rating__user__username=username)


