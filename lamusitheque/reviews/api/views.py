from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from lamusitheque.apiutils.mixins import VoteMixin
from lamusitheque.apiutils.serializers import VoteSerializer
from reviews.api.filters import ReviewFilter
from reviews.api.permissions import IsUserOrReadOnly
from reviews.api.serializers import ReviewSerializer, ReviewCreateSerializer
from reviews.models import Review


class ReviewViewset(viewsets.ModelViewSet, VoteMixin):

    permission_classes = (IsUserOrReadOnly,)
    queryset = Review.objects.all()
    filter_class = ReviewFilter
    ordering_fields = ('date_publication', 'rating__score')
    
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


class UserReviewViewset(viewsets.GenericViewSet, mixins.ListModelMixin):

    permission_classes = (IsUserOrReadOnly,)
    queryset = Review.objects.all()
    filter_class = ReviewFilter
    serializer_class = ReviewSerializer

    def get_queryset(self):
        username = self.kwargs["users_user__username"]
        queryset = Review.objects.filter(rating__user__username=username)
        album_title = self.request.query_params.get("album_title__icontains")
        if album_title:
            queryset = queryset.filter(rating__rating__albums__title__icontains=album_title)
        return queryset




