from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, generics, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from star_ratings.api.serializers import RatingSerializer, UserRatingSerializer, ExtendedUserRatingSerializer
from star_ratings.models import Rating, UserRating


class RatingViewset(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    """
    API View to retrieve a Rating object.
    """

    serializer_class = RatingSerializer
    queryset = Rating.objects.all()

    @action(detail=True, methods=['GET'])
    def stats(self, request, pk=None):
        rating = self.get_object()
        user_ratings = rating.user_ratings
        count = []
        # TODO : optimize this into a single query
        for i in range(1, 11):
            count.append(user_ratings.filter(score=i).count())
        serializer = self.get_serializer(rating)
        return Response({
            **serializer.data,
            "stats":
                {
                    "labels": list(range(1, 11)),
                    "data": count
                }
        })


class CreateUserRatingView(generics.CreateAPIView):
    serializer_class = UserRatingSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, rating_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_rating = serializer.save(rating_id=rating_id, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserRatingView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserRatingSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        user = self.request.user
        rating_id = self.kwargs["rating_id"]
        rating = get_object_or_404(UserRating, user=user, rating__id=rating_id)
        return rating

    def get_queryset(self):
        return None


class UserUserRatingViewset(viewsets.GenericViewSet, mixins.ListModelMixin):

    serializer_class = ExtendedUserRatingSerializer

    def get_queryset(self):
        username = self.kwargs["users_user__username"]
        return UserRating.objects.filter(user__username=username)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def followees_ratings(request):
    ids = request.GET.get('ids')
    if ids is not None:
        try:
            ids = [int(el) for el in ids.split(',')]
        except ValueError:
            return Response({"message": "IDs are not integers"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "Parameter 'ids' is required"}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    ratings_list = UserRating.objects.filter(Q(rating_id__in=ids) & Q(user__followers__follower=user))\
        .values('rating__id').annotate(avg=Avg('score'))
    ratings_list = {el['rating__id']: el['avg'] for el in ratings_list}
    return Response({
        "ratings": ratings_list
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_ratings(request):
    ids = request.GET.get('ids')
    if ids is not None:
        try:
            ids = [int(el) for el in ids.split(',')]
        except ValueError:
            return Response({"message": "IDs are not integers"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "Parameter 'ids' is required"}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    ratings_list = UserRating.objects.filter(rating_id__in=ids).filter(user=user)
    ratings_list = {el.rating_id: el.score for el in ratings_list}
    return Response({
        "ratings": ratings_list
    })
